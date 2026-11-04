"""
CyberSentinel - premier prototype du proxy.

Lance avec :  mitmdump -s proxy/addon.py
Repère les données sensibles envoyées aux sites d'IA et les affiche dans le terminal.
Étape suivante : bloquer / masquer, puis envoyer l'événement à l'API.
"""
import re

from mitmproxy import http

# Sites d'IA surveillés
AI_HOSTS = (
    "chatgpt.com",
    "chat.openai.com",
    "api.openai.com",
    "gemini.google.com",
    "claude.ai",
    "copilot.microsoft.com",
    "chat.mistral.ai",
)

# Données sensibles recherchées
PATTERNS = {
    "IBAN": re.compile(r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){3,7}(?: ?[A-Z0-9]{1,3})?\b"),
    "Numéro de sécurité sociale": re.compile(
        r"\b[12] ?\d{2} ?(?:0[1-9]|1[0-2]) ?(?:\d{2}|2A|2B) ?\d{3} ?\d{3} ?\d{2}\b"
    ),
    "Carte bancaire": re.compile(r"\b(?:\d{4}[ -]?){3}\d{4}\b"),
    "Clé API": re.compile(r"\b(?:sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36})\b"),
    "E-mail": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "Téléphone": re.compile(r"(?:\+33 ?|\b0)[1-9](?:[ .-]?\d{2}){4}\b"),
}


def luhn_ok(number: str) -> bool:
    """Vérifie qu'un numéro de carte est valide (algorithme de Luhn)."""
    digits = [int(d) for d in number if d.isdigit()]
    total = 0
    for i, d in enumerate(reversed(digits)):
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def find_sensitive(text: str) -> list[tuple[str, str]]:
    """Renvoie la liste (type, valeur trouvée), sans doublons qui se chevauchent."""
    found = []
    taken = []  # zones du texte déjà détectées
    for label, pattern in PATTERNS.items():
        for m in pattern.finditer(text):
            start, end = m.span()
            if any(start < t_end and end > t_start for t_start, t_end in taken):
                continue
            if label == "Carte bancaire" and not luhn_ok(m.group()):
                continue
            taken.append((start, end))
            found.append((label, m.group()))
    return found


def request(flow: http.HTTPFlow) -> None:
    host = flow.request.pretty_host
    if not any(host.endswith(h) for h in AI_HOSTS):
        return
    if flow.request.method != "POST":
        return

    body = flow.request.get_text(strict=False) or ""
    findings = find_sensitive(body)
    if findings:
        print(f"\n[CyberSentinel] ALERTE vers {host}")
        for label, value in findings:
            print(f"   - {label} : {value}")
