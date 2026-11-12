# Sites d'IA à couvrir

Le proxy n'analyse que le trafic vers les sites d'IA. La liste utilisée par le code est `rules/sites_ia.yaml`. Cette page explique les choix.

**Responsable :** Aloïs · **Captures :** Arno (12/11/2026, Firefox 152, mitmproxy 12.3.1, `--set http2=false`, prompt de test « TESTCYBER bonjour »)

## Priorités

| Priorité | Sites | Pourquoi |
| --- | --- | --- |
| 1 · démo | ChatGPT, Gemini, Claude, Le Chat (Mistral), Copilot | Les plus utilisés en entreprise en France ; demandés dans le sujet |
| 2 | DeepSeek, Perplexity, API OpenAI / Anthropic / Gemini / Mistral | Usage croissant ; les API sont appelées par les scripts et les extensions des développeurs |
| 3 | Grok, Meta AI, Poe, HuggingChat, GitHub Copilot | Moins courants en entreprise, à ajouter si on a le temps |

## Sites prioritaires : résultats des captures

| Site | Requête qui porte le prompt | Format | Comment lire le prompt | Statut |
| --- | --- | --- | --- | --- |
| ChatGPT | `POST chatgpt.com/unauth-mweb/conversation/updates` | formulaire | champ `prompt` | ✅ sans compte |
| Gemini | `POST geminiweb-pa.clients6.google.com/v1/processSession` | formulaire + base64 + protobuf | décoder `reqN___data__` en base64, puis garder le texte lisible | ✅ sans compte |
| Claude | `POST claude.ai/claudeai-rpc/…/ConversationService/PerformAction` | protobuf brut | garder le texte lisible du corps | ✅ connecté |
| Le Chat (Mistral) | `POST chat.mistral.ai/api/chat` | JSON | `messageInput[].text` (+ `messageFiles[]`) | ✅ sans compte |
| Copilot | `POST turbo.microsoft.com/pe/api/artifacts/encodeArtifactUnauthenticated` | JSON | champ `content` | ✅ sans compte |

Ce qui a changé par rapport à la première version :

- **ChatGPT** sans compte n'utilise pas `/backend-api/conversation` mais `/unauth-mweb/conversation/updates`, en formulaire. Le mode connecté reste à capturer.
- **Gemini** n'envoie plus rien à `gemini.google.com/…StreamGenerate`. Le prompt part vers un autre domaine, `geminiweb-pa.clients6.google.com`.
- **Claude** est passé de `/api/organizations/…` (JSON) à `/claudeai-rpc/` (protobuf).
- **Copilot** sans compte envoie le prompt à `turbo.microsoft.com`, un domaine qu'on n'avait pas.

## Constats importants (pour la démo et le dossier)

1. **La donnée part avant la connexion.** Sur Le Chat et Copilot sans compte, le site demande de se connecter *après* l'envoi, mais le prompt a déjà quitté le poste (réponse 200). Même si l'utilisateur abandonne, la donnée est chez l'éditeur. C'est un bon argument pour CyberSentinel : il faut intercepter au moment de l'envoi, pas compter sur l'utilisateur.
2. **Gemini enverrait le texte pendant la frappe.** Le texte a été vu deux fois. À vérifier : taper un texte sans appuyer sur Entrée et regarder si un POST part. Si c'est confirmé, une donnée collée puis effacée serait déjà sortie.
3. **Le prompt n'est pas toujours en clair.** Gemini l'encode en base64, Claude utilise du protobuf. Un filtre `~b TESTCYBER` ne trouve pas Gemini. Il faut décoder avant de chercher.

## Règle pour l'addon

Ne jamais analyser le corps brut avec `get_text()` : il faut toujours décoder selon le format du site (champ `extraction` de `rules/sites_ia.yaml`).

| `extraction` | Sites | Méthode |
| --- | --- | --- |
| `champ_form` | ChatGPT | `flow.request.urlencoded_form["prompt"]` |
| `champ_json` | Mistral, Copilot, API | lire le champ indiqué dans le JSON |
| `textes_lisibles` | Claude | extraire les suites de caractères lisibles du corps binaire |
| `base64_textes` | Gemini | décoder `reqN___data__` en base64, puis textes lisibles |
| `corps_entier` | sites non capturés | secours : tout le corps |

**Méthode de secours qui marche partout :** décoder ce qui est encodé, extraire tous les morceaux de texte lisibles, puis appeler `detect()` dessus.

## Reste à faire

- Capturer ChatGPT **connecté** (sans doute `/backend-api/…` en JSON).
- Capturer Copilot **connecté** : le vrai chat passe probablement par un WebSocket (filtre `~websocket` ; dans l'addon, hook `websocket_message` au lieu de `request`).
- Vérifier l'envoi pendant la frappe sur Gemini.
- Sites de priorité 2 et 3 : chemins à trouver.

## Points d'attention

- **Requêtes vs réponses** : utiliser `~bq` (et non `~b`) dans mitmweb pour ne chercher que dans les requêtes. Par exemple, `StreamTimeline` de Claude contient le texte dans la réponse, ce qui n'est pas une fuite.
- **Fichiers joints** : Mistral les met dans `messageFiles[]`. Sur les autres sites, ils partent dans des requêtes d'upload séparées. Hors périmètre pour l'instant, à noter comme limite.
- **Certificate pinning** : les applis de bureau et mobiles refusent le certificat mitmproxy. On teste uniquement dans le **navigateur**.
- **Sous-domaines** : comparer `host == d or host.endswith("." + d)`, car `endswith("claude.ai")` accepterait aussi `faux-claude.ai`.
