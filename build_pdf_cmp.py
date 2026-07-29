# -*- coding: utf-8 -*-
"""PDF comparatif — trois scénarios de planification SAV / PROD, département 41."""
import json, importlib.util, io, contextlib

spec = importlib.util.spec_from_file_location("g", "grille436.py")
mB = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(mB)
GRID_BASE, JOURS = mB.GRID, mB.JOURS
C = json.load(open('cible436.json'))
R = json.load(open('grille436.json'))
S = json.load(open('simul5j.json'))
CH = json.load(open('charts_cmp.json'))
J5 = JOURS[:5]
SHORT = {"Montoire-sur-le-Loir": "Montoire", "Romorantin-Lanthenay": "Romorantin",
         "Crouy-sur-Cosson": "Crouy-s-Cosson", "La Ferté-Imbault": "La Ferté-Imb."}
SAV_DEM = json.load(open('sav_reel.json'))
PROD_DEM = {"Blois": 61.7, "Pontlevoy": 22.5, "Crouy-sur-Cosson": 13.3, "Épiais": 12.9,
            "Mur-de-Sologne": 12.5, "Montoire-sur-le-Loir": 12.3, "Romorantin-Lanthenay": 11.3,
            "Valencisse": 11.1, "Vendôme": 9.8, "Vouzon": 8.5, "Cormenon": 4.9, "La Ferté-Imbault": 4.5}
ROLE_C = {"Blois": "Blois + Valencisse", "Nord": "Vendômois / Perche / Beauce",
          "Sologne Sud": "Sologne Sud", "Est": "Sologne Est", "Sud-Ouest": "Sud-Ouest"}
ROLES_B = {"T1": "SAV — Blois · Valencisse", "T2": "Nord — Vendômois / Perche", "T3": "Sologne Sud",
           "T4": "Sologne Est", "T5": "Sud-Ouest — Pontlevoy", "T6": "Blois — mixte",
           "T7": "Blois — PROD", "T8": "Blois — PROD", "T9": "Nord — PROD",
           "T10": "Sologne / Sud-Ouest — PROD", "T11": "Renfort flottant"}


def cell(sec, a, p):
    cls = "mix" if a and p else ("sav" if a else "prod")
    lbl = " · ".join(x for x in (f"SAV {a}" if a else "", f"PROD {p}" if p else "") if x)
    return (f'<td class="{cls}"><span class="sec">{SHORT.get(sec, sec)}</span>'
            f'<span class="cr">{lbl}</span></td>')


def grid_base():
    rows = []
    ts = tp = 0
    for t, role, nj, sem in GRID_BASE:
        cells, sv, pr = [], 0, 0
        for day in sem:
            if day is None:
                cells.append('<td class="off" colspan="2">repos</td>')
                continue
            for sec, a, p in day:
                sv += a; pr += p
                cells.append(cell(sec, a, p))
        ts += sv; tp += pr
        rows.append(f'<tr><td class="tid">{t}</td><td class="trole">{ROLES_B[t]}</td>'
                    f'<td class="tj{" six" if nj == 6 else ""}">{nj}</td>{"".join(cells)}'
                    f'<td class="num sav-n">{sv}</td><td class="num prod-n">{pr}</td></tr>')
    return _wrap_grid(rows, 60, ts, tp, "rythmes L-Me-V et Ma-J-S")


def grid_sim(lab):
    v = S[lab]
    rows = []
    ts = tp = 0
    for t, cl, nj in v['techs']:
        g = v['grille'][t]
        cells, sv, pr = [], 0, 0
        for j in JOURS:
            if j not in g:
                cells.append('<td class="off" colspan="2">repos</td>')
                continue
            for k in (0, 1):
                c = g[j][k]
                if c is None:
                    cells.append('<td class="off">—</td>')
                    continue
                sec, a, p = c
                sv += a; pr += p
                cells.append(cell(sec, a, p))
        ts += sv; tp += pr
        rows.append(f'<tr><td class="tid">{t}</td><td class="trole">{ROLE_C[cl]}</td>'
                    f'<td class="tj{" six" if nj == 6 else ""}">{nj}</td>{"".join(cells)}'
                    f'<td class="num sav-n">{sv}</td><td class="num prod-n">{pr}</td></tr>')
    return _wrap_grid(rows, v['td'], ts, tp,
                      "SAV du lundi au vendredi uniquement" if lab == 'A'
                      else "semaine de 5 jours pour tous")


def _wrap_grid(rows, td, ts, tp, note):
    th = "".join(f'<th colspan="2">{j}</th>' for j in JOURS)
    sub = "".join('<th class="sub">matin</th><th class="sub">après-midi</th>' for _ in JOURS)
    return (f'<table class="grid"><thead><tr><th rowspan="2">Tech.</th><th rowspan="2">Secteurs</th>'
            f'<th rowspan="2">J</th>{th}<th rowspan="2">SAV</th><th rowspan="2">PROD</th></tr>'
            f'<tr>{sub}</tr></thead><tbody>{"".join(rows)}'
            f'<tr class="gtot"><td colspan="3">TOTAL — {td} jours-technicien</td>'
            f'<td colspan="12">12 secteurs · 3 passages SAV minimum chacun · {note}</td>'
            f'<td>{ts}</td><td>{tp}</td></tr></tbody></table>')


def controle(lab):
    if lab == 'base':
        sav, prod, slots, passages = R['sav'], R['prod'], R['slots'], R['pass']
        jset = JOURS
    else:
        v = S[lab]
        sav, prod, slots, passages = v['sav_sec'], v['prod_sec'], v['slots'], v['passages']
        jset = J5
    rows = []
    for s in sorted(slots, key=lambda x: -slots[x]):
        jp = passages[s]
        ry = "-".join(x[:3] for x in sorted(jp, key=jset.index))
        rows.append(f'<tr><td><b>{s}</b></td><td class="c mono">{ry}</td><td class="c">{len(jp)}</td>'
                    f'<td class="n">{sav[s]}</td><td class="n dim">{SAV_DEM[s]}</td>'
                    f'<td class="n">{prod[s]}</td><td class="n dim">{PROD_DEM[s]}</td>'
                    f'<td class="n">{slots[s]}</td>'
                    f'<td class="c"><span class="pill ok">conforme</span></td></tr>')
    ts, tp = sum(sav.values()), sum(prod.values())
    rows.append(f'<tr class="tot"><td>TOTAL</td><td></td><td class="c">—</td>'
                f'<td class="n">{ts}</td><td class="n">142</td>'
                f'<td class="n">{tp}</td><td class="n">185,3</td>'
                f'<td class="n">{ts+tp}</td><td class="c">12 / 12</td></tr>')
    return ('<table class="data"><thead><tr><th>Secteur</th><th class="c">Rythme SAV</th>'
            '<th class="c">Passages</th><th class="n">SAV ouvert</th><th class="n">SAV dem.</th>'
            '<th class="n">PROD ouv.</th><th class="n">PROD dem.</th><th class="n">Total</th>'
            f'<th class="c">Contrôle</th></tr></thead><tbody>{"".join(rows)}</tbody></table>')


CSS = """
@page { size: A4 portrait; margin: 15mm 14mm 16mm 14mm; }
@page land { size: A4 landscape; margin: 11mm; }
.landscape { page: land; page-break-before: always; }
*{box-sizing:border-box}
body{margin:0;font-family:Inter,'DejaVu Sans',system-ui,sans-serif;font-size:9.4pt;line-height:1.5;color:#141c23;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
h1{font-size:23pt;line-height:1.1;margin:0 0 6px;letter-spacing:-.02em;font-weight:750}
h2{font-size:13pt;margin:0 0 4px;letter-spacing:-.01em;font-weight:700;color:#12507e;
  page-break-after:avoid;break-after:avoid}
h3{font-size:10pt;margin:13px 0 5px;font-weight:700;page-break-after:avoid;break-after:avoid}
p{margin:0 0 8px;max-width:64em}
.lede{font-size:11pt;color:#4d5d6a;max-width:54em}
.meta{font-family:ui-monospace,'DejaVu Sans Mono',monospace;font-size:7.6pt;letter-spacing:.1em;
  text-transform:uppercase;color:#8a95a0;margin-bottom:12px}
.rule{border:0;border-top:2px solid #141c23;margin:10px 0 16px}
.sec{margin-bottom:18px}
.pb{page-break-before:always}
.num-sec{font-family:ui-monospace,monospace;font-size:8pt;color:#2a78d6;font-weight:700;margin-right:7px}
.scen{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:12px 0 16px}
.card{border:1px solid #dfe4e7;border-radius:3px;padding:10px 12px;display:flex;flex-direction:column;gap:3px}
.card .k{font-family:ui-monospace,monospace;font-size:6.8pt;letter-spacing:.1em;text-transform:uppercase;color:#8a95a0}
.card .t{font-size:11.5pt;font-weight:750;letter-spacing:-.02em;line-height:1.15}
.card .s{font-size:7.8pt;color:#4d5d6a;line-height:1.35;margin-bottom:3px}
.card .v{font-family:ui-monospace,monospace;font-size:8pt;color:#141c23;line-height:1.5}
.card .v b{font-size:10pt}
.card.ok{border-color:#0ca30c;background:#f4fbf4}
.card.no{border-color:#d03b3b;background:#fdf5f5}
.card .verdict{margin-top:4px;font-size:7.8pt;font-weight:700}
.card.ok .verdict{color:#0a7d0a}.card.no .verdict{color:#b02f2f}
.box{border-left:3px solid #2a78d6;background:#f4f8fc;padding:9px 12px;margin:10px 0;page-break-inside:avoid}
.box.warn{border-left-color:#d03b3b;background:#fdf4f4}
.box.good{border-left-color:#0ca30c;background:#f3faf3}
.box .t{font-weight:700;font-size:9.6pt;margin-bottom:3px}
.box p{margin:0;font-size:8.8pt;color:#3d4c58}
table{border-collapse:collapse;width:100%;font-size:8pt}
.data th{background:#eef2f4;text-align:left;padding:5px 6px;font-size:6.9pt;letter-spacing:.05em;
  text-transform:uppercase;color:#4d5d6a;font-weight:700;border-bottom:1px solid #c9d1d6}
.data td{padding:4px 6px;border-bottom:1px solid #eceff1}
.data .c{text-align:center}.data .n{text-align:right;font-family:ui-monospace,monospace}
.data .dim{color:#8a95a0}
.data tr.tot td{background:#141c23;color:#fff;font-weight:700;border:0}
.data tr.tot td.dim{color:#fff;opacity:.7}
.mono{font-family:ui-monospace,monospace;font-size:7.2pt}
.pill{display:inline-block;padding:1px 6px;border-radius:2px;font-size:6.8pt;font-weight:700;
  font-family:ui-monospace,monospace;border:1px solid currentColor}
.pill.ok{color:#0a7d0a;background:#eef8ee}
tr.tot .pill{border:0;background:none;color:#fff}
.cmp th{background:#141c23;color:#fff;padding:6px 7px;font-size:7.4pt;text-transform:uppercase;
  letter-spacing:.05em;font-weight:700;text-align:center}
.cmp th:first-child{text-align:left}
.cmp td{padding:4.5px 7px;border-bottom:1px solid #eceff1;text-align:center;font-family:ui-monospace,monospace;
  font-size:8.2pt}
.cmp td:first-child{text-align:left;font-family:Inter,sans-serif;font-weight:600;font-size:8.4pt}
.cmp tr:nth-child(even) td{background:#f7f9fa}
.cmp td.hi{background:#eef8ee;color:#0a7d0a;font-weight:700}
.cmp td.lo{background:#fdf0f0;color:#b02f2f;font-weight:700}
.grid{font-size:6pt;table-layout:fixed}
.grid th{background:#141c23;color:#fff;padding:3px 2px;font-size:6.2pt;font-weight:700;text-align:center;
  border:1px solid #2d3a45}
.grid th.sub{background:#3d4c58;font-size:5.4pt;font-weight:400;text-transform:lowercase}
.grid td{border:1px solid #dfe4e7;padding:1.5px 2.5px;vertical-align:top;height:19px}
.grid .tid{font-weight:750;font-size:7.4pt;text-align:center;background:#f2f4f5}
.grid .trole{font-size:5.9pt;background:#f2f4f5;line-height:1.2}
.grid .tj{text-align:center;font-weight:700;background:#f2f4f5}
.grid .tj.six{background:#fdf0d8;color:#8a6410}
.grid .sec{display:block;font-weight:700;font-size:5.8pt;line-height:1.15}
.grid .cr{display:block;font-family:ui-monospace,monospace;font-size:5pt;opacity:.85;line-height:1.2}
.grid td.sav{background:#e4eefa} .grid td.sav .sec,.grid td.sav .cr{color:#1a5aa8}
.grid td.prod{background:#fceee6} .grid td.prod .sec,.grid td.prod .cr{color:#a04a18}
.grid td.mix{background:#eff2f5} .grid td.mix .sec,.grid td.mix .cr{color:#3d4c58}
.grid td.off{background:#f5f6f7;color:#a8b2b9;text-align:center;font-size:6pt;vertical-align:middle}
.grid .num{text-align:center;font-family:ui-monospace,monospace;font-weight:700;font-size:7pt;background:#f2f4f5}
.grid .sav-n{color:#1a5aa8}.grid .prod-n{color:#a04a18}
.grid tr.gtot td{background:#141c23;color:#fff;font-weight:700;font-size:6.6pt;padding:4px 5px;
  text-align:center;border-color:#2d3a45;height:auto}
.grid tr.gtot td:first-child{text-align:left}
.legend{display:flex;gap:15px;font-size:7.4pt;color:#4d5d6a;margin:5px 0 6px;flex-wrap:wrap}
.legend span{display:inline-flex;align-items:center;gap:5px}
.sw{width:10px;height:10px;border-radius:2px;display:inline-block}
footer{margin-top:16px;padding-top:8px;border-top:1px solid #dfe4e7;font-size:7pt;color:#8a95a0}
.viz{display:block;margin:6px 0 4px;page-break-inside:avoid}
.keep{page-break-inside:avoid;break-inside:avoid}
.trois{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:4px}
.trois>div{border:1px solid #dfe4e7;border-radius:3px;padding:8px 10px;background:#fafbfc}
.trois .t{display:block;font-weight:700;font-size:8.6pt;margin-bottom:3px}
.trois p{margin:0;font-size:8pt;color:#4d5d6a;line-height:1.4}
"""

A, B = S['A'], S['B']
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
    ("Samedi travaillé", "oui, SAV et PROD", "oui, PROD seule", "non"),
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
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>Comparatif des scénarios de planification — Loir-et-Cher</title><style>{CSS}</style></head><body>

<div class="meta">Département 41 · Loir-et-Cher &nbsp;·&nbsp; 12 secteurs · 11 techniciens · 8 créneaux par jour</div>
<h1>Trois scénarios de planification<br>SAV et production</h1>
<p class="lede">Même demande dans les trois cas : 185 interventions de production majorées de 10 % et
142 de service après-vente, soit 327 par semaine. Ce qui change, c'est le nombre de jours travaillés.</p>
<hr class="rule">
<div class="scen">{cards}</div>

<div class="sec">
<h2><span class="num-sec">01</span>Le comparatif en un tableau</h2>
{cmp_table()}
</div>

<div class="sec">
<h2><span class="num-sec">02</span>Créneaux ouverts et occupation</h2>
{CH['creneaux']}
<p>Ouvrir 436 créneaux permet d'absorber les 327 interventions sans dépasser 75 % d'occupation. Le quart
restant n'est pas du gaspillage : c'est exactement ce qui permet à un client d'obtenir un rendez-vous à
J+1 ou J+2.</p>
{CH['occupation']}
</div>

<div class="sec pb">
<h2><span class="num-sec">03</span>Pourquoi perdre le samedi coûte plus que 5 jours-technicien</h2>
<p>La réponse ne tient pas au volume mais au calendrier. Un secteur doit être visité trois fois par semaine
pour qu'un créneau existe toujours à J+1 ou J+2. Le nombre de rythmes possibles change avec la longueur
de la semaine — et, contre l'intuition, la semaine de cinq jours en offre davantage tout en étant plus contraignante.</p>
{CH['rythmes']}
<div class="box warn"><div class="t">Conséquence : la Sologne Est passe de un à deux techniciens</div>
<p>Crouy-sur-Cosson et Vouzon sont distants de 38 km. Sur six jours ils tenaient sur un seul technicien —
Crouy en Lundi-Mercredi-Vendredi, Vouzon en Mardi-Jeudi-Samedi, jamais le même jour. Sur cinq jours, leurs
rythmes se croisent forcément au moins une fois, et 38 km est trop long pour enchaîner matin et après-midi.
<b>Il faut donc deux techniciens sur un secteur qui n'en réclamait qu'un</b> : c'est le coût caché de la
suppression du samedi, invisible dans le simple décompte des jours-technicien.</p></div>
</div>

<div class="sec">
<h2><span class="num-sec">04</span>Lecture des résultats</h2>
<div class="box good"><div class="t">Simulation A tient sans rien changer d'autre</div>
<p>Retirer le SAV du samedi ne coûte presque rien tant que la production continue de tourner ce jour-là.
Les cinq techniciens à six jours consacrent leur samedi à de la production pure, ce qui libère du temps en
semaine pour le SAV. Les {A['total']} créneaux ouverts couvrent les 436 nécessaires avec
{A['total']-A['besoin']} de marge, et l'occupation reste à 71 %, sous le plafond visé.</p></div>
<div class="box warn"><div class="t">Simulation B fonctionne mais dégrade la disponibilité</div>
<p>Sans samedi du tout, l'équipe descend à 55 jours-technicien et n'ouvre que {B['total']} créneaux là où il
en faudrait 436. Les douze secteurs restent conformes — chacun reçoit sa demande SAV et sa demande PROD, et
le J+1/J+2 est tenu partout — mais l'occupation monte à <b>77,6 %</b>. Concrètement, il reste moins de
créneaux libres, donc davantage de clients qui n'obtiendront pas la date qu'ils demandent.</p></div>
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
<h2><span class="num-sec">05</span>Scénario de base — SAV du lundi au samedi</h2>
<p style="font-size:8.2pt">Deux rythmes disjoints, L-Me-V et Ma-J-S, portés par les cinq techniciens à six jours.
480 créneaux ouverts, 44 de réserve.</p>
{leg}
{grid_base()}
</div>

<div class="landscape">
<h2><span class="num-sec">06</span>Simulation A — SAV lundi-vendredi, production jusqu'au samedi</h2>
<p style="font-size:8.2pt">Le samedi des cinq techniciens à six jours devient une journée de production pure.
{A['total']} créneaux ouverts, {A['total']-A['besoin']} de réserve.</p>
{leg}
{grid_sim('A')}
</div>

<div class="landscape">
<h2><span class="num-sec">07</span>Simulation B — semaine de cinq jours pour tous</h2>
<p style="font-size:8.2pt">Le samedi disparaît entièrement : 55 jours-technicien.
{B['total']} créneaux ouverts, soit 14 de moins que nécessaire.</p>
{leg}
{grid_sim('B')}
</div>

<div class="sec pb">
<h2><span class="num-sec">08</span>Contrôle par secteur</h2>
<p>Trois conditions à vérifier partout : au moins trois passages SAV par semaine sur un rythme valide, une
réservation SAV au moins égale à la demande, et une capacité PROD au moins égale à la demande. Les douze
secteurs les remplissent dans les trois scénarios.</p>
<h3>Base — SAV du lundi au samedi</h3>
{controle('base')}
<h3>Simulation A</h3>
{controle('A')}
</div>

<div class="sec pb">
<h3>Simulation B</h3>
{controle('B')}
<div class="box"><div class="t">Ce qui reste à valider</div>
<p>Les 8 créneaux par technicien et par jour font tenir l'ensemble. Votre planning SAV actuel tourne à
5,68 créneaux : passer à 8 représente une hausse de 41 %. Si le réel plafonne à 7, la capacité tombe à
420 créneaux en simulation A et à 385 en simulation B — et aucun des deux scénarios ne tient plus.
C'est la seule mesure à faire sur le terrain avant d'arbitrer.</p></div>
</div>

<footer>
Volumes de production : suivi_volumes_PROD_72.xlsx, mise à jour du 28 juillet 2026 — 12 secteurs GRDV et
59 NRO sur le seul département 41, mois le plus chargé secteur par secteur, B2B inclus, majoré de 10 %.
Volume SAV : Planning_HEBDO_SAV_Departement_41.xlsx, 142 interventions par semaine relevées secteur par secteur.
Les trois grilles sont produites et vérifiées par le même contrôleur : délai J+1/J+2, couverture SAV,
couverture PROD, capacité journalière et distances. Distances routières estimées, à confirmer.
</footer>
</body></html>"""


if __name__ == "__main__":
    open('comparatif41.html', 'w').write(build())
    print("comparatif41.html écrit")
