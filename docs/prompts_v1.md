# Jeu de données `data/prompts_v1.csv`

Nolan, séance 2 (12/11/2026). Sert à **tester** la détection (règles et modèle) et à **entraîner** la baseline ML.

## Contenu

150 prompts en français, réalistes pour une PME, dans 4 contextes : mail (45), code (45), RH (32), compta (28).

| Catégorie | Nb | Exemple de contenu |
|---|---|---|
| `non_sensible` | 65 | dont **55 pièges** et 10 neutres |
| `donnees_clients` | 19 | listes de clients, contacts, SIRET, marges |
| `identite` | 18 | n° de sécu, date de naissance, adresse, passeport |
| `finance` | 18 | IBAN, carte bancaire, salaire nominatif |
| `secret_technique` | 18 | clés API, mots de passe, tokens, clé SSH |
| `sante` | 12 | arrêt maladie, diagnostic, traitement |

## Colonnes

| Colonne | Valeurs | Sens |
|---|---|---|
| `id` | 1-150 | identifiant |
| `texte` | str | le prompt |
| `contexte` | `mail`, `code`, `rh`, `compta` | situation métier |
| `sensible` | 0 / 1 | faut-il réagir ? |
| `categorie` | 6 étiquettes ci-dessus | étiquettes du classifieur (guide d'Elias) |
| `piege` | 0 / 1 | ressemble à du sensible mais ne l'est pas |
| `types_donnees` | `IBAN\|NOM\|…` | données présentes, séparées par `\|` |

## Les pièges

Ils mesurent le **taux de fausses alertes**. Exemples : carte de test Stripe `4242 4242 4242 4242`, IBAN d'exemple des docs bancaires, `os.getenv("OPENAI_API_KEY")`, hash de commit Git, « combien de chiffres a un n° de sécu ? », prénom seul (« écris un mail à Paul »).

## Fabrication

- Toutes les données sont **fictives** : aucune personne ni aucun compte réel.
- Les IBAN, n° de sécu, cartes (Luhn) et SIRET ont des **clés de contrôle valides**, pour que les règles de validation se déclenchent comme sur de vraies données.
- Ligne 113 : clés Stripe et SendGrid préfixées `FAKE` pour passer la protection des secrets de GitHub.
- Fichier en UTF-8 avec BOM (lisible dans Excel). **Ne pas l'enregistrer depuis Excel** : modifier avec VS Code ou pandas.

## Limites

- Un seul annotateur : à relire avec le guide d'annotation d'Elias.
- Prompts synthétiques : à compléter avec des données publiques (ai4privacy) aux séances 3-5.
- Cas limites à trancher en équipe : SIRET d'un client (public mais lié à un client), salaire nominatif (finance ou identité).
