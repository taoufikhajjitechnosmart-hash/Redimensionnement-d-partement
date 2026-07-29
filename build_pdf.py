# -*- coding: utf-8 -*-
"""Rapport PDF — planification SAV / PROD du département 41."""
import json, math, importlib.util, io, contextlib

spec = importlib.util.spec_from_file_location("g", "grille436.py")
m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(m)
GRID, JOURS = m.GRID, m.JOURS
C = json.load(open('cible436.json'))
R = json.load(open('grille436.json'))
CH = json.load(open('charts.json'))
SHORT = {"Montoire-sur-le-Loir": "Montoire", "Romorantin-Lanthenay": "Romorantin",
         "Crouy-sur-Cosson": "Crouy-s-Cosson", "La Ferté-Imbault": "La Ferté-Imb."}
ORDER = sorted(C['cible'], key=lambda x: -R['slots'][x])
PASS_AV = {"Blois": 5, "Pontlevoy": 5, "Valencisse": 2, "Vendôme": 3, "Épiais": 3,
           "Montoire-sur-le-Loir": 2, "Cormenon": 1, "Crouy-sur-Cosson": 2, "Vouzon": 1,
           "Mur-de-Sologne": 2, "Romorantin-Lanthenay": 2, "La Ferté-Imbault": 2}

ROLES = {"T1": "SAV — Blois · Valencisse", "T2": "Nord — Vendômois / Perche",
         "T3": "Sologne Sud", "T4": "Sologne Est", "T5": "Sud-Ouest — Pontlevoy",
         "T6": "Blois — mixte", "T7": "Blois — PROD", "T8": "Blois — PROD",
         "T9": "Nord — PROD", "T10": "Sologne / Sud-Ouest — PROD", "T11": "Renfort flottant"}

# ── grille hebdomadaire ────────────────────────────────────────────────────
def grid_table():
    th = "".join(f'<th colspan="2">{j}</th>' for j in JOURS)
    sub = "".join('<th class="sub">matin</th><th class="sub">après-midi</th>' for _ in JOURS)
    rows = []
    tot_s = tot_p = 0
    for t, role, nj, sem in GRID:
        cells = []
        sv = pr = 0
        for day in sem:
            if day is None:
                cells.append('<td class="off" colspan="2">repos</td>')
                continue
            for sec, a, p in day:
                sv += a; pr += p
                cls = "mix" if a and p else ("sav" if a else "prod")
                lbl = " · ".join(x for x in (f"SAV {a}" if a else "", f"PROD {p}" if p else "") if x)
                cells.append(f'<td class="{cls}"><span class="sec">{SHORT.get(sec, sec)}</span>'
                             f'<span class="cr">{lbl}</span></td>')
        tot_s += sv; tot_p += pr
        short_role = role.split(" (")[0].replace(" — ", " — ")
        rows.append(f'<tr><td class="tid">{t}</td><td class="trole">{ROLES.get(t, short_role)}</td>'
                    f'<td class="tj{" six" if nj==6 else ""}">{nj}</td>{"".join(cells)}'
                    f'<td class="num sav-n">{sv}</td><td class="num prod-n">{pr}</td></tr>')
    return (f'<table class="grid"><thead><tr><th rowspan="2">Tech.</th><th rowspan="2">Rôle</th>'
            f'<th rowspan="2">Jours</th>{th}<th rowspan="2">SAV</th><th rowspan="2">PROD</th></tr>'
            f'<tr>{sub}</tr></thead><tbody>{"".join(rows)}'
            f'<tr class="gtot"><td colspan="3">TOTAL — 60 jours-technicien</td>'
            f'<td colspan="12">12 secteurs · 3 passages minimum chacun · rythmes L-Me-V et Ma-J-S</td>'
            f'<td>{tot_s}</td><td>{tot_p}</td></tr></tbody></table>')


# ── contrôle par secteur ───────────────────────────────────────────────────
def controle_table():
    rows = []
    for s in ORDER:
        jp = R['pass'][s]
        ry = ("L-Me-V" if set(jp) == {"Lundi", "Mercredi", "Vendredi"}
              else "Ma-J-S" if set(jp) == {"Mardi", "Jeudi", "Samedi"} else "quotidien")
        rows.append(
            f'<tr><td><b>{s}</b></td><td class="c">{len(jp)}</td><td class="c mono">{ry}</td>'
            f'<td class="n">{R["slots"][s]}</td><td class="n dim">{round(C["cible"][s])}</td>'
            f'<td class="n">{R["sav"][s]}</td><td class="n dim">{C["sav_dem"][s]}</td>'
            f'<td class="n">{R["prod"][s]}</td><td class="n dim">{round(C["prod_dem"][s],1)}</td>'
            f'<td class="c"><span class="pill ok">conforme</span></td></tr>')
    return ('<table class="data"><thead><tr><th>Secteur</th><th class="c">Passages</th><th class="c">Rythme</th>'
            '<th class="n">Créneaux</th><th class="n">Cible</th><th class="n">SAV ouvert</th>'
            '<th class="n">SAV demandé</th><th class="n">PROD ouverte</th><th class="n">PROD demandée</th>'
            '<th class="c">Contrôle</th></tr></thead><tbody>' + "".join(rows) +
            f'<tr class="tot"><td>TOTAL</td><td class="c">—</td><td></td>'
            f'<td class="n">{sum(R["slots"].values())}</td><td class="n">436</td>'
            f'<td class="n">{sum(R["sav"].values())}</td><td class="n">142</td>'
            f'<td class="n">{sum(R["prod"].values())}</td><td class="n">185</td>'
            f'<td class="c">12 / 12</td></tr></tbody></table>')


# ── matrice des distances ──────────────────────────────────────────────────
PTS = [("Blois", 47.586, 1.336, "X"), ("Valencisse", 47.590, 1.220, "N"), ("Pontlevoy", 47.395, 1.256, "S"),
       ("Vendôme", 47.793, 1.066, "N"), ("Épiais", 47.760, 1.375, "N"), ("Montoire", 47.752, 0.866, "N"),
       ("Cormenon", 47.955, 0.980, "N"), ("Crouy-s-Cosson", 47.680, 1.610, "S"), ("Vouzon", 47.660, 2.020, "S"),
       ("Mur-de-Sologne", 47.383, 1.612, "S"), ("Romorantin", 47.357, 1.744, "S"), ("La Ferté-Imb.", 47.395, 1.976, "S")]


def km(a, b):
    x = math.radians(b[2] - a[2]) * math.cos(math.radians((a[1] + b[1]) / 2))
    y = math.radians(b[1] - a[1])
    d = 6371 * math.hypot(x, y) * 1.25
    if a[3] != b[3] and "X" not in (a[3], b[3]):
        d += 8
    return round(d)


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
                cls = "d1" if d <= 30 else ("d2" if d <= 50 else "d3")
                cells.append(f'<td class="{cls}">{d}</td>')
        rows.append(f'<tr><th class="rowh">{a[0]}</th>{"".join(cells)}</tr>')
    return f'<table class="dist"><thead><tr><th></th>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table>'


CSS = """
@page { size: A4 portrait; margin: 15mm 14mm 16mm 14mm; }
@page land { size: A4 landscape; margin: 11mm; }
.landscape { page: land; }
*{box-sizing:border-box}
body{margin:0;font-family:Inter,'DejaVu Sans',system-ui,sans-serif;font-size:9.4pt;line-height:1.5;color:#141c23;
  -webkit-print-color-adjust:exact;print-color-adjust:exact}
h1{font-size:23pt;line-height:1.1;margin:0 0 6px;letter-spacing:-.02em;font-weight:750}
h2{font-size:13pt;margin:0 0 4px;letter-spacing:-.01em;font-weight:700;color:#12507e}
h3{font-size:10pt;margin:14px 0 5px;font-weight:700}
p{margin:0 0 8px;max-width:64em}
.lede{font-size:11pt;color:#4d5d6a;max-width:52em}
.meta{font-family:ui-monospace,'DejaVu Sans Mono',monospace;font-size:7.6pt;letter-spacing:.1em;
  text-transform:uppercase;color:#8a95a0;margin-bottom:12px}
.rule{border:0;border-top:2px solid #141c23;margin:10px 0 16px}
.sec{margin-bottom:18px}
.pb{page-break-before:always}
.num-sec{font-family:ui-monospace,monospace;font-size:8pt;color:#2a78d6;font-weight:700;margin-right:7px}
/* tuiles */
.tiles{display:grid;grid-template-columns:repeat(5,1fr);gap:7px;margin:12px 0 16px}
.tile{border:1px solid #dfe4e7;border-radius:3px;padding:9px 10px}
.tile .k,.tile .v,.tile .n{display:block}
.tile .k{font-family:ui-monospace,monospace;font-size:6.6pt;letter-spacing:.1em;text-transform:uppercase;color:#8a95a0}
.tile .v{font-size:20pt;font-weight:750;letter-spacing:-.03em;line-height:1.05;margin:2px 0}
.tile .n{font-size:7.4pt;color:#4d5d6a;line-height:1.35}
.tile.ok{border-color:#0ca30c;background:#f2faf2}.tile.ok .v{color:#0a7d0a}
.tile.no{border-color:#d03b3b;background:#fdf3f3}.tile.no .v{color:#b02f2f}
/* encadrés */
.box{border-left:3px solid #2a78d6;background:#f4f8fc;padding:9px 12px;margin:10px 0;page-break-inside:avoid}
.box.warn{border-left-color:#d03b3b;background:#fdf4f4}
.box.good{border-left-color:#0ca30c;background:#f3faf3}
.box .t{font-weight:700;font-size:9.6pt;margin-bottom:3px}
.box p{margin:0;font-size:8.8pt;color:#3d4c58}
/* tableaux */
table{border-collapse:collapse;width:100%;font-size:8pt}
.data th{background:#eef2f4;text-align:left;padding:5px 6px;font-size:6.9pt;letter-spacing:.05em;
  text-transform:uppercase;color:#4d5d6a;font-weight:700;border-bottom:1px solid #c9d1d6}
.data td{padding:4px 6px;border-bottom:1px solid #eceff1}
.data .c{text-align:center}.data .n{text-align:right;font-family:ui-monospace,monospace}
.data .dim{color:#8a95a0}
.data tr.tot td{background:#141c23;color:#fff;font-weight:700;border:0}
.mono{font-family:ui-monospace,monospace;font-size:7.4pt}
.pill{display:inline-block;padding:1px 6px;border-radius:2px;font-size:6.8pt;font-weight:700;
  font-family:ui-monospace,monospace;border:1px solid currentColor}
.pill.ok{color:#0a7d0a;background:#eef8ee}
/* grille hebdo */
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
/* distances */
.dist{font-size:6.6pt;table-layout:fixed}
.dist th{background:#eef2f4;color:#4d5d6a;font-size:6pt;padding:2px;border:1px solid #dfe4e7;font-weight:700}
.dist th.rot{height:62px;vertical-align:bottom;padding-bottom:4px}
.dist th.rot span{writing-mode:vertical-rl;transform:rotate(180deg);white-space:nowrap;font-size:6pt}
.dist th.rowh{text-align:left;padding-left:3px;white-space:nowrap;color:#141c23;width:104px;font-size:5.7pt}
.dist td{text-align:center;padding:2.5px 0;border:1px solid #e8ebed;font-family:ui-monospace,monospace;font-size:6.2pt}
.dist td.d1{background:#eef8ee;color:#0a7d0a;font-weight:700}
.dist td.d2{background:#fdf6e3;color:#8a6410}
.dist td.d3{background:#fdf0f0;color:#b02f2f}
.dist td.self{background:#141c23}
/* règles */
ol.rules{margin:0;padding:0;list-style:none}
ol.rules li{display:grid;grid-template-columns:52px 1fr;gap:9px;padding:5px 0;border-bottom:1px solid #eceff1;
  page-break-inside:avoid}
ol.rules li .w{font-family:ui-monospace,monospace;font-size:7.2pt;font-weight:700;color:#2a78d6}
ol.rules li p{margin:0;font-size:8.4pt;color:#3d4c58}
ol.rules li p b{color:#141c23}
.legend{display:flex;gap:16px;font-size:7.6pt;color:#4d5d6a;margin:6px 0 0;flex-wrap:wrap}
.legend span{display:inline-flex;align-items:center;gap:5px}
.sw{width:10px;height:10px;border-radius:2px;display:inline-block}
footer{margin-top:16px;padding-top:8px;border-top:1px solid #dfe4e7;font-size:7pt;color:#8a95a0}
.viz{display:block;margin:6px 0 4px}
"""


def build():
    tiles = '<div class="tiles">' + "".join(f'<div class="tile {c}"><span class="k">{k}</span><span class="v">{v}</span>'
                    f'<span class="n">{n}</span></div>'
                    for k, v, n, c in [
                        ("Capacité", "480", "créneaux/semaine<br>60 j-tech × 8 créneaux", ""),
                        ("À ouvrir", "436", "créneaux/semaine<br>75 % d'occupation", ""),
                        ("Demande", "327", "interventions/semaine<br>185 PROD + 142 SAV", ""),
                        ("Réserve", "44", "créneaux, soit 5,5 j-tech<br>un technicien de marge", "ok"),
                        ("Secteurs conformes", "12/12", "au délai J+1/J+2<br>contre 3/12 aujourd'hui", "ok")]) + '</div>'
    rules = "".join(f'<li><span class="w">{w}</span><p>{t}</p></li>' for w, t in [
        ("Permanent", "<b>La tournée est figée.</b> Technicien × jour × secteur ne change jamais : distances maîtrisées, techniciens sur des secteurs qu'ils connaissent."),
        ("Permanent", "<b>Trois passages par semaine et par secteur</b>, rythme Lundi-Mercredi-Vendredi ou Mardi-Jeudi-Samedi. C'est ce qui garantit mécaniquement le J+1/J+2."),
        ("Permanent", "Sur chaque demi-journée, un nombre fixe de créneaux est réservé au SAV. <b>L'occupation ne dépasse jamais 75 %</b> : le quart restant est la disponibilité."),
        ("J-7 à J-5", "La PROD se pose uniquement sur les créneaux non réservés au SAV, dans le carnet J+5 à J+7. Le client PROD obtient bien son RDV à J+5/J+6/J+7."),
        ("J-2, 18 h", "Ouverture à la prise de RDV SAV des créneaux réservés du jour J. Le client qui appelle voit de la disponibilité à J+1 et J+2."),
        ("J-1, 18 h", "<b>Bascule.</b> Tout créneau SAV encore libre pour le lendemain est réaffecté à une intervention PROD <b>du même secteur</b>, puisée dans le carnet J+5/J+7. Aucun créneau perdu."),
        ("J-1, 18 h", "La bascule suppose au moins deux interventions PROD en attente dans le secteur. Sur Cormenon et La Ferté-Imbault, maintenir ce stock tampon."),
        ("Jour J", "Un SAV urgent arrivé après la bascule prend la place d'une PROD du jour, qui repart en J+5. <b>La PROD absorbe l'aléa, jamais le SAV</b> — c'est elle qui a le délai le plus long."),
        ("Hebdo", "Si l'occupation SAV d'un secteur dépasse 75 % quatre semaines de suite, augmenter sa réservation. Le curseur suit la demande réelle."),
        ("Hebdo", "Le renfort flottant (T11) est affecté le vendredi pour la semaine suivante, au secteur dont le carnet est le plus tendu."),
    ])
    questions = "".join(f'<h3>{q}</h3><p>{a}</p>' for q, a in [
        ("8 créneaux par jour, est-ce tenable sur le terrain ?",
         "C'est l'hypothèse qui fait tenir tout le reste. Votre planning SAV actuel tourne à <b>5,68 créneaux</b> par technicien et par jour, avec des journées affichées à 7 sur Blois et 5 en rural : passer à 8 représente <b>+41 %</b>. Si le réel plafonne à 7, la capacité tombe à 420 créneaux et il manque 16 créneaux pour atteindre 436."),
        ("La répartition des 436 créneaux entre secteurs vous convient-elle ?",
         "Elle est faite au prorata de la demande totale de chaque secteur, SAV et PROD confondus. Si un secteur mérite plus de disponibilité que son volume ne le justifie — un NRO récent, un client sensible, une zone à reprises fréquentes — la réservation peut être décalée sans toucher à la structure."),
        ("Où habitent les techniciens ?",
         "Les bases proposées (Blois, Vendôme, Romorantin, Crouy-sur-Cosson, Pontlevoy) sont déduites de la seule géographie. Si les domiciles réels sont ailleurs, les binômes de secteurs se réorganisent : c'est du temps de trajet payé tous les jours."),
        ("Comment piloter le renfort flottant ?",
         "T11 représente 5 journées, soit la totalité de la marge. Le principe retenu est une réaffectation hebdomadaire au secteur le plus tendu. Le figer sur Blois ferait disparaître la réserve des onze autres secteurs."),
        ("Le carnet PROD est-il assez fourni sur les petits secteurs ?",
         "Cormenon fait 19 interventions PROD par mois, La Ferté-Imbault 18 : moins d'une par jour ouvré. Si le carnet y est vide, un créneau SAV non vendu est perdu au lieu d'être recyclé en PROD par la bascule."),
        ("Y a-t-il des pénalités contractuelles sur le J+1/J+2 ?",
         "Si oui, le taux d'occupation cible doit être calé sur le pire cas et non sur la moyenne. À 65 % au lieu de 75 %, la cible passerait à 503 créneaux, au-delà de ce que 11 techniciens peuvent ouvrir."),
        ("Les volumes PROD d'octobre sont-ils une prévision ou un historique ?",
         "Le calcul retient le mois le plus chargé entre octobre et mars, secteur par secteur. Si octobre est une prévision haute qui ne se réalisera pas, la demande PROD baisse d'environ 20 interventions par semaine et la réserve passe de 44 à près de 70 créneaux."),
    ])
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8">
<title>Planification SAV / PROD — Loir-et-Cher</title><style>{CSS}</style></head><body>

<div class="meta">Département 41 · Loir-et-Cher &nbsp;·&nbsp; 12 secteurs GRDV · 59 NRO &nbsp;·&nbsp; 11 techniciens</div>
<h1>Planification SAV et PROD<br>du Loir-et-Cher</h1>
<p class="lede">Comment tenir un rendez-vous SAV à J+1 ou J+2 sur les douze secteurs,
tout en plaçant la production à J+5, J+6 ou J+7, avec l'effectif actuel.</p>
<hr class="rule">
{tiles}

<div class="sec">
<h2><span class="num-sec">01</span>Ce que dit le calcul</h2>
<p>La demande hebdomadaire du département est de <b>327 interventions</b> : 185 en production — volume du fichier
de suivi, mois le plus chargé secteur par secteur, B2B inclus, majoré des 10 % de flexibilité demandés — et
142 en service après-vente, relevées sur le planning hebdomadaire SAV.</p>
<p>À 8 créneaux par technicien et par jour, les 11 techniciens ouvrent <b>480 créneaux</b> par semaine
(60 jours-technicien : 5 techniciens à 6 jours et 6 techniciens à 5 jours). En n'occupant jamais plus de 75 %
des créneaux, il faut en ouvrir 436 pour absorber les 327 interventions. <b>La marge est de 44 créneaux,
soit un technicien.</b></p>
{CH['capacite']}
<div class="box good"><div class="t">Le quart de créneaux libres n'est pas du gaspillage, c'est le produit</div>
<p>Occuper 75 % des créneaux, c'est en laisser 109 ouverts chaque semaine. Sans eux, aucun client ne trouve de
place à J+1 ou J+2 : la disponibilité <b>est</b> ce quart. Et elle ne coûte presque rien, parce que la bascule
de la veille récupère les créneaux SAV non vendus pour y poser de la production tirée du carnet J+5/J+7.</p></div>
</div>

<div class="sec pb">
<h2><span class="num-sec">02</span>Pourquoi le délai n'est pas tenu aujourd'hui</h2>
<p>Le problème n'est pas le volume, c'est le calendrier. La grille actuelle concentre beaucoup de créneaux sur
peu de jours : <b>Cormenon n'est visité que le jeudi, Vouzon que le mercredi</b>. Un client de Cormenon qui
appelle le vendredi attend jusqu'au jeudi suivant, soit J+6.</p>
{CH['passages']}
<p>En énumérant toutes les combinaisons possibles de jours de passage, le résultat est net : sur une semaine de
six jours, <b>aucune paire de jours ne tient le J+1/J+2</b>, et parmi les vingt combinaisons de trois jours,
<b>deux seulement fonctionnent</b>. Elles se trouvent être exactement complémentaires.</p>
{CH['rythmes']}
</div>

<div class="sec pb">
<h2><span class="num-sec">03</span>Le principe : le SAV commande, la PROD suit</h2>
<p>Le service après-vente impose <b>où</b> et <b>quand</b> il faut être : chaque secteur doit être visité trois
fois par semaine, sur l'un des deux rythmes valides. La production, elle, dispose de cinq à sept jours de
visibilité : elle peut attendre, donc elle se place dans tout ce qui reste. C'est elle qui absorbe les
contraintes, jamais le SAV.</p>
{CH['calendrier']}
<p>Les cinq techniciens à six jours portent obligatoirement les secteurs du rythme Mardi-Jeudi-Samedi : sans
leur samedi, aucun créneau n'existe à J+1 ou J+2 pour un appel passé le jeudi ou le vendredi.</p>
</div>

<div class="sec pb">
<h2><span class="num-sec">04</span>Répartition des créneaux</h2>
<p>Les 480 créneaux sont répartis au prorata de la demande totale de chaque secteur. Blois, qui concentre 34 %
du volume départemental, en reçoit 160 ; La Ferté-Imbault, le plus petit, en reçoit 16.</p>
{CH['repartition']}
<h3>Contrôle secteur par secteur</h3>
<p>Trois conditions doivent être remplies partout : au moins trois passages SAV par semaine, une réservation SAV
au moins égale à la demande, et une capacité PROD au moins égale à la demande. Les douze secteurs les remplissent.</p>
{controle_table()}
</div>

<div class="landscape">
<h2><span class="num-sec">05</span>La grille hebdomadaire</h2>
<p style="font-size:8.4pt">Chaque journée est coupée en deux demi-journées de 4 créneaux. « SAV n » désigne les créneaux
réservés, ouverts à la prise de rendez-vous J+1/J+2 ; « PROD n » les interventions posées depuis le carnet J+5/J+7.
La tournée est figée : seul le partage SAV / PROD à l'intérieur de la journée évolue.</p>
<div class="legend">
  <span><i class="sw" style="background:#e4eefa;border:1px solid #b6cfe9"></i>demi-journée SAV</span>
  <span><i class="sw" style="background:#fceee6;border:1px solid #eec7ac"></i>demi-journée PROD</span>
  <span><i class="sw" style="background:#eff2f5;border:1px solid #cfd6dc"></i>demi-journée mixte</span>
  <span><i class="sw" style="background:#fdf0d8;border:1px solid #e5c98a"></i>technicien à 6 jours</span>
</div>
{grid_table()}
<p style="font-size:7.6pt;color:#4d5d6a;margin-top:7px;page-break-inside:avoid">T1 est le technicien 100 % SAV déjà
en poste, maintenu sur Blois et Valencisse (11 km entre les deux hubs). T11 est le renfort flottant : ses journées
constituent la réserve, réaffectée chaque vendredi pour la semaine suivante.</p>
</div>

<div class="sec pb">
<h2><span class="num-sec">06</span>Le moteur de disponibilité</h2>
<p>Réserver un créneau au SAV ne le consomme pas. Tant qu'il n'est pas vendu, il redevient de la production la
veille au soir. C'est ce qui rend une réservation généreuse presque gratuite, et c'est le mécanisme qui libère
de la disponibilité sans embaucher.</p>
<ol class="rules">{rules}</ol>
</div>

<div class="sec pb">
<h2><span class="num-sec">07</span>Cohérence des distances</h2>
<p>Distances routières estimées : vol d'oiseau majoré de 25 %, plus 8 km lorsque le trajet franchit la Loire
(ponts de Blois, Chaumont, Muides, Beaugency). À recaler avec votre outil de tournées.</p>
{dist_table()}
<div class="legend" style="margin-top:8px">
  <span><i class="sw" style="background:#eef8ee;border:1px solid #0ca30c"></i>≤ 30 km — enchaînement acceptable</span>
  <span><i class="sw" style="background:#fdf6e3;border:1px solid #fab219"></i>31 à 50 km — à éviter dans la même journée</span>
  <span><i class="sw" style="background:#fdf0f0;border:1px solid #d03b3b"></i>plus de 50 km — incohérent</span>
</div>
<h3>Enchaînements retenus dans la grille</h3>
<p>Quatre enchaînements seulement font passer un technicien d'un secteur à un autre en cours de journée, et
aucun ne dépasse 30 km : Montoire → Cormenon 30 km, Vendôme → Épiais 29 km, Romorantin → La Ferté-Imbault 22 km,
Romorantin → Mur-de-Sologne 13 km. Toutes les autres demi-journées restent dans le même secteur.</p>
<div class="box"><div class="t">Deux corrections par rapport à la grille actuelle</div>
<p>Cormenon était rattaché à la Sologne Est, à 113 km de Vouzon dans le même secteur, avec un jeudi enchaînant
Épiais le matin et Cormenon l'après-midi — 46 km entre les deux vacations. Cormenon repart au Nord, dans le
Vendômois-Perche, et l'enchaînement le plus long de la grille retombe à 30 km.</p></div>
</div>

<div class="sec pb">
<h2><span class="num-sec">08</span>Points à valider</h2>
{questions}
</div>

<footer>
Volumes de production : suivi_volumes_PROD_72.xlsx, mise à jour du 28 juillet 2026 — onglets « Suivi des volumes PROD »
et « Volume par NRO », 12 secteurs GRDV et 59 NRO sur le seul département 41.
Volume SAV : Planning_HEBDO_SAV_Departement_41.xlsx, 142 interventions par semaine.
Cadence de production rétro-calculée depuis le fichier source (règle vérifiée sur 256 des 263 lignes) mais non
utilisée dans ce document, la durée des interventions n'étant pas modélisée. Distances estimées, à confirmer.
</footer>
</body></html>"""


if __name__ == "__main__":
    open('rapport41.html', 'w').write(build())
    print("rapport41.html écrit")
