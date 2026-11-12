# backend/

API CyberSentinel en **Node.js (Express)** avec une base **MySQL**. Elle reçoit les événements du proxy et les fournit au tableau de bord.

Responsable : Fati (reprise des cartes de Yarkin).

## Lancer avec Docker (recommandé)

Depuis la racine du dépôt :

```bash
docker compose up --build
```

- La base MySQL démarre et la table `evenements` est créée automatiquement (`db/init.sql`).
- L'API répond sur http://localhost:3000. Vérification : http://localhost:3000/health

Pour arrêter : `Ctrl + C`, puis `docker compose down`. Pour **effacer aussi la base** : `docker compose down -v`.

## Envoyer des événements de test

Dans un autre terminal, l'API étant lancée :

```bash
cd backend
npm install
npm run exemples
```

Trois faux événements (IBAN bloqué, e-mail masqué, paquet suspect) sont enregistrés. Ils apparaissent sur http://localhost:3000/alerts

## Lancer les tests

```bash
cd backend
npm install
npm test
```

Les tests utilisent une fausse base en mémoire : MySQL n'a pas besoin de tourner.

## Organisation

| Fichier | Rôle |
| --- | --- |
| `src/server.js` | Point d'entrée : lit la configuration et démarre l'API |
| `src/app.js` | Les routes (`/events`, `/alerts`…) |
| `src/validation.js` | Vérifie qu'un événement respecte le format commun |
| `src/db.js` | Toutes les requêtes SQL |
| `db/init.sql` | Création de la table `evenements` |
| `scripts/envoyer-exemples.js` | Envoie 3 faux événements à l'API |
| `test/api.test.js` | Tests automatiques des routes |

Les routes sont décrites dans [`docs/api.md`](../docs/api.md).
