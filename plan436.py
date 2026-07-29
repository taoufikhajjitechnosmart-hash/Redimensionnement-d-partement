# -*- coding: utf-8 -*-
"""Planification 41 : 11 techniciens · 8 créneaux/jour · 436 créneaux ouverts.
   Le SAV impose le rythme de passage ; la PROD se cale dans ce qui reste."""
import json, math
JOURS=["Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"]
LMV={"Lundi","Mercredi","Vendredi"}; MJS={"Mardi","Jeudi","Samedi"}
CR_JOUR=8; MATIN=4; APREM=4
OCC=0.75                                   # objectif : ne jamais dépasser 75 % d'occupation

SAV_DEM=json.load(open('sav_reel.json'))   # 142/sem, mesuré sur le planning fourni
PROD_DEM={"Blois":61.7,"Pontlevoy":22.5,"Crouy-sur-Cosson":13.3,"Épiais":12.9,"Mur-de-Sologne":12.5,
 "Montoire-sur-le-Loir":12.3,"Romorantin-Lanthenay":11.3,"Valencisse":11.1,"Vendôme":9.8,
 "Vouzon":8.5,"Cormenon":4.9,"La Ferté-Imbault":4.5}
SECT=list(PROD_DEM)
cible={s:(SAV_DEM[s]+PROD_DEM[s])/OCC for s in SECT}
sav_res={s:SAV_DEM[s]/OCC for s in SECT}
print("═══ CIBLE PAR SECTEUR (436 créneaux répartis au prorata de la demande) ═══")
print(f"{'Secteur':<23}{'SAV dem':>8}{'PROD dem':>9}{'total':>7}{'créneaux':>10}{'dont SAV':>9}{'j-tech':>8}")
for s in sorted(SECT,key=lambda x:-cible[x]):
    print(f"{s:<23}{SAV_DEM[s]:>8}{PROD_DEM[s]:>9.1f}{SAV_DEM[s]+PROD_DEM[s]:>7.1f}{cible[s]:>10.0f}{sav_res[s]:>9.0f}{cible[s]/CR_JOUR:>8.2f}")
print(f"{'TOTAL':<23}{sum(SAV_DEM.values()):>8}{sum(PROD_DEM.values()):>9.1f}"
      f"{sum(SAV_DEM.values())+sum(PROD_DEM.values()):>7.1f}{sum(cible.values()):>10.0f}"
      f"{sum(sav_res.values()):>9.0f}{sum(cible.values())/CR_JOUR:>8.2f}")
print(f"\nCapacité 11 techniciens : 60 j-tech × {CR_JOUR} = {60*CR_JOUR} créneaux -> marge {60*CR_JOUR-sum(cible.values()):.0f}")
json.dump({'cible':cible,'sav_res':sav_res,'prod_dem':PROD_DEM,'sav_dem':SAV_DEM},open('cible436.json','w'),ensure_ascii=False)
