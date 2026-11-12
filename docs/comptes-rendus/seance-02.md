# Compte rendu, séance 2 (12 novembre 2026)

Rédigé par Elias, d'après le point d'Arno après la séance 2 et l'état de `main` en fin de séance (après fusion des PR #65 à #71).

## Objectif de la journée

Rattraper le cadrage de la séance 1 et lancer la conception, pour que tout le monde puisse coder dès la séance 3.

## En bref

Toutes les briques du module M1 existent, mais elles ne sont pas encore **branchées de bout en bout**. Le proxy voit les requêtes des 5 IA prioritaires, l'addon d'Arno extrait le prompt et appelle `detect()`, les règles d'Aloïs tournent, le format d'événement est fixé, et l'API Node.js avec sa base MySQL démarre avec Docker Compose. Le tableau de bord lit déjà les alertes de l'API. Tout est fusionné dans `main` en fin de séance. Il reste à relier l'addon à l'API pour que la chaîne marche de bout en bout. M2 (paquets inventés) a ses 4 premières règles, sans exemples ni code pour l'instant.

## Présents / absents

| Membre | Présent | Remarque |
| --- | --- | --- |
| Elias | ✅ | OK |
| Imad | ✅ | OK |
| Nolan | ✅ | OK |
| Arno | ✅ | OK |
| Aloïs | ✅ | OK |
| Kiliann | ✅ | OK |
| Yarkin | ❌ | Absent, ses cartes ont été reprises par Fati (binôme) |
| Fati | ✅ | OK |

## Avancement des objectifs

| # | Objectif | État | Commentaire |
| --- | --- | --- | --- |
| 1 | Charte d'équipe, rôles et Kanban rempli | ✅ | OK |
| 2 | Dépôt rangé, chacun a poussé au moins un commit | 🟡 | Dépôt rangé ; Yarkin (absent) n'a pas encore de commit |
| 3 | Conception : architecture, format d'événement, maquettes, règles M1 et M2 | ✅ | OK : règles M2 écrites, leurs exemples restent à remplir |
| 4 | Le proxy voit le trafic ChatGPT (bonus : repère un IBAN) | ✅ | OK : 5 IA, et l'addon v1 détecte un IBAN (dans `main`) |
| 5 | Premier lot de prompts français étiquetés | ✅ | OK : 150 prompts |

## Ce qu'on a (livrables par personne)

| Brique | Qui | État | Où |
| --- | --- | --- | --- |
| Proxy mitmproxy + certificat + procédure | Arno | ✅ Fait, testé par Kiliann | `docs/proxy-installation-windows.md` |
| Où passe le prompt (ChatGPT, Gemini, Mistral, Claude, Copilot) | Arno | ✅ Fait (sans compte, sauf Claude) | `docs/captures-sites-ia.md` |
| Addon CyberSentinel M1 v1 : 5 IA, `detect()`, événements JSON dans un fichier | Arno | 🟡 Fait, dans `main` (PR #70) ; pas encore relié à l'API | `proxy/cybersentinel.py` |
| Liste des sites d'IA, v2 corrigée avec les captures d'Arno | Aloïs | ✅ Fait, dans `main` (PR #70) | `rules/sites_ia.yaml`, `docs/sites-ia.md` |
| Règles M1 (8 règles, 49/49 exemples OK) | Aloïs | ✅ Fait, dans `main` | `rules/m1.yaml`, `rules/m1_detect.py` |
| Note RGPD | Aloïs | ✅ Fait | `docs/rgpd.md` |
| Interface `detect(texte)` + code | Arno, Nolan | ✅ v1, dans `main` | `docs/detect.md`, `detection/detect.py` |
| 150 prompts français étiquetés, au format du guide d'annotation | Nolan | ✅ Fait | `data/prompts_v1.csv`, `docs/prompts_v1.md` |
| Modèle baseline TF-IDF | Nolan | 🟡 Fait, mais faible (rappel 41 %, fausses alertes 5 %) | `data/baseline.py`, `docs/detect.md` |
| Test Presidio + métriques cibles | Imad | ✅ Fait | `docs/choix-modele-metriques.md` |
| Charte d'équipe, guide d'annotation, Kanban | Elias | ✅ Fait | `docs/` |
| Format d'événement | Elias | ✅ Fait, les 4 points ont été tranchés côté API | `docs/format-evenement.md`, `docs/api.md` |
| Maquettes des 4 écrans | Fati | ✅ Fait | `docs/maquettes/` |
| Front React + Vite : page « liste des alertes » | Fati | ✅ Faite, lit `GET /alerts` toutes les 10 s (PR #71) ; les 3 autres écrans restent à coder | `frontend/` |
| API Node.js (Express) + base MySQL + Docker Compose | Fati (cartes de Yarkin) | ✅ Fait, routes testées | `backend/`, `docs/api.md` |
| Schéma d'architecture | Fati (carte de Yarkin) | ✅ Fait | `docs/architecture.md` |
| Règles M2 (4 règles : très récent, peu téléchargé, nom proche, inexistant) | Kiliann | 🟡 Règles écrites, exemples à remplir | `rules/m2.yaml` |

## Mesures de la détection

Mesurées par Imad sur la première version des 150 prompts (`docs/choix-modele-metriques.md`). Nolan a depuis réétiqueté le jeu selon le guide (18 prompts par catégorie sensible) : les mesures seront à refaire en séance 3.

| Métrique | Règles M1 seules | Règles M1 + Presidio | Objectif |
| --- | --- | --- | --- |
| Rappel | 60 % | 88 % | ≥ 90 % |
| Rappel critique (IBAN, carte, n° de sécu, clés, mots de passe) | 72 % | 72 % | ≥ 95 % |
| Fausses alertes | 8 % | 17 % | ≤ 10 % |
| Temps par prompt (95ᵉ centile) | 0,1 ms | 8,3 ms | ≤ 50 ms |

Points faibles des règles seules, sur cette première version (`data/resultats/prompts_rappel_par_type.csv`) : mots de passe 1/8, santé 0/12, noms de personnes 0/51.

## Décisions prises

- **Kanban** : une issue GitHub par tâche (#22 à #57), avec l'étiquette de filière plus `prioritaire` ou `bonus`.
- **Étiquettes du classifieur** : `non_sensible`, `identite`, `finance`, `sante`, `secret_technique`, `donnees_clients` (`docs/guide-annotation.md`).
- **Pile de l'API** : Node.js (Express) + MySQL au lieu de FastAPI + PostgreSQL. Le proxy et la détection restent en Python et parlent à l'API en HTTP et en JSON.
- **Format d'événement** (`docs/api.md`) : champs en français ; `requete_id` ajouté (facultatif, un événement par donnée détectée) ; `source.module` est un champ à part ; une colonne par champ dans la table `evenements`.
- **Dossiers** : `backend/` et `frontend/` sont gardés.
- **Sites d'IA** : ChatGPT sans compte passe par `/unauth-mweb/conversation/updates` ; Gemini envoie le prompt à `geminiweb-pa.clients6.google.com` (l'ancien chemin `StreamGenerate` est abandonné).
- **Fin de séance** : tout est fusionné dans `main` (PR #65 à #71). L'ancien prototype `proxy/addon.py` est supprimé, remplacé par `proxy/cybersentinel.py`.

## Ce qui manque pour une démo

Aucun prompt ne va encore du navigateur jusqu'au tableau de bord : l'API et la page des alertes sont reliées, mais pas l'addon. Il reste à :

1. **Relier l'addon à l'API** (Arno) : l'addon écrit aujourd'hui ses événements dans `logs/evenements.jsonl` ; il doit les envoyer à `POST /events`.
2. **Les réglages** : une route que le proxy lira pour savoir s'il faut bloquer, masquer ou alerter chaque type de donnée.

Ensuite seulement : bloquer ou masquer pour de vrai, M2 dans le proxy (pip, npm), un modèle qui monte le rappel.

## Risques

| Risque | Pourquoi | Parade proposée |
| --- | --- | --- |
| Branches qui divergent | Le travail avance sur 4 branches ; tout a été fusionné en fin de séance 2, mais il faut le refaire à chaque séance | Une PR vers `main` en fin de chaque séance, relue par une autre filière |
| Les sites d'IA changent leurs requêtes | Gemini a déjà changé de domaine ; le mode connecté de ChatGPT n'est pas encore capturé | Refaire les captures avant la démo ; méthode de secours « texte lisible » dans l'addon |
| Rappel trop bas | 60 % avec les règles seules, 88 % avec Presidio mais 17 % de fausses alertes | Renforcer les règles secrets (Aloïs) ; Presidio limité aux noms ; un classifieur |
| Bloquer casse la page de l'IA | Une réponse 403 au milieu d'un flux peut faire planter l'interface | Commencer par **alerter** seulement, bloquer/masquer à partir de la séance 5 |
| M2 en retard | Les règles M2 n'ont encore ni exemples ni code | Kiliann remplit les exemples en séance 3, avec son binôme Arno |
| L'API n'est protégée par aucun mot de passe | Elle n'a ni connexion ni rôles | Ne la lancer que sur le réseau de test |

## Changements pour le planning et le dossier Ydays

- La séance 1 n'a servi qu'à une mise en place légère : la séance 2 a rattrapé le cadrage et lancé la conception.
- La pile de l'API change : Node.js + MySQL.
- Jalons proposés au point d'équipe, à valider en séance 3 : **démo M1 complète à la fin de la séance 5**, M2 à la fin de la séance 7, puis bonus M3/M4 si on est dans les temps (règle d'or de la fiche de direction).

| | Séance 3 | Séances 4 et 5 | Séances 6 et 7 | Séances 8 à 11 |
| --- | --- | --- | --- | --- |
| Jalon | Un faux IBAN dans ChatGPT arrive dans la base | Démo M1 complète | M1 + M2 finis, bonus ? | Soutenance |
| **Cyber** (Arno, Aloïs, Kiliann) | Addon relié à l'API, secrets M1, exemples M2 | Alerter puis bloquer, M2 dans le proxy | Masquer en direct, M2 bloque pip/npm, lab VM de démo | Bonus M3 agents IA, tests d'attaque, démo finale |
| **Dev** (Fati, Yarkin) | Page détail d'une alerte | Page réglages | Page statistiques, alertes M2, tests bout en bout | Bonus M4 affichage, finitions, démo déployée |
| **Data/IA** (Elias, Imad, Nolan) | Plus de données, Presidio pour les noms, mesures à chaque PR | Modèle v1 branché, seuil réglable, suivi des métriques | Viser rappel ≥ 90 % et fausses alertes ≤ 10 %, score expliqué | Bonus M4 textes, résultats chiffrés pour le dossier |

## Objectifs de la séance 3

**Objectif de la séance :** un faux IBAN tapé dans ChatGPT apparaît dans la base, même si l'écran est encore brut.

| Personne | Tâche | Terminée quand |
| --- | --- | --- |
| Arno | Faire envoyer les événements de l'addon à `POST /events` | Un faux IBAN dans ChatGPT arrive dans la base |
| Aloïs | Renforcer les règles `cle_api` et `mot_de_passe` | Secrets ≥ 15/18 sur les 150 prompts |
| Kiliann | Remplir les exemples de `rules/m2.yaml`, écrire `docs/m2-pip-npm.md` | Chaque règle M2 a ses exemples |
| Fati | Coder la page « détail d'une alerte » (maquette `docs/maquettes/02-detail-alerte.pdf`) | La page affiche une alerte de la base |
| Yarkin | Reprendre ses cartes avec Fati (rôle à confirmer) | Rôle noté dans la charte |
| Elias | Mettre à jour le planning du dossier Ydays | Dossier à jour |
| Nolan | Réentraîner le modèle avec plus de données | Rappel du modèle mesuré |
| Imad | Refaire les mesures sur le nouveau `prompts_v1.csv`, préparer ai4privacy, ajouter Presidio (noms) dans `detect()` | Rappel mesuré règles + Presidio dans `main` |

## À décider en équipe en séance 3

- [ ] Rôle de Yarkin dans l'équipe Dev maintenant que l'API est faite.
- [ ] On teste aussi les IA en mode connecté (ChatGPT, Gemini, Copilot), ou seulement sans compte pour la démo ?
- [ ] Valider les jalons (démo M1 en séance 5, M2 en séance 7).
