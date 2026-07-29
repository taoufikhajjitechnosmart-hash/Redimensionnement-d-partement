import type { Jour, Regime } from './rythmes';
import { NOMS_JOURS } from './rythmes';
import { fournisseurMatrice, type FournisseurDistances } from './distance';
import { repartir } from './scenario';
import type { Referentiel, Scenario } from './types';

export type Activite = 'SAV' | 'PROD' | 'MIXTE';

export interface Technicien {
  readonly id: string;
  readonly nom: string;
  readonly societe: string;
  readonly activite: Activite;
  readonly regime: Regime;
  /** Zone de rattachement. Absente pour un renfort mobile. */
  readonly zoneId?: string;
}

/** Une vacation : des créneaux sur un secteur, dans une journée. */
export interface Vacation {
  readonly secteurId: string;
  readonly creneaux: number;
}

export interface JourneeTechnicien {
  readonly technicienId: string;
  readonly jour: Jour;
  readonly vacations: readonly Vacation[];
}

export type Affectation = readonly JourneeTechnicien[];

export type CodeInfraction =
  | 'capacite-depassee'
  | 'trop-de-secteurs'
  | 'distance-excessive'
  | 'hors-regime'
  | 'vacation-vide'
  | 'secteur-inconnu';

export interface Infraction {
  readonly code: CodeInfraction;
  readonly technicienId: string;
  readonly jour: Jour;
  readonly message: string;
}

/**
 * Contrôle une affectation contre les règles du scénario.
 *
 * Conçu pour être appelé à chaque déplacement dans l'interface : il ne modifie
 * rien et renvoie la liste complète des infractions, pas seulement la première.
 */
export function validerAffectation(
  affectation: Affectation,
  techniciens: readonly Technicien[],
  scenario: Scenario,
  referentiel: Referentiel,
  distances: FournisseurDistances = fournisseurMatrice(referentiel.distances),
): Infraction[] {
  const parId = new Map(referentiel.secteurs.map((s) => [s.id, s]));
  const techParId = new Map(techniciens.map((t) => [t.id, t]));
  const infractions: Infraction[] = [];

  for (const journee of affectation) {
    const { technicienId, jour, vacations } = journee;
    const tech = techParId.get(technicienId);
    const nomTech = tech?.nom ?? technicienId;
    const ajouter = (code: CodeInfraction, message: string): void => {
      infractions.push({ code, technicienId, jour, message });
    };

    if (tech && jour >= tech.regime) {
      ajouter(
        'hors-regime',
        `${nomTech} travaille ${tech.regime} jours : le ${NOMS_JOURS[jour].toLowerCase()} n'existe pas pour lui.`,
      );
    }
    if (jour >= scenario.regime) {
      ajouter(
        'hors-regime',
        `Le scénario est en ${scenario.regime} jours : le ${NOMS_JOURS[jour].toLowerCase()} n'est pas ouvert.`,
      );
    }

    const inconnus = vacations.filter((v) => !parId.has(v.secteurId));
    for (const v of inconnus) {
      ajouter('secteur-inconnu', `Secteur « ${v.secteurId} » absent du référentiel.`);
    }

    if (vacations.some((v) => v.creneaux <= 0)) {
      ajouter('vacation-vide', `${nomTech}, ${NOMS_JOURS[jour].toLowerCase()} : vacation à zéro créneau.`);
    }

    const total = vacations.reduce((s, v) => s + v.creneaux, 0);
    if (total > scenario.capaciteParTechJour) {
      ajouter(
        'capacite-depassee',
        `${nomTech}, ${NOMS_JOURS[jour].toLowerCase()} : ${total} créneaux pour une capacité de ${scenario.capaciteParTechJour}.`,
      );
    }

    const secteursDistincts = [...new Set(vacations.map((v) => v.secteurId))];
    if (secteursDistincts.length > scenario.maxSecteursParTechJour) {
      ajouter(
        'trop-de-secteurs',
        `${nomTech}, ${NOMS_JOURS[jour].toLowerCase()} : ${secteursDistincts.length} secteurs, le maximum est ${scenario.maxSecteursParTechJour}.`,
      );
    }

    for (let i = 0; i < secteursDistincts.length; i++) {
      for (let j = i + 1; j < secteursDistincts.length; j++) {
        const a = secteursDistincts[i]!;
        const b = secteursDistincts[j]!;
        if (!parId.has(a) || !parId.has(b)) continue;
        const km = distances.km(a, b);
        if (km > scenario.distanceMaxEnchainement) {
          ajouter(
            'distance-excessive',
            `${nomTech}, ${NOMS_JOURS[jour].toLowerCase()} : ${parId.get(a)!.nom} → ${parId.get(b)!.nom}, ` +
              `${Math.round(km)} km pour un maximum de ${scenario.distanceMaxEnchainement} km.`,
          );
        }
      }
    }
  }

  return infractions;
}

/** Charge d'un secteur pour un jour donné, telle que le scénario l'a répartie. */
function chargeParSecteurEtJour(scenario: Scenario): Map<string, number[]> {
  const charge = new Map<string, number[]>();
  for (const offre of scenario.offres) {
    charge.set(offre.secteurId, repartir(offre.creneaux, offre.jours));
  }
  return charge;
}

export interface OptionsSolveur {
  /** Ne pas dépasser cette part de la capacité d'un technicien. */
  readonly tauxRemplissageMax?: number;
}

/**
 * Construit une affectation à partir d'un scénario, par glouton déterministe.
 *
 * Journée par journée, les secteurs les plus chargés sont servis en premier par
 * les techniciens de leur zone, puis par les techniciens restants. Chaque pose
 * est soumise au validateur : le solveur ne produit jamais une affectation qu'il
 * refuserait ensuite.
 *
 * Le résultat est un point de départ à retoucher à la main, pas un optimum.
 * Les créneaux qui n'ont pas trouvé de place sont listés dans `nonPlaces`.
 */
export function construireAffectation(
  scenario: Scenario,
  referentiel: Referentiel,
  techniciens: readonly Technicien[],
  distances: FournisseurDistances = fournisseurMatrice(referentiel.distances),
  options: OptionsSolveur = {},
): { affectation: JourneeTechnicien[]; nonPlaces: { secteurId: string; jour: Jour; creneaux: number }[] } {
  const charge = chargeParSecteurEtJour(scenario);
  const parId = new Map(referentiel.secteurs.map((s) => [s.id, s]));
  const capacite = Math.floor(
    scenario.capaciteParTechJour * (options.tauxRemplissageMax ?? 1),
  );

  const journees = new Map<string, { vacations: Vacation[] }>();
  const cle = (t: string, j: Jour): string => `${t}#${j}`;
  const nonPlaces: { secteurId: string; jour: Jour; creneaux: number }[] = [];

  for (let jour = 0 as Jour; jour < scenario.regime; jour = (jour + 1) as Jour) {
    const disponibles = techniciens.filter((t) => jour < t.regime);

    const aPlacer = [...charge.entries()]
      .map(([secteurId, parJour]) => ({ secteurId, creneaux: parJour[jour] ?? 0 }))
      .filter((x) => x.creneaux > 0)
      .sort((a, b) => b.creneaux - a.creneaux || a.secteurId.localeCompare(b.secteurId));

    for (const { secteurId, creneaux } of aPlacer) {
      let reste = creneaux;
      const secteur = parId.get(secteurId);

      // Les techniciens de la zone d'abord, puis les plus proches.
      const candidats = [...disponibles].sort((a, b) => {
        const zoneA = a.zoneId === secteur?.zoneId ? 0 : 1;
        const zoneB = b.zoneId === secteur?.zoneId ? 0 : 1;
        if (zoneA !== zoneB) return zoneA - zoneB;
        return a.id.localeCompare(b.id);
      });

      for (const tech of candidats) {
        if (reste <= 0) break;
        const k = cle(tech.id, jour);
        const journee = journees.get(k) ?? { vacations: [] };
        const dejaPose = journee.vacations.reduce((s, v) => s + v.creneaux, 0);
        const place = capacite - dejaPose;
        if (place <= 0) continue;

        const secteursDistincts = new Set(journee.vacations.map((v) => v.secteurId));
        if (!secteursDistincts.has(secteurId)) {
          if (secteursDistincts.size >= scenario.maxSecteursParTechJour) continue;
          const tropLoin = [...secteursDistincts].some(
            (autre) => distances.km(autre, secteurId) > scenario.distanceMaxEnchainement,
          );
          if (tropLoin) continue;
        }

        const pose = Math.min(place, reste);
        const existante = journee.vacations.find((v) => v.secteurId === secteurId);
        if (existante) {
          journee.vacations = journee.vacations.map((v) =>
            v.secteurId === secteurId ? { ...v, creneaux: v.creneaux + pose } : v,
          );
        } else {
          journee.vacations.push({ secteurId, creneaux: pose });
        }
        journees.set(k, journee);
        reste -= pose;
      }

      if (reste > 0) nonPlaces.push({ secteurId, jour, creneaux: reste });
    }
  }

  const affectation: JourneeTechnicien[] = [];
  for (const [k, { vacations }] of journees) {
    const [technicienId, jourTexte] = k.split('#');
    affectation.push({
      technicienId: technicienId!,
      jour: Number(jourTexte) as Jour,
      vacations,
    });
  }
  affectation.sort((a, b) => a.jour - b.jour || a.technicienId.localeCompare(b.technicienId));

  return { affectation, nonPlaces };
}
