import { NextResponse } from 'next/server';
import { importerSuivi } from '@/lib/import-suivi';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

/** 12 Mo : le classeur de suivi complet pèse moins de 300 Ko. */
const TAILLE_MAX = 12 * 1024 * 1024;

export async function POST(requete: Request): Promise<NextResponse> {
  let formulaire: FormData;
  try {
    formulaire = await requete.formData();
  } catch {
    return NextResponse.json({ erreur: 'Requête illisible : envoyez un formulaire.' }, { status: 400 });
  }

  const fichier = formulaire.get('fichier');
  if (!(fichier instanceof File)) {
    return NextResponse.json({ erreur: 'Aucun fichier reçu.' }, { status: 400 });
  }
  if (fichier.size > TAILLE_MAX) {
    return NextResponse.json(
      { erreur: `Fichier trop volumineux : ${Math.round(fichier.size / 1024)} Ko pour 12 Mo au plus.` },
      { status: 413 },
    );
  }
  if (!/\.(xlsx|xlsm|xls)$/i.test(fichier.name)) {
    return NextResponse.json(
      { erreur: `« ${fichier.name} » n'est pas un classeur Excel.` },
      { status: 415 },
    );
  }

  const departement = String(formulaire.get('departement') ?? '41');

  try {
    const resultat = importerSuivi(await fichier.arrayBuffer(), departement);
    return NextResponse.json({
      departement: resultat.departement,
      misAJour: resultat.misAJour,
      inconnus: resultat.inconnus,
      manquants: resultat.manquants,
      dateMaj: resultat.dateMaj,
      secteurs: resultat.referentiel.secteurs.map((s) => ({
        id: s.id,
        nom: s.nom,
        volume: s.volume,
      })),
    });
  } catch (erreur) {
    return NextResponse.json(
      { erreur: erreur instanceof Error ? erreur.message : 'Import impossible.' },
      { status: 422 },
    );
  }
}
