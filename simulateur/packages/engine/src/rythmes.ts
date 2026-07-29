/**
 * Règle J+2 — le cœur du modèle.
 *
 * Un secteur respecte le J+2 si l'écart entre deux passages consécutifs n'excède
 * jamais 2 jours ouvrés, en calcul cyclique sur la semaine : le lundi suit le
 * vendredi en régime de 5 jours, le samedi en régime de 6 jours.
 */

export const NOMS_JOURS = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi'] as const;

/** 0 = lundi … 5 = samedi. */
export type Jour = 0 | 1 | 2 | 3 | 4 | 5;

/** Nombre de jours ouvrés dans la semaine. */
export type Regime = 5 | 6;

/** Écart maximal toléré, en jours ouvrés, entre deux passages consécutifs. */
export const ECART_MAX_J2 = 2;

export const estJour = (n: number): n is Jour => Number.isInteger(n) && n >= 0 && n <= 5;

/**
 * Écart maximal entre deux passages consécutifs, en cyclique sur la semaine.
 *
 * Transcription fidèle du moteur de référence : les jours sont triés puis
 * décalés en base 1, et le dernier écart reboucle sur le premier jour de la
 * semaine suivante.
 *
 * Un secteur jamais visité renvoie `Infinity` — il ne peut être conforme.
 * Un secteur visité une seule fois renvoie `regime`, l'écart d'un tour complet.
 */
export function ecartMax(jours: readonly Jour[], regime: Regime): number {
  if (jours.length === 0) return Number.POSITIVE_INFINITY;

  const distincts = [...new Set(jours)].sort((a, b) => a - b);
  const horsRegime = distincts.find((j) => j >= regime);
  if (horsRegime !== undefined) {
    throw new RangeError(
      `${NOMS_JOURS[horsRegime]} n'existe pas dans un régime de ${regime} jours.`,
    );
  }

  const p = distincts.map((x) => x + 1);
  let max = 0;
  for (let i = 0; i < p.length; i++) {
    const ecart = i + 1 < p.length ? p[i + 1]! - p[i]! : p[0]! + regime - p[i]!;
    if (ecart > max) max = ecart;
  }
  return max;
}

/** Un rythme de passage tient-il le J+2 ? */
export function conformeJ2(jours: readonly Jour[], regime: Regime): boolean {
  return ecartMax(jours, regime) <= ECART_MAX_J2;
}

/** Tous les rythmes de `nbPassages` jours qui tiennent le J+2, dans l'ordre lexicographique. */
export function rythmesValides(regime: Regime, nbPassages: number): Jour[][] {
  if (!Number.isInteger(nbPassages) || nbPassages < 0) {
    throw new RangeError('Le nombre de passages doit être un entier positif.');
  }
  if (nbPassages > regime) return [];

  const valides: Jour[][] = [];
  const courant: Jour[] = [];

  const explorer = (debut: number): void => {
    if (courant.length === nbPassages) {
      if (conformeJ2(courant, regime)) valides.push([...courant]);
      return;
    }
    // Élaguer : il ne reste pas assez de jours pour compléter le rythme.
    if (regime - debut < nbPassages - courant.length) return;
    for (let j = debut; j < regime; j++) {
      courant.push(j as Jour);
      explorer(j + 1);
      courant.pop();
    }
  };

  explorer(0);
  return valides;
}

/**
 * Nombre minimal de passages hebdomadaires permettant de tenir le J+2.
 * Vaut 3 dans les deux régimes — c'est la conséquence structurelle de la règle.
 */
export function passagesMinimum(regime: Regime): number {
  for (let n = 1; n <= regime; n++) {
    if (rythmesValides(regime, n).length > 0) return n;
  }
  throw new Error(`Aucun rythme conforme dans un régime de ${regime} jours.`);
}

/** Deux rythmes n'ayant aucun jour en commun : un technicien peut porter les deux. */
export function sontDisjoints(a: readonly Jour[], b: readonly Jour[]): boolean {
  const set = new Set(a);
  return !b.some((j) => set.has(j));
}

/**
 * Paires de rythmes valides sans jour commun.
 *
 * En 6 jours, `[Lun-Mer-Ven, Mar-Jeu-Sam]` est la seule paire : les deux rythmes
 * valides sont exactement complémentaires. En 5 jours il n'en existe aucune —
 * 3 + 3 = 6 dépasse la semaine — donc un technicien couvrant deux secteurs sera
 * réclamé deux fois le même jour au moins une fois par semaine.
 */
export function pairesDisjointes(regime: Regime, nbPassages: number): [Jour[], Jour[]][] {
  const rythmes = rythmesValides(regime, nbPassages);
  const paires: [Jour[], Jour[]][] = [];
  for (let i = 0; i < rythmes.length; i++) {
    for (let j = i + 1; j < rythmes.length; j++) {
      if (sontDisjoints(rythmes[i]!, rythmes[j]!)) paires.push([rythmes[i]!, rythmes[j]!]);
    }
  }
  return paires;
}

/** « Lu/Me/Ve » — la notation des plannings. */
export function formaterRythme(jours: readonly Jour[]): string {
  return [...jours]
    .sort((a, b) => a - b)
    .map((j) => NOMS_JOURS[j].slice(0, 2))
    .join('/');
}

/** Lit « Lu/Me/Ve », « Lun-Mer-Ven », « Lu Me Ve ». */
export function lireRythme(texte: string): Jour[] {
  const jetons = texte.split(/[\s/,;.-]+/).filter(Boolean);
  return jetons.map((jeton) => {
    const cible = jeton.slice(0, 2).toLowerCase();
    const index = NOMS_JOURS.findIndex((nom) => nom.slice(0, 2).toLowerCase() === cible);
    if (index < 0) throw new RangeError(`Jour non reconnu : « ${jeton} »`);
    return index as Jour;
  });
}
