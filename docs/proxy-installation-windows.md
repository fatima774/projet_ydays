# Installer le proxy CyberSentinel (mitmproxy) sur Windows

Procédure testée le 12/11/2026 (séance 2) sur Windows 11 + Firefox 152.
But : faire passer Firefox par mitmproxy pour lire en clair ce qu'on envoie à ChatGPT.

> ⚠️ Le certificat de mitmproxy permet de lire **tout** le trafic HTTPS du navigateur qui l'accepte.
> On l'installe **uniquement dans Firefox** (jamais dans Windows), et on le retire à la fin (voir « Nettoyage »).

## 1. Installer mitmproxy

1. Télécharger l'installeur Windows sur https://mitmproxy.org (bouton **Download**).
2. Lancer le `.exe`, options par défaut. À la fin, **décocher** « Launch mitmproxy ».
3. Ouvrir un **nouveau** PowerShell et lancer :

```powershell
mitmweb --set http2=false
```

- Le proxy écoute sur `127.0.0.1:8080`.
- L'interface web s'ouvre sur `http://127.0.0.1:8081` (n'importe quel navigateur, Chrome compris).
- `--set http2=false` : sans cette option, mitmproxy plante sur certains sites
  (`ValueError: Flow control increment must be between 1 and 2147483647`).

> Pas besoin de Python : l'installeur embarque le sien. (`pip install mitmproxy` demande Python 3.12 ou plus.)

## 2. Brancher Firefox sur le proxy

Firefox → **Paramètres** → chercher `proxy` → **Paramètres…**

- Cocher **Configuration manuelle du proxy**
- Proxy HTTP : `127.0.0.1`, port `8080`
- Cocher **Utiliser également ce proxy pour HTTPS**
- OK

Seul Firefox passe par le proxy, le reste du PC n'est pas touché.

## 3. Installer le certificat dans Firefox

Le fichier est créé au premier lancement de mitmproxy : `%USERPROFILE%\.mitmproxy\mitmproxy-ca-cert.pem`

1. Firefox → **Paramètres** → **Vie privée et sécurité** → **Afficher les certificats…**
2. Onglet **Autorités** → **Importer…**
3. Coller `%USERPROFILE%\.mitmproxy` dans la barre d'adresse, choisir `mitmproxy-ca-cert.pem`
4. Cocher **Confirmer cette AC pour identifier des sites web** → OK

(La page `http://mitm.it` propose aussi le certificat, mais chez nous l'import ne s'est pas fait tout seul.)

**Vérification :** ouvrir `https://chatgpt.com` dans Firefox. La page s'affiche et les requêtes
`chatgpt.com` apparaissent dans mitmweb.
Si mitmproxy affiche `Client TLS handshake failed. The client does not trust the proxy's certificate`,
le certificat n'est pas (bien) importé.

## 4. Où passe le prompt sur chatgpt.com

Méthode : envoyer un message repère (`TESTCYBER bonjour`), puis dans mitmweb, champ **Search** : `~b TESTCYBER`
(`~b` = cherche dans le corps des requêtes).

**Résultat (ChatGPT sans compte, 12/11/2026) :**

| | |
|---|---|
| Méthode + adresse | `POST https://chatgpt.com/unauth-mweb/conversation/updates?lightweight_authenticated=0&operationId=<uuid>` |
| Content-Type | `application/x-www-form-urlencoded;charset=UTF-8` (**pas du JSON**) |
| Champ qui contient le prompt | `prompt` |
| Réponse attendue | `Accept: application/vnd.openai.conversation-source+ndjson` (flux) |

Extrait du corps (vue **URL-encoded** de mitmweb, jetons masqués) :

```
conversationState: '{"messages":[],"parentMessageId":"client-created-root",...}'
oai-session-id: <masqué>
imageAttachments: '[]'
prompt: TESTCYBER bonjour
timezone: Europe/Paris
assistantMessageId: pending-<uuid>
userMessageId: <uuid>
chatRequirementsToken: <masqué>
proofToken: <masqué>
turnstileToken: <masqué>
```

Le corps brut ressemble à : `prompt=TESTCYBER+bonjour&timezone=Europe%2FParis&...`
→ les espaces deviennent `+`, `@` devient `%40`, etc.

Autres requêtes vues sans intérêt pour nous : `/unauth-mweb/events/*` (statistiques),
`/unauth-mweb/sentinel/chat-requirements/prepare` (anti-bot), `/unauth-mweb/conversation/prepare`.

**À vérifier plus tard :** avec un compte connecté, l'adresse et le format sont sûrement différents
(probablement du JSON sur `/backend-api/...`). Même méthode `~b TESTCYBER` pour la trouver.

> 🔒 Ne jamais coller les en-têtes `Cookie`, `x-conduit-token`, `OAI-Session-Id` ni les `*Token`
> dans le dépôt ou un chat : ce sont des jetons de session.

## 5. Bonus : faire tourner l'addon `proxy/addon.py`

Depuis le dossier du dépôt :

```powershell
mitmweb --set http2=false -s proxy/addon.py
```

Puis envoyer dans ChatGPT un faux IBAN, par exemple : `TESTCYBER FR76 3000 6000 0112 3456 7890 189`.
L'alerte doit s'afficher dans le PowerShell.

**Constat :** sur ChatGPT sans compte, l'addon **ne détecte rien**. Il lit le corps brut (`get_text`),
donc il voit `FR76+3000+6000+...` et `jean.dupont%40ynov.com` : les regex ne reconnaissent plus rien.
Testé hors ligne avec les mêmes regex :

| Texte analysé | Résultat |
|---|---|
| corps encodé `prompt=...FR76+3000+6000...` | aucune détection |
| prompt décodé `...FR76 3000 6000...` | IBAN, e-mail, téléphone détectés |

**Correction proposée (pour Fati)** : décoder le formulaire avant d'analyser, dans `request()` :

```python
    content_type = flow.request.headers.get("content-type", "")
    if "x-www-form-urlencoded" in content_type:
        body = " ".join(flow.request.urlencoded_form.values())
    else:
        body = flow.request.get_text(strict=False) or ""
```

## Nettoyage (à la fin des tests)

1. Firefox → paramètres proxy → **Pas de proxy** (ou « Utiliser les paramètres proxy du système »)
2. Firefox → **Afficher les certificats…** → **Autorités** → supprimer **mitmproxy**
3. Fermer mitmweb (Ctrl+C dans PowerShell)
