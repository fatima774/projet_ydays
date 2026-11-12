# Jeu de données `data/prompts_v1.csv`

Nolan, séance 2 (12/11/2026). Étiqueté selon le **guide d'annotation d'Elias**.
Sert à **tester** la détection (règles et modèle) et à **entraîner** la baseline ML.

## Contenu

150 prompts en français, réalistes pour une PME. Répartition conforme au guide (section 5) :

| Étiquette | Nb |
|---|---|
| `non_sensible` | 60, dont **55 pièges** |
| `identite` | 18 |
| `finance` | 18 |
| `sante` | 18 |
| `secret_technique` | 18 |
| `donnees_clients` | 18 |

Contextes : code (45), mail (36), RH (32), compta (29), support (8).

## Format (guide, section 4)

`id, prompt, sensible, etiquette, etiquettes_secondaires, contexte, piege, annotateur, commentaire`

- `id` : `p0001` à `p0150`.
- `etiquette` : étiquette principale, la plus grave (règle 3.1 : secret_technique > sante > finance > identite > donnees_clients).
- `etiquettes_secondaires` : autres catégories présentes, séparées par `;`.
- `commentaire` : 13 cas limites signalés (voir ci-dessous).

## Application des règles du guide

- **3.2 Identité ou données clients** : 1 ou 2 personnes nommées → `identite` ; liste de 3+ ou extrait d'outil métier → `donnees_clients`. Les prompts clients qui ne nommaient qu'1 ou 2 personnes sont passés en `identite`.
- **3.4 Pièges** : valeurs masquées, exemples de documentation, variables sans valeur, numéros de commande ou de suivi, sujets sensibles sans donnée, personnages publics.
- **Doute** : une valeur réelle et complète, même inventée, est sensible.

## Cas limites à trancher avec Elias

| id | Cas | Choix |
|---|---|---|
| p0004 | liste de 3 salariés avec n° de sécu (3.2 ne parle que de clients) | `identite` |
| p0007 | clé de licence logicielle : accès à un outil, pas au SI | `secret_technique` |
| p0017 | marges par client : données clients + finance non publiée | `finance` (+ secondaires) |
| p0097 | IBAN de l'entreprise envoyé aux fournisseurs : valeur réelle et complète | `finance` |
| p0012, p0148, p0038 | carte de test Stripe, IBAN d'exemple, JWT de jwt.io : valeurs publiques de documentation | `non_sensible` (piège) |

L'IBAN d'exemple `FR76 3000 6000 0112 3456 7890 189` est un piège chez nous mais un vrai IBAN dans l'exemple `p0001` du guide : à harmoniser.

## Fabrication

- Toutes les données sont **fictives**. Les IBAN, n° de sécu, cartes et SIRET ont des clés de contrôle valides mais n'appartiennent à personne.
- `p0112` : clés Stripe et SendGrid préfixées `FAKE` pour passer la protection des secrets de GitHub.
- UTF-8 avec BOM (lisible dans Excel). **Ne pas l'enregistrer depuis Excel** : modifier avec VS Code ou pandas.

## Limites

- Prompts synthétiques : à compléter avec des données publiques (ai4privacy) aux séances 3-5.
- Un seul annotateur (Nolan) : pas de double annotation pour l'instant (section 6 du guide non faite).
