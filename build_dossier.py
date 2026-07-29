# -*- coding: utf-8 -*-
"""Dossier complet — planification SAV / PROD du département 41, tous scénarios."""
import json, math, importlib.util, io, contextlib

spec = importlib.util.spec_from_file_location("g", "grille436.py")
mB = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(mB)
GRID_BASE, JOURS = mB.GRID, mB.JOURS
R = json.load(open('grille436.json'))
S = json.load(open('simul5j.json'))
C1 = json.load(open('charts.json'))       # graphiques du premier rapport
C2 = json.load(open('charts_cmp.json'))   # graphiques comparatifs
J5 = JOURS[:5]
SAV_DEM = json.load(open('sav_reel.json'))
PROD_DEM = {"Blois": 61.7, "Pontlevoy": 22.5, "Crouy-sur-Cosson": 13.3, "Épiais": 12.9,
            "Mur-de-Sologne": 12.5, "Montoire-sur-le-Loir": 12.3, "Romorantin-Lanthenay": 11.3,
            "Valencisse": 11.1, "Vendôme": 9.8, "Vouzon": 8.5, "Cormenon": 4.9, "La Ferté-Imbault": 4.5}
SRC = {"Blois": (240, 218, 3.0), "Pontlevoy": (88, 84, 0.667), "Crouy-sur-Cosson": (52, 48, 0.333),
       "Épiais": (48, 50, 0.667), "Mur-de-Sologne": (49, 36, 0.333), "Montoire-sur-le-Loir": (37, 48, 0.333),
       "Romorantin-Lanthenay": (44, 31, 0.333), "Valencisse": (43, 42, 0.667), "Vendôme": (38, 34, 0.667),
       "Vouzon": (31, 33, 0.333), "Cormenon": (18, 19, 0.333), "La Ferté-Imbault": (17, 13, 0.667)}
SHORT = {"Montoire-sur-le-Loir": "Montoire", "Romorantin-Lanthenay": "Romorantin",
         "Crouy-sur-Cosson": "Crouy-s-Cosson", "La Ferté-Imbault": "La Ferté-Imb."}
ROLE_C = {"Blois": "Blois + Valencisse", "Nord": "Vendômois / Perche / Beauce",
          "Sologne Sud": "Sologne Sud", "Est": "Sologne Est", "Sud-Ouest": "Sud-Ouest"}
ROLES_B = {"T1": "SAV — Blois · Valencisse", "T2": "Nord — Vendômois / Perche", "T3": "Sologne Sud",
           "T4": "Sologne Est", "T5": "Sud-Ouest — Pontlevoy", "T6": "Blois — mixte",
           "T7": "Blois — PROD", "T8": "Blois — PROD", "T9": "Nord — PROD",
           "T10": "Sologne / Sud-Ouest — PROD", "T11": "Renfort flottant"}
ORDER = sorted(PROD_DEM, key=lambda x: -R['slots'][x])
A, B = S['A'], S['B']


def cell(sec, a, p):
    cls = "mix" if a and p else ("sav" if a else "prod")
    lbl = " · ".join(x for x in (f"SAV {a}" if a else "", f"PROD {p}" if p else "") if x)
    return (f'<td class="{cls}"><span class="sec">{SHORT.get(sec, sec)}</span>'
            f'<span class="cr">{lbl}</span></td>')


def _wrap_grid(rows, td, ts, tp, note):
    th = "".join(f'<th colspan="2">{j}</th>' for j in JOURS)
    sub = "".join('<th class="sub">matin</th><th class="sub">après-midi</th>' for _ in JOURS)
    return (f'<table class="grid"><thead><tr><th rowspan="2">Tech.</th><th rowspan="2">Secteurs</th>'
            f'<th rowspan="2">J</th>{th}<th rowspan="2">SAV</th><th rowspan="2">PROD</th></tr>'
            f'<tr>{sub}</tr></thead><tbody>{"".join(rows)}'
            f'<tr class="gtot"><td colspan="3">TOTAL — {td} jours-technicien</td>'
            f'<td colspan="12">12 secteurs · 3 passages SAV minimum chacun · {note}</td>'
            f'<td>{ts}</td><td>{tp}</td></tr></tbody></table>')


def grid_base():
    rows, ts, tp = [], 0, 0
    for t, role, nj, sem in GRID_BASE:
        cells, sv, pr = [], 0, 0
        for day in sem:
            if day is None:
                cells.append('<td class="off" colspan="2">repos</td>'); continue
            for sec, a, p in day:
                sv += a; pr += p; cells.append(cell(sec, a, p))
        ts += sv; tp += pr
        rows.append(f'<tr><td class="tid">{t}</td><td class="trole">{ROLES_B[t]}</td>'
                    f'<td class="tj{" six" if nj == 6 else ""}">{nj}</td>{"".join(cells)}'
                    f'<td class="num sav-n">{sv}</td><td class="num prod-n">{pr}</td></tr>')
    return _wrap_grid(rows, 60, ts, tp, "rythmes L-Me-V et Ma-J-S")


def grid_sim(lab):
    v = S[lab]
    rows, ts, tp = [], 0, 0
    for t, cl, nj in v['techs']:
        g = v['grille'][t]
        cells, sv, pr = [], 0, 0
        for j in JOURS:
            if j not in g:
                cells.append('<td class="off" colspan="2">repos</td>'); continue
            for k in (0, 1):
                c = g[j][k]
                if c is None:
                    cells.append('<td class="off">—</td>'); continue
                sec, a, p = c
                sv += a; pr += p; cells.append(cell(sec, a, p))
        ts += sv; tp += pr
        rows.append(f'<tr><td class="tid">{t}</td><td class="trole">{ROLE_C[cl]}</td>'
                    f'<td class="tj{" six" if nj == 6 else ""}">{nj}</td>{"".join(cells)}'
                    f'<td class="num sav-n">{sv}</td><td class="num prod-n">{pr}</td></tr>')
    return _wrap_grid(rows, v['td'], ts, tp,
                      "SAV du lundi au vendredi uniquement" if lab == 'A' else "semaine de 5 jours pour tous")


def controle(lab):
    if lab == 'base':
        sav, prod, slots, passages, jset = R['sav'], R['prod'], R['slots'], R['pass'], JOURS
    else:
        v = S[lab]
        sav, prod, slots, passages, jset = v['sav_sec'], v['prod_sec'], v['slots'], v['passages'], J5
    rows = []
    for s in sorted(slots, key=lambda x: -slots[x]):
        jp = passages[s]
        rows.append(f'<tr><td><b>{s}</b></td>'
                    f'<td class="c mono">{"-".join(x[:3] for x in sorted(jp, key=jset.index))}</td>'
                    f'<td class="c">{len(jp)}</td>'
                    f'<td class="n">{sav[s]}</td><td class="n dim">{SAV_DEM[s]}</td>'
                    f'<td class="n">{prod[s]}</td><td class="n dim">{PROD_DEM[s]}</td>'
                    f'<td class="n">{slots[s]}</td>'
                    f'<td class="c"><span class="pill ok">conforme</span></td></tr>')
    ts, tp = sum(sav.values()), sum(prod.values())
    rows.append(f'<tr class="tot"><td>TOTAL</td><td></td><td class="c">—</td>'
                f'<td class="n">{ts}</td><td class="n">142</td><td class="n">{tp}</td>'
                f'<td class="n">185,3</td><td class="n">{ts+tp}</td><td class="c">12 / 12</td></tr>')
    return ('<table class="data"><thead><tr><th>Secteur</th><th class="c">Rythme SAV</th>'
            '<th class="c">Passages</th><th class="n">SAV ouvert</th><th class="n">SAV dem.</th>'
            '<th class="n">PROD ouv.</th><th class="n">PROD dem.</th><th class="n">Total</th>'
            f'<th class="c">Contrôle</th></tr></thead><tbody>{"".join(rows)}</tbody></table>')


def demande_table():
    rows = []
    to, tm, tb, tp, ts = 0, 0, 0, 0, 0
    for s in ORDER:
        o, ma, b = SRC[s]
        to += o; tm += ma; tb += b; tp += PROD_DEM[s]; ts += SAV_DEM[s]
        rows.append(f'<tr><td><b>{s}</b></td><td class="n">{o}</td><td class="n">{ma}</td>'
                    f'<td class="n">{b:.2f}</td><td class="n">{max(o, ma)}</td>'
                    f'<td class="n">{PROD_DEM[s]}</td><td class="n">{SAV_DEM[s]}</td>'
                    f'<td class="n"><b>{PROD_DEM[s]+SAV_DEM[s]:.1f}</b></td></tr>')
    rows.append(f'<tr class="tot"><td>TOTAL 41</td><td class="n">{to}</td><td class="n">{tm}</td>'
                f'<td class="n">{tb:.1f}</td><td class="n">{sum(max(SRC[s][0], SRC[s][1]) for s in ORDER)}</td>'
                f'<td class="n">{tp:.1f}</td><td class="n">{ts}</td><td class="n">{tp+ts:.1f}</td></tr>')
    return ('<table class="data"><thead><tr><th>Secteur</th>'
            '<th class="n">PROD oct. /mois</th><th class="n">PROD mars /mois</th><th class="n">B2B /mois</th>'
            '<th class="n">Mois retenu</th><th class="n">PROD +10 % /sem.</th>'
            '<th class="n">SAV /sem.</th><th class="n">Demande /sem.</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')


PTS = [("Blois", 47.586, 1.336, "X"), ("Valencisse", 47.590, 1.220, "N"), ("Pontlevoy", 47.395, 1.256, "S"),
       ("Vendôme", 47.793, 1.066, "N"), ("Épiais", 47.760, 1.375, "N"), ("Montoire", 47.752, 0.866, "N"),
       ("Cormenon", 47.955, 0.980, "N"), ("Crouy-s-Cosson", 47.680, 1.610, "S"), ("Vouzon", 47.660, 2.020, "S"),
       ("Mur-de-Sologne", 47.383, 1.612, "S"), ("Romorantin", 47.357, 1.744, "S"), ("La Ferté-Imb.", 47.395, 1.976, "S")]


def km(a, b):
    x = math.radians(b[2] - a[2]) * math.cos(math.radians((a[1] + b[1]) / 2))
    y = math.radians(b[1] - a[1])
    d = 6371 * math.hypot(x, y) * 1.25
    return round(d + 8 if a[3] != b[3] and "X" not in (a[3], b[3]) else d)


def dist_table():
    head = "".join(f'<th class="rot"><span>{p[0]}</span></th>' for p in PTS)
    rows = []
    for a in PTS:
        cells = []
        for b in PTS:
            if a[0] == b[0]:
                cells.append('<td class="self">·</td>')
            else:
                d = km(a, b)
                cells.append(f'<td class="{"d1" if d <= 30 else ("d2" if d <= 50 else "d3")}">{d}</td>')
        rows.append(f'<tr><th class="rowh">{a[0]}</th>{"".join(cells)}</tr>')
    return f'<table class="dist"><thead><tr><th></th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


LIGNES = [
    ("SAV proposé", "lundi au samedi", "lundi au vendredi", "lundi au vendredi"),
    ("PROD réalisée", "lundi au samedi", "lundi au samedi", "lundi au vendredi"),
    ("Techniciens", "11", "11", "11"),
    ("dont à 6 jours", "5", "5", "0"),
    ("Jours-technicien / semaine", "60", "60", "55"),
    ("Capacité théorique (créneaux)", "480", "480", "440"),
    ("Créneaux réellement ouverts", "480", str(A['total']), str(B['total'])),
    ("Créneaux nécessaires (75 %)", "436", "436", "436"),
    ("Réserve", "+44", f"+{A['total']-A['besoin']}", f"{B['total']-B['besoin']}"),
    ("Occupation atteinte", "68,2 %", "70,8 %", "77,6 %"),
    ("Rythmes SAV disponibles", "2, disjoints", "5, jamais disjoints", "5, jamais disjoints"),
    ("Secteurs tenant le J+1/J+2", "12 / 12", "12 / 12", "12 / 12"),
    ("Trajet matin→après-midi max.", "30 km", f"{A['pire']} km", f"{B['pire']} km"),
    ("Techniciens sur la Sologne Est", "1", "2", "2"),
]


def cmp_table():
    tr = []
    for lab, base, a, b in LIGNES:
        ca = cb = ""
        if lab == "Réserve":
            ca, cb = "hi", "lo"
        if lab == "Occupation atteinte":
            cb = "lo"
        tr.append(f'<tr><td>{lab}</td><td>{base}</td><td class="{ca}">{a}</td><td class="{cb}">{b}</td></tr>')
    return ('<table class="cmp"><thead><tr><th>Critère</th><th>Base<br>SAV 6 jours</th>'
            '<th>Simulation A<br>SAV 5 j, PROD 6 j</th><th>Simulation B<br>tout 5 jours</th></tr></thead>'
            f'<tbody>{"".join(tr)}</tbody></table>')


REGLES = [
    ("Permanent", "<b>La tournée est figée.</b> Technicien × jour × secteur ne change jamais : distances maîtrisées, techniciens sur des secteurs qu'ils connaissent."),
    ("Permanent", "<b>Trois passages par semaine et par secteur.</b> C'est ce qui garantit mécaniquement le J+1/J+2."),
    ("Permanent", "Sur chaque demi-journée, un nombre fixe de créneaux est réservé au SAV. <b>L'occupation ne dépasse jamais 75 %</b> : le quart restant est la disponibilité."),
    ("J-7 à J-5", "La PROD se pose uniquement sur les créneaux non réservés au SAV, dans le carnet J+5 à J+7."),
    ("J-2, 18 h", "Ouverture à la prise de RDV SAV des créneaux réservés du jour J."),
    ("J-1, 18 h", "<b>Bascule.</b> Tout créneau SAV encore libre pour le lendemain est réaffecté à une intervention PROD <b>du même secteur</b>. Aucun créneau perdu."),
    ("J-1, 18 h", "La bascule suppose au moins deux interventions PROD en attente dans le secteur. Sur Cormenon et La Ferté-Imbault, maintenir ce stock tampon."),
    ("Jour J", "Un SAV urgent arrivé après la bascule prend la place d'une PROD du jour, qui repart en J+5. <b>La PROD absorbe l'aléa, jamais le SAV.</b>"),
    ("Hebdo", "Si l'occupation SAV d'un secteur dépasse 75 % quatre semaines de suite, augmenter sa réservation."),
    ("Hebdo", "Le renfort flottant est affecté le vendredi pour la semaine suivante, au secteur dont le carnet est le plus tendu."),
]

QUESTIONS = [
    ("8 créneaux par technicien et par jour, est-ce tenable ?",
     "C'est l'hypothèse qui fait tenir l'ensemble. Votre planning SAV actuel tourne à <b>5,68 créneaux</b> : passer à 8 représente <b>+41 %</b>. Si le réel plafonne à 7, la capacité tombe à 420 créneaux en simulation A et 385 en B — et aucun scénario ne tient plus. C'est la seule mesure à faire sur le terrain avant d'arbitrer."),
    ("La répartition des créneaux entre secteurs vous convient-elle ?",
     "Elle est faite au prorata de la demande totale de chaque secteur. Si un secteur mérite plus de disponibilité que son volume ne le justifie — NRO récent, client sensible, zone à reprises fréquentes — la réservation peut être décalée sans toucher à la structure."),
    ("Où habitent les techniciens ?",
     "Les bases proposées (Blois, Vendôme, Romorantin, Crouy-sur-Cosson, Pontlevoy) sont déduites de la seule géographie. Si les domiciles réels sont ailleurs, les binômes de secteurs se réorganisent : c'est du temps de trajet payé tous les jours."),
    ("Le carnet PROD est-il assez fourni sur les petits secteurs ?",
     "Cormenon fait 19 interventions PROD par mois, La Ferté-Imbault 18 : moins d'une par jour ouvré. Si le carnet y est vide, un créneau SAV non vendu est perdu au lieu d'être recyclé par la bascule."),
    ("Y a-t-il des pénalités contractuelles sur le J+1/J+2 ?",
     "Si oui, le taux d'occupation cible doit être calé sur le pire cas et non sur la moyenne. À 65 % au lieu de 75 %, la cible passerait à 503 créneaux, au-delà de ce que 11 techniciens peuvent ouvrir."),
    ("Les volumes PROD d'octobre sont-ils une prévision ou un historique ?",
     "Le calcul retient le mois le plus chargé entre octobre et mars, secteur par secteur. Si octobre est une prévision haute qui ne se réalisera pas, la demande PROD baisse d'environ 20 interventions par semaine et la réserve gagne 26 créneaux."),
]

CSS = open('build_pdf_cmp.py').read().split('CSS = """')[1].split('"""')[0]
CSS += """
.dist{font-size:6.6pt;table-layout:fixed;margin-top:4px}
.dist th{background:#eef2f4;color:#4d5d6a;font-size:6pt;padding:2px;border:1px solid #dfe4e7;font-weight:700}
.dist th.rot{height:62px;vertical-align:bottom;padding-bottom:4px}
.dist th.rot span{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;font-size:6pt}
.dist th.rowh{text-align:left;padding-left:3px;white-space:nowrap;color:#141c23;width:104px;font-size:5.7pt}
.dist td{text-align:center;padding:2.5px 0;border:1px solid #e8ebed;font-family:ui-monospace,monospace;font-size:6.2pt}
.dist td.d1{background:#eef8ee;color:#0a7d0a;font-weight:700}
.dist td.d2{background:#fdf6e3;color:#8a6410}
.dist td.d3{background:#fdf0f0;color:#b02f2f}
.dist td.self{background:#141c23}
ol.rules{margin:0;padding:0;list-style:none}
ol.rules li{display:grid;grid-template-columns:52px 1fr;gap:9px;padding:5px 0;border-bottom:1px solid #eceff1;
  page-break-inside:avoid}
ol.rules li .w{font-family:ui-monospace,monospace;font-size:7.2pt;font-weight:700;color:#2a78d6}
ol.rules li p{margin:0;font-size:8.4pt;color:#3d4c58}
ol.rules li p b{color:#141c23}
.q{page-break-inside:avoid;margin-bottom:9px}
.q .t{font-weight:700;font-size:9.6pt;margin-bottom:2px}
.q p{margin:0;font-size:8.8pt;color:#3d4c58}
"""


def build():
    cards = "".join([
        '<div class="card"><span class="k">Référence</span><span class="t">Base</span>'
        '<span class="s">SAV et production du lundi au samedi</span>'
        '<span class="v"><b>60</b> j-tech · <b>480</b> créneaux<br>réserve +44 · occupation 68 %</span>'
        '<span class="verdict">Tenable</span></div>',
        '<div class="card ok"><span class="k">Simulation A</span><span class="t">SAV lundi-vendredi</span>'
        '<span class="s">La production continue le samedi</span>'
        f'<span class="v"><b>60</b> j-tech · <b>{A["total"]}</b> créneaux<br>'
        f'réserve +{A["total"]-A["besoin"]} · occupation 71 %</span>'
        '<span class="verdict">Tenable</span></div>',
        '<div class="card no"><span class="k">Simulation B</span><span class="t">Semaine de 5 jours</span>'
        '<span class="s">Plus personne ne travaille le samedi</span>'
        f'<span class="v"><b>55</b> j-tech · <b>{B["total"]}</b> créneaux<br>'
        f'réserve {B["total"]-B["besoin"]} · occupation 78 %</span>'
        '<span class="verdict">Insuffisant de 14 créneaux</span></div>'])
    leg = ('<div class="legend">'
           '<span><i class="sw" style="background:#e4eefa;border:1px solid #b6cfe9"></i>demi-journée SAV</span>'
           '<span><i class="sw" style="background:#fceee6;border:1px solid #eec7ac"></i>demi-journée PROD</span>'
           '<span><i class="sw" style="background:#eff2f5;border:1px solid #cfd6dc"></i>demi-journée mixte</span>'
           '<span><i class="sw" style="background:#fdf0d8;border:1px solid #e5c98a"></i>technicien à 6 jours</span>'
           '</div>')
    regles = "".join(f'<li><span class="w">{w}</span><p>{t}</p></li>' for w, t in REGLES)
    quests = "".join(f'<div class="q"><div class="t">{q}</div><p>{a}</p></div>' for q, a in QUESTIONS)
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>Dossier de planification SAV / PROD — Loir-et-Cher</title><style>{CSS}</style></head><body>

<div class="meta">Département 41 · Loir-et-Cher &nbsp;·&nbsp; 12 secteurs GRDV · 59 NRO &nbsp;·&nbsp; 11 techniciens</div>
<h1>Planification SAV et production<br>du Loir-et-Cher</h1>
<p class="lede">Comment tenir un rendez-vous SAV à J+1 ou J+2 sur les douze secteurs, tout en plaçant la
production à J+5, J+6 ou J+7. Dossier complet : données, diagnostic, dimensionnement, trois scénarios
comparés et grilles hebdomadaires.</p>
<hr class="rule">
<div class="scen">{cards}</div>
<div class="box good"><div class="t">Recommandation</div>
<p>Le scénario de base et la simulation A tiennent tous deux. <b>La simulation A est préférable</b> : elle
retire le SAV du samedi — un gain social réel — sans dégrader la disponibilité, parce que la production
continue de tourner ce jour-là. La simulation B, semaine de cinq jours pour tous, reste réalisable mais
fait tomber la disponibilité sous l'objectif : il manque 14 créneaux.</p></div>

<div class="sec pb">
<h2><span class="num-sec">01</span>Les données de départ</h2>
<p>Deux sources, toutes deux limitées au département 41. Pour la production, le fichier de suivi des volumes :
je retiens le <b>mois le plus chargé secteur par secteur</b> entre octobre et mars, B2B inclus, majoré des
10 % de flexibilité demandés. Le fichier ne dimensionne que sur mars, or octobre est le mois haut sur le 41
(705 interventions contre 656) : retenir le maximum ajoute environ 7 % au besoin.</p>
<p>Pour le SAV, votre planning hebdomadaire : j'ai additionné les créneaux secteur par secteur, soit
<b>142 interventions par semaine</b>, ou 615 par mois.</p>
{demande_table()}
<div class="box"><div class="t">La demande totale : 327 interventions par semaine</div>
<p>185 en production majorée de 10 %, 142 en service après-vente. C'est le chiffre qui commande tout le reste.</p></div>
</div>

<div class="sec pb">
<h2><span class="num-sec">02</span>Diagnostic : pourquoi le délai n'est pas tenu aujourd'hui</h2>
<p>Le problème n'est pas le volume mais le calendrier. La grille actuelle concentre beaucoup de créneaux sur
peu de jours : <b>Cormenon n'est visité que le jeudi, Vouzon que le mercredi</b>. Un client de Cormenon qui
appelle le vendredi attend jusqu'au jeudi suivant, soit J+6.</p>
{C1['passages']}
</div>

<div class="sec">
<h2><span class="num-sec">03</span>La règle des rythmes de passage</h2>
<p>Un secteur doit être visité trois fois par semaine pour qu'un créneau existe toujours à J+1 ou J+2.
Deux passages ne suffisent jamais, quelle que soit la combinaison. Le nombre de rythmes possibles dépend
de la longueur de la semaine — et, contre l'intuition, la semaine de cinq jours en offre davantage tout
en étant plus contraignante.</p>
{C2['rythmes']}
<div class="box warn"><div class="t">Conséquence sur cinq jours : la Sologne Est passe de un à deux techniciens</div>
<p>Crouy-sur-Cosson et Vouzon sont distants de 38 km. Sur six jours ils tenaient sur un seul technicien —
Crouy en Lundi-Mercredi-Vendredi, Vouzon en Mardi-Jeudi-Samedi, jamais le même jour. Sur cinq jours, leurs
rythmes se croisent forcément, et 38 km est trop long pour enchaîner matin et après-midi. <b>Il faut deux
techniciens sur un secteur qui n'en réclamait qu'un</b> : c'est le coût caché de la suppression du samedi,
invisible dans le simple décompte des jours-technicien.</p></div>
</div>

<div class="sec">
<h2><span class="num-sec">04</span>Dimensionnement : pourquoi 436 créneaux</h2>
<p>Ouvrir exactement 327 créneaux pour 327 interventions reviendrait à travailler à 100 % d'occupation :
aucun client ne trouverait jamais de place. En n'occupant jamais plus de <b>75 %</b> des créneaux, il faut
en ouvrir 436. Le quart restant n'est pas du gaspillage — c'est précisément la disponibilité.</p>
{C1['capacite']}
<div class="box good"><div class="t">Et ce quart ne coûte presque rien</div>
<p>Parce que la bascule de la veille récupère les créneaux SAV non vendus pour y poser de la production
tirée du carnet J+5/J+7. Le seul coût réel est la réserve de sécurité.</p></div>
</div>

<div class="sec pb">
<h2><span class="num-sec">05</span>Les trois scénarios</h2>
{cmp_table()}
{C2['creneaux']}
{C2['occupation']}
</div>

<div class="sec">
<h2><span class="num-sec">06</span>Lecture des résultats</h2>
<div class="box good"><div class="t">Base et simulation A tiennent</div>
<p>Retirer le SAV du samedi ne coûte presque rien tant que la production continue ce jour-là : les cinq
techniciens à six jours consacrent leur samedi à de la production pure, ce qui libère du temps en semaine
pour le SAV. Les {A['total']} créneaux ouverts couvrent les 436 nécessaires avec
{A['total']-A['besoin']} de marge, et l'occupation reste à 71 %.</p></div>
<div class="box warn"><div class="t">La simulation B dégrade la disponibilité</div>
<p>Sans samedi du tout, l'équipe descend à 55 jours-technicien et n'ouvre que {B['total']} créneaux là où il
en faudrait 436. Les douze secteurs restent conformes et le J+1/J+2 est tenu partout, mais l'occupation
monte à <b>77,6 %</b> : il reste moins de créneaux libres, donc davantage de clients qui n'obtiendront pas
la date demandée.</p></div>
<div class="keep"><h3>Trois façons de combler les 14 créneaux manquants</h3>
<div class="trois">
  <div><span class="t">Accepter 78 % d'occupation</span><p>L'option gratuite : la planification fonctionne
  telle quelle, mais la marge de disponibilité passe de 25 % à 22 %.</p></div>
  <div><span class="t">Ajouter deux jours-technicien</span><p>Un mi-temps, ou deux techniciens passant
  ponctuellement à six jours. Cela apporte 16 créneaux, un peu plus que les 14 manquants.</p></div>
  <div><span class="t">Monter à 8,5 créneaux par jour</span><p>55 jours-technicien donneraient 468 créneaux.
  Le levier le plus incertain : votre planning actuel tourne à 5,68.</p></div>
</div></div>
</div>

<div class="landscape">
<h2><span class="num-sec">07</span>Grille — scénario de base, SAV du lundi au samedi</h2>
<p style="font-size:8.2pt">Deux rythmes disjoints, L-Me-V et Ma-J-S, portés par les cinq techniciens à six jours.
480 créneaux ouverts, 44 de réserve.</p>
{leg}{grid_base()}
</div>

<div class="landscape">
<h2><span class="num-sec">08</span>Grille — simulation A, SAV lundi-vendredi</h2>
<p style="font-size:8.2pt">Le samedi des cinq techniciens à six jours devient une journée de production pure.
{A['total']} créneaux ouverts, {A['total']-A['besoin']} de réserve.</p>
{leg}{grid_sim('A')}
</div>

<div class="landscape">
<h2><span class="num-sec">09</span>Grille — simulation B, semaine de cinq jours</h2>
<p style="font-size:8.2pt">Le samedi disparaît entièrement : 55 jours-technicien.
{B['total']} créneaux ouverts, soit 14 de moins que nécessaire.</p>
{leg}{grid_sim('B')}
</div>

<div class="sec pb">
<h2><span class="num-sec">10</span>Contrôle par secteur</h2>
<p>Trois conditions à vérifier partout : au moins trois passages SAV par semaine sur un rythme valide, une
réservation SAV au moins égale à la demande, et une capacité PROD au moins égale à la demande. Les douze
secteurs les remplissent dans les trois scénarios.</p>
<h3>Base — SAV du lundi au samedi</h3>{controle('base')}
<h3>Simulation A</h3>{controle('A')}
</div>

<div class="sec pb">
<h3>Simulation B</h3>{controle('B')}
<h2 style="margin-top:16px"><span class="num-sec">11</span>Le moteur de disponibilité</h2>
<p>Réserver un créneau au SAV ne le consomme pas. Tant qu'il n'est pas vendu, il redevient de la production
la veille au soir. C'est ce qui rend une réservation généreuse presque gratuite.</p>
<ol class="rules">{regles}</ol>
</div>

<div class="sec pb">
<h2><span class="num-sec">12</span>Cohérence des distances</h2>
<p>Distances routières estimées : vol d'oiseau majoré de 25 %, plus 8 km lorsque le trajet franchit la Loire
(ponts de Blois, Chaumont, Muides, Beaugency). À recaler avec votre outil de tournées.</p>
{dist_table()}
<div class="legend" style="margin-top:8px">
  <span><i class="sw" style="background:#eef8ee;border:1px solid #0ca30c"></i>≤ 30 km — enchaînement acceptable</span>
  <span><i class="sw" style="background:#fdf6e3;border:1px solid #fab219"></i>31 à 50 km — à éviter dans la même journée</span>
  <span><i class="sw" style="background:#fdf0f0;border:1px solid #d03b3b"></i>plus de 50 km — incohérent</span>
</div>
<div class="box"><div class="t">Deux corrections par rapport à la grille d'origine</div>
<p>Cormenon était rattaché à la Sologne Est, à 113 km de Vouzon dans le même secteur, avec un jeudi enchaînant
Épiais le matin et Cormenon l'après-midi — 46 km entre les deux vacations. Cormenon repart au Nord, dans le
Vendômois-Perche, et <b>aucun enchaînement ne dépasse 30 km dans les trois scénarios</b>.</p></div>
</div>

<div class="sec pb">
<h2><span class="num-sec">13</span>Points à valider</h2>
{quests}
</div>

<footer>
Volumes de production : suivi_volumes_PROD_72.xlsx, mise à jour du 28 juillet 2026 — onglets « Suivi des volumes
PROD » et « Volume par NRO », 12 secteurs GRDV et 59 NRO sur le seul département 41. Étanchéité vérifiée dans
les deux sens : aucun NRO du 41 rattaché à un secteur extérieur, aucun secteur extérieur contenant un NRO du 41.
Volume SAV : Planning_HEBDO_SAV_Departement_41.xlsx, 142 interventions par semaine relevées secteur par secteur.
Les trois grilles sont produites et vérifiées par le même contrôleur : délai J+1/J+2, couverture SAV, couverture
PROD, capacité journalière et distances. Distances routières estimées, à confirmer.
</footer>
</body></html>"""


if __name__ == "__main__":
    open('dossier41.html', 'w').write(build())
    print("dossier41.html écrit")
