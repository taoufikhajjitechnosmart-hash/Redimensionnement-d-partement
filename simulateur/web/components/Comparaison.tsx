'use client';

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  evaluerScenario,
  formaterRythme,
  type Referentiel,
  type Resultat,
  type Scenario,
} from '@sim/engine';

const nombre = (x: number, decimales = 0): string =>
  Number.isFinite(x)
    ? x.toLocaleString('fr-FR', {
        minimumFractionDigits: decimales,
        maximumFractionDigits: decimales,
      })
    : '—';

const pourcent = (x: number): string => (Number.isFinite(x) ? `${Math.round(x * 100)} %` : '—');

interface Props {
  readonly referentiel: Referentiel;
  readonly preregles: readonly Scenario[];
  readonly scenarioCourant: Scenario;
}

interface Colonne {
  readonly scenario: Scenario;
  readonly resultat: Resultat;
  readonly origine: 'courant' | 'préréglage' | 'enregistré';
}

/** Meilleure valeur d'une ligne : sert à mettre en avant la colonne gagnante. */
type Sens = 'bas' | 'haut' | 'aucun';

interface Ligne {
  readonly libelle: string;
  readonly valeurs: readonly number[];
  readonly format: (x: number) => string;
  readonly sens: Sens;
  readonly aide?: string;
}

export function Comparaison({ referentiel, preregles, scenarioCourant }: Props) {
  const [enregistres, setEnregistres] = useState<Scenario[]>([]);
  const [selection, setSelection] = useState<string[]>(['__courant__']);
  const [erreur, setErreur] = useState<string | null>(null);
  const [chargement, setChargement] = useState(true);

  useEffect(() => {
    let annule = false;
    void (async () => {
      try {
        const reponse = await fetch(`/api/scenarios?departement=${referentiel.departement}`);
        if (!reponse.ok) throw new Error(`Erreur ${reponse.status}`);
        const corps = (await reponse.json()) as { scenarios: { scenario: Scenario }[] };
        if (!annule) setEnregistres(corps.scenarios.map((s) => s.scenario));
      } catch (e) {
        if (!annule) setErreur(e instanceof Error ? e.message : 'Lecture impossible.');
      } finally {
        if (!annule) setChargement(false);
      }
    })();
    return () => {
      annule = true;
    };
  }, [referentiel.departement]);

  /** Tous les scénarios comparables, sans doublon d'identifiant. */
  const disponibles = useMemo(() => {
    const liste: { cle: string; scenario: Scenario; origine: Colonne['origine'] }[] = [
      { cle: '__courant__', scenario: scenarioCourant, origine: 'courant' },
    ];
    for (const p of preregles) {
      liste.push({ cle: `p:${p.id}`, scenario: p, origine: 'préréglage' });
    }
    for (const e of enregistres) {
      if (preregles.some((p) => p.id === e.id)) continue;
      liste.push({ cle: `e:${e.id}`, scenario: e, origine: 'enregistré' });
    }
    return liste;
  }, [scenarioCourant, preregles, enregistres]);

  const basculer = useCallback((cle: string) => {
    setSelection((s) => (s.includes(cle) ? s.filter((x) => x !== cle) : [...s, cle]));
  }, []);

  const colonnes = useMemo((): Colonne[] => {
    const retenues: Colonne[] = [];
    for (const cle of selection) {
      const trouve = disponibles.find((d) => d.cle === cle);
      if (!trouve) continue;
      try {
        retenues.push({
          scenario: trouve.scenario,
          resultat: evaluerScenario(trouve.scenario, referentiel),
          origine: trouve.origine,
        });
      } catch {
        // Un scénario incohérent est simplement écarté de la comparaison.
      }
    }
    return retenues;
  }, [selection, disponibles, referentiel]);

  const lignes = useMemo((): Ligne[] => {
    if (colonnes.length === 0) return [];
    const r = colonnes.map((c) => c.resultat);
    return [
      {
        libelle: 'Créneaux ouverts',
        valeurs: r.map((x) => x.offreTotale),
        format: (x) => nombre(x),
        sens: 'aucun',
      },
      {
        libelle: 'Demande hebdomadaire',
        valeurs: r.map((x) => x.demandeTotale),
        format: (x) => nombre(x, 1),
        sens: 'aucun',
        aide: 'dépend des paramètres de conversion du scénario',
      },
      {
        libelle: 'Couverture',
        valeurs: r.map((x) => x.couverture),
        format: pourcent,
        sens: 'aucun',
      },
      {
        libelle: 'Alertes J+2',
        valeurs: r.map((x) => x.nbAlertesJ2),
        format: (x) => `${nombre(x)} / ${referentiel.secteurs.length}`,
        sens: 'bas',
      },
      {
        libelle: 'Techniciens',
        valeurs: r.map((x) => x.effectifMinimum),
        format: (x) => nombre(x),
        sens: 'bas',
        aide: 'minimum structurel, journée de pointe par zone',
      },
      {
        libelle: 'dont le samedi',
        valeurs: r.map((x) => x.effectifSamedi),
        format: (x) => nombre(x),
        sens: 'aucun',
      },
      {
        libelle: 'Occupation',
        valeurs: r.map((x) => x.occupation),
        format: pourcent,
        sens: 'aucun',
      },
      {
        libelle: 'Kilomètres par semaine',
        valeurs: r.map((x) => x.kmSemaine),
        format: (x) => nombre(Math.round(x)),
        sens: 'bas',
      },
      {
        libelle: 'Passages hebdomadaires',
        valeurs: r.map((x) => x.secteurs.reduce((s, y) => s + y.nbPassages, 0)),
        format: (x) => nombre(x),
        sens: 'aucun',
      },
    ];
  }, [colonnes, referentiel.secteurs.length]);

  const meilleure = (ligne: Ligne): number | null => {
    if (ligne.sens === 'aucun' || ligne.valeurs.length < 2) return null;
    const utiles = ligne.valeurs.filter(Number.isFinite);
    if (utiles.length === 0) return null;
    const cible = ligne.sens === 'bas' ? Math.min(...utiles) : Math.max(...utiles);
    // Pas de gagnant si tout le monde est à égalité.
    return ligne.valeurs.every((v) => v === cible) ? null : cible;
  };

  return (
    <>
      <section className="carte">
        <h2>Scénarios à comparer</h2>
        {chargement ? (
          <p className="vide">Lecture des scénarios enregistrés…</p>
        ) : (
          <>
            {erreur && <p className="message est-alerte">Scénarios enregistrés : {erreur}</p>}
            <div className="choix-scenarios">
              {disponibles.map((d) => (
                <label key={d.cle} className="choix">
                  <input
                    type="checkbox"
                    checked={selection.includes(d.cle)}
                    onChange={() => basculer(d.cle)}
                  />
                  <span>
                    {d.scenario.nom}
                    <span className="zone-puce">{d.origine}</span>
                    <span className="aide">
                      {' '}
                      {d.scenario.regime} j · {d.scenario.capaciteParTechJour} cr/j
                    </span>
                  </span>
                </label>
              ))}
            </div>
          </>
        )}
      </section>

      {colonnes.length === 0 ? (
        <section className="carte">
          <p className="vide">Cochez au moins un scénario.</p>
        </section>
      ) : (
        <>
          <section className="carte">
            <h2>Comparaison</h2>
            <div className="enveloppe-table">
              <table>
                <thead>
                  <tr>
                    <th>Indicateur</th>
                    {colonnes.map((c, i) => (
                      <th key={`${c.scenario.id}-${i}`} className="num">
                        {c.scenario.nom}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {lignes.map((ligne) => {
                    const cible = meilleure(ligne);
                    return (
                      <tr key={ligne.libelle}>
                        <td>
                          {ligne.libelle}
                          {ligne.aide && (
                            <>
                              <br />
                              <span className="aide">{ligne.aide}</span>
                            </>
                          )}
                        </td>
                        {ligne.valeurs.map((v, i) => (
                          <td
                            key={i}
                            className={`num ${cible !== null && v === cible ? 'est-bon' : ''}`}
                          >
                            {ligne.format(v)}
                          </td>
                        ))}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <p className="aide" style={{ marginTop: 10 }}>
              En vert, la meilleure valeur de la ligne lorsqu’un sens de lecture existe : moins
              d’alertes, moins de techniciens, moins de kilomètres. La couverture et l’occupation
              n’ont pas de sens univoque — elles se lisent contre la cible du scénario.
            </p>
          </section>

          <section className="carte">
            <h2>Délai J+2, secteur par secteur</h2>
            <div className="enveloppe-table">
              <table>
                <thead>
                  <tr>
                    <th>Secteur</th>
                    {colonnes.map((c, i) => (
                      <th key={`${c.scenario.id}-${i}`}>{c.scenario.nom}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {referentiel.secteurs.map((secteur) => (
                    <tr key={secteur.id}>
                      <td className="nom-secteur">{secteur.nom}</td>
                      {colonnes.map((c, i) => {
                        const s = c.resultat.secteurs.find((x) => x.secteurId === secteur.id);
                        if (!s) return <td key={i}>—</td>;
                        return (
                          <td key={i}>
                            <span
                              className={`etat ${s.conformeJ2 ? 'etat-bon' : 'etat-alerte'}`}
                              title={`${s.offre} créneaux · écart maximal ${s.ecartMax} j`}
                            >
                              {s.conformeJ2 ? formaterRythme(s.jours) || '—' : `${s.ecartMax} j`}
                            </span>
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </>
  );
}
