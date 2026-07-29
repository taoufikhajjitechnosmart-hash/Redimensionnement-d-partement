# -*- coding: utf-8 -*-
"""41 · 11 techniciens · 8 créneaux/jour (matin 4 + après-midi 4).
   Demi-journée = (secteur, créneaux SAV réservés, créneaux PROD)."""
import json, math
JOURS=["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]
C=json.load(open('cible436.json'))
def D(sec,sav,prod): return (sec,sav,prod)
B,V,P,VD,E,M,CO,CR,VZ,MU,RO,LF = ("Blois","Valencisse","Pontlevoy","Vendôme","Épiais",
 "Montoire-sur-le-Loir","Cormenon","Crouy-sur-Cosson","Vouzon","Mur-de-Sologne",
 "Romorantin-Lanthenay","La Ferté-Imbault")
def wk(**k): return [k.get(j) for j in JOURS]
GRID=[
 ("T1","100 % SAV — Blois (L-Me-V) · Valencisse (Ma-J-S)",6,
  wk(Lundi=(D(B,4,0),D(B,4,0)), Mardi=(D(V,3,1),D(V,0,4)), Mercredi=(D(B,4,0),D(B,4,0)),
     Jeudi=(D(V,3,1),D(V,0,4)), Vendredi=(D(B,4,0),D(B,4,0)), Samedi=(D(V,3,1),D(V,0,4)))),
 ("T2","Nord — Vendôme+Épiais (L-Me-V) · Montoire+Cormenon (Ma-J-S)",6,
  wk(Lundi=(D(VD,4,0),D(E,4,0)), Mardi=(D(M,4,0),D(CO,3,1)), Mercredi=(D(VD,4,0),D(E,4,0)),
     Jeudi=(D(M,4,0),D(CO,3,1)), Vendredi=(D(VD,4,0),D(E,3,1)), Samedi=(D(M,3,1),D(CO,3,1)))),
 ("T3","Sologne Sud — Mur (L-Me-V) · Romorantin+La Ferté (Ma-J-S)",6,
  wk(Lundi=(D(MU,4,0),D(MU,1,3)), Mardi=(D(RO,3,1),D(LF,2,2)), Mercredi=(D(MU,4,0),D(MU,1,3)),
     Jeudi=(D(RO,3,1),D(LF,2,2)), Vendredi=(D(MU,4,0),D(MU,1,3)), Samedi=(D(RO,2,2),D(LF,1,3)))),
 ("T4","Sologne Est — Crouy (L-Me-V) · Vouzon (Ma-J-S)",6,
  wk(Lundi=(D(CR,4,0),D(CR,0,4)), Mardi=(D(VZ,3,1),D(VZ,0,4)), Mercredi=(D(CR,4,0),D(CR,0,4)),
     Jeudi=(D(VZ,3,1),D(VZ,0,4)), Vendredi=(D(CR,3,1),D(CR,0,4)), Samedi=(D(VZ,3,1),D(VZ,0,4)))),
 ("T5","Sud-Ouest — Pontlevoy (SAV L-Me-V · PROD Ma-J-S)",6,
  wk(Lundi=(D(P,4,0),D(P,4,0)), Mardi=(D(P,0,4),D(P,0,4)), Mercredi=(D(P,4,0),D(P,4,0)),
     Jeudi=(D(P,0,4),D(P,0,4)), Vendredi=(D(P,4,0),D(P,4,0)), Samedi=(D(P,0,4),D(P,0,4)))),
 ("T6","Blois — mixte SAV / PROD",5, wk(**{j:(D(B,4,0),D(B,0,4)) for j in JOURS[:5]})),
 ("T7","Blois — PROD",5, wk(**{j:(D(B,0,4),D(B,0,4)) for j in JOURS[:5]})),
 ("T8","Blois — PROD",5, wk(**{j:(D(B,0,4),D(B,0,4)) for j in JOURS[:5]})),
 ("T9","Nord — PROD Vendômois / Beauce",5,
  wk(Lundi=(D(VD,0,4),D(E,0,4)), Mardi=(D(M,0,4),D(CO,0,4)), Mercredi=(D(VD,0,4),D(E,0,4)),
     Jeudi=(D(E,0,4),D(E,0,4)), Vendredi=(D(M,0,4),D(M,0,4)))),
 ("T10","Sologne / Sud-Ouest — PROD",5,
  wk(Lundi=(D(RO,0,4),D(MU,0,4)), Mardi=(D(P,0,4),D(P,0,4)), Mercredi=(D(RO,0,4),D(MU,0,4)),
     Jeudi=(D(P,0,4),D(P,0,4)), Vendredi=(D(RO,0,4),D(LF,0,4)))),
 ("T11","Renfort flottant — réserve opérationnelle",5,
  wk(Lundi=(D(B,0,4),D(B,0,4)), Mardi=(D(E,0,4),D(VD,0,4)), Mercredi=(D(B,0,4),D(B,0,4)),
     Jeudi=(D(M,0,4),D(M,0,4)), Vendredi=(D(CR,0,4),D(CR,0,4)))),
]
# ═════════ VÉRIFICATION ═════════
def sla_ok(jours, n_ouvres):
    """un appel le jour d trouve-t-il un créneau SAV en d+1 ou d+2 ?"""
    idx=[JOURS.index(j) for j in jours]
    return all(any(((d+k)%n_ouvres) in idx for k in (1,2)) for d in range(n_ouvres))
N_OUVRES=6
sav={};prod={};slots={};passages={};td=0;al=[]
for t,role,nj,sem in GRID:
    n=0
    for j,day in zip(JOURS,sem):
        if day is None: continue
        n+=1
        if sum(x[1]+x[2] for x in day)!=8: al.append(f"{t} {j}: {sum(x[1]+x[2] for x in day)} créneaux")
        for sec,sv,pr in day:
            slots[sec]=slots.get(sec,0)+sv+pr; sav[sec]=sav.get(sec,0)+sv; prod[sec]=prod.get(sec,0)+pr
            if sv: passages.setdefault(sec,set()).add(j)
    if n!=nj: al.append(f"{t}: {n} jours ≠ {nj}")
    td+=n
n6=sum(1 for _,_,nj,_ in GRID if nj==6)
print(f"11 techniciens ({n6} à 6 jours + {len(GRID)-n6} à 5 jours) · {td} jours-technicien · {sum(slots.values())} créneaux")
if al: print("ALERTES :",*al,sep="\n  ")
print(f"\n{'Secteur':<23}{'créneaux':>9}{'cible':>7}{'SAV rés':>8}{'SAV dem':>8}{'PROD':>6}{'dem':>7}{'pass':>5}  jours SAV")
ok=True
for s in sorted(C['cible'],key=lambda x:-C['cible'][x]):
    jp=passages.get(s,set()); v=sla_ok(jp,N_OUVRES)
    a=sav.get(s,0)>=C['sav_dem'][s]; b=prod.get(s,0)>=C['prod_dem'][s]
    if not(v and a and b): ok=False
    fl=("" if v else " SLA!")+("" if a else " SAV<dem!")+("" if b else " PROD<dem!")
    print(f"{s:<23}{slots.get(s,0):>9}{C['cible'][s]:>7.0f}{sav.get(s,0):>8}{C['sav_dem'][s]:>8}"
          f"{prod.get(s,0):>6}{C['prod_dem'][s]:>7.1f}{len(jp):>5}  {'-'.join(x[:3] for x in sorted(jp,key=JOURS.index))}{fl}")
print(f"{'TOTAL':<23}{sum(slots.values()):>9}{sum(C['cible'].values()):>7.0f}{sum(sav.values()):>8}"
      f"{sum(C['sav_dem'].values()):>8}{sum(prod.values()):>6}{sum(C['prod_dem'].values()):>7.1f}")
PTS={"Blois":(47.586,1.336,"X"),"Valencisse":(47.590,1.220,"N"),"Pontlevoy":(47.395,1.256,"S"),
 "Vendôme":(47.793,1.066,"N"),"Épiais":(47.760,1.375,"N"),"Montoire-sur-le-Loir":(47.752,0.866,"N"),
 "Cormenon":(47.955,0.980,"N"),"Crouy-sur-Cosson":(47.680,1.610,"S"),"Vouzon":(47.660,2.020,"S"),
 "Mur-de-Sologne":(47.383,1.612,"S"),"Romorantin-Lanthenay":(47.357,1.744,"S"),"La Ferté-Imbault":(47.395,1.976,"S")}
def km(a,b):
    (a1,o1,r1),(a2,o2,r2)=PTS[a],PTS[b]
    x=math.radians(o2-o1)*math.cos(math.radians((a1+a2)/2)); y=math.radians(a2-a1)
    v=6371*math.hypot(x,y)*1.25
    return round(v+8 if r1!=r2 and "X" not in (r1,r2) else v)
pa={}
for t,role,nj,sem in GRID:
    for j,day in zip(JOURS,sem):
        if day and day[0][0]!=day[1][0]: pa.setdefault((day[0][0],day[1][0]),[]).append(f"{t} {j[:3]}")
print("\nEnchaînements matin -> après-midi :"); worst=0
for (a,b),q in sorted(pa.items(),key=lambda x:-km(*x[0])):
    worst=max(worst,km(a,b)); print(f"   {a} -> {b:<24}{km(a,b):>4} km  ({', '.join(q)})")
print(f"\nSLA J+1/J+2 · SAV couvert · PROD couverte · trajets ≤30 km : {'TOUT OK' if ok and not al and worst<=30 else 'NON — voir ci-dessus'} (max {worst} km)")
json.dump({'sav':sav,'prod':prod,'slots':slots,'grid':[(t,r,nj,[list(map(list,d)) if d else None for d in s]) for t,r,nj,s in GRID],
           'pass':{k:sorted(v,key=JOURS.index) for k,v in passages.items()}},open('grille436.json','w'),ensure_ascii=False)
