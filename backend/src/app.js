// Les routes de l'API. La base est passée en paramètre, ce qui permet
// de tester les routes avec une fausse base (voir test/api.test.js).
import cors from 'cors'
import express from 'express'
import {
  ACTIONS,
  MODULES,
  STATUTS,
  validerEvenement,
} from './validation.js'

const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i

export function creerApp(base, { origineFront = 'http://localhost:5173' } = {}) {
  const app = express()
  app.use(cors({ origin: origineFront })) // autorise le tableau de bord React
  app.use(express.json({ limit: '100kb' }))

  // L'API et la base répondent-elles ?
  app.get('/health', async (req, res) => {
    try {
      await base.verifier()
      res.json({ statut: 'ok', base: 'ok' })
    } catch {
      res.status(503).json({ statut: 'erreur', base: 'injoignable' })
    }
  })

  // Le proxy envoie un événement, ou une liste d'événements (un par donnée détectée)
  app.post('/events', async (req, res) => {
    const evenements = Array.isArray(req.body) ? req.body : [req.body]
    if (evenements.length === 0 || evenements.length > 50) {
      return res.status(400).json({ erreur: 'Envoyer entre 1 et 50 événements' })
    }

    const erreurs = []
    evenements.forEach((e, i) => {
      for (const message of validerEvenement(e)) {
        erreurs.push(evenements.length > 1 ? `[${i}] ${message}` : message)
      }
    })
    if (erreurs.length) {
      return res.status(400).json({ erreur: 'Événement invalide', details: erreurs })
    }

    try {
      await base.ajouterEvenements(evenements)
    } catch (erreur) {
      if (erreur.code === 'ER_DUP_ENTRY') {
        return res.status(409).json({ erreur: 'Un événement avec cet id existe déjà' })
      }
      throw erreur
    }
    res.status(201).json({ enregistres: evenements.length, ids: evenements.map((e) => e.id) })
  })

  // Le tableau de bord récupère les alertes, avec filtres et pagination
  app.get('/alerts', async (req, res) => {
    const { action, type_donnee, site_ia, module, statut, depuis } = req.query
    const limite = Math.min(Math.max(parseInt(req.query.limite ?? '50', 10) || 50, 1), 200)
    const decalage = Math.max(parseInt(req.query.decalage ?? '0', 10) || 0, 0)

    if (action && !ACTIONS.includes(action)) {
      return res.status(400).json({ erreur: `action : une valeur parmi ${ACTIONS.join(', ')}` })
    }
    if (module && !MODULES.includes(module)) {
      return res.status(400).json({ erreur: `module : une valeur parmi ${MODULES.join(', ')}` })
    }
    if (statut && !STATUTS.includes(statut)) {
      return res.status(400).json({ erreur: `statut : une valeur parmi ${STATUTS.join(', ')}` })
    }
    if (depuis && Number.isNaN(Date.parse(depuis))) {
      return res.status(400).json({ erreur: 'depuis : date ISO 8601 attendue' })
    }

    const resultat = await base.listerAlertes(
      { action, type_donnee, site_ia, module, statut, depuis },
      limite,
      decalage,
    )
    res.json({ ...resultat, limite, decalage })
  })

  // Le détail d'une alerte
  app.get('/alerts/:id', async (req, res) => {
    if (!UUID.test(req.params.id)) return res.status(404).json({ erreur: 'Alerte introuvable' })
    const alerte = await base.trouverAlerte(req.params.id)
    if (!alerte) return res.status(404).json({ erreur: 'Alerte introuvable' })
    res.json(alerte)
  })

  // L'analyste change le statut ou ajoute un commentaire
  app.patch('/alerts/:id', async (req, res) => {
    if (!UUID.test(req.params.id)) return res.status(404).json({ erreur: 'Alerte introuvable' })
    const { statut, commentaire } = req.body ?? {}
    if (statut === undefined && commentaire === undefined) {
      return res.status(400).json({ erreur: 'Envoyer un statut et/ou un commentaire' })
    }
    if (statut !== undefined && !STATUTS.includes(statut)) {
      return res.status(400).json({ erreur: `statut : une valeur parmi ${STATUTS.join(', ')}` })
    }
    if (
      commentaire !== undefined &&
      commentaire !== null &&
      (typeof commentaire !== 'string' || commentaire.length > 2000)
    ) {
      return res.status(400).json({ erreur: 'commentaire : texte de 2000 caractères maximum' })
    }

    const alerte = await base.modifierAlerte(req.params.id, { statut, commentaire })
    if (!alerte) return res.status(404).json({ erreur: 'Alerte introuvable' })
    res.json(alerte)
  })

  // Route inconnue
  app.use((req, res) => {
    res.status(404).json({ erreur: 'Route inconnue' })
  })

  // Erreur inattendue : on la note dans la console, sans détails pour le client
  // eslint-disable-next-line no-unused-vars
  app.use((erreur, req, res, next) => {
    if (erreur.type === 'entity.parse.failed') {
      return res.status(400).json({ erreur: 'JSON invalide' })
    }
    if (erreur.type === 'entity.too.large') {
      return res.status(413).json({ erreur: 'Requête trop volumineuse' })
    }
    console.error(erreur)
    res.status(500).json({ erreur: 'Erreur interne' })
  })

  return app
}
