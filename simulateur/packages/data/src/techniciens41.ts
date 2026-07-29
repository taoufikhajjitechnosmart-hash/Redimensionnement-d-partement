import type { Technicien } from '@sim/engine';

/**
 * Effectif relevé au 29 juillet 2026.
 *
 * `zoneId` n'est renseigné que lorsque tous les secteurs habituels du technicien
 * appartiennent à la même zone. Un technicien à cheval sur deux zones, ou sans
 * secteur attitré, reste sans rattachement : le solveur le traite alors comme un
 * renfort mobile plutôt que de lui inventer une base.
 */
export const TECHNICIENS_41: readonly Technicien[] = [
  { id: 'khlili', nom: 'Ahmed Khlili', societe: 'MK COM', activite: 'MIXTE', regime: 6, zoneId: 'Z2' },
  { id: 'ghrab', nom: 'Amine Ghrab', societe: 'MK COM', activite: 'MIXTE', regime: 6, zoneId: 'Z2' },
  { id: 'zagrouba', nom: 'Zouhaier Zagrouba', societe: 'MK COM', activite: 'MIXTE', regime: 6, zoneId: 'Z3' },
  { id: 'sevinc', nom: 'Melik Sevinc', societe: 'ACN', activite: 'PROD', regime: 5, zoneId: 'Z1' },
  { id: 'aktan', nom: 'Muhammet Aktan', societe: 'ACN', activite: 'MIXTE', regime: 5, zoneId: 'Z3' },
  { id: 'hardoud', nom: 'Naser Hardoud', societe: 'ACN', activite: 'MIXTE', regime: 5, zoneId: 'Z1' },
  { id: 'hajji', nom: 'Rachid Hajji', societe: 'ACN', activite: 'SAV', regime: 5, zoneId: 'Z1' },
  // Mur-de-Sologne (Sologne) et Valencisse (Val de Loire) : à cheval sur deux zones.
  { id: 'hassine', nom: 'Zied Hassine', societe: 'MK COM', activite: 'MIXTE', regime: 5 },
  { id: 'inci', nom: 'Fatih Inci', societe: 'ACN', activite: 'MIXTE', regime: 6, zoneId: 'Z1' },
  { id: 'caglar', nom: 'Mustafa Caglar', societe: 'ACN', activite: 'PROD', regime: 6, zoneId: 'Z1' },
  { id: 'laprasse', nom: 'Hamdani Laprasse', societe: 'TS', activite: 'MIXTE', regime: 5 },
];

/** Secteurs habituels de chaque technicien, tels que relevés. Indicatif. */
export const SECTEURS_HABITUELS_41: Readonly<Record<string, readonly string[]>> = {
  khlili: ['41077', '41149'],
  ghrab: ['41060', '41149', '41269'],
  zagrouba: ['41084', '41296'],
  sevinc: ['41018'],
  aktan: ['41157', '41194'],
  hardoud: ['41180'],
  hajji: ['41018', '41142'],
  hassine: ['41157', '41142'],
  inci: ['41071'],
  caglar: ['41018'],
  laprasse: [],
};
