# Interface `detect(texte)` : proxy ↔ détection

Carte #52 (Arno + Nolan). Version 1.0 du 12/11/2026 : réponses de Nolan intégrées, **à relire par Arno** (pull request).
Code : `detection/detect.py`

## Le principe

```
Navigateur ──► proxy (mitmproxy + addon)
                 │ 1. extrait le prompt de la requête (décodé)
                 │ 2. appelle detect(texte)
                 │ 3. décide : bloquer / masquer / alerter / laisser passer
                 │ 4. écrit un événement pour le SIEM
                 ▼
               l'IA (chatgpt.com, ...)
```

Le proxy ne connaît que `detect(texte)`. Derrière, `detection/detect.py` appelle :

1. les **règles** d'Aloïs (`rules/m1_detect.py`) ;
2. le **modèle ML** de Data/IA (`data/modele_baseline.joblib`, s'il existe) ;

puis fusionne les deux. On peut changer les règles ou le modèle sans toucher au proxy.

## Entrée

`texte` : une chaîne Python (`str`), le prompt en clair, déjà décodé par le proxy.

C'est au proxy de décoder (voir `docs/proxy-installation-windows.md`). Où se trouve le prompt dans chaque requête :

- `docs/captures-sites-ia.md` : captures des 5 IA (ChatGPT, Gemini, Mistral, Claude, Copilot), avec l'emplacement du prompt pour chacune ;
- `rules/sites_ia.yaml` (Aloïs) : la liste des sites d'IA couverts.

Si le prompt arrive en plusieurs morceaux, le proxy les concatène avant d'appeler `detect()`.

## Sortie

Une liste de dictionnaires, une entrée par donnée trouvée, triée par position. Liste vide = rien de sensible.

```json
{
  "regle": "iban",
  "libelle": "IBAN",
  "categorie": "finance",
  "priorite": "critique",
  "score": 0.95,
  "action": "bloquer",
  "motif": "iban",
  "debut": 10,
  "fin": 43,
  "extrait_masque": "FR76 **** **** **** **** **** 189",
  "source": "regle"
}
```

| Champ | Type | Sens |
|---|---|---|
| `regle` | str | id de la règle (`iban`…) ou du modèle (`ml.sante`…) |
| `libelle` | str | nom lisible pour le tableau de bord |
| `categorie` | str | `identite`, `finance`, `sante`, `secret_technique`, `donnees_clients` |
| `priorite` | str | `critique` > `haute` > `moyenne` > `basse` |
| `score` | float 0-1 | confiance |
| `action` | str | `bloquer`, `masquer` ou `alerter` |
| `motif` | str | motif reconnu, ou `modele` |
| `debut`, `fin` | int | position dans `texte` (sert à masquer) |
| `extrait_masque` | str | la donnée masquée, **jamais la valeur en clair** (RGPD) |
| `source` | str | `regle` ou `modele` (ajouté par `detection/detect.py`) |

## Détections du modèle

Le modèle classe le prompt entier, il ne pointe pas un mot précis :

| Champ | Valeur |
|---|---|
| `regle` | `ml.<categorie>` (ex. `ml.sante`) |
| `debut`, `fin` | `0`, `len(texte)` |
| `motif` | `modele` |
| `extrait_masque` | `""` |
| `action` | `alerter` (jamais `masquer`, sinon tout le prompt serait effacé) |
| `priorite` | selon la catégorie : santé et secret technique → critique, finance et identité → haute, données clients → moyenne (à valider avec Aloïs) |

Il ne signale rien sous un score de **0,6** (`SEUIL_MODELE`).

## Fusion règles + modèle

- Toutes les détections des règles sont gardées.
- Une détection du modèle est ajoutée **seulement si aucune règle n'a trouvé la même catégorie**. Les règles sont plus précises, le modèle sert à attraper ce qu'elles ne voient pas (santé, noms, adresses).
- Sans fichier `data/modele_baseline.joblib`, `detect()` fonctionne avec les règles seules.

## Décision du proxy

1. Si au moins une entrée a `action = bloquer` → la requête ne part pas (réponse 403 + message).
2. Sinon, si une entrée a `action = masquer` → on remplace chaque zone par `extrait_masque` (`mask_text`), puis on envoie.
3. Sinon, si une entrée a `action = alerter` → on envoie tel quel.
4. Dans les cas 1 à 3 → on écrit un événement (format de `docs/format-evenement.md`, carte #39).

`action_finale(findings)` renvoie directement l'action à appliquer (`None` si rien trouvé).
`mask_text` ignore les détections du modèle : seules les zones précises des règles sont masquées.

## Exemple d'appel dans l'addon

```python
from detection.detect import detect, mask_text, action_finale

findings = detect(prompt)
action = action_finale(findings)

if action == "bloquer":
    ...  # 403 + message
elif action == "masquer":
    prompt = mask_text(prompt, findings)
    ...  # réécrire la requête avec le prompt masqué
if findings:
    ...  # écrire un événement par entrée (carte #39)
```

## Performances et tests

```bash
python detection/detect.py data/prompts_v1.csv   # règles + modèle sur les 150 prompts
python data/baseline.py                          # mesure honnête du modèle + réentraînement
```

Baseline TF-IDF + régression logistique, validation croisée 5 plis sur `prompts_v1.csv` :

| Mesure | Résultat |
|---|---|
| Rappel (sensible détecté) | 32 % |
| Fausses alertes | 3 % (2 pièges sur 55) |
| Santé | 0/12 |

150 prompts, c'est trop peu pour un modèle : il servira de point de comparaison. Le jeu sera agrandi aux séances 3-5 (ai4privacy, carte d'Imad).

## Réponses de Nolan au brouillon

- [x] Le format de sortie d'Aloïs convient pour le modèle (conventions ci-dessus).
- [x] On ajoute le champ `source`.
- [x] Une seule fonction `detect()` qui appelle règles puis modèle et fusionne. Le proxy importe `detection.detect`, jamais `m1_detect` directement.

## Points ouverts

- **Arno** : requête chatgpt.com en mode connecté.
- **Aloïs** : valider la table catégorie → priorité du modèle.
- **Yarkin / Elias** : un événement par entrée ou un par prompt (carte #39).
