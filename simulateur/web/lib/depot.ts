import { mkdir, readFile, readdir, unlink, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { depotSupabase } from './depot-supabase';
import {
  migrerScenario,
  scenarioEnregistreSchema,
  VERSION_SCHEMA,
  type Scenario,
  type ScenarioEnregistre,
} from '@sim/domain';

/**
 * Dépôt des scénarios.
 *
 * L'interface est le seul contrat que connaissent les routes d'API. Elle est
 * satisfaite aujourd'hui par des fichiers JSON, ce qui suffit à un usage local
 * et évite d'imposer une base de données pour démarrer. Le jour où plusieurs
 * personnes doivent partager leurs scénarios, une implémentation adossée à
 * Postgres se substitue à celle-ci sans qu'aucune route ne change.
 */
export interface DepotScenarios {
  lister(departement?: string): Promise<ScenarioEnregistre[]>;
  lire(id: string): Promise<ScenarioEnregistre | null>;
  enregistrer(scenario: Scenario, note?: string): Promise<ScenarioEnregistre>;
  supprimer(id: string): Promise<boolean>;
}

const RACINE = process.env.SIM_DONNEES ?? path.join(process.cwd(), '.donnees', 'scenarios');

/** Un identifiant ne doit jamais pouvoir désigner un fichier hors du dépôt. */
const identifiantValide = (id: string): boolean => /^[a-zA-Z0-9_-]{1,64}$/.test(id);

function chemin(id: string): string {
  if (!identifiantValide(id)) throw new RangeError(`Identifiant de scénario invalide : « ${id} »`);
  return path.join(RACINE, `${id}.json`);
}

export function depotFichier(): DepotScenarios {
  return {
    async lister(departement) {
      await mkdir(RACINE, { recursive: true });
      const fichiers = (await readdir(RACINE)).filter((f) => f.endsWith('.json'));
      const enregistres: ScenarioEnregistre[] = [];
      for (const fichier of fichiers) {
        try {
          const brut = JSON.parse(await readFile(path.join(RACINE, fichier), 'utf8'));
          const enregistre = migrerScenario(brut);
          if (!departement || enregistre.scenario.departement === departement) {
            enregistres.push(enregistre);
          }
        } catch {
          // Un fichier corrompu ne doit pas empêcher de lire les autres.
        }
      }
      return enregistres.sort((a, b) => b.modifieLe.localeCompare(a.modifieLe));
    },

    async lire(id) {
      try {
        const brut = JSON.parse(await readFile(chemin(id), 'utf8'));
        return migrerScenario(brut);
      } catch (erreur) {
        if ((erreur as NodeJS.ErrnoException).code === 'ENOENT') return null;
        throw erreur;
      }
    },

    async enregistrer(scenario, note) {
      try {
        await mkdir(RACINE, { recursive: true });
      } catch (erreur) {
        const code = (erreur as NodeJS.ErrnoException).code;
        // Hébergement sans disque inscriptible : le dire clairement plutôt que
        // de laisser remonter un EROFS incompréhensible.
        if (code === 'EROFS' || code === 'EACCES' || code === 'EPERM') {
          throw new Error(
            "Ce serveur n'a pas de disque inscriptible : renseignez SUPABASE_URL et " +
              'SUPABASE_SERVICE_ROLE_KEY pour enregistrer les scénarios en base.',
          );
        }
        throw erreur;
      }
      const existant = await this.lire(scenario.id);
      const maintenant = new Date().toISOString();
      const enregistre = scenarioEnregistreSchema.parse({
        version: VERSION_SCHEMA,
        scenario,
        creeLe: existant?.creeLe ?? maintenant,
        modifieLe: maintenant,
        ...(note !== undefined ? { note } : existant?.note !== undefined ? { note: existant.note } : {}),
      });
      // Écriture atomique : un plantage en cours d'écriture ne corrompt rien.
      const cible = chemin(scenario.id);
      const provisoire = `${cible}.${process.pid}.tmp`;
      await writeFile(provisoire, JSON.stringify(enregistre, null, 2), 'utf8');
      const { rename } = await import('node:fs/promises');
      await rename(provisoire, cible);
      return enregistre;
    },

    async supprimer(id) {
      try {
        await unlink(chemin(id));
        return true;
      } catch (erreur) {
        if ((erreur as NodeJS.ErrnoException).code === 'ENOENT') return false;
        throw erreur;
      }
    },
  };
}

let instance: DepotScenarios | undefined;

/**
 * Dépôt courant.
 *
 * Postgres dès que `SUPABASE_URL` et `SUPABASE_SERVICE_ROLE_KEY` sont présentes,
 * fichiers JSON sinon. Le repli permet de travailler en local sans base et fait
 * que l'application démarre même mal configurée, plutôt que d'échouer au
 * chargement.
 */
export function depot(): DepotScenarios {
  if (instance) return instance;

  const url = process.env.SUPABASE_URL;
  const cle = process.env.SUPABASE_SERVICE_ROLE_KEY;
  instance = url && cle ? depotSupabase(url, cle) : depotFichier();
  return instance;
}

/** Mode de stockage effectif, affiché dans l'interface. */
export function modeStockage(): 'postgres' | 'fichier' {
  return process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY ? 'postgres' : 'fichier';
}
