# -*- coding: utf-8 -*-
"""Pivote la grille par secteur : planning SAV, planning PROD, contrôle."""
import json, importlib.util, io, contextlib
spec = importlib.util.spec_from_file_location("g", "grille436.py")
m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(m)
GRID, JOURS = m.GRID, m.JOURS
C = json.load(open('cible436.json')); R = json.load(open('grille436.json'))
ORDER = sorted(C['cible'], key=lambda x: -R['slots'][x])
PER = ["matin", "après-midi"]

# secteur -> jour -> période -> [(tech, sav, prod)]
piv = {s: {j: {p: [] for p in PER} for j in JOURS} for s in C['cible']}
for t, role, nj, sem in GRID:
    for j, day in zip(JOURS, sem):
        if day is None: continue
        for k, (sec, sav, prod) in enumerate(day):
            piv[sec][j][PER[k]].append((t, sav, prod))

def cellule(sec, j, p, typ):
    """typ = 'sav' | 'prod' -> texte de la cellule"""
    out = []
    for t, sav, prod in piv[sec][j][p]:
        n = sav if typ == 'sav' else prod
        if n: out.append(f"{t}:{n}")
    return " ".join(out)

def total(sec, typ):
    return sum((sav if typ == 'sav' else prod)
               for j in JOURS for p in PER for t, sav, prod in piv[sec][j][p])

for typ, titre in (('sav', "TABLEAU 1 — PLANNING SAV PAR SECTEUR (créneaux réservés)"),
                   ('prod', "TABLEAU 2 — PLANNING PROD PAR SECTEUR (créneaux ouverts)")):
    print("═" * 132); print(titre); print("═" * 132)
    print(f"{'Secteur':<22}" + "".join(f"{j[:3]+' m':>9}{j[:3]+' am':>9}" for j in JOURS) + f"{'TOTAL':>8}{'DEM.':>7}")
    for s in ORDER:
        line = f"{s:<22}"
        for j in JOURS:
            for p in PER:
                line += f"{cellule(s, j, p, typ) or '·':>9}"
        dem = C['sav_dem'][s] if typ == 'sav' else round(C['prod_dem'][s], 1)
        line += f"{total(s, typ):>8}{dem:>7}"
        print(line)
    tt = sum(total(s, typ) for s in ORDER)
    dd = sum(C['sav_dem'].values()) if typ == 'sav' else round(sum(C['prod_dem'].values()), 1)
    print(f"{'TOTAL':<22}" + " " * (12 * 9) + f"{tt:>8}{dd:>7}")
    print()

print("═" * 132); print("TABLEAU 3 — CONTRÔLE PAR SECTEUR"); print("═" * 132)
print(f"{'Secteur':<22}{'passages':>9}{'rythme':>9}{'SAV rés':>9}{'SAV dem':>9}{'PROD ouv':>10}{'PROD dem':>10}"
      f"{'total':>7}{'cible':>7}{'J+1/J+2':>9}{'SAV ok':>8}{'PROD ok':>9}")
alertes = []
for s in ORDER:
    jp = R['pass'][s]
    ry = ("L-Me-V" if set(jp) == {"Lundi","Mercredi","Vendredi"}
          else "Ma-J-S" if set(jp) == {"Mardi","Jeudi","Samedi"} else "quotid.")
    sv, pr = total(s, 'sav'), total(s, 'prod')
    a = len(jp) >= 3; b = sv >= C['sav_dem'][s]; c = pr >= C['prod_dem'][s]
    if not (a and b and c): alertes.append(s)
    print(f"{s:<22}{len(jp):>9}{ry:>9}{sv:>9}{C['sav_dem'][s]:>9}{pr:>10}{round(C['prod_dem'][s],1):>10}"
          f"{sv+pr:>7}{round(C['cible'][s]):>7}{'OK' if a else 'NON':>9}{'OK' if b else 'NON':>8}{'OK' if c else 'NON':>9}")
sv_t = sum(total(s,'sav') for s in ORDER); pr_t = sum(total(s,'prod') for s in ORDER)
print(f"{'TOTAL':<22}{'':>9}{'':>9}{sv_t:>9}{142:>9}{pr_t:>10}{185.3:>10}{sv_t+pr_t:>7}{436:>7}")
print(f"\nSecteurs en défaut : {alertes if alertes else 'aucun — 12/12 conformes'}")

# cohérence croisée avec la grille par technicien
print("\n── Contrôle de cohérence avec la grille par technicien ──")
gs = sum(sav for t,ro,nj,sem in GRID for day in sem if day for sec,sav,prod in day)
gp = sum(prod for t,ro,nj,sem in GRID for day in sem if day for sec,sav,prod in day)
print(f"  SAV  : pivot secteur {sv_t}  |  grille technicien {gs}  ->  {'identique' if sv_t==gs else 'ÉCART !'}")
print(f"  PROD : pivot secteur {pr_t}  |  grille technicien {gp}  ->  {'identique' if pr_t==gp else 'ÉCART !'}")
json.dump({'piv': {s: {j: {p: piv[s][j][p] for p in PER} for j in JOURS} for s in C['cible']}},
          open('pivot.json','w'), ensure_ascii=False)
