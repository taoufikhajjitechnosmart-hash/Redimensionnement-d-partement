import { NextResponse } from 'next/server';
import { scenarioSchema, verifierCoherence } from '@sim/domain';
import { depot } from '@/lib/depot';

export const dynamic = 'force-dynamic';

type Contexte = { params: Promise<{ id: string }> };

export async function GET(_requete: Request, { params }: Contexte): Promise<NextResponse> {
  const { id } = await params;
  const enregistre = await depot().lire(id);
  if (!enregistre) return NextResponse.json({ erreur: 'Scénario introuvable.' }, { status: 404 });
  return NextResponse.json(enregistre);
}

export async function PUT(requete: Request, { params }: Contexte): Promise<NextResponse> {
  const { id } = await params;

  let corps: unknown;
  try {
    corps = await requete.json();
  } catch {
    return NextResponse.json({ erreur: 'Corps de requête illisible.' }, { status: 400 });
  }

  const analyse = scenarioSchema.safeParse((corps as { scenario?: unknown })?.scenario ?? corps);
  if (!analyse.success) {
    return NextResponse.json(
      { erreur: 'Scénario invalide.', details: analyse.error.flatten() },
      { status: 422 },
    );
  }
  if (analyse.data.id !== id) {
    return NextResponse.json(
      { erreur: `L'identifiant du corps (${analyse.data.id}) ne correspond pas à l'URL (${id}).` },
      { status: 409 },
    );
  }

  const incoherences = verifierCoherence(analyse.data);
  if (incoherences.length > 0) {
    return NextResponse.json({ erreur: 'Scénario incohérent.', details: incoherences }, { status: 422 });
  }

  const note = typeof (corps as { note?: unknown })?.note === 'string'
    ? (corps as { note: string }).note
    : undefined;

  return NextResponse.json(await depot().enregistrer(analyse.data, note));
}

export async function DELETE(_requete: Request, { params }: Contexte): Promise<NextResponse> {
  const { id } = await params;
  const supprime = await depot().supprimer(id);
  if (!supprime) return NextResponse.json({ erreur: 'Scénario introuvable.' }, { status: 404 });
  return new NextResponse(null, { status: 204 });
}
