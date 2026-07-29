import { REFERENTIEL_41, SCENARIOS_41, TECHNICIENS_41 } from '@sim/data';
import { Application } from '@/components/Application';

export default function Page() {
  return (
    <main className="page">
      <header className="entete">
        <div>
          <h1>Simulateur de dimensionnement</h1>
          <div className="sous-titre">
            Département {REFERENTIEL_41.departement} — {REFERENTIEL_41.libelle} ·{' '}
            {REFERENTIEL_41.secteurs.length} secteurs GRDV · {TECHNICIENS_41.length} techniciens
          </div>
        </div>
      </header>
      <Application
        referentielInitial={REFERENTIEL_41}
        preregles={[...SCENARIOS_41]}
        techniciens={[...TECHNICIENS_41]}
      />
    </main>
  );
}
