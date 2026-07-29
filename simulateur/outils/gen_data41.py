# -*- coding: utf-8 -*-
"""Génère packages/data/src/dept41.ts depuis le fichier de suivi + le référentiel géographique."""
import openpyxl, json, unicodedata

SRC = '/root/.claude/uploads/f71559d2-3695-58ab-95b7-be0c10466104/514fd968-suivi_volumes_PROD_72.xlsx'
OUT = '/home/user/Redimensionnement-d-partement/simulateur/packages/data/src/dept41.ts'

# code INSEE, nom d'usage, lat, lon, zone — coordonnées issues de l'API Géo officielle
GEO = {
    'BLOIS':                ('41018', 'Blois',                 47.5813, 1.3049, 'Z1'),
    'PONTLEVOY':            ('41180', 'Pontlevoy',             47.4023, 1.2315, 'Z1'),
    'EPIAIS':               ('41077', 'Épiais',                47.8120, 1.2489, 'Z2'),
    'CROUY-SUR-COSSON':     ('41071', 'Crouy-sur-Cosson',      47.6598, 1.6204, 'Z1'),
    'VALENCISSE':           ('41142', 'Valencisse',            47.5715, 1.1968, 'Z1'),
    'MONTOIRE-SUR-LE-LOIR': ('41149', 'Montoire-sur-le-Loir',  47.7648, 0.8431, 'Z2'),
    'MUR-DE-SOLOGNE':       ('41157', 'Mur-de-Sologne',        47.4241, 1.6094, 'Z3'),
    'VENDOME':              ('41269', 'Vendôme',               47.7995, 1.0646, 'Z2'),
    'ROMORANTIN-LANTHENAY': ('41194', 'Romorantin-Lanthenay',  47.3725, 1.7368, 'Z3'),
    'VOUZON':               ('41296', 'Vouzon',                47.6347, 2.0348, 'Z3'),
    'CORMENON':             ('41060', 'Cormenon',              47.9625, 0.9090, 'Z2'),
    'LA FERTE-IMBAULT':     ('41084', 'La Ferté-Imbault',      47.4012, 1.9601, 'Z3'),
}

ZONES = [
    ('Z1', 'Blois / Val de Loire',   '41018'),
    ('Z2', 'Vendômois / Vallée du Loir', '41269'),
    ('Z3', 'Sologne',                '41194'),
]

# Matrice des distances routières (km), ordre ci-dessous.
ORDRE = ['BLOIS', 'VALENCISSE', 'PONTLEVOY', 'CROUY-SUR-COSSON', 'VENDOME', 'EPIAIS',
         'MONTOIRE-SUR-LE-LOIR', 'CORMENON', 'ROMORANTIN-LANTHENAY', 'MUR-DE-SOLOGNE',
         'LA FERTE-IMBAULT', 'VOUZON']
M = [
    [  0,  10,  26,  32,  38,  32,  50,  65,  50,  36,  66,  69],
    [ 10,   0,  24,  42,  34,  34,  43,  61,  58,  44,  76,  79],
    [ 26,  24,   0,  51,  57,  57,  62,  84,  48,  36,  69,  82],
    [ 32,  42,  51,   0,  55,  41,  74,  79,  41,  33,  48,  39],
    [ 38,  34,  57,  55,   0,  17,  21,  27,  87,  73, 101,  94],
    [ 32,  34,  57,  41,  17,   0,  38,  38,  76,  64,  88,  78],
    [ 50,  43,  62,  74,  21,  38,   0,  28, 100,  86, 116, 113],
    [ 65,  61,  84,  79,  27,  38,  28,   0, 113,  99, 126, 115],
    [ 50,  58,  48,  41,  87,  76, 100, 113,   0,  14,  21,  46],
    [ 36,  44,  36,  33,  73,  64,  86,  99,  14,   0,  33,  50],
    [ 66,  76,  69,  48, 101,  88, 116, 126,  21,  33,   0,  33],
    [ 69,  79,  82,  39,  94,  78, 113, 115,  46,  50,  33,   0],
]


def cle(libelle):
    n = str(libelle).split(' - ')[-1].strip().upper()
    return unicodedata.normalize('NFD', n).encode('ascii', 'ignore').decode()


def main():
    wb = openpyxl.load_workbook(SRC, data_only=True)
    ws = wb['Suivi des volumes PROD']
    volumes = {}
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[1] and str(r[1]).strip() == '41':
            volumes[cle(r[0])] = {
                'libelleGrdv': str(r[0]).strip(),
                'interOctobre': round(r[3] or 0, 4),
                'moyJrOctobre': round(r[4] or 0, 6),
                'interMars': round(r[6] or 0, 4),
                'moyJrMars': round(r[7] or 0, 6),
                'b2bMois': round(r[8] or 0, 4),
            }

    manquants = set(GEO) - set(volumes)
    if manquants:
        raise SystemExit(f'Secteurs sans volume : {manquants}')

    secteurs = []
    for k, (insee, nom, lat, lon, zone) in GEO.items():
        v = volumes[k]
        secteurs.append({
            'id': insee, 'nom': nom, 'libelleGrdv': v['libelleGrdv'],
            'departement': '41', 'lat': lat, 'lon': lon, 'zoneId': zone,
            'volume': {
                'interOctobre': v['interOctobre'], 'interMars': v['interMars'],
                'b2bMois': v['b2bMois'],
                'moyJrOctobre': v['moyJrOctobre'], 'moyJrMars': v['moyJrMars'],
            },
        })
    secteurs.sort(key=lambda s: s['id'])

    dist = {}
    for i, a in enumerate(ORDRE):
        ia = GEO[a][0]
        dist[ia] = {GEO[b][0]: M[i][j] for j, b in enumerate(ORDRE)}
    dist = {k: dist[k] for k in sorted(dist)}
    for k in dist:
        dist[k] = {j: dist[k][j] for j in sorted(dist[k])}

    # Contrôle de symétrie
    for a in dist:
        for b in dist[a]:
            if dist[a][b] != dist[b][a]:
                raise SystemExit(f'Matrice asymétrique : {a}/{b}')

    j = lambda o: json.dumps(o, ensure_ascii=False, indent=2).replace('"', "'")
    ts = f'''/**
 * Référentiel du département 41 (Loir-et-Cher) — 12 secteurs GRDV.
 *
 * Fichier généré. Volumes extraits de suivi_volumes_PROD_72.xlsx (mise à jour du
 * 28 juillet 2026). Coordonnées issues de l'API Géo officielle. Matrice des
 * distances estimée par vol d'oiseau majoré de 25 %, à recaler sur un outil de
 * tournées.
 */
import type {{ Referentiel, Secteur, Zone }} from '@sim/engine';

export const SECTEURS_41: readonly Secteur[] = {j(secteurs)} as const;

export const ZONES_41: readonly Zone[] = {j([{'id': i, 'nom': n, 'baseSecteurId': b} for i, n, b in ZONES])} as const;

export const DISTANCES_41 = {j(dist)} as const;

export const REFERENTIEL_41: Referentiel = {{
  departement: '41',
  libelle: 'Loir-et-Cher',
  secteurs: SECTEURS_41,
  zones: ZONES_41,
  distances: DISTANCES_41,
}};
'''
    import os
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'w').write(ts)
    print(f'{len(secteurs)} secteurs, {len(ZONES)} zones → {OUT}')
    tot = sum(max(s['volume']['interOctobre'], s['volume']['interMars']) + s['volume']['b2bMois'] for s in secteurs)
    print(f'  volume pic + B2B = {tot} inter/mois → {tot/4.333:.1f}/sem → {tot/4.333*1.1:.1f} avec +10 %')


if __name__ == '__main__':
    main()
