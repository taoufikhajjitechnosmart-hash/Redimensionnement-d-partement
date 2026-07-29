# -*- coding: utf-8 -*-
"""Classeur de planification 41 — 11 techniciens, 8 créneaux/jour, 436 créneaux ouverts."""
import openpyxl, json, math, importlib.util, io, contextlib
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

spec = importlib.util.spec_from_file_location("g", "grille436.py")
m = importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):
    spec.loader.exec_module(m)
GRID, JOURS = m.GRID, m.JOURS
C = json.load(open('cible436.json'))
R = json.load(open('grille436.json'))

F = "Arial"
BLK = Font(name=F, size=10); BOLD = Font(name=F, size=10, bold=True)
BLUE = Font(name=F, size=10, color="0000FF"); GRN = Font(name=F, size=10, color="008000")
SUB = Font(name=F, size=9, italic=True, color="595959")
TIT = Font(name=F, size=14, bold=True, color="1F3864")
H1 = Font(name=F, size=10, bold=True, color="FFFFFF"); WHT = Font(name=F, size=10, bold=True, color="FFFFFF")
SEC_TIT = Font(name=F, size=11, bold=True, color="1F3864")
SMS = Font(name=F, size=8, bold=True, color="1F3864")
SMP = Font(name=F, size=8, bold=True, color="843C0C")
SMM = Font(name=F, size=8, bold=True, color="404040")
SMG = Font(name=F, size=8, color="808080")
FH = PatternFill("solid", fgColor="1F3864"); FY = PatternFill("solid", fgColor="FFFF00")
FG = PatternFill("solid", fgColor="E2EFDA"); FR = PatternFill("solid", fgColor="FCE4E4")
FO = PatternFill("solid", fgColor="FFF2CC"); FS = PatternFill("solid", fgColor="D9E2F3")
FSAV = PatternFill("solid", fgColor="DDEBF7"); FPROD = PatternFill("solid", fgColor="FBE5D6")
FMIX = PatternFill("solid", fgColor="EAEFF5"); FOFF = PatternFill("solid", fgColor="F2F2F2")
th = Side(style="thin", color="BFBFBF"); BOX = Border(th, th, th, th)
CC = Alignment(horizontal="center", vertical="center", wrap_text=True)
LL = Alignment(horizontal="left", vertical="center", wrap_text=True)
SHORT = {"Montoire-sur-le-Loir": "Montoire", "Romorantin-Lanthenay": "Romorantin",
         "Crouy-sur-Cosson": "Crouy-s-Cosson", "La Ferté-Imbault": "La Ferté-Imb."}
ORDER = sorted(C['cible'], key=lambda x: -C['cible'][x])


def hdr(ws, row, labels, widths=None, h=32):
    for i, l in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=l)
        c.font = H1; c.fill = FH; c.alignment = CC; c.border = BOX
    ws.row_dimensions[row].height = h
    if widths:
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w


wb = openpyxl.Workbook()

# ═══════════════════════════ 1. SYNTHÈSE
ws = wb.active; ws.title = "Synthèse"
ws["A1"] = "PLANIFICATION SAV / PROD — DÉPARTEMENT 41 (LOIR-ET-CHER)"; ws["A1"].font = TIT
ws["A2"] = "11 techniciens · 8 créneaux par technicien et par jour · objectif 436 créneaux ouverts par semaine"
ws["A2"].font = SUB
ws["A3"] = ("Volumes PROD : suivi_volumes_PROD_72.xlsx (MAJ 28/07/2026) — 12 secteurs du 41, mois le plus chargé "
            "secteur par secteur, B2B inclus, majoré de 10 %.")
ws["A3"].font = SUB
ws["A4"] = "Volume SAV : Planning_HEBDO_SAV_Departement_41.xlsx — 142 interventions par semaine, relevées secteur par secteur."
ws["A4"].font = SUB
for col, w in zip("ABCD", (52, 14, 14, 60)):
    ws.column_dimensions[col].width = w

r = 6
ws.cell(row=r, column=1, value="1 · PARAMÈTRES  (cellules jaunes = à ajuster)").font = SEC_TIT
r += 1; hdr(ws, r, ["Paramètre", "Valeur", "Unité", "Commentaire"])
P = {}
params = [
    ("Créneaux par technicien et par jour", 8, "créneaux", "Un créneau est un créneau, quelle que soit la nature de l'intervention", "cr", "0"),
    ("dont le matin", 4, "créneaux", "", "mat", "0"),
    ("dont l'après-midi", 4, "créneaux", "", "apm", "0"),
    ("Objectif d'occupation", 0.75, "%", "On n'occupe jamais plus de 75 % des créneaux : le quart restant EST la disponibilité", "occ", "0%"),
    ("Marge de flexibilité sur les volumes PROD", 0.10, "%", "Demande client", "marge", "0%"),
    ("Nombre de techniciens", 11, "tech.", "Effectif actuel", "n", "0"),
    ("dont travaillant 6 jours", 5, "tech.", "Ils portent le rythme Mardi-Jeudi-Samedi", "n6", "0"),
    ("dont travaillant 5 jours", None, "tech.", "", "n5", "0"),
    ("Jours-technicien par semaine", None, "j-tech", "", "td", "0"),
    ("Capacité totale", None, "créneaux/sem.", "jours-technicien × créneaux par jour", "cap", "0"),
]
for lab, val, unit, com, key, fmt in params:
    r += 1
    ws.cell(row=r, column=1, value=lab).font = BLK
    c = ws.cell(row=r, column=2)
    if key == "n5":
        c.value = f"={P['n']}-{P['n6']}"; c.font = BLK
    elif key == "td":
        c.value = f"={P['n6']}*6+{P['n5']}*5"; c.font = BLK
    elif key == "cap":
        c.value = f"={P['td']}*{P['cr']}"; c.font = BOLD
    else:
        c.value = val; c.font = BLUE; c.fill = FY
    c.alignment = CC; c.number_format = fmt
    ws.cell(row=r, column=3, value=unit).font = BLK; ws.cell(row=r, column=3).alignment = CC
    ws.cell(row=r, column=4, value=com).font = SUB; ws.cell(row=r, column=4).alignment = LL
    for k in range(1, 5):
        ws.cell(row=r, column=k).border = BOX
    P[key] = f"$B${r}"

r += 2
ws.cell(row=r, column=1, value="2 · BILAN HEBDOMADAIRE").font = SEC_TIT
r += 1; hdr(ws, r, ["Poste", "Interventions / sem.", "Créneaux / sem.", "Lecture"])


def bl(lab, inter, cren, com, fill=None):
    global r
    r += 1
    ws.cell(row=r, column=1, value=lab).font = BOLD if fill else BLK
    for col, v in ((2, inter), (3, cren)):
        c = ws.cell(row=r, column=col, value=v)
        c.font = BOLD if fill else BLK; c.alignment = CC; c.number_format = "0"
        if fill:
            c.fill = fill
    ws.cell(row=r, column=4, value=com).font = SUB; ws.cell(row=r, column=4).alignment = LL
    for k in range(1, 5):
        ws.cell(row=r, column=k).border = BOX
    if fill:
        ws.cell(row=r, column=1).fill = fill; ws.cell(row=r, column=4).fill = fill
    return r


rd = bl("Demande PROD (+10 %)", "='Demande 41'!$H$17", f"='Demande 41'!$H$17/{P['occ']}",
        "Volumes du fichier source, mois le plus chargé par secteur, B2B inclus")
rs = bl("Demande SAV", "='Demande 41'!$I$17", f"='Demande 41'!$I$17/{P['occ']}",
        "Relevée sur votre planning hebdomadaire SAV")
rt = bl("TOTAL à couvrir", f"=$B${rd}+$B${rs}", f"=$C${rd}+$C${rs}",
        "Créneaux à ouvrir pour ne pas dépasser 75 % d'occupation", FO)
rc = bl("Créneaux ouverts par la grille", "", "GRILLE_TOTAL_REF", "Voir l'onglet « Grille hebdo »")
rm = bl("Réserve", "", f"=$C${rc}-$C${rt}", "En jours-technicien : voir le verdict ci-dessous", FG)
r += 1
ws.cell(row=r, column=1, value="VERDICT").font = WHT
ws.cell(row=r, column=1).fill = FH; ws.cell(row=r, column=1).border = BOX
ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
ws.cell(row=r, column=2, value=(
    f'=IF($C${rc}>=$C${rt},"TENABLE À "&TEXT({P["n"]},"0")&" TECHNICIENS — réserve de "&TEXT($C${rc}-$C${rt},"0")'
    f'&" créneaux, soit "&TEXT(($C${rc}-$C${rt})/{P["cr"]},"0.0")&" jours-technicien",'
    f'"INSUFFISANT — il manque "&TEXT($C${rt}-$C${rc},"0")&" créneaux")'))
ws.cell(row=r, column=2).font = BOLD; ws.cell(row=r, column=2).alignment = LL; ws.cell(row=r, column=2).border = BOX
ws.row_dimensions[r].height = 30

r += 2
ws.cell(row=r, column=1, value="3 · PRINCIPE : LE SAV COMMANDE, LA PROD SUIT").font = SEC_TIT
for txt in [
    "Le SAV impose OÙ et QUAND il faut être. Chaque secteur est visité 3 fois par semaine sur un rythme Lundi-Mercredi-Vendredi ou Mardi-Jeudi-Samedi. Sur une semaine de 6 jours, ce sont les DEUX SEULES combinaisons de 3 jours qui garantissent un créneau à J+1 ou J+2 quel que soit le jour d'appel — et elles sont exactement complémentaires.",
    "Deux passages par semaine ne suffisent jamais, quelle que soit la combinaison choisie. C'est démontré : aucune paire de jours ne tient le J+1/J+2.",
    "La PROD se place ensuite dans tout ce qui reste. Elle dispose de 5 à 7 jours de visibilité, donc elle peut attendre : c'est elle qui absorbe les contraintes, jamais le SAV.",
    "À J-1 18 h, tout créneau SAV non vendu pour le lendemain est rempli par une intervention PROD du même secteur, puisée dans le carnet J+5/J+7. Aucun créneau n'est perdu.",
    "Les 5 techniciens à 6 jours portent obligatoirement les secteurs du rythme Mardi-Jeudi-Samedi : sans leur samedi, aucun créneau n'existe à J+1/J+2 pour un appel du jeudi ou du vendredi.",
]:
    r += 1
    ws.cell(row=r, column=1, value="• " + txt).font = SUB
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=4)
    ws.cell(row=r, column=1).alignment = LL
    ws.row_dimensions[r].height = 32

# ═══════════════════════════ 2. GRILLE HEBDO
ws = wb.create_sheet("Grille hebdo")
ws["A1"] = "GRILLE HEBDOMADAIRE — 11 TECHNICIENS · 8 CRÉNEAUX PAR JOUR"; ws["A1"].font = TIT
ws["A2"] = ("Chaque case est coupée en deux : matin (4 créneaux) au-dessus, après-midi (4 créneaux) en dessous. "
            "« SAV n » = créneaux réservés, ouverts à la prise de RDV J+1/J+2. « PROD n » = interventions posées depuis le carnet J+5/J+7.")
ws["A2"].font = SUB
ws["A3"] = "La tournée est figée : technicien × jour × secteur ne change jamais. Seul le partage SAV / PROD à l'intérieur de la journée évolue."
ws["A3"].font = SUB
H = ["Tech.", "Rôle", "Jours"]
for j in JOURS:
    H += [f"{j}\nmatin", f"{j}\naprès-midi"]
H += ["SAV\n/sem.", "PROD\n/sem.", "Total\n/sem."]
hdr(ws, 5, H, [7, 40, 6] + [15] * 12 + [8, 8, 8], h=34)
r = 6
for t, role, nj, sem in GRID:
    ws.cell(row=r, column=1, value=t).font = BOLD; ws.cell(row=r, column=1).alignment = CC
    ws.cell(row=r, column=2, value=role).font = BLK; ws.cell(row=r, column=2).alignment = LL
    ws.cell(row=r, column=3, value=nj).font = BOLD if nj == 6 else BLK
    ws.cell(row=r, column=3).alignment = CC
    if nj == 6:
        ws.cell(row=r, column=3).fill = FO
    nsav = nprod = 0
    for k, (j, day) in enumerate(zip(JOURS, sem)):
        for off in (0, 1):
            col = 4 + k * 2 + off
            c = ws.cell(row=r, column=col)
            if day is None:
                c.value = "repos"; c.font = SMG; c.fill = FOFF
            else:
                sec, sv, pr = day[off]
                lab = SHORT.get(sec, sec)
                parts = []
                if sv: parts.append(f"SAV {sv}")
                if pr: parts.append(f"PROD {pr}")
                c.value = f"{lab}\n{' · '.join(parts)}"
                if sv and pr:
                    c.font = SMM; c.fill = FMIX
                elif sv:
                    c.font = SMS; c.fill = FSAV
                else:
                    c.font = SMP; c.fill = FPROD
                nsav += sv; nprod += pr
            c.alignment = CC; c.border = BOX
    for col, v in ((16, nsav), (17, nprod), (18, nsav + nprod)):
        c = ws.cell(row=r, column=col, value=v); c.font = BOLD; c.alignment = CC; c.border = BOX
    for col in (1, 2, 3):
        ws.cell(row=r, column=col).border = BOX
    ws.row_dimensions[r].height = 30
    r += 1
ws.cell(row=r, column=1, value="TOTAL"); ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
ws.cell(row=r, column=3, value=f"=SUM(C6:C{r-1})")
for col in (16, 17, 18):
    cl = get_column_letter(col)
    ws.cell(row=r, column=col, value=f"=SUM({cl}6:{cl}{r-1})")
for col in range(1, 19):
    c = ws.cell(row=r, column=col); c.font = WHT; c.fill = FH; c.alignment = CC; c.border = BOX
TOT_ROW = r
r += 2
ws.cell(row=r, column=1, value="Bleu = créneaux SAV réservés   ·   Orange = PROD posée   ·   Gris = demi-journée mixte   ·   Colonne « Jours » sur fond orange = les 5 techniciens à 6 jours").font = SUB
r += 1
ws.cell(row=r, column=1, value="Enchaînements matin → après-midi sur deux secteurs différents : Montoire→Cormenon 30 km · Vendôme→Épiais 29 km · Romorantin→La Ferté-Imbault 22 km · Romorantin→Mur-de-Sologne 13 km. Aucun au-delà de 30 km.").font = SUB
r += 1
ws.cell(row=r, column=1, value="T11 est le renfort flottant : ses journées constituent la réserve pour les absences, les urgences et les pointes de volume. C'est le seul technicien réaffectable d'une semaine sur l'autre.").font = SUB
ws.freeze_panes = "D6"

# ═══════════════════════════ 3. CONTRÔLE SECTEURS
ws = wb.create_sheet("Contrôle secteurs")
ws["A1"] = "CONTRÔLE PAR SECTEUR — DÉLAI SAV, COUVERTURE SAV ET PROD"; ws["A1"].font = TIT
ws["A2"] = "Les quatre colonnes de contrôle doivent toutes afficher OK. Elles vérifient le délai J+1/J+2, la couverture du SAV et celle de la PROD."
ws["A2"].font = SUB
hdr(ws, 4, ["Secteur", "Jours de passage SAV", "Passages /sem.", "Rythme",
            "Créneaux ouverts", "Cible", "SAV réservés", "SAV demandé", "PROD ouverte", "PROD demandée",
            "Délai J+1/J+2", "SAV couvert", "PROD couverte"],
    [24, 20, 9, 10, 11, 8, 11, 10, 11, 11, 12, 11, 12], h=44)
r = 5
ST = r
for s in ORDER:
    jp = R['pass'].get(s, [])
    rythme = ("L-Me-V" if set(jp) == {"Lundi", "Mercredi", "Vendredi"}
              else "Ma-J-S" if set(jp) == {"Mardi", "Jeudi", "Samedi"} else "Quotidien")
    ws.cell(row=r, column=1, value=s).font = BLK; ws.cell(row=r, column=1).alignment = LL
    ws.cell(row=r, column=2, value=" · ".join(x[:3] for x in jp)).font = BLK
    ws.cell(row=r, column=3, value=len(jp)).font = BLK
    ws.cell(row=r, column=4, value=rythme).font = BLK
    ws.cell(row=r, column=5, value=R['slots'].get(s, 0)).font = BOLD
    ws.cell(row=r, column=6, value=round(C['cible'][s])).font = GRN
    ws.cell(row=r, column=7, value=R['sav'].get(s, 0)).font = BOLD
    ws.cell(row=r, column=8, value=C['sav_dem'][s]).font = BLUE
    ws.cell(row=r, column=9, value=R['prod'].get(s, 0)).font = BOLD
    ws.cell(row=r, column=10, value=round(C['prod_dem'][s], 1)).font = BLK
    ws.cell(row=r, column=11, value=f'=IF($C{r}>=3,"OK","NON")')
    ws.cell(row=r, column=12, value=f'=IF($G{r}>=$H{r},"OK","NON")')
    ws.cell(row=r, column=13, value=f'=IF($I{r}>=$J{r},"OK","NON")')
    for col in range(11, 14):
        c = ws.cell(row=r, column=col); c.font = BOLD; c.fill = FG
    for col in range(1, 14):
        c = ws.cell(row=r, column=col); c.border = BOX
        if col > 1:
            c.alignment = CC
        if col == 10:
            c.number_format = "0.0"
    r += 1
EN = r - 1
ws.cell(row=r, column=1, value="TOTAL"); ws.cell(row=r, column=2, value="12 secteurs")
for col in (5, 6, 7, 8, 9, 10):
    cl = get_column_letter(col)
    ws.cell(row=r, column=col, value=f"=SUM({cl}{ST}:{cl}{EN})")
for col in range(1, 14):
    c = ws.cell(row=r, column=col); c.font = WHT; c.fill = FH; c.alignment = CC; c.border = BOX
    if col == 10:
        c.number_format = "0.0"
r += 2
ws.cell(row=r, column=1, value="« Cible » = part des 436 créneaux revenant au secteur, au prorata de sa demande totale (SAV + PROD).").font = SUB
r += 1
ws.cell(row=r, column=1, value="Un secteur peut dépasser sa cible : l'excédent constitue sa réserve locale. Il ne doit jamais passer sous la demande SAV ni sous la demande PROD.").font = SUB

MARGE_REF = P["marge"]; OCC_REF = P["occ"]
# ═══════════════════════════ 4. DEMANDE 41
ws = wb.create_sheet("Demande 41")
ws["A1"] = "DEMANDE PAR SECTEUR — DÉPARTEMENT 41"; ws["A1"].font = TIT
ws["A2"] = "Colonnes B à D : volumes bruts du fichier source. Colonne I (bleue) : volume SAV relevé sur votre planning hebdomadaire."
ws["A2"].font = SUB
hdr(ws, 4, ["Secteur", "PROD octobre\n(inter./mois)", "PROD mars\n(inter./mois)", "B2B\n(inter./mois)",
            "Mois retenu\n(max par secteur)", "PROD retenue\n+10 % (/mois)", "PROD\n+10 % (/sem.)",
            "PROD\n(/sem.)", "SAV\n(/sem.)", "Demande totale\n(/sem.)", "Créneaux cible\n(occupation 75 %)"],
    [24, 13, 13, 11, 13, 13, 12, 11, 11, 13, 14], h=48)
SRC = {"Blois": (240, 218, 3.000), "Valencisse": (43, 42, 0.667), "Pontlevoy": (88, 84, 0.667),
       "Vendôme": (38, 34, 0.667), "Épiais": (48, 50, 0.667), "Montoire-sur-le-Loir": (37, 48, 0.333),
       "Cormenon": (18, 19, 0.333), "Crouy-sur-Cosson": (52, 48, 0.333), "Vouzon": (31, 33, 0.333),
       "Mur-de-Sologne": (49, 36, 0.333), "Romorantin-Lanthenay": (44, 31, 0.333), "La Ferté-Imbault": (17, 13, 0.667)}
r = 5
for s in ORDER:
    o, ma, b = SRC[s]
    ws.cell(row=r, column=1, value=s).font = BLK; ws.cell(row=r, column=1).alignment = LL
    for col, v in ((2, o), (3, ma), (4, round(b, 2))):
        ws.cell(row=r, column=col, value=v).font = BLK
    ws.cell(row=r, column=5, value=f"=MAX($B{r},$C{r})")
    ws.cell(row=r, column=6, value=f"=($E{r}+$D{r})*(1+Synthèse!{P[chr(39)+chr(39)] if False else MARGE_REF})")
    ws.cell(row=r, column=7, value=f"=$F{r}/4.3333")
    ws.cell(row=r, column=8, value=f"=$G{r}")
    ws.cell(row=r, column=9, value=C['sav_dem'][s]).font = BLUE
    ws.cell(row=r, column=9).fill = FY
    ws.cell(row=r, column=10, value=f"=$H{r}+$I{r}")
    ws.cell(row=r, column=11, value=f"=$J{r}/Synthèse!{OCC_REF}")
    for col in range(2, 12):
        c = ws.cell(row=r, column=col); c.border = BOX; c.alignment = CC
        c.number_format = "0.0" if col in (4, 6, 7, 8, 10, 11) else "0"
        if col != 9:
            c.font = BLK
    ws.cell(row=r, column=1).border = BOX
    r += 1
ws.cell(row=r, column=1, value="TOTAL DÉPARTEMENT 41")
for col in (2, 3, 4, 5, 6, 7, 8, 9, 10, 11):
    cl = get_column_letter(col)
    ws.cell(row=r, column=col, value=f"=SUM({cl}5:{cl}{r-1})")
for col in range(1, 12):
    c = ws.cell(row=r, column=col); c.font = WHT; c.fill = FH; c.alignment = CC; c.border = BOX
    c.number_format = "0.0" if col in (4, 6, 7, 8, 10, 11) else "0"
r += 2
ws.cell(row=r, column=1, value="Le fichier source ne dimensionne que sur mars. Or sur le 41, octobre est le mois haut (705 interventions contre 656) : retenir le mois le plus chargé secteur par secteur ajoute environ 7 % au besoin.").font = SUB

# ═══════════════════════════ 5. MOTEUR DISPO
ws = wb.create_sheet("Moteur dispo")
ws["A1"] = "MOTEUR DE DISPONIBILITÉ — RÉSERVATION SAV ET BASCULE PROD"; ws["A1"].font = TIT
ws["A2"] = "Le mécanisme qui libère de la disponibilité sans embaucher : on réserve large pour le SAV, et tout créneau non vendu redevient de la PROD la veille au soir."
ws["A2"].font = SUB
r = 4
ws.cell(row=r, column=1, value="RÈGLES D'EXPLOITATION").font = SEC_TIT
r += 1
hdr(ws, r, ["N°", "Moment", "Règle", "Effet"], [5, 18, 64, 50], h=24)
for n, mo, rg, ef in [
    ("R1", "Permanent", "La tournée est figée : technicien × jour × secteur ne change jamais.", "Distances maîtrisées, techniciens sur des secteurs qu'ils connaissent."),
    ("R2", "Permanent", "Chaque secteur est visité 3 fois par semaine, rythme Lundi-Mercredi-Vendredi ou Mardi-Jeudi-Samedi.", "Quel que soit le jour d'appel, il existe un passage à J+1 ou J+2."),
    ("R3", "Permanent", "Sur chaque demi-journée, un nombre fixe de créneaux est réservé au SAV. Le reste est ouvert à la PROD.", "L'occupation ne dépasse jamais 75 % : le quart restant est la disponibilité."),
    ("R4", "J-7 à J-5", "La PROD se pose uniquement sur les créneaux non réservés au SAV, dans le carnet J+5 à J+7.", "Le client PROD obtient bien un RDV à J+5/J+6/J+7."),
    ("R5", "J-2, 18 h", "Ouverture à la prise de RDV SAV des créneaux réservés du jour J.", "Le client SAV qui appelle voit de la dispo à J+1 et J+2."),
    ("R6", "J-1, 18 h", "BASCULE : tout créneau SAV encore libre pour le lendemain est réaffecté à une intervention PROD du même secteur.", "Aucun créneau perdu. C'est ce qui rend la réservation SAV quasi gratuite."),
    ("R7", "J-1, 18 h", "La bascule suppose au moins 2 interventions PROD en attente dans le secteur.", "Sur Cormenon et La Ferté-Imbault, maintenir un stock PROD tampon."),
    ("R8", "Jour J", "Un SAV urgent arrivé après la bascule prend la place d'une PROD du jour, qui repart en J+5.", "La PROD absorbe l'aléa, jamais le SAV — c'est elle qui a le délai le plus long."),
    ("R9", "Hebdo", "Si l'occupation SAV d'un secteur dépasse 75 % quatre semaines de suite, augmenter sa réservation.", "Le curseur de réservation suit la demande réelle."),
    ("R10", "Hebdo", "Le renfort flottant (T11) est affecté le vendredi pour la semaine suivante, au secteur au carnet le plus tendu.", "La réserve va là où elle sert, pas là où elle dort."),
]:
    r += 1
    for col, v, f in ((1, n, BOLD), (2, mo, BLK), (3, rg, BLK), (4, ef, SUB)):
        c = ws.cell(row=r, column=col, value=v)
        c.font = f; c.alignment = CC if col <= 2 else LL; c.border = BOX
    ws.row_dimensions[r].height = 30
    if n in ("R2", "R6"):
        for col in range(1, 5):
            ws.cell(row=r, column=col).fill = FG
r += 2
ws.cell(row=r, column=1, value="TABLEAU DE BORD QUOTIDIEN — À REMPLIR CHAQUE SOIR AVANT LA BASCULE").font = SEC_TIT
r += 1
ws.cell(row=r, column=1, value="Colonne D (jaune) : nombre de RDV SAV réellement pris pour le lendemain. Le reste se calcule.").font = SUB
r += 1
hdr(ws, r, ["Secteur visité demain", "Créneaux du jour", "dont réservés SAV", "RDV SAV pris (à saisir)",
            "Créneaux SAV libres", "PROD à injecter", "Occupation SAV", "Alerte"],
    [24, 13, 14, 15, 14, 13, 12, 40], h=44)
r += 1
ST2 = r
DAILY = [("Blois", 8, 4), ("Pontlevoy", 8, 4), ("Vendôme", 8, 4), ("Épiais", 8, 4), ("Mur-de-Sologne", 8, 4),
         ("Crouy-sur-Cosson", 8, 4), ("Valencisse", 8, 3), ("Montoire-sur-le-Loir", 8, 4), ("Cormenon", 8, 3),
         ("Romorantin-Lanthenay", 8, 3), ("La Ferté-Imbault", 8, 2), ("Vouzon", 8, 3)]
for sec, tot, res in DAILY:
    ws.cell(row=r, column=1, value=sec).font = BLK; ws.cell(row=r, column=1).alignment = LL
    ws.cell(row=r, column=2, value=tot).font = BLK
    ws.cell(row=r, column=3, value=res).font = BLK
    c = ws.cell(row=r, column=4, value=0); c.font = BLUE; c.fill = FY
    ws.cell(row=r, column=5, value=f"=MAX(0,$C{r}-$D{r})")
    ws.cell(row=r, column=6, value=f"=$E{r}")
    ws.cell(row=r, column=7, value=f"=IFERROR($D{r}/$C{r},0)").number_format = "0%"
    ws.cell(row=r, column=8, value=(f'=IF($D{r}>$C{r},"Débordement SAV : basculer une PROD du jour",'
                                    f'IF($D{r}/$C{r}>0.75,"Occupation SAV > 75 % : augmenter la réservation",'
                                    f'"Injecter "&TEXT($F{r},"0")&" PROD du carnet J+5/J+7"))'))
    ws.cell(row=r, column=8).font = SUB; ws.cell(row=r, column=8).alignment = LL
    for col in range(1, 9):
        c = ws.cell(row=r, column=col); c.border = BOX
        if col not in (1, 8):
            c.alignment = CC
        if col in (5, 6):
            c.font = BLK
    r += 1
EN2 = r - 1
ws.cell(row=r, column=1, value="TOTAL JOUR")
for col in (2, 3, 4, 5, 6):
    cl = get_column_letter(col)
    ws.cell(row=r, column=col, value=f"=SUM({cl}{ST2}:{cl}{EN2})")
ws.cell(row=r, column=7, value=f"=IFERROR($D{r}/$C{r},0)").number_format = "0%"
for col in range(1, 9):
    c = ws.cell(row=r, column=col); c.font = WHT; c.fill = FH; c.alignment = CC; c.border = BOX

# ═══════════════════════════ 6. DISTANCES
ws = wb.create_sheet("Distances")
ws["A1"] = "COHÉRENCE GÉOGRAPHIQUE — DISTANCES ROUTIÈRES ESTIMÉES (km)"; ws["A1"].font = TIT
ws["A2"] = ("Estimation : vol d'oiseau × 1,25, majorée de 8 km entre les deux rives de la Loire "
            "(ponts de Blois, Chaumont, Muides, Beaugency). À recaler avec votre outil de tournées.")
ws["A2"].font = SUB
PTS = [("Blois", 47.586, 1.336, "X"), ("Valencisse", 47.590, 1.220, "N"), ("Pontlevoy", 47.395, 1.256, "S"),
       ("Vendôme", 47.793, 1.066, "N"), ("Épiais", 47.760, 1.375, "N"), ("Montoire-sur-le-Loir", 47.752, 0.866, "N"),
       ("Cormenon", 47.955, 0.980, "N"), ("Crouy-sur-Cosson", 47.680, 1.610, "S"), ("Vouzon", 47.660, 2.020, "S"),
       ("Mur-de-Sologne", 47.383, 1.612, "S"), ("Romorantin-Lanthenay", 47.357, 1.744, "S"),
       ("La Ferté-Imbault", 47.395, 1.976, "S")]


def dist(a, b):
    x = math.radians(b[2] - a[2]) * math.cos(math.radians((a[1] + b[1]) / 2))
    y = math.radians(b[1] - a[1])
    d = 6371 * math.hypot(x, y) * 1.25
    if a[3] != b[3] and "X" not in (a[3], b[3]):
        d += 8
    return round(d)


r = 4
hdr(ws, r, [""] + [p[0] for p in PTS], [24] + [13] * 12, h=54)
for i in range(2, 14):
    ws.cell(row=r, column=i).alignment = Alignment(horizontal="center", vertical="bottom", wrap_text=True, textRotation=60)
r += 1
for a in PTS:
    c = ws.cell(row=r, column=1, value=a[0]); c.font = BOLD; c.fill = FS; c.alignment = LL; c.border = BOX
    for j, b in enumerate(PTS, 2):
        d = dist(a, b)
        cc = ws.cell(row=r, column=j, value=("—" if a[0] == b[0] else d))
        cc.font = BLK; cc.alignment = CC; cc.border = BOX
        if a[0] != b[0]:
            cc.fill = FG if d <= 30 else (FO if d <= 50 else FR)
    r += 1
r += 1
ws.cell(row=r, column=1, value="Vert ≤ 30 km : enchaînement de deux demi-journées acceptable   ·   Orange 31-50 km : à éviter dans la même journée   ·   Rouge > 50 km : incohérent").font = SUB
r += 2
ws.cell(row=r, column=1, value="ENCHAÎNEMENTS RETENUS DANS LA GRILLE").font = SEC_TIT
r += 1
hdr(ws, r, ["Matin", "Après-midi", "Distance", "Techniciens concernés"], [24, 24, 11, 44], h=24)
PAIRS = [("Montoire-sur-le-Loir", "Cormenon", 30, "T2 mardi, jeudi, samedi · T9 mardi"),
         ("Vendôme", "Épiais", 29, "T2 lundi, mercredi, vendredi · T9 lundi, mercredi"),
         ("Épiais", "Vendôme", 29, "T11 mardi"),
         ("Romorantin-Lanthenay", "La Ferté-Imbault", 22, "T3 mardi, jeudi, samedi · T10 vendredi"),
         ("Romorantin-Lanthenay", "Mur-de-Sologne", 13, "T10 lundi, mercredi")]
for a, b, d, q in PAIRS:
    r += 1
    for col, v in ((1, a), (2, b), (3, f"{d} km"), (4, q)):
        c = ws.cell(row=r, column=col, value=v)
        c.font = BLK if col != 3 else BOLD; c.alignment = LL if col in (1, 2, 4) else CC; c.border = BOX
        if col == 3:
            c.fill = FG

# ═══════════════════════════ 7. EFFECTIF
ws = wb.create_sheet("Effectif")
ws["A1"] = "AFFECTATION DES 11 TECHNICIENS"; ws["A1"].font = TIT
ws["A2"] = "5 techniciens à 6 jours + 6 techniciens à 5 jours = 60 jours-technicien par semaine = 480 créneaux."
ws["A2"].font = SUB
hdr(ws, 4, ["Tech.", "Rôle", "Jours /sem.", "Base conseillée", "Secteurs couverts", "SAV /sem.", "PROD /sem."],
    [7, 44, 9, 22, 46, 10, 10], h=28)
BASE = {"T1": "Blois", "T2": "Vendôme", "T3": "Romorantin-Lanthenay", "T4": "Crouy-sur-Cosson ou Lamotte-Beuvron",
        "T5": "Pontlevoy ou Montrichard", "T6": "Blois", "T7": "Blois", "T8": "Blois",
        "T9": "Vendôme", "T10": "Romorantin-Lanthenay", "T11": "Blois"}
r = 5
ST3 = r
for t, role, nj, sem in GRID:
    secs = {}
    sv = pr = 0
    for day in sem:
        if not day:
            continue
        for sec, a, b in day:
            secs[sec] = secs.get(sec, 0) + a + b
            sv += a; pr += b
    for col, v in ((1, t), (2, role), (3, nj), (4, BASE[t]),
                   (5, " · ".join(sorted(secs, key=lambda x: -secs[x]))), (6, sv), (7, pr)):
        c = ws.cell(row=r, column=col, value=v)
        c.font = BOLD if col == 1 else BLK
        c.alignment = CC if col in (1, 3, 6, 7) else LL
        c.border = BOX
    if nj == 6:
        for col in range(1, 8):
            ws.cell(row=r, column=col).fill = FO
    ws.row_dimensions[r].height = 26
    r += 1
EN3 = r - 1
ws.cell(row=r, column=1, value="TOTAL")
ws.cell(row=r, column=2, value=f'=COUNTA(A{ST3}:A{EN3})&" techniciens"')
for col, f in ((3, f"=SUM(C{ST3}:C{EN3})"), (6, f"=SUM(F{ST3}:F{EN3})"), (7, f"=SUM(G{ST3}:G{EN3})")):
    ws.cell(row=r, column=col, value=f)
ws.cell(row=r, column=5, value="12 secteurs GRDV couverts")
for col in range(1, 8):
    c = ws.cell(row=r, column=col); c.fill = FH; c.border = BOX; c.alignment = CC; c.font = WHT
r += 2
ws.cell(row=r, column=1, value="Fond orange = les 5 techniciens à 6 jours. Ils portent les secteurs du rythme Mardi-Jeudi-Samedi : sans leur samedi, aucun créneau SAV n'existe à J+1/J+2 pour un appel du jeudi ou du vendredi.").font = SUB
r += 1
ws.cell(row=r, column=1, value="T1 est le technicien 100 % SAV déjà en poste, maintenu sur Blois et Valencisse comme demandé (11 km entre les deux hubs).").font = SUB
r += 1
ws.cell(row=r, column=1, value="T11 est le renfort flottant : réserve pour les absences, les urgences et les pointes. Il est réaffecté chaque vendredi pour la semaine suivante.").font = SUB

for w in wb.worksheets:
    w.sheet_view.showGridLines = False
    w.page_setup.orientation = 'landscape'
    w.page_setup.fitToWidth = 1
    w.sheet_properties.pageSetUpPr.fitToPage = True
# la Synthèse est écrite avant la grille : on résout maintenant la référence
# garde-fou : un commentaire commençant par '=' serait interprété comme une formule par Excel
import re as _re
for _ws in wb.worksheets:
    for _row in _ws.iter_rows():
        for _c in _row:
            if isinstance(_c.value,str) and _c.value.startswith('=') and _re.match(r'^=\s', _c.value):
                _c.value=_c.value[1:].strip()
syn=wb['Synthèse']
for row in syn.iter_rows():
    for c in row:
        if c.value=="GRILLE_TOTAL_REF": c.value=f"='Grille hebdo'!$R${TOT_ROW}"
wb.save('Planification_41_SAV_PROD.xlsx')
print("Classeur écrit :", wb.sheetnames)
print("Ligne TOTAL de la grille :", TOT_ROW)
