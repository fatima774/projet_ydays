"""
CyberSentinel · addon mitmproxy du module M1 (carte #28).

Pour chaque requête envoyée à une IA :
  1. reconnaît le site (ChatGPT, Gemini, Mistral, Claude, Copilot) ;
  2. extrait le prompt avec la bonne méthode (formulaire, JSON, protobuf, base64) ;
  3. appelle detect(texte) ;
  4. écrit un événement JSON par donnée trouvée dans logs/evenements.jsonl
     (format de docs/format-evenement.md) et affiche une alerte.

Lancer depuis la racine du dépôt :
    mitmweb --set http2=false -s proxy/cybersentinel.py

Pour bloquer vraiment les requêtes dont l'action est « bloquer » :
    mitmweb --set http2=false -s proxy/cybersentinel.py --set cs_bloquer=true

Où passe le prompt sur chaque site : docs/captures-sites-ia.md
"""
from __future__ import annotations

import base64
import json
import re
import socket
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from mitmproxy import ctx, http

RACINE = Path(__file__).resolve().parent.parent
FICHIER_EVENEMENTS = RACINE / "logs" / "evenements.jsonl"
POSTE = socket.gethostname()

# --- PyYAML n'est pas fourni avec l'installeur Windows de mitmproxy, mais ruamel.yaml l'est ---
try:
    import yaml  # noqa: F401
except ImportError:
    import types
    from ruamel.yaml import YAML

    _yaml = types.ModuleType("yaml")
    _yaml.safe_load = lambda flux: YAML(typ="safe", pure=True).load(flux)
    sys.modules["yaml"] = _yaml

# --- detect() : celle de Nolan si elle est là (detection/), sinon les règles d'Aloïs seules ---
sys.path.insert(0, str(RACINE))
sys.path.insert(0, str(RACINE / "rules"))
try:
    from detection.detect import detect, mask_text  # règles + modèle
    VERSION_DETECT = "detection.detect"
except ImportError:
    from m1_detect import detect, mask_text  # règles M1 seules
    VERSION_DETECT = "rules.m1_detect"

ORDRE_ACTION = {"bloquer": 3, "masquer": 2, "alerter": 1}


# ---------------------------------------------------------------------
# Extraction du prompt, site par site (voir docs/captures-sites-ia.md)
# ---------------------------------------------------------------------

def textes_lisibles(brut: bytes) -> list[str]:
    """Morceaux de texte lisible (au moins 4 caractères) dans un corps binaire (protobuf)."""
    morceaux = re.findall(rb"[\x20-\x7e\xc2-\xf4\x80-\xbf]{4,}", brut)
    return [m.decode("utf-8", "ignore").strip() for m in morceaux if m.strip()]


def prompt_chatgpt(flow: http.HTTPFlow) -> list[str]:
    # Sans compte : formulaire, champ « prompt »
    if flow.request.urlencoded_form and "prompt" in flow.request.urlencoded_form:
        return [flow.request.urlencoded_form["prompt"]]
    # Connecté (pas encore capturé) : on se rabat sur tout le corps
    return [flow.request.get_text(strict=False) or ""]


def prompt_mistral(flow: http.HTTPFlow) -> list[str]:
    # JSON : messageInput[].text
    try:
        corps = json.loads(flow.request.get_text(strict=False) or "{}")
    except json.JSONDecodeError:
        return []
    return [m.get("text", "") for m in corps.get("messageInput", []) if m.get("type") == "text"]


def prompt_copilot(flow: http.HTTPFlow) -> list[str]:
    # JSON : champ « content » (envoyé avant même la demande de connexion)
    try:
        corps = json.loads(flow.request.get_text(strict=False) or "{}")
    except json.JSONDecodeError:
        return []
    return [corps["content"]] if isinstance(corps.get("content"), str) else []


def prompt_claude(flow: http.HTTPFlow) -> list[str]:
    # protobuf brut : le prompt est une chaîne lisible dans le binaire
    return textes_lisibles(flow.request.raw_content or b"")


def prompt_gemini(flow: http.HTTPFlow) -> list[str]:
    # formulaire WebChannel : reqN___data__ = protobuf encodé en base64
    textes = []
    for cle, valeur in flow.request.urlencoded_form.items(multi=True):
        if cle.startswith("req") and cle.endswith("___data__"):
            try:
                brut = base64.b64decode(valeur + "==")
            except ValueError:
                continue
            textes += textes_lisibles(brut)
    return textes


# domaine, début du chemin, fonction d'extraction
SITES = [
    ("chatgpt.com", "/unauth-mweb/conversation", prompt_chatgpt),
    ("chatgpt.com", "/backend-api/", prompt_chatgpt),
    ("chat.mistral.ai", "/api/chat", prompt_mistral),
    ("claude.ai", "/claudeai-rpc/", prompt_claude),
    ("geminiweb-pa.clients6.google.com", "/v1/processSession", prompt_gemini),
    ("turbo.microsoft.com", "/pe/api/artifacts/", prompt_copilot),
]


def domaine_ok(hote: str, domaine: str) -> bool:
    """Vrai si hote == domaine ou en est un sous-domaine (faux-claude.ai ne passe pas)."""
    return hote == domaine or hote.endswith("." + domaine)


def trouver_site(flow: http.HTTPFlow):
    hote, chemin = flow.request.pretty_host, flow.request.path
    for domaine, debut_chemin, extraire in SITES:
        if domaine_ok(hote, domaine) and chemin.startswith(debut_chemin):
            return domaine, extraire
    return None, None


# ---------------------------------------------------------------------
# Événement (docs/format-evenement.md)
# ---------------------------------------------------------------------

def extrait_autour(texte_masque: str, debut: int, fin: int, largeur: int = 200) -> str:
    """Contexte d'au plus `largeur` caractères autour de la donnée, dans le texte déjà masqué."""
    marge = max(0, (largeur - (fin - debut)) // 2)
    a, b = max(0, debut - marge), min(len(texte_masque), fin + marge)
    extrait = texte_masque[a:b][:largeur]
    return ("…" if a > 0 else "") + extrait + ("…" if b < len(texte_masque) else "")


def evenement(site: str, texte_masque: str, f: dict, requete_id: str, latence_ms: int) -> dict:
    """Un événement pour une donnée trouvée. `texte_masque` = le prompt avec TOUTES ses données masquées."""
    source = f.get("source", "regle")
    return {
        "id": str(uuid.uuid4()),
        "requete_id": requete_id,
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source": {"poste": POSTE, "module": "M1"},
        "site_ia": site,
        "type_donnee": f.get("libelle", f.get("regle")),
        "regle": f"m1.{f['regle']}" if source == "regle" else "modele",
        "detecteur": "modele" if source == "modele" else "regle",
        "score": f.get("score"),
        "etiquette": f.get("categorie"),
        "explication": f"{f.get('libelle')} détecté dans le prompt envoyé à {site}.",
        "action": f.get("action"),
        "extrait_masque": extrait_autour(texte_masque, f["debut"], f["fin"]) if source == "regle" else "",
        "version_modele": VERSION_DETECT,
        "latence_ms": latence_ms,
    }


def ecrire(evenements: list[dict]) -> None:
    FICHIER_EVENEMENTS.parent.mkdir(exist_ok=True)
    with open(FICHIER_EVENEMENTS, "a", encoding="utf-8") as fichier:
        for e in evenements:
            fichier.write(json.dumps(e, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------
# Hooks mitmproxy
# ---------------------------------------------------------------------

def load(loader) -> None:
    loader.add_option("cs_bloquer", bool, False, "Bloquer les requêtes dont l'action est « bloquer »")


def request(flow: http.HTTPFlow) -> None:
    if flow.request.method != "POST":
        return
    site, extraire = trouver_site(flow)
    if site is None:
        return

    t0 = time.perf_counter()
    trouves = []  # (prompt masqué, détection)
    for prompt in extraire(flow):
        if prompt and prompt.strip():
            resultats = detect(prompt)
            # RGPD : on masque toutes les données du prompt avant d'en garder un extrait
            # (le masquage garde la longueur, donc debut/fin restent valables)
            masque = mask_text(prompt, [f for f in resultats if f.get("source", "regle") == "regle"])
            trouves += [(masque, f) for f in resultats]
    latence_ms = round((time.perf_counter() - t0) * 1000)
    if not trouves:
        return

    requete_id = str(uuid.uuid4())
    evenements = [evenement(site, m, f, requete_id, latence_ms) for m, f in trouves]
    ecrire(evenements)

    action = max((e["action"] for e in evenements), key=lambda a: ORDRE_ACTION.get(a, 0))
    ctx.log.warn(f"[CyberSentinel] {site} : {len(evenements)} donnée(s) sensible(s), action « {action} »")
    for e in evenements:
        ctx.log.warn(f"   - {e['type_donnee']} ({e['action']}) : {e['extrait_masque']}")

    if action == "bloquer" and ctx.options.cs_bloquer:
        flow.response = http.Response.make(
            403,
            "CyberSentinel : requête bloquée, elle contient une donnée sensible.",
            {"Content-Type": "text/plain; charset=utf-8"},
        )
