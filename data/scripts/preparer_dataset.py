"""
Extraction des exemples FRANÇAIS du dataset AI4Privacy OpenPII 1M.

Source : https://huggingface.co/datasets/ai4privacy/pii-masking-openpii-1m
Licence : CC-BY-4.0 — attribution « Ai4Privacy / Ai Suisse SA ».
Données : 100 % synthétiques (aucune vraie donnée personnelle).

On lit la version Parquet convertie par Hugging Face, en ne récupérant que les
colonnes utiles (évite de télécharger les ~4,6 Go de JSONL d'origine).

Sorties :
  data/raw/ai4privacy_fr_validation.jsonl   -> tous les exemples FR du split validation
  data/processed/echantillon_fr.jsonl       -> échantillon aléatoire (reproductible)

Usage :
  python data/scripts/preparer_dataset.py              # échantillon de 1000 exemples
  python data/scripts/preparer_dataset.py --taille 200
"""

import argparse
import json
import random
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq
from huggingface_hub import HfFileSystem

DATASET = "ai4privacy/pii-masking-openpii-1m"
SPLIT = "validation"  # on garde "train" pour un éventuel entraînement futur
COLONNES = ["uid", "source_text", "privacy_mask", "language", "region"]

RACINE = Path(__file__).resolve().parents[2]  # racine du dépôt
FICHIER_BRUT = RACINE / "data" / "raw" / "ai4privacy_fr_validation.jsonl"
FICHIER_ECHANTILLON = RACINE / "data" / "processed" / "echantillon_fr.jsonl"


def extraire_exemples_fr() -> list[dict]:
    """Lit les fichiers Parquet du split et ne garde que les lignes language == 'fr'."""
    fs = HfFileSystem()
    dossier = f"datasets/{DATASET}@~parquet/default/{SPLIT}"
    fichiers = sorted(fs.glob(f"{dossier}/*.parquet"))

    exemples = []
    for chemin in fichiers:
        with fs.open(chemin) as f:
            parquet = pq.ParquetFile(f)
            for i in range(parquet.num_row_groups):
                table = parquet.read_row_group(i, columns=COLONNES)
                table = table.filter(pc.equal(table["language"], "fr"))
                exemples.extend(table.to_pylist())
        print(f"  {chemin.rsplit('/', 1)[-1]} lu -> {len(exemples)} exemples FR cumulés")
    return exemples


def nettoyer(exemple: dict) -> dict:
    """Garde uniquement les champs utiles des annotations."""
    return {
        "uid": exemple["uid"],
        "region": exemple["region"],
        "texte": exemple["source_text"],
        "annotations": [
            {"label": a["label"], "debut": a["start"], "fin": a["end"], "valeur": a["value"]}
            for a in exemple["privacy_mask"]
        ],
    }


def verifier_positions(exemples: list[dict]) -> int:
    """Contrôle que texte[debut:fin] == valeur pour chaque annotation. Renvoie le nb d'erreurs."""
    return sum(
        1
        for ex in exemples
        for a in ex["annotations"]
        if ex["texte"][a["debut"]:a["fin"]] != a["valeur"]
    )


def ecrire_jsonl(chemin: Path, lignes: list[dict]) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    with chemin.open("w", encoding="utf-8") as f:
        for ligne in lignes:
            f.write(json.dumps(ligne, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--taille", type=int, default=1000, help="taille de l'échantillon")
    parser.add_argument("--graine", type=int, default=42, help="graine aléatoire (reproductibilité)")
    args = parser.parse_args()

    if FICHIER_BRUT.exists():
        print(f"Lecture du cache local : {FICHIER_BRUT}")
        with FICHIER_BRUT.open(encoding="utf-8") as f:
            exemples = [json.loads(l) for l in f]
    else:
        print(f"Téléchargement des exemples FR de {DATASET} ({SPLIT})...")
        exemples = [nettoyer(e) for e in extraire_exemples_fr()]
        ecrire_jsonl(FICHIER_BRUT, exemples)

    erreurs = verifier_positions(exemples)
    nb_annotations = sum(len(e["annotations"]) for e in exemples)
    print(f"\nExemples FR ({SPLIT}) : {len(exemples)}")
    print(f"Annotations : {nb_annotations} (positions incohérentes : {erreurs})")

    random.seed(args.graine)
    echantillon = random.sample(exemples, min(args.taille, len(exemples)))
    ecrire_jsonl(FICHIER_ECHANTILLON, echantillon)
    print(f"Échantillon de {len(echantillon)} exemples -> {FICHIER_ECHANTILLON}")


if __name__ == "__main__":
    main()
