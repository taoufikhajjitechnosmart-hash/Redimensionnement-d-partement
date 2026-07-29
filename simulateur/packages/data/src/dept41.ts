/**
 * Référentiel du département 41 (Loir-et-Cher) — 12 secteurs GRDV.
 *
 * Fichier généré. Volumes extraits de suivi_volumes_PROD_72.xlsx (mise à jour du
 * 28 juillet 2026). Coordonnées issues de l'API Géo officielle. Matrice des
 * distances estimée par vol d'oiseau majoré de 25 %, à recaler sur un outil de
 * tournées.
 */
import type { Referentiel, Secteur, Zone } from '@sim/engine';

export const SECTEURS_41: readonly Secteur[] = [
  {
    'id': '41018',
    'nom': 'Blois',
    'libelleGrdv': '41 LOIR-ET-CHER ZMD - BLOIS',
    'departement': '41',
    'lat': 47.5813,
    'lon': 1.3049,
    'zoneId': 'Z1',
    'volume': {
      'interOctobre': 240,
      'interMars': 218,
      'b2bMois': 3.0,
      'moyJrOctobre': 9.6,
      'moyJrMars': 9.083333
    }
  },
  {
    'id': '41060',
    'nom': 'Cormenon',
    'libelleGrdv': '41 LOIR-ET-CHER RIP VDLF - CORMENON',
    'departement': '41',
    'lat': 47.9625,
    'lon': 0.909,
    'zoneId': 'Z2',
    'volume': {
      'interOctobre': 18,
      'interMars': 19,
      'b2bMois': 0.3333,
      'moyJrOctobre': 0.72,
      'moyJrMars': 0.791667
    }
  },
  {
    'id': '41071',
    'nom': 'Crouy-sur-Cosson',
    'libelleGrdv': '41 LOIR-ET-CHER RIP VDLF - CROUY-SUR-COSSON',
    'departement': '41',
    'lat': 47.6598,
    'lon': 1.6204,
    'zoneId': 'Z1',
    'volume': {
      'interOctobre': 52,
      'interMars': 48,
      'b2bMois': 0.3333,
      'moyJrOctobre': 2.08,
      'moyJrMars': 2
    }
  },
  {
    'id': '41077',
    'nom': 'Épiais',
    'libelleGrdv': '41 LOIR-ET-CHER RIP VDLF - EPIAIS',
    'departement': '41',
    'lat': 47.812,
    'lon': 1.2489,
    'zoneId': 'Z2',
    'volume': {
      'interOctobre': 48,
      'interMars': 50,
      'b2bMois': 0.6667,
      'moyJrOctobre': 1.92,
      'moyJrMars': 2.083333
    }
  },
  {
    'id': '41084',
    'nom': 'La Ferté-Imbault',
    'libelleGrdv': '41 LOIR-ET-CHER RIP VDLF - LA FERTE-IMBAULT',
    'departement': '41',
    'lat': 47.4012,
    'lon': 1.9601,
    'zoneId': 'Z3',
    'volume': {
      'interOctobre': 17,
      'interMars': 13,
      'b2bMois': 0.6667,
      'moyJrOctobre': 0.68,
      'moyJrMars': 0.541667
    }
  },
  {
    'id': '41142',
    'nom': 'Valencisse',
    'libelleGrdv': '41 LOIR-ET-CHER RIP VDLF - VALENCISSE',
    'departement': '41',
    'lat': 47.5715,
    'lon': 1.1968,
    'zoneId': 'Z1',
    'volume': {
      'interOctobre': 43,
      'interMars': 42,
      'b2bMois': 0.6667,
      'moyJrOctobre': 1.72,
      'moyJrMars': 1.75
    }
  },
  {
    'id': '41149',
    'nom': 'Montoire-sur-le-Loir',
    'libelleGrdv': '41 LOIR-ET-CHER RIP VDLF - MONTOIRE-SUR-LE-LOIR',
    'departement': '41',
    'lat': 47.7648,
    'lon': 0.8431,
    'zoneId': 'Z2',
    'volume': {
      'interOctobre': 37,
      'interMars': 48,
      'b2bMois': 0.3333,
      'moyJrOctobre': 1.48,
      'moyJrMars': 2
    }
  },
  {
    'id': '41157',
    'nom': 'Mur-de-Sologne',
    'libelleGrdv': '41 LOIR-ET-CHER RIP VDLF - MUR-DE-SOLOGNE',
    'departement': '41',
    'lat': 47.4241,
    'lon': 1.6094,
    'zoneId': 'Z3',
    'volume': {
      'interOctobre': 49,
      'interMars': 36,
      'b2bMois': 0.3333,
      'moyJrOctobre': 1.96,
      'moyJrMars': 1.5
    }
  },
  {
    'id': '41180',
    'nom': 'Pontlevoy',
    'libelleGrdv': '41 LOIR-ET-CHER RIP VDLF - PONTLEVOY',
    'departement': '41',
    'lat': 47.4023,
    'lon': 1.2315,
    'zoneId': 'Z1',
    'volume': {
      'interOctobre': 88,
      'interMars': 84,
      'b2bMois': 0.6667,
      'moyJrOctobre': 3.52,
      'moyJrMars': 3.5
    }
  },
  {
    'id': '41194',
    'nom': 'Romorantin-Lanthenay',
    'libelleGrdv': '41 LOIR-ET-CHER ZMD - ROMORANTIN-LANTHENAY',
    'departement': '41',
    'lat': 47.3725,
    'lon': 1.7368,
    'zoneId': 'Z3',
    'volume': {
      'interOctobre': 44,
      'interMars': 31,
      'b2bMois': 0.3333,
      'moyJrOctobre': 1.76,
      'moyJrMars': 1.291667
    }
  },
  {
    'id': '41269',
    'nom': 'Vendôme',
    'libelleGrdv': '41 LOIR-ET-CHER ZMD - VENDOME',
    'departement': '41',
    'lat': 47.7995,
    'lon': 1.0646,
    'zoneId': 'Z2',
    'volume': {
      'interOctobre': 38,
      'interMars': 34,
      'b2bMois': 0.6667,
      'moyJrOctobre': 1.52,
      'moyJrMars': 1.416667
    }
  },
  {
    'id': '41296',
    'nom': 'Vouzon',
    'libelleGrdv': '41 LOIR-ET-CHER RIP VDLF - VOUZON',
    'departement': '41',
    'lat': 47.6347,
    'lon': 2.0348,
    'zoneId': 'Z3',
    'volume': {
      'interOctobre': 31,
      'interMars': 33,
      'b2bMois': 0.3333,
      'moyJrOctobre': 1.24,
      'moyJrMars': 1.375
    }
  }
] as const;

export const ZONES_41: readonly Zone[] = [
  {
    'id': 'Z1',
    'nom': 'Blois / Val de Loire',
    'baseSecteurId': '41018'
  },
  {
    'id': 'Z2',
    'nom': 'Vendômois / Vallée du Loir',
    'baseSecteurId': '41269'
  },
  {
    'id': 'Z3',
    'nom': 'Sologne',
    'baseSecteurId': '41194'
  }
] as const;

export const DISTANCES_41 = {
  '41018': {
    '41018': 0,
    '41060': 65,
    '41071': 32,
    '41077': 32,
    '41084': 66,
    '41142': 10,
    '41149': 50,
    '41157': 36,
    '41180': 26,
    '41194': 50,
    '41269': 38,
    '41296': 69
  },
  '41060': {
    '41018': 65,
    '41060': 0,
    '41071': 79,
    '41077': 38,
    '41084': 126,
    '41142': 61,
    '41149': 28,
    '41157': 99,
    '41180': 84,
    '41194': 113,
    '41269': 27,
    '41296': 115
  },
  '41071': {
    '41018': 32,
    '41060': 79,
    '41071': 0,
    '41077': 41,
    '41084': 48,
    '41142': 42,
    '41149': 74,
    '41157': 33,
    '41180': 51,
    '41194': 41,
    '41269': 55,
    '41296': 39
  },
  '41077': {
    '41018': 32,
    '41060': 38,
    '41071': 41,
    '41077': 0,
    '41084': 88,
    '41142': 34,
    '41149': 38,
    '41157': 64,
    '41180': 57,
    '41194': 76,
    '41269': 17,
    '41296': 78
  },
  '41084': {
    '41018': 66,
    '41060': 126,
    '41071': 48,
    '41077': 88,
    '41084': 0,
    '41142': 76,
    '41149': 116,
    '41157': 33,
    '41180': 69,
    '41194': 21,
    '41269': 101,
    '41296': 33
  },
  '41142': {
    '41018': 10,
    '41060': 61,
    '41071': 42,
    '41077': 34,
    '41084': 76,
    '41142': 0,
    '41149': 43,
    '41157': 44,
    '41180': 24,
    '41194': 58,
    '41269': 34,
    '41296': 79
  },
  '41149': {
    '41018': 50,
    '41060': 28,
    '41071': 74,
    '41077': 38,
    '41084': 116,
    '41142': 43,
    '41149': 0,
    '41157': 86,
    '41180': 62,
    '41194': 100,
    '41269': 21,
    '41296': 113
  },
  '41157': {
    '41018': 36,
    '41060': 99,
    '41071': 33,
    '41077': 64,
    '41084': 33,
    '41142': 44,
    '41149': 86,
    '41157': 0,
    '41180': 36,
    '41194': 14,
    '41269': 73,
    '41296': 50
  },
  '41180': {
    '41018': 26,
    '41060': 84,
    '41071': 51,
    '41077': 57,
    '41084': 69,
    '41142': 24,
    '41149': 62,
    '41157': 36,
    '41180': 0,
    '41194': 48,
    '41269': 57,
    '41296': 82
  },
  '41194': {
    '41018': 50,
    '41060': 113,
    '41071': 41,
    '41077': 76,
    '41084': 21,
    '41142': 58,
    '41149': 100,
    '41157': 14,
    '41180': 48,
    '41194': 0,
    '41269': 87,
    '41296': 46
  },
  '41269': {
    '41018': 38,
    '41060': 27,
    '41071': 55,
    '41077': 17,
    '41084': 101,
    '41142': 34,
    '41149': 21,
    '41157': 73,
    '41180': 57,
    '41194': 87,
    '41269': 0,
    '41296': 94
  },
  '41296': {
    '41018': 69,
    '41060': 115,
    '41071': 39,
    '41077': 78,
    '41084': 33,
    '41142': 79,
    '41149': 113,
    '41157': 50,
    '41180': 82,
    '41194': 46,
    '41269': 94,
    '41296': 0
  }
} as const;

export const REFERENTIEL_41: Referentiel = {
  departement: '41',
  libelle: 'Loir-et-Cher',
  secteurs: SECTEURS_41,
  zones: ZONES_41,
  distances: DISTANCES_41,
};
