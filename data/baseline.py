"""CyberSentinel — bonus Nolan : baseline TF-IDF + régression logistique.

Apprend la catégorie d'un prompt (non_sensible, identite, finance, sante,
secret_technique, donnees_clients) à partir de data/prompts_v1.csv.

1. Mesure honnête par validation croisée (le modèle ne voit jamais le prompt qu'il prédit).
2. Entraîne le modèle final sur tout le fichier et l'enregistre dans
   data/modele_baseline.joblib, que detection/detect.py charge automatiquement.

Installation : pip install scikit-learn pandas joblib
Lancement    : python data/baseline.py
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline, make_union

DOSSIER = Path(__file__).resolve().parent
CSV = DOSSIER / "prompts_v1.csv"
SORTIE = DOSSIER / "modele_baseline.joblib"


def creer_modele():
    mots = TfidfVectorizer(analyzer="word", ngram_range=(1, 2), sublinear_tf=True)
    caracteres = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)
    return make_pipeline(
        make_union(mots, caracteres),
        LogisticRegression(max_iter=3000, class_weight="balanced", C=10),
    )


def main():
    df = pd.read_csv(CSV, encoding="utf-8-sig")
    X, y = df["texte"], df["categorie"]

    # 1. Mesure honnête : validation croisée en 5 parties
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    pred = cross_val_predict(creer_modele(), X, y, cv=cv)

    print("=== Par catégorie (validation croisée 5 plis) ===")
    print(classification_report(y, pred, zero_division=0))

    sensible = df["sensible"] == 1
    alerte = pred != "non_sensible"
    rappel = (alerte & sensible).sum() / sensible.sum()
    fausses = (alerte & ~sensible).sum() / (~sensible).sum()
    pieges = (alerte & (df["piege"] == 1)).sum()
    print("=== Sensible / non sensible ===")
    print(f"rappel          : {rappel:.0%}")
    print(f"fausses alertes : {fausses:.0%}  (pièges déclenchés : {pieges}/{(df['piege'] == 1).sum()})")

    # 2. Modèle final sur tout le jeu
    modele = creer_modele().fit(X, y)
    joblib.dump(modele, SORTIE)
    print(f"\nModèle enregistré : {SORTIE.relative_to(DOSSIER.parent)}")


if __name__ == "__main__":
    main()
