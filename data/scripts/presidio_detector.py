"""
Configuration de Microsoft Presidio pour analyser des textes en français.

Presidio = moteur de détection de données personnelles (PII).
Il combine :
  - des recognizers à base de règles (regex + checksum) : IBAN, e-mail, IP...
  - un modèle NER spaCy (ici fr_core_news_lg) : noms de personnes, lieux, organisations.

Ici on utilise UNIQUEMENT les capacités natives de Presidio (aucun recognizer
personnalisé), pour mesurer honnêtement ce que l'outil fait "tel quel".
"""

import time

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider

LANGUE = "fr"
MODELE_SPACY = "fr_core_news_lg"


def creer_analyzer() -> AnalyzerEngine:
    """Crée un AnalyzerEngine Presidio configuré pour le français."""
    configuration_nlp = {
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": LANGUE, "model_name": MODELE_SPACY}],
    }
    moteur_nlp = NlpEngineProvider(nlp_configuration=configuration_nlp).create_engine()
    return AnalyzerEngine(nlp_engine=moteur_nlp, supported_languages=[LANGUE])


def analyser(analyzer: AnalyzerEngine, texte: str):
    """
    Analyse un texte et renvoie (liste des entités détectées, temps en ms).
    Chaque entité = dict {type, texte, debut, fin, score}.
    """
    debut = time.perf_counter()
    resultats = analyzer.analyze(text=texte, language=LANGUE)
    duree_ms = (time.perf_counter() - debut) * 1000

    entites = [
        {
            "type": r.entity_type,
            "texte": texte[r.start:r.end],
            "debut": r.start,
            "fin": r.end,
            "score": round(r.score, 2),
        }
        for r in sorted(resultats, key=lambda r: r.start)
    ]
    return entites, duree_ms


if __name__ == "__main__":
    # Premier test simple : un prompt français avec des données FICTIVES.
    analyzer = creer_analyzer()

    print("Entités supportées en français :")
    print(sorted(analyzer.get_supported_entities(language=LANGUE)))
    print()

    prompt = (
        "Bonjour, je suis Marie Dupont, j'habite à Lyon. "
        "Peux-tu rédiger un mail pour mon banquier ? Mon IBAN est "
        "FR76 3000 6000 0112 3456 7890 189, mon mail marie.dupont@exemple.fr "
        "et mon téléphone 06 12 34 56 78. Ma clé API OpenAI est "
        "sk-proj-AbC123xYz456DeF789ghI012jKl345mNo678."
    )
    print("Prompt :", prompt)
    print()

    # 1er appel = "à froid" (chargements internes), on mesure aussi un 2e appel.
    entites, t1 = analyser(analyzer, prompt)
    _, t2 = analyser(analyzer, prompt)

    for e in entites:
        print(f"  {e['type']:<15} score={e['score']:<5} -> {e['texte']!r}")
    print()
    print(f"Temps : 1er appel {t1:.1f} ms | 2e appel {t2:.1f} ms")
