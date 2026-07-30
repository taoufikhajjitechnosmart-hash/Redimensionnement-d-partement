import * as XLSX from 'xlsx';
import {
  evaluerScenario,
  formaterRythme,
  NOMS_JOURS,
  type Referentiel,
  type Scenario,
} from '@sim/engine';

/**
 * Classeur de restitution.
 *
 * Six onglets, un par question qu'on se pose devant un dimensionnement : le
 * résumé, le détail par secteur, la charge jour par jour, le contrôle du délai,
 * les distances, et les hypothèses retenues. Ce dernier onglet n'est pas
 * décoratif : sans lui, les chiffres des cinq autres ne sont pas
 * interprétables.
 */

type Cellule = string | number | null;

function feuille(lignes: Cellule[][], largeurs: number[]): XLSX.WorkSheet {
  const f = XLSX.utils.aoa_to_sheet(lignes);
  f['!cols'] = largeurs.map((w) => ({ wch: w }));
  if (lignes.length > 1) f['!freeze'] = { xSplit: 0, ySplit: 1 };
  return f;
}

export function construireClasseur(
  scenarios: readonly Scenario[],
  referentiel: Referentiel,
): Buffer {
  if (scenarios.length === 0) throw new Error('Aucun scénario à exporter.');

  const evalues = scenarios.map((s) => ({ scenario: s, resultat: evaluerScenario(s, referentiel) }));
  const classeur = XLSX.utils.book_new();

  // ── Synthèse ────────────────────────────────────────────────────────────
  const synthese: Cellule[][] = [
    ['Indicateur', ...evalues.map((e) => e.scenario.nom)],
    ['Régime (jours ouvrés)', ...evalues.map((e) => e.scenario.regime)],
    ['Créneaux par technicien et par jour', ...evalues.map((e) => e.scenario.capaciteParTechJour)],
    ['Créneaux ouverts', ...evalues.map((e) => e.resultat.offreTotale)],
    ['Demande hebdomadaire', ...evalues.map((e) => Math.round(e.resultat.demandeTotale * 10) / 10)],
    ['Couverture', ...evalues.map((e) => Math.round(e.resultat.couverture * 100) / 100)],
    [
      `Secteurs hors délai J+2 (sur ${referentiel.secteurs.length})`,
      ...evalues.map((e) => e.resultat.nbAlertesJ2),
    ],
    ['Techniciens (minimum structurel)', ...evalues.map((e) => e.resultat.effectifMinimum)],
    ['dont le samedi', ...evalues.map((e) => e.resultat.effectifSamedi)],
    ['Capacité totale', ...evalues.map((e) => e.resultat.capaciteTotale)],
    ['Occupation', ...evalues.map((e) => Math.round(e.resultat.occupation * 100) / 100)],
    ['Kilomètres par semaine', ...evalues.map((e) => Math.round(e.resultat.kmSemaine))],
    [],
    ['Techniciens par zone'],
    ...referentiel.zones.map(
      (z): Cellule[] => [
        `  ${z.nom}`,
        ...evalues.map((e) => e.resultat.effectifParZone[z.id] ?? 0),
      ],
    ),
  ];
  XLSX.utils.book_append_sheet(
    classeur,
    feuille(synthese, [38, ...evalues.map(() => 20)]),
    'Synthèse',
  );

  /**
   * Nom d'onglet : Excel plafonne à 31 caractères et refuse les doublons, si
   * bien que deux scénarios aux noms proches se télescoperaient sans ce garde-fou.
   */
  const nomsUtilises = new Set<string>();
  const nomOnglet = (souhaite: string): string => {
    const base = souhaite.replace(/[[\]:*?/\\]/g, ' ').slice(0, 31).trim();
    if (!nomsUtilises.has(base)) {
      nomsUtilises.add(base);
      return base;
    }
    for (let n = 2; n < 100; n++) {
      const candidat = `${base.slice(0, 31 - String(n).length - 1)} ${n}`;
      if (!nomsUtilises.has(candidat)) {
        nomsUtilises.add(candidat);
        return candidat;
      }
    }
    throw new Error(`Impossible de nommer l'onglet « ${souhaite} ».`);
  };

  // ── Secteurs, un onglet par scénario si plusieurs ───────────────────────
  for (const { scenario, resultat } of evalues) {
    const lignes: Cellule[][] = [
      [
        'Secteur',
        'Zone',
        'Demande/sem',
        'Créneaux',
        'Couverture',
        'Passages',
        'Rythme',
        'Écart max',
        'Délai J+2',
        'Km/sem',
        ...NOMS_JOURS.slice(0, scenario.regime),
      ],
      ...resultat.secteurs.map((s): Cellule[] => [
        s.nom,
        s.zoneId,
        Math.round(s.demandeHebdo * 10) / 10,
        s.offre,
        Number.isFinite(s.couverture) ? Math.round(s.couverture * 100) / 100 : null,
        s.nbPassages,
        formaterRythme(s.jours) || '—',
        Number.isFinite(s.ecartMax) ? s.ecartMax : null,
        s.conformeJ2 ? 'conforme' : 'HORS DÉLAI',
        Math.round(s.kmSemaine),
        ...s.creneauxParJour.slice(0, scenario.regime),
      ]),
      [
        'TOTAL',
        null,
        Math.round(resultat.demandeTotale * 10) / 10,
        resultat.offreTotale,
        null,
        resultat.secteurs.reduce((s, x) => s + x.nbPassages, 0),
        null,
        null,
        `${resultat.nbAlertesJ2} hors délai`,
        Math.round(resultat.kmSemaine),
        ...resultat.chargeParJour.slice(0, scenario.regime),
      ],
    ];
    XLSX.utils.book_append_sheet(
      classeur,
      feuille(lignes, [24, 6, 12, 10, 11, 9, 16, 10, 12, 9, ...NOMS_JOURS.map(() => 8)]),
      nomOnglet(scenario.nom),
    );
  }

  // ── Contrôle du délai ───────────────────────────────────────────────────
  const controle: Cellule[][] = [
    ['Secteur', ...evalues.flatMap((e) => [`${e.scenario.nom} — rythme`, `${e.scenario.nom} — écart`])],
    ...referentiel.secteurs.map((secteur): Cellule[] => [
      secteur.nom,
      ...evalues.flatMap((e) => {
        const s = e.resultat.secteurs.find((x) => x.secteurId === secteur.id);
        if (!s) return [null, null];
        return [
          formaterRythme(s.jours) || '—',
          Number.isFinite(s.ecartMax) ? s.ecartMax : 'jamais visité',
        ];
      }),
    ]),
    [],
    ['Un secteur est conforme si son écart maximal ne dépasse jamais 2 jours ouvrés,'],
    ['en calcul cyclique : le lundi suit le vendredi en semaine de 5 jours, le samedi en 6.'],
  ];
  XLSX.utils.book_append_sheet(
    classeur,
    feuille(controle, [24, ...evalues.flatMap(() => [18, 10])]),
    'Contrôle J+2',
  );

  // ── Distances ───────────────────────────────────────────────────────────
  const noms = referentiel.secteurs.map((s) => s.nom);
  const distances: Cellule[][] = [
    ['km', ...noms],
    ...referentiel.secteurs.map((a): Cellule[] => [
      a.nom,
      ...referentiel.secteurs.map((b) => referentiel.distances[a.id]?.[b.id] ?? null),
    ]),
    [],
    ['Distances estimées : vol d’oiseau majoré de 25 %. À recaler sur un outil de tournées.'],
  ];
  XLSX.utils.book_append_sheet(
    classeur,
    feuille(distances, [24, ...noms.map(() => 11)]),
    'Distances',
  );

  // ── Hypothèses ──────────────────────────────────────────────────────────
  const libelleMois: Record<string, string> = {
    pic: 'le plus chargé des deux mois',
    moyenne: 'moyenne octobre / mars',
    octobre: 'octobre',
    mars: 'mars',
  };
  const libelleMethode: Record<string, string> = {
    'volume-mensuel': 'volume du mois ÷ semaines par mois',
    'moyenne-journaliere': 'moyenne par jour × jours ouvrés ÷ semaines par mois',
  };
  const hypotheses: Cellule[][] = [
    ['Hypothèse', ...evalues.map((e) => e.scenario.nom)],
    ['Mois de dimensionnement', ...evalues.map((e) => libelleMois[e.scenario.paramsDemande.mois] ?? '')],
    ['Méthode de conversion', ...evalues.map((e) => libelleMethode[e.scenario.paramsDemande.methode] ?? '')],
    ['Semaines par mois', ...evalues.map((e) => e.scenario.paramsDemande.semainesParMois)],
    ['Jours ouvrés par mois', ...evalues.map((e) => e.scenario.paramsDemande.joursOuvresParMois)],
    ['B2B compté', ...evalues.map((e) => (e.scenario.paramsDemande.inclureB2B ? 'oui' : 'non'))],
    ['Marge de flexibilité', ...evalues.map((e) => e.scenario.paramsDemande.margeFlexibilite)],
    ['Couverture visée', ...evalues.map((e) => e.scenario.couvertureCible)],
    ['Secteurs max par technicien et par jour', ...evalues.map((e) => e.scenario.maxSecteursParTechJour)],
    ['Distance max entre secteurs enchaînés (km)', ...evalues.map((e) => e.scenario.distanceMaxEnchainement)],
    [],
    ['Réserves'],
    ['Aucun volume SAV mesuré n’existe dans les fichiers sources. La demande ci-dessus'],
    ['ne couvre que la production ; le SAV est absorbé par l’écart entre offre et demande.'],
    [],
    ['L’effectif est un minimum structurel : journée de pointe par zone, sans absences,'],
    ['congés ni enchaînements inter-zones. Prévoir au moins un poste de plus.'],
    [],
    ['Les distances sont approchées, pas des temps de trajet réels.'],
    [],
    ['Le SAV ne peut pas être garanti à 100 % : les arrivées sont aléatoires.'],
    ['On vise un taux de service, jamais la certitude.'],
    [],
    [`Classeur produit le ${new Date().toLocaleDateString('fr-FR')} — département ${referentiel.departement}, ${referentiel.libelle}.`],
  ];
  XLSX.utils.book_append_sheet(
    classeur,
    feuille(hypotheses, [42, ...evalues.map(() => 32)]),
    'Hypothèses',
  );

  return XLSX.write(classeur, { type: 'buffer', bookType: 'xlsx' }) as Buffer;
}
