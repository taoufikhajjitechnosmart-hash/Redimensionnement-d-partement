import { describe, expect, it } from 'vitest';
import { evaluerScenario } from '../src/scenario';
import {
  REFERENTIEL_41,
  SCENARIO_CIBLE_5J_41,
  SCENARIO_CIBLE_6J_41,
  SCENARIO_EXISTANT_41,
} from '@sim/data';

/**
 * Non-régression.
 *
 * Ne sont figées ici que les grandeurs qui ne dépendent pas de l'hypothèse de
 * demande : nombre d'alertes J+2, offre ouverte, effectif commandé par la
 * pointe, kilomètres. Les totaux de demande restent délibérément hors de ce
 * fichier tant que le volume SAV réel n'a pas été mesuré.
 */

describe('scénario existant', () => {
  const r = evaluerScenario(SCENARIO_EXISTANT_41, REFERENTIEL_41);

  it('ouvre 311 créneaux', () => {
    expect(r.offreTotale).toBe(311);
  });

  it('laisse 5 secteurs sur 12 hors délai J+2', () => {
    expect(r.nbAlertesJ2).toBe(5);
  });

  it('nomme précisément ces cinq secteurs', () => {
    const enEchec = r.secteurs
      .filter((s) => !s.conformeJ2)
      .map((s) => s.nom)
      .sort();
    expect(enEchec).toEqual(
      ['Cormenon', 'Montoire-sur-le-Loir', 'Mur-de-Sologne', 'Vendôme', 'Vouzon'].sort(),
    );
  });

  it('chacun d’eux souffre d’un écart de 4 jours ouvrés', () => {
    for (const secteur of r.secteurs.filter((s) => !s.conformeJ2)) {
      expect(secteur.ecartMax, secteur.nom).toBe(4);
    }
  });
});

describe('scénario cible, semaine de 6 jours', () => {
  const r = evaluerScenario(SCENARIO_CIBLE_6J_41, REFERENTIEL_41);

  it('ouvre 190 créneaux, soit 121 de moins que l’existant', () => {
    expect(r.offreTotale).toBe(190);
    expect(311 - r.offreTotale).toBe(121);
  });

  it('supprime toutes les alertes de délai', () => {
    expect(r.nbAlertesJ2).toBe(0);
  });

  it('appelle 8 techniciens, répartis 4 / 2 / 2', () => {
    expect(r.effectifMinimum).toBe(8);
    expect(r.effectifParZone).toEqual({ Z1: 4, Z2: 2, Z3: 2 });
  });

  it('mobilise 5 techniciens le samedi', () => {
    expect(r.effectifSamedi).toBe(5);
  });

  it('visite chaque secteur au moins trois fois', () => {
    for (const secteur of r.secteurs) {
      expect(secteur.nbPassages, secteur.nom).toBeGreaterThanOrEqual(3);
    }
  });
});

describe('scénario cible, semaine de 5 jours', () => {
  const r = evaluerScenario(SCENARIO_CIBLE_5J_41, REFERENTIEL_41);

  it('ouvre la même offre de 190 créneaux', () => {
    expect(r.offreTotale).toBe(190);
  });

  it('supprime toutes les alertes de délai', () => {
    expect(r.nbAlertesJ2).toBe(0);
  });

  it('appelle 8 techniciens', () => {
    expect(r.effectifMinimum).toBe(8);
  });

  it('n’ouvre jamais le samedi', () => {
    expect(r.chargeParJour[5]).toBe(0);
  });

  it('coûte moins de kilomètres que la cible à 6 jours', () => {
    const six = evaluerScenario(SCENARIO_CIBLE_6J_41, REFERENTIEL_41);
    expect(r.kmSemaine).toBeLessThan(six.kmSemaine);
  });
});

describe('tableau de non-régression du §6', () => {
  /**
   * Les six colonnes du tableau de référence, moins la couverture — seule
   * grandeur qui dépende de l'hypothèse de demande, donc seule à ne pas être
   * figée ici.
   */
  const attendu = [
    { scenario: SCENARIO_EXISTANT_41, offre: 311, alertes: 5, techniciens: 10, occupation: 0.86, km: 1514 },
    { scenario: SCENARIO_CIBLE_6J_41, offre: 190, alertes: 0, techniciens: 8, occupation: 0.66, km: 1440 },
    { scenario: SCENARIO_CIBLE_5J_41, offre: 190, alertes: 0, techniciens: 8, occupation: 0.79, km: 1388 },
  ];

  it.each(attendu)('$scenario.nom', ({ scenario, offre, alertes, techniciens, occupation, km }) => {
    const r = evaluerScenario(scenario, REFERENTIEL_41);
    expect(r.offreTotale).toBe(offre);
    expect(r.nbAlertesJ2).toBe(alertes);
    expect(r.effectifMinimum).toBe(techniciens);
    expect(r.occupation).toBeCloseTo(occupation, 2);
    expect(Math.round(r.kmSemaine)).toBe(km);
  });

  it('le samedi coûte environ 8 % de kilomètres de plus', () => {
    const six = evaluerScenario(SCENARIO_CIBLE_6J_41, REFERENTIEL_41).kmSemaine;
    const cinq = evaluerScenario(SCENARIO_CIBLE_5J_41, REFERENTIEL_41).kmSemaine;
    expect(six / cinq - 1).toBeGreaterThan(0.03);
    expect(six / cinq - 1).toBeLessThan(0.08);
  });
});

describe('les trois scénarios', () => {
  it('8 techniciens est le plancher structurel, en 5 comme en 6 jours', () => {
    expect(evaluerScenario(SCENARIO_CIBLE_5J_41, REFERENTIEL_41).effectifMinimum).toBe(8);
    expect(evaluerScenario(SCENARIO_CIBLE_6J_41, REFERENTIEL_41).effectifMinimum).toBe(8);
  });

  it('la cible réduit l’offre sans dégrader le délai', () => {
    const existant = evaluerScenario(SCENARIO_EXISTANT_41, REFERENTIEL_41);
    for (const cible of [SCENARIO_CIBLE_6J_41, SCENARIO_CIBLE_5J_41]) {
      const r = evaluerScenario(cible, REFERENTIEL_41);
      expect(r.offreTotale).toBeLessThan(existant.offreTotale);
      expect(r.nbAlertesJ2).toBeLessThan(existant.nbAlertesJ2);
    }
  });
});
