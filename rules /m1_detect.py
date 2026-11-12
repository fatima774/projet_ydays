"""
CyberSentinel · Module 1 : détection des données sensibles dans un texte.

Charge les règles de rules/m1.yaml et expose :

    detect(texte) -> list[dict]

Chaque élément renvoyé décrit une donnée trouvée :
    {
        "regle": "iban",              # id de la règle
        "libelle": "IBAN",
        "categorie": "finance",
        "priorite": "critique",
        "score": 0.95,
        "action": "bloquer",
        "motif": "iban",              # quel motif de la règle a déclenché
        "debut": 52, "fin": 85,       # position dans le texte
        "extrait_masque": "FR76 **** **** **** **** ***0 189",
    }

La valeur en clair n'est jamais renvoyée (RGPD) : seulement sa position
et un extrait masqué. Le proxy peut utiliser debut/fin pour masquer.

Utilisation en ligne de commande :
    python rules/m1_detect.py --test           # vérifie les exemples de chaque règle
    python rules/m1_detect.py "mon texte"      # analyse un texte
"""
from __future__ import annotations

import math
import re
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

import yaml

RULES_FILE = Path(__file__).with_name("m1.yaml")


# ---------------------------------------------------------------------
# Validations (appelées après la regex pour éliminer les faux positifs)
# ---------------------------------------------------------------------

def _digits(value: str) -> str:
    return "".join(c for c in value if c.isdigit())


def luhn_ok(number: str) -> bool:
    digits = _digits(number)
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return bool(digits) and total % 10 == 0


def valid_iban(value: str) -> bool:
    iban = re.sub(r"\s", "", value).upper()
    if not 15 <= len(iban) <= 34 or not iban[2:4].isdigit():
        return False
    rearranged = iban[4:] + iban[:4]
    number = "".join(str(int(c, 36)) for c in rearranged)
    return int(number) % 97 == 1


def valid_card(value: str) -> bool:
    d = _digits(value)
    n = len(d)
    visa = d.startswith("4") and n in (13, 16, 19)
    mastercard = n == 16 and (51 <= int(d[:2]) <= 55 or 2221 <= int(d[:4]) <= 2720)
    amex = n == 15 and d[:2] in ("34", "37")
    return (visa or mastercard or amex) and luhn_ok(d)


def valid_nir(value: str) -> bool:
    nir = re.sub(r"[\s.]", "", value).upper()
    if len(nir) != 15:
        return False
    body, key = nir[:13], nir[13:]
    body = body.replace("2A", "19").replace("2B", "18")
    if not body.isdigit():
        return False
    return 97 - int(body) % 97 == int(key)


def valid_siret(value: str) -> bool:
    d = _digits(value)
    if len(d) != 14:
        return False
    if d.startswith("356000000"):  # La Poste : règle spéciale
        return sum(int(c) for c in d) % 5 == 0
    return luhn_ok(d)


def shannon_entropy(value: str) -> float:
    counts = Counter(value)
    n = len(value)
    return -sum(c / n * math.log2(c / n) for c in counts.values())


def valid_secret(value: str) -> bool:
    return shannon_entropy(value) >= 3.0


_PLACEHOLDER = re.compile(r"^(?:[*x•.\-_]+|<.*>?|\{\{.*|\$\{?.*|%.*%|\[.*\]?)$", re.I)


def valid_password(value: str) -> bool:
    if _PLACEHOLDER.match(value):
        return False
    classes = sum(
        bool(re.search(p, value))
        for p in (r"[a-zà-ÿ]", r"[A-ZÀ-Ý]", r"\d", r"[^\w\s]")
    )
    return classes >= 2


VALIDATIONS = {
    "aucune": lambda v: True,
    "iban_mod97": valid_iban,
    "carte_bancaire": valid_card,
    "nir_cle": valid_nir,
    "siret": valid_siret,
    "entropie": valid_secret,
    "mot_de_passe": valid_password,
}


# ---------------------------------------------------------------------
# Masquage
# ---------------------------------------------------------------------

def mask(value: str, debut: int = 0, fin: int = 0) -> str:
    """Remplace chaque caractère par * (sauf les espaces) en gardant `debut` et `fin` caractères."""
    positions = [i for i, c in enumerate(value) if not c.isspace()]
    keep = set(positions[:debut]) | set(positions[len(positions) - fin:] if fin else [])
    return "".join(c if (i in keep or c.isspace()) else "*" for i, c in enumerate(value))


# ---------------------------------------------------------------------
# Chargement des règles
# ---------------------------------------------------------------------

@lru_cache(maxsize=4)
def load_rules(path: str | Path = RULES_FILE) -> tuple[dict, ...]:
    with open(path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    ranks = config["priorites"]
    rules = []
    for order, rule in enumerate(config["regles"]):
        rule = dict(rule)
        rule["_rang"] = (-ranks[rule["priorite"]], order)
        compiled = []
        for motif in rule["motifs"]:
            flags = re.IGNORECASE if motif.get("ignorer_casse") else 0
            validation = motif.get("validation", rule.get("validation", "aucune"))
            if validation not in VALIDATIONS:
                raise ValueError(f"Règle {rule['id']} : validation inconnue « {validation} »")
            compiled.append((motif["nom"], re.compile(motif["regex"], flags), VALIDATIONS[validation]))
        rule["_motifs"] = compiled
        rules.append(rule)
    rules.sort(key=lambda r: r["_rang"])
    return tuple(rules)


# ---------------------------------------------------------------------
# Détection
# ---------------------------------------------------------------------

def detect(texte: str, path: str | Path = RULES_FILE) -> list[dict]:
    """Renvoie la liste des données sensibles trouvées dans `texte`.

    Les règles sont appliquées de la plus prioritaire à la moins prioritaire ;
    une zone du texte déjà attribuée à une règle n'est pas comptée deux fois
    (ex. les chiffres d'un IBAN ne déclenchent pas aussi « carte bancaire »).
    """
    found: list[dict] = []
    taken: list[tuple[int, int]] = []
    for rule in load_rules(path):
        groupe = rule.get("groupe")
        for nom, regex, validate in rule["_motifs"]:
            for m in regex.finditer(texte):
                start, end = m.span(groupe) if groupe else m.span()
                value = m.group(groupe) if groupe else m.group()
                if any(start < t_end and end > t_start for t_start, t_end in taken):
                    continue
                if not validate(value):
                    continue
                taken.append((start, end))
                masquage = rule.get("masquage", {})
                found.append({
                    "regle": rule["id"],
                    "libelle": rule["libelle"],
                    "categorie": rule["categorie"],
                    "priorite": rule["priorite"],
                    "score": rule["score"],
                    "action": rule["action"],
                    "motif": nom,
                    "debut": start,
                    "fin": end,
                    "extrait_masque": mask(value, masquage.get("debut", 0), masquage.get("fin", 0)),
                })
    found.sort(key=lambda f: f["debut"])
    return found


def mask_text(texte: str, findings: list[dict]) -> str:
    """Renvoie le texte où chaque donnée trouvée est remplacée par son extrait masqué."""
    for f in sorted(findings, key=lambda f: f["debut"], reverse=True):
        texte = texte[: f["debut"]] + f["extrait_masque"] + texte[f["fin"]:]
    return texte


# ---------------------------------------------------------------------
# Auto-test : chaque exemple du YAML doit se comporter comme annoncé
# ---------------------------------------------------------------------

def run_tests(path: str | Path = RULES_FILE) -> int:
    failures = 0
    total = 0
    for rule in load_rules(path):
        ex = rule.get("exemples", {})
        for texte in ex.get("declenche", []):
            total += 1
            ids = [f["regle"] for f in detect(texte, path)]
            if rule["id"] not in ids:
                failures += 1
                print(f"ÉCHEC  [{rule['id']}] aurait dû déclencher : {texte!r} (trouvé : {ids})")
        for texte in ex.get("ne_declenche_pas", []):
            total += 1
            hits = [f for f in detect(texte, path) if f["regle"] == rule["id"]]
            if hits:
                failures += 1
                print(f"ÉCHEC  [{rule['id']}] n'aurait pas dû déclencher : {texte!r} -> {hits[0]['extrait_masque']}")
        if len(ex.get("declenche", [])) < 3 or len(ex.get("ne_declenche_pas", [])) < 3:
            print(f"ATTENTION [{rule['id']}] moins de 3 exemples dans une des deux listes")
    print(f"\n{total - failures}/{total} exemples OK, {len(load_rules(path))} règles.")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--test":
        return run_tests()
    texte = " ".join(argv)
    findings = detect(texte)
    if not findings:
        print("Rien de sensible trouvé.")
        return 0
    for f in findings:
        print(f"[{f['priorite']:>8}] {f['libelle']:<35} {f['action']:<8} {f['extrait_masque']}")
    print("\nTexte masqué :", mask_text(texte, findings))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
