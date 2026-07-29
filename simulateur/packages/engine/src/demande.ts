/**
 * Conversion des volumes mensuels en demande hebdomadaire.
 *
 * Tout est paramétrable et rien n'est figé : c'est ici que se logent les écarts
 * entre les analyses successives. Deux études du même département ont conclu
 * l'une à 141 interventions PROD par semaine, l'autre à 185, à partir des mêmes
 * lignes de suivi. Les paramètres ci-dessous rendent l'écart explicite et
 * reproductible au lieu de le laisser dans le code.
 */

/** Volumes bruts d'un secteur, tels qu'ils figurent dans le fichier de suivi. */
export interface VolumeSecteur {
  /** Nombre d'interventions sur le mois d'octobre. */
  readonly interOctobre: number;
  /** Nombre d'interventions sur le mois de mars. */
  readonly interMars: number;
  /** Nombre d'interventions B2B sur le mois. */
  readonly b2bMois: number;
  /** Moyenne par jour ouvré déclarée pour octobre. */
  readonly moyJrOctobre: number;
  /** Moyenne par jour ouvré déclarée pour mars. */
  readonly moyJrMars: number;
}

/** Mois de référence retenu pour dimensionner. */
export type ChoixMois = 'octobre' | 'mars' | 'moyenne' | 'pic';

/**
 * Deux façons d'aller du mois à la semaine.
 *
 * `volume-mensuel` divise le nombre d'interventions du mois par le nombre de
 * semaines : c'est la conversion arithmétiquement fidèle, indépendante du
 * nombre de jours travaillés.
 *
 * `moyenne-journaliere` repart de la moyenne par jour et la reprojette sur un
 * nombre de jours ouvrés choisi. Cette voie est sensible à ce choix : les mois
 * du fichier de suivi comptent 25 jours (octobre) et 24 jours (mars), si bien
 * qu'une projection sur 22 jours minore la demande d'environ 12 %.
 */
export type MethodeConversion = 'volume-mensuel' | 'moyenne-journaliere';

export interface ParamsDemande {
  readonly mois: ChoixMois;
  readonly methode: MethodeConversion;
  /** Semaines par mois. 4,333 = 52 / 12. */
  readonly semainesParMois: number;
  /** Jours ouvrés par mois — utilisé par `moyenne-journaliere` seulement. */
  readonly joursOuvresParMois: number;
  /** Compter les interventions B2B dans la demande. */
  readonly inclureB2B: boolean;
  /** Marge de flexibilité. 0 = aucune, 0,10 = +10 %. */
  readonly margeFlexibilite: number;
}

export const SEMAINES_PAR_MOIS = 52 / 12; // 4,3333…

/**
 * Conversion fidèle au fichier de suivi : volume du mois le plus chargé, B2B
 * inclus, plus 10 % de flexibilité. Donne 185,3 interventions par semaine sur
 * le département 41.
 */
export const PARAMS_VOLUME_PIC: ParamsDemande = {
  mois: 'pic',
  methode: 'volume-mensuel',
  semainesParMois: 4.333,
  joursOuvresParMois: 22,
  inclureB2B: true,
  margeFlexibilite: 0.1,
};

/**
 * Paramétrage de l'étude antérieure : moyenne des deux mois, reprojetée sur un
 * mois de 22 jours ouvrés, hors B2B et sans marge. Donne 141 interventions par
 * semaine. Conservé pour comparaison — la projection sur 22 jours contredit les
 * 25 et 24 jours effectifs des mois relevés.
 */
export const PARAMS_MOYENNE_22J: ParamsDemande = {
  mois: 'moyenne',
  methode: 'moyenne-journaliere',
  semainesParMois: 4.333,
  joursOuvresParMois: 22,
  inclureB2B: false,
  margeFlexibilite: 0,
};

/** Volume mensuel retenu, avant conversion. */
export function volumeMensuel(v: VolumeSecteur, params: ParamsDemande): number {
  const base = ((): number => {
    switch (params.mois) {
      case 'octobre':
        return v.interOctobre;
      case 'mars':
        return v.interMars;
      case 'pic':
        return Math.max(v.interOctobre, v.interMars);
      case 'moyenne':
        return (v.interOctobre + v.interMars) / 2;
    }
  })();
  return base + (params.inclureB2B ? v.b2bMois : 0);
}

/** Moyenne par jour ouvré retenue, avant conversion. */
export function moyenneJournaliere(v: VolumeSecteur, params: ParamsDemande): number {
  const base = ((): number => {
    switch (params.mois) {
      case 'octobre':
        return v.moyJrOctobre;
      case 'mars':
        return v.moyJrMars;
      case 'pic':
        return Math.max(v.moyJrOctobre, v.moyJrMars);
      case 'moyenne':
        return (v.moyJrOctobre + v.moyJrMars) / 2;
    }
  })();
  const b2bJournalier = v.b2bMois / params.joursOuvresParMois;
  return base + (params.inclureB2B ? b2bJournalier : 0);
}

/** Demande hebdomadaire d'un secteur, marge comprise. */
export function demandeHebdo(v: VolumeSecteur, params: ParamsDemande): number {
  const brut =
    params.methode === 'volume-mensuel'
      ? volumeMensuel(v, params) / params.semainesParMois
      : (moyenneJournaliere(v, params) * params.joursOuvresParMois) / params.semainesParMois;
  return brut * (1 + params.margeFlexibilite);
}

/**
 * Jours ouvrés implicites du fichier source, par secteur et par mois.
 *
 * Rapport entre le volume du mois et la moyenne journalière déclarée. Sert de
 * garde-fou : si le résultat s'écarte nettement du `joursOuvresParMois` retenu,
 * la conversion `moyenne-journaliere` déforme la demande.
 */
export function joursOuvresImplicites(v: VolumeSecteur): { octobre: number; mars: number } {
  return {
    octobre: v.moyJrOctobre > 0 ? v.interOctobre / v.moyJrOctobre : Number.NaN,
    mars: v.moyJrMars > 0 ? v.interMars / v.moyJrMars : Number.NaN,
  };
}
