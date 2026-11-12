# proxy/

Le proxy intercepte le trafic des PC de test vers les sites d'IA et les registres de paquets (PyPI, npm).

- `cybersentinel.py` : addon mitmproxy du module M1. Il reconnaît les 5 IA, extrait le prompt, appelle `detect()` et écrit un événement JSON par donnée trouvée dans `logs/evenements.jsonl`. Lancer : `mitmweb --set http2=false -s proxy/cybersentinel.py` (ajouter `--set cs_bloquer=true` pour bloquer vraiment).

**Responsables :** Arno (installation, certificat), Nolan (branchement des règles et du modèle).

**À venir :** masquer la requête, envoyer chaque décision à l'API, contrôler les `pip install` / `npm install` (module 2).
