import { lireRythme, PARAMS_VOLUME_PIC, type Scenario } from '@sim/engine';

/**
 * Préréglages du département 41.
 *
 * L'existant est le planning relevé au 29 juillet 2026 ; les deux cibles sont
 * issues de l'étude de rezonage. Ils servent de points de comparaison, pas de
 * vérité : les paramètres de demande restent modifiables dans l'interface.
 */

interface LigneGrille {
  readonly secteurId: string;
  readonly creneaux: number;
  readonly rythme: string;
}

/** Planning relevé. Cinq secteurs n'y tiennent pas le J+2. */
const EXISTANT: readonly LigneGrille[] = [
  { secteurId: '41018', creneaux: 78, rythme: 'Lu/Ma/Me/Je/Ve/Sa' },
  { secteurId: '41180', creneaux: 30, rythme: 'Lu/Ma/Me/Je/Ve' },
  { secteurId: '41077', creneaux: 30, rythme: 'Lu/Ma/Me/Je/Sa' },
  { secteurId: '41071', creneaux: 29, rythme: 'Lu/Ma/Me/Je/Ve/Sa' },
  { secteurId: '41142', creneaux: 24, rythme: 'Lu/Ma/Me/Je/Ve' },
  { secteurId: '41149', creneaux: 12, rythme: 'Me/Ve' },
  { secteurId: '41157', creneaux: 24, rythme: 'Ma/Je' },
  { secteurId: '41269', creneaux: 18, rythme: 'Lu/Ve/Sa' },
  { secteurId: '41194', creneaux: 18, rythme: 'Lu/Me/Ve' },
  { secteurId: '41296', creneaux: 12, rythme: 'Ma/Je' },
  { secteurId: '41060', creneaux: 12, rythme: 'Ma/Je' },
  { secteurId: '41084', creneaux: 24, rythme: 'Lu/Me/Ve/Sa' },
];

/** Cible en semaine de six jours. */
const CIBLE_6J: readonly LigneGrille[] = [
  { secteurId: '41018', creneaux: 64, rythme: 'Lu/Ma/Me/Je/Ve/Sa' },
  { secteurId: '41180', creneaux: 24, rythme: 'Lu/Ma/Me/Je/Ve/Sa' },
  { secteurId: '41077', creneaux: 14, rythme: 'Ma/Je/Sa' },
  { secteurId: '41071', creneaux: 14, rythme: 'Ma/Je/Sa' },
  { secteurId: '41142', creneaux: 12, rythme: 'Lu/Me/Ve' },
  { secteurId: '41149', creneaux: 12, rythme: 'Lu/Me/Ve' },
  { secteurId: '41157', creneaux: 12, rythme: 'Lu/Me/Ve' },
  { secteurId: '41269', creneaux: 10, rythme: 'Lu/Me/Ve' },
  { secteurId: '41194', creneaux: 10, rythme: 'Ma/Je/Sa' },
  { secteurId: '41296', creneaux: 9, rythme: 'Lu/Me/Ve' },
  { secteurId: '41060', creneaux: 5, rythme: 'Ma/Je/Sa' },
  { secteurId: '41084', creneaux: 4, rythme: 'Ma/Je/Sa' },
];

/** Cible en semaine de cinq jours. */
const CIBLE_5J: readonly LigneGrille[] = [
  { secteurId: '41018', creneaux: 64, rythme: 'Lu/Ma/Me/Je/Ve' },
  { secteurId: '41180', creneaux: 24, rythme: 'Lu/Ma/Me/Je/Ve' },
  { secteurId: '41077', creneaux: 14, rythme: 'Ma/Je/Ve' },
  { secteurId: '41071', creneaux: 14, rythme: 'Ma/Je/Ve' },
  { secteurId: '41142', creneaux: 12, rythme: 'Lu/Me/Ve' },
  { secteurId: '41149', creneaux: 12, rythme: 'Lu/Ma/Je' },
  { secteurId: '41157', creneaux: 12, rythme: 'Lu/Me/Ve' },
  { secteurId: '41269', creneaux: 10, rythme: 'Lu/Me/Ve' },
  { secteurId: '41194', creneaux: 10, rythme: 'Ma/Je/Ve' },
  { secteurId: '41296', creneaux: 9, rythme: 'Lu/Me/Je' },
  { secteurId: '41060', creneaux: 5, rythme: 'Ma/Me/Ve' },
  { secteurId: '41084', creneaux: 4, rythme: 'Ma/Je/Ve' },
];

const REGLES = {
  departement: '41',
  capaciteParTechJour: 6,
  creneauxDemiJournee: [1, 3] as const,
  creneauxJournee: [4, 6] as const,
  maxSecteursParTechJour: 2,
  distanceMaxEnchainement: 60,
  paramsDemande: PARAMS_VOLUME_PIC,
  couvertureCible: 1.1,
} satisfies Partial<Scenario>;

const batir = (
  id: string,
  nom: string,
  regime: 5 | 6,
  grille: readonly LigneGrille[],
): Scenario => ({
  ...REGLES,
  id,
  nom,
  regime,
  offres: grille.map((l) => ({
    secteurId: l.secteurId,
    jours: lireRythme(l.rythme),
    creneaux: l.creneaux,
  })),
});

export const SCENARIO_EXISTANT_41 = batir(
  '41-existant',
  'Existant — planning relevé',
  6,
  EXISTANT,
);
export const SCENARIO_CIBLE_6J_41 = batir('41-cible-6j', 'Cible — semaine de 6 jours', 6, CIBLE_6J);
export const SCENARIO_CIBLE_5J_41 = batir('41-cible-5j', 'Cible — semaine de 5 jours', 5, CIBLE_5J);

export const SCENARIOS_41: readonly Scenario[] = [
  SCENARIO_EXISTANT_41,
  SCENARIO_CIBLE_6J_41,
  SCENARIO_CIBLE_5J_41,
];
