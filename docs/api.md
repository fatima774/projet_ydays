# API CyberSentinel

L'API fait le lien entre le proxy, la base et le tableau de bord. Elle tourne sur http://localhost:3000.

```
Proxy (addon)  --POST /events-->  API Node.js  -->  MySQL
Tableau de bord  <--GET /alerts--  API Node.js  <--  MySQL
```

## Stack

| Partie | Technologie |
| --- | --- |
| API | Node.js 22 + Express 5 |
| Base de données | MySQL 8.4 |
| Lancement | Docker Compose (`docker compose up`) |
| Tableau de bord | React + Vite (`frontend/`) |

Le proxy et la détection (`detect()`, règles, modèle) restent en Python : ils parlent à l'API en HTTP et en JSON, le langage de l'API ne change rien pour eux.

## Décisions prises sur le format d'événement

Ce sont les 4 points de [`format-evenement.md`](format-evenement.md) à trancher côté API :

| Question | Décision |
| --- | --- |
| Noms des champs : français ou anglais ? | **Français**, exactement comme dans `format-evenement.md` |
| Ajouter `requete_id` ? | **Oui**, facultatif. Un UUID commun aux événements d'une même requête (un événement par donnée détectée) |
| `source.module` : champ à part ou déduit de `regle` ? | **Champ à part**, obligatoire (`M1`, `M2` ou `M3`) |
| Table : une colonne par champ ou JSON ? | **Une colonne par champ** (table `evenements`) : plus simple pour filtrer et compter |

L'API ajoute 3 champs pour le suivi : `statut` (`nouveau` par défaut), `commentaire` et `recu_le`.

## Routes

### `GET /health`

Vérifie que l'API et la base répondent.

```json
{ "statut": "ok", "base": "ok" }
```

### `POST /events` (le proxy)

Reçoit **un** événement ou une **liste** d'événements (50 maximum), au format de `format-evenement.md`.

| Réponse | Quand |
| --- | --- |
| `201` `{ "enregistres": 2, "ids": [...] }` | Tout est enregistré |
| `400` `{ "erreur": "...", "details": ["score : nombre entre 0 et 1", ...] }` | Un champ manque ou est incorrect : rien n'est enregistré |
| `409` | Un événement avec le même `id` existe déjà |

Rappels du format : `date` en UTC (`2026-11-12T10:42:07Z`), `score` entre 0 et 1, `etiquette` obligatoire pour M1, `extrait_masque` de 200 caractères maximum, **jamais la donnée en clair**.

### `GET /alerts` (le tableau de bord)

Liste les alertes, les plus récentes d'abord. Les événements dont l'action est `laisser` ne sont pas des alertes et n'apparaissent pas.

Filtres facultatifs, à combiner : `action`, `type_donnee`, `site_ia`, `module`, `statut`, `depuis` (date ISO). Pagination : `limite` (50 par défaut, 200 au maximum) et `decalage`.

Exemple : `GET /alerts?action=bloquer&statut=nouveau&limite=20`

```json
{
  "total": 1,
  "limite": 20,
  "decalage": 0,
  "alertes": [
    {
      "id": "6f1c2b0e-8a4d-4c1e-9f3a-2d7b5e0c9a11",
      "requete_id": "…",
      "date": "2026-11-12T10:42:07.000Z",
      "source": { "poste": "pc-test-01", "module": "M1" },
      "site_ia": "chatgpt.com",
      "type_donnee": "IBAN",
      "regle": "m1.iban",
      "detecteur": "regle",
      "score": 1,
      "etiquette": "finance",
      "explication": "IBAN français valide (clé de contrôle correcte) détecté dans le prompt.",
      "action": "bloquer",
      "extrait_masque": "…virer 1 200 € sur FR76 **** **** **** **** **** 189 avant…",
      "version_modele": null,
      "latence_ms": 4,
      "statut": "nouveau",
      "commentaire": null,
      "recu_le": "2026-11-12T10:42:07.120Z"
    }
  ]
}
```

### `GET /alerts/:id`

Le détail d'une alerte (même format qu'une ligne de la liste). `404` si elle n'existe pas.

### `PATCH /alerts/:id`

L'analyste change le statut et/ou ajoute un commentaire.

```json
{ "statut": "traite", "commentaire": "Utilisateur prévenu" }
```

Statuts possibles : `nouveau`, `en_cours`, `traite`, `faux_positif`.

## Ce qui reste à faire

- **Authentification** (connexion, rôles analyste et administrateur) : pas encore en place. L'API ne doit tourner que sur le réseau de test.
- **`GET /stats`** pour la page Statistiques.
- **Réglages** (action par type de donnée) lus par le proxy.
