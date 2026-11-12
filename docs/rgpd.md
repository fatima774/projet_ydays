# CyberSentinel · Note RGPD

**Responsable :** Aloïs · **Relecture :** Kiliann (cadre d'utilisation, `docs/README.md`)

CyberSentinel lit le contenu des messages envoyés aux IA pour y chercher des données personnelles. C'est un traitement de données personnelles au sens du RGPD. Cette page fixe ce qu'on s'autorise **pendant le projet** et ce qu'il faudrait prévoir **si l'outil était déployé en entreprise**.

## 1. Pendant le projet Ydays

### Périmètre

- Le proxy tourne **uniquement sur des PC ou VM de test** appartenant à l'équipe.
- Seuls les membres de l'équipe envoient du trafic dans le proxy, en connaissance de cause.
- **Aucune vraie donnée** : IBAN, cartes, n° de sécu, clés… sont inventés ou sont des numéros de test publics (ex. carte `4111 1111 1111 1111`, clé AWS d'exemple de la documentation AWS). Les exemples de `rules/m1.yaml` et de `data/` respectent cette règle.

### Ce qui est stocké

| Donnée | Stockée ? | Comment |
| --- | --- | --- |
| Prompt complet | **Non** | Analysé en mémoire par le proxy, jamais écrit sur disque ni envoyé à l'API |
| Donnée sensible trouvée (l'IBAN, la clé…) | **Non en clair** | Seulement un extrait masqué (`FR76 **** … 189`) produit par `detect()` |
| Événement (date, site d'IA, règle, type de donnée, score, action, extrait masqué) | Oui | Base PostgreSQL de test |
| Identité de l'utilisateur | Pseudonymisée | Identifiant du poste de test (ex. `pc-test-01`), pas de nom |
| Logs mitmproxy (`mitmweb`, fichiers `.flow`) | Non conservés | Les captures pour la doc sont faites avec de fausses données, puis supprimées |

> Règle pour le code : **aucun `print()` ni log du prompt en clair** dans la version finale. Le prototype `proxy/addon.py` affiche encore la valeur trouvée : à remplacer par `extrait_masque` quand `detect()` sera branché.

### Durée de conservation

- Événements en base de test : **30 jours**, puis suppression automatique (tâche planifiée ou `DELETE … WHERE date < now() - interval '30 days'`).
- Fin du projet : base, captures et certificats **supprimés** ; seul le jeu de prompts inventés (`data/prompts_v1.csv`) est gardé.

## 2. Si CyberSentinel était déployé en entreprise

Ce qui serait obligatoire, à présenter dans le dossier comme « limites et conditions de déploiement » :

1. **Base légale** : intérêt légitime de l'employeur (protéger ses données et celles de ses clients). Pas de consentement : il n'est pas libre dans une relation de travail.
2. **Information des salariés** : charte informatique mise à jour, information individuelle avant la mise en service (Code du travail, art. L1222-4).
3. **Consultation du CSE** avant la mise en place d'un outil de contrôle de l'activité (art. L2312-38).
4. **Proportionnalité** : on n'analyse que le trafic vers les sites d'IA (`rules/sites_ia.yaml`), pas toute la navigation. Pas de capture d'écran, pas de frappe clavier.
5. **Minimisation** : on stocke l'événement et l'extrait masqué, jamais le prompt. Pour le NIR (donnée de santé), l'extrait masqué ne garde que le premier chiffre.
6. **AIPD** (analyse d'impact) recommandée : surveillance systématique de salariés + interception de flux chiffrés, ce qui correspond aux critères de la CNIL.
7. **Registre des traitements** : inscription du traitement par le DPO.
8. **Accès restreints** : seules l'équipe sécurité et le DPO voient le tableau de bord ; journal des consultations.
9. **Droits des personnes** : accès, rectification, opposition, via le DPO.
10. **Exceptions** : exclure les flux personnels identifiés (messagerie perso, banque, santé) de toute interception TLS.

## 3. Liens avec le reste du projet

- Format d'événement (Yarkin, Elias) : le champ `extrait_masque` remplace toute valeur en clair.
- `detect()` (`rules/m1_detect.py`) ne renvoie jamais la valeur trouvée, seulement sa position et son extrait masqué.
- Le tableau de bord (Fati) n'affiche que l'extrait masqué.

## Sources

- CNIL, *Les outils de surveillance des salariés* et *Cybersécurité : le filtrage des flux chiffrés (TLS)*.
- RGPD, art. 5 (minimisation, limitation de conservation), art. 9 (données de santé), art. 35 (AIPD).
