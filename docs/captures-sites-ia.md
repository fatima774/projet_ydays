# Captures des sites d'IA (mitmproxy)

Captures faites par Arno le 12/11/2026 (Firefox 152, mitmproxy 12.3.1, `--set http2=false`, **sans compte**).
Méthode : envoyer `TESTCYBER bonjour`, puis filtre mitmweb `~b TESTCYBER`.
But : confirmer/corriger `rules/sites_ia.yaml` (Aloïs).

## ChatGPT ✅

| | |
|---|---|
| Requête | `POST https://chatgpt.com/unauth-mweb/conversation/updates` |
| Format | `application/x-www-form-urlencoded` |
| Prompt | champ `prompt`, en clair |
| Pour sites_ia.yaml | ajouter le chemin `/unauth-mweb/conversation/updates`, `format: form`, `champ_prompt: prompt` (mode sans compte) |

## Gemini ✅ (prompt encodé, mais décodable)

| | |
|---|---|
| Domaine | `geminiweb-pa.clients6.google.com` (**pas dans sites_ia.yaml**) |
| Requêtes | `POST /v1/processSession?VER=8&gsessionid=...&SID=...&RID=...` (WebChannel Google : les POST envoient, les GET attendent la réponse) |
| Format | `application/x-www-form-urlencoded`, champs `count`, `ofs`, `req0___data__` (puis `req1___data__`... si plusieurs messages) |
| `req0___data__` | **protobuf encodé en base64** |
| Prompt | dans un **petit POST** (~100 octets) : `EhcIAUoTChFURVNUQ1lCRVIgYm9uam91cg==` → protobuf `{2: {1: 1, 9: {1: "TESTCYBER bonjour"}}}` |
| Gros POST (2,7 à 3,9 ko) | ouverture de session : identifiants + jeton anti-robot, pas de prompt |
| `StreamGenerate` sur gemini.google.com | **aucune requête vue** : l'entrée actuelle de sites_ia.yaml semble obsolète |

`~b TESTCYBER` ne trouve rien car le texte est en base64. Pour l'addon, pas besoin de comprendre
le protobuf : on décode le base64 et on garde les morceaux de texte lisibles, puis on appelle `detect()` dessus.

```python
import base64, re

def textes_gemini(flow):
    """Renvoie les textes lisibles des messages WebChannel de Gemini."""
    textes = []
    for cle, valeur in flow.request.urlencoded_form.items(multi=True):
        if cle.startswith("req") and cle.endswith("___data__"):
            try:
                brut = base64.b64decode(valeur + "==")
            except ValueError:
                continue
            # suites d'au moins 4 caractères imprimables (UTF-8)
            for morceau in re.findall(rb"[\x20-\x7e\xc2-\xf4\x80-\xbf]{4,}", brut):
                textes.append(morceau.decode("utf-8", "ignore"))
    return textes
```

Remarque : on a vu le texte deux fois (`TESTCYBER bonjour` et ` TESTCYBER bonjour `). Gemini envoie peut-être
le texte pendant la frappe : la donnée sortirait **avant même** que l'utilisateur appuie sur Entrée.
À vérifier (taper un texte sans l'envoyer et regarder si un POST part).

## Mistral (Le Chat) ✅

| | |
|---|---|
| Requête | `POST https://chat.mistral.ai/api/chat` |
| Format | `application/json` |
| Prompt | `messageInput[].text` (avec `type: "text"`), en clair |
| Fichiers joints | `messageFiles[]` (à surveiller aussi) |
| Pour sites_ia.yaml | `chemins: ["/api/chat"]`, `format: json`, `champ_prompt: "messageInput[].text"` |

Extrait du corps :

```json
{
  "chatId": "<uuid>",
  "mode": "append",
  "messageInput": [{"type": "text", "text": "TESTCYBER bonjour"}],
  "messageFiles": [],
  "messageId": "<uuid>",
  "modelConfig": {"model_alias": "...", "reasoning_effort": "low"}
}
```

**Remarque importante :** sans compte, Le Chat demande de se connecter **après** l'envoi, mais la requête
`/api/chat` est **déjà partie** avec le prompt (2 requêtes vues, réponse 200). La donnée a donc quitté le poste
même si l'utilisateur ne se connecte jamais. Bon exemple pour la démo.

## Claude (claude.ai) ✅ (protobuf, mais texte lisible)

Capture faite **connecté** (claude.ai n'est pas utilisable sans compte).

| | |
|---|---|
| Requête | `POST https://claude.ai/claudeai-rpc/anthropic.bard.api.v1alpha.ConversationService/PerformAction` |
| Format | `application/proto` (protobuf brut, **pas** de base64) |
| Prompt | chaîne UTF-8 en clair dans le protobuf (juste après les 2 uuid de conversation/message) |
| Autres champs vus | id de session (`sess_...`), uuid de conversation, nom du modèle, `fr-FR`, `Europe/Paris` |
| Pour sites_ia.yaml | `chemins: ["/claudeai-rpc/"]` (au lieu de `/api/organizations/`), `format: protobuf` |

Extrait (hexdump mitmweb, identifiants masqués) :

```
... 1a 11 54 45 53 54 43 59 42 45 52 20 62 6f 6e 6a 6f 75 72 ...   ..TESTCYBER bonjour
```

`~b TESTCYBER` trouve aussi `ConversationService/StreamTimeline` (`application/connect+proto`), mais là le texte
est dans la **réponse** (fil de la conversation), pas dans la requête. Utiliser `~bq` pour ne chercher que dans les requêtes.

Pour l'addon : même méthode que Gemini **sans** l'étape base64 : extraire les morceaux de texte lisibles du corps
binaire, puis `detect()`.

## Copilot ✅ (sans compte, avant connexion)

| | |
|---|---|
| Requête | `POST https://turbo.microsoft.com/pe/api/artifacts/encodeArtifactUnauthenticated` |
| Domaine | `turbo.microsoft.com` (**pas dans sites_ia.yaml**) |
| Format | `application/json` |
| Prompt | champ `content`, en clair |

```json
{"content": "TESTCYBER bonjour", "cmmId": "<id>", "correlationId": "<uuid>"}
```

**Comme Mistral :** Copilot demande de se connecter, mais le prompt est **déjà envoyé** à Microsoft avant
(probablement pour le garder pendant la connexion). La donnée quitte le poste même si l'utilisateur abandonne.

**Pas encore testé :** Copilot connecté (le vrai chat passe sûrement par un WebSocket, filtre `~websocket`).

## Résumé pour l'addon

| Site | Format | Comment lire le prompt |
|---|---|---|
| ChatGPT (sans compte) | formulaire | `urlencoded_form["prompt"]` |
| Mistral | JSON | `messageInput[].text` |
| Claude | protobuf brut | textes lisibles du corps |
| Gemini | formulaire + base64 + protobuf | base64 de `reqN___data__`, puis textes lisibles |
| Copilot (sans compte) | JSON | `content` (domaine `turbo.microsoft.com`) |

Leçon générale : **ne jamais analyser le corps brut** (`get_text()`), toujours décoder selon le format du site.
Méthode de secours qui marche partout : décoder ce qui est encodé, puis extraire tous les morceaux de texte lisibles.
