# -*- coding: utf-8 -*-
"""Rythmes valides sur une semaine SAV de 5 jours, et répartition équilibrée des 12 secteurs."""
from itertools import combinations
import json
J5 = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"]
def ok(c, n=5):
    idx = [J5.index(j) for j in c]
    return all(any(((d + k) % n) in idx for k in (1, 2)) for d in range(n))
duos  = [c for c in combinations(J5, 2) if ok(c)]
trios = [c for c in combinations(J5, 3) if ok(c)]
print("SEMAINE SAV DU LUNDI AU VENDREDI")
print(f"  2 passages/semaine : {len(duos)} combinaison(s) valide(s) — aucune ne tient le J+1/J+2")
print(f"  3 passages/semaine : {len(trios)} valides -> " + " · ".join("-".join(x[:3] for x in c) for c in trios))
print("\n  Différence majeure avec la semaine de 6 jours : deux motifs de 3 jours parmi 5 partagent")
print("  toujours au moins un jour (3+3 > 5). Il n'existe donc plus de paire de rythmes disjoints :")
for a, b in combinations(trios, 2):
    inter = set(a) & set(b)
    if len(inter) == 1:
        print(f"    exemple : {'-'.join(x[:3] for x in a)} + {'-'.join(x[:3] for x in b)} -> jour commun {inter.pop()}")
        break
print("  Un technicien couvrant deux secteurs doit donc, le jour commun, en faire un le matin et l'autre l'après-midi.\n")

SAV_DEM = json.load(open('sav_reel.json'))
CLUS = {"Blois":"Blois","Valencisse":"Blois","Pontlevoy":"Sud-Ouest","Vendôme":"Nord","Épiais":"Nord",
        "Montoire-sur-le-Loir":"Nord","Cormenon":"Nord","Crouy-sur-Cosson":"Est","Vouzon":"Est",
        "Mur-de-Sologne":"Sologne Sud","Romorantin-Lanthenay":"Sologne Sud","La Ferté-Imbault":"Sologne Sud"}
autres = [s for s in SAV_DEM if s != "Blois"]

# on cherche l'effectif de chaque motif (x1..x5, somme 11) qui équilibre la charge journalière
best = None
n = len(trios)
def rec(i, rest, xs):
    global best
    if i == n - 1: xs = xs + [rest]; rest = 0
    if rest == 0 and len(xs) == n:
        charge = {j: 1 for j in J5}                       # Blois tous les jours
        for k, t in enumerate(trios):
            for j in t: charge[j] += xs[k]
        e = max(charge.values()) - min(charge.values())
        if best is None or e < best[0]: best = (e, list(xs), dict(charge))
        return
    if len(xs) >= n: return
    for v in range(rest + 1): rec(i + 1, rest - v, xs + [v])
rec(0, len(autres), [])
ecart, xs, charge = best
print(f"Équilibrage de la charge journalière — écart max/min retenu : {ecart}")
print("  secteurs visités par jour :", {j[:3]: v for j, v in charge.items()})
print("  effectif par motif :", {"-".join(x[:3] for x in t): v for t, v in zip(trios, xs)})

# affectation des secteurs aux motifs : les gros volumes d'abord, en évitant d'empiler un cluster sur un seul motif
slots = []
for t, v in zip(trios, xs): slots += [t] * v
slots.sort(key=lambda t: J5.index(t[0]))
plan = {"Blois": tuple(J5)}
restants = sorted(autres, key=lambda s: -SAV_DEM[s])
used_by_clus = {}
for s in restants:
    cl = CLUS[s]
    cand = sorted(range(len(slots)), key=lambda i: (slots[i] in used_by_clus.get(cl, []), i))
    i = cand[0]
    plan[s] = slots.pop(i)
    used_by_clus.setdefault(cl, []).append(plan[s])
print(f"\n{'Secteur':<24}{'cluster':<14}{'rythme SAV':<20}{'SAV dem':>8}")
for s in sorted(plan, key=lambda x: -SAV_DEM[x]):
    print(f"{s:<24}{CLUS[s]:<14}{'-'.join(x[:3] for x in plan[s]):<20}{SAV_DEM[s]:>8}")
dj = 10 + sum(len(plan[s]) for s in autres)
print(f"\nDemi-journées de présence SAV : Blois 10 + autres {dj-10} = {dj}")
json.dump({s: list(v) for s, v in plan.items()}, open('plan5j.json','w'), ensure_ascii=False)
