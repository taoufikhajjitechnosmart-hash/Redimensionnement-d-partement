import { NextResponse } from 'next/server';
import { scenarioSchema, verifierCoherence } from '@sim/domain';
import { depot } from '@/lib/depot';

export const dynamic = 'force-dynamic';

export async function GET(requete: Request): Promise<NextResponse> {
  const departement = new URL(requete.url).searchParams.get('departement') ?? undefined;
  const scenarios = await depot().lister(departement);
  return NextResponse.json({ scenarios });
}

export async function POST(requete: Request): Promise<NextResponse> {
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

  const incoherences = verifierCoherence(analyse.data);
  if (incoherences.length > 0) {
    return NextResponse.json({ erreur: 'Scénario incohérent.', details: incoherences }, { status: 422 });
  }

  const note = typeof (corps as { note?: unknown })?.note === 'string'
    ? (corps as { note: string }).note
    : undefined;

  const enregistre = await depot().enregistrer(analyse.data, note);
  return NextResponse.json(enregistre, { status: 201 });
}
