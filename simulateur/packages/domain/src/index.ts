import { z } from 'zod';

/**
 * Contrat de données des scénarios.
 *
 * Le schéma porte un numéro de version : un scénario enregistré aujourd'hui
 * doit rester lisible après une évolution du modèle. Toute modification de
 * forme s'accompagne d'une migration dans `migrerScenario`.
 */
export const VERSION_SCHEMA = 1;

export const jourSchema = z.union([
  z.literal(0),
  z.literal(1),
  z.literal(2),
  z.literal(3),
  z.literal(4),
  z.literal(5),
]);

export const regimeSchema = z.union([z.literal(5), z.literal(6)]);

export const paramsDemandeSchema = z.object({
  mois: z.enum(['octobre', 'mars', 'moyenne', 'pic']),
  methode: z.enum(['volume-mensuel', 'moyenne-journaliere']),
  semainesParMois: z.number().positive().max(6),
  joursOuvresParMois: z.number().positive().max(31),
  inclureB2B: z.boolean(),
  margeFlexibilite: z.number().min(0).max(1),
});

export const offreSecteurSchema = z.object({
  secteurId: z.string().min(1),
  jours: z.array(jourSchema).max(6),
  creneaux: z.number().int().min(0).max(1000),
});

export const scenarioSchema = z.object({
  id: z.string().min(1),
  nom: z.string().min(1).max(120),
  departement: z.string().min(1).max(3),
  regime: regimeSchema,
  capaciteParTechJour: z.number().int().min(1).max(24),
  creneauxDemiJournee: z.tuple([z.number().int().min(0), z.number().int().min(0)]),
  creneauxJournee: z.tuple([z.number().int().min(0), z.number().int().min(0)]),
  maxSecteursParTechJour: z.number().int().min(1).max(6),
  distanceMaxEnchainement: z.number().min(0).max(500),
  paramsDemande: paramsDemandeSchema,
  couvertureCible: z.number().min(0.5).max(5),
  offres: z.array(offreSecteurSchema),
});

/** Enveloppe de persistance : le scénario plus ses métadonnées. */
export const scenarioEnregistreSchema = z.object({
  version: z.number().int().positive(),
  scenario: scenarioSchema,
  creeLe: z.string().datetime(),
  modifieLe: z.string().datetime(),
  note: z.string().max(2000).optional(),
});

export type Jour = z.infer<typeof jourSchema>;
export type Regime = z.infer<typeof regimeSchema>;
export type ParamsDemande = z.infer<typeof paramsDemandeSchema>;
export type OffreSecteur = z.infer<typeof offreSecteurSchema>;
export type Scenario = z.infer<typeof scenarioSchema>;
export type ScenarioEnregistre = z.infer<typeof scenarioEnregistreSchema>;

/** Cohérences que le schéma seul n'exprime pas. */
export function verifierCoherence(scenario: Scenario): string[] {
  const erreurs: string[] = [];
  const [minDemi, maxDemi] = scenario.creneauxDemiJournee;
  const [minJour, maxJour] = scenario.creneauxJournee;

  if (minDemi > maxDemi) erreurs.push('Demi-journée : le minimum dépasse le maximum.');
  if (minJour > maxJour) erreurs.push('Journée : le minimum dépasse le maximum.');
  if (maxJour > scenario.capaciteParTechJour) {
    erreurs.push(
      `Une journée peut aller jusqu'à ${maxJour} créneaux alors que la capacité est de ${scenario.capaciteParTechJour}.`,
    );
  }
  for (const offre of scenario.offres) {
    const horsRegime = offre.jours.filter((j) => j >= scenario.regime);
    if (horsRegime.length > 0) {
      erreurs.push(
        `Secteur ${offre.secteurId} : passage programmé hors du régime de ${scenario.regime} jours.`,
      );
    }
    if (new Set(offre.jours).size !== offre.jours.length) {
      erreurs.push(`Secteur ${offre.secteurId} : jour de passage en double.`);
    }
  }
  const ids = scenario.offres.map((o) => o.secteurId);
  if (new Set(ids).size !== ids.length) erreurs.push('Un secteur apparaît deux fois dans l’offre.');

  return erreurs;
}

/** Amène un enregistrement quelconque à la version courante du schéma. */
export function migrerScenario(brut: unknown): ScenarioEnregistre {
  const enveloppe = scenarioEnregistreSchema.parse(brut);
  if (enveloppe.version > VERSION_SCHEMA) {
    throw new Error(
      `Scénario en version ${enveloppe.version}, cette application lit jusqu'à la ${VERSION_SCHEMA}.`,
    );
  }
  // Aucune migration nécessaire tant que le schéma n'a pas évolué.
  return { ...enveloppe, version: VERSION_SCHEMA };
}
