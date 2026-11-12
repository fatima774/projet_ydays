# Choix du modèle et métriques

**Projet :** CyberSentinel
**Responsable :** Imad
**Date :** 12/11/2026
**Détails et calculs :** `data/presidio_test.ipynb` · analyse du dataset public : `docs/analyse-dataset-ai4privacy.md`

---

## Résumé

- **Presidio seul ne suffit pas.** Sur les 150 prompts de l'équipe, il signale 94 % des prompts sensibles, mais aussi **40 % des prompts non sensibles**. Il ne voit ni les cartes bancaires, ni le n° de sécu, ni aucun secret technique.
- **Les règles M1 d'Aloïs seules ne suffisent pas non plus.** Elles se trompent rarement (8 % de fausses alertes), mais ne voient aucun nom de personne (rappel 60 %).
- **Choix :** un `detect()` en trois étages : **règles M1**, puis **Presidio limité aux noms de personnes**, puis un **classifieur de prompt**.
- **Métriques fixées :** rappel ≥ 90 %, rappel sur les données critiques ≥ 95 %, fausses alertes ≤ 10 %, temps de réponse ≤ 50 ms (p95).
- **Aujourd'hui, règles + Presidio :** rappel 88 %, rappel critique 72 %, fausses alertes 17 %, 8,3 ms (p95). Les objectifs ne sont pas encore atteints : il faut améliorer les règles sur les secrets et ajouter le classifieur.

---

## 1. Les métriques retenues

On mesure **par prompt** : c'est ce que vit l'utilisateur (son prompt part, ou il est bloqué ou masqué).

| Métrique | Définition | Objectif |
|---|---|---|
| **Rappel** *(prioritaire)* | Part des prompts sensibles qui déclenchent une alerte | **≥ 90 %** |
| **Rappel critique** | Part des IBAN, cartes, n° de sécu, clés/tokens et mots de passe **trouvés eux-mêmes** | **≥ 95 %** |
| **Taux de fausses alertes** | Part des prompts non sensibles qui déclenchent une alerte | **≤ 10 %** |
| Taux de fausses alertes sur pièges | Idem, sur les prompts piégeux du guide d'annotation | ≤ 20 % |
| **Temps de réponse** | Durée de `detect()` par prompt, 95ᵉ centile | **≤ 50 ms** |
| Précision par donnée *(suivi)* | Part des détections qui tombent sur une vraie donnée (dataset AI4Privacy) | ≥ 85 % |

**Pourquoi le rappel passe en premier :** une fuite ratée est irréversible. Une fausse alerte coûte seulement un prompt à reformuler.

**Pourquoi on limite quand même les fausses alertes :** au-delà d'un prompt légitime sur dix bloqué, les salariés contournent l'outil.

**Pourquoi « rappel critique » en plus du rappel :** un prompt peut être signalé pour une autre raison (un nom) alors que l'IBAN qu'il contient n'est pas trouvé. Dans ce cas, le proxy ne peut pas masquer l'IBAN.

**Attention :** taux de fausses alertes ≠ 100 % − précision. La précision de 90 % de Presidio sur AI4Privacy se calcule par donnée, sur des textes qui contiennent tous des données. Le taux de fausses alertes se calcule sur des prompts qui n'en contiennent pas.

**Jeu de test de référence :** `data/prompts_v1.csv` (Nolan) : 150 prompts, dont 85 sensibles et 65 non sensibles (55 pièges), étiquetés avec le guide d'Elias. AI4Privacy reste un jeu de contrôle pour les noms, adresses et e-mails.

## 2. Résultats sur les 150 prompts

| Détecteur | Rappel | Rappel critique | Fausses alertes | Fausses alertes (pièges) | Temps p95 |
|---|---|---|---|---|---|
| Presidio natif | 94 % ✅ | 30 % ❌ | 40 % ❌ | 45 % ❌ | 11,5 ms ✅ |
| Règles M1 (Aloïs) | 60 % ❌ | 72 % ❌ | 8 % ✅ | 9 % ✅ | 0,1 ms ✅ |
| **Règles M1 + Presidio (noms, e-mail, tél., IBAN)** | **88 %** ❌ | **72 %** ❌ | **17 %** ❌ | **20 %** ✅ | **8,3 ms** ✅ |
| *Objectif* | *≥ 90 %* | *≥ 95 %* | *≤ 10 %* | *≤ 20 %* | *≤ 50 ms* |

### Test détaillé sur 20 prompts (12 sensibles, 8 pièges)

| | Presidio | Règles M1 | Règles + Presidio |
|---|---|---|---|
| Prompts sensibles signalés | 11 / 12 | 8 / 12 | 10 / 12 |
| Prompts où toutes les données sont trouvées | 3 / 12 | 5 / 12 | 6 / 12 |
| Fausses alertes sur les pièges | 7 / 8 | 2 / 8 | 6 / 8 |

**Presidio trouve :** noms, e-mails, téléphones français, IBAN, dates de naissance.
**Presidio rate :** cartes bancaires (pas de détecteur en français), n° de sécu, SIRET, toutes les clés et tous les mots de passe, la santé et les salaires.
**Presidio se trompe sur :** « Victor Hugo », « Paul », « API_KEY », une empreinte SHA-256 (pris pour des personnes), « France », « Traduis », « Dockerfile » (pris pour des lieux), « TVA », « HT », « MFA » (pris pour des organisations).

## 3. Règles ou modèle : qui détecte quoi

| Donnée | Presidio | Règles M1 | Qui s'en charge |
|---|---|---|---|
| IBAN, carte bancaire, n° de sécu, SIRET | IBAN seulement | ✅ 100 % | **Règles** (formats fixes avec clé de contrôle) |
| Téléphone, e-mail | ✅ 100 % | ✅ 100 % | **Règles** (plus rapides, aussi fiables) |
| Clés API à préfixe connu (`sk-`, `AKIA`, `ghp_`), JWT, clés privées | ❌ | ✅ | **Règles** |
| Mots de passe, jetons `Bearer`, secrets Azure, webhooks | ❌ | 0 à 50 % | **Règles, à améliorer** (voir § 5) |
| Passeport, carte d'identité, permis, immatriculation | ❌ | ❌ | **Règles à ajouter** |
| Noms de personnes | ✅ 98 % | ❌ | **Modèle NER** (Presidio / spaCy `fr_core_news_lg`) |
| Adresses, dates de naissance | ✅ 100 % | ❌ | **Modèle NER**, mais trop de fausses alertes sur les lieux : à filtrer |
| Santé, salaire, dettes, données commerciales | ❌ | ❌ | **Classifieur de prompt** : ce n'est pas un format |
| « Ce nom est-il lié à une donnée personnelle ? » | ❌ | ❌ | **Classifieur de prompt** |

## 4. Le choix

Une seule fonction `detect(texte)`, au format de `docs/interface-detect.md`, qui enchaîne trois étages :

```
prompt ──► 1. Règles M1 (Aloïs)          formats fixes : IBAN, carte, NIR, SIRET, tél., e-mail, clés, mots de passe
       ──► 2. Presidio / spaCy (NER)     noms de personnes (+ e-mail, tél., IBAN en double sécurité)
       ──► 3. Classifieur de prompt      les 6 étiquettes d'Elias : santé, finance, données clients…
                                         décide aussi si un nom seul est sensible ou non
```

1. **Règles M1** : déjà prêtes, < 1 ms, très peu de fausses alertes. Elles gardent la main pour bloquer ou masquer les données critiques.
2. **Presidio, limité à `PERSON`, `EMAIL_ADDRESS`, `PHONE_NUMBER`, `IBAN_CODE`.** On écarte `LOCATION`, `ORGANIZATION`, `URL`, `DATE_TIME` : ils créent surtout des fausses alertes. Coût : 5 à 8 ms par prompt.
3. **Classifieur de prompt** : on commence par la baseline TF-IDF + régression logistique prévue par Nolan, entraînée sur `prompts_v1.csv`. On ne passe à un modèle plus lourd (CamemBERT, Hugging Face) que si la baseline n'atteint pas les objectifs. Ce n'est pas mesuré ici : il faut d'abord plus de prompts (≥ 500).

Chaque détection porte un champ `source` (`regle` ou `modele`), comme proposé dans `docs/interface-detect.md`.

## 5. Prochaines étapes

| # | Action | Pour qui | Gain attendu |
|---|---|---|---|
| 1 | Règle `mot_de_passe` : accepter « mot de passe Tigre33$ » sans `:` ni `=`, et les mots de passe dans le code (`login('admin', '…')`, `postgresql://user:…@`) | Aloïs | rappel critique (7 mots de passe ratés sur 8) |
| 2 | Règle « chaîne à forte entropie près d'un mot-clé » (`secret`, `token`, `key`, `Bearer`), avec la validation `entropie` qui existe déjà | Aloïs | jetons `Bearer`, secrets Azure, SendGrid, webhooks |
| 3 | Liste blanche des valeurs de test publiques (carte Stripe `4242…`, JWT de jwt.io, IBAN de documentation, `@example.com`) | Aloïs, Imad | fausses alertes |
| 4 | Règles passeport, carte d'identité, permis, immatriculation | Aloïs | rappel identité |
| 5 | Baseline TF-IDF + régression logistique sur les 6 étiquettes | Nolan, Imad | santé, salaires, noms isolés |
| 6 | Agrandir le jeu de prompts (≥ 500, en gardant ⅓ de pièges) et garder 20 % de côté pour le test final | Nolan, Elias | métriques fiables |
| 7 | Relancer `data/presidio_test.ipynb` après chaque changement et suivre les 5 métriques | Imad | suivi |

**Remarque sur le jeu de prompts :** la clé `sk_live_FAKE_…` (prompt 112) contient `FAKE_` pour ne pas être bloquée par GitHub. La règle Stripe ne la reconnaît donc pas. Ce n'est pas un défaut de la règle.

## 6. Limites de cette évaluation

- 150 prompts, c'est peu : un prompt représente environ 1,2 point de rappel. Les chiffres donnent une tendance, pas une mesure précise.
- Les prompts ont été écrits par l'équipe, qui connaît les règles. Il faudra un jeu écrit par d'autres personnes pour le test final.
- Le temps est mesuré sur un PC portable, sans le proxy. Le budget complet (proxy + détection) reste à mesurer avec Arno.
- Les règles M1 testées sont celles de la branche `cyber` au 12/11/2026 (commit `1761758`).
