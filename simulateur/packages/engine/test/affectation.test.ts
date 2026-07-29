import { describe, expect, it } from 'vitest';
import { construireAffectation, validerAffectation, type Technicien } from '../src/affectation';
import { PARAMS_VOLUME_PIC } from '../src/demande';
import { lireRythme } from '../src/rythmes';
import type { Scenario } from '../src/types';
import { REFERENTIEL_41 } from '@sim/data';

const SCENARIO: Scenario = {
  id: 'test',
  nom: 'Test',
  departement: '41',
  regime: 6,
  capaciteParTechJour: 6,
  creneauxDemiJournee: [1, 3],
  creneauxJournee: [4, 6],
  maxSecteursParTechJour: 2,
  distanceMaxEnchainement: 60,
  paramsDemande: PARAMS_VOLUME_PIC,
  couvertureCible: 1.1,
  offres: REFERENTIEL_41.secteurs.map((s) => ({
    secteurId: s.id,
    jours: lireRythme(s.zoneId === 'Z2' ? 'Ma/Je/Sa' : 'Lu/Me/Ve'),
    creneaux: 12,
  })),
};

const TECHS: Technicien[] = [
  { id: 'T1', nom: 'T1', societe: 'ACN', activite: 'MIXTE', regime: 6, zoneId: 'Z1' },
  { id: 'T2', nom: 'T2', societe: 'ACN', activite: 'MIXTE', regime: 6, zoneId: 'Z1' },
  { id: 'T3', nom: 'T3', societe: 'MK COM', activite: 'MIXTE', regime: 6, zoneId: 'Z2' },
  { id: 'T4', nom: 'T4', societe: 'MK COM', activite: 'MIXTE', regime: 6, zoneId: 'Z2' },
  { id: 'T5', nom: 'T5', societe: 'ACN', activite: 'MIXTE', regime: 6, zoneId: 'Z3' },
  { id: 'T6', nom: 'T6', societe: 'ACN', activite: 'MIXTE', regime: 6, zoneId: 'Z3' },
  { id: 'T7', nom: 'T7', societe: 'TS', activite: 'MIXTE', regime: 5 },
  { id: 'T8', nom: 'T8', societe: 'TS', activite: 'MIXTE', regime: 5 },
];

describe('validerAffectation', () => {
  it('accepte une journée conforme', () => {
    const infractions = validerAffectation(
      [{ technicienId: 'T1', jour: 0, vacations: [{ secteurId: '41018', creneaux: 6 }] }],
      TECHS,
      SCENARIO,
      REFERENTIEL_41,
    );
    expect(infractions).toEqual([]);
  });

  it('refuse un dépassement de capacité', () => {
    const infractions = validerAffectation(
      [{ technicienId: 'T1', jour: 0, vacations: [{ secteurId: '41018', creneaux: 7 }] }],
      TECHS,
      SCENARIO,
      REFERENTIEL_41,
    );
    expect(infractions.map((i) => i.code)).toContain('capacite-depassee');
  });

  it('refuse un troisième secteur dans la journée', () => {
    const infractions = validerAffectation(
      [
        {
          technicienId: 'T1',
          jour: 0,
          vacations: [
            { secteurId: '41018', creneaux: 2 },
            { secteurId: '41142', creneaux: 2 },
            { secteurId: '41180', creneaux: 2 },
          ],
        },
      ],
      TECHS,
      SCENARIO,
      REFERENTIEL_41,
    );
    expect(infractions.map((i) => i.code)).toContain('trop-de-secteurs');
  });

  it('refuse un enchaînement trop long', () => {
    // Vendôme → Vouzon : 94 km, au-delà des 60 autorisés.
    const infractions = validerAffectation(
      [
        {
          technicienId: 'T3',
          jour: 1,
          vacations: [
            { secteurId: '41269', creneaux: 3 },
            { secteurId: '41296', creneaux: 3 },
          ],
        },
      ],
      TECHS,
      SCENARIO,
      REFERENTIEL_41,
    );
    const distance = infractions.find((i) => i.code === 'distance-excessive');
    expect(distance).toBeDefined();
    expect(distance!.message).toContain('94 km');
  });

  it('accepte un enchaînement court', () => {
    // Blois → Valencisse : 10 km.
    const infractions = validerAffectation(
      [
        {
          technicienId: 'T1',
          jour: 0,
          vacations: [
            { secteurId: '41018', creneaux: 3 },
            { secteurId: '41142', creneaux: 3 },
          ],
        },
      ],
      TECHS,
      SCENARIO,
      REFERENTIEL_41,
    );
    expect(infractions).toEqual([]);
  });

  it('refuse de faire travailler un technicien de 5 jours le samedi', () => {
    const infractions = validerAffectation(
      [{ technicienId: 'T7', jour: 5, vacations: [{ secteurId: '41018', creneaux: 4 }] }],
      TECHS,
      SCENARIO,
      REFERENTIEL_41,
    );
    expect(infractions.map((i) => i.code)).toContain('hors-regime');
  });

  it('signale toutes les infractions, pas seulement la première', () => {
    const infractions = validerAffectation(
      [
        {
          technicienId: 'T7',
          jour: 5,
          vacations: [
            { secteurId: '41269', creneaux: 5 },
            { secteurId: '41296', creneaux: 5 },
          ],
        },
      ],
      TECHS,
      SCENARIO,
      REFERENTIEL_41,
    );
    const codes = new Set(infractions.map((i) => i.code));
    expect(codes).toContain('hors-regime');
    expect(codes).toContain('capacite-depassee');
    expect(codes).toContain('distance-excessive');
  });

  it('signale un secteur absent du référentiel', () => {
    const infractions = validerAffectation(
      [{ technicienId: 'T1', jour: 0, vacations: [{ secteurId: 'ZZZZZ', creneaux: 3 }] }],
      TECHS,
      SCENARIO,
      REFERENTIEL_41,
    );
    expect(infractions.map((i) => i.code)).toContain('secteur-inconnu');
  });
});

describe('construireAffectation', () => {
  it('ne produit jamais une affectation que le validateur refuserait', () => {
    const { affectation } = construireAffectation(SCENARIO, REFERENTIEL_41, TECHS);
    expect(validerAffectation(affectation, TECHS, SCENARIO, REFERENTIEL_41)).toEqual([]);
  });

  it('est déterministe', () => {
    const a = construireAffectation(SCENARIO, REFERENTIEL_41, TECHS);
    const b = construireAffectation(SCENARIO, REFERENTIEL_41, TECHS);
    expect(a).toEqual(b);
  });

  it('place tous les créneaux quand l’effectif suffit', () => {
    const { nonPlaces } = construireAffectation(SCENARIO, REFERENTIEL_41, TECHS);
    expect(nonPlaces).toEqual([]);
  });

  it('rend compte de ce qu’il n’a pas pu placer', () => {
    const { affectation, nonPlaces } = construireAffectation(SCENARIO, REFERENTIEL_41, [TECHS[0]!]);
    expect(nonPlaces.length).toBeGreaterThan(0);
    // Ce qui a été placé reste malgré tout conforme.
    expect(validerAffectation(affectation, TECHS, SCENARIO, REFERENTIEL_41)).toEqual([]);
  });

  it('conserve le total : placé + non placé = offre du scénario', () => {
    const { affectation, nonPlaces } = construireAffectation(SCENARIO, REFERENTIEL_41, [TECHS[0]!]);
    const place = affectation.reduce(
      (s, j) => s + j.vacations.reduce((t, v) => t + v.creneaux, 0),
      0,
    );
    const restant = nonPlaces.reduce((s, x) => s + x.creneaux, 0);
    const offert = SCENARIO.offres.reduce((s, o) => s + o.creneaux, 0);
    expect(place + restant).toBe(offert);
  });

  it('ne fait pas travailler le samedi en régime de 5 jours', () => {
    const scenario5 = {
      ...SCENARIO,
      regime: 5 as const,
      offres: REFERENTIEL_41.secteurs.map((s) => ({
        secteurId: s.id,
        jours: lireRythme('Lu/Me/Ve'),
        creneaux: 12,
      })),
    };
    const { affectation } = construireAffectation(scenario5, REFERENTIEL_41, TECHS);
    expect(affectation.every((j) => j.jour < 5)).toBe(true);
  });
});
