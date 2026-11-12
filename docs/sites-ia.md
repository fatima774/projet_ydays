# Sites d'IA à couvrir

Le proxy n'analyse que le trafic vers les sites d'IA. La liste utilisée par le code est `rules/sites_ia.yaml`. Cette page explique les choix.

**Responsable :** Aloïs · **Validation des chemins :** Arno (captures mitmproxy)

## Priorités

| Priorité | Sites | Pourquoi |
| --- | --- | --- |
| 1 · démo | ChatGPT, Gemini, Claude, Le Chat (Mistral), Copilot | Les plus utilisés en entreprise en France ; demandés dans le sujet |
| 2 | DeepSeek, Perplexity, API OpenAI / Anthropic / Gemini / Mistral | Usage croissant ; les API sont appelées par les scripts et les extensions des développeurs |
| 3 | Grok, Meta AI, Poe, HuggingChat, GitHub Copilot | Moins courants en entreprise, à ajouter si on a le temps |

## Ce qu'il faut trouver pour chaque site

Pour brancher un site, il faut trois infos, toutes visibles dans mitmproxy (`mitmweb`) en envoyant un prompt de test :

1. **Le domaine** qui reçoit le prompt (ex. `chatgpt.com`).
2. **Le chemin** de la requête POST (ex. `/backend-api/conversation`).
3. **Où est le texte** dans le corps : champ JSON, formulaire, ou WebSocket.

| Site | Domaine | Chemin connu | Format | Statut |
| --- | --- | --- | --- | --- |
| ChatGPT | chatgpt.com | `/backend-api/conversation` (ou `/backend-api/f/conversation`) | JSON, texte dans `messages[].content.parts[]` | à confirmer (Arno) |
| Gemini | gemini.google.com | `/_/BardChatUi/data/…StreamGenerate` | formulaire, paramètre `f.req` (JSON dans une chaîne) | à confirmer |
| Claude | claude.ai | `/api/organizations/<org>/chat_conversations/<id>/completion` | JSON, champ `prompt` | à confirmer |
| Le Chat | chat.mistral.ai | ? | JSON | à trouver |
| Copilot | copilot.microsoft.com | ? | probablement WebSocket | à trouver |

Les chemins internes des interfaces web ne sont pas documentés et changent régulièrement : **c'est la capture qui fait foi**. Les API (api.openai.com, etc.) sont documentées publiquement et stables.

## Points d'attention

- **Analyser tout le corps** : tant que le champ exact n'est pas confirmé, le plus sûr est de passer le corps entier dans `detect()`. On perd un peu en précision (métadonnées JSON), mais on ne rate pas de prompt.
- **WebSocket (Copilot)** : mitmproxy les intercepte avec le hook `websocket_message`, pas `request`. Il faudra un bout de code à part dans l'addon.
- **Fichiers joints** : les fichiers déposés dans ChatGPT/Claude partent dans des requêtes d'upload séparées (souvent vers d'autres domaines, du stockage cloud). Hors périmètre pour l'instant, à noter comme limite dans le dossier.
- **Certificate pinning** : les applis de bureau et mobiles de certaines IA refusent le certificat mitmproxy. On teste uniquement dans le **navigateur**.
- **Sous-domaines** : un hôte correspond s'il se termine par `.<domaine>` (attention : `endswith("claude.ai")` accepterait aussi `faux-claude.ai`, il faut comparer `host == d or host.endswith("." + d)`).
