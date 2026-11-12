# Guide d'annotation des prompts

Rédigé par Elias, séance 2. Il sert à étiqueter `data/prompts_v1.csv` et tous les jeux de données qui suivront. **Si un cas n'est pas couvert, on l'écrit dans la colonne `commentaire` et on complète ce guide.**

## 1. La question à se poser

> « Si ce prompt part chez ChatGPT, est-ce que l'entreprise perd le contrôle d'une donnée qu'elle doit protéger ? »

- **Oui** → `sensible = 1`, puis on choisit la catégorie.
- **Non** → `sensible = 0`, étiquette `non_sensible`.

On juge **le contenu réel** du prompt, pas le sujet. Parler de salaires n'est pas sensible ; coller la fiche de paie de Mme Durand l'est.

## 2. Les 6 étiquettes

| Étiquette | Définition | Exemples typiques |
| --- | --- | --- |
| `non_sensible` | Aucune donnée qui identifie une personne, un client ou un secret de l'entreprise | Question générale, code sans secret, données fictives évidentes |
| `identite` | Données qui identifient **une personne précise** | Nom + adresse, n° de sécurité sociale, date de naissance + nom, n° de passeport, téléphone ou e-mail personnel d'un salarié |
| `finance` | Données bancaires ou financières exploitables | IBAN, n° de carte, RIB, salaire nominatif, chiffre d'affaires non publié |
| `sante` | Toute information de santé sur une personne identifiable | Arrêt maladie, diagnostic, handicap, mutuelle avec pathologie |
| `secret_technique` | Ce qui donne accès aux systèmes de l'entreprise | Clé API, mot de passe, token, chaîne de connexion à une base, clé privée, IP interne + identifiants |
| `donnees_clients` | Données sur **plusieurs clients** ou issues d'un outil métier | Export CRM, liste de clients avec contacts, historique de commandes, base de prospects |

## 3. Règles de décision

### 3.1 Une seule étiquette principale

Si un prompt contient plusieurs types de données, on garde **la plus grave**, dans cet ordre :

1. `secret_technique`
2. `sante`
3. `finance`
4. `identite`
5. `donnees_clients`

Les autres catégories présentes vont dans la colonne `etiquettes_secondaires`, séparées par `;`.

> Exemple : « Voici la liste de nos clients avec leurs IBAN » → `finance` (principale), `donnees_clients` (secondaire).

### 3.2 Identité ou données clients ?

- **Une ou deux personnes nommées** → `identite`.
- **Une liste, un tableau, un export** (3 personnes ou plus, ou un extrait d'outil métier) → `donnees_clients`.

### 3.3 Les données de contact professionnelles

Un e-mail ou un téléphone **générique** (contact@entreprise.fr, standard) est `non_sensible`. Un e-mail ou un téléphone **nominatif** (jean.martin@entreprise.fr) est `identite`.

### 3.4 Les faux positifs piégeux → `non_sensible`

Ces prompts **ressemblent** à des fuites mais n'en sont pas. Il faut au moins **un tiers** du jeu de données de ce type.

| Piège | Exemple | Étiquette |
| --- | --- | --- |
| Valeur masquée ou factice | `FR76 XXXX XXXX XXXX`, `sk-xxxxxxxx`, `password=CHANGEME` | `non_sensible` |
| Exemple de documentation | « Le format d'un IBAN français est FR76 suivi de 23 caractères » | `non_sensible` |
| Variable sans valeur | `api_key = os.environ["API_KEY"]` | `non_sensible` |
| Numéro qui a la forme d'une donnée | n° de commande, référence produit, n° de facture, numéro de ticket | `non_sensible` |
| Sujet sensible sans donnée | « Comment rédiger un mail pour un arrêt maladie ? » | `non_sensible` |
| Personnage public ou fictif | « Résume la carrière de Zinedine Zidane » | `non_sensible` |

Dans le doute entre une vraie valeur et une valeur factice : **une valeur qui a l'air réelle et complète est sensible**, même si elle est inventée pour le jeu de données (c'est ce que le modèle doit apprendre à attraper).

## 4. Format du fichier `data/prompts_v1.csv`

Encodage UTF-8, séparateur `,`, champs entre guillemets s'ils contiennent une virgule ou un retour à la ligne.

| Colonne | Valeurs | Description |
| --- | --- | --- |
| `id` | `p0001`, `p0002`… | Identifiant unique |
| `prompt` | texte | Le prompt complet, tel qu'un salarié l'écrirait |
| `sensible` | `0` / `1` | Vérité binaire, utilisée pour le rappel et les fausses alertes |
| `etiquette` | une des 6 étiquettes | Étiquette principale (règle 3.1) |
| `etiquettes_secondaires` | ex. `donnees_clients;identite` | Vide si aucune |
| `contexte` | `mail`, `code`, `rh`, `compta`, `support`, `autre` | Situation métier du prompt |
| `piege` | `0` / `1` | `1` si c'est un non-sensible piégeux (règle 3.4) |
| `annotateur` | prénom | Qui a étiqueté |
| `commentaire` | texte libre | Hésitation, cas non couvert par le guide |

Exemple :

```csv
id,prompt,sensible,etiquette,etiquettes_secondaires,contexte,piege,annotateur,commentaire
p0001,"Peux-tu reformuler ce mail : merci de virer 1 200 € sur FR76 3000 6000 0112 3456 7890 189",1,finance,,compta,0,Nolan,
p0002,"Quel est le format d'un IBAN français ?",0,non_sensible,,compta,1,Nolan,
p0003,"Corrige ce code : conn = psycopg2.connect(password='Mdp!2026prod')",1,secret_technique,,code,0,Nolan,
```

## 5. Répartition cible pour les 150 prompts

| Étiquette | Nombre visé |
| --- | --- |
| `non_sensible` (dont au moins 50 piégeux) | 60 |
| `identite` | 18 |
| `finance` | 18 |
| `sante` | 18 |
| `secret_technique` | 18 |
| `donnees_clients` | 18 |

Contextes à mélanger : mails, code, RH, compta, support client.

## 6. Contrôle qualité

- **Double annotation** : 30 prompts tirés au hasard sont étiquetés une deuxième fois par une autre personne (Elias ou Imad). Si l'accord est inférieur à 80 %, on corrige le guide et on relit les cas litigieux.
- **Aucune vraie donnée** : tous les noms, IBAN, numéros et clés sont inventés. Les IBAN et cartes peuvent être valides au sens de la clé de contrôle (générateurs de test), mais ne doivent appartenir à personne.
