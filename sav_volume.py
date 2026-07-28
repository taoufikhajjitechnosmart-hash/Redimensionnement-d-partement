# -*- coding: utf-8 -*-
import openpyxl, re, json
p='/root/.claude/uploads/f71559d2-3695-58ab-95b7-be0c10466104/c4f3d1cf-Planning_HEBDO_SAV_Departement_41.xlsx'
ws=openpyxl.load_workbook(p,data_only=True)['Planning SAV 41']
JOURS=["Lundi","Mardi","Mercredi","Jeudi","Vendredi"]
NORM={"Montoire":"Montoire-sur-le-Loir","Romorantin":"Romorantin-Lanthenay"}
pat=re.compile(r'^(.*?)\s*(Journée|Matin|Après-midi)\s*[-–]\s*(\d+)\s*cr',re.I)
sav={}; passages={}; td=0.0; detail=[]
for row in ws.iter_rows(min_row=4,max_row=8,values_only=True):
    tech=row[0]; nj=0
    for j,cell in zip(JOURS,row[1:6]):
        if not cell: continue
        nj+=1
        lines=[l.strip() for l in str(cell).split('\n') if l.strip()]
        pending=None                      # secteur annoncé sur la ligne précédente
        for line in lines:
            m=pat.match(line)
            if m:
                sec=m.group(1).strip() or pending   # "Journée - 7 cr" seul -> secteur de la ligne d'avant
                per,n=m.group(2),int(m.group(3))
                sec=NORM.get(sec,sec)
                assert sec, f"secteur introuvable: {tech} {j} {line!r}"
                sav[sec]=sav.get(sec,0)+n
                passages.setdefault(sec,set()).add(j)
                detail.append((tech,j,sec,per,n))
            else:
                pending=line              # ligne ne portant que le nom du secteur
    td+=nj
tot=sum(sav.values())
assert tot==142, tot
print(f"{'Secteur':<24}{'inter/sem':>10}{'inter/mois':>12}{'passages':>10}   jours de passage")
for sec,n in sorted(sav.items(),key=lambda x:-x[1]):
    jp=[j for j in JOURS if j in passages[sec]]
    print(f"{sec:<24}{n:>10}{n*4.3333:>12.0f}{len(jp):>10}   {' · '.join(j[:3] for j in jp)}")
print(f"{'TOTAL DÉPARTEMENT 41':<24}{tot:>10}{tot*4.3333:>12.0f}")
print(f"\nJours-technicien consommés : {td:.0f}/semaine (5 techniciens × 5 jours)")
print(f"Cadence moyenne réalisée   : {tot/td:.2f} interventions SAV / technicien / jour")

TD=5*6+6*5; PROD_TD=46.28
print(f"\n--- DIMENSIONNEMENT ---")
print(f"Charge PROD +10 %            {PROD_TD:>6.2f} j-tech/sem  (185 interventions)")
print(f"Charge SAV (cette grille)    {td:>6.2f} j-tech/sem  ({tot} interventions)")
print(f"TOTAL REQUIS                 {PROD_TD+td:>6.2f} j-tech/sem")
print(f"Disponible à 11 techniciens  {TD:>6.2f} j-tech/sem")
print(f"DÉFICIT                      {PROD_TD+td-TD:>6.2f} j-tech/sem = {(PROD_TD+td-TD)/(TD/11):.2f} ETP")
besoin=PROD_TD+td
print(f"\nEffectif requis : {besoin:.2f} j-tech/sem")
for n in (12,13,14):
    for n6 in range(0,n+1):
        cap=n6*6+(n-n6)*5
        if cap>=besoin:
            print(f"   {n} techniciens dont {n6} à 6 jours -> {cap} j-tech/sem (premier montage suffisant)")
            break
    else: print(f"   {n} techniciens : insuffisant même avec tous à 6 jours ({n*6} j-tech)")
json.dump(sav,open('sav_reel.json','w'),ensure_ascii=False)
