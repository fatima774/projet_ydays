# proxy/

Le proxy (mitmproxy) intercepte le trafic des PC de test vers les sites d'IA et, plus tard, vers les registres de paquets (PyPI, npm).

- `cybersentinel.py` : addon du module M1. Il reconnaît les 5 IA (ChatGPT, Gemini, Claude, Le Chat, Copilot), extrait le prompt selon le format de chaque site, appelle `detect()` et écrit un événement par donnée sensible dans `logs/evenements.jsonl` (format de `docs/format-evenement.md`). Les données sont masquées avant tout affichage ou écriture.

## Lancer

Depuis la racine du dépôt, avec Firefox réglé sur le proxy `127.0.0.1:8080` (voir `docs/proxy-installation-windows.md`) :

```
mitmweb --set http2=false -s proxy/cybersentinel.py
```

Pour bloquer vraiment les requêtes dont l'action est « bloquer » (réponse 403) :

```
mitmweb --set http2=false -s proxy/cybersentinel.py --set cs_bloquer=true
```

## Documents liés

- `docs/captures-sites-ia.md` : où passe le prompt sur chaque site.
- `rules/sites_ia.yaml` : liste des sites surveillés et méthode d'extraction.
- `docs/detect.md` : interface de `detect()`.

**Responsables :** Arno (proxy, captures), Nolan (branchement de la détection).

**À venir :** lire la liste des sites dans `rules/sites_ia.yaml`, envoyer chaque événement à l'API (`POST /events`), contrôler les `pip install` / `npm install` (module 2).
