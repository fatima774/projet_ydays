-- Base CyberSentinel : créée automatiquement au premier `docker compose up`.
-- Une ligne = un événement = une décision du proxy sur une donnée détectée
-- (voir docs/format-evenement.md et docs/api.md).

CREATE TABLE IF NOT EXISTS evenements (
  id              CHAR(36)      NOT NULL,
  requete_id      CHAR(36)      NULL,
  date_detection  DATETIME(3)   NOT NULL,
  poste           VARCHAR(64)   NOT NULL,
  module          ENUM('M1', 'M2', 'M3') NOT NULL,
  site_ia         VARCHAR(255)  NOT NULL,
  type_donnee     VARCHAR(64)   NOT NULL,
  regle           VARCHAR(128)  NOT NULL,
  detecteur       ENUM('regle', 'modele', 'les_deux') NOT NULL,
  score           DECIMAL(4, 3) NOT NULL,
  etiquette       ENUM('non_sensible', 'identite', 'finance', 'sante',
                       'secret_technique', 'donnees_clients') NULL,
  explication     VARCHAR(500)  NOT NULL,
  action          ENUM('bloquer', 'masquer', 'alerter', 'laisser') NOT NULL,
  extrait_masque  VARCHAR(200)  NOT NULL,
  version_modele  VARCHAR(64)   NULL,
  latence_ms      INT UNSIGNED  NULL,

  -- Champs ajoutés par l'API pour le suivi des alertes dans le tableau de bord
  statut          ENUM('nouveau', 'en_cours', 'traite', 'faux_positif')
                  NOT NULL DEFAULT 'nouveau',
  commentaire     TEXT          NULL,
  recu_le         DATETIME(3)   NOT NULL DEFAULT CURRENT_TIMESTAMP(3),

  PRIMARY KEY (id),
  INDEX idx_date (date_detection),
  INDEX idx_action (action),
  INDEX idx_requete (requete_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
