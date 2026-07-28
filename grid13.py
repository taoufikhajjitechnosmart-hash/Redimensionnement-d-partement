# -*- coding: utf-8 -*-
import json
JOURS=["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]
CIBLE=json.load(open('sav_reel.json'))                      # SAV/semaine mesuré sur le planning fourni
ZONE={"Blois":"BLOIS","Vendôme":"ZMD","Romorantin-Lanthenay":"ZMD"}
CAD_SAV=lambda s: 7.0 if ZONE.get(s)=="BLOIS" else (6.0 if ZONE.get(s)=="ZMD" else 5.0)
CAD_PROD, CAD_PROD_LOC = 4.0, 5.0
PROD_SEM={"Blois":61.7,"Valencisse":11.1,"Pontlevoy":22.5,"Vendôme":9.8,"Épiais":12.9,
 "Montoire-sur-le-Loir":12.3,"Cormenon":4.9,"Crouy-sur-Cosson":13.3,"Vouzon":8.5,
 "Mur-de-Sologne":12.5,"Romorantin-Lanthenay":11.3,"La Ferté-Imbault":4.5}

def S(sec,n): return (sec,"SAV",n)
def P(sec,n): return (sec,"PROD",n)
L,Ma,Me,J,V,Sa=JOURS
def wk(**kw): return [kw.get(j) for j in JOURS]           # jour -> (matin, aprem) ou None

GRID=[
 ("T1","100 % SAV — Blois + Valencisse",6,
   wk(Lundi=(S("Blois",4),S("Blois",3)), Mardi=(S("Blois",4),S("Valencisse",2)),
      Mercredi=(S("Blois",4),S("Blois",3)), Jeudi=(S("Blois",4),S("Valencisse",2)),
      Vendredi=(S("Blois",4),S("Blois",3)), Samedi=(S("Blois",4),S("Valencisse",2)))),
 ("T2","Blois — mixte SAV / PROD",6,
   wk(Lundi=(P("Blois",2),S("Blois",3)), Mardi=(P("Blois",2),P("Blois",2)),
      Mercredi=(P("Blois",2),S("Blois",3)), Jeudi=(P("Blois",2),P("Blois",2)),
      Vendredi=(P("Blois",2),S("Blois",3)), Samedi=(P("Blois",2),P("Blois",2)))),
 ("T3","Blois — PROD",5, wk(**{d:(P("Blois",2),P("Blois",2)) for d in JOURS[:5]})),
 ("T4","Blois — PROD",5, wk(**{d:(P("Blois",2),P("Blois",2)) for d in JOURS[:5]})),
 ("T5","Sud-Ouest — Pontlevoy",6,
   wk(Lundi=(S("Pontlevoy",3),S("Pontlevoy",2)), Mardi=(S("Pontlevoy",3),P("Pontlevoy",2)),
      Mercredi=(S("Pontlevoy",3),S("Pontlevoy",2)), Jeudi=(S("Pontlevoy",3),P("Pontlevoy",2)),
      Vendredi=(S("Pontlevoy",3),S("Pontlevoy",2)), Samedi=(S("Pontlevoy",3),P("Pontlevoy",2)))),
 ("T6","Sud-Ouest — PROD Pontlevoy / Valencisse",5,
   wk(Lundi=(P("Pontlevoy",2),P("Pontlevoy",2)), Mardi=(P("Valencisse",2),P("Valencisse",2)),
      Mercredi=(P("Pontlevoy",2),P("Pontlevoy",2)), Jeudi=(P("Valencisse",2),P("Valencisse",2)),
      Vendredi=(P("Pontlevoy",2),P("Pontlevoy",2)))),
 ("T7","Nord — Vendôme / Épiais",6,
   wk(Lundi=(S("Vendôme",3),S("Épiais",2)), Mardi=(S("Épiais",3),P("Épiais",2)),
      Mercredi=(S("Vendôme",3),S("Épiais",2)), Jeudi=(S("Épiais",3),P("Épiais",2)),
      Vendredi=(S("Vendôme",3),S("Épiais",1)), Samedi=(P("Épiais",2),P("Épiais",2)))),
 ("T8","Nord — Montoire / Cormenon",6,
   wk(Lundi=(P("Montoire-sur-le-Loir",2),P("Montoire-sur-le-Loir",2)),
      Mardi=(S("Montoire-sur-le-Loir",3),S("Cormenon",2)),
      Mercredi=(P("Montoire-sur-le-Loir",2),P("Cormenon",2)),
      Jeudi=(S("Montoire-sur-le-Loir",3),S("Cormenon",2)),
      Vendredi=(P("Montoire-sur-le-Loir",2),P("Cormenon",2)),
      Samedi=(S("Montoire-sur-le-Loir",2),S("Cormenon",3)))),
 ("T9","Nord — PROD Vendômois / Beauce",5,
   wk(**{d:(P("Vendôme",2),P("Épiais",2)) for d in JOURS[:5]})),
 ("T10","Sologne Est — Crouy / Vouzon",6,
   wk(Lundi=(S("Crouy-sur-Cosson",3),P("Crouy-sur-Cosson",2)), Mardi=(S("Vouzon",3),P("Vouzon",2)),
      Mercredi=(S("Crouy-sur-Cosson",3),P("Crouy-sur-Cosson",2)), Jeudi=(S("Vouzon",2),P("Vouzon",2)),
      Vendredi=(S("Crouy-sur-Cosson",2),P("Crouy-sur-Cosson",2)), Samedi=(S("Vouzon",2),P("Vouzon",2)))),
 ("T11","Sologne Sud — Mur-de-Sologne",6,
   wk(Lundi=(S("Mur-de-Sologne",3),P("Mur-de-Sologne",2)), Mardi=(S("Romorantin-Lanthenay",3),S("La Ferté-Imbault",2)),
      Mercredi=(S("Mur-de-Sologne",3),S("Mur-de-Sologne",1)), Jeudi=(S("Romorantin-Lanthenay",2),S("La Ferté-Imbault",1)),
      Vendredi=(S("Mur-de-Sologne",3),P("Mur-de-Sologne",2)), Samedi=(S("Romorantin-Lanthenay",1),S("La Ferté-Imbault",1)))),
 ("T12","Sologne — PROD",5,
   wk(**{d:(P("Romorantin-Lanthenay",2),P("Mur-de-Sologne",2)) for d in JOURS[:5]})),
 ("T13","Sologne / Val de Loire — PROD",5,
   wk(Lundi=(P("Crouy-sur-Cosson",2),P("Crouy-sur-Cosson",2)),
      Mardi=(P("Mur-de-Sologne",2),P("Romorantin-Lanthenay",2)),
      Mercredi=(P("Crouy-sur-Cosson",2),P("Crouy-sur-Cosson",2)),
      Jeudi=(P("Romorantin-Lanthenay",2),P("La Ferté-Imbault",2)),
      Vendredi=(P("Vouzon",2),P("Vouzon",2)))),
]

sav={}; prod={}; passages={}; charge_tot=0; alertes=[]; td=0
for t,role,nj,sem in GRID:
    for j,day in zip(JOURS,sem):
        if day is None: continue
        td+=1; ch=0
        (s1,t1,n1),(s2,t2,n2)=day
        for k,(sec,typ,n) in enumerate(day):
            if typ=="SAV":
                sav[sec]=sav.get(sec,0)+n; passages.setdefault(sec,set()).add(j)
                ch+=n/CAD_SAV(sec)
            else:
                prod[sec]=prod.get(sec,0)+n
                local = (k==1 and day[0][0]==sec)          # après-midi dans le secteur du matin
                ch+=n/(CAD_PROD_LOC if local else CAD_PROD)
        charge_tot+=ch
        if ch>1.02: alertes.append(f"{t} {j} : charge {ch:.2f}")
print(f"Techniciens : {len(GRID)}  |  jours-technicien : {td}  |  charge totale : {charge_tot:.2f}")
if alertes: print("DEMI-JOURNÉES SURCHARGÉES :", *alertes, sep="\n   ")
else: print("Aucune journée surchargée (toutes ≤ 1,02 j-tech)")

print(f"\n{'Secteur':<23}{'SAV cible':>10}{'SAV grille':>11}{'écart':>7}{'PROD besoin':>12}{'PROD grille':>12}{'passages':>10} rythme")
ok=True
for sec in sorted(CIBLE,key=lambda s:-CIBLE[s]):
    jp=[j for j in JOURS if j in passages.get(sec,())]
    r="L-Me-V" if set(jp)>={"Lundi","Mercredi","Vendredi"} else ("Ma-J-S" if set(jp)>={"Mardi","Jeudi","Samedi"} else "/".join(x[:2] for x in jp))
    ec=sav.get(sec,0)-CIBLE[sec]
    sla=len(jp)>=3 and (set(jp)>={"Lundi","Mercredi","Vendredi"} or set(jp)>={"Mardi","Jeudi","Samedi"} or len(jp)>=5)
    if not sla or ec<0: ok=False
    print(f"{sec:<23}{CIBLE[sec]:>10}{sav.get(sec,0):>11}{ec:>+7}{PROD_SEM[sec]:>12.1f}{prod.get(sec,0):>12}{len(jp):>10} {r}{'' if sla else '   <-- SLA KO'}")
print(f"{'TOTAL':<23}{sum(CIBLE.values()):>10}{sum(sav.values()):>11}{sum(sav.values())-sum(CIBLE.values()):>+7}{sum(PROD_SEM.values()):>12.1f}{sum(prod.values()):>12}")
print("\nSLA J+1/J+2 tenu sur tous les secteurs :", "OUI" if ok else "NON")
print(f"PROD servie en direct : {sum(prod.values())} / {sum(PROD_SEM.values()):.0f} requises -> reste {sum(PROD_SEM.values())-sum(prod.values()):.0f} à récupérer par la bascule J-1")

import math
PTS={"Blois":(47.586,1.336,"X"),"Valencisse":(47.590,1.220,"N"),"Pontlevoy":(47.395,1.256,"S"),
 "Vendôme":(47.793,1.066,"N"),"Épiais":(47.760,1.375,"N"),"Montoire-sur-le-Loir":(47.752,0.866,"N"),
 "Cormenon":(47.955,0.980,"N"),"Crouy-sur-Cosson":(47.680,1.610,"S"),"Vouzon":(47.660,2.020,"S"),
 "Mur-de-Sologne":(47.383,1.612,"S"),"Romorantin-Lanthenay":(47.357,1.744,"S"),"La Ferté-Imbault":(47.395,1.976,"S")}
def dkm(a,b):
    (la1,lo1,r1),(la2,lo2,r2)=PTS[a],PTS[b]
    x=math.radians(lo2-lo1)*math.cos(math.radians((la1+la2)/2)); y=math.radians(la2-la1)
    d=6371*math.hypot(x,y)*1.25
    if r1!=r2 and "X" not in (r1,r2): d+=8
    return round(d)
print("\n--- ENCHAÎNEMENTS MATIN -> APRÈS-MIDI ---")
paires={}
for t,role,nj,sem in GRID:
    for j,day in zip(JOURS,sem):
        if day is None: continue
        a,b=day[0][0],day[1][0]
        if a!=b: paires.setdefault((a,b),[]).append(f"{t} {j[:3]}")
worst=0
for (a,b),qui in sorted(paires.items(),key=lambda x:-dkm(*x[0])):
    d=dkm(a,b); worst=max(worst,d)
    flag="OK" if d<=30 else ("LIMITE" if d<=50 else "INCOHÉRENT")
    print(f"   {a} -> {b:<22} {d:>3} km  {flag:<11} ({', '.join(qui)})")
print(f"   Enchaînement le plus long : {worst} km")

json.dump({'sav':sav,'prod':prod,'pass':{k:sorted(v,key=JOURS.index) for k,v in passages.items()}},
          open('grid13.json','w'),ensure_ascii=False)
