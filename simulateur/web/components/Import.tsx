'use client';

import { useCallback, useState } from 'react';
import type { Referentiel, VolumeSecteur } from '@sim/engine';

interface Rapport {
  readonly departement: string;
  readonly misAJour: number;
  readonly inconnus: readonly string[];
  readonly manquants: readonly string[];
  readonly dateMaj: string | null;
  readonly secteurs: readonly { id: string; nom: string; volume: VolumeSecteur }[];
}

interface Props {
  readonly referentiel: Referentiel;
  readonly onImport: (secteurs: Rapport['secteurs']) => void;
}

export function Import({ referentiel, onImport }: Props) {
  const [rapport, setRapport] = useState<Rapport | null>(null);
  const [erreur, setErreur] = useState<string | null>(null);
  const [encours, setEncours] = useState(false);

  const envoyer = useCallback(
    async (fichier: File) => {
      setEncours(true);
      setErreur(null);
      setRapport(null);
      try {
        const formulaire = new FormData();
        formulaire.append('fichier', fichier);
        formulaire.append('departement', referentiel.departement);
        const reponse = await fetch('/api/import', { method: 'POST', body: formulaire });
        const corps = await reponse.json();
        if (!reponse.ok) throw new Error(corps.erreur ?? `Erreur ${reponse.status}`);
        setRapport(corps as Rapport);
      } catch (e) {
        setErreur(e instanceof Error ? e.message : 'Import impossible.');
      } finally {
        setEncours(false);
      }
    },
    [referentiel.departement],
  );

  const volumeActuel = new Map(referentiel.secteurs.map((s) => [s.id, s.volume]));

  return (
    <>
      <section className="carte">
        <h2>Importer le classeur de suivi</h2>
        <p className="aide" style={{ marginTop: 0, marginBottom: 12 }}>
          Déposez <code>suivi_volumes_PROD.xlsx</code>. Seuls les volumes sont repris : le classeur
          ne porte ni coordonnées, ni zones, ni distances, qui restent celles du référentiel du
          département {referentiel.departement}. Rien n’est modifié tant que vous n’avez pas
          confirmé.
        </p>

        <div className="actions">
          <input
            type="file"
            accept=".xlsx,.xlsm,.xls"
            aria-label="Classeur de suivi"
            disabled={encours}
            onChange={(e) => {
              const fichier = e.target.files?.[0];
              if (fichier) void envoyer(fichier);
            }}
          />
          {encours && <span className="message">Lecture…</span>}
          {erreur && <span className="message est-alerte">{erreur}</span>}
        </div>
      </section>

      {rapport && (
        <section className="carte">
          <div className="entete-carte">
            <h2>
              {rapport.misAJour} secteur{rapport.misAJour > 1 ? 's' : ''} lu
              {rapport.misAJour > 1 ? 's' : ''}
              {rapport.dateMaj && (
                <span className="sous-titre"> · classeur du {rapport.dateMaj.slice(0, 10)}</span>
              )}
            </h2>
            <button
              type="button"
              className="bouton bouton-primaire"
              onClick={() => {
                onImport(rapport.secteurs);
                setRapport(null);
              }}
            >
              Appliquer ces volumes
            </button>
          </div>

          {rapport.inconnus.length > 0 && (
            <div className="reserve" style={{ marginTop: 12 }}>
              <span className="reserve-icone" aria-hidden="true">
                !
              </span>
              <div>
                <b>
                  {rapport.inconnus.length} secteur{rapport.inconnus.length > 1 ? 's' : ''} du
                  classeur {rapport.inconnus.length > 1 ? 'sont' : 'est'} inconnu
                  {rapport.inconnus.length > 1 ? 's' : ''} du référentiel
                </b>{' '}
                — {rapport.inconnus.join(', ')}. Sans coordonnées ni zone, ils ne peuvent pas entrer
                dans le calcul. Ajoutez-les au référentiel avant de les dimensionner.
              </div>
            </div>
          )}

          {rapport.manquants.length > 0 && (
            <div className="reserve" style={{ marginTop: 12 }}>
              <span className="reserve-icone" aria-hidden="true">
                !
              </span>
              <div>
                <b>Absents du classeur</b> — {rapport.manquants.join(', ')}. Leurs volumes actuels
                sont conservés.
              </div>
            </div>
          )}

          <div className="enveloppe-table" style={{ marginTop: 12 }}>
            <table>
              <thead>
                <tr>
                  <th>Secteur</th>
                  <th className="num">Inter. octobre</th>
                  <th className="num">Inter. mars</th>
                  <th className="num">B2B</th>
                  <th className="num">Écart</th>
                </tr>
              </thead>
              <tbody>
                {rapport.secteurs.map((s) => {
                  const avant = volumeActuel.get(s.id);
                  const picAvant = avant ? Math.max(avant.interOctobre, avant.interMars) : 0;
                  const picApres = Math.max(s.volume.interOctobre, s.volume.interMars);
                  const delta = picApres - picAvant;
                  return (
                    <tr key={s.id}>
                      <td className="nom-secteur">{s.nom}</td>
                      <td className="num">{s.volume.interOctobre}</td>
                      <td className="num">{s.volume.interMars}</td>
                      <td className="num">{s.volume.b2bMois.toFixed(1)}</td>
                      <td className={`num ${delta === 0 ? '' : delta > 0 ? 'est-attention' : 'est-bon'}`}>
                        {delta === 0 ? '—' : `${delta > 0 ? '+' : ''}${delta}`}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>
      )}
    </>
  );
}
