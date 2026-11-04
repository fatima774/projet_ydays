# projet_ydays
# CyberSentinel

**Protéger l'entreprise contre les fuites de données vers les IA.**

Projet Ydays · Bachelor 3 · Ynov Bordeaux · 2026–2027

---

## Le projet en bref

Les salariés collent tous les jours des données dans ChatGPT, Gemini ou Copilot : des IBAN, des données clients, des clés d'accès. Une fois envoyées, ces données sortent de l'entreprise.

CyberSentinel se place entre les postes de travail et Internet. Il lit ce qui part vers les sites d'IA, repère les données sensibles grâce à des règles et à un modèle de machine learning, puis **bloque**, **masque** ou **laisse passer**. Chaque décision s'affiche dans un tableau de bord, avec une explication.

## Les modules

| Module | Ce qu'il fait | Statut |
| --- | --- | --- |
| Socle | Proxy, réception des événements, base PostgreSQL, tableau de bord | Obligatoire |
| 1. Fuites vers les IA | Repère les données sensibles dans les prompts (IBAN, n° de sécu, clés API, données clients) et les bloque ou les masque | Obligatoire · démo phare |
| 2. Paquets inventés par les IA | Vérifie chaque `pip install` / `npm install` : paquet récent, peu téléchargé, nom proche d'un paquet connu | Obligatoire |
| 3. Surveillance des agents IA | Surveille les outils appelés par un agent IA (fichiers, mails, web) pour repérer une exfiltration | Bonus |
| 4. Alertes expliquées | Une IA traduit chaque alerte en français simple, avec quoi faire | Bonus |

Règle : les bonus ne démarrent que si les modules 1 et 2 fonctionnent vers la séance 7.

## Architecture

```
PC de test ──► Proxy (mitmproxy) ──► Internet (ChatGPT, Gemini, PyPI, npm…)
                    │
                    │  règles + modèle ML → bloquer / masquer / laisser passer
                    ▼
               API (FastAPI) ──► Base PostgreSQL
                    │
                    ▼
          Tableau de bord (React)
```

## Structure du dépôt

| Dossier | Contenu | Responsables |
| --- | --- | --- |
| `proxy/` | Addon mitmproxy qui intercepte et analyse le trafic | Cyber + Nolan |
| `rules/` | Règles de détection (expressions régulières, listes) | Cyber |
| `data/` | Jeu de prompts étiqueté, notebooks, modèle ML | Data/IA |
| `backend/` | API FastAPI et base de données | Dev |
| `frontend/` | Tableau de bord React | Dev |
| `docs/` | Documentation, RGPD, comptes rendus, Kanban | Tout le monde |

## Équipe

| Membre | Filière |
| --- | --- |
| Elias Perez | Data/IA · porteur de projet |
| Imad Belghazy | Data/IA · co-porteur |
| Nolan | Développement & IA |
| Fati | Développement |
| Yarkin | Développement |
| Arno | Cybersécurité |
| Aloïs | Cybersécurité |
| Kiliann | Cybersécurité |

## Démarrer le proxy (premier prototype)

```bash
pip install mitmproxy
mitmdump -s proxy/addon.py
```

Puis, sur le PC de test :

1. Régler le proxy du navigateur sur `127.0.0.1:8080`.
2. Ouvrir http://mitm.it et installer le certificat mitmproxy.
3. Coller un faux IBAN dans ChatGPT : l'alerte s'affiche dans le terminal.

## Cadre d'utilisation

Le proxy lit le contenu des messages. Il ne tourne **que sur des PC de test**, avec **de fausses données**. Aucun trafic réel d'une personne n'est intercepté. Voir `docs/README.md`.

## Contribuer

Voir [CONTRIBUTING.md](CONTRIBUTING.md).
