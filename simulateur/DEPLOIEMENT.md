# Déploiement

La base de données est prête. Il reste le rattachement du dépôt à Vercel, qui demande
la console — je ne peux pas le faire d'ici.

## Ce qui est déjà fait

**Table Postgres** créée sur votre projet Supabase existant
(`hqommdnvponvybjipwsu`, région eu-west-1) :

```
public.dim_scenarios
  id text primary key · departement · nom · version · scenario jsonb
  note · cree_le · modifie_le      + déclencheur sur modifie_le
  index (departement, modifie_le desc)
```

Le préfixe `dim_` évite toute collision avec les tables de l'application de gestion
déjà présente dans ce projet (`techniciens`, `interventions`, `historique`…).

**RLS active, aucune politique.** La table est donc inaccessible aux rôles `anon` et
`authenticated` : rien n'est exposé au navigateur. Seule la clé de service, lue côté
serveur par les routes d'API, la traverse.

## Les trois étapes qui restent

### 1. Créer le projet Vercel depuis le dépôt

Sur vercel.com → **Add New… → Project** → importer
`taoufikhajjitechnosmart-hash/Redimensionnement-d-partement`.

Un seul réglage à changer : **Root Directory = `simulateur`**. Le reste est dans
`vercel.json` (framework, commandes, région Paris).

Passer par l'import Git plutôt que par un téléversement : chaque push redéploie tout
seul, et le déployé reste identique au dépôt.

### 2. Renseigner les deux variables d'environnement

Dans **Settings → Environment Variables** :

| Nom | Valeur |
|---|---|
| `SUPABASE_URL` | `https://hqommdnvponvybjipwsu.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | à copier depuis Supabase → Settings → API → `service_role` |

**Ne préfixez jamais la seconde par `NEXT_PUBLIC_`.** Elle contourne RLS : exposée au
navigateur, elle ouvrirait la table à tout le monde. Je ne l'ai pas récupérée
moi-même, et c'est volontaire — une clé de service n'a pas à transiter par un agent.

Sans ces deux variables l'application démarre quand même, mais elle bascule sur le
stockage fichier, qui ne fonctionne pas sur Vercel : le disque y est en lecture seule.
L'enregistrement répond alors par un message explicite plutôt que par une erreur
obscure.

### 3. Vérifier

Une fois déployé :

- la page se charge et affiche les trois onglets ;
- onglet **Dimensionnement**, préréglage *Existant* : 311 créneaux, 5 alertes sur 12 ;
- bouton **Enregistrer ce scénario** : doit répondre « enregistré » et non un message
  de disque en lecture seule ;
- la ligne apparaît alors dans `public.dim_scenarios`.

## Ce que je n'ai pas pu vérifier

L'aller-retour HTTP vers Supabase depuis l'application. Le conteneur où j'ai travaillé
bloque l'hôte `hqommdnvponvybjipwsu.supabase.co` par politique réseau — la requête
revient en `403 Host not in allowlist`. Ce qui est vérifié en revanche :

- la table, le déclencheur `modifie_le` et l'état RLS, testés directement en SQL ;
- la gestion d'erreur du dépôt, qui a bien remonté le refus réseau sous forme de
  message lisible au lieu de planter ;
- toutes les routes d'API, testées de bout en bout sur le dépôt fichier.

Le premier enregistrement en production est donc le vrai test du chemin Postgres.
S'il échoue, `vercel logs` donnera le code exact renvoyé par PostgREST.

## Développement local

```bash
cd simulateur
npm install
npm test          # 76 tests
npm run dev       # http://localhost:3000
```

Sans variables d'environnement, les scénarios vont dans `web/.donnees/scenarios/`.
Pour travailler sur la base, créez `web/.env.local` avec les deux variables — le
fichier est ignoré par git.
