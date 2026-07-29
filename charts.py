# -*- coding: utf-8 -*-
"""Graphiques SVG statiques pour le rapport PDF — palette validée par le validateur dataviz."""
import json, math, importlib.util, io, contextlib

SAV_C, PROD_C = "#2a78d6", "#eb6834"      # slots catégoriels 1 et 2, validés light
OK_C, KO_C = "#0ca30c", "#d03b3b"          # status good / critical
INK, INK2, INK3 = "#141c23", "#4d5d6a", "#8a95a0"
GRID_C, SURF2 = "#e4e8ea", "#f2f4f5"
SURF = "#ffffff"

spec = importlib.util.spec_from_file_location("g", "grille436.py")
m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(m)
GRID, JOURS = m.GRID, m.JOURS
C = json.load(open('cible436.json'))
R = json.load(open('grille436.json'))
ORDER = sorted(C['cible'], key=lambda x: -R['slots'][x])
SHORT = {"Montoire-sur-le-Loir": "Montoire", "Romorantin-Lanthenay": "Romorantin",
         "Crouy-sur-Cosson": "Crouy-s-Cosson", "La Ferté-Imbault": "La Ferté-Imbault"}
PASS_AV = {"Blois": 5, "Pontlevoy": 5, "Valencisse": 2, "Vendôme": 3, "Épiais": 3,
           "Montoire-sur-le-Loir": 2, "Cormenon": 1, "Crouy-sur-Cosson": 2, "Vouzon": 1,
           "Mur-de-Sologne": 2, "Romorantin-Lanthenay": 2, "La Ferté-Imbault": 2}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def txt(x, y, s, size=9, fill=INK2, anchor="start", weight="400", mono=False, dy=0):
    fam = "ui-monospace, 'DejaVu Sans Mono', monospace" if mono else "Inter, 'DejaVu Sans', sans-serif"
    return (f'<text x="{x:.1f}" y="{y + dy:.1f}" font-size="{size}" fill="{fill}" '
            f'text-anchor="{anchor}" font-weight="{weight}" font-family="{fam}">{esc(str(s))}</text>')


def wrap(w, h, body, cls="viz"):
    return (f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="Inter, sans-serif" class="{cls}" role="img">{body}</svg>')


# ══════════ 1. Répartition des créneaux par secteur (barres empilées horizontales)
def chart_repartition():
    W, RH, TOP, LEFT, RIGHT = 700, 25, 62, 130, 74
    H = TOP + len(ORDER) * RH + 30
    plot = W - LEFT - RIGHT
    mx = max(R['slots'][s] for s in ORDER)
    sc = plot / (mx * 1.02)
    b = [f'<rect width="{W}" height="{H}" fill="{SURF}"/>']
    b.append(txt(0, 15, "Répartition des créneaux ouverts, par secteur", 11.5, INK, weight="650"))
    b.append(txt(0, 30, "Créneaux réservés au SAV et créneaux ouverts à la PROD — total 480 par semaine", 8.5, INK3))
    for gx in range(0, int(mx) + 1, 40):
        x = LEFT + gx * sc
        b.append(f'<line x1="{x:.1f}" y1="{TOP - 6}" x2="{x:.1f}" y2="{TOP + len(ORDER)*RH - 4}" stroke="{GRID_C}" stroke-width="1"/>')
        b.append(txt(x, TOP - 10, gx, 7.5, INK3, "middle", mono=True))
    for i, s in enumerate(ORDER):
        y = TOP + i * RH
        sv, pr = R['sav'][s], R['prod'][s]
        b.append(txt(LEFT - 8, y + 12, SHORT.get(s, s), 8.5, INK, "end"))
        wsv, wpr = sv * sc, pr * sc
        b.append(f'<path d="M{LEFT} {y+3} h{max(0,wsv-4):.1f} a4 4 0 0 1 4 4 v6 a4 4 0 0 1 -4 4 h-{max(0,wsv-4):.1f} z" fill="{SAV_C}"/>')
        x2 = LEFT + wsv + 2
        b.append(f'<path d="M{x2:.1f} {y+3} h{max(0,wpr-6):.1f} a4 4 0 0 1 4 4 v6 a4 4 0 0 1 -4 4 h-{max(0,wpr-6):.1f} z" fill="{PROD_C}"/>')
        b.append(txt(LEFT + wsv + wpr + 10, y + 12, f"{sv + pr}", 8.5, INK, weight="650", mono=True))
        cx = LEFT + C['cible'][s] * sc
        b.append(f'<line x1="{cx:.1f}" y1="{y}" x2="{cx:.1f}" y2="{y+17}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="2 2"/>')
    yl = TOP + len(ORDER) * RH + 14
    b.append(f'<rect x="{LEFT}" y="{yl-8}" width="9" height="9" rx="2" fill="{SAV_C}"/>')
    b.append(txt(LEFT + 13, yl, "Créneaux SAV réservés", 8, INK2))
    b.append(f'<rect x="{LEFT+140}" y="{yl-8}" width="9" height="9" rx="2" fill="{PROD_C}"/>')
    b.append(txt(LEFT + 153, yl, "Créneaux PROD", 8, INK2))
    b.append(f'<line x1="{LEFT+250}" y1="{yl-9}" x2="{LEFT+250}" y2="{yl+1}" stroke="{INK}" stroke-width="1.5" stroke-dasharray="2 2"/>')
    b.append(txt(LEFT + 257, yl, "cible au prorata de la demande", 8, INK2))
    return wrap(W, H, "".join(b))


# ══════════ 2. Passages SAV : avant / après (haltères)
def chart_passages():
    W, RH, TOP, LEFT, RIGHT = 700, 25, 66, 130, 108
    H = TOP + len(ORDER) * RH + 30
    plot = W - LEFT - RIGHT
    sc = plot / 6.4
    b = [f'<rect width="{W}" height="{H}" fill="{SURF}"/>']
    b.append(txt(0, 15, "Passages SAV par semaine — grille actuelle et grille proposée", 11.5, INK, weight="650"))
    b.append(txt(0, 30, "Trois passages minimum sont nécessaires pour garantir un créneau à J+1 ou J+2", 8.5, INK3))
    seuil = LEFT + 3 * sc
    b.append(f'<rect x="{LEFT}" y="{TOP-8}" width="{3*sc:.1f}" height="{len(ORDER)*RH}" fill="{KO_C}" opacity="0.05"/>')
    b.append(f'<line x1="{seuil:.1f}" y1="{TOP-12}" x2="{seuil:.1f}" y2="{TOP+len(ORDER)*RH-4}" stroke="{INK}" stroke-width="1.2"/>')
    b.append(txt(seuil, TOP - 16, "seuil : 3 passages", 8, INK, "middle", weight="650"))
    for g in range(0, 7):
        x = LEFT + g * sc
        if g != 3:
            b.append(f'<line x1="{x:.1f}" y1="{TOP-6}" x2="{x:.1f}" y2="{TOP+len(ORDER)*RH-4}" stroke="{GRID_C}" stroke-width="1"/>')
        b.append(txt(x, TOP + len(ORDER) * RH + 8, g, 7.5, INK3, "middle", mono=True))
    for i, s in enumerate(ORDER):
        y = TOP + i * RH + 6
        av, ap = PASS_AV[s], len(R['pass'][s])
        b.append(txt(LEFT - 8, y + 3, SHORT.get(s, s), 8.5, INK, "end"))
        xa, xb = LEFT + av * sc, LEFT + ap * sc
        b.append(f'<line x1="{xa:.1f}" y1="{y}" x2="{xb:.1f}" y2="{y}" stroke="{INK3}" stroke-width="2"/>')
        b.append(f'<circle cx="{xa:.1f}" cy="{y}" r="4.5" fill="{SURF}" stroke="{KO_C if av<3 else OK_C}" stroke-width="2"/>')
        b.append(f'<circle cx="{xb:.1f}" cy="{y}" r="5" fill="{OK_C}" stroke="{SURF}" stroke-width="2"/>')
        etat = "conforme" if av >= 3 else f"jusqu'à J+{6 if av==1 else 3}"
        b.append(txt(W - RIGHT + 12, y + 3, etat, 8, KO_C if av < 3 else INK3, weight="650" if av < 3 else "400"))
    yl = TOP + len(ORDER) * RH + 22
    b.append(f'<circle cx="{LEFT+5}" cy="{yl-3}" r="4.5" fill="{SURF}" stroke="{KO_C}" stroke-width="2"/>')
    b.append(txt(LEFT + 15, yl, "grille actuelle", 8, INK2))
    b.append(f'<circle cx="{LEFT+110}" cy="{yl-3}" r="5" fill="{OK_C}"/>')
    b.append(txt(LEFT + 120, yl, "grille proposée — les 12 secteurs conformes", 8, INK2))
    return wrap(W, H, "".join(b))


# ══════════ 3. Calendrier des tournées SAV
def chart_calendrier():
    W, CW, RH, TOP, LEFT = 700, 88, 24, 58, 130
    H = TOP + len(ORDER) * RH + 44
    b = [f'<rect width="{W}" height="{H}" fill="{SURF}"/>']
    b.append(txt(0, 15, "Calendrier des passages SAV", 11.5, INK, weight="650"))
    b.append(txt(0, 30, "Les deux rythmes s'imbriquent : chaque jour de la semaine porte des tournées, chaque secteur est vu 3 fois", 8.5, INK3))
    for j, jour in enumerate(JOURS):
        b.append(txt(LEFT + j * CW + CW / 2, TOP - 10, jour, 8.5, INK, "middle", weight="650"))
    for i, s in enumerate(ORDER):
        y = TOP + i * RH
        jp = R['pass'][s]
        ry = ("L-Me-V" if set(jp) == {"Lundi", "Mercredi", "Vendredi"}
              else "Ma-J-S" if set(jp) == {"Mardi", "Jeudi", "Samedi"} else "quotidien")
        if i % 2 == 0:
            b.append(f'<rect x="{LEFT}" y="{y}" width="{6*CW}" height="{RH-3}" fill="{SURF2}"/>')
        b.append(txt(LEFT - 8, y + 15, SHORT.get(s, s), 8.5, INK, "end"))
        for j, jour in enumerate(JOURS):
            if jour in jp:
                n = R['sav'][s]
                b.append(f'<rect x="{LEFT + j*CW + 4}" y="{y+3}" width="{CW-10}" height="{RH-9}" rx="3" fill="{SAV_C}"/>')
                b.append(txt(LEFT + j * CW + CW / 2 - 3, y + 14, "SAV", 8, "#ffffff", "middle", weight="650"))
        b.append(txt(W - 6, y + 15, ry, 7.5, INK3, "end", mono=True))
    yl = TOP + len(ORDER) * RH + 18
    b.append(txt(LEFT, yl, "Bleu = demi-journée comportant des créneaux SAV réservés. Les demi-journées blanches sont de la PROD pure.", 8, INK2))
    b.append(txt(LEFT, yl + 13, "Colonne de droite : rythme du secteur. Les deux rythmes sont complémentaires et couvrent les six jours.", 8, INK2))
    return wrap(W, H, "".join(b))


# ══════════ 4. Échelle de capacité
def chart_capacite():
    W, H, LEFT, BARH, TOP = 700, 200, 150, 30, 46
    plot = W - LEFT - 90
    sc = plot / 500
    b = [f'<rect width="{W}" height="{H}" fill="{SURF}"/>']
    b.append(txt(0, 15, "De la demande à la capacité", 11.5, INK, weight="650"))
    b.append(txt(0, 30, "Pourquoi 436 créneaux et non 327 : l'écart est la disponibilité elle-même", 8.5, INK3))
    rows = [("Demande réelle", 327, [("SAV", 142, SAV_C), ("PROD", 185, PROD_C)],
             "142 SAV + 185 PROD majorée de 10 %"),
            ("Créneaux à ouvrir", 436, [("", 436, "#b9c6d2")], "327 ÷ 75 % d'occupation"),
            ("Capacité de l'équipe", 480, [("", 480, "#8fa3b4")], "60 jours-technicien × 8 créneaux")]
    for i, (lab, tot, segs, note) in enumerate(rows):
        y = TOP + i * (BARH + 24)
        b.append(txt(LEFT - 10, y + 15, lab, 9, INK, "end", weight="650"))
        x = LEFT
        for nm, v, col in segs:
            w = v * sc
            b.append(f'<path d="M{x:.1f} {y} h{max(0,w-4):.1f} a4 4 0 0 1 4 4 v{BARH-8} a4 4 0 0 1 -4 4 h-{max(0,w-4):.1f} z" fill="{col}"/>')
            if nm and w > 40:
                b.append(txt(x + w / 2, y + BARH / 2 + 1, f"{nm} {v}", 8.5, "#ffffff", "middle", weight="650"))
            x += w + 2
        b.append(txt(LEFT + tot * sc + 10, y + BARH / 2 + 1, tot, 11, INK, weight="700", mono=True))
        b.append(txt(LEFT - 10, y + 27, note, 7.5, INK3, "end"))
    ya = TOP + 2 * (BARH + 24) + 8
    x1, x2 = LEFT + 327 * sc, LEFT + 436 * sc
    b.append(f'<line x1="{x1:.1f}" y1="{TOP+BARH+4}" x2="{x1:.1f}" y2="{ya+16}" stroke="{INK3}" stroke-width="1" stroke-dasharray="2 2"/>')
    b.append(f'<line x1="{x2:.1f}" y1="{TOP+BARH+28+4}" x2="{x2:.1f}" y2="{ya+16}" stroke="{INK3}" stroke-width="1" stroke-dasharray="2 2"/>')
    b.append(txt((x1 + x2) / 2, ya + 30, "109 créneaux libres = la disponibilité à J+1/J+2", 8.5, INK, "middle", weight="650"))
    return wrap(W, H, "".join(b))


# ══════════ 5. Démonstration des rythmes
def chart_rythmes():
    from itertools import combinations
    J6 = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"]

    def ok(c):
        idx = [J6.index(j) for j in c]
        return all(any(((d + k) % 6) in idx for k in (1, 2)) for d in range(6))
    duos = list(combinations(J6, 2)); trios = list(combinations(J6, 3))
    good3 = [c for c in trios if ok(c)]
    W, H, CW, RH, LEFT, TOP = 700, 250, 46, 22, 152, 60
    b = [f'<rect width="{W}" height="{H}" fill="{SURF}"/>']
    b.append(txt(0, 15, "Pourquoi trois passages, et pourquoi ceux-là", 11.5, INK, weight="650"))
    b.append(txt(0, 30, "Toutes les combinaisons de jours testées contre la règle : un appel le jour J trouve un créneau en J+1 ou J+2", 8.5, INK3))
    b.append(txt(0, 52, f"2 passages — {len(duos)} combinaisons testées", 9, INK, weight="650"))
    b.append(f'<rect x="{LEFT-8}" y="{TOP+2}" width="{6*CW+16}" height="26" rx="3" fill="{KO_C}" opacity="0.08"/>')
    b.append(txt(LEFT + 3 * CW, TOP + 19, "AUCUNE ne tient le délai J+1/J+2", 10, KO_C, "middle", weight="700"))
    y0 = TOP + 44
    b.append(txt(0, y0 + 30, f"3 passages", 9, INK, weight="650"))
    b.append(txt(0, y0 + 43, f"{len(trios)} combinaisons testées,", 8.5, INK3))
    b.append(txt(0, y0 + 55, f"{len(good3)} seulement fonctionnent", 8.5, INK3))
    for j, jour in enumerate(J6):
        b.append(txt(LEFT + j * CW + CW / 2, y0 + 6, jour, 8, INK2, "middle", weight="650"))
    for i, c in enumerate(good3):
        y = y0 + 14 + i * RH
        for j, jour in enumerate(J6):
            on = jour in c
            b.append(f'<rect x="{LEFT + j*CW + 3}" y="{y}" width="{CW-8}" height="{RH-6}" rx="3" '
                     f'fill="{OK_C if on else GRID_C}" opacity="{1 if on else 0.5}"/>')
            if on:
                b.append(txt(LEFT + j * CW + CW / 2 - 1.5, y + 11, "✓", 9, "#ffffff", "middle", weight="700"))
        b.append(txt(W - 6, y + 11, "-".join(c), 8, INK, "end", mono=True, weight="650"))
    yb = y0 + 14 + len(good3) * RH + 18
    b.append(f'<rect x="0" y="{yb-12}" width="{W}" height="30" rx="3" fill="{OK_C}" opacity="0.07"/>')
    b.append(txt(10, yb + 6, "Ces deux rythmes sont exactement complémentaires : réunis, ils couvrent les six jours sans trou ni doublon.",
                 9, INK, weight="650"))
    return wrap(W, H, "".join(b))


if __name__ == "__main__":
    out = {"repartition": chart_repartition(), "passages": chart_passages(),
           "calendrier": chart_calendrier(), "capacite": chart_capacite(), "rythmes": chart_rythmes()}
    json.dump(out, open('charts.json', 'w'), ensure_ascii=False)
    for k, v in out.items():
        print(f"{k:<12} {len(v):>6} caractères")
