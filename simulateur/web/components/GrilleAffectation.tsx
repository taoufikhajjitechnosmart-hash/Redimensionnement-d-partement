'use client';

import { useCallback, useMemo, useState } from 'react';
import {
  construireAffectation,
  NOMS_JOURS,
  repartir,
  validerAffectation,
  type Infraction,
  type Jour,
  type JourneeTechnicien,
  type Referentiel,
  type Scenario,
  type Technicien,
  type Vacation,
} from '@sim/engine';

/** Clé d'une case de la grille. */
const cle = (technicienId: string, jour: Jour): string => `${technicienId}#${jour}`;

interface Glisse {
  readonly secteurId: string;
  readonly creneaux: number;
  /** Case d'origine, si l'on déplace une vacation déjà posée. */
  readonly origine?: string;
}

interface Props {
  readonly scenario: Scenario;
  readonly referentiel: Referentiel;
  readonly techniciens: readonly Technicien[];
}

export function GrilleAffectation({ scenario, referentiel, techniciens }: Props) {
  const [cases, setCases] = useState<Record<string, Vacation[]>>({});
  const [glisse, setGlisse] = useState<Glisse | null>(null);
  const [survol, setSurvol] = useState<string | null>(null);

  const nomSecteur = useMemo(
    () => new Map(referentiel.secteurs.map((s) => [s.id, s.nom])),
    [referentiel],
  );

  /** Ce que le scénario demande de placer, jour par jour et secteur par secteur. */
  const aPlacer = useMemo(() => {
    const parSecteurJour = new Map<string, number>();
    for (const offre of scenario.offres) {
      const parJour = repartir(offre.creneaux, offre.jours);
      for (let j = 0; j < 6; j++) {
        if (parJour[j]! > 0) parSecteurJour.set(`${offre.secteurId}#${j}`, parJour[j]!);
      }
    }
    return parSecteurJour;
  }, [scenario]);

  /** Ce qui est déjà posé, par secteur et par jour. */
  const dejaPose = useMemo(() => {
    const total = new Map<string, number>();
    for (const [k, vacations] of Object.entries(cases)) {
      const jour = Number(k.split('#')[1]);
      for (const v of vacations) {
        const c = `${v.secteurId}#${jour}`;
        total.set(c, (total.get(c) ?? 0) + v.creneaux);
      }
    }
    return total;
  }, [cases]);

  const affectation = useMemo((): JourneeTechnicien[] => {
    return Object.entries(cases)
      .filter(([, v]) => v.length > 0)
      .map(([k, vacations]) => {
        const [technicienId, jour] = k.split('#');
        return { technicienId: technicienId!, jour: Number(jour) as Jour, vacations };
      });
  }, [cases]);

  const infractions = useMemo(
    () => validerAffectation(affectation, techniciens, scenario, referentiel),
    [affectation, techniciens, scenario, referentiel],
  );

  /** Infractions regroupées par case, pour marquer la grille. */
  const infractionsParCase = useMemo(() => {
    const parCase = new Map<string, Infraction[]>();
    for (const i of infractions) {
      const k = cle(i.technicienId, i.jour);
      parCase.set(k, [...(parCase.get(k) ?? []), i]);
    }
    return parCase;
  }, [infractions]);

  const poser = useCallback(
    (destination: string, charge: Glisse) => {
      setCases((precedent) => {
        const suivant = { ...precedent };

        // Retirer de la case d'origine si l'on déplace.
        if (charge.origine && charge.origine !== destination) {
          const source = (suivant[charge.origine] ?? []).filter(
            (v) => v.secteurId !== charge.secteurId,
          );
          if (source.length > 0) suivant[charge.origine] = source;
          else delete suivant[charge.origine];
        }
        if (charge.origine === destination) return precedent;

        const existantes = suivant[destination] ?? [];
        const deja = existantes.find((v) => v.secteurId === charge.secteurId);
        suivant[destination] = deja
          ? existantes.map((v) =>
              v.secteurId === charge.secteurId ? { ...v, creneaux: v.creneaux + charge.creneaux } : v,
            )
          : [...existantes, { secteurId: charge.secteurId, creneaux: charge.creneaux }];
        return suivant;
      });
    },
    [],
  );

  const retirer = useCallback((k: string, secteurId: string) => {
    setCases((precedent) => {
      const restantes = (precedent[k] ?? []).filter((v) => v.secteurId !== secteurId);
      const suivant = { ...precedent };
      if (restantes.length > 0) suivant[k] = restantes;
      else delete suivant[k];
      return suivant;
    });
  }, []);

  const remplirAutomatiquement = useCallback(() => {
    const { affectation: proposee } = construireAffectation(scenario, referentiel, techniciens);
    const nouvelles: Record<string, Vacation[]> = {};
    for (const j of proposee) nouvelles[cle(j.technicienId, j.jour)] = [...j.vacations];
    setCases(nouvelles);
  }, [scenario, referentiel, techniciens]);

  const totalAPlacer = [...aPlacer.values()].reduce((s, x) => s + x, 0);
  const totalPose = [...dejaPose.values()].reduce((s, x) => s + x, 0);

  return (
    <>
      <section className="carte">
        <div className="entete-carte">
          <h2>Grille par technicien</h2>
          <div className="actions">
            <span className="message">
              {totalPose} / {totalAPlacer} créneaux placés
              {infractions.length > 0 && (
                <>
                  {' · '}
                  <span className="est-alerte">
                    {infractions.length} infraction{infractions.length > 1 ? 's' : ''}
                  </span>
                </>
              )}
            </span>
            <button type="button" className="bouton" onClick={remplirAutomatiquement}>
              Proposer une répartition
            </button>
            <button type="button" className="bouton" onClick={() => setCases({})} disabled={totalPose === 0}>
              Vider
            </button>
          </div>
        </div>

        <p className="aide" style={{ marginTop: 0, marginBottom: 12 }}>
          Faites glisser un secteur depuis la réserve du bas vers la case d’un technicien. Les règles
          sont vérifiées à chaque dépôt : capacité de {scenario.capaciteParTechJour} créneaux,{' '}
          {scenario.maxSecteursParTechJour} secteurs au plus dans la journée,{' '}
          {scenario.distanceMaxEnchainement} km entre deux secteurs enchaînés.
        </p>

        <div className="enveloppe-table">
          <table className="grille">
            <thead>
              <tr>
                <th>Technicien</th>
                {NOMS_JOURS.slice(0, scenario.regime).map((nom) => (
                  <th key={nom}>{nom}</th>
                ))}
                <th className="num">Total</th>
              </tr>
            </thead>
            <tbody>
              {techniciens.map((tech) => {
                const totalTech = NOMS_JOURS.slice(0, scenario.regime).reduce(
                  (s, _, j) =>
                    s + (cases[cle(tech.id, j as Jour)] ?? []).reduce((t, v) => t + v.creneaux, 0),
                  0,
                );
                return (
                  <tr key={tech.id}>
                    <td className="cellule-tech">
                      <span className="nom-secteur">{tech.nom}</span>
                      <span className="meta-tech">
                        {tech.societe} · {tech.activite} · {tech.regime} j
                        {tech.zoneId ? ` · ${tech.zoneId}` : ' · mobile'}
                      </span>
                    </td>
                    {NOMS_JOURS.slice(0, scenario.regime).map((_, index) => {
                      const jour = index as Jour;
                      const k = cle(tech.id, jour);
                      const vacations = cases[k] ?? [];
                      const repos = jour >= tech.regime;
                      const problemes = infractionsParCase.get(k) ?? [];
                      const total = vacations.reduce((s, v) => s + v.creneaux, 0);
                      return (
                        <td
                          key={k}
                          className={[
                            'case-jour',
                            repos ? 'case-repos' : '',
                            survol === k ? 'case-survol' : '',
                            problemes.length > 0 ? 'case-infraction' : '',
                          ]
                            .filter(Boolean)
                            .join(' ')}
                          title={problemes.map((p) => p.message).join('\n')}
                          onDragOver={(e) => {
                            if (repos || !glisse) return;
                            e.preventDefault();
                            setSurvol(k);
                          }}
                          onDragLeave={() => setSurvol((s) => (s === k ? null : s))}
                          onDrop={(e) => {
                            e.preventDefault();
                            setSurvol(null);
                            if (repos || !glisse) return;
                            poser(k, glisse);
                            setGlisse(null);
                          }}
                        >
                          {repos ? (
                            <span className="repos">repos</span>
                          ) : (
                            <>
                              {vacations.map((v) => (
                                <span
                                  key={v.secteurId}
                                  className="vacation"
                                  draggable
                                  onDragStart={() =>
                                    setGlisse({
                                      secteurId: v.secteurId,
                                      creneaux: v.creneaux,
                                      origine: k,
                                    })
                                  }
                                  onDragEnd={() => setGlisse(null)}
                                >
                                  {nomSecteur.get(v.secteurId) ?? v.secteurId}
                                  <b> {v.creneaux}</b>
                                  <button
                                    type="button"
                                    className="retirer"
                                    aria-label={`Retirer ${nomSecteur.get(v.secteurId)}`}
                                    onClick={() => retirer(k, v.secteurId)}
                                  >
                                    ×
                                  </button>
                                </span>
                              ))}
                              {total > 0 && (
                                <span
                                  className={`total-case ${
                                    total > scenario.capaciteParTechJour ? 'est-alerte' : ''
                                  }`}
                                >
                                  {total}/{scenario.capaciteParTechJour}
                                </span>
                              )}
                            </>
                          )}
                        </td>
                      );
                    })}
                    <td className="num">{totalTech}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <section className="carte">
        <h2>Réserve — créneaux à placer</h2>
        <p className="aide" style={{ marginTop: 0 }}>
          Ce que le scénario demande d’ouvrir, jour par jour. Un secteur disparaît de la réserve
          quand tous ses créneaux du jour sont posés.
        </p>
        <div className="reserve-jours">
          {NOMS_JOURS.slice(0, scenario.regime).map((nom, index) => {
            const jour = index as Jour;
            const restants = referentiel.secteurs
              .map((s) => {
                const demande = aPlacer.get(`${s.id}#${jour}`) ?? 0;
                const pose = dejaPose.get(`${s.id}#${jour}`) ?? 0;
                return { secteur: s, reste: demande - pose };
              })
              .filter((x) => x.reste > 0);
            return (
              <div className="colonne-jour" key={nom}>
                <h3>{nom}</h3>
                {restants.length === 0 ? (
                  <span className="vide">tout placé</span>
                ) : (
                  restants.map(({ secteur, reste }) => (
                    <span
                      key={secteur.id}
                      className="jeton"
                      draggable
                      onDragStart={() => setGlisse({ secteurId: secteur.id, creneaux: reste })}
                      onDragEnd={() => setGlisse(null)}
                    >
                      {secteur.nom}
                      <b> {reste}</b>
                    </span>
                  ))
                )}
              </div>
            );
          })}
        </div>
      </section>

      {infractions.length > 0 && (
        <section className="carte">
          <h2>
            Règles enfreintes — <span className="est-alerte">{infractions.length}</span>
          </h2>
          <ul className="liste-alertes">
            {infractions.map((i, index) => (
              <li key={`${i.code}-${i.technicienId}-${i.jour}-${index}`}>{i.message}</li>
            ))}
          </ul>
        </section>
      )}
    </>
  );
}
