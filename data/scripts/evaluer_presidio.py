"""
Évaluation de Presidio (configuration native, français) sur l'échantillon AI4Privacy.

Prérequis : python data/scripts/preparer_dataset.py

Deux façons de compter une détection :
  - "typée"     : Presidio trouve la donnée AVEC le bon type (ex. EMAIL -> EMAIL_ADDRESS).
                  Calculée seulement pour les labels qui ont un équivalent Presidio.
  - "tous types": Presidio signale la zone, quel que soit le type.
                  C'est ce qui compte pour CyberSentinel : bloquer ou masquer.

Correspondance par CHEVAUCHEMENT de positions (pas d'égalité stricte) :
"Dr Marie Dupont" détecté en PERSON couvre bien GIVENNAME + SURNAME.

Usage :
  python data/scripts/evaluer_presidio.py
  python data/scripts/evaluer_presidio.py --seuil 0.5
"""

import argparse
import json
import statistics
from collections import defaultdict
from pathlib import Path

import pandas as pd

from presidio_detector import analyser, creer_analyzer

RACINE = Path(__file__).resolve().parents[2]  # racine du dépôt
FICHIER_ECHANTILLON = RACINE / "data" / "processed" / "echantillon_fr.jsonl"
DOSSIER_SORTIE = RACINE / "data" / "processed"   # erreurs.json (non versionné)
DOSSIER_RESULTATS = RACINE / "data" / "resultats"  # tableaux de résultats (versionnés)

# Label AI4Privacy -> type Presidio attendu (None = pas d'équivalent natif)
CORRESPONDANCE = {
    "GIVENNAME": "PERSON",
    "SURNAME": "PERSON",
    "EMAIL": "EMAIL_ADDRESS",
    "TELEPHONENUM": "PHONE_NUMBER",
    "CITY": "LOCATION",
    "STREET": "LOCATION",
    "DATE": "DATE_TIME",
    "AGE": "AGE",
    "CREDITCARDNUMBER": "CREDIT_CARD",  # NB : non supporté par Presidio en français
    "ZIPCODE": None,
    "BUILDINGNUM": None,
    "TITLE": None,
    "SEX": None,
    "GENDER": None,
    "IDCARDNUM": None,
    "PASSPORTNUM": None,
    "DRIVERLICENSENUM": None,
    "SOCIALNUM": None,
    "TAXNUM": None,
}


def chevauche(a_debut, a_fin, b_debut, b_fin) -> bool:
    return a_debut < b_fin and b_debut < a_fin


def f1(precision, rappel):
    return 2 * precision * rappel / (precision + rappel) if precision + rappel else 0.0


def pct(n, total):
    return round(100 * n / total, 1) if total else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seuil", type=float, default=0.0, help="score minimum Presidio")
    parser.add_argument("--limite", type=int, default=None, help="n'évaluer que N exemples")
    args = parser.parse_args()

    with FICHIER_ECHANTILLON.open(encoding="utf-8") as f:
        exemples = [json.loads(l) for l in f][: args.limite]

    print("Chargement de Presidio...")
    analyzer = creer_analyzer()
    analyser(analyzer, "Échauffement du modèle.")  # exclut le 1er appel "à froid" des mesures

    # Compteurs par label AI4Privacy
    par_label = defaultdict(lambda: {"total": 0, "detecte_tous_types": 0, "detecte_type": 0})
    # Compteurs par type prédit par Presidio
    par_type = defaultdict(lambda: {"predictions": 0, "correctes_tous_types": 0, "correctes_type": 0})
    durees = []
    oublis, faux_positifs = [], []

    for i, ex in enumerate(exemples, 1):
        texte, gold = ex["texte"], ex["annotations"]
        preds, duree = analyser(analyzer, texte)
        preds = [p for p in preds if p["score"] >= args.seuil]
        durees.append(duree)

        # Rappel : chaque donnée annotée est-elle trouvée ?
        for g in gold:
            attendu = CORRESPONDANCE.get(g["label"])
            touches = [p for p in preds if chevauche(g["debut"], g["fin"], p["debut"], p["fin"])]
            stats = par_label[g["label"]]
            stats["total"] += 1
            stats["detecte_tous_types"] += bool(touches)
            stats["detecte_type"] += any(p["type"] == attendu for p in touches)
            if not touches:
                oublis.append({"uid": ex["uid"], "label": g["label"], "valeur": g["valeur"]})

        # Précision : chaque détection Presidio correspond-elle à une donnée annotée ?
        for p in preds:
            touches = [g for g in gold if chevauche(g["debut"], g["fin"], p["debut"], p["fin"])]
            stats = par_type[p["type"]]
            stats["predictions"] += 1
            stats["correctes_tous_types"] += bool(touches)
            stats["correctes_type"] += any(CORRESPONDANCE.get(g["label"]) == p["type"] for g in touches)
            if not touches:
                faux_positifs.append(
                    {"uid": ex["uid"], "type": p["type"], "texte": p["texte"], "score": p["score"]}
                )

        if i % 100 == 0:
            print(f"  {i}/{len(exemples)} exemples analysés")

    # ---- Tableaux de résultats ----
    df_label = pd.DataFrame(
        [
            {
                "label_ai4privacy": label,
                "type_presidio_attendu": CORRESPONDANCE.get(label) or "-",
                "nb": s["total"],
                "rappel_type_%": pct(s["detecte_type"], s["total"]) if CORRESPONDANCE.get(label) else None,
                "rappel_tous_types_%": pct(s["detecte_tous_types"], s["total"]),
            }
            for label, s in par_label.items()
        ]
    ).sort_values("nb", ascending=False)

    df_type = pd.DataFrame(
        [
            {
                "type_presidio": t,
                "nb_predictions": s["predictions"],
                "precision_type_%": pct(s["correctes_type"], s["predictions"]),
                "precision_tous_types_%": pct(s["correctes_tous_types"], s["predictions"]),
            }
            for t, s in par_type.items()
        ]
    ).sort_values("nb_predictions", ascending=False)

    # ---- Scores globaux ----
    total_gold = sum(s["total"] for s in par_label.values())
    total_pred = sum(s["predictions"] for s in par_type.values())
    rappel_any = sum(s["detecte_tous_types"] for s in par_label.values()) / total_gold
    precision_any = sum(s["correctes_tous_types"] for s in par_type.values()) / total_pred

    gold_mappe = {l: s for l, s in par_label.items() if CORRESPONDANCE.get(l)}
    rappel_type = sum(s["detecte_type"] for s in gold_mappe.values()) / sum(
        s["total"] for s in gold_mappe.values()
    )
    precision_type = sum(s["correctes_type"] for s in par_type.values()) / total_pred

    durees_triees = sorted(durees)
    p95 = durees_triees[int(0.95 * (len(durees_triees) - 1))]

    pd.set_option("display.width", 140)
    print(f"\n=== Presidio natif (fr) sur {len(exemples)} exemples AI4Privacy — seuil {args.seuil} ===\n")
    print("Par label AI4Privacy (RAPPEL = part des données trouvées) :")
    print(df_label.to_string(index=False))
    print("\nPar type Presidio (PRÉCISION = part des détections justes) :")
    print(df_type.to_string(index=False))
    print("\nGlobal :")
    print(f"  Tous types (blocage)   : précision {precision_any:.1%} | rappel {rappel_any:.1%} "
          f"| F1 {f1(precision_any, rappel_any):.1%}")
    print(f"  Typé (labels mappés)   : précision {precision_type:.1%} | rappel {rappel_type:.1%} "
          f"| F1 {f1(precision_type, rappel_type):.1%}")
    print(f"  Temps par texte        : moyenne {statistics.mean(durees):.1f} ms "
          f"| médiane {statistics.median(durees):.1f} ms | p95 {p95:.1f} ms")

    # ---- Sauvegarde ----
    DOSSIER_RESULTATS.mkdir(parents=True, exist_ok=True)
    df_label.to_csv(DOSSIER_RESULTATS / "ai4privacy_par_label.csv", index=False, encoding="utf-8-sig")
    df_type.to_csv(DOSSIER_RESULTATS / "ai4privacy_par_type.csv", index=False, encoding="utf-8-sig")
    with (DOSSIER_SORTIE / "erreurs.json").open("w", encoding="utf-8") as f:
        json.dump({"oublis": oublis, "faux_positifs": faux_positifs}, f, ensure_ascii=False, indent=1)
    print(f"\nRésultats enregistrés dans {DOSSIER_RESULTATS} et {DOSSIER_SORTIE}")


if __name__ == "__main__":
    main()
