// Accès à la base MySQL. Toutes les requêtes SQL du projet sont ici.
import mysql from 'mysql2/promise'

// Colonnes renvoyées au tableau de bord
const COLONNES = `id, requete_id, date_detection, poste, module, site_ia, type_donnee,
  regle, detecteur, score, etiquette, explication, action, extrait_masque,
  version_modele, latence_ms, statut, commentaire, recu_le`

// Transforme une ligne de la table en événement au format commun
function versEvenement(ligne) {
  return {
    id: ligne.id,
    requete_id: ligne.requete_id,
    date: ligne.date_detection.toISOString(),
    source: { poste: ligne.poste, module: ligne.module },
    site_ia: ligne.site_ia,
    type_donnee: ligne.type_donnee,
    regle: ligne.regle,
    detecteur: ligne.detecteur,
    score: ligne.score,
    etiquette: ligne.etiquette,
    explication: ligne.explication,
    action: ligne.action,
    extrait_masque: ligne.extrait_masque,
    version_modele: ligne.version_modele,
    latence_ms: ligne.latence_ms,
    statut: ligne.statut,
    commentaire: ligne.commentaire,
    recu_le: ligne.recu_le.toISOString(),
  }
}

export function creerBase(config) {
  const pool = mysql.createPool({
    ...config,
    timezone: 'Z', // toutes les dates sont en UTC
    decimalNumbers: true, // le score revient comme un nombre, pas un texte
    waitForConnections: true,
    connectionLimit: 10,
  })

  return {
    async verifier() {
      await pool.query('SELECT 1')
    },

    // Enregistre une liste d'événements. Lève une erreur ER_DUP_ENTRY si un id existe déjà.
    async ajouterEvenements(evenements) {
      const connexion = await pool.getConnection()
      try {
        await connexion.beginTransaction()
        for (const e of evenements) {
          await connexion.execute(
            `INSERT INTO evenements (id, requete_id, date_detection, poste, module,
               site_ia, type_donnee, regle, detecteur, score, etiquette, explication,
               action, extrait_masque, version_modele, latence_ms, recu_le)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
            [
              e.id,
              e.requete_id ?? null,
              new Date(e.date),
              e.source.poste,
              e.source.module,
              e.site_ia,
              e.type_donnee,
              e.regle,
              e.detecteur,
              e.score,
              e.etiquette ?? null,
              e.explication,
              e.action,
              e.extrait_masque,
              e.version_modele ?? null,
              e.latence_ms ?? null,
              new Date(), // date de réception, en UTC comme les autres dates
            ],
          )
        }
        await connexion.commit()
      } catch (erreur) {
        await connexion.rollback()
        throw erreur
      } finally {
        connexion.release()
      }
    },

    // Liste les alertes (tous les événements sauf action = laisser), les plus récentes d'abord
    async listerAlertes(filtres, limite, decalage) {
      const conditions = ["action <> 'laisser'"]
      const valeurs = []
      for (const [champ, colonne] of [
        ['action', 'action'],
        ['type_donnee', 'type_donnee'],
        ['site_ia', 'site_ia'],
        ['module', 'module'],
        ['statut', 'statut'],
      ]) {
        if (filtres[champ]) {
          conditions.push(`${colonne} = ?`)
          valeurs.push(filtres[champ])
        }
      }
      if (filtres.depuis) {
        conditions.push('date_detection >= ?')
        valeurs.push(new Date(filtres.depuis))
      }
      const where = conditions.join(' AND ')

      const [[{ total }]] = await pool.query(
        `SELECT COUNT(*) AS total FROM evenements WHERE ${where}`,
        valeurs,
      )
      const [lignes] = await pool.query(
        `SELECT ${COLONNES} FROM evenements WHERE ${where}
         ORDER BY date_detection DESC LIMIT ? OFFSET ?`,
        [...valeurs, limite, decalage],
      )
      return { total, alertes: lignes.map(versEvenement) }
    },

    async trouverAlerte(id) {
      const [lignes] = await pool.query(
        `SELECT ${COLONNES} FROM evenements WHERE id = ?`,
        [id],
      )
      return lignes.length ? versEvenement(lignes[0]) : null
    },

    // Met à jour le statut et/ou le commentaire. Renvoie l'alerte modifiée, ou null.
    async modifierAlerte(id, { statut, commentaire }) {
      const champs = []
      const valeurs = []
      if (statut !== undefined) {
        champs.push('statut = ?')
        valeurs.push(statut)
      }
      if (commentaire !== undefined) {
        champs.push('commentaire = ?')
        valeurs.push(commentaire)
      }
      const [resultat] = await pool.query(
        `UPDATE evenements SET ${champs.join(', ')} WHERE id = ?`,
        [...valeurs, id],
      )
      if (resultat.affectedRows === 0) return null
      return this.trouverAlerte(id)
    },

    async fermer() {
      await pool.end()
    },
  }
}
