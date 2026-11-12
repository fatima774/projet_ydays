# data/

Jeu de prompts en français étiquetés « sensible / pas sensible », notebooks d'analyse et modèle de classification.

- Uniquement des **données inventées** : aucune vraie donnée personnelle.
- Les fichiers lourds (`data/raw/`, modèles `.joblib`) ne sont pas envoyés sur GitHub.

**Responsables :** Elias, Imad, Nolan.

## Contenu

| Fichier | Auteur | Contenu |
|---|---|---|
| `prompts_v1.csv` | Nolan | 150 prompts français étiquetés (guide : `docs/guide-annotation.md`) |
| `presidio_test.ipynb` | Imad | Test de Presidio sur les prompts, comparaison avec les règles M1, métriques |
| `scripts/presidio_detector.py` | Imad | Configuration de Presidio en français (spaCy `fr_core_news_lg`) |
| `scripts/preparer_dataset.py` | Imad | Téléchargement des exemples français d'AI4Privacy et échantillonnage |
| `scripts/evaluer_presidio.py` | Imad | Évaluation de Presidio sur l'échantillon AI4Privacy |
| `scripts/m1_source.py` | Imad | Charge les règles M1 d'Aloïs (`rules/`, ou branche `cyber` si pas encore fusionnée) |
| `resultats/` | Imad | Tableaux de résultats (AI4Privacy et prompts), sans aucune valeur en clair |

Synthèse : `docs/choix-modele-metriques.md` et `docs/analyse-dataset-ai4privacy.md`.

## Installer l'environnement

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r data\requirements.txt
.\.venv\Scripts\python -m spacy download fr_core_news_lg
```

Puis ouvrir `data/presidio_test.ipynb` et lancer toutes les cellules.
