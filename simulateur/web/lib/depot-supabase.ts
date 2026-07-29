import {
  migrerScenario,
  VERSION_SCHEMA,
  type Scenario,
  type ScenarioEnregistre,
} from '@sim/domain';
import type { DepotScenarios } from './depot';

/**
 * Dépôt adossé à Postgres, via l'API REST de Supabase.
 *
 * La table `public.dim_scenarios` a RLS active et aucune politique : elle est
 * donc inaccessible aux rôles `anon` et `authenticated`. Seule la clé de service,
 * lue côté serveur uniquement, la traverse. Cette clé ne doit jamais être
 * préfixée `NEXT_PUBLIC_` : elle contournerait alors RLS depuis le navigateur.
 */

const TABLE = 'dim_scenarios';

interface Ligne {
  id: string;
  departement: string;
  nom: string;
  version: number;
  scenario: Scenario;
  note: string | null;
  cree_le: string;
  modifie_le: string;
}

function versEnregistre(ligne: Ligne): ScenarioEnregistre {
  return migrerScenario({
    version: ligne.version,
    scenario: ligne.scenario,
    creeLe: new Date(ligne.cree_le).toISOString(),
    modifieLe: new Date(ligne.modifie_le).toISOString(),
    ...(ligne.note !== null ? { note: ligne.note } : {}),
  });
}

export function depotSupabase(url: string, cle: string): DepotScenarios {
  const base = `${url.replace(/\/$/, '')}/rest/v1/${TABLE}`;
  const entetes = {
    apikey: cle,
    authorization: `Bearer ${cle}`,
    'content-type': 'application/json',
  };

  async function appeler(chemin: string, init?: RequestInit): Promise<Response> {
    const reponse = await fetch(`${base}${chemin}`, {
      ...init,
      headers: { ...entetes, ...(init?.headers ?? {}) },
      cache: 'no-store',
    });
    if (!reponse.ok && reponse.status !== 406) {
      const detail = await reponse.text().catch(() => '');
      throw new Error(`Supabase ${reponse.status} sur ${TABLE} : ${detail.slice(0, 300)}`);
    }
    return reponse;
  }

  return {
    async lister(departement) {
      const filtre = departement ? `&departement=eq.${encodeURIComponent(departement)}` : '';
      const reponse = await appeler(`?select=*${filtre}&order=modifie_le.desc`);
      const lignes = (await reponse.json()) as Ligne[];
      // Un enregistrement illisible ne doit pas masquer les autres.
      return lignes.flatMap((l) => {
        try {
          return [versEnregistre(l)];
        } catch {
          return [];
        }
      });
    },

    async lire(id) {
      const reponse = await appeler(`?select=*&id=eq.${encodeURIComponent(id)}&limit=1`);
      const lignes = (await reponse.json()) as Ligne[];
      return lignes[0] ? versEnregistre(lignes[0]) : null;
    },

    async enregistrer(scenario, note) {
      const existant = await this.lire(scenario.id);
      const corps = {
        id: scenario.id,
        departement: scenario.departement,
        nom: scenario.nom,
        version: VERSION_SCHEMA,
        scenario,
        note: note ?? existant?.note ?? null,
      };
      const reponse = await appeler('?on_conflict=id', {
        method: 'POST',
        headers: { prefer: 'resolution=merge-duplicates,return=representation' },
        body: JSON.stringify(corps),
      });
      const lignes = (await reponse.json()) as Ligne[];
      if (!lignes[0]) throw new Error("L'enregistrement n'a rien renvoyé.");
      return versEnregistre(lignes[0]);
    },

    async supprimer(id) {
      const reponse = await appeler(`?id=eq.${encodeURIComponent(id)}`, {
        method: 'DELETE',
        headers: { prefer: 'return=representation' },
      });
      const lignes = (await reponse.json()) as Ligne[];
      return lignes.length > 0;
    },
  };
}
