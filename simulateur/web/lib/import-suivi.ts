import * as XLSX from 'xlsx';
import type { Referentiel, Secteur, Zone } from '@sim/engine';
import { construireMatrice, fournisseurGeometrique } from '@sim/engine';
import { REFERENTIELS } from '@sim/data';

/**
 * Lecture du classeur « suivi des volumes PROD ».
 *
 * L'import ne fournit que les volumes : le classeur ne porte ni coordonnées, ni
 * zones, ni distances. Ces éléments sont repris du référentiel déjà connu pour
 * le département, et les secteurs qu'il ne connaît pas sont signalés plutôt que
 * devinés — un secteur sans coordonnées ne peut pas entrer dans un calcul de
 * kilomètres.
 */

const ONGLET = 'Suivi des volumes PROD';

const COLONNES = {
  secteur: 'Secteur GRDV',
  departement: 'Département',
  interOctobre: "Nbr d'inter Octobre",
  moyJrOctobre: 'Moy/JR (octobre)',
  interMars: "Nbr d'inter mars",
  moyJrMars: 'Moy/JR (mars)',
  b2bMois: 'Nbr B2B Mois',
} as const;

export interface ResultatImport {
  readonly departement: string;
  readonly referentiel: Referentiel;
  /** Secteurs du classeur absents du référentiel : ni coordonnées ni zone. */
  readonly inconnus: readonly string[];
  /** Secteurs du référentiel absents du classeur : volumes laissés inchangés. */
  readonly manquants: readonly string[];
  readonly misAJour: number;
  readonly dateMaj: string | null;
}

/** Nom court, insensible aux accents et à la casse, pour rapprocher les libellés. */
function normaliser(libelle: string): string {
  return String(libelle)
    .split(' - ')
    .pop()!
    .trim()
    .toUpperCase()
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '');
}

const nombreOuZero = (valeur: unknown): number => {
  const n = typeof valeur === 'number' ? valeur : Number.parseFloat(String(valeur ?? ''));
  return Number.isFinite(n) ? n : 0;
};

/**
 * Date de mise à jour, portée par la ligne d'en-tête et non par une colonne :
 * la cellule « Date MAJ : » est suivie de la valeur, sur la même ligne.
 */
function lireDateMaj(feuille: XLSX.WorkSheet): string | null {
  const etendue = feuille['!ref'];
  if (!etendue) return null;
  const { s, e } = XLSX.utils.decode_range(etendue);
  for (let colonne = s.c; colonne < e.c; colonne++) {
    const cellule = feuille[XLSX.utils.encode_cell({ r: s.r, c: colonne })];
    if (!cellule || !/date\s*maj/i.test(String(cellule.v ?? ''))) continue;
    const voisine = feuille[XLSX.utils.encode_cell({ r: s.r, c: colonne + 1 })];
    if (!voisine?.v) return null;
    return voisine.v instanceof Date ? voisine.v.toISOString() : String(voisine.v);
  }
  return null;
}

export function importerSuivi(donnees: ArrayBuffer, departement: string): ResultatImport {
  const classeur = XLSX.read(donnees, { type: "array", cellDates: true });
  const feuille = classeur.Sheets[ONGLET] ?? classeur.Sheets[classeur.SheetNames[0]!];
  if (!feuille) throw new Error(`Onglet « ${ONGLET} » introuvable dans le classeur.`);

  const lignes = XLSX.utils.sheet_to_json<Record<string, unknown>>(feuille, { defval: null });
  if (lignes.length === 0) throw new Error('Le classeur ne contient aucune ligne.');

  const entetes = Object.keys(lignes[0]!);
  const absentes = Object.values(COLONNES).filter((c) => !entetes.includes(c));
  if (absentes.length > 0) {
    throw new Error(`Colonnes manquantes dans le classeur : ${absentes.join(', ')}.`);
  }

  const base = REFERENTIELS[departement];
  if (!base) {
    throw new Error(
      `Aucun référentiel géographique pour le département ${departement}. ` +
        `Les volumes seuls ne suffisent pas : il manque les coordonnées et les zones.`,
    );
  }

  const duClasseur = new Map<string, Record<string, unknown>>();
  for (const ligne of lignes) {
    if (String(ligne[COLONNES.departement] ?? '').trim() !== departement) continue;
    const libelle = ligne[COLONNES.secteur];
    if (!libelle) continue;
    duClasseur.set(normaliser(String(libelle)), ligne);
  }

  const connus = new Set(base.secteurs.map((s) => normaliser(s.libelleGrdv)));
  const inconnus = [...duClasseur.keys()].filter((k) => !connus.has(k)).sort();

  const manquants: string[] = [];
  let misAJour = 0;

  const secteurs: Secteur[] = base.secteurs.map((secteur) => {
    const ligne = duClasseur.get(normaliser(secteur.libelleGrdv));
    if (!ligne) {
      manquants.push(secteur.nom);
      return secteur;
    }
    misAJour++;
    return {
      ...secteur,
      volume: {
        interOctobre: nombreOuZero(ligne[COLONNES.interOctobre]),
        interMars: nombreOuZero(ligne[COLONNES.interMars]),
        b2bMois: nombreOuZero(ligne[COLONNES.b2bMois]),
        moyJrOctobre: nombreOuZero(ligne[COLONNES.moyJrOctobre]),
        moyJrMars: nombreOuZero(ligne[COLONNES.moyJrMars]),
      },
    };
  });

  // Les distances suivent les coordonnées, qui n'ont pas bougé : on les reprend.
  const distances =
    Object.keys(base.distances).length > 0
      ? base.distances
      : construireMatrice(secteurs, fournisseurGeometrique(secteurs));

  const dateBrute = lireDateMaj(feuille);

  return {
    departement,
    referentiel: { ...base, secteurs, distances } satisfies Referentiel,
    inconnus,
    manquants,
    misAJour,
    dateMaj: dateBrute ? String(dateBrute) : null,
  };
}

export type { Zone };
