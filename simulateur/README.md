# Simulateur de dimensionnement

Reprise du prototype `Simulateur_Dimensionnement_41.html` sous forme d'application.
Département 41 pour l'instant, modèle prévu pour les autres.

## Démarrer

```bash
npm install
npm test          # 76 tests du moteur
npm run dev       # http://localhost:3000
```

## Découpage

Quatre paquets, le moteur au centre.

```
packages/
  engine/    TypeScript pur, aucune dépendance de production, aucune entrée-sortie
  domain/    schémas zod, versionnés — le contrat des données enregistrées
  data/      référentiels départementaux, générés depuis les fichiers de suivi
web/         Next.js : interface + routes d'API
```

Le moteur ne connaît ni React, ni le réseau, ni le disque. `evaluerScenario(scenario,
referentiel)` est une fonction pure : mêmes entrées, mêmes sorties. C'est ce qui rend
les tests possibles et la refonte sûre.

### `engine`

| Module | Rôle |
|---|---|
| `rythmes` | la règle J+2, l'énumération des rythmes valides, les paires disjointes |
| `demande` | conversion des volumes mensuels en demande hebdomadaire, entièrement paramétrable |
| `distance` | interface `FournisseurDistances` + implémentation géométrique |
| `scenario` | `evaluerScenario` : couverture, alertes, effectif, occupation, kilomètres |
| `affectation` | validateur de règles et solveur glouton par technicien |

### Ajouter un département

Déposer un fichier de la forme de `packages/data/src/dept41.ts` puis l'inscrire dans
`REFERENTIELS`. Aucun code du moteur ni de l'interface n'a à changer. Le générateur
qui produit ce fichier depuis le classeur de suivi est dans `outils/gen_data41.py`.

### Changer de source de distances

Implémenter `FournisseurDistances` et le passer en troisième argument de
`evaluerScenario`. L'implémentation par défaut est une approximation géométrique
(orthodromique × 1,25) ; un fournisseur adossé à un service d'itinéraires se
substitue à elle sans toucher au reste.

### Changer de stockage

`web/lib/depot.ts` définit `DepotScenarios`, seul contrat que connaissent les routes
d'API. L'implémentation actuelle écrit des fichiers JSON dans `.donnees/`, ce qui
suffit à un usage local. Une implémentation Postgres se substitue à elle sans qu'aucune
route ne change.

## API

| Méthode | Route | Effet |
|---|---|---|
| `GET` | `/api/scenarios?departement=41` | liste |
| `POST` | `/api/scenarios` | crée ou remplace |
| `GET` | `/api/scenarios/:id` | lit |
| `PUT` | `/api/scenarios/:id` | remplace |
| `DELETE` | `/api/scenarios/:id` | supprime |

Tout scénario est validé par le schéma zod puis par `verifierCoherence` avant
enregistrement. Un passage le samedi dans un scénario de cinq jours est refusé en 422.

## Tests

76 tests. Deux catégories :

- **règles et formules** — la règle J+2 comparée au moteur de référence sur toutes
  les parties de la semaine, l'énumération des rythmes, la répartition des créneaux,
  le validateur d'affectation.
- **non-régression** — les grandeurs du tableau de référence qui ne dépendent pas de
  l'hypothèse de demande : offre ouverte, alertes J+2, effectif, occupation,
  kilomètres, pour les trois scénarios.

| Scénario | Offre | Alertes | Techniciens | Occupation | Km/sem |
|---|---|---|---|---|---|
| Existant | 311 | 5 / 12 | 10 | 86 % | 1 514 |
| Cible, 6 jours | 190 | 0 / 12 | 8 | 66 % | 1 440 |
| Cible, 5 jours | 190 | 0 / 12 | 8 | 79 % | 1 388 |

La **couverture** est délibérément absente de ce tableau : c'est la seule colonne qui
dépende de l'hypothèse de demande, et cette hypothèse n'est pas tranchée. Voir plus bas.

## Ce qui n'est pas tranché

**Aucun volume SAV mesuré n'existe dans les fichiers sources.** Deux analyses du même
département ont conclu l'une à 141 interventions PROD par semaine, l'autre à 185, à
partir des mêmes lignes de suivi. L'écart se décompose en trois choix, tous exposés
dans `ParamsDemande` :

| | Étude antérieure | Conversion fidèle au fichier |
|---|---|---|
| Mois retenu | moyenne octobre / mars | le plus chargé des deux |
| Passage au hebdomadaire | moyenne journalière × 22 jours | volume mensuel ÷ 4,333 |
| B2B | non compté | compté |
| Marge | aucune | +10 % |
| **Résultat** | **141** | **185** |

Le deuxième point est le plus lourd : les mois relevés comptent 25 jours ouvrés en
octobre et 24 en mars — le test `demande.test.ts` le vérifie secteur par secteur. Les
projeter sur 22 jours minore la demande d'environ 12 %.

Tant que le SAV réel n'est pas relevé, aucun total de demande n'est figé en test.
Les deux paramétrages sont fournis (`PARAMS_VOLUME_PIC`, `PARAMS_MOYENNE_22J`) et
l'interface laisse modifier mois, marge et méthode.

## Réserves à ne pas masquer

Elles sont affichées en tête de l'application et doivent le rester.

- Le SAV ne peut pas être garanti à 100 % : les arrivées sont aléatoires, on vise un
  taux de service.
- Les distances sont approchées, pas des temps de trajet réels.
- L'effectif calculé est un minimum structurel : journée de pointe par zone, sans
  absences, congés ni enchaînements inter-zones. Prévoir au moins un poste de plus.
- Le samedi coûte environ 4 % de kilomètres de plus. Il se justifie par le lissage de
  charge et le délai client, pas par l'économie de trajets.

## Les trois onglets

**Dimensionnement** — réglages, indicateurs, tableau des secteurs avec créneaux et
jours de passage modifiables, quatre graphiques, liste des alertes.

**Grille par technicien** — glisser-déposer entre une réserve de créneaux et les cases
technicien/jour. Les règles sont contrôlées à chaque dépôt : capacité, secteurs par
journée, distance d'enchaînement, régime du technicien. Les cases en infraction sont
marquées et le motif exact listé. Le bouton *Proposer une répartition* appelle le
solveur glouton ; ce qu'il ne place pas reste visible dans la réserve.

**Import** — lecture du classeur de suivi, rapprochement des libellés GRDV insensible
aux accents, rapport d'écart secteur par secteur avant application. Les secteurs
inconnus du référentiel sont signalés, jamais devinés : sans coordonnées ni zone ils ne
peuvent pas entrer dans un calcul de distances.

## Déploiement

Voir `DEPLOIEMENT.md`. La table Postgres est créée ; restent le rattachement du dépôt à
Vercel et les deux variables d'environnement.

## Reste à faire

- Export du classeur de restitution depuis l'application.
- Comparaison de plusieurs scénarios côte à côte.
- Départements 37, 44 et 49 — un fichier de données par département, aucun code.
- Fournisseur de distances réelles à la place de l'approximation géométrique.
