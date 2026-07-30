'use client';

import { useCallback, useMemo, useState } from 'react';
import {
  evaluerScenario,
  formaterRythme,
  NOMS_JOURS,
  type Jour,
  type Referentiel,
  type Regime,
  type Resultat,
  type Scenario,
} from '@sim/engine';

const COULEUR_BONNE = 'var(--bon)';
const COULEUR_ALERTE = 'var(--alerte)';
const COULEUR_PRIMAIRE = 'var(--primaire)';
const COULEUR_ACCENT = 'var(--accent)';

const nombre = (x: number, decimales = 0): string =>
  x.toLocaleString('fr-FR', { minimumFractionDigits: decimales, maximumFractionDigits: decimales });

const pourcent = (x: number, decimales = 0): string =>
  Number.isFinite(x)
    ? `${(x * 100).toLocaleString('fr-FR', { minimumFractionDigits: decimales, maximumFractionDigits: decimales })} %`
    : '—';

interface Props {
  readonly referentiel: Referentiel;
  readonly preregles: readonly Scenario[];
  readonly scenario: Scenario;
  readonly setScenario: React.Dispatch<React.SetStateAction<Scenario>>;
}

export function Simulateur({ referentiel, preregles, scenario, setScenario }: Props) {
  const [message, setMessage] = useState<string | null>(null);
  const [enregistrement, setEnregistrement] = useState(false);
  const [export_, setExport] = useState(false);

  const resultat = useMemo((): Resultat | { erreur: string } => {
    try {
      return evaluerScenario(scenario, referentiel);
    } catch (erreur) {
      return { erreur: erreur instanceof Error ? erreur.message : String(erreur) };
    }
  }, [scenario, referentiel]);

  const modifier = useCallback(
    (maj: Partial<Scenario>) => {
      setScenario((s) => ({ ...s, ...maj }));
      setMessage(null);
    },
    [setScenario],
  );

  /** Change de régime en retirant les samedis devenus impossibles. */
  const changerRegime = useCallback(
    (regime: Regime) => {
      setScenario((s) => ({
        ...s,
        regime,
        offres: s.offres.map((o) => ({ ...o, jours: o.jours.filter((j) => j < regime) })),
      }));
      setMessage(null);
    },
    [setScenario],
  );

  const basculerJour = useCallback((secteurId: string, jour: Jour) => {
    setScenario((s) => ({
      ...s,
      offres: s.offres.map((o) =>
        o.secteurId === secteurId
          ? {
              ...o,
              jours: o.jours.includes(jour)
                ? o.jours.filter((j) => j !== jour)
                : [...o.jours, jour].sort((a, b) => a - b),
            }
          : o,
      ),
    }));
    setMessage(null);
  }, [setScenario]);

  const changerCreneaux = useCallback((secteurId: string, creneaux: number) => {
    setScenario((s) => ({
      ...s,
      offres: s.offres.map((o) =>
        o.secteurId === secteurId ? { ...o, creneaux: Math.max(0, Math.round(creneaux) || 0) } : o,
      ),
    }));
    setMessage(null);
  }, [setScenario]);

  const chargerPrereglage = useCallback(
    (id: string) => {
      const trouve = preregles.find((p) => p.id === id);
      if (trouve) {
        setScenario({ ...trouve });
        setMessage(null);
      }
    },
    [preregles, setScenario],
  );

  const enregistrer = useCallback(async () => {
    setEnregistrement(true);
    setMessage(null);
    try {
      const reponse = await fetch('/api/scenarios', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ scenario }),
      });
      if (!reponse.ok) {
        const corps = await reponse.json().catch(() => ({}));
        throw new Error(corps.erreur ?? `Erreur ${reponse.status}`);
      }
      setMessage(`Scénario « ${scenario.nom} » enregistré.`);
    } catch (erreur) {
      setMessage(erreur instanceof Error ? erreur.message : 'Enregistrement impossible.');
    } finally {
      setEnregistrement(false);
    }
  }, [scenario]);

  const exporter = useCallback(async () => {
    setExport(true);
    setMessage(null);
    try {
      const reponse = await fetch('/api/export', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ scenarios: [scenario], departement: scenario.departement }),
      });
      if (!reponse.ok) {
        const corps = await reponse.json().catch(() => ({}));
        throw new Error(corps.erreur ?? `Erreur ${reponse.status}`);
      }
      // Nom de fichier fourni par le serveur, dans l'en-tête content-disposition.
      const entete = reponse.headers.get('content-disposition') ?? '';
      const nomFichier = /filename="([^"]+)"/.exec(entete)?.[1] ?? 'dimensionnement.xlsx';
      const blob = await reponse.blob();
      const lien = document.createElement('a');
      lien.href = URL.createObjectURL(blob);
      lien.download = nomFichier;
      lien.click();
      URL.revokeObjectURL(lien.href);
      setMessage(`Classeur « ${nomFichier} » téléchargé.`);
    } catch (erreur) {
      setMessage(erreur instanceof Error ? erreur.message : 'Export impossible.');
    } finally {
      setExport(false);
    }
  }, [scenario]);

  if ('erreur' in resultat) {
    return (
      <div className="carte">
        <h2>Scénario impossible à évaluer</h2>
        <p className="message">{resultat.erreur}</p>
      </div>
    );
  }

  const alertesDelai = resultat.alertes.filter((a) => a.code === 'delai-j2');
  const alertesCouverture = resultat.alertes.filter((a) => a.code === 'couverture');
  const nbSecteurs = referentiel.secteurs.length;

  return (
    <>
      <div className="reserve">
        <span className="reserve-icone" aria-hidden="true">
          !
        </span>
        <div>
          <b>Aucun volume SAV mesuré n’alimente ce calcul.</b> La demande affichée ne couvre que la
          production. Le SAV est absorbé implicitement par l’écart entre l’offre ouverte et cette
          demande. Tant qu’un relevé SAV réel n’aura pas été fait, l’effectif calculé reste un
          minimum structurel : journée de pointe par zone, sans absences ni congés.
        </div>
      </div>

      <section className="carte">
        <h2>Réglages</h2>
        <div className="reglages">
          <div className="champ">
            <label htmlFor="prereglage">Préréglage</label>
            <select id="prereglage" value={scenario.id} onChange={(e) => chargerPrereglage(e.target.value)}>
              {preregles.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.nom}
                </option>
              ))}
              {!preregles.some((p) => p.id === scenario.id) && (
                <option value={scenario.id}>{scenario.nom}</option>
              )}
            </select>
          </div>

          <div className="champ">
            <label htmlFor="regime">Semaine</label>
            <select
              id="regime"
              value={scenario.regime}
              onChange={(e) => changerRegime(Number(e.target.value) as Regime)}
            >
              <option value={5}>5 jours — lundi à vendredi</option>
              <option value={6}>6 jours — lundi à samedi</option>
            </select>
          </div>

          <div className="champ">
            <label htmlFor="capacite">Créneaux par technicien et par jour</label>
            <input
              id="capacite"
              type="number"
              min={1}
              max={24}
              value={scenario.capaciteParTechJour}
              onChange={(e) => modifier({ capaciteParTechJour: Math.max(1, Number(e.target.value) || 1) })}
            />
          </div>

          <div className="champ">
            <label htmlFor="couverture">Couverture visée</label>
            <input
              id="couverture"
              type="number"
              min={50}
              max={400}
              step={5}
              value={Math.round(scenario.couvertureCible * 100)}
              onChange={(e) =>
                modifier({ couvertureCible: Math.max(0.5, (Number(e.target.value) || 100) / 100) })
              }
            />
            <span className="aide">en % de la demande</span>
          </div>

          <div className="champ">
            <label htmlFor="mois">Mois de dimensionnement</label>
            <select
              id="mois"
              value={scenario.paramsDemande.mois}
              onChange={(e) =>
                modifier({
                  paramsDemande: {
                    ...scenario.paramsDemande,
                    mois: e.target.value as typeof scenario.paramsDemande.mois,
                  },
                })
              }
            >
              <option value="pic">Le plus chargé des deux</option>
              <option value="moyenne">Moyenne octobre / mars</option>
              <option value="octobre">Octobre</option>
              <option value="mars">Mars</option>
            </select>
          </div>

          <div className="champ">
            <label htmlFor="marge">Marge de flexibilité</label>
            <input
              id="marge"
              type="number"
              min={0}
              max={100}
              step={5}
              value={Math.round(scenario.paramsDemande.margeFlexibilite * 100)}
              onChange={(e) =>
                modifier({
                  paramsDemande: {
                    ...scenario.paramsDemande,
                    margeFlexibilite: Math.min(1, Math.max(0, (Number(e.target.value) || 0) / 100)),
                  },
                })
              }
            />
            <span className="aide">ajoutée à la demande, en %</span>
          </div>
        </div>
      </section>

      <div className="indicateurs">
        <Indicateur
          libelle="Créneaux ouverts"
          valeur={nombre(resultat.offreTotale)}
          detail={`pour ${nombre(resultat.demandeTotale, 1)} de demande`}
        />
        <Indicateur
          libelle="Couverture"
          valeur={pourcent(resultat.couverture)}
          detail={`cible ${pourcent(scenario.couvertureCible)}`}
          etat={resultat.couverture >= scenario.couvertureCible ? 'bon' : 'alerte'}
        />
        <Indicateur
          libelle="Alertes J+2"
          valeur={`${resultat.nbAlertesJ2} / ${nbSecteurs}`}
          detail={resultat.nbAlertesJ2 === 0 ? 'délai tenu partout' : 'secteurs hors délai'}
          etat={resultat.nbAlertesJ2 === 0 ? 'bon' : 'alerte'}
        />
        <Indicateur
          libelle="Techniciens"
          valeur={nombre(resultat.effectifMinimum)}
          detail={
            scenario.regime === 6
              ? `dont ${resultat.effectifSamedi} le samedi`
              : 'minimum structurel'
          }
        />
        <Indicateur
          libelle="Occupation"
          valeur={pourcent(resultat.occupation)}
          detail={`capacité ${nombre(resultat.capaciteTotale)}`}
          etat={resultat.occupation > 0.9 ? 'attention' : undefined}
        />
        <Indicateur
          libelle="Kilomètres"
          valeur={nombre(Math.round(resultat.kmSemaine))}
          detail="par semaine"
        />
      </div>

      <section className="carte">
        <h2>Secteurs</h2>
        <div className="enveloppe-table">
          <table>
            <thead>
              <tr>
                <th>Secteur</th>
                <th className="num">Demande</th>
                <th className="num">Créneaux</th>
                <th className="num">Couverture</th>
                <th>Jours de passage</th>
                <th className="num">Écart</th>
                <th>Délai J+2</th>
                <th className="num">Km/sem</th>
              </tr>
            </thead>
            <tbody>
              {resultat.secteurs.map((s) => {
                const offre = scenario.offres.find((o) => o.secteurId === s.secteurId);
                return (
                  <tr key={s.secteurId}>
                    <td>
                      <span className="nom-secteur">{s.nom}</span>
                      <span className="zone-puce">{s.zoneId}</span>
                    </td>
                    <td className="num">{nombre(s.demandeHebdo, 1)}</td>
                    <td className="num">
                      <input
                        className="saisie-creneaux"
                        type="number"
                        min={0}
                        max={1000}
                        aria-label={`Créneaux sur ${s.nom}`}
                        value={offre?.creneaux ?? 0}
                        onChange={(e) => changerCreneaux(s.secteurId, Number(e.target.value))}
                      />
                    </td>
                    <td className={`num ${s.couvertureSuffisante ? 'est-bon' : 'est-attention'}`}>
                      {pourcent(s.couverture)}
                    </td>
                    <td>
                      <div className="jours" role="group" aria-label={`Jours de passage sur ${s.nom}`}>
                        {NOMS_JOURS.map((nom, index) => {
                          const jour = index as Jour;
                          const actif = s.jours.includes(jour);
                          const indisponible = jour >= scenario.regime;
                          return (
                            <button
                              key={nom}
                              type="button"
                              className="jour"
                              aria-pressed={actif}
                              aria-label={`${nom} sur ${s.nom}`}
                              disabled={indisponible}
                              onClick={() => basculerJour(s.secteurId, jour)}
                            >
                              {nom.slice(0, 2)}
                            </button>
                          );
                        })}
                      </div>
                    </td>
                    <td className="num">{Number.isFinite(s.ecartMax) ? s.ecartMax : '—'}</td>
                    <td>
                      <span className={`etat ${s.conformeJ2 ? 'etat-bon' : 'etat-alerte'}`}>
                        {s.conformeJ2 ? formaterRythme(s.jours) || 'conforme' : 'hors délai'}
                      </span>
                    </td>
                    <td className="num">{nombre(Math.round(s.kmSemaine))}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      <div className="graphiques">
        <section className="carte">
          <h2>Couverture par secteur</h2>
          <Barres
            lignes={resultat.secteurs
              .slice()
              .sort((a, b) => a.couverture - b.couverture)
              .map((s) => ({
                libelle: s.nom,
                valeur: Number.isFinite(s.couverture) ? s.couverture : 0,
                texte: pourcent(s.couverture),
                couleur: s.couvertureSuffisante ? COULEUR_BONNE : COULEUR_ALERTE,
              }))}
            maximum={Math.max(
              scenario.couvertureCible * 1.3,
              ...resultat.secteurs.map((s) => (Number.isFinite(s.couverture) ? s.couverture : 0)),
            )}
            seuil={scenario.couvertureCible}
          />
          <div className="legende">
            <Legende couleur={COULEUR_BONNE} texte="couverture atteinte" />
            <Legende couleur={COULEUR_ALERTE} texte="en deçà de la cible" />
            <span className="legende-item">| repère : cible {pourcent(scenario.couvertureCible)}</span>
          </div>
        </section>

        <section className="carte">
          <h2>Écart maximal entre deux passages</h2>
          <Barres
            lignes={resultat.secteurs
              .slice()
              .sort((a, b) => b.ecartMax - a.ecartMax)
              .map((s) => ({
                libelle: s.nom,
                valeur: Number.isFinite(s.ecartMax) ? s.ecartMax : scenario.regime,
                texte: Number.isFinite(s.ecartMax) ? `${s.ecartMax} j` : '—',
                couleur: s.conformeJ2 ? COULEUR_BONNE : COULEUR_ALERTE,
              }))}
            maximum={scenario.regime}
            seuil={2}
          />
          <div className="legende">
            <span className="legende-item">| repère : 2 jours ouvrés, la limite du J+2</span>
          </div>
        </section>

        <section className="carte">
          <h2>Charge par jour</h2>
          <Barres
            lignes={NOMS_JOURS.slice(0, scenario.regime).map((nom, index) => ({
              libelle: nom,
              valeur: resultat.chargeParJour[index] ?? 0,
              texte: nombre(resultat.chargeParJour[index] ?? 0),
              couleur: COULEUR_PRIMAIRE,
            }))}
            maximum={Math.max(...resultat.chargeParJour, 1)}
          />
        </section>

        <section className="carte">
          <h2>Techniciens par zone</h2>
          <Barres
            lignes={referentiel.zones.map((z) => ({
              libelle: z.nom,
              valeur: resultat.effectifParZone[z.id] ?? 0,
              texte: nombre(resultat.effectifParZone[z.id] ?? 0),
              couleur: COULEUR_ACCENT,
            }))}
            maximum={Math.max(...Object.values(resultat.effectifParZone), 1)}
          />
        </section>
      </div>

      <section className="carte">
        <h2>
          Alertes {resultat.alertes.length > 0 && `— ${resultat.alertes.length}`}
        </h2>
        {resultat.alertes.length === 0 ? (
          <p className="vide">Aucune alerte : le délai est tenu partout et la couverture est atteinte.</p>
        ) : (
          <>
            {alertesDelai.length > 0 && (
              <>
                <h3>Délai J+2</h3>
                <ul className="liste-alertes">
                  {alertesDelai.map((a) => (
                    <li key={`${a.code}-${a.secteurId}`}>{a.message}</li>
                  ))}
                </ul>
              </>
            )}
            {alertesCouverture.length > 0 && (
              <>
                <h3 style={{ marginTop: alertesDelai.length > 0 ? 12 : 0 }}>Couverture</h3>
                <ul className="liste-alertes">
                  {alertesCouverture.map((a) => (
                    <li key={`${a.code}-${a.secteurId}`}>{a.message}</li>
                  ))}
                </ul>
              </>
            )}
          </>
        )}
      </section>

      <section className="carte">
        <h2>Enregistrer et exporter</h2>
        <div className="actions">
          <input
            className="saisie-creneaux"
            style={{ width: 260, textAlign: 'left' }}
            aria-label="Nom du scénario"
            value={scenario.nom}
            onChange={(e) => modifier({ nom: e.target.value })}
          />
          <button
            type="button"
            className="bouton bouton-primaire"
            onClick={() => void enregistrer()}
            disabled={enregistrement || scenario.nom.trim().length === 0}
          >
            {enregistrement ? 'Enregistrement…' : 'Enregistrer ce scénario'}
          </button>
          <button
            type="button"
            className="bouton"
            onClick={() => void exporter()}
            disabled={export_}
          >
            {export_ ? 'Génération…' : 'Exporter en Excel'}
          </button>
          <button
            type="button"
            className="bouton"
            onClick={() =>
              modifier({
                id: `copie-${Date.now().toString(36)}`,
                nom: `${scenario.nom} (copie)`,
              })
            }
          >
            Dupliquer sous un nouveau nom
          </button>
          {message && <span className="message">{message}</span>}
        </div>
      </section>
    </>
  );
}

function Indicateur({
  libelle,
  valeur,
  detail,
  etat,
}: {
  libelle: string;
  valeur: string;
  detail?: string;
  etat?: 'bon' | 'alerte' | 'attention';
}) {
  const classe = etat ? ` est-${etat}` : '';
  return (
    <div className="indicateur">
      <div className="indicateur-libelle">{libelle}</div>
      <div className={`indicateur-valeur${classe}`}>{valeur}</div>
      {detail && <div className="indicateur-detail">{detail}</div>}
    </div>
  );
}

interface LigneBarre {
  libelle: string;
  valeur: number;
  texte: string;
  couleur: string;
}

function Barres({
  lignes,
  maximum,
  seuil,
}: {
  lignes: readonly LigneBarre[];
  maximum: number;
  seuil?: number;
}) {
  const echelle = maximum > 0 ? maximum : 1;
  return (
    <div className="barres">
      {lignes.map((l) => (
        <div className="barre-ligne" key={l.libelle}>
          <span className="barre-libelle" title={l.libelle}>
            {l.libelle}
          </span>
          <span className="barre-piste">
            <span
              className="barre-remplissage"
              style={{
                width: `${Math.min(100, (l.valeur / echelle) * 100)}%`,
                background: l.couleur,
              }}
            />
            {seuil !== undefined && seuil <= echelle && (
              <span className="barre-seuil" style={{ left: `${(seuil / echelle) * 100}%` }} />
            )}
          </span>
          <span className="barre-valeur">{l.texte}</span>
        </div>
      ))}
    </div>
  );
}

function Legende({ couleur, texte }: { couleur: string; texte: string }) {
  return (
    <span className="legende-item">
      <span className="legende-pastille" style={{ background: couleur }} />
      {texte}
    </span>
  );
}
