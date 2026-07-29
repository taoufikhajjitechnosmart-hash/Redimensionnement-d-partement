import { describe, expect, it } from 'vitest';
import {
  demandeHebdo,
  joursOuvresImplicites,
  PARAMS_MOYENNE_22J,
  PARAMS_VOLUME_PIC,
  type VolumeSecteur,
} from '../src/demande';
import { REFERENTIEL_41 } from '@sim/data';

const total = (params: Parameters<typeof demandeHebdo>[1]): number =>
  REFERENTIEL_41.secteurs.reduce((s, x) => s + demandeHebdo(x.volume, params), 0);

describe('conversion des volumes en demande hebdomadaire', () => {
  it('le paramétrage « volume au pic » donne 185 interventions par semaine', () => {
    // 185,15 exactement. Le dossier d'analyse annonçait 185,3 : cette valeur
    // était la somme des demandes arrondies au dixième secteur par secteur,
    // et non l'arrondi de la somme. L'écart est de 0,15 intervention.
    expect(total(PARAMS_VOLUME_PIC)).toBeCloseTo(185.15, 1);
  });

  it('le paramétrage de l’étude antérieure donne 141', () => {
    expect(total(PARAMS_MOYENNE_22J)).toBeCloseTo(141, 0);
  });

  it('les deux écarts se décomposent en trois choix indépendants', () => {
    const base = { ...PARAMS_MOYENNE_22J };
    const surLePic = total({ ...base, mois: 'pic' });
    const avecB2B = total({ ...base, mois: 'pic', inclureB2B: true });
    const avecMarge = total({ ...base, mois: 'pic', inclureB2B: true, margeFlexibilite: 0.1 });

    expect(surLePic).toBeGreaterThan(total(base)); // pic contre moyenne
    expect(avecB2B).toBeGreaterThan(surLePic); // B2B compté
    expect(avecMarge).toBeCloseTo(avecB2B * 1.1, 6); // marge de flexibilité
  });
});

describe('jours ouvrés implicites du fichier source', () => {
  it('les mois relevés comptent 25 jours en octobre et 24 en mars', () => {
    for (const secteur of REFERENTIEL_41.secteurs) {
      const { octobre, mars } = joursOuvresImplicites(secteur.volume);
      expect(octobre, `${secteur.nom}, octobre`).toBeCloseTo(25, 1);
      expect(mars, `${secteur.nom}, mars`).toBeCloseTo(24, 1);
    }
  });

  it('projeter sur 22 jours minore donc la demande d’environ 12 %', () => {
    const fidele = total({ ...PARAMS_MOYENNE_22J, methode: 'volume-mensuel' });
    const projete = total(PARAMS_MOYENNE_22J);
    expect(projete / fidele).toBeCloseTo(22 / 24.5, 1);
    expect(projete).toBeLessThan(fidele);
  });
});

describe('demandeHebdo', () => {
  const v: VolumeSecteur = {
    interOctobre: 100,
    interMars: 80,
    b2bMois: 10,
    moyJrOctobre: 4,
    moyJrMars: 3.2,
  };

  it('divise le volume mensuel par le nombre de semaines', () => {
    const p = { ...PARAMS_VOLUME_PIC, semainesParMois: 4, inclureB2B: false, margeFlexibilite: 0 };
    expect(demandeHebdo(v, p)).toBe(25); // 100 / 4
  });

  it('compte le B2B quand on le demande', () => {
    const p = { ...PARAMS_VOLUME_PIC, semainesParMois: 4, inclureB2B: true, margeFlexibilite: 0 };
    expect(demandeHebdo(v, p)).toBe(27.5); // 110 / 4
  });

  it('applique la marge en dernier', () => {
    const p = { ...PARAMS_VOLUME_PIC, semainesParMois: 4, inclureB2B: false, margeFlexibilite: 0.1 };
    expect(demandeHebdo(v, p)).toBeCloseTo(27.5, 10); // 25 × 1,1
  });

  it('retient bien le mois demandé', () => {
    const p = { ...PARAMS_VOLUME_PIC, semainesParMois: 4, inclureB2B: false, margeFlexibilite: 0 };
    expect(demandeHebdo(v, { ...p, mois: 'octobre' })).toBe(25);
    expect(demandeHebdo(v, { ...p, mois: 'mars' })).toBe(20);
    expect(demandeHebdo(v, { ...p, mois: 'moyenne' })).toBe(22.5);
    expect(demandeHebdo(v, { ...p, mois: 'pic' })).toBe(25);
  });
});
