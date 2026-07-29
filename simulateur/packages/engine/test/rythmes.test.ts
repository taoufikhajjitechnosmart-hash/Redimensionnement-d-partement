import { describe, expect, it } from 'vitest';
import {
  conformeJ2,
  ecartMax,
  formaterRythme,
  lireRythme,
  pairesDisjointes,
  passagesMinimum,
  rythmesValides,
  sontDisjoints,
  type Jour,
  type Regime,
} from '../src/rythmes';

/** Implémentation de référence du §3, transcrite telle quelle pour comparaison. */
function ecartReference(jours: number[], mode: number): number {
  const p = [...jours].sort((a, b) => a - b).map((x) => x + 1);
  let max = 0;
  for (let i = 0; i < p.length; i++) {
    const g = i + 1 < p.length ? p[i + 1]! - p[i]! : p[0]! + mode - p[i]!;
    if (g > max) max = g;
  }
  return max;
}

/** Toutes les parties non vides de {0 … regime-1}. */
function toutesLesParties(regime: Regime): Jour[][] {
  const parties: Jour[][] = [];
  for (let masque = 1; masque < 1 << regime; masque++) {
    const jours: Jour[] = [];
    for (let j = 0; j < regime; j++) if (masque & (1 << j)) jours.push(j as Jour);
    parties.push(jours);
  }
  return parties;
}

describe('ecartMax', () => {
  it.each([5, 6] as const)(
    'coïncide avec le moteur de référence sur toutes les parties (%i jours)',
    (regime) => {
      for (const jours of toutesLesParties(regime)) {
        expect(ecartMax(jours, regime)).toBe(ecartReference(jours, regime));
      }
    },
  );

  it('reboucle sur la semaine suivante', () => {
    // Vendredi puis lundi : 3 jours d'écart en régime de 5 jours.
    expect(ecartMax([0, 4], 5)).toBe(4);
    // Lundi, mercredi, vendredi : 2 partout, y compris du vendredi au lundi.
    expect(ecartMax([0, 2, 4], 5)).toBe(2);
  });

  it('vaut un tour complet pour un passage unique', () => {
    expect(ecartMax([2], 5)).toBe(5);
    expect(ecartMax([2], 6)).toBe(6);
  });

  it('vaut l’infini sans aucun passage', () => {
    expect(ecartMax([], 5)).toBe(Number.POSITIVE_INFINITY);
    expect(conformeJ2([], 6)).toBe(false);
  });

  it('ignore les doublons', () => {
    expect(ecartMax([0, 2, 2, 4], 5)).toBe(ecartMax([0, 2, 4], 5));
  });

  it('refuse un samedi en régime de 5 jours', () => {
    expect(() => ecartMax([0, 2, 5], 5)).toThrow(RangeError);
  });
});

describe('rythmes valides', () => {
  it('en 5 jours, exactement les cinq rythmes de trois passages du §3', () => {
    const trouves = rythmesValides(5, 3).map(formaterRythme).sort();
    expect(trouves).toEqual(['Lu/Ma/Je', 'Lu/Me/Je', 'Lu/Me/Ve', 'Ma/Je/Ve', 'Ma/Me/Ve'].sort());
  });

  it('en 6 jours, seuls Lu/Me/Ve et Ma/Je/Sa', () => {
    const trouves = rythmesValides(6, 3).map(formaterRythme).sort();
    expect(trouves).toEqual(['Lu/Me/Ve', 'Ma/Je/Sa'].sort());
  });

  it('sur 20 combinaisons de trois jours en 6 jours, 2 conviennent ; sur 10 en 5 jours, 5', () => {
    expect(rythmesValides(6, 3)).toHaveLength(2);
    expect(rythmesValides(5, 3)).toHaveLength(5);
  });

  it('aucun rythme à deux passages ne tient le J+2', () => {
    expect(rythmesValides(5, 2)).toHaveLength(0);
    expect(rythmesValides(6, 2)).toHaveLength(0);
    expect(rythmesValides(5, 1)).toHaveLength(0);
    expect(rythmesValides(6, 1)).toHaveLength(0);
  });

  it('trois passages hebdomadaires est le minimum structurel', () => {
    expect(passagesMinimum(5)).toBe(3);
    expect(passagesMinimum(6)).toBe(3);
  });

  it('tout rythme renvoyé est effectivement conforme, et réciproquement', () => {
    for (const regime of [5, 6] as const) {
      const attendus = toutesLesParties(regime).filter((j) => conformeJ2(j, regime));
      const obtenus = [3, 4, 5, 6].flatMap((n) => rythmesValides(regime, n));
      expect(obtenus.map(formaterRythme).sort()).toEqual(attendus.map(formaterRythme).sort());
    }
  });
});

describe('paires disjointes', () => {
  it('en 6 jours, Lu/Me/Ve et Ma/Je/Sa sont complémentaires et uniques', () => {
    const paires = pairesDisjointes(6, 3);
    expect(paires).toHaveLength(1);
    const [a, b] = paires[0]!;
    expect([formaterRythme(a), formaterRythme(b)].sort()).toEqual(['Lu/Me/Ve', 'Ma/Je/Sa']);
    // Réunis, ils couvrent la semaine entière.
    expect(new Set([...a, ...b]).size).toBe(6);
  });

  it('en 5 jours, aucune paire disjointe — 3 + 3 dépasse la semaine', () => {
    expect(pairesDisjointes(5, 3)).toHaveLength(0);
  });

  it('sontDisjoints', () => {
    expect(sontDisjoints([0, 2, 4], [1, 3, 5])).toBe(true);
    expect(sontDisjoints([0, 2, 4], [1, 2, 5])).toBe(false);
  });
});

describe('notation des rythmes', () => {
  it('formate et relit', () => {
    expect(formaterRythme([0, 2, 4])).toBe('Lu/Me/Ve');
    expect(lireRythme('Lu/Me/Ve')).toEqual([0, 2, 4]);
    expect(lireRythme('Mar-Jeu-Sam')).toEqual([1, 3, 5]);
    expect(lireRythme('Lu Ma Je')).toEqual([0, 1, 3]);
  });

  it('signale un jour inconnu', () => {
    expect(() => lireRythme('Lu/Xx')).toThrow(RangeError);
  });
});
