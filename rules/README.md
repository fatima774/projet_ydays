# rules/

Règles de détection écrites par la team cyber : expressions régulières des données sensibles, listes de sites d'IA, critères des paquets suspects.

Chaque règle est documentée : ce qu'elle repère, un exemple qui doit déclencher, un exemple qui ne doit pas déclencher.

**Responsables :** Aloïs, Arno.

## Fichiers

| Fichier | Contenu |
| --- | --- |
| `m1.yaml` | Module 1 : 8 règles (IBAN, carte bancaire, n° de sécu, clé API, mot de passe, téléphone, e-mail, SIRET) avec motif, validation, priorité, action et exemples |
| `m1_detect.py` | Charge `m1.yaml` et expose `detect(texte)` ; lance aussi les tests des exemples |
| `sites_ia.yaml` | Domaines des sites et API d'IA que le proxy doit surveiller |
| `m2.yaml` | Module 2 : paquets inventés (Kiliann) |

## Vérifier les règles

```bash
pip install pyyaml
python rules/m1_detect.py --test
```

Chaque exemple `declenche` doit être détecté par sa règle, chaque exemple `ne_declenche_pas` ne doit pas l'être. Toute modification de `m1.yaml` doit garder `49/49 exemples OK` (ou plus).

## Tester un texte

```bash
python rules/m1_detect.py "Mon IBAN est FR76 3000 6000 0112 3456 7890 189"
```

## Utiliser depuis le proxy

```python
from rules.m1_detect import detect, mask_text

findings = detect(prompt)          # liste de dicts : regle, priorite, action, score, debut, fin, extrait_masque
prompt_masque = mask_text(prompt, findings)
```

La valeur en clair n'est jamais renvoyée : seulement sa position et un extrait masqué (voir `docs/rgpd.md`).

## Résumé des règles M1

| Règle | Validation | Priorité | Action |
| --- | --- | --- | --- |
| IBAN | clé modulo 97 | critique | bloquer |
| Carte bancaire | Luhn + préfixe Visa/Mastercard/Amex | critique | bloquer |
| N° de sécu (NIR) | clé de contrôle (97 − n mod 97, Corse 2A/2B) | critique | bloquer |
| Clé API | entropie ≥ 3 bits/car. (rejette `sk-xxxx…`) | critique | bloquer |
| Mot de passe | mot-clé obligatoire + au moins 2 types de caractères | haute | masquer |
| Téléphone FR | format | moyenne | masquer |
| E-mail | format | moyenne | masquer |
| SIRET | Luhn (exception La Poste) | basse | alerter |
