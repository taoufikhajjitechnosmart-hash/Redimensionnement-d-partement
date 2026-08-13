/**
 * Version autonome du simulateur, destinée à être publiée en page unique.
 *
 * Elle importe le moteur et le référentiel du dépôt : aucune règle n'est
 * réécrite ici, seule l'interface l'est. Ce qui suppose un serveur — import du
 * classeur, export Excel, base de données — n'y figure pas ; les scénarios sont
 * conservés dans le navigateur.
 */
import {
  construireAffectation,
  evaluerScenario,
  formaterRythme,
  NOMS_JOURS,
  repartir,
  validerAffectation,
  type Jour,
  type Regime,
  type Resultat,
  type Scenario,
  type Vacation,
} from '@sim/engine';
import { REFERENTIEL_41, SCENARIOS_41, TECHNICIENS_41 } from '@sim/data';

const REF = REFERENTIEL_41;
const TECHS = TECHNICIENS_41;
const CLE_STOCKAGE = 'simulateur-41-scenarios';

type Onglet = 'dimensionnement' | 'grille' | 'comparaison';

interface Etat {
  onglet: Onglet;
  scenario: Scenario;
  cases: Record<string, Vacation[]>;
  selection: string[];
  message: string | null;
}

const etat: Etat = {
  onglet: 'dimensionnement',
  scenario: structuredClone(SCENARIOS_41[0]!),
  cases: {},
  selection: ['__courant__'],
  message: null,
};

// ── Utilitaires ────────────────────────────────────────────────────────────

const nb = (x: number, d = 0): string =>
  Number.isFinite(x)
    ? x.toLocaleString('fr-FR', { minimumFractionDigits: d, maximumFractionDigits: d })
    : '—';

const pct = (x: number): string => (Number.isFinite(x) ? `${Math.round(x * 100)} %` : '—');

const echapper = (s: string): string =>
  s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

const cle = (t: string, j: Jour): string => `${t}#${j}`;

function scenariosEnregistres(): Scenario[] {
  try {
    const brut = localStorage.getItem(CLE_STOCKAGE);
    return brut ? (JSON.parse(brut) as Scenario[]) : [];
  } catch {
    return [];
  }
}

function enregistrer(scenario: Scenario): void {
  const liste = scenariosEnregistres().filter((s) => s.id !== scenario.id);
  liste.push(structuredClone(scenario));
  localStorage.setItem(CLE_STOCKAGE, JSON.stringify(liste));
}

// ── Fragments réutilisables ────────────────────────────────────────────────

function indicateur(libelle: string, valeur: string, detail: string, etatVis?: string): string {
  return `<div class="kpi">
    <div class="kpi-lib">${echapper(libelle)}</div>
    <div class="kpi-val ${etatVis ? `est-${etatVis}` : ''}">${echapper(valeur)}</div>
    <div class="kpi-det">${echapper(detail)}</div>
  </div>`;
}

interface LigneBarre {
  libelle: string;
  valeur: number;
  texte: string;
  ton: 'bon' | 'alerte' | 'accent' | 'neutre';
}

function barres(lignes: LigneBarre[], maximum: number, seuil?: number): string {
  const echelle = maximum > 0 ? maximum : 1;
  const corps = lignes
    .map((l) => {
      const largeur = Math.min(100, (Math.max(0, l.valeur) / echelle) * 100);
      const repere =
        seuil !== undefined && seuil <= echelle
          ? `<i class="seuil" style="left:${(seuil / echelle) * 100}%"></i>`
          : '';
      return `<div class="barre-ligne">
        <span class="barre-lib" title="${echapper(l.libelle)}">${echapper(l.libelle)}</span>
        <span class="piste"><i class="remplissage ton-${l.ton}" style="width:${largeur.toFixed(1)}%"></i>${repere}</span>
        <span class="barre-val">${echapper(l.texte)}</span>
      </div>`;
    })
    .join('');
  return `<div class="barres">${corps}</div>`;
}

// ── Onglet Dimensionnement ─────────────────────────────────────────────────

function vueDimensionnement(r: Resultat): string {
  const s = etat.scenario;
  const alertesDelai = r.alertes.filter((a) => a.code === 'delai-j2');
  const alertesCouv = r.alertes.filter((a) => a.code === 'couverture');

  const reglages = `
  <section class="bloc">
    <h2>Réglages</h2>
    <div class="reglages">
      <label class="champ"><span>Préréglage</span>
        <select data-action="prereglage">
          ${SCENARIOS_41.map(
            (p) => `<option value="${p.id}" ${p.id === s.id ? 'selected' : ''}>${echapper(p.nom)}</option>`,
          ).join('')}
          ${SCENARIOS_41.some((p) => p.id === s.id) ? '' : `<option value="${echapper(s.id)}" selected>${echapper(s.nom)}</option>`}
        </select>
      </label>
      <label class="champ"><span>Semaine</span>
        <select data-action="regime">
          <option value="5" ${s.regime === 5 ? 'selected' : ''}>5 jours — lundi à vendredi</option>
          <option value="6" ${s.regime === 6 ? 'selected' : ''}>6 jours — lundi à samedi</option>
        </select>
      </label>
      <label class="champ"><span>Créneaux par technicien et par jour</span>
        <input type="number" min="1" max="24" value="${s.capaciteParTechJour}" data-action="capacite">
      </label>
      <label class="champ"><span>Couverture visée (%)</span>
        <input type="number" min="50" max="400" step="5" value="${Math.round(s.couvertureCible * 100)}" data-action="couverture">
      </label>
      <label class="champ"><span>Mois de dimensionnement</span>
        <select data-action="mois">
          ${(
            [
              ['pic', 'Le plus chargé des deux'],
              ['moyenne', 'Moyenne octobre / mars'],
              ['octobre', 'Octobre'],
              ['mars', 'Mars'],
            ] as const
          )
            .map(
              ([v, t]) =>
                `<option value="${v}" ${s.paramsDemande.mois === v ? 'selected' : ''}>${t}</option>`,
            )
            .join('')}
        </select>
      </label>
      <label class="champ"><span>Marge de flexibilité (%)</span>
        <input type="number" min="0" max="100" step="5" value="${Math.round(s.paramsDemande.margeFlexibilite * 100)}" data-action="marge">
      </label>
    </div>
  </section>`;

  const kpis = `<div class="kpis">
    ${indicateur('Créneaux ouverts', nb(r.offreTotale), `pour ${nb(r.demandeTotale, 1)} de demande`)}
    ${indicateur('Couverture', pct(r.couverture), `cible ${pct(s.couvertureCible)}`, r.couverture >= s.couvertureCible ? 'bon' : 'alerte')}
    ${indicateur('Alertes J+2', `${r.nbAlertesJ2} / ${REF.secteurs.length}`, r.nbAlertesJ2 === 0 ? 'délai tenu partout' : 'secteurs hors délai', r.nbAlertesJ2 === 0 ? 'bon' : 'alerte')}
    ${indicateur('Techniciens', nb(r.effectifMinimum), s.regime === 6 ? `dont ${r.effectifSamedi} le samedi` : 'minimum structurel')}
    ${indicateur('Occupation', pct(r.occupation), `capacité ${nb(r.capaciteTotale)}`, r.occupation > 0.9 ? 'attention' : undefined)}
    ${indicateur('Kilomètres', nb(Math.round(r.kmSemaine)), 'par semaine')}
  </div>`;

  const rangs = r.secteurs
    .map((sec) => {
      const offre = s.offres.find((o) => o.secteurId === sec.secteurId);
      const jours = NOMS_JOURS.map((nom, i) => {
        const actif = sec.jours.includes(i as Jour);
        const bloque = i >= s.regime;
        return `<button class="jour" type="button" aria-pressed="${actif}" ${bloque ? 'disabled' : ''}
          aria-label="${nom} sur ${echapper(sec.nom)}" data-jour="${i}" data-secteur="${sec.secteurId}">${nom.slice(0, 2)}</button>`;
      }).join('');
      return `<tr>
        <td><span class="nom">${echapper(sec.nom)}</span><span class="puce">${sec.zoneId}</span></td>
        <td class="num">${nb(sec.demandeHebdo, 1)}</td>
        <td class="num"><input class="saisie" type="number" min="0" max="1000" value="${offre?.creneaux ?? 0}"
            aria-label="Créneaux sur ${echapper(sec.nom)}" data-creneaux="${sec.secteurId}"></td>
        <td class="num ${sec.couvertureSuffisante ? 'est-bon' : 'est-attention'}">${pct(sec.couverture)}</td>
        <td><div class="jours">${jours}</div></td>
        <td class="num">${Number.isFinite(sec.ecartMax) ? sec.ecartMax : '—'}</td>
        <td><span class="etat ${sec.conformeJ2 ? 'etat-bon' : 'etat-alerte'}">${sec.conformeJ2 ? echapper(formaterRythme(sec.jours) || 'conforme') : 'hors délai'}</span></td>
        <td class="num">${nb(Math.round(sec.kmSemaine))}</td>
      </tr>`;
    })
    .join('');

  const tableau = `
  <section class="bloc">
    <h2>Secteurs</h2>
    <div class="defile">
      <table>
        <thead><tr>
          <th>Secteur</th><th class="num">Demande</th><th class="num">Créneaux</th><th class="num">Couverture</th>
          <th>Jours de passage</th><th class="num">Écart</th><th>Délai J+2</th><th class="num">Km/sem</th>
        </tr></thead>
        <tbody>${rangs}</tbody>
      </table>
    </div>
  </section>`;

  const maxCouv = Math.max(
    s.couvertureCible * 1.3,
    ...r.secteurs.map((x) => (Number.isFinite(x.couverture) ? x.couverture : 0)),
  );
  const graphiques = `
  <div class="grille-graphes">
    <section class="bloc"><h2>Couverture par secteur</h2>
      ${barres(
        [...r.secteurs]
          .sort((a, b) => a.couverture - b.couverture)
          .map((x) => ({
            libelle: x.nom,
            valeur: Number.isFinite(x.couverture) ? x.couverture : 0,
            texte: pct(x.couverture),
            ton: x.couvertureSuffisante ? ('bon' as const) : ('alerte' as const),
          })),
        maxCouv,
        s.couvertureCible,
      )}
      <p class="note">Repère vertical : la couverture visée, ${pct(s.couvertureCible)}.</p>
    </section>
    <section class="bloc"><h2>Écart maximal entre deux passages</h2>
      ${barres(
        [...r.secteurs]
          .sort((a, b) => b.ecartMax - a.ecartMax)
          .map((x) => ({
            libelle: x.nom,
            valeur: Number.isFinite(x.ecartMax) ? x.ecartMax : s.regime,
            texte: Number.isFinite(x.ecartMax) ? `${x.ecartMax} j` : '—',
            ton: x.conformeJ2 ? ('bon' as const) : ('alerte' as const),
          })),
        s.regime,
        2,
      )}
      <p class="note">Repère vertical : 2 jours ouvrés, la limite du J+2.</p>
    </section>
    <section class="bloc"><h2>Charge par jour</h2>
      ${barres(
        NOMS_JOURS.slice(0, s.regime).map((nom, i) => ({
          libelle: nom,
          valeur: r.chargeParJour[i] ?? 0,
          texte: nb(r.chargeParJour[i] ?? 0),
          ton: 'accent' as const,
        })),
        Math.max(...r.chargeParJour, 1),
      )}
    </section>
    <section class="bloc"><h2>Techniciens par zone</h2>
      ${barres(
        REF.zones.map((z) => ({
          libelle: z.nom,
          valeur: r.effectifParZone[z.id] ?? 0,
          texte: nb(r.effectifParZone[z.id] ?? 0),
          ton: 'neutre' as const,
        })),
        Math.max(...Object.values(r.effectifParZone), 1),
      )}
    </section>
  </div>`;

  const alertes = `
  <section class="bloc">
    <h2>Alertes${r.alertes.length ? ` — ${r.alertes.length}` : ''}</h2>
    ${
      r.alertes.length === 0
        ? '<p class="vide">Aucune alerte : le délai est tenu partout et la couverture est atteinte.</p>'
        : `${alertesDelai.length ? `<h3>Délai J+2</h3><ul class="liste">${alertesDelai.map((a) => `<li>${echapper(a.message)}</li>`).join('')}</ul>` : ''}
           ${alertesCouv.length ? `<h3>Couverture</h3><ul class="liste">${alertesCouv.map((a) => `<li>${echapper(a.message)}</li>`).join('')}</ul>` : ''}`
    }
  </section>`;

  const actions = `
  <section class="bloc">
    <h2>Enregistrer</h2>
    <div class="actions">
      <input class="saisie large" value="${echapper(s.nom)}" aria-label="Nom du scénario" data-action="nom">
      <button class="bouton primaire" type="button" data-action="enregistrer">Enregistrer dans ce navigateur</button>
      <button class="bouton" type="button" data-action="dupliquer">Dupliquer</button>
      ${etat.message ? `<span class="message">${echapper(etat.message)}</span>` : ''}
    </div>
  </section>`;

  return reglages + kpis + tableau + graphiques + alertes + actions;
}

// ── Onglet Grille ──────────────────────────────────────────────────────────

function vueGrille(): string {
  const s = etat.scenario;
  const nomSecteur = new Map(REF.secteurs.map((x) => [x.id, x.nom]));

  const aPlacer = new Map<string, number>();
  for (const offre of s.offres) {
    const parJour = repartir(offre.creneaux, offre.jours);
    for (let j = 0; j < 6; j++) {
      if (parJour[j]! > 0) aPlacer.set(`${offre.secteurId}#${j}`, parJour[j]!);
    }
  }

  const pose = new Map<string, number>();
  for (const [k, vacations] of Object.entries(etat.cases)) {
    const jour = Number(k.split('#')[1]);
    for (const v of vacations) {
      const c = `${v.secteurId}#${jour}`;
      pose.set(c, (pose.get(c) ?? 0) + v.creneaux);
    }
  }

  const affectation = Object.entries(etat.cases)
    .filter(([, v]) => v.length > 0)
    .map(([k, vacations]) => {
      const [t, j] = k.split('#');
      return { technicienId: t!, jour: Number(j) as Jour, vacations };
    });
  const infractions = validerAffectation(affectation, TECHS, s, REF);
  const parCase = new Map<string, string[]>();
  for (const i of infractions) {
    const k = cle(i.technicienId, i.jour);
    parCase.set(k, [...(parCase.get(k) ?? []), i.message]);
  }

  const totalAPlacer = [...aPlacer.values()].reduce((a, b) => a + b, 0);
  const totalPose = [...pose.values()].reduce((a, b) => a + b, 0);

  const rangs = TECHS.map((tech) => {
    const cellules = NOMS_JOURS.slice(0, s.regime)
      .map((_, index) => {
        const jour = index as Jour;
        const k = cle(tech.id, jour);
        const vacations = etat.cases[k] ?? [];
        const repos = jour >= tech.regime;
        const problemes = parCase.get(k) ?? [];
        const total = vacations.reduce((a, v) => a + v.creneaux, 0);
        const contenu = repos
          ? '<span class="repos">repos</span>'
          : vacations
              .map(
                (v) => `<span class="vacation" draggable="true" data-de="${k}" data-secteur="${v.secteurId}">
                  ${echapper(nomSecteur.get(v.secteurId) ?? v.secteurId)} <b>${v.creneaux}</b>
                  <button class="retirer" type="button" aria-label="Retirer" data-retirer="${k}" data-secteur="${v.secteurId}">×</button>
                </span>`,
              )
              .join('') +
            (total > 0
              ? `<span class="total-case ${total > s.capaciteParTechJour ? 'est-alerte' : ''}">${total}/${s.capaciteParTechJour}</span>`
              : '');
        const classes = ['case', repos ? 'case-repos' : '', problemes.length ? 'case-faute' : '']
          .filter(Boolean)
          .join(' ');
        return `<td class="${classes}" data-case="${k}" ${problemes.length ? `title="${echapper(problemes.join(' · '))}"` : ''}>${contenu}</td>`;
      })
      .join('');
    const totalTech = NOMS_JOURS.slice(0, s.regime).reduce(
      (a, _, j) => a + (etat.cases[cle(tech.id, j as Jour)] ?? []).reduce((t, v) => t + v.creneaux, 0),
      0,
    );
    return `<tr>
      <td class="cel-tech"><span class="nom">${echapper(tech.nom)}</span>
        <span class="meta">${echapper(tech.societe)} · ${tech.activite} · ${tech.regime} j${tech.zoneId ? ` · ${tech.zoneId}` : ' · mobile'}</span></td>
      ${cellules}<td class="num">${totalTech}</td>
    </tr>`;
  }).join('');

  const reserve = NOMS_JOURS.slice(0, s.regime)
    .map((nom, index) => {
      const jour = index as Jour;
      const restants = REF.secteurs
        .map((sec) => ({
          sec,
          reste: (aPlacer.get(`${sec.id}#${jour}`) ?? 0) - (pose.get(`${sec.id}#${jour}`) ?? 0),
        }))
        .filter((x) => x.reste > 0);
      return `<div class="colonne">
        <h3>${nom}</h3>
        ${
          restants.length === 0
            ? '<span class="vide">tout placé</span>'
            : restants
                .map(
                  ({ sec, reste }) =>
                    `<span class="jeton" draggable="true" data-secteur="${sec.id}" data-creneaux="${reste}">${echapper(sec.nom)} <b>${reste}</b></span>`,
                )
                .join('')
        }
      </div>`;
    })
    .join('');

  return `
  <section class="bloc">
    <div class="entete-bloc">
      <h2>Grille par technicien</h2>
      <div class="actions">
        <span class="message">${totalPose} / ${totalAPlacer} créneaux placés${
          infractions.length ? ` · <span class="est-alerte">${infractions.length} infraction${infractions.length > 1 ? 's' : ''}</span>` : ''
        }</span>
        <button class="bouton" type="button" data-action="proposer">Proposer une répartition</button>
        <button class="bouton" type="button" data-action="vider" ${totalPose === 0 ? 'disabled' : ''}>Vider</button>
      </div>
    </div>
    <p class="note">Faites glisser un secteur depuis la réserve vers la case d’un technicien. Chaque dépôt est
      contrôlé : capacité de ${s.capaciteParTechJour} créneaux, ${s.maxSecteursParTechJour} secteurs au plus dans la
      journée, ${s.distanceMaxEnchainement} km entre deux secteurs enchaînés.</p>
    <div class="defile">
      <table class="grille">
        <thead><tr><th>Technicien</th>${NOMS_JOURS.slice(0, s.regime).map((n) => `<th>${n}</th>`).join('')}<th class="num">Total</th></tr></thead>
        <tbody>${rangs}</tbody>
      </table>
    </div>
  </section>
  <section class="bloc">
    <h2>Réserve — créneaux à placer</h2>
    <div class="reserve">${reserve}</div>
  </section>
  ${
    infractions.length
      ? `<section class="bloc"><h2>Règles enfreintes — <span class="est-alerte">${infractions.length}</span></h2>
         <ul class="liste">${infractions.map((i) => `<li>${echapper(i.message)}</li>`).join('')}</ul></section>`
      : ''
  }`;
}

// ── Onglet Comparaison ─────────────────────────────────────────────────────

function vueComparaison(): string {
  const disponibles: { cle: string; scenario: Scenario; origine: string }[] = [
    { cle: '__courant__', scenario: etat.scenario, origine: 'courant' },
    ...SCENARIOS_41.map((p) => ({ cle: `p:${p.id}`, scenario: p, origine: 'préréglage' })),
    ...scenariosEnregistres()
      .filter((e) => !SCENARIOS_41.some((p) => p.id === e.id))
      .map((e) => ({ cle: `e:${e.id}`, scenario: e, origine: 'enregistré' })),
  ];

  const choix = disponibles
    .map(
      (d) => `<label class="choix">
      <input type="checkbox" data-compare="${echapper(d.cle)}" ${etat.selection.includes(d.cle) ? 'checked' : ''}>
      <span>${echapper(d.scenario.nom)}<span class="puce">${d.origine}</span>
      <span class="note">${d.scenario.regime} j · ${d.scenario.capaciteParTechJour} cr/j</span></span>
    </label>`,
    )
    .join('');

  const colonnes = etat.selection
    .map((k) => disponibles.find((d) => d.cle === k))
    .filter((d): d is (typeof disponibles)[number] => Boolean(d))
    .map((d) => {
      try {
        return { nom: d.scenario.nom, r: evaluerScenario(d.scenario, REF) };
      } catch {
        return null;
      }
    })
    .filter((c): c is { nom: string; r: Resultat } => c !== null);

  if (colonnes.length === 0) {
    return `<section class="bloc"><h2>Scénarios à comparer</h2><div class="choix-liste">${choix}</div></section>
            <section class="bloc"><p class="vide">Cochez au moins un scénario.</p></section>`;
  }

  type Sens = 'bas' | 'aucun';
  const lignes: { lib: string; vals: number[]; fmt: (x: number) => string; sens: Sens; note?: string }[] = [
    { lib: 'Créneaux ouverts', vals: colonnes.map((c) => c.r.offreTotale), fmt: (x) => nb(x), sens: 'aucun' },
    { lib: 'Demande hebdomadaire', vals: colonnes.map((c) => c.r.demandeTotale), fmt: (x) => nb(x, 1), sens: 'aucun', note: 'dépend des paramètres de conversion' },
    { lib: 'Couverture', vals: colonnes.map((c) => c.r.couverture), fmt: pct, sens: 'aucun' },
    { lib: 'Alertes J+2', vals: colonnes.map((c) => c.r.nbAlertesJ2), fmt: (x) => `${nb(x)} / ${REF.secteurs.length}`, sens: 'bas' },
    { lib: 'Techniciens', vals: colonnes.map((c) => c.r.effectifMinimum), fmt: (x) => nb(x), sens: 'bas', note: 'minimum structurel, journée de pointe par zone' },
    { lib: 'dont le samedi', vals: colonnes.map((c) => c.r.effectifSamedi), fmt: (x) => nb(x), sens: 'aucun' },
    { lib: 'Occupation', vals: colonnes.map((c) => c.r.occupation), fmt: pct, sens: 'aucun' },
    { lib: 'Kilomètres par semaine', vals: colonnes.map((c) => Math.round(c.r.kmSemaine)), fmt: (x) => nb(x), sens: 'bas' },
  ];

  const corps = lignes
    .map((l) => {
      let cible: number | null = null;
      if (l.sens === 'bas' && l.vals.length > 1) {
        const m = Math.min(...l.vals.filter(Number.isFinite));
        cible = l.vals.every((v) => v === m) ? null : m;
      }
      return `<tr><td>${echapper(l.lib)}${l.note ? `<br><span class="note">${echapper(l.note)}</span>` : ''}</td>
        ${l.vals.map((v) => `<td class="num ${cible !== null && v === cible ? 'est-bon' : ''}">${echapper(l.fmt(v))}</td>`).join('')}</tr>`;
    })
    .join('');

  const parSecteur = REF.secteurs
    .map((sec) => {
      const cellules = colonnes
        .map((c) => {
          const x = c.r.secteurs.find((y) => y.secteurId === sec.id);
          if (!x) return '<td>—</td>';
          return `<td><span class="etat ${x.conformeJ2 ? 'etat-bon' : 'etat-alerte'}" title="${x.offre} créneaux · écart ${x.ecartMax} j">${
            x.conformeJ2 ? echapper(formaterRythme(x.jours) || '—') : `${x.ecartMax} j`
          }</span></td>`;
        })
        .join('');
      return `<tr><td class="nom">${echapper(sec.nom)}</td>${cellules}</tr>`;
    })
    .join('');

  const entetes = colonnes.map((c) => `<th class="num">${echapper(c.nom)}</th>`).join('');
  const entetesG = colonnes.map((c) => `<th>${echapper(c.nom)}</th>`).join('');

  return `
  <section class="bloc"><h2>Scénarios à comparer</h2><div class="choix-liste">${choix}</div></section>
  <section class="bloc">
    <h2>Comparaison</h2>
    <div class="defile"><table><thead><tr><th>Indicateur</th>${entetes}</tr></thead><tbody>${corps}</tbody></table></div>
    <p class="note">En vert, la meilleure valeur de la ligne lorsqu’un sens de lecture existe : moins d’alertes,
      moins de techniciens, moins de kilomètres. La couverture et l’occupation se lisent contre la cible du
      scénario, pas les unes contre les autres.</p>
  </section>
  <section class="bloc">
    <h2>Délai J+2, secteur par secteur</h2>
    <div class="defile"><table><thead><tr><th>Secteur</th>${entetesG}</tr></thead><tbody>${parSecteur}</tbody></table></div>
  </section>`;
}

// ── Rendu ──────────────────────────────────────────────────────────────────

const ONGLETS: { id: Onglet; libelle: string }[] = [
  { id: 'dimensionnement', libelle: 'Dimensionnement' },
  { id: 'grille', libelle: 'Grille par technicien' },
  { id: 'comparaison', libelle: 'Comparaison' },
];

function rendre(): void {
  const racine = document.getElementById('app');
  if (!racine) return;

  let contenu: string;
  try {
    const r = evaluerScenario(etat.scenario, REF);
    contenu =
      etat.onglet === 'dimensionnement'
        ? vueDimensionnement(r)
        : etat.onglet === 'grille'
          ? vueGrille()
          : vueComparaison();
  } catch (erreur) {
    contenu = `<section class="bloc"><h2>Scénario impossible à évaluer</h2>
      <p class="message est-alerte">${echapper(erreur instanceof Error ? erreur.message : String(erreur))}</p></section>`;
  }

  racine.innerHTML = `
    <div class="onglets" role="tablist">
      ${ONGLETS.map(
        (o) =>
          `<button class="onglet" role="tab" type="button" aria-selected="${etat.onglet === o.id}" data-onglet="${o.id}">${o.libelle}</button>`,
      ).join('')}
    </div>
    ${contenu}`;
}

// ── Interactions ───────────────────────────────────────────────────────────

let glisse: { secteurId: string; creneaux: number; origine?: string } | null = null;

function poser(destination: string, charge: NonNullable<typeof glisse>): void {
  if (charge.origine === destination) return;
  if (charge.origine) {
    const source = (etat.cases[charge.origine] ?? []).filter((v) => v.secteurId !== charge.secteurId);
    if (source.length) etat.cases[charge.origine] = source;
    else delete etat.cases[charge.origine];
  }
  const existantes = etat.cases[destination] ?? [];
  const deja = existantes.find((v) => v.secteurId === charge.secteurId);
  etat.cases[destination] = deja
    ? existantes.map((v) =>
        v.secteurId === charge.secteurId ? { ...v, creneaux: v.creneaux + charge.creneaux } : v,
      )
    : [...existantes, { secteurId: charge.secteurId, creneaux: charge.creneaux }];
}

document.addEventListener('click', (evenement) => {
  const cible = evenement.target as HTMLElement;
  const bouton = cible.closest<HTMLElement>('[data-onglet],[data-action],[data-jour],[data-retirer]');
  if (!bouton) return;

  const onglet = bouton.dataset.onglet as Onglet | undefined;
  if (onglet) {
    etat.onglet = onglet;
    etat.message = null;
    rendre();
    return;
  }

  if (bouton.dataset.retirer) {
    const k = bouton.dataset.retirer;
    const secteurId = bouton.dataset.secteur!;
    const restantes = (etat.cases[k] ?? []).filter((v) => v.secteurId !== secteurId);
    if (restantes.length) etat.cases[k] = restantes;
    else delete etat.cases[k];
    rendre();
    return;
  }

  if (bouton.dataset.jour !== undefined) {
    const jour = Number(bouton.dataset.jour) as Jour;
    const secteurId = bouton.dataset.secteur!;
    etat.scenario = {
      ...etat.scenario,
      offres: etat.scenario.offres.map((o) =>
        o.secteurId === secteurId
          ? {
              ...o,
              jours: o.jours.includes(jour)
                ? o.jours.filter((j) => j !== jour)
                : [...o.jours, jour].sort((a, b) => a - b),
            }
          : o,
      ),
    };
    etat.message = null;
    rendre();
    return;
  }

  switch (bouton.dataset.action) {
    case 'enregistrer':
      enregistrer(etat.scenario);
      etat.message = `Scénario « ${etat.scenario.nom} » enregistré dans ce navigateur.`;
      rendre();
      break;
    case 'dupliquer':
      etat.scenario = {
        ...etat.scenario,
        id: `copie-${Date.now().toString(36)}`,
        nom: `${etat.scenario.nom} (copie)`,
      };
      etat.message = null;
      rendre();
      break;
    case 'proposer': {
      const { affectation } = construireAffectation(etat.scenario, REF, TECHS);
      etat.cases = {};
      for (const j of affectation) etat.cases[cle(j.technicienId, j.jour)] = [...j.vacations];
      rendre();
      break;
    }
    case 'vider':
      etat.cases = {};
      rendre();
      break;
  }
});

document.addEventListener('change', (evenement) => {
  const cible = evenement.target as HTMLInputElement | HTMLSelectElement;
  const s = etat.scenario;

  if (cible.dataset.compare) {
    const k = cible.dataset.compare;
    etat.selection = (cible as HTMLInputElement).checked
      ? [...etat.selection, k]
      : etat.selection.filter((x) => x !== k);
    rendre();
    return;
  }

  if (cible.dataset.creneaux) {
    const secteurId = cible.dataset.creneaux;
    const valeur = Math.max(0, Math.round(Number(cible.value) || 0));
    etat.scenario = {
      ...s,
      offres: s.offres.map((o) => (o.secteurId === secteurId ? { ...o, creneaux: valeur } : o)),
    };
    etat.message = null;
    rendre();
    return;
  }

  switch (cible.dataset.action) {
    case 'prereglage': {
      const trouve = SCENARIOS_41.find((p) => p.id === cible.value);
      if (trouve) {
        etat.scenario = structuredClone(trouve);
        etat.cases = {};
      }
      break;
    }
    case 'regime': {
      const regime = Number(cible.value) as Regime;
      etat.scenario = {
        ...s,
        regime,
        offres: s.offres.map((o) => ({ ...o, jours: o.jours.filter((j) => j < regime) })),
      };
      etat.cases = {};
      break;
    }
    case 'capacite':
      etat.scenario = { ...s, capaciteParTechJour: Math.max(1, Number(cible.value) || 1) };
      break;
    case 'couverture':
      etat.scenario = { ...s, couvertureCible: Math.max(0.5, (Number(cible.value) || 100) / 100) };
      break;
    case 'mois':
      etat.scenario = {
        ...s,
        paramsDemande: { ...s.paramsDemande, mois: cible.value as typeof s.paramsDemande.mois },
      };
      break;
    case 'marge':
      etat.scenario = {
        ...s,
        paramsDemande: {
          ...s.paramsDemande,
          margeFlexibilite: Math.min(1, Math.max(0, (Number(cible.value) || 0) / 100)),
        },
      };
      break;
    case 'nom':
      etat.scenario = { ...s, nom: cible.value };
      break;
    default:
      return;
  }
  etat.message = null;
  rendre();
});

document.addEventListener('dragstart', (evenement) => {
  const cible = (evenement.target as HTMLElement).closest<HTMLElement>('.jeton,.vacation');
  if (!cible) return;
  glisse = {
    secteurId: cible.dataset.secteur!,
    creneaux: Number(cible.dataset.creneaux ?? 0),
    ...(cible.dataset.de ? { origine: cible.dataset.de } : {}),
  };
  if (cible.classList.contains('vacation') && cible.dataset.de) {
    const existante = (etat.cases[cible.dataset.de] ?? []).find(
      (v) => v.secteurId === cible.dataset.secteur,
    );
    glisse.creneaux = existante?.creneaux ?? 0;
  }
  evenement.dataTransfer?.setData('text/plain', cible.dataset.secteur ?? '');
});

document.addEventListener('dragover', (evenement) => {
  const cellule = (evenement.target as HTMLElement).closest<HTMLElement>('td.case');
  if (!cellule || cellule.classList.contains('case-repos') || !glisse) return;
  evenement.preventDefault();
  cellule.classList.add('case-survol');
});

document.addEventListener('dragleave', (evenement) => {
  (evenement.target as HTMLElement)
    .closest<HTMLElement>('td.case')
    ?.classList.remove('case-survol');
});

document.addEventListener('drop', (evenement) => {
  const cellule = (evenement.target as HTMLElement).closest<HTMLElement>('td.case');
  if (!cellule || cellule.classList.contains('case-repos') || !glisse) return;
  evenement.preventDefault();
  poser(cellule.dataset.case!, glisse);
  glisse = null;
  rendre();
});

document.addEventListener('dragend', () => {
  glisse = null;
  document.querySelectorAll('.case-survol').forEach((c) => c.classList.remove('case-survol'));
});

rendre();
