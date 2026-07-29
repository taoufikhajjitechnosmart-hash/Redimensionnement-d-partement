import type { MatriceDistances, Secteur } from './types';

/**
 * Distances entre secteurs.
 *
 * L'interface isole le reste du moteur de la façon dont la distance est
 * obtenue. L'implémentation par défaut est une approximation géométrique ;
 * un fournisseur adossé à un service d'itinéraires se substitue à elle sans
 * qu'aucun calcul en amont ne change.
 */
export interface FournisseurDistances {
  readonly nom: string;
  /** Distance de `a` vers `b` en kilomètres. */
  km(a: string, b: string): number;
  /** Vraie si les distances sont des estimations géométriques. */
  readonly estApproximation: boolean;
}

/** Rayon terrestre moyen, en kilomètres. */
const RAYON_TERRE = 6371;

/** Facteur de sinuosité appliqué au vol d'oiseau pour approcher la route. */
export const FACTEUR_ROUTIER = 1.25;

const rad = (deg: number): number => (deg * Math.PI) / 180;

/** Distance orthodromique, en kilomètres. */
export function orthodromique(
  a: { lat: number; lon: number },
  b: { lat: number; lon: number },
): number {
  const dLat = rad(b.lat - a.lat);
  const dLon = rad(b.lon - a.lon);
  const h =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(rad(a.lat)) * Math.cos(rad(b.lat)) * Math.sin(dLon / 2) ** 2;
  return 2 * RAYON_TERRE * Math.asin(Math.min(1, Math.sqrt(h)));
}

/** Vol d'oiseau majoré du facteur de sinuosité. */
export function distanceApprochee(
  a: { lat: number; lon: number },
  b: { lat: number; lon: number },
  facteur = FACTEUR_ROUTIER,
): number {
  return orthodromique(a, b) * facteur;
}

/** Calcule les distances à la volée depuis les coordonnées des secteurs. */
export function fournisseurGeometrique(
  secteurs: readonly Secteur[],
  facteur = FACTEUR_ROUTIER,
): FournisseurDistances {
  const index = new Map(secteurs.map((s) => [s.id, s]));
  return {
    nom: `Orthodromique × ${facteur}`,
    estApproximation: true,
    km(a, b) {
      if (a === b) return 0;
      const sa = index.get(a);
      const sb = index.get(b);
      if (!sa || !sb) throw new RangeError(`Secteur inconnu : ${!sa ? a : b}`);
      return distanceApprochee(sa, sb, facteur);
    },
  };
}

/** Lit une matrice fournie, sans recalcul. */
export function fournisseurMatrice(
  matrice: MatriceDistances,
  nom = 'Matrice fournie',
  estApproximation = true,
): FournisseurDistances {
  return {
    nom,
    estApproximation,
    km(a, b) {
      if (a === b) return 0;
      const valeur = matrice[a]?.[b] ?? matrice[b]?.[a];
      if (valeur === undefined) throw new RangeError(`Distance absente : ${a} → ${b}`);
      return valeur;
    },
  };
}

/** Matrice complète, symétrique, calculée depuis un fournisseur. */
export function construireMatrice(
  secteurs: readonly Secteur[],
  fournisseur: FournisseurDistances,
): MatriceDistances {
  const matrice: Record<string, Record<string, number>> = {};
  for (const a of secteurs) {
    matrice[a.id] = {};
    for (const b of secteurs) {
      matrice[a.id]![b.id] = a.id === b.id ? 0 : Math.round(fournisseur.km(a.id, b.id));
    }
  }
  return matrice;
}
