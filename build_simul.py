# -*- coding: utf-8 -*-
"""Page de comparaison des deux simulations avec SAV du lundi au vendredi."""
import json

D = json.load(open('simul5j.json'))
J5 = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
JOURS = J5 + ["Samedi"]
SHORT = {"Montoire-sur-le-Loir": "Montoire", "Romorantin-Lanthenay": "Romorantin",
         "Crouy-sur-Cosson": "Crouy-s-Cosson", "La Ferté-Imbault": "La Ferté-Imb."}
SAV_DEM = json.load(open('sav_reel.json'))
PROD_DEM = {"Blois": 61.7, "Pontlevoy": 22.5, "Crouy-sur-Cosson": 13.3, "Épiais": 12.9,
            "Mur-de-Sologne": 12.5, "Montoire-sur-le-Loir": 12.3, "Romorantin-Lanthenay": 11.3,
            "Valencisse": 11.1, "Vendôme": 9.8, "Vouzon": 8.5, "Cormenon": 4.9, "La Ferté-Imbault": 4.5}
ROLE = {"Blois": "Blois + Valencisse", "Nord": "Vendômois / Perche / Beauce",
        "Sologne Sud": "Sologne Sud", "Est": "Sologne Est", "Sud-Ouest": "Sud-Ouest"}


def grille_table(lab):
    v = D[lab]
    rows = []
    for t, cl, nj in v['techs']:
        g = v['grille'][t]
        cells = []
        sv = pr = 0
        for j in JOURS:
            if j not in g:
                cells.append('<td class="off" colspan="2">repos</td>')
                continue
            for k in (0, 1):
                c = g[j][k]
                if c is None:
                    cells.append('<td class="nil">—</td>')
                    continue
                s, a, p = c
                sv += a; pr += p
                cls = "sav" if a else "prod"
                cells.append(f'<td class="{cls}"><span class="s">{SHORT.get(s, s)}</span>'
                             f'<span class="c">{"SAV" if a else "PROD"} {a or p}</span></td>')
        rows.append(f'<tr><td class="tid">{t}</td><td class="trole">{ROLE[cl]}</td>'
                    f'<td class="tj{" six" if nj == 6 else ""}">{nj}</td>{"".join(cells)}'
                    f'<td class="n sv">{sv}</td><td class="n pr">{pr}</td></tr>')
    th = "".join(f'<th colspan="2">{j}</th>' for j in JOURS)
    sub = "".join('<th class="sub">m</th><th class="sub">ap-m</th>' for _ in JOURS)
    return (f'<table class="gr"><thead><tr><th rowspan="2">Tech.</th><th rowspan="2">Secteurs</th>'
            f'<th rowspan="2">J</th>{th}<th rowspan="2">SAV</th><th rowspan="2">PROD</th></tr>'
            f'<tr>{sub}</tr></thead><tbody>{"".join(rows)}'
            f'<tr class="gtot"><td colspan="3">TOTAL — {v["td"]} jours-technicien</td>'
            f'<td colspan="12">12 secteurs · 3 passages SAV minimum chacun</td>'
            f'<td>{v["sav"]}</td><td>{v["prod"]}</td></tr></tbody></table>')


def secteurs_table(lab):
    v = D[lab]
    rows = []
    for s in sorted(v['slots'], key=lambda x: -v['slots'][x]):
        jp = v['passages'][s]
        rows.append(f'<tr><th class="rowh">{s}</th>'
                    f'<td class="c mono">{"-".join(x[:3] for x in jp)}</td><td class="c"><b>{len(jp)}</b></td>'
                    f'<td class="n">{v["sav_sec"][s]}</td><td class="n dim">{SAV_DEM[s]}</td>'
                    f'<td class="n">{v["prod_sec"][s]}</td><td class="n dim">{PROD_DEM[s]}</td>'
                    f'<td class="n">{v["slots"][s]}</td>'
                    f'<td class="c"><span class="pill ok">conforme</span></td></tr>')
    rows.append(f'<tr class="gtot"><th>TOTAL</th><td colspan="2">12 secteurs</td>'
                f'<td class="n">{v["sav"]}</td><td class="n">142</td>'
                f'<td class="n">{v["prod"]}</td><td class="n">185,3</td>'
                f'<td class="n">{v["total"]}</td><td class="c">12 / 12</td></tr>')
    return ('<table class="ct"><thead><tr><th class="rowh">Secteur</th><th class="c">Rythme SAV</th>'
            '<th class="c">Passages</th><th class="n">SAV ouvert</th><th class="n">SAV dem.</th>'
            '<th class="n">PROD ouv.</th><th class="n">PROD dem.</th><th class="n">Total</th>'
            f'<th class="c">Contrôle</th></tr></thead><tbody>{"".join(rows)}</tbody></table>')


CSS = """
:root{--paper:#f5f7f4;--surface:#fff;--surface-2:#eef1ee;--ink:#131c23;--ink-2:#4d5d6a;--ink-3:#77878f;
 --rule:#dde2de;--rule-2:#c6cec8;--sav:#2a78d6;--sav-bg:#e8f0fb;--prod:#c2551f;--prod-bg:#fceee6;
 --ok:#0a7d0a;--ok-bg:#eef8ee;--ko:#b02f2f;--ko-bg:#fdf0f0;--warn:#8a6410;--warn-bg:#fdf6e3;--accent:#12507e;
 --shadow:0 1px 2px rgba(19,28,35,.06),0 4px 14px rgba(19,28,35,.05)}
@media (prefers-color-scheme:dark){:root{--paper:#0e151b;--surface:#161f27;--surface-2:#1c272f;--ink:#e7eef3;
 --ink-2:#9dadba;--ink-3:#71828f;--rule:#27333d;--rule-2:#35434e;--sav:#7ab4ee;--sav-bg:#14304a;
 --prod:#e3a06a;--prod-bg:#382916;--ok:#63bd88;--ok-bg:#152c1f;--ko:#e5786e;--ko-bg:#311a18;
 --warn:#d9ab4a;--warn-bg:#2c2413;--accent:#93c8ea;--shadow:0 1px 2px rgba(0,0,0,.4),0 4px 16px rgba(0,0,0,.3)}}
:root[data-theme="dark"]{--paper:#0e151b;--surface:#161f27;--surface-2:#1c272f;--ink:#e7eef3;--ink-2:#9dadba;
 --ink-3:#71828f;--rule:#27333d;--rule-2:#35434e;--sav:#7ab4ee;--sav-bg:#14304a;--prod:#e3a06a;
 --prod-bg:#382916;--ok:#63bd88;--ok-bg:#152c1f;--ko:#e5786e;--ko-bg:#311a18;--warn:#d9ab4a;--warn-bg:#2c2413;
 --accent:#93c8ea;--shadow:0 1px 2px rgba(0,0,0,.4),0 4px 16px rgba(0,0,0,.3)}
:root[data-theme="light"]{--paper:#f5f7f4;--surface:#fff;--surface-2:#eef1ee;--ink:#131c23;--ink-2:#4d5d6a;
 --ink-3:#77878f;--rule:#dde2de;--rule-2:#c6cec8;--sav:#2a78d6;--sav-bg:#e8f0fb;--prod:#c2551f;
 --prod-bg:#fceee6;--ok:#0a7d0a;--ok-bg:#eef8ee;--ko:#b02f2f;--ko-bg:#fdf0f0;--warn:#8a6410;--warn-bg:#fdf6e3;
 --accent:#12507e;--shadow:0 1px 2px rgba(19,28,35,.06),0 4px 14px rgba(19,28,35,.05)}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-size:15px;line-height:1.55;
 font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1280px;margin:0 auto;padding:38px 22px 70px;display:flex;flex-direction:column;gap:42px}
header{border-bottom:2px solid var(--ink);padding-bottom:18px;display:flex;flex-direction:column;gap:10px}
.eyebrow{font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3)}
h1{margin:0;font-size:clamp(24px,3.4vw,34px);letter-spacing:-.02em;font-weight:750;line-height:1.1}
.lede{margin:0;color:var(--ink-2);max-width:68ch}
section{display:flex;flex-direction:column;gap:13px}
h2{margin:0;font-size:19px;font-weight:700;letter-spacing:-.015em;display:flex;align-items:baseline;gap:11px}
h2 .n{font-family:ui-monospace,monospace;font-size:12px;color:var(--accent);font-weight:700}
h3{margin:6px 0 0;font-size:14.5px;font-weight:700}
.note{margin:0;color:var(--ink-2);font-size:13.5px;max-width:78ch}
.note b{color:var(--ink)}
.scroll{overflow-x:auto;border:1px solid var(--rule);border-radius:3px;background:var(--surface);box-shadow:var(--shadow)}
table{border-collapse:collapse;width:100%;font-size:12px}
th,td{border:1px solid var(--rule);padding:5px 6px;white-space:nowrap}
thead th{background:var(--ink);color:var(--paper);font-size:10.5px;font-weight:650;letter-spacing:.04em;
 text-transform:uppercase;text-align:center}
thead th.sub{background:var(--ink-2);font-size:9.5px;text-transform:lowercase;letter-spacing:0;font-weight:400}
th.rowh{text-align:left;background:var(--surface-2);color:var(--ink);font-weight:650;font-size:12px;
 min-width:150px;text-transform:none;letter-spacing:0}
thead th.rowh{background:var(--ink);color:var(--paper)}
td{text-align:center}
.gr{font-size:10.5px;table-layout:fixed}
.gr td{padding:3px 4px;vertical-align:top;height:34px}
.gr .tid{font-weight:750;font-size:12px;background:var(--surface-2)}
.gr .trole{font-size:10px;background:var(--surface-2);text-align:left;white-space:normal;min-width:110px}
.gr .tj{font-weight:700;background:var(--surface-2);width:28px}
.gr .tj.six{background:var(--warn-bg);color:var(--warn)}
.gr .s{display:block;font-weight:700;font-size:10px;line-height:1.2}
.gr .c{display:block;font-family:ui-monospace,monospace;font-size:8.5px;opacity:.85}
.gr td.sav{background:var(--sav-bg)} .gr td.sav .s,.gr td.sav .c{color:var(--sav)}
.gr td.prod{background:var(--prod-bg)} .gr td.prod .s,.gr td.prod .c{color:var(--prod)}
.gr td.off{background:var(--surface-2);color:var(--ink-3);font-size:10px;vertical-align:middle}
.gr td.nil{color:var(--ink-3)}
.gr .n{font-family:ui-monospace,monospace;font-weight:700;font-size:11px;background:var(--surface-2)}
.gr .n.sv{color:var(--sav)} .gr .n.pr{color:var(--prod)}
td.n{text-align:right;font-family:ui-monospace,monospace;font-variant-numeric:tabular-nums}
td.dim{color:var(--ink-3)}
.mono{font-family:ui-monospace,monospace;font-size:11px;color:var(--ink-2)}
tr.gtot th,tr.gtot td{background:var(--ink);color:var(--paper);font-weight:700}
tr.gtot td.dim{color:var(--paper);opacity:.7}
.pill{display:inline-block;padding:1px 7px;border-radius:2px;font-size:10px;font-weight:700;
 font-family:ui-monospace,monospace;border:1px solid currentColor}
.pill.ok{color:var(--ok);background:var(--ok-bg)}
tr.gtot .pill{border:0;background:none;color:var(--paper)}
.cmp{display:grid;grid-template-columns:1fr;gap:0;border:1px solid var(--rule);border-radius:3px;
 overflow:hidden;background:var(--surface);box-shadow:var(--shadow)}
.cmp table{font-size:13px}
.cmp th:first-child{text-align:left}
.cmp td.hi{background:var(--ok-bg);color:var(--ok);font-weight:700}
.cmp td.lo{background:var(--ko-bg);color:var(--ko);font-weight:700}
.box{border-left:3px solid var(--accent);background:var(--surface);padding:12px 15px;border-radius:0 3px 3px 0;
 box-shadow:var(--shadow);display:flex;flex-direction:column;gap:5px}
.box.warn{border-left-color:var(--ko)}
.box.good{border-left-color:var(--ok)}
.box .t{font-weight:700;font-size:14px}
.box p{margin:0;font-size:13.5px;color:var(--ink-2)}
.legend{display:flex;gap:18px;flex-wrap:wrap;font-size:12.5px;color:var(--ink-2);align-items:center}
.legend span{display:inline-flex;align-items:center;gap:6px}
.sw{width:13px;height:13px;border-radius:2px;border:1px solid var(--rule-2)}
@media (max-width:620px){.wrap{padding:24px 12px 50px;gap:30px}}
"""


def build():
    A, B = D['A'], D['B']
    lignes = [
        ("Jours travaillés — SAV", "lundi au samedi", "lundi au vendredi", "lundi au vendredi"),
        ("Jours travaillés — PROD", "lundi au samedi", "lundi au samedi", "lundi au vendredi"),
        ("Techniciens à 6 jours", "5", "5", "0"),
        ("Jours-technicien / semaine", "60", "60", "55"),
        ("Capacité théorique", "480", "480", "440"),
        ("Créneaux réellement ouverts", "480", str(A['total']), str(B['total'])),
        ("Créneaux à ouvrir (75 % d'occupation)", "436", "436", "436"),
        ("Réserve", "+44", f"+{A['total']-A['besoin']}", f"{B['total']-B['besoin']}"),
        ("Taux d'occupation atteint", "68,1 %", f"{A['occupation']:.1%}".replace('.', ','),
         f"{B['occupation']:.1%}".replace('.', ',')),
        ("Rythmes SAV disponibles", "2 (L-Me-V et Ma-J-S)", "5 motifs, jamais disjoints", "5 motifs, jamais disjoints"),
        ("Secteurs tenant le J+1/J+2", "12 / 12", "12 / 12", "12 / 12"),
        ("Enchaînement le plus long", "30 km", f"{A['pire']} km", f"{B['pire']} km"),
        ("Techniciens sur la Sologne Est", "1", "2", "2"),
    ]
    tr = []
    for lab, base, a, b in lignes:
        cls_a = cls_b = ""
        if lab == "Réserve":
            cls_a, cls_b = "hi", "lo"
        if lab == "Taux d'occupation atteint":
            cls_b = "lo"
        tr.append(f'<tr><th>{lab}</th><td>{base}</td><td class="{cls_a}">{a}</td><td class="{cls_b}">{b}</td></tr>')
    cmp_table = ('<table><thead><tr><th>Critère</th><th>Base — SAV 6 jours</th>'
                 '<th>Simulation A</th><th>Simulation B</th></tr></thead>'
                 f'<tbody>{"".join(tr)}</tbody></table>')
    return f"""<title>Simulations SAV lundi-vendredi — Loir-et-Cher</title>
<style>{CSS}</style>
<div class="wrap">
<header>
  <div class="eyebrow">Département 41 · deux simulations · 11 techniciens · 8 créneaux par jour</div>
  <h1>Et si le SAV s'arrêtait au vendredi ?</h1>
  <p class="lede">Même base de demande — 185 interventions de production majorées de 10 % et 142 de service
  après-vente — mais le SAV n'est plus proposé le samedi. Deux variantes : la production continue le samedi
  (A), ou plus personne ne travaille le samedi (B).</p>
</header>

<section>
  <h2><span class="n">01</span>Ce que change la semaine de cinq jours</h2>
  <p class="note">Sur six jours, il n'existait que <b>deux</b> rythmes de trois passages tenant le J+1/J+2 —
  Lundi-Mercredi-Vendredi et Mardi-Jeudi-Samedi — et ils étaient exactement complémentaires. Sur cinq jours,
  il en existe <b>cinq</b> : Lun-Mar-Jeu, Lun-Mer-Jeu, Lun-Mer-Ven, Mar-Mer-Ven et Mar-Jeu-Ven. Plus de
  souplesse en apparence, mais une contrainte nouvelle et coûteuse.</p>
  <div class="box warn"><span class="t">Deux motifs de trois jours pris parmi cinq se chevauchent forcément</span>
  <p>Trois plus trois font six, or la semaine n'a que cinq jours : <b>il n'existe plus aucune paire de rythmes
  disjoints</b>. Un technicien qui couvre deux secteurs se retrouve donc, au moins un jour par semaine, attendu
  aux deux endroits le même jour. Il peut faire l'un le matin et l'autre l'après-midi — mais seulement si les
  deux sont assez proches.</p></div>
  <div class="box"><span class="t">Conséquence concrète : la Sologne Est passe de un à deux techniciens</span>
  <p>Crouy-sur-Cosson et Vouzon sont distants de 38 km. Sur six jours, ils tenaient sur un seul technicien
  (Crouy en Lundi-Mercredi-Vendredi, Vouzon en Mardi-Jeudi-Samedi, jamais le même jour). Sur cinq jours, leurs
  rythmes se croisent forcément un jour, et 38 km est trop long pour un enchaînement matin/après-midi.
  <b>Il faut deux techniciens sur un cluster qui n'en demandait qu'un</b> — c'est le coût caché de la perte du samedi.</p></div>
</section>

<section>
  <h2><span class="n">02</span>Comparaison</h2>
  <div class="cmp">{cmp_table}</div>
  <div class="box good"><span class="t">Simulation A tient : 462 créneaux ouverts pour 436 nécessaires</span>
  <p>Supprimer le SAV du samedi ne coûte presque rien tant que la production, elle, continue de tourner ce
  jour-là. Les cinq techniciens à six jours consacrent leur samedi à de la production pure, et les 26 créneaux
  de réserve suffisent. Le taux d'occupation reste à {A['occupation']:.0%}, sous l'objectif de 75 %.</p></div>
  <div class="box warn"><span class="t">Simulation B ne tient pas tout à fait : il manque 14 créneaux</span>
  <p>Sans samedi du tout, l'équipe descend à 55 jours-technicien et n'ouvre que {B['total']} créneaux là où il
  en faudrait 436. Les douze secteurs restent conformes — chacun reçoit sa demande SAV et sa demande PROD —
  mais le taux d'occupation monte à <b>{B['occupation']:.0%}</b> au lieu des 75 % visés. Autrement dit, la
  planification fonctionne, mais la disponibilité promise au client se réduit :
  il reste moins de créneaux libres à J+1 et J+2.</p></div>
</section>

<section>
  <h2><span class="n">03</span>Simulation A — grille hebdomadaire</h2>
  <p class="note">SAV du lundi au vendredi, production jusqu'au samedi. Les cinq techniciens à six jours
  (colonne J en orange) font du samedi une journée de production pure.</p>
  <div class="legend">
    <span><i class="sw" style="background:var(--sav-bg);border-color:var(--sav)"></i>demi-journée SAV</span>
    <span><i class="sw" style="background:var(--prod-bg);border-color:var(--prod)"></i>demi-journée PROD</span>
    <span><i class="sw" style="background:var(--warn-bg);border-color:var(--warn)"></i>technicien à 6 jours</span>
  </div>
  <div class="scroll">{grille_table('A')}</div>
  <h3>Contrôle par secteur</h3>
  <div class="scroll">{secteurs_table('A')}</div>
</section>

<section>
  <h2><span class="n">04</span>Simulation B — grille hebdomadaire</h2>
  <p class="note">Tout le monde du lundi au vendredi. Le samedi disparaît entièrement : 55 jours-technicien
  au lieu de 60.</p>
  <div class="scroll">{grille_table('B')}</div>
  <h3>Contrôle par secteur</h3>
  <div class="scroll">{secteurs_table('B')}</div>
</section>

<section>
  <h2><span class="n">05</span>Ce qu'il faudrait pour que B tienne</h2>
  <p class="note">Trois leviers, à choisir selon ce qui est négociable :</p>
  <div class="box"><span class="t">Accepter 78 % d'occupation au lieu de 75 %</span>
  <p>C'est l'option gratuite. La planification fonctionne telle quelle, mais la marge de disponibilité passe
  de 25 % à 22 %. Concrètement, un client sur cinquante de plus ne trouvera pas de créneau à J+1 ou J+2 aux
  heures de pointe.</p></div>
  <div class="box"><span class="t">Ajouter deux jours-technicien</span>
  <p>Faire travailler deux techniciens six jours — mais du lundi au vendredi plus un jour de récupération
  ailleurs — ou recruter un mi-temps. C'est 16 créneaux, soit un peu plus que les 14 manquants.</p></div>
  <div class="box"><span class="t">Passer à 8,5 créneaux par technicien et par jour</span>
  <p>55 jours-technicien à 8,5 créneaux donnent 468 créneaux, largement au-dessus des 436 requis.
  Mais votre planning actuel tourne à 5,68 : c'est le levier le plus incertain des trois.</p></div>
</section>
</div>"""


if __name__ == "__main__":
    open('simulations41.html', 'w').write(build())
    print("simulations41.html écrit")
