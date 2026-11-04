# Règles de travail

## 1. On ne code jamais directement sur `main`

`main` contient uniquement du code qui marche. Pour chaque tâche, on crée une branche :

| Type | Nom de la branche | Exemple |
| --- | --- | --- |
| Nouvelle fonctionnalité | `feature/<sujet>` | `feature/detection-iban` |
| Correction | `fix/<sujet>` | `fix/import-csv` |
| Documentation | `docs/<sujet>` | `docs/rgpd` |

```bash
git checkout main
git pull
git checkout -b feature/detection-iban
```

## 2. Des messages de commit clairs

Format : `type: ce qui a été fait`

- `feat: détection des IBAN dans les prompts`
- `fix: le proxy plante sur les requêtes vides`
- `docs: ajout de la page RGPD`
- `test: tests des règles IBAN`

## 3. Une Pull Request relue avant de fusionner

1. Pousser sa branche : `git push -u origin feature/detection-iban`
2. Ouvrir une Pull Request sur GitHub vers `main`.
3. Lier la carte du Kanban (écrire `Closes #12` dans la description).
4. **Une autre personne relit et valide** avant la fusion.

## 4. Le Kanban est à jour

- On prend une carte → on la met dans **En cours** et on s'assigne.
- On ouvre une Pull Request → **En relecture**.
- C'est fusionné → **Terminé**.
- On est bloqué → on le dit tout de suite dans le groupe.

## 5. Jamais de secrets dans le dépôt

Pas de mots de passe, clés API, certificats ou vraies données. Ils vont dans un fichier `.env` (ignoré par Git). Le modèle à suivre est `.env.example`.
