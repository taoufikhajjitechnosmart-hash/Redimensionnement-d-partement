import { conformeJ2, ecartMax, type Jour } from './rythmes';
import { demandeHebdo } from './demande';
import { fournisseurMatrice, type FournisseurDistances } from './distance';
import type {
  Alerte,
  Referentiel,
  Resultat,
  ResultatSecteur,
  Scenario,
  Secteur,
} from './types';

/**
 * Répartit `total` créneaux sur `jours`, division entière, le reste distribué
 * sur les premiers jours de la semaine.
 *
 * Renvoie un tableau de six cases, du lundi au samedi ; les jours sans passage
 * restent à zéro.
 */
export function repartir(total: number, jours: readonly Jour[]): number[] {
  const parJour = [0, 0, 0, 0, 0, 0];
  if (jours.length === 0) return parJour;

  const tries = [...new Set(jours)].sort((a, b) => a - b);
  const base = Math.floor(total / tries.length);
  let reste = total - base * tries.length;
  for (const jour of tries) {
    parJour[jour] = base + (reste > 0 ? 1 : 0);
    if (reste > 0) reste--;
  }
  return parJour;
}

/** Kilomètres hebdomadaires d'un secteur : un aller-retour depuis sa base par passage. */
export function kmSecteur(
  secteur: Secteur,
  nbPassages: number,
  baseSecteurId: string,
  distances: FournisseurDistances,
): number {
  return nbPassages * 2 * distances.km(baseSecteurId, secteur.id);
}

const plafond = (x: number): number => Math.ceil(x - 1e-9);

/**
 * Évalue un scénario. Fonction pure : mêmes entrées, mêmes sorties, aucun
 * accès au réseau ni au disque.
 */
export function evaluerScenario(
  scenario: Scenario,
  referentiel: Referentiel,
  distances: FournisseurDistances = fournisseurMatrice(referentiel.distances),
): Resultat {
  const parId = new Map(referentiel.secteurs.map((s) => [s.id, s]));
  const zoneParId = new Map(referentiel.zones.map((z) => [z.id, z]));
  const offreParSecteur = new Map(scenario.offres.map((o) => [o.secteurId, o]));

  const secteurs: ResultatSecteur[] = [];
  const alertes: Alerte[] = [];
  const chargeParJour = [0, 0, 0, 0, 0, 0];
  /** Charge par zone puis par jour, pour la pointe journalière. */
  const chargeZoneJour = new Map<string, number[]>();

  for (const secteur of referentiel.secteurs) {
    const offre = offreParSecteur.get(secteur.id);
    const jours = offre ? [...new Set(offre.jours)].sort((a, b) => a - b) : [];
    const creneaux = offre?.creneaux ?? 0;

    const horsRegime = jours.find((j) => j >= scenario.regime);
    if (horsRegime !== undefined) {
      throw new RangeError(
        `${secteur.nom} : passage programmé hors du régime de ${scenario.regime} jours.`,
      );
    }

    const demande = demandeHebdo(secteur.volume, scenario.paramsDemande);
    const couverture = demande > 0 ? creneaux / demande : Number.POSITIVE_INFINITY;
    const ecart = ecartMax(jours, scenario.regime);
    const tientJ2 = conformeJ2(jours, scenario.regime);
    const couvre = couverture >= scenario.couvertureCible;
    const creneauxParJour = repartir(creneaux, jours);

    const zone = zoneParId.get(secteur.zoneId);
    if (!zone) throw new RangeError(`${secteur.nom} : zone « ${secteur.zoneId} » inconnue.`);

    const km = kmSecteur(secteur, jours.length, zone.baseSecteurId, distances);

    if (!tientJ2) {
      alertes.push({
        secteurId: secteur.id,
        nom: secteur.nom,
        gravite: 'critique',
        code: 'delai-j2',
        message:
          jours.length === 0
            ? `${secteur.nom} n'est jamais visité.`
            : `${secteur.nom} : ${ecart} jours entre deux passages, le délai J+2 n'est pas tenu.`,
      });
    }
    if (!couvre) {
      alertes.push({
        secteurId: secteur.id,
        nom: secteur.nom,
        gravite: 'avertissement',
        code: 'couverture',
        message:
          `${secteur.nom} : ${creneaux} créneaux pour ${demande.toFixed(1)} de demande, ` +
          `soit ${(couverture * 100).toFixed(0)} % au lieu des ` +
          `${(scenario.couvertureCible * 100).toFixed(0)} % visés.`,
      });
    }

    for (let j = 0; j < 6; j++) chargeParJour[j]! += creneauxParJour[j]!;

    const parJourZone = chargeZoneJour.get(secteur.zoneId) ?? [0, 0, 0, 0, 0, 0];
    for (let j = 0; j < 6; j++) parJourZone[j]! += creneauxParJour[j]!;
    chargeZoneJour.set(secteur.zoneId, parJourZone);

    secteurs.push({
      secteurId: secteur.id,
      nom: secteur.nom,
      zoneId: secteur.zoneId,
      demandeHebdo: demande,
      offre: creneaux,
      couverture,
      jours,
      nbPassages: jours.length,
      ecartMax: ecart,
      conformeJ2: tientJ2,
      couvertureSuffisante: couvre,
      creneauxParJour,
      kmSemaine: km,
    });
  }

  // Effectif minimum : dans chaque zone, la journée de pointe commande.
  const effectifParZone: Record<string, number> = {};
  let effectifMinimum = 0;
  let effectifSamedi = 0;
  for (const zone of referentiel.zones) {
    const parJour = chargeZoneJour.get(zone.id) ?? [0, 0, 0, 0, 0, 0];
    const pointe = Math.max(...parJour.slice(0, scenario.regime));
    const besoin = plafond(pointe / scenario.capaciteParTechJour);
    effectifParZone[zone.id] = besoin;
    effectifMinimum += besoin;
    if (scenario.regime === 6) {
      effectifSamedi += plafond(parJour[5]! / scenario.capaciteParTechJour);
    }
  }

  const offreTotale = secteurs.reduce((s, x) => s + x.offre, 0);
  const demandeTotale = secteurs.reduce((s, x) => s + x.demandeHebdo, 0);
  const capaciteTotale = effectifMinimum * scenario.regime * scenario.capaciteParTechJour;

  return {
    scenarioId: scenario.id,
    offreTotale,
    demandeTotale,
    couverture: demandeTotale > 0 ? offreTotale / demandeTotale : Number.POSITIVE_INFINITY,
    alertes,
    nbAlertesJ2: alertes.filter((a) => a.code === 'delai-j2').length,
    effectifMinimum,
    effectifSamedi,
    capaciteTotale,
    occupation: capaciteTotale > 0 ? offreTotale / capaciteTotale : 0,
    kmSemaine: secteurs.reduce((s, x) => s + x.kmSemaine, 0),
    chargeParJour,
    effectifParZone,
    secteurs,
  };
}
