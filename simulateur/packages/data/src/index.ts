import type { Referentiel } from '@sim/engine';
import { REFERENTIEL_41 } from './dept41';

export * from './dept41';
export * from './scenarios41';
export * from './techniciens41';

/**
 * Référentiels disponibles, indexés par code département.
 *
 * Seul le 41 est renseigné à ce jour. Ajouter le 37, le 44 ou le 49 consiste à
 * déposer un fichier de la même forme puis à l'inscrire ici — aucun code du
 * moteur ni de l'interface n'a à changer.
 */
export const REFERENTIELS: Readonly<Record<string, Referentiel>> = {
  '41': REFERENTIEL_41,
};

export const DEPARTEMENTS_DISPONIBLES = Object.keys(REFERENTIELS);

export function referentiel(departement: string): Referentiel {
  const trouve = REFERENTIELS[departement];
  if (!trouve) {
    throw new RangeError(
      `Aucun référentiel pour le département ${departement}. Disponibles : ${DEPARTEMENTS_DISPONIBLES.join(', ')}.`,
    );
  }
  return trouve;
}
