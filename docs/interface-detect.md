# Interface `detect(texte)` : proxy ↔ détection

Carte #52 (Arno + Nolan). Brouillon du 12/11/2026, à valider avec Nolan.

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

Le proxy ne connaît **que** `detect(texte)`. Il ne sait pas si la détection vient des règles (Aloïs)
ou du modèle (Nolan, Imad). On peut donc changer l'un ou l'autre sans toucher au proxy.

## Entrée

`texte` : une chaîne Python (`str`), **le prompt en clair, déjà décodé** par le proxy.

C'est au proxy de décoder (voir `docs/proxy-installation-windows.md`) :

| Site | Requête | Où est le prompt |
|---|---|---|
| chatgpt.com (sans compte) | `POST /unauth-mweb/conversation/updates`, form-urlencoded | champ `prompt` |
| chatgpt.com (connecté) | à identifier | à identifier |
| autres IA | liste d'Aloïs (carte #32) | à identifier |

## Sortie

Une **liste** de dictionnaires, une entrée par donnée trouvée, triée par position.
Liste vide = rien de sensible.

C'est le format déjà codé par Aloïs dans `rules/m1_detect.py` (testé : 49/49 exemples OK) :

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
  "extrait_masque": "FR76 **** **** **** **** **** 189"
}
```

| Champ | Type | Sens |
|---|---|---|
| `regle` | str | id de la règle (ou de l'étiquette du modèle) |
| `libelle` | str | nom lisible pour le tableau de bord |
| `categorie` | str | `identite`, `finance`, `sante`, `secret_technique`, `donnees_clients` |
| `priorite` | str | `critique` > `haute` > `moyenne` > `basse` |
| `score` | float 0-1 | confiance |
| `action` | str | `bloquer`, `masquer` ou `alerter` |
| `debut`, `fin` | int | position dans `texte` (sert à masquer) |
| `extrait_masque` | str | la donnée masquée. **Jamais la valeur en clair** (RGPD) |

**À ajouter (proposition) :** `"source": "regle"` ou `"source": "modele"`, pour savoir dans le SIEM qui a détecté.

## Côté modèle (Nolan, Imad)

Le modèle renvoie **le même format**. Pour une détection sur tout le texte (pas un mot précis) :
`debut = 0`, `fin = len(texte)`, `motif = "modele"`, `extrait_masque = ""`.

## Décision du proxy

1. Si au moins une entrée a `action = bloquer` → la requête ne part pas (réponse 403 + message).
2. Sinon, si une entrée a `action = masquer` → on remplace chaque zone par `extrait_masque` (`mask_text`), puis on envoie.
3. Sinon, si une entrée a `action = alerter` → on envoie tel quel.
4. Dans les cas 1 à 3 → on écrit un événement (format de `docs/format-evenement.md`, carte #39).

## Exemple d'appel dans l'addon

```python
from m1_detect import detect, mask_text

findings = detect(prompt)
if any(f["action"] == "bloquer" for f in findings):
    ...  # bloquer
```

## À valider avec Nolan

- [ ] Le format de sortie ci-dessus lui convient pour le modèle
- [ ] On ajoute le champ `source`
- [ ] Une seule fonction `detect()` qui appelle règles **puis** modèle, ou deux fonctions que le proxy fusionne ?
