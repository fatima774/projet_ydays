# backend/

API FastAPI et base PostgreSQL : reçoit les événements du proxy, les enregistre et les fournit au tableau de bord.

Premières routes prévues :

| Route | Rôle |
| --- | --- |
| `POST /events` | Le proxy envoie un événement (site, type de donnée, décision) |
| `GET /events` | Le tableau de bord récupère la liste des événements |
| `GET /stats` | Chiffres du tableau de bord (fuites bloquées, masquées…) |
| `GET/PUT /settings` | Réglages : bloquer, masquer ou alerter par type de donnée |

**Responsables :** Fati, Yarkin.
