"""CyberSentinel — point d'entrée unique de la détection (carte #52, Arno + Nolan).

Le proxy n'appelle que detect(texte). Ce module :
  1. appelle les règles d'Aloïs (rules/m1_detect.py) ;
  2. appelle le modèle ML (Data/IA) s'il est entraîné (data/modele_baseline.joblib) ;
  3. fusionne, ajoute le champ "source" et trie par position.

Contrat complet : docs/detect.md
Évaluation     : python detection/detect.py data/prompts_v1.csv
"""
from __future__ import annotations

import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RACINE / "rules"))

from m1_detect import detect as _detect_regles          # noqa: E402  (règles d'Aloïs)
from m1_detect import mask_text as _mask_text_regles    # noqa: E402

__all__ = ["detect", "mask_text", "action_finale", "detect_modele", "VERSION"]

VERSION = "1.0"

CHEMIN_MODELE = RACINE / "data" / "modele_baseline.joblib"
SEUIL_MODELE = 0.6          # en dessous, le modèle ne signale rien
ACTION_MODELE = "alerter"   # le modèle n'est jamais "masquer" (il vise tout le texte)

ORDRE_ACTION = {"bloquer": 3, "masquer": 2, "alerter": 1}

PRIORITE_PAR_CATEGORIE = {   # à valider avec Aloïs
    "sante": "critique",
    "secret_technique": "critique",
    "finance": "haute",
    "identite": "haute",
    "donnees_clients": "moyenne",
}

LIBELLE_PAR_CATEGORIE = {
    "sante": "Donnée de santé",
    "secret_technique": "Secret technique",
    "finance": "Donnée financière",
    "identite": "Donnée d'identité",
    "donnees_clients": "Données clients",
}


# ------------------------------------------------------------------ modèle ML

_modele = None
_modele_charge = False


def _charger_modele():
    """Charge le modèle une seule fois. Absent ou illisible → None (règles seules)."""
    global _modele, _modele_charge
    if not _modele_charge:
        _modele_charge = True
        try:
            import joblib
            _modele = joblib.load(CHEMIN_MODELE)
        except Exception:
            _modele = None
    return _modele


def detect_modele(texte: str) -> list[dict]:
    """Détection sur tout le texte par le modèle. [] si pas de modèle ou rien de sûr."""
    modele = _charger_modele()
    if modele is None:
        return []

    probas = modele.predict_proba([texte])[0]
    i = int(probas.argmax())
    categorie = str(modele.classes_[i])
    score = float(probas[i])

    if categorie == "non_sensible" or score < SEUIL_MODELE:
        return []

    return [{
        "regle": f"ml.{categorie}",
        "libelle": LIBELLE_PAR_CATEGORIE.get(categorie, categorie),
        "categorie": categorie,
        "priorite": PRIORITE_PAR_CATEGORIE.get(categorie, "moyenne"),
        "score": round(score, 2),
        "action": ACTION_MODELE,
        "motif": "modele",
        "debut": 0,
        "fin": len(texte),
        "extrait_masque": "",
        "source": "modele",
    }]


# ------------------------------------------------------------------ API publique

def detect(texte: str) -> list[dict]:
    """Renvoie les données sensibles trouvées dans `texte` (règles + modèle), triées par position."""
    if not isinstance(texte, str) or not texte.strip():
        return []

    resultats = [{**f, "source": "regle"} for f in _detect_regles(texte)]

    # Le modèle n'ajoute une alerte que si les règles n'ont rien trouvé dans cette catégorie.
    categories_regles = {f.get("categorie") for f in resultats}
    for f in detect_modele(texte):
        if f["categorie"] not in categories_regles:
            resultats.append(f)

    return sorted(resultats, key=lambda f: (f["debut"], f["fin"]))


def mask_text(texte: str, findings: list[dict]) -> str:
    """Masque les zones trouvées par les règles. Les détections du modèle (tout le texte) sont ignorées."""
    zones = [f for f in findings if f.get("motif") != "modele" and f.get("source") != "modele"]
    return _mask_text_regles(texte, zones)


def action_finale(findings: list[dict]) -> str | None:
    """Action la plus forte : bloquer > masquer > alerter. None si rien trouvé."""
    actions = [f["action"] for f in findings if f.get("action") in ORDRE_ACTION]
    return max(actions, key=ORDRE_ACTION.__getitem__) if actions else None


# ------------------------------------------------------------------ évaluation

if __name__ == "__main__":
    import csv
    import time
    from collections import Counter, defaultdict

    chemin = sys.argv[1] if len(sys.argv) > 1 else str(RACINE / "data" / "prompts_v1.csv")
    with open(chemin, encoding="utf-8-sig") as f:
        lignes = list(csv.DictReader(f))

    t0 = time.perf_counter()
    resultats = [detect(l["texte"]) for l in lignes]
    ms = (time.perf_counter() - t0) * 1000 / len(lignes)

    par_cat = defaultdict(lambda: [0, 0])
    sources = Counter()
    for l, r in zip(lignes, resultats):
        par_cat[l["categorie"]][0] += bool(r)
        par_cat[l["categorie"]][1] += 1
        if r and l["sensible"] == "1":
            sources["regles seules" if all(f["source"] == "regle" for f in r) else "avec modele"] += 1

    sens = [bool(r) for l, r in zip(lignes, resultats) if l["sensible"] == "1"]
    nons = [bool(r) for l, r in zip(lignes, resultats) if l["sensible"] == "0"]
    pieg = [bool(r) for l, r in zip(lignes, resultats) if l["piege"] == "1"]

    print(f"detect v{VERSION} — modèle {'chargé' if _charger_modele() else 'absent (règles seules)'}")
    print(f"  rappel          : {sum(sens)}/{len(sens)} = {sum(sens) / len(sens):.0%}")
    print(f"  fausses alertes : {sum(nons)}/{len(nons)} = {sum(nons) / len(nons):.0%}  (pièges : {sum(pieg)}/{len(pieg)})")
    print(f"  temps moyen     : {ms:.2f} ms/prompt")
    print(f"  sensibles trouvés par : {dict(sources)}")
    for cat, (ok, n) in sorted(par_cat.items()):
        print(f"  {cat:<17} {ok}/{n}")
    if _charger_modele():
        print("  ⚠ le modèle a été entraîné sur ce même fichier : scores optimistes, "
              "voir data/baseline.py pour la mesure honnête (validation croisée).")
