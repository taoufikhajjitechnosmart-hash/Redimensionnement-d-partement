# -*- coding: utf-8 -*-
"""Graphiques du PDF comparatif — palette validée (slots catégoriels 1 et 2)."""
import json, itertools

SAV_C, PROD_C = "#2a78d6", "#eb6834"
OK_C, KO_C, WARN_C = "#0ca30c", "#d03b3b", "#c08a10"
INK, INK2, INK3 = "#141c23", "#4d5d6a", "#8a95a0"
GRID_C, SURF2, SURF = "#e4e8ea", "#f2f4f5", "#ffffff"

R = json.load(open('grille436.json'))
S = json.load(open('simul5j.json'))
DEM = 327.3
BESOIN = 436

SCEN = [
    ("Base", "SAV du lundi au samedi", 60, sum(R['sav'].values()), sum(R['prod'].values())),
    ("Simulation A", "SAV lundi-vendredi, PROD jusqu'au samedi", S['A']['td'], S['A']['sav'], S['A']['prod']),
    ("Simulation B", "tout le monde du lundi au vendredi", S['B']['td'], S['B']['sav'], S['B']['prod']),
]


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=9, fill=INK2, anchor="start", weight="400", mono=False):
    fam = "ui-monospace, 'DejaVu Sans Mono', monospace" if mono else "Inter, 'DejaVu Sans', sans-serif"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{fam}">{esc(s)}</text>')


def wrap(w, h, body):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="Inter, sans-serif" class="viz" role="img">{body}</svg>')


def bar(x, y, w, h, col):
    w = max(0, w)
    r = min(4, w)
    return (f'<path d="M{x:.1f} {y:.1f} h{w-r:.1f} a{r} {r} 0 0 1 {r} {r} v{h-2*r:.1f} '
            f'a{r} {r} 0 0 1 -{r} {r} h-{w-r:.1f} z" fill="{col}"/>')


# ═════════ 1. Créneaux ouverts par scénario
def chart_creneaux():
    W, RH, TOP, LEFT, RIGHT = 700, 62, 74, 118, 96
    H = TOP + len(SCEN) * RH + 40
    plot = W - LEFT - RIGHT
    mx = 500
    sc = plot / mx
    b = [f'<rect width="{W}" height="{H}" fill="{SURF}"/>']
    b.append(txt(0, 15, "Créneaux ouverts par semaine, selon le scénario", 11.5, INK, weight="650"))
    b.append(txt(0, 30, "Il faut en ouvrir 436 pour absorber 327 interventions sans dépasser 75 % d'occupation", 8.5, INK3))
    for g in range(0, mx + 1, 100):
        x = LEFT + g * sc
        b.append(f'<line x1="{x:.1f}" y1="{TOP-8}" x2="{x:.1f}" y2="{TOP+len(SCEN)*RH-14}" stroke="{GRID_C}" stroke-width="1"/>')
        b.append(txt(x, TOP - 12, g, 7.5, INK3, "middle", mono=True))
    xb = LEFT + BESOIN * sc
    b.append(f'<line x1="{xb:.1f}" y1="{TOP-26}" x2="{xb:.1f}" y2="{TOP+len(SCEN)*RH-14}" stroke="{INK}" stroke-width="1.5"/>')
    b.append(txt(xb, TOP - 30, "436 nécessaires", 8, INK, "middle", weight="650"))
    for i, (nom, sous, td, sav, prod) in enumerate(SCEN):
        y = TOP + i * RH
        tot = sav + prod
        cap = td * 8
        b.append(txt(LEFT - 10, y + 12, nom, 9.5, INK, "end", weight="650"))
        b.append(txt(LEFT - 10, y + 24, f"{td} j-tech", 7.5, INK3, "end", mono=True))
        # capacité théorique en fond
        b.append(f'<rect x="{LEFT}" y="{y+2}" width="{cap*sc:.1f}" height="26" rx="3" fill="{SURF2}"/>')
        b.append(bar(LEFT, y + 2, sav * sc, 26, SAV_C))
        b.append(bar(LEFT + sav * sc + 2, y + 2, prod * sc - 2, 26, PROD_C))
        if sav * sc > 46:
            b.append(txt(LEFT + sav * sc / 2, y + 19, f"SAV {sav}", 8.5, "#fff", "middle", weight="650"))
        if prod * sc > 54:
            b.append(txt(LEFT + (sav + prod / 2) * sc, y + 19, f"PROD {prod}", 8.5, "#fff", "middle", weight="650"))
        col = OK_C if tot >= BESOIN else KO_C
        b.append(txt(LEFT + cap * sc + 10, y + 13, tot, 12, col, weight="700", mono=True))
        b.append(txt(LEFT + cap * sc + 10, y + 25, f"{tot-BESOIN:+d}", 8, col, weight="650", mono=True))
        b.append(txt(LEFT + cap * sc - 4, y + 40, f"capacité {cap}", 7.5, INK3, "end", mono=True))
    yl = TOP + len(SCEN) * RH + 4
    b.append(f'<rect x="{LEFT}" y="{yl-8}" width="9" height="9" rx="2" fill="{SAV_C}"/>')
    b.append(txt(LEFT + 13, yl, "créneaux SAV réservés", 8, INK2))
    b.append(f'<rect x="{LEFT+146}" y="{yl-8}" width="9" height="9" rx="2" fill="{PROD_C}"/>')
    b.append(txt(LEFT + 159, yl, "créneaux PROD", 8, INK2))
    b.append(f'<rect x="{LEFT+256}" y="{yl-8}" width="9" height="9" rx="2" fill="{SURF2}"/>')
    b.append(txt(LEFT + 269, yl, "capacité théorique non ouverte", 8, INK2))
    return wrap(W, H, "".join(b))


# ═════════ 2. Taux d'occupation
def chart_occupation():
    W, RH, TOP, LEFT, RIGHT = 700, 40, 66, 118, 118
    H = TOP + len(SCEN) * RH + 26
    plot = W - LEFT - RIGHT
    sc = plot / 0.90
    b = [f'<rect width="{W}" height="{H}" fill="{SURF}"/>']
    b.append(txt(0, 15, "Taux d'occupation atteint", 11.5, INK, weight="650"))
    b.append(txt(0, 30, "Part des créneaux consommée par la demande. Le complément est la disponibilité offerte au client.", 8.5, INK3))
    for g in [0, .25, .5, .75]:
        x = LEFT + g * sc
        b.append(f'<line x1="{x:.1f}" y1="{TOP-8}" x2="{x:.1f}" y2="{TOP+len(SCEN)*RH-12}" stroke="{GRID_C}" stroke-width="1"/>')
        b.append(txt(x, TOP - 12, f"{g:.0%}", 7.5, INK3, "middle", mono=True))
    xs = LEFT + 0.75 * sc
    b.append(f'<line x1="{xs:.1f}" y1="{TOP-26}" x2="{xs:.1f}" y2="{TOP+len(SCEN)*RH-12}" stroke="{INK}" stroke-width="1.5"/>')
    b.append(txt(xs, TOP - 30, "plafond visé : 75 %", 8, INK, "middle", weight="650"))
    for i, (nom, sous, td, sav, prod) in enumerate(SCEN):
        y = TOP + i * RH
        occ = DEM / (sav + prod)
        col = OK_C if occ <= 0.75 else KO_C
        b.append(txt(LEFT - 10, y + 15, nom, 9.5, INK, "end", weight="650"))
        b.append(bar(LEFT, y + 4, occ * sc, 20, col))
        b.append(txt(LEFT + 0.83 * sc, y + 18, f"{occ:.1%}".replace(".", ","), 10, col, weight="700", mono=True))
        libre = 1 - occ
        b.append(txt(W - 6, y + 18, f"{libre:.0%} libre", 8, INK3, "end", mono=True))
    return wrap(W, H, "".join(b))


# ═════════ 3. Rythmes valides : 6 jours contre 5 jours
def chart_rythmes():
    J6 = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"]
    J5 = J6[:5]

    def ok(c, ouvres):
        n = len(ouvres); idx = [ouvres.index(j) for j in c]
        return all(any(((d + k) % n) in idx for k in (1, 2)) for d in range(n))
    t6 = [c for c in itertools.combinations(J6, 3) if ok(c, J6)]
    t5 = [c for c in itertools.combinations(J5, 3) if ok(c, J5)]
    W, CW, RH = 700, 44, 20
    TOP1, TOP2 = 62, 62 + 22 + 2 * RH + 40
    H = TOP2 + 22 + len(t5) * RH + 52
    b = [f'<rect width="{W}" height="{H}" fill="{SURF}"/>']
    b.append(txt(0, 15, "Rythmes de passage valides : semaine de 6 jours contre semaine de 5 jours", 11.5, INK, weight="650"))
    b.append(txt(0, 30, "Un rythme est valide si, quel que soit le jour d'appel, un créneau existe à J+1 ou J+2", 8.5, INK3))

    def panneau(y0, jours, trios, titre, sstitre, col):
        LEFT = 176
        b.append(txt(0, y0 + 2, titre, 9.5, INK, weight="700"))
        b.append(txt(0, y0 + 15, sstitre, 8, INK3))
        for j, jour in enumerate(jours):
            b.append(txt(LEFT + j * CW + CW / 2, y0 - 6, jour, 8, INK2, "middle", weight="650"))
        for i, c in enumerate(trios):
            y = y0 + i * RH
            for j, jour in enumerate(jours):
                on = jour in c
                b.append(f'<rect x="{LEFT + j*CW + 3}" y="{y}" width="{CW-7}" height="{RH-5}" rx="3" '
                         f'fill="{col if on else GRID_C}" opacity="{1 if on else .45}"/>')
                if on:
                    b.append(txt(LEFT + j * CW + CW / 2 - 1, y + 11, "●", 7, "#fff", "middle"))
            b.append(txt(W - 6, y + 11, "-".join(c), 8, INK, "end", mono=True, weight="650"))
    panneau(TOP1, J6, t6, "Semaine de 6 jours", f"{len(t6)} rythmes valides sur 20 testés", OK_C)
    yb = TOP1 + len(t6) * RH + 10
    b.append(f'<rect x="0" y="{yb}" width="{W}" height="24" rx="3" fill="{OK_C}" opacity="0.09"/>')
    b.append(txt(10, yb + 16, "Les deux sont disjoints : réunis, ils couvrent les six jours sans qu'un secteur "
                              "n'en réclame deux le même jour.", 8.5, INK, weight="650"))
    panneau(TOP2, J5, t5, "Semaine de 5 jours", f"{len(t5)} rythmes valides sur 10 testés", WARN_C)
    yb2 = TOP2 + len(t5) * RH + 10
    b.append(f'<rect x="0" y="{yb2}" width="{W}" height="36" rx="3" fill="{KO_C}" opacity="0.08"/>')
    b.append(txt(10, yb2 + 15, "Trois jours plus trois jours font six, or la semaine n'en compte que cinq :", 8.5, INK, weight="650"))
    b.append(txt(10, yb2 + 28, "aucune paire n'est disjointe. Deux secteurs d'un même technicien se réclament "
                               "forcément le même jour au moins une fois.", 8.5, INK, weight="650"))
    return wrap(W, H, "".join(b))


if __name__ == "__main__":
    out = {"creneaux": chart_creneaux(), "occupation": chart_occupation(), "rythmes": chart_rythmes()}
    json.dump(out, open('charts_cmp.json', 'w'), ensure_ascii=False)
    for k, v in out.items():
        print(f"{k:<12}{len(v):>7} caractères")
    for nom, sous, td, sav, prod in SCEN:
        print(f"  {nom:<15}{td:>4} j-tech · {sav+prod:>4} créneaux · occupation {DEM/(sav+prod):.1%}")
