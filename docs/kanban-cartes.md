# Cartes du Kanban : séance 2

Mise à jour le 12 novembre 2026 d'après la répartition de la séance 2 (elle remplace la version des séances 1-2).

Objectif fin de séance 2 : tout le monde peut coder dès la séance 3. Bonus : un IBAN collé dans ChatGPT est repéré par le proxy.

★ = prioritaire.

## Sur GitHub

Chaque ligne de ce document est **une issue** GitHub intitulée `S2 · NN · <titre> (<personne>)`, avec l'étiquette de filière, plus `prioritaire` (★) ou `bonus`. **Numéro d'issue = numéro de carte + 21.**

| Personne | Cartes | Issues |
| --- | --- | --- |
| Tous (première heure) | 1 à 3 | #22 à #24 |
| Arno | 4 à 7 (+ 31) | #25 à #28 (+ #52) |
| Aloïs | 8 à 12 (+ 36) | #29 à #33 (+ #57) |
| Kiliann | 13 à 16 | #34 à #37 |
| Yarkin (absent, non assigné, repris par Fati) | 17 à 20 | #38 à #41 |
| Fati | 21 à 24 | #42 à #45 |
| Elias | 25 à 28 (+ 18) | #46 à #49 (+ #39) |
| Nolan | 29 à 32 | #50 à #53 |
| Imad | 33 à 36 | #54 à #57 |

## Orga (tous)

| # | Titre de la carte | Assignée à | Étiquette | Terminée quand… |
| --- | --- | --- | --- | --- |
| 1 | ★ Valider la fiche de direction | Tous | orga | Chacun a confirmé qu'on part dessus |
| 2 | ★ Écrire et valider la charte d'équipe | Elias (animation), tous | orga | `docs/charte-equipe.md` validée par les 8 membres |
| 3 | ★ Installer Python 3.11+, Git, Docker, VS Code + accès au dépôt | Tous | orga | Chacun a poussé au moins un commit |

## Cyber

| # | Titre de la carte | Assignée à | Étiquette | Terminée quand… |
| --- | --- | --- | --- | --- |
| 4 | ★ Installer mitmproxy + certificat, voir le trafic HTTPS | Arno | cyber | Une requête HTTPS est visible dans le proxy |
| 5 | ★ Identifier la requête qui transporte le prompt sur chatgpt.com | Arno | cyber | Adresse et format JSON documentés dans `docs/` |
| 6 | ★ Procédure d'installation proxy + certificat | Arno | cyber | Un autre membre installe le proxy en suivant la procédure |
| 7 | Bonus : addon qui extrait le prompt et détecte un IBAN | Arno | cyber | Un événement JSON est écrit dans un fichier |
| 8 | ★ Lister les données sensibles M1 | Aloïs | cyber | Liste IBAN, carte, n° de sécu, SIRET, téléphone, e-mail, clés API, mots de passe |
| 9 | ★ Écrire `rules/m1.yaml` (motif, validation, priorité, action) | Aloïs | cyber | Chaque donnée a sa règle |
| 10 | ★ Cas de test M1 : 3 qui déclenchent, 3 qui ne déclenchent pas | Aloïs | cyber | 6 exemples par règle |
| 11 | Lister les autres sites d'IA à couvrir | Aloïs | cyber | Domaines Gemini, Claude, Mistral, Copilot notés |
| 12 | Note RGPD | Aloïs | cyber | Page RGPD dans `docs/` |
| 13 | ★ Comprendre les téléchargements pip / npm | Kiliann | cyber | Ce que voit le proxy est documenté |
| 14 | ★ Écrire `rules/m2.yaml` avec les seuils de départ | Kiliann | cyber | Règles : inexistant, récent, peu téléchargé, nom proche |
| 15 | ★ 5 à 10 exemples réels de paquets inventés ou piégés | Kiliann | cyber | Liste dans `docs/` |
| 16 | Bonus : script de score de risque via l'API PyPI | Kiliann | cyber | Le script donne un score pour un nom de paquet |

## Dev

| # | Titre de la carte | Assignée à | Étiquette | Terminée quand… |
| --- | --- | --- | --- | --- |
| 17 | ★ Ranger le dépôt (dossiers + README) et donner l'accès | Yarkin | dev | Les 8 membres ont accès, structure à jour |
| 18 | ★ Format commun d'événement | Yarkin, Elias | dev | `docs/format-evenement.md` validé |
| 19 | ★ Schéma d'architecture proxy → API → base → dashboard | Yarkin | dev | Schéma dans `docs/` avec M1, M2 et le modèle |
| 20 | Docker Compose PostgreSQL + API FastAPI vide | Yarkin | dev | `docker compose up` démarre `POST /events` et `GET /alerts` |
| 21 | ★ Maquettes des 4 écrans | Fati | dev | Alertes, détail, réglages, statistiques dans `docs/` |
| 22 | ★ Appliquer la charte graphique | Fati | dev | #0A1A33, #2EE6D6, #FF4D6D, police Inter |
| 23 | ★ Créer le projet front (React + Vite) | Fati | dev | Le projet démarre avec `npm run dev` |
| 24 | Bonus : page « liste des alertes » avec données factices | Fati | dev | Affiche des événements au format commun |

## Data / IA

| # | Titre de la carte | Assignée à | Étiquette | Terminée quand… |
| --- | --- | --- | --- | --- |
| 25 | ★ Remplir le Kanban | Elias | orga | Une carte par tâche de ce document |
| 26 | ★ Format d'événement côté modèle (score, étiquette, explication) | Elias | data | Section validée dans `docs/format-evenement.md` |
| 27 | ★ Étiquettes du classifieur + guide d'annotation | Elias | data | `docs/guide-annotation.md` relu par Nolan |
| 28 | Compte rendu de séance + changements planning / dossier Ydays | Elias | orga | `docs/comptes-rendus/seance-02.md` complété |
| 29 | ★ 150 prompts français réalistes (⅓ non sensibles piégeux) | Nolan | data | 150 lignes dans `data/prompts_v1.csv` |
| 30 | ★ Étiqueter les prompts avec le guide | Nolan | data | Toutes les lignes ont une étiquette |
| 31 | ★ Interface `detect(texte)` entre le proxy et la détection | Nolan, Arno | data | Interface décrite dans `docs/` |
| 32 | Bonus : baseline TF-IDF + régression logistique | Nolan | data | Rappel et taux de fausses alertes mesurés |
| 33 | ★ Tester Presidio en français sur 20 prompts | Imad | data | `data/presidio_test.ipynb` |
| 34 | ★ Trouver un jeu de données public de PII en français | Imad | data | Source notée (ex. ai4privacy) |
| 35 | ★ Fixer les métriques | Imad | data | Rappel, taux de fausses alertes, temps de réponse définis |
| 36 | Comparer règles et modèle | Imad, Aloïs | data | Page « choix du modèle et métriques » |

## Étiquettes à créer

| Étiquette | Couleur conseillée |
| --- | --- |
| dev | bleu |
| cyber | rouge |
| data | vert |
| orga | gris |
| bloquant | orange |
| prioritaire | jaune |
| bonus | violet |
