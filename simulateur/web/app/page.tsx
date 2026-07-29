import { REFERENTIEL_41, SCENARIOS_41 } from '@sim/data';
import { Simulateur } from '@/components/Simulateur';

export default function Page() {
  return (
    <main className="page">
      <header className="entete">
        <div>
          <h1>Simulateur de dimensionnement</h1>
          <div className="sous-titre">
            Département {REFERENTIEL_41.departement} — {REFERENTIEL_41.libelle} ·{' '}
            {REFERENTIEL_41.secteurs.length} secteurs GRDV
          </div>
        </div>
      </header>
      <Simulateur referentiel={REFERENTIEL_41} preregles={[...SCENARIOS_41]} />
    </main>
  );
}
