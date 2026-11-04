# proxy/

Le proxy intercepte le trafic des PC de test vers les sites d'IA et les registres de paquets (PyPI, npm).

- `addon.py` : premier prototype qui repère les données sensibles dans les messages envoyés aux IA.

**Responsables :** Arno (installation, certificat), Nolan (branchement des règles et du modèle).

**À venir :** bloquer ou masquer la requête, envoyer chaque décision à l'API, contrôler les `pip install` / `npm install` (module 2).
