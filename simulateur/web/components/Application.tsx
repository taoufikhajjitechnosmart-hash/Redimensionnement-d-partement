'use client';

import { useState } from 'react';
import type { Referentiel, Scenario, Technicien, VolumeSecteur } from '@sim/engine';
import { Simulateur } from './Simulateur';
import { GrilleAffectation } from './GrilleAffectation';
import { Import } from './Import';
import { Comparaison } from './Comparaison';

type Onglet = 'dimensionnement' | 'grille' | 'comparaison' | 'import';

const ONGLETS: readonly { id: Onglet; libelle: string }[] = [
  { id: 'dimensionnement', libelle: 'Dimensionnement' },
  { id: 'grille', libelle: 'Grille par technicien' },
  { id: 'comparaison', libelle: 'Comparaison' },
  { id: 'import', libelle: 'Import' },
];

interface Props {
  readonly referentielInitial: Referentiel;
  readonly preregles: readonly Scenario[];
  readonly techniciens: readonly Technicien[];
}

export function Application({ referentielInitial, preregles, techniciens }: Props) {
  const [onglet, setOnglet] = useState<Onglet>('dimensionnement');
  const [referentiel, setReferentiel] = useState<Referentiel>(referentielInitial);
  const [scenario, setScenario] = useState<Scenario>(() => ({ ...preregles[0]! }));

  const appliquerVolumes = (
    importes: readonly { id: string; nom: string; volume: VolumeSecteur }[],
  ): void => {
    const parId = new Map(importes.map((s) => [s.id, s.volume]));
    setReferentiel((r) => ({
      ...r,
      secteurs: r.secteurs.map((s) => (parId.has(s.id) ? { ...s, volume: parId.get(s.id)! } : s)),
    }));
    setOnglet('dimensionnement');
  };

  return (
    <>
      <div className="onglets" role="tablist">
        {ONGLETS.map((o) => (
          <button
            key={o.id}
            type="button"
            role="tab"
            className="onglet"
            aria-selected={onglet === o.id}
            onClick={() => setOnglet(o.id)}
          >
            {o.libelle}
          </button>
        ))}
      </div>

      {onglet === 'dimensionnement' && (
        <Simulateur
          referentiel={referentiel}
          preregles={preregles}
          scenario={scenario}
          setScenario={setScenario}
        />
      )}

      {onglet === 'grille' && (
        <GrilleAffectation
          scenario={scenario}
          referentiel={referentiel}
          techniciens={techniciens}
        />
      )}

      {onglet === 'comparaison' && (
        <Comparaison
          referentiel={referentiel}
          preregles={preregles}
          scenarioCourant={scenario}
        />
      )}

      {onglet === 'import' && <Import referentiel={referentiel} onImport={appliquerVolumes} />}
    </>
  );
}
