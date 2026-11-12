# Analyse du dataset AI4Privacy et évaluation de Presidio

**Projet :** CyberSentinel
**Responsable :** Imad
**Date :** 12/11/2026

---

## Résumé

- **Dataset retenu pour les tests :** AI4Privacy OpenPII 1M (Hugging Face). Il contient **131 173 exemples en français**, synthétiques, annotés et sous licence CC-BY-4.0.
- **Presidio dans sa configuration native, sur 1 000 exemples français :**
  - il repère **53 %** des données personnelles ;
  - **90 %** de ses alertes sont justes ;
  - il traite un texte en **14 ms** (médiane).
- **Très bien détecté :** e-mails (100 %), villes (86 %), rues (79 %), prénoms (78 %).
- **Jamais détecté :** âges (0 %) et cartes bancaires (0 %).
- **Limites du dataset :**
  - les textes ne ressemblent pas à des prompts envoyés à une IA ;
  - les numéros de téléphone et de carte bancaire ne sont pas réalistes ;
  - il ne contient ni IBAN, ni clés API, ni mots de passe.
- **Conclusion :** le dataset est utile pour mesurer la détection des données d'identité (noms, adresses, e-mails). Il ne suffit pas pour CyberSentinel : il faut le compléter par un jeu de prompts créé par l'équipe, et ajouter des règles de détection à Presidio.

---

## 1. Présentation du dataset

| | |
|---|---|
| Nom | AI4Privacy OpenPII 1M |
| Identifiant | `ai4privacy/pii-masking-openpii-1m` |
| Lien | https://huggingface.co/datasets/ai4privacy/pii-masking-openpii-1m |
| DOI | 10.57967/hf/8202 |
| Éditeur | Ai4Privacy / Ai Suisse SA |
| Dernière mise à jour | 04/04/2026 (consulté le 12/11/2026) |
| Type | Textes synthétiques contenant des données personnelles fictives |

## 2. Informations générales

| | |
|---|---|
| Nombre total d'exemples | 1 428 143 |
| Découpage | train : 1 143 397 / validation : 284 746 |
| Langues | 23 langues européennes |
| **Exemples en français** | **131 173** (105 227 en train, 25 946 en validation) |
| Pays représentés en français | France, Canada, Suisse (environ 1/3 chacun) |
| Annotations | 10 328 208 au total, 19 types |

## 3. Types de données annotées

Le dataset annote 19 types de données personnelles :

| Catégorie | Labels |
|---|---|
| Identité | `GIVENNAME` (prénom), `SURNAME` (nom), `TITLE` (civilité), `AGE`, `SEX`, `GENDER`, `DATE` |
| Adresse | `STREET` (rue), `BUILDINGNUM` (n° de rue), `CITY` (ville), `ZIPCODE` (code postal) |
| Contact | `EMAIL`, `TELEPHONENUM` |
| Pièces d'identité | `IDCARDNUM` (carte d'identité), `PASSPORTNUM`, `DRIVERLICENSENUM` (permis), `SOCIALNUM` (sécurité sociale), `TAXNUM` (n° fiscal) |
| Bancaire | `CREDITCARDNUMBER` |

**Absents du dataset :** IBAN, clés API et tokens, mots de passe, adresses IP, URL, noms d'entreprises.

## 4. Format des annotations

Chaque exemple contient :
- `source_text` : le texte d'origine ;
- `masked_text` : le même texte avec les données remplacées par leur type (ex. `[EMAIL]`) ;
- `privacy_mask` : la liste des données personnelles, chacune avec sa valeur, sa position de début et de fin dans le texte, et son type ;
- `language` et `region` : la langue et le pays.

Les positions sont exprimées en caractères, comme dans les résultats de Presidio. On peut donc comparer directement ce que Presidio trouve avec ce qui est annoté. Nous avons vérifié les 185 507 annotations des exemples français de validation : toutes les positions sont correctes.

**Exemple :**
> Formulaire d'inscription à la détox digitale
> Nom : Pejman Murad Coroian Vilariño — Âge : 81 — Email : sinéadnadalin@yahoo.com — Téléphone : +3366.939.1416

Annotations : `GIVENNAME` « Pejman Murad », `SURNAME` « Coroian Vilariño », `AGE` « 81 », `EMAIL`, `TELEPHONENUM`, etc.

## 5. Licence

- **Licence :** CC-BY-4.0. L'utilisation est autorisée, y compris commerciale. Les modifications et la redistribution sont aussi autorisées.
- **Obligation :** citer « Ai4Privacy / Ai Suisse SA » et donner le lien vers le dataset.
- **RGPD :** les données sont entièrement synthétiques (« synthetic PII only »). Elles ne concernent aucune personne réelle.

---

## 6. Évaluation de Presidio

### 6.1 Méthode

- **Outil testé :** Microsoft Presidio, configuration native en français, sans règle ajoutée. Les noms de personnes et de lieux sont repérés par le modèle de langue spaCy `fr_core_news_lg`.
- **Échantillon :** 1 000 exemples français tirés au hasard dans le split validation. Le tirage est fixé (graine 42), donc il est reproductible. L'échantillon contient 7 148 données annotées.
- **Correspondance :** une donnée est comptée comme trouvée si Presidio signale une zone qui la recouvre, même partiellement.
- **Deux façons de compter :**
  - **Détection pour bloquer** : Presidio signale la donnée, quel que soit le type qu'il lui donne. C'est ce qui compte pour CyberSentinel, qui doit bloquer ou masquer.
  - **Détection avec le bon type** : Presidio donne aussi le bon type (ex. un e-mail reconnu comme `EMAIL_ADDRESS`). Ce calcul ne porte que sur les types qui ont un équivalent dans Presidio.
- **Définitions :**
  - **Rappel** : part des données personnelles que Presidio trouve.
  - **Précision** : part des alertes de Presidio qui sont justes.
  - **F1** : moyenne harmonique des deux, pour résumer la performance en un seul chiffre.

### 6.2 Résultats globaux

| | Précision | Rappel | F1 |
|---|---|---|---|
| **Détection pour bloquer** | **90,0 %** | **53,3 %** | **67,0 %** |
| Détection avec le bon type | 52,9 % | 55,3 % | 54,1 % |

**Temps de traitement par texte :**
- moyenne : 16,7 ms ;
- médiane : 14,1 ms ;
- 95 % des textes en moins de 35 ms.

Cette vitesse est compatible avec une analyse en temps réel des prompts.

### 6.3 Résultats par type de donnée

| Type (AI4Privacy) | Équivalent Presidio | Nombre | Trouvé (bon type) | Trouvé (tous types) |
|---|---|---|---|---|
| EMAIL | EMAIL_ADDRESS | 515 | 100 % | **100 %** |
| CITY | LOCATION | 497 | 74 % | **86 %** |
| STREET | LOCATION | 323 | 74 % | **79 %** |
| GIVENNAME | PERSON | 837 | 69 % | **78 %** |
| SURNAME | PERSON | 738 | 62 % | **68 %** |
| DRIVERLICENSENUM | aucun | 201 | – | 66 % |
| TITLE | aucun | 467 | – | 63 % |
| TELEPHONENUM | PHONE_NUMBER | 387 | 50 % | **53 %** |
| SEX | aucun | 202 | – | 52 % |
| TAXNUM | aucun | 149 | – | 47 % |
| SOCIALNUM | aucun | 182 | – | 39 % |
| IDCARDNUM | aucun | 222 | – | 37 % |
| GENDER | aucun | 173 | – | 36 % |
| DATE | DATE_TIME | 865 | 33 % | **34 %** |
| PASSPORTNUM | aucun | 128 | – | 28 % |
| ZIPCODE | aucun | 337 | – | 21 % |
| BUILDINGNUM | aucun | 329 | – | 13 % |
| CREDITCARDNUMBER | CREDIT_CARD | 217 | 0 % | **1 %** |
| AGE | AGE | 379 | 0 % | **0 %** |

Quand une donnée sans équivalent Presidio est « trouvée », c'est en général par hasard : spaCy l'a prise pour un nom de lieu ou d'organisation.

### 6.4 Analyse des erreurs

**Données manquées :**
- **Cartes bancaires (0 %).** En français, Presidio ne propose pas de détecteur de carte bancaire. Il n'est disponible qu'en anglais.
- **Âges (0 %).** Un nombre seul comme « 81 » ne peut pas être reconnu sans contexte.
- **Dates (34 %).** Les formats français écrits en toutes lettres (« 22e mai 1943 », « juin/92 ») et les formats techniques (« 1966-05-25T00:00:00 ») ne sont pas reconnus.
- **Téléphones (53 %).** Beaucoup de numéros du dataset ont des formats irréalistes (voir partie 7). Un vrai numéro français comme « 06 12 34 56 78 » est bien détecté.
- **Noms rares ou étrangers.** Des noms comme « Rusli », « Usupov » ou « Gevelhoff » ne sont pas reconnus par le modèle spaCy.

**Fausses alertes :** 444 alertes sur 4 432 ne correspondent à aucune donnée annotée.
- Des mots courants qui commencent par une majuscule sont pris pour des entités : « Cordialement », « Adresse », « Téléphone », « Âge », « Merci ».
- Une partie de ces alertes porte en réalité sur de vraies informations que le dataset n'a pas annotées (« Montréal », « Canada », noms d'organismes). La précision réelle est donc un peu supérieure à 90 %.

**Pourquoi la précision « avec le bon type » est basse (53 %) :**
- Presidio signale aussi le nom de domaine des e-mails comme une URL (« exemple.fr »).
- Il range parfois une adresse dans la catégorie « organisation ».

La donnée est bien signalée, mais avec un autre type. Pour bloquer ou masquer, ce n'est pas gênant.

### 6.5 Test complémentaire sur un prompt réaliste

Nous avons aussi testé un prompt écrit par l'équipe. Il contient un nom, une ville, un IBAN, un e-mail, un téléphone et une clé API.

| Donnée | Résultat |
|---|---|
| Nom, ville, e-mail, téléphone | Détectés |
| IBAN | Détecté (score 1,0) |
| Clé API `sk-proj-...` | **Non détectée** |
| « FR76 » (début de l'IBAN) | Fausse alerte : pris pour un lieu |

---

## 7. Limites du dataset pour CyberSentinel

1. **Ce ne sont pas des prompts.** Les textes sont des formulaires, des courriers et des SMS. Aucun ne ressemble à une question posée à une IA (« Peux-tu rédiger… »).
2. **Les numéros ne sont pas réalistes.**
   - Téléphones : par exemple `+053.125.239.7941`, `8779-073-4876`.
   - Cartes bancaires : seules 21 sur 217 ont une clé de contrôle valide (algorithme de Luhn), avec des longueurs de 12 à 19 chiffres.
   - Conséquence : même un bon détecteur rejetterait ces numéros. Le dataset ne permet pas d'évaluer correctement les cartes bancaires et sous-estime la détection des téléphones.
3. **Les données les plus critiques pour CyberSentinel sont absentes :** IBAN, clés API, tokens, mots de passe, adresses IP.
4. **Il y a des erreurs d'annotation.** Par exemple, « 38 % » est annoté comme un âge.
5. **Seul un tiers des textes est au format français de France.** Les autres suivent les formats canadiens et suisses (codes postaux, numéros fiscaux).

## 8. Conclusion et prochaines étapes

AI4Privacy OpenPII 1M est un **bon dataset pour mesurer la détection des données d'identité** : noms, adresses, e-mails. Il est volumineux, en français, sous licence libre et sans données réelles. Mais **il ne suffit pas à lui seul** pour évaluer CyberSentinel.

Presidio, sans règle ajoutée, est **rapide et fiable quand il signale quelque chose** (90 % d'alertes justes). En revanche, **il manque près d'une donnée sur deux**, ce qui est insuffisant pour un outil de protection.

**Prochaines étapes proposées :**

1. **Ajouter des règles de détection à Presidio :**
   - clés API et tokens (formats `sk-...`, `ghp_...`, `AKIA...`) ;
   - cartes bancaires en français ;
   - dates en français ;
   - numéros français (sécurité sociale, téléphone) ;
   - une liste de mots à ignorer (« Cordialement », « Adresse »…).
2. **Créer un jeu de test de prompts réalistes**, écrit par l'équipe, contenant les données critiques absentes du dataset : IBAN, clés API, mots de passe, adresses IP.
3. **Relancer la même évaluation** après chaque amélioration, pour mesurer le gain obtenu.
4. **Tester l'anonymisation** avec presidio-anonymizer (masquer les données plutôt que bloquer tout le prompt).

---

## Annexe : reproduire les résultats

Depuis la racine du dépôt, avec un environnement Python où `data/requirements.txt` est installé :

```powershell
python -m spacy download fr_core_news_lg     # une seule fois
python data\scripts\preparer_dataset.py      # télécharge les exemples FR et crée l'échantillon
python data\scripts\evaluer_presidio.py      # évalue Presidio et enregistre les résultats
```

| Fichier | Contenu |
|---|---|
| `data/scripts/presidio_detector.py` | Configuration de Presidio en français |
| `data/scripts/preparer_dataset.py` | Extraction des exemples français et échantillonnage |
| `data/scripts/evaluer_presidio.py` | Calcul des métriques |
| `data/resultats/ai4privacy_par_label.csv` | Résultats par type de donnée |
| `data/resultats/ai4privacy_par_type.csv` | Précision par type Presidio |
| `data/processed/erreurs.json` | Liste des oublis et des fausses alertes (recréé localement, non versionné) |

Le test sur les prompts de l'équipe et le choix du modèle sont dans `data/presidio_test.ipynb` et `docs/choix-modele-metriques.md`.

*Dataset : Ai4Privacy / Ai Suisse SA — https://huggingface.co/datasets/ai4privacy/pii-masking-openpii-1m — CC-BY-4.0.*
