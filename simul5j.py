# -*- coding: utf-8 -*-
"""Deux simulations avec SAV du lundi au vendredi.
   A : PROD du lundi au samedi (5 techniciens à 6 jours)   -> 60 j-tech, 480 créneaux
   B : tout le monde du lundi au vendredi                  -> 55 j-tech, 440 créneaux"""
import json, math, itertools

J5 = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
JOURS = J5 + ["Samedi"]
CR_JOUR, DEMI = 8, 4
OCC = 0.75

SAV_DEM = json.load(open('sav_reel.json'))
PROD_DEM = {"Blois": 61.7, "Pontlevoy": 22.5, "Crouy-sur-Cosson": 13.3, "Épiais": 12.9,
            "Mur-de-Sologne": 12.5, "Montoire-sur-le-Loir": 12.3, "Romorantin-Lanthenay": 11.3,
            "Valencisse": 11.1, "Vendôme": 9.8, "Vouzon": 8.5, "Cormenon": 4.9, "La Ferté-Imbault": 4.5}
CLUS = {"Blois": "Blois", "Valencisse": "Blois", "Pontlevoy": "Sud-Ouest", "Vendôme": "Nord",
        "Épiais": "Nord", "Montoire-sur-le-Loir": "Nord", "Cormenon": "Nord",
        "Crouy-sur-Cosson": "Est", "Vouzon": "Est", "Mur-de-Sologne": "Sologne Sud",
        "Romorantin-Lanthenay": "Sologne Sud", "La Ferté-Imbault": "Sologne Sud"}
PTS = {"Blois": (47.586, 1.336, "X"), "Valencisse": (47.590, 1.220, "N"), "Pontlevoy": (47.395, 1.256, "S"),
       "Vendôme": (47.793, 1.066, "N"), "Épiais": (47.760, 1.375, "N"), "Montoire-sur-le-Loir": (47.752, 0.866, "N"),
       "Cormenon": (47.955, 0.980, "N"), "Crouy-sur-Cosson": (47.680, 1.610, "S"), "Vouzon": (47.660, 2.020, "S"),
       "Mur-de-Sologne": (47.383, 1.612, "S"), "Romorantin-Lanthenay": (47.357, 1.744, "S"),
       "La Ferté-Imbault": (47.395, 1.976, "S")}


BASE = {"Blois": "Blois", "Nord": "Vendôme", "Sologne Sud": "Romorantin-Lanthenay",
        "Sud-Ouest": "Pontlevoy", "Est": "Crouy-sur-Cosson"}
RAYON = 40


def km(a, b):
    (a1, o1, r1), (a2, o2, r2) = PTS[a], PTS[b]
    x = math.radians(o2 - o1) * math.cos(math.radians((a1 + a2) / 2))
    y = math.radians(a2 - a1)
    d = 6371 * math.hypot(x, y) * 1.25
    return round(d + 8 if r1 != r2 and "X" not in (r1, r2) else d)


# ── rythmes SAV : Blois tous les jours, les autres sur un motif de 3 jours valide ──
def valide(c):
    idx = [J5.index(j) for j in c]
    return all(any(((d + k) % 5) in idx for k in (1, 2)) for d in range(5))


TRIOS = [c for c in itertools.combinations(J5, 3) if valide(c)]
# choisi à la main pour que chaque cluster soit géographiquement tenable jour par jour
PLAN = {
    "Blois":                tuple(J5),
    "Valencisse":           ("Mardi", "Mercredi", "Vendredi"),
    "Pontlevoy":            ("Lundi", "Mercredi", "Vendredi"),
    "Vendôme":              ("Lundi", "Mercredi", "Vendredi"),
    "Épiais":               ("Lundi", "Mercredi", "Jeudi"),
    "Montoire-sur-le-Loir": ("Mardi", "Jeudi", "Vendredi"),
    "Cormenon":             ("Mardi", "Jeudi", "Vendredi"),
    "Crouy-sur-Cosson":     ("Lundi", "Mercredi", "Vendredi"),
    "Vouzon":               ("Mardi", "Jeudi", "Vendredi"),
    "Mur-de-Sologne":       ("Lundi", "Mercredi", "Jeudi"),
    "Romorantin-Lanthenay": ("Mardi", "Jeudi", "Vendredi"),
    "La Ferté-Imbault":     ("Mardi", "Mercredi", "Vendredi"),
}
for s, p in PLAN.items():
    assert s == "Blois" or tuple(p) in TRIOS, f"{s}: rythme {p} invalide"

# ── créneaux SAV réservés par passage ──
# une demi-journée ne contient que 4 créneaux : la réservation SAV y est plafonnée.
# Les secteurs qui demandent plus de 4 créneaux par passage occupent les deux demi-journées.
SAV_RES = {s: min(DEMI, max(2, round(SAV_DEM[s] / OCC / len(PLAN[s])))) for s in SAV_DEM}

# ══════════════════ construction d'une simulation ══════════════════
def build(nom, samedi_prod, techs):
    """techs = liste (id, cluster, jours)"""
    grille = {t[0]: {j: [None, None] for j in JOURS} for t in techs}
    dispo = {t[0]: (JOURS if (samedi_prod and t[2] == 6) else J5) for t in techs}
    # 1) demi-journées SAV, jour par jour, groupées par proximité
    for j in J5:
        besoin = [s for s in PLAN if j in PLAN[s]]
        besoin.sort(key=lambda x: -SAV_DEM[x])
        # Blois occupe les deux demi-journées de son référent tant que sa demande n'est pas couverte
        for t, cl, nj in techs:
            if not besoin:
                break
            cands = [x for x in besoin if CLUS[x] == cl]
            if not cands:
                continue
            a = cands[0]
            grille[t][j][0] = (a, SAV_RES[a], 0)
            besoin.remove(a)
            proches = [x for x in besoin if CLUS[x] == cl and km(a, x) <= 30]
            if proches:
                b = proches[0]
            elif a == "Blois" and j != "Jeudi":
                b = "Blois"                      # Blois aussi l'après-midi (sauf jeudi)
            else:
                b = None
            if b:
                grille[t][j][1] = (b, SAV_RES[b], 0)
                if b in besoin:
                    besoin.remove(b)
        assert not besoin, f"{nom} — {j} : secteurs SAV non placés {besoin}"
    # 1bis) compléter le SAV des secteurs encore sous leur demande, sur les jours de leur rythme
    def sav_total(x):
        return sum(c[1] for t, cl, nj in techs for j in dispo[t]
                   for c in grille[t][j] if c and c[0] == x)
    for x in sorted(SAV_DEM, key=lambda y: -SAV_DEM[y]):
        for t, cl, nj in techs:
            if CLUS[x] != cl:
                continue
            for j in PLAN[x]:
                if sav_total(x) >= SAV_DEM[x]:
                    break
                for k in (1, 0):
                    if grille[t][j][k] is None:
                        autre = grille[t][j][1 - k]
                        if autre and autre[0] != x and km(autre[0], x) > 30:
                            continue
                        grille[t][j][k] = (x, SAV_RES[x], 0)
                        break
    # 2) PROD : on comble en visant le secteur le plus en retard, dans un rayon de 40 km de la base
    reste = dict(PROD_DEM)
    cases = [(t, cl, j, k) for t, cl, nj in techs for j in dispo[t] for k in (0, 1)
             if grille[t][j][k] is None]
    for t, cl, j, k in cases:
        voisin = grille[t][j][1 - k]
        base = BASE[cl]
        pool = [x for x in PROD_DEM if km(base, x) <= RAYON]
        if voisin:
            pool = [x for x in pool if x == voisin[0] or km(x, voisin[0]) <= 30] or [voisin[0]]
        x = max(pool, key=lambda y: reste.get(y, 0))
        grille[t][j][k] = (x, 0, DEMI)
        reste[x] = reste.get(x, 0) - DEMI
    # 3) rééquilibrage : on prend une demi-journée à un secteur en excédent pour un secteur en déficit
    def prod_total(x):
        return sum(c[2] for t, cl, nj in techs for j in dispo[t]
                   for c in grille[t][j] if c and c[0] == x)
    for _ in range(40):
        deficit = [x for x in PROD_DEM if prod_total(x) < PROD_DEM[x]]
        if not deficit:
            break
        x = max(deficit, key=lambda y: PROD_DEM[y] - prod_total(y))
        pris = False
        for t, cl, nj in techs:
            if pris:
                break
            for j in dispo[t]:
                for k in (0, 1):
                    c = grille[t][j][k]
                    if not c or c[1] or c[0] == x:
                        continue                       # on ne touche jamais au SAV
                    if prod_total(c[0]) - DEMI < PROD_DEM[c[0]]:
                        continue                       # ne pas créer un nouveau déficit
                    autre = grille[t][j][1 - k]
                    if autre and autre[0] != x and km(autre[0], x) > 30:
                        continue
                    if km(BASE[cl], x) > RAYON:
                        continue
                    grille[t][j][k] = (x, 0, DEMI)
                    pris = True
                    break
                if pris:
                    break
        if not pris:
            # échange d'une journée entière : utile quand la demi-journée est bloquée
            # par la distance avec l'autre demi-journée (ex. Épiais → Montoire, 48 km)
            for t, cl, nj in techs:
                if pris or km(BASE[cl], x) > RAYON:
                    continue
                for j in dispo[t]:
                    d = grille[t][j]
                    if any(c is None or c[1] for c in d):
                        continue                        # journée incomplète ou contenant du SAV
                    if d[0][0] != d[1][0] or d[0][0] == x:
                        continue                        # journée mono-secteur uniquement
                    src = d[0][0]
                    if prod_total(src) - 2 * DEMI < PROD_DEM[src]:
                        continue
                    grille[t][j] = [(x, 0, DEMI), (x, 0, DEMI)]
                    pris = True
                    break
        if not pris:
            break
    return grille, dispo


def verifier(nom, grille, dispo, techs):
    sav, prod, slots, passages = {}, {}, {}, {}
    td = 0
    liens = {}
    for t, cl, nj in techs:
        for j in dispo[t]:
            td += 1
            d = grille[t][j]
            if d[0] and d[1] and d[0][0] != d[1][0]:
                liens.setdefault((d[0][0], d[1][0]), []).append(f"{t} {j[:3]}")
            for cell in d:
                if cell is None:
                    continue
                s, a, p = cell
                slots[s] = slots.get(s, 0) + a + p
                sav[s] = sav.get(s, 0) + a
                prod[s] = prod.get(s, 0) + p
                if a:
                    passages.setdefault(s, set()).add(j)
    for t, cl, nj in techs:
        for j in dispo[t]:
            n = sum((c[1] + c[2]) for c in grille[t][j] if c)
            assert n <= CR_JOUR, f"{nom} — {t} {j} : {n} créneaux (max {CR_JOUR})"
    print("═" * 118)
    print(f"{nom}")
    print("═" * 118)
    print(f"{'Secteur':<23}{'rythme SAV':<18}{'pass':>5}{'SAV ouv':>9}{'SAV dem':>9}"
          f"{'PROD ouv':>10}{'PROD dem':>10}{'total':>7}{'SLA':>6}{'SAV':>5}{'PROD':>6}")
    ko = []
    for s in sorted(slots, key=lambda x: -slots[x]):
        jp = passages.get(s, set())
        a = len(jp) >= 3 and (s == "Blois" or tuple(sorted(jp, key=J5.index)) in TRIOS)
        b = sav.get(s, 0) >= SAV_DEM[s]
        c = prod.get(s, 0) >= PROD_DEM[s]
        if not (a and b and c):
            ko.append(s)
        print(f"{s:<23}{'-'.join(x[:3] for x in sorted(jp, key=J5.index)):<18}{len(jp):>5}"
              f"{sav.get(s,0):>9}{SAV_DEM[s]:>9}{prod.get(s,0):>10}{PROD_DEM[s]:>10.1f}{slots[s]:>7}"
              f"{'OK' if a else 'NON':>6}{'OK' if b else 'NON':>5}{'OK' if c else 'NON':>6}")
    ts, tp = sum(sav.values()), sum(prod.values())
    print(f"{'TOTAL':<23}{'':<18}{'':>5}{ts:>9}{sum(SAV_DEM.values()):>9}{tp:>10}{sum(PROD_DEM.values()):>10.1f}{ts+tp:>7}")
    besoin = (sum(SAV_DEM.values()) + sum(PROD_DEM.values())) / OCC
    print(f"\n  jours-technicien {td} · créneaux ouverts {ts+tp} · à ouvrir pour 75 % d'occupation {besoin:.0f}"
          f" · réserve {ts+tp-besoin:+.0f}")
    pire = max((km(a, b) for a, b in liens), default=0)
    print(f"  enchaînements matin→après-midi : {len(liens)} · le plus long {pire} km")
    for (a, b), q in sorted(liens.items(), key=lambda x: -km(*x[0]))[:4]:
        print(f"      {a} → {b} : {km(a,b)} km  ({', '.join(q[:4])}{'…' if len(q)>4 else ''})")
    print(f"  secteurs en défaut : {ko if ko else 'aucun — 12/12 conformes'}")
    return dict(nom=nom, td=td, sav=ts, prod=tp, total=ts + tp, besoin=besoin,
                ko=ko, pire=pire, grille=grille, dispo=dispo, passages={k: sorted(v, key=J5.index) for k, v in passages.items()},
                sav_sec=sav, prod_sec=prod, slots=slots)


# affectation des techniciens aux clusters, au prorata de la demande totale de chaque cluster
# (Blois 20,1 j-tech · Nord 12,5 · Sologne Sud 8,1 · Sud-Ouest 7,8 · Est 6,1)
# Est reçoit 2 techniciens malgré son faible volume : Crouy et Vouzon sont distants de 38 km
# et leurs rythmes se chevauchent forcément sur une semaine de 5 jours.
TECHS_A = [("T1", "Blois", 5), ("T2", "Nord", 6), ("T3", "Sologne Sud", 6), ("T4", "Est", 6),
           ("T5", "Sud-Ouest", 6), ("T6", "Blois", 6), ("T7", "Blois", 5), ("T8", "Nord", 5),
           ("T9", "Sologne Sud", 5), ("T10", "Nord", 5), ("T11", "Est", 5)]
TECHS_B = [(t, c, 5) for t, c, n in TECHS_A]

res = []
for nom, sam, techs in (("SIMULATION A — SAV du lundi au vendredi, PROD jusqu'au samedi (5 techniciens à 6 jours)", True, TECHS_A),
                        ("SIMULATION B — tout le monde du lundi au vendredi (11 techniciens à 5 jours)", False, TECHS_B)):
    g, d = build(nom, sam, techs)
    res.append(verifier(nom, g, d, techs))
    print()

export = {}
for r, (lab, techs) in zip(res, (("A", TECHS_A), ("B", TECHS_B))):
    export[lab] = dict(nom=r['nom'], td=r['td'], sav=r['sav'], prod=r['prod'], total=r['total'],
                       besoin=round(r['besoin']), pire=r['pire'], ko=r['ko'],
                       capacite=r['td'] * CR_JOUR,
                       occupation=round((sum(SAV_DEM.values()) + sum(PROD_DEM.values())) / r['total'], 4),
                       sav_sec=r['sav_sec'], prod_sec=r['prod_sec'], slots=r['slots'],
                       passages=r['passages'], plan={k: list(v) for k, v in PLAN.items()},
                       techs=[list(t) for t in techs],
                       grille={t: {j: [list(c) if c else None for c in r['grille'][t][j]]
                                   for j in r['dispo'][t]} for t, cl, nj in techs})
json.dump(export, open('simul5j.json', 'w'), ensure_ascii=False)
print("═" * 118)
print("COMPARAISON")
print("═" * 118)
base = {"nom": "Base (SAV 6 jours)", "td": 60, "total": 480, "besoin": 436, "pire": 30}
print(f"{'Scénario':<52}{'j-tech':>8}{'créneaux':>10}{'à ouvrir':>10}{'réserve':>9}{'défauts':>9}")
print(f"{'Base — SAV du lundi au samedi':<52}{60:>8}{480:>10}{436:>10}{'+44':>9}{'aucun':>9}")
for r in res:
    lab = r['nom'].split(' — ')[0] + " — " + r['nom'].split(' — ')[1][:34]
    print(f"{lab:<52}{r['td']:>8}{r['total']:>10}{r['besoin']:>10.0f}{r['total']-r['besoin']:>+9.0f}"
          f"{(len(r['ko']) or 'aucun'):>9}")
