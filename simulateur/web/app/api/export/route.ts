import { NextResponse } from 'next/server';
import { scenarioSchema, verifierCoherence } from '@sim/domain';
import { referentiel as referentielDe } from '@sim/data';
import type { Scenario } from '@sim/engine';
import { construireClasseur } from '@/lib/export-classeur';
import { depot } from '@/lib/depot';

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

/** Un nom de fichier ne doit contenir ni séparateur ni caractère de contrôle. */
const assainir = (nom: string): string =>
  nom
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-zA-Z0-9 _-]/g, '')
    .trim()
    .replace(/\s+/g, '_')
    .slice(0, 60) || 'export';

/** Exporte des scénarios déjà enregistrés : /api/export?ids=a,b&departement=41 */
export async function GET(requete: Request): Promise<NextResponse> {
  const parametres = new URL(requete.url).searchParams;
  const departement = parametres.get('departement') ?? '41';
  const ids = (parametres.get('ids') ?? '').split(',').map((s) => s.trim()).filter(Boolean);

  if (ids.length === 0) {
    return NextResponse.json({ erreur: 'Indiquez au moins un identifiant : ?ids=…' }, { status: 400 });
  }

  const scenarios: Scenario[] = [];
  for (const id of ids) {
    const enregistre = await depot().lire(id);
    if (!enregistre) {
      return NextResponse.json({ erreur: `Scénario « ${id} » introuvable.` }, { status: 404 });
    }
    scenarios.push(enregistre.scenario as Scenario);
  }

  return produire(scenarios, departement);
}

/** Exporte des scénarios envoyés directement, sans passer par l'enregistrement. */
export async function POST(requete: Request): Promise<NextResponse> {
  let corps: unknown;
  try {
    corps = await requete.json();
  } catch {
    return NextResponse.json({ erreur: 'Corps de requête illisible.' }, { status: 400 });
  }

  const brut = (corps as { scenarios?: unknown })?.scenarios;
  if (!Array.isArray(brut) || brut.length === 0) {
    return NextResponse.json({ erreur: 'Envoyez un tableau « scenarios » non vide.' }, { status: 400 });
  }
  if (brut.length > 8) {
    return NextResponse.json({ erreur: 'Huit scénarios au plus par classeur.' }, { status: 422 });
  }

  const scenarios: Scenario[] = [];
  for (const candidat of brut) {
    const analyse = scenarioSchema.safeParse(candidat);
    if (!analyse.success) {
      return NextResponse.json(
        { erreur: 'Scénario invalide.', details: analyse.error.flatten() },
        { status: 422 },
      );
    }
    const incoherences = verifierCoherence(analyse.data);
    if (incoherences.length > 0) {
      return NextResponse.json(
        { erreur: `« ${analyse.data.nom} » est incohérent.`, details: incoherences },
        { status: 422 },
      );
    }
    scenarios.push(analyse.data as Scenario);
  }

  const departement =
    typeof (corps as { departement?: unknown })?.departement === 'string'
      ? (corps as { departement: string }).departement
      : (scenarios[0]?.departement ?? '41');

  return produire(scenarios, departement);
}

function produire(scenarios: readonly Scenario[], departement: string): NextResponse {
  let classeur: Buffer;
  try {
    classeur = construireClasseur(scenarios, referentielDe(departement));
  } catch (erreur) {
    return NextResponse.json(
      { erreur: erreur instanceof Error ? erreur.message : 'Export impossible.' },
      { status: 422 },
    );
  }

  const jour = new Date().toISOString().slice(0, 10);
  const suffixe =
    scenarios.length === 1 ? assainir(scenarios[0]!.nom) : `${scenarios.length}_scenarios`;
  const fichier = `Dimensionnement_${departement}_${suffixe}_${jour}.xlsx`;

  return new NextResponse(new Uint8Array(classeur), {
    headers: {
      'content-type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'content-disposition': `attachment; filename="${fichier}"`,
      'content-length': String(classeur.byteLength),
      'cache-control': 'no-store',
    },
  });
}
