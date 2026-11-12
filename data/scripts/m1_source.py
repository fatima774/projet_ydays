"""
Accès aux règles M1 d'Aloïs (rules/m1.yaml + rules/m1_detect.py) depuis la branche data.

Les règles vivent dans rules/ (branche cyber). Tant que cyber n'est pas fusionnée
avec data, ce module récupère les deux fichiers depuis Git (origin/cyber) et les
copie dans data/.cache/m1/ (non versionné). Une fois la fusion faite, il utilise
directement rules/ du dépôt.

Usage :
    from m1_source import charger_m1
    m1, origine = charger_m1()
    m1.detect("Mon IBAN est FR76 3000 6000 0112 3456 7890 189")
"""

import importlib.util
import subprocess
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
DOSSIER_RULES = RACINE / "rules"
CACHE = RACINE / "data" / ".cache" / "m1"
BRANCHE = "origin/cyber"
FICHIERS = ("m1_detect.py", "m1.yaml")


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=RACINE, check=True, capture_output=True, text=True, encoding="utf-8"
    ).stdout


def _importer(chemin: Path):
    spec = importlib.util.spec_from_file_location("m1_detect", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def charger_m1():
    """Renvoie (module m1_detect, description de l'origine des règles)."""
    if all((DOSSIER_RULES / f).exists() for f in FICHIERS):
        return _importer(DOSSIER_RULES / "m1_detect.py"), "rules/ du dépôt"

    CACHE.mkdir(parents=True, exist_ok=True)
    for f in FICHIERS:
        (CACHE / f).write_text(_git("show", f"{BRANCHE}:rules/{f}"), encoding="utf-8")
    commit = _git("log", "-1", "--format=%h %ad", "--date=short", BRANCHE, "--", "rules/m1.yaml").strip()
    return _importer(CACHE / "m1_detect.py"), f"{BRANCHE} (commit {commit})"
