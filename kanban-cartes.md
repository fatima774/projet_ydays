# Cartes du Kanban : séances 1 et 2

Objectif fin de séance 2 : un IBAN collé dans ChatGPT est repéré par le proxy et apparaît dans la base.

Créer une carte (Issue) par ligne, l'assigner à la personne et ajouter l'étiquette de sa filière.

| # | Titre de la carte | Assignée à | Étiquette | Terminée quand… |
| --- | --- | --- | --- | --- |
| 1 | Valider la nouvelle direction et répartir les modules | Elias, Imad | orga | Chaque membre a un module, noté dans le README |
| 2 | Mettre à jour la fiche Ydays | Imad | orga | La fiche décrit le projet proxy + modules |
| 3 | Créer le dépôt GitHub et pousser le squelette | Fati | dev | Tout le monde a cloné le dépôt |
| 4 | Créer le Kanban et les cartes des séances 1-2 | Yarkin | dev | Les cartes sont créées et assignées |
| 5 | Installer mitmproxy + certificat sur un PC de test | Arno | cyber | Une requête vers ChatGPT est visible dans le proxy |
| 6 | Règles de détection : IBAN, n° de sécu, carte, clé API | Aloïs | cyber | Chaque règle a un exemple qui déclenche et un qui ne déclenche pas |
| 7 | Cadre RGPD et règles d'usage du proxy | Kiliann | cyber | La page `docs/README.md` est complétée |
| 8 | Brancher les règles dans le proxy | Nolan | data | Un IBAN collé dans ChatGPT déclenche une alerte |
| 9 | Squelette API FastAPI + PostgreSQL, route `POST /events` | Fati | dev | Le proxy envoie un événement, il est enregistré en base |
| 10 | Squelette React : page qui liste les événements | Yarkin | dev | Les événements de la base s'affichent |
| 11 | Jeu de prompts : 100 premiers exemples étiquetés | Elias, Imad | data | Fichier CSV avec 100 prompts « sensible / pas sensible » |

## Étiquettes à créer

| Étiquette | Couleur conseillée |
| --- | --- |
| dev | bleu |
| cyber | rouge |
| data | vert |
| orga | gris |
| bloquant | orange |
