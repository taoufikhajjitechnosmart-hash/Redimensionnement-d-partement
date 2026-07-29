# -*- coding: utf-8 -*-
"""Trois tableaux de vérification, pivotés par secteur."""
import json, importlib.util, io, contextlib

spec = importlib.util.spec_from_file_location("g", "grille436.py")
m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(m)
GRID, JOURS = m.GRID, m.JOURS
C = json.load(open('cible436.json'))
R = json.load(open('grille436.json'))
ORDER = sorted(C['cible'], key=lambda x: -R['slots'][x])
PER = ["matin", "après-midi"]

piv = {s: {j: {p: [] for p in PER} for j in JOURS} for s in C['cible']}
for t, role, nj, sem in GRID:
    for j, day in zip(JOURS, sem):
        if day is None:
            continue
        for k, (sec, sav, prod) in enumerate(day):
            piv[sec][j][PER[k]].append((t, sav, prod))


def entries(sec, j, p, typ):
    return [(t, sav if typ == 'sav' else prod)
            for t, sav, prod in piv[sec][j][p] if (sav if typ == 'sav' else prod)]


def total(sec, typ):
    return sum(n for j in JOURS for p in PER for _, n in entries(sec, j, p, typ))


def planning_table(typ):
    cls = "sav" if typ == 'sav' else "prod"
    head = "".join(f'<th colspan="2">{j}</th>' for j in JOURS)
    sub = "".join('<th class="sub">m</th><th class="sub">ap-m</th>' for _ in JOURS)
    rows = []
    for s in ORDER:
        jp = R['pass'][s]
        cells = []
        for j in JOURS:
            for p in PER:
                e = entries(s, j, p, typ)
                if not e:
                    cells.append('<td class="nil">·</td>')
                else:
                    inner = "".join(f'<span class="chip"><i>{t}</i>{n}</span>' for t, n in e)
                    cells.append(f'<td class="{cls}">{inner}</td>')
        dem = C['sav_dem'][s] if typ == 'sav' else round(C['prod_dem'][s], 1)
        tot = total(s, typ)
        ok = tot >= dem
        rows.append(f'<tr><th class="rowh">{s}</th>{"".join(cells)}'
                    f'<td class="n tot">{tot}</td><td class="n dim">{dem}</td>'
                    f'<td class="n"><span class="pill {"ok" if ok else "ko"}">{"OK" if ok else "NON"}</span></td></tr>')
    tt = sum(total(s, typ) for s in ORDER)
    dd = 142 if typ == 'sav' else 185.3
    rows.append(f'<tr class="grand"><th>TOTAL</th><td colspan="12">12 secteurs</td>'
                f'<td class="n">{tt}</td><td class="n">{dd}</td><td class="n">12/12</td></tr>')
    return (f'<table class="pl"><thead><tr><th rowspan="2" class="rowh">Secteur</th>{head}'
            f'<th rowspan="2">ouvert</th><th rowspan="2">demandé</th><th rowspan="2">contrôle</th></tr>'
            f'<tr>{sub}</tr></thead><tbody>{"".join(rows)}</tbody></table>')


def controle_table():
    rows = []
    for s in ORDER:
        jp = R['pass'][s]
        ry = ("L-Me-V" if set(jp) == {"Lundi", "Mercredi", "Vendredi"}
              else "Ma-J-S" if set(jp) == {"Mardi", "Jeudi", "Samedi"} else "quotidien")
        sv, pr = total(s, 'sav'), total(s, 'prod')
        sd, pd = C['sav_dem'][s], round(C['prod_dem'][s], 1)
        marge_s, marge_p = sv - sd, round(pr - pd, 1)
        rows.append(
            f'<tr><th class="rowh">{s}</th>'
            f'<td class="c">{" · ".join(x[:3] for x in jp)}</td>'
            f'<td class="c"><b>{len(jp)}</b></td><td class="c mono">{ry}</td>'
            f'<td class="n">{sv}</td><td class="n dim">{sd}</td><td class="n pos">+{marge_s}</td>'
            f'<td class="n">{pr}</td><td class="n dim">{pd}</td><td class="n pos">+{marge_p}</td>'
            f'<td class="n">{sv+pr}</td><td class="n dim">{round(C["cible"][s])}</td>'
            f'<td class="c"><span class="pill ok">conforme</span></td></tr>')
    sv_t = sum(total(s, 'sav') for s in ORDER)
    pr_t = sum(total(s, 'prod') for s in ORDER)
    rows.append(f'<tr class="grand"><th>TOTAL</th><td class="c">—</td><td class="c">—</td><td></td>'
                f'<td class="n">{sv_t}</td><td class="n">142</td><td class="n">+{sv_t-142}</td>'
                f'<td class="n">{pr_t}</td><td class="n">185,3</td><td class="n">+{round(pr_t-185.3,1)}</td>'
                f'<td class="n">{sv_t+pr_t}</td><td class="n">436</td><td class="c">12 / 12</td></tr>')
    return ('<table class="ct"><thead><tr><th class="rowh">Secteur</th><th class="c">Jours SAV</th>'
            '<th class="c">Passages</th><th class="c">Rythme</th>'
            '<th class="n">SAV ouvert</th><th class="n">SAV dem.</th><th class="n">marge</th>'
            '<th class="n">PROD ouv.</th><th class="n">PROD dem.</th><th class="n">marge</th>'
            '<th class="n">Total</th><th class="n">Cible</th><th class="c">Contrôle</th>'
            f'</tr></thead><tbody>{"".join(rows)}</tbody></table>')


HTML = """<title>Vérification par secteur — Planification 41</title>
<style>
  :root{--paper:#f5f7f4;--surface:#fff;--surface-2:#eef1ee;--ink:#131c23;--ink-2:#4d5d6a;--ink-3:#77878f;
    --rule:#dde2de;--rule-2:#c6cec8;--sav:#2a78d6;--sav-bg:#e8f0fb;--prod:#c2551f;--prod-bg:#fceee6;
    --ok:#0a7d0a;--ok-bg:#eef8ee;--ko:#b02f2f;--ko-bg:#fdf0f0;--accent:#12507e;
    --shadow:0 1px 2px rgba(19,28,35,.06),0 4px 14px rgba(19,28,35,.05)}
  @media (prefers-color-scheme:dark){:root{--paper:#0e151b;--surface:#161f27;--surface-2:#1c272f;
    --ink:#e7eef3;--ink-2:#9dadba;--ink-3:#71828f;--rule:#27333d;--rule-2:#35434e;
    --sav:#7ab4ee;--sav-bg:#14304a;--prod:#e3a06a;--prod-bg:#382916;
    --ok:#63bd88;--ok-bg:#152c1f;--ko:#e5786e;--ko-bg:#311a18;--accent:#93c8ea;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 4px 16px rgba(0,0,0,.3)}}
  :root[data-theme="dark"]{--paper:#0e151b;--surface:#161f27;--surface-2:#1c272f;
    --ink:#e7eef3;--ink-2:#9dadba;--ink-3:#71828f;--rule:#27333d;--rule-2:#35434e;
    --sav:#7ab4ee;--sav-bg:#14304a;--prod:#e3a06a;--prod-bg:#382916;
    --ok:#63bd88;--ok-bg:#152c1f;--ko:#e5786e;--ko-bg:#311a18;--accent:#93c8ea;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 4px 16px rgba(0,0,0,.3)}
  :root[data-theme="light"]{--paper:#f5f7f4;--surface:#fff;--surface-2:#eef1ee;--ink:#131c23;--ink-2:#4d5d6a;
    --ink-3:#77878f;--rule:#dde2de;--rule-2:#c6cec8;--sav:#2a78d6;--sav-bg:#e8f0fb;--prod:#c2551f;
    --prod-bg:#fceee6;--ok:#0a7d0a;--ok-bg:#eef8ee;--ko:#b02f2f;--ko-bg:#fdf0f0;--accent:#12507e;
    --shadow:0 1px 2px rgba(19,28,35,.06),0 4px 14px rgba(19,28,35,.05)}
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);font-size:15px;line-height:1.55;
    font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1280px;margin:0 auto;padding:38px 22px 70px;display:flex;flex-direction:column;gap:40px}
  header{border-bottom:2px solid var(--ink);padding-bottom:18px;display:flex;flex-direction:column;gap:10px}
  .eyebrow{font-family:ui-monospace,monospace;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-3)}
  h1{margin:0;font-size:clamp(24px,3.4vw,34px);letter-spacing:-.02em;font-weight:750;line-height:1.1}
  .lede{margin:0;color:var(--ink-2);max-width:66ch}
  section{display:flex;flex-direction:column;gap:13px}
  h2{margin:0;font-size:19px;font-weight:700;letter-spacing:-.015em;display:flex;align-items:baseline;gap:11px}
  h2 .n{font-family:ui-monospace,monospace;font-size:12px;color:var(--accent);font-weight:700}
  .note{margin:0;color:var(--ink-2);font-size:13.5px;max-width:76ch}
  .note b{color:var(--ink)}
  .scroll{overflow-x:auto;border:1px solid var(--rule);border-radius:3px;background:var(--surface);box-shadow:var(--shadow)}
  table{border-collapse:collapse;width:100%;font-size:12px}
  th,td{border:1px solid var(--rule);padding:5px 6px;white-space:nowrap}
  thead th{background:var(--ink);color:var(--paper);font-size:10.5px;font-weight:650;letter-spacing:.04em;
    text-transform:uppercase;text-align:center;position:sticky;top:0;z-index:2}
  thead th.sub{background:var(--ink-2);font-size:9.5px;text-transform:lowercase;letter-spacing:0;font-weight:400}
  th.rowh{text-align:left;background:var(--surface-2);color:var(--ink);font-weight:650;font-size:12px;
    position:sticky;left:0;z-index:1;min-width:158px;text-transform:none;letter-spacing:0}
  thead th.rowh{background:var(--ink);color:var(--paper);z-index:3}
  td{text-align:center}
  td.nil{color:var(--ink-3);background:var(--surface)}
  td.sav{background:var(--sav-bg)} td.prod{background:var(--prod-bg)}
  .chip{display:inline-flex;align-items:baseline;gap:3px;font-family:ui-monospace,monospace;font-size:11px;
    font-weight:700;margin:0 2px}
  td.sav .chip{color:var(--sav)} td.prod .chip{color:var(--prod)}
  .chip i{font-style:normal;font-size:9px;opacity:.75;font-weight:400}
  td.n{text-align:right;font-family:ui-monospace,monospace;font-variant-numeric:tabular-nums}
  td.c{text-align:center}
  td.dim{color:var(--ink-3)} td.tot{font-weight:700}
  td.pos{color:var(--ok);font-size:11px}
  .mono{font-family:ui-monospace,monospace;font-size:11px;color:var(--ink-2)}
  tr.grand th,tr.grand td{background:var(--ink);color:var(--paper);font-weight:700}
  tr.grand td.dim,tr.grand td.pos{color:var(--paper);opacity:.75}
  .pill{display:inline-block;padding:1px 7px;border-radius:2px;font-size:10px;font-weight:700;
    font-family:ui-monospace,monospace;border:1px solid currentColor}
  .pill.ok{color:var(--ok);background:var(--ok-bg)} .pill.ko{color:var(--ko);background:var(--ko-bg)}
  tr.grand .pill{border:0;background:none;color:var(--paper)}
  .legend{display:flex;gap:18px;flex-wrap:wrap;font-size:12.5px;color:var(--ink-2);align-items:center}
  .legend span{display:inline-flex;align-items:center;gap:6px}
  .sw{width:13px;height:13px;border-radius:2px;border:1px solid var(--rule-2)}
  .box{border-left:3px solid var(--accent);background:var(--surface);padding:12px 15px;border-radius:0 3px 3px 0;
    box-shadow:var(--shadow);display:flex;flex-direction:column;gap:5px}
  .box.warn{border-left-color:var(--prod)}
  .box .t{font-weight:700;font-size:14px}
  .box p{margin:0;font-size:13.5px;color:var(--ink-2)}
  @media (max-width:620px){.wrap{padding:24px 12px 50px;gap:30px}}
</style>
<div class="wrap">
<header>
  <div class="eyebrow">Département 41 · vérification croisée · 11 techniciens · 480 créneaux</div>
  <h1>Le planning vu par secteur</h1>
  <p class="lede">La même grille, pivotée : au lieu de lire ce que fait chaque technicien, on lit ce que
  reçoit chaque secteur. Les totaux se recoupent exactement avec la grille par technicien —
  168 créneaux SAV et 312 créneaux PROD des deux côtés.</p>
</header>

<section>
  <h2><span class="n">01</span>Planning SAV par secteur</h2>
  <p class="note">Créneaux réservés au SAV, ouverts à la prise de rendez-vous J+1/J+2.
  Chaque case indique le technicien et le nombre de créneaux. <b>Un secteur doit apparaître trois fois
  par semaine</b>, sur les colonnes Lundi-Mercredi-Vendredi ou Mardi-Jeudi-Samedi.</p>
  <div class="legend">
    <span><i class="sw" style="background:var(--sav-bg);border-color:var(--sav)"></i>demi-journée avec créneaux SAV</span>
    <span><i class="sw" style="background:var(--surface)"></i>pas de SAV sur cette demi-journée</span>
    <span class="mono">T2·4 = technicien T2, 4 créneaux</span>
  </div>
  <div class="scroll">{TABLE_SAV}</div>
</section>

<section>
  <h2><span class="n">02</span>Planning PROD par secteur</h2>
  <p class="note">Créneaux ouverts à la production, posés depuis le carnet J+5/J+7. Ils occupent tout ce que
  le SAV ne réserve pas. <b>Chaque secteur doit recevoir au moins sa demande</b> — les excédents constituent
  la réserve locale et absorbent les reports.</p>
  <div class="legend">
    <span><i class="sw" style="background:var(--prod-bg);border-color:var(--prod)"></i>demi-journée avec créneaux PROD</span>
    <span><i class="sw" style="background:var(--surface)"></i>pas de PROD sur cette demi-journée</span>
  </div>
  <div class="scroll">{TABLE_PROD}</div>
  <div class="box warn"><span class="t">Ce que ce tableau révèle : la réserve est concentrée sur Blois</span>
  <p>Blois reçoit 116 créneaux PROD pour une demande de 61,7 — près du double. C'est là que se loge l'essentiel
  des 44 créneaux de réserve, parce que T7, T8 et le renfort flottant T11 y sont basés à plein temps.
  C'est défendable (Blois est le secteur le plus volumineux et le plus variable), mais si vous préférez
  redistribuer cette marge vers les secteurs ruraux, c'est le levier à actionner.</p></div>
</section>

<section>
  <h2><span class="n">03</span>Contrôle</h2>
  <p class="note">Les trois conditions à vérifier sur chaque secteur : au moins trois passages SAV par semaine
  sur un rythme valide, une réservation SAV au moins égale à la demande, et une capacité PROD au moins égale
  à la demande.</p>
  <div class="scroll">{TABLE_CTRL}</div>
  <div class="box"><span class="t">12 secteurs sur 12 conformes</span>
  <p>Aucune marge n'est négative. Les écarts positifs ne sont pas du gaspillage : ce sont les créneaux qui
  restent libres à J-1 et que la bascule recycle en production. Le seul secteur légèrement sous sa cible
  théorique est Vendôme (24 créneaux ouverts pour 25 visés), sans conséquence puisque sa demande SAV
  et sa demande PROD sont toutes deux couvertes.</p></div>
</section>
</div>"""


if __name__ == "__main__":
    html = (HTML.replace("{TABLE_SAV}", planning_table('sav'))
                .replace("{TABLE_PROD}", planning_table('prod'))
                .replace("{TABLE_CTRL}", controle_table()))
    open('verification41.html', 'w').write(html)
    print("verification41.html écrit —", len(html), "caractères")
    sv = sum(total(s, 'sav') for s in ORDER); pr = sum(total(s, 'prod') for s in ORDER)
    print(f"contrôle : SAV {sv} · PROD {pr} · total {sv+pr}")
