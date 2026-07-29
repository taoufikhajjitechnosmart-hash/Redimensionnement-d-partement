import { describe, expect, it } from 'vitest';
import { evaluerScenario, repartir } from '../src/scenario';
import { PARAMS_VOLUME_PIC } from '../src/demande';
import { fournisseurGeometrique, fournisseurMatrice } from '../src/distance';
import { lireRythme, type Jour } from '../src/rythmes';
import type { Referentiel, Scenario } from '../src/types';
import { REFERENTIEL_41 } from '@sim/data';

const scenarioBase = (partiel: Partial<Scenario> = {}): Scenario => ({
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
  offres: [],
  ...partiel,
});

describe('repartir', () => {
  it('division entière, reste sur les premiers jours', () => {
    expect(repartir(10, [0, 2, 4])).toEqual([4, 0, 3, 0, 3, 0]);
    expect(repartir(9, [0, 2, 4])).toEqual([3, 0, 3, 0, 3, 0]);
    expect(repartir(11, [0, 2, 4])).toEqual([4, 0, 4, 0, 3, 0]);
  });

  it('conserve le total', () => {
    for (let total = 0; total <= 40; total++) {
      for (const jours of [[0], [0, 2], [0, 2, 4], [1, 3, 5], [0, 1, 2, 3, 4, 5]] as Jour[][]) {
        expect(repartir(total, jours).reduce((s, x) => s + x, 0)).toBe(total);
      }
    }
  });

  it('sans jour de passage, rien n’est réparti', () => {
    expect(repartir(12, [])).toEqual([0, 0, 0, 0, 0, 0]);
  });

  it('ne place jamais rien un jour non desservi', () => {
    const parJour = repartir(7, [1, 3]);
    expect([parJour[0], parJour[2], parJour[4], parJour[5]]).toEqual([0, 0, 0, 0]);
  });
});

describe('evaluerScenario', () => {
  it('signale les secteurs jamais visités', () => {
    const r = evaluerScenario(scenarioBase(), REFERENTIEL_41);
    expect(r.nbAlertesJ2).toBe(12);
    expect(r.offreTotale).toBe(0);
    expect(r.alertes.every((a) => a.gravite === 'critique' || a.code === 'couverture')).toBe(true);
  });

  it('un rythme Lu/Me/Ve suffisamment doté ne déclenche aucune alerte', () => {
    const offres = REFERENTIEL_41.secteurs.map((s) => ({
      secteurId: s.id,
      jours: lireRythme('Lu/Me/Ve'),
      creneaux: 200, // volontairement large
    }));
    const r = evaluerScenario(scenarioBase({ offres }), REFERENTIEL_41);
    expect(r.alertes).toHaveLength(0);
    expect(r.nbAlertesJ2).toBe(0);
    expect(r.secteurs.every((s) => s.conformeJ2)).toBe(true);
  });

  it('un rythme Ma/Je laisse 3 jours d’écart et échoue', () => {
    const offres = REFERENTIEL_41.secteurs.map((s) => ({
      secteurId: s.id,
      jours: lireRythme('Ma/Je'),
      creneaux: 200,
    }));
    const r = evaluerScenario(scenarioBase({ offres }), REFERENTIEL_41);
    expect(r.nbAlertesJ2).toBe(12);
    expect(r.secteurs[0]!.ecartMax).toBe(4);
  });

  it('refuse un passage le samedi dans un scénario de 5 jours', () => {
    const offres = [{ secteurId: '41018', jours: lireRythme('Ma/Je/Sa'), creneaux: 30 }];
    expect(() => evaluerScenario(scenarioBase({ regime: 5, offres }), REFERENTIEL_41)).toThrow(
      RangeError,
    );
  });

  it('l’effectif est commandé par la journée de pointe de chaque zone', () => {
    // Une seule zone chargée, 12 créneaux le lundi, capacité 6 → 2 techniciens.
    const referentiel: Referentiel = {
      departement: '99',
      libelle: 'Test',
      secteurs: [
        {
          id: 'A',
          nom: 'A',
          libelleGrdv: 'A',
          departement: '99',
          lat: 47,
          lon: 1,
          zoneId: 'Z',
          volume: { interOctobre: 0, interMars: 0, b2bMois: 0, moyJrOctobre: 0, moyJrMars: 0 },
        },
      ],
      zones: [{ id: 'Z', nom: 'Z', baseSecteurId: 'A' }],
      distances: { A: { A: 0 } },
    };
    const r = evaluerScenario(
      scenarioBase({ offres: [{ secteurId: 'A', jours: [0, 2, 4], creneaux: 36 }] }),
      referentiel,
    );
    expect(r.chargeParJour).toEqual([12, 0, 12, 0, 12, 0]);
    expect(r.effectifMinimum).toBe(2);
    expect(r.capaciteTotale).toBe(2 * 6 * 6);
    expect(r.occupation).toBeCloseTo(36 / 72, 6);
  });

  it('les kilomètres comptent un aller-retour depuis la base par passage', () => {
    const offres = [{ secteurId: '41180', jours: lireRythme('Lu/Me/Ve'), creneaux: 12 }];
    const r = evaluerScenario(scenarioBase({ offres }), REFERENTIEL_41);
    // Pontlevoy est à 26 km de Blois, sa base : 3 passages × 2 × 26.
    expect(r.kmSemaine).toBe(3 * 2 * 26);
  });

  it('un secteur sur sa propre base ne coûte aucun kilomètre', () => {
    const offres = [{ secteurId: '41018', jours: lireRythme('Lu/Me/Ve'), creneaux: 12 }];
    expect(evaluerScenario(scenarioBase({ offres }), REFERENTIEL_41).kmSemaine).toBe(0);
  });

  it('est une fonction pure : deux appels donnent le même résultat', () => {
    const offres = REFERENTIEL_41.secteurs.map((s) => ({
      secteurId: s.id,
      jours: lireRythme('Lu/Me/Ve'),
      creneaux: 15,
    }));
    const s = scenarioBase({ offres });
    expect(evaluerScenario(s, REFERENTIEL_41)).toEqual(evaluerScenario(s, REFERENTIEL_41));
  });
});

describe('fournisseurs de distances', () => {
  it('la matrice fournie est symétrique et nulle sur la diagonale', () => {
    const d = fournisseurMatrice(REFERENTIEL_41.distances);
    for (const a of REFERENTIEL_41.secteurs) {
      expect(d.km(a.id, a.id)).toBe(0);
      for (const b of REFERENTIEL_41.secteurs) {
        expect(d.km(a.id, b.id)).toBe(d.km(b.id, a.id));
      }
    }
  });

  it('l’estimation géométrique reste dans 30 % de la matrice fournie', () => {
    const geo = fournisseurGeometrique(REFERENTIEL_41.secteurs);
    const mat = fournisseurMatrice(REFERENTIEL_41.distances);
    for (const a of REFERENTIEL_41.secteurs) {
      for (const b of REFERENTIEL_41.secteurs) {
        if (a.id === b.id) continue;
        const ecart = Math.abs(geo.km(a.id, b.id) - mat.km(a.id, b.id)) / mat.km(a.id, b.id);
        expect(ecart, `${a.nom} → ${b.nom}`).toBeLessThan(0.3);
      }
    }
  });

  it('signale un secteur inconnu', () => {
    expect(() => fournisseurMatrice(REFERENTIEL_41.distances).km('41018', 'XXXXX')).toThrow(
      RangeError,
    );
  });
});
