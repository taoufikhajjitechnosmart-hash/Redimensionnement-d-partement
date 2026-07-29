import type { Jour, Regime } from './rythmes';
import type { ParamsDemande, VolumeSecteur } from './demande';

/** Un secteur GRDV. L'identifiant est le code INSEE de la commune support. */
export interface Secteur {
  readonly id: string;
  readonly nom: string;
  readonly libelleGrdv: string;
  readonly departement: string;
  readonly lat: number;
  readonly lon: number;
  readonly zoneId: string;
  readonly volume: VolumeSecteur;
}

/** Un regroupement de secteurs autour d'une base de départ. */
export interface Zone {
  readonly id: string;
  readonly nom: string;
  /** Secteur servant de point de départ des tournées. */
  readonly baseSecteurId: string;
}

/** Distances routières entre secteurs, en kilomètres, indexées par identifiant. */
export type MatriceDistances = Readonly<Record<string, Readonly<Record<string, number>>>>;

/** Le socle de données d'un département : ce qui ne dépend d'aucun scénario. */
export interface Referentiel {
  readonly departement: string;
  readonly libelle: string;
  readonly secteurs: readonly Secteur[];
  readonly zones: readonly Zone[];
  readonly distances: MatriceDistances;
}

/** L'offre ouverte sur un secteur : combien de créneaux, quels jours. */
export interface OffreSecteur {
  readonly secteurId: string;
  readonly jours: readonly Jour[];
  /** Total hebdomadaire, réparti sur les jours de passage. */
  readonly creneaux: number;
}

/** Une hypothèse de dimensionnement, entièrement décrite par ses paramètres. */
export interface Scenario {
  readonly id: string;
  readonly nom: string;
  readonly departement: string;
  readonly regime: Regime;
  /** Créneaux qu'un technicien absorbe en une journée. */
  readonly capaciteParTechJour: number;
  /** Bornes d'une vacation, utilisées par le validateur d'affectation. */
  readonly creneauxDemiJournee: readonly [number, number];
  readonly creneauxJournee: readonly [number, number];
  /** Secteurs distincts qu'un technicien peut enchaîner dans la journée. */
  readonly maxSecteursParTechJour: number;
  /** Distance maximale entre deux secteurs enchaînés le même jour, en km. */
  readonly distanceMaxEnchainement: number;
  readonly paramsDemande: ParamsDemande;
  /** Couverture visée : 1,10 = 10 % d'offre au-delà de la demande. */
  readonly couvertureCible: number;
  readonly offres: readonly OffreSecteur[];
}

export interface ResultatSecteur {
  readonly secteurId: string;
  readonly nom: string;
  readonly zoneId: string;
  readonly demandeHebdo: number;
  readonly offre: number;
  /** Offre rapportée à la demande. `Infinity` si la demande est nulle. */
  readonly couverture: number;
  readonly jours: readonly Jour[];
  readonly nbPassages: number;
  readonly ecartMax: number;
  readonly conformeJ2: boolean;
  readonly couvertureSuffisante: boolean;
  /** Créneaux ouverts jour par jour, du lundi au samedi. */
  readonly creneauxParJour: readonly number[];
  readonly kmSemaine: number;
}

export type GraviteAlerte = 'critique' | 'avertissement';

export interface Alerte {
  readonly secteurId: string;
  readonly nom: string;
  readonly gravite: GraviteAlerte;
  readonly code: 'delai-j2' | 'couverture' | 'capacite-jour';
  readonly message: string;
}

export interface Resultat {
  readonly scenarioId: string;
  readonly offreTotale: number;
  readonly demandeTotale: number;
  readonly couverture: number;
  readonly alertes: readonly Alerte[];
  readonly nbAlertesJ2: number;
  readonly effectifMinimum: number;
  readonly effectifSamedi: number;
  readonly capaciteTotale: number;
  readonly occupation: number;
  readonly kmSemaine: number;
  readonly chargeParJour: readonly number[];
  readonly effectifParZone: Readonly<Record<string, number>>;
  readonly secteurs: readonly ResultatSecteur[];
}

export type { Jour, Regime, ParamsDemande, VolumeSecteur };
