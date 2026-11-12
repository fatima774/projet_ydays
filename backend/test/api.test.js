// Tests des routes avec une fausse base en mémoire (pas besoin de MySQL).
// Lancer : npm test
import assert from 'node:assert/strict'
import { after, before, beforeEach, describe, it } from 'node:test'
import { creerApp } from '../src/app.js'

function fausseBase() {
  let lignes = []
  return {
    vider() {
      lignes = []
    },
    async verifier() {},
    async ajouterEvenements(evenements) {
      for (const e of evenements) {
        if (lignes.some((l) => l.id === e.id)) {
          const erreur = new Error('doublon')
          erreur.code = 'ER_DUP_ENTRY'
          throw erreur
        }
      }
      for (const e of evenements) lignes.push({ ...e, statut: 'nouveau', commentaire: null })
    },
    async listerAlertes(filtres, limite, decalage) {
      const alertes = lignes
        .filter((l) => l.action !== 'laisser')
        .filter((l) => !filtres.action || l.action === filtres.action)
        .filter((l) => !filtres.statut || l.statut === filtres.statut)
        .sort((a, b) => b.date.localeCompare(a.date))
      return { total: alertes.length, alertes: alertes.slice(decalage, decalage + limite) }
    },
    async trouverAlerte(id) {
      return lignes.find((l) => l.id === id) ?? null
    },
    async modifierAlerte(id, { statut, commentaire }) {
      const ligne = lignes.find((l) => l.id === id)
      if (!ligne) return null
      if (statut !== undefined) ligne.statut = statut
      if (commentaire !== undefined) ligne.commentaire = commentaire
      return ligne
    },
  }
}

function evenement(changements = {}) {
  return {
    id: '6f1c2b0e-8a4d-4c1e-9f3a-2d7b5e0c9a11',
    date: '2026-11-12T10:42:07Z',
    source: { poste: 'pc-test-01', module: 'M1' },
    site_ia: 'chatgpt.com',
    type_donnee: 'IBAN',
    regle: 'm1.iban',
    detecteur: 'regle',
    score: 1.0,
    etiquette: 'finance',
    explication: 'IBAN français valide détecté dans le prompt.',
    action: 'bloquer',
    extrait_masque: '…sur FR76 **** **** **** **** **** 189 avant…',
    version_modele: null,
    latence_ms: 4,
    ...changements,
  }
}

const base = fausseBase()
let serveur
let url

before(async () => {
  serveur = creerApp(base).listen(0)
  await new Promise((ok) => serveur.once('listening', ok))
  url = `http://localhost:${serveur.address().port}`
})
after(() => serveur.close())
beforeEach(() => base.vider())

async function appel(methode, chemin, corps) {
  const reponse = await fetch(url + chemin, {
    method: methode,
    headers: { 'Content-Type': 'application/json' },
    body: corps === undefined ? undefined : JSON.stringify(corps),
  })
  return { statut: reponse.status, json: await reponse.json() }
}

describe('POST /events', () => {
  it('enregistre un événement valide', async () => {
    const r = await appel('POST', '/events', evenement())
    assert.equal(r.statut, 201)
    assert.equal(r.json.enregistres, 1)
  })

  it('accepte une liste d’événements', async () => {
    const r = await appel('POST', '/events', [
      evenement(),
      evenement({ id: '7a1c2b0e-8a4d-4c1e-9f3a-2d7b5e0c9a12', action: 'masquer' }),
    ])
    assert.equal(r.statut, 201)
    assert.equal(r.json.enregistres, 2)
  })

  it('refuse un événement incomplet et dit pourquoi', async () => {
    const r = await appel('POST', '/events', evenement({ score: 3, action: 'supprimer' }))
    assert.equal(r.statut, 400)
    assert.ok(r.json.details.some((d) => d.startsWith('score')))
    assert.ok(r.json.details.some((d) => d.startsWith('action')))
  })

  it("exige l'étiquette pour M1 mais pas pour M2", async () => {
    const m1 = await appel('POST', '/events', evenement({ etiquette: undefined }))
    assert.equal(m1.statut, 400)
    const m2 = await appel(
      'POST',
      '/events',
      evenement({ etiquette: undefined, source: { poste: 'pc-test-02', module: 'M2' } }),
    )
    assert.equal(m2.statut, 201)
  })

  it('refuse un extrait trop long', async () => {
    const r = await appel('POST', '/events', evenement({ extrait_masque: 'x'.repeat(201) }))
    assert.equal(r.statut, 400)
  })

  it('refuse un id déjà enregistré', async () => {
    await appel('POST', '/events', evenement())
    const r = await appel('POST', '/events', evenement())
    assert.equal(r.statut, 409)
  })

  it('répond 400 à un JSON cassé', async () => {
    const reponse = await fetch(url + '/events', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: '{pas du json',
    })
    assert.equal(reponse.status, 400)
  })
})

describe('GET /alerts', () => {
  it("renvoie les alertes, sans les événements « laisser »", async () => {
    await appel('POST', '/events', [
      evenement(),
      evenement({ id: '7a1c2b0e-8a4d-4c1e-9f3a-2d7b5e0c9a12', action: 'laisser' }),
    ])
    const r = await appel('GET', '/alerts')
    assert.equal(r.statut, 200)
    assert.equal(r.json.total, 1)
    assert.equal(r.json.alertes[0].type_donnee, 'IBAN')
  })

  it('filtre par action', async () => {
    await appel('POST', '/events', [
      evenement(),
      evenement({ id: '7a1c2b0e-8a4d-4c1e-9f3a-2d7b5e0c9a12', action: 'masquer' }),
    ])
    const r = await appel('GET', '/alerts?action=masquer')
    assert.equal(r.json.total, 1)
    assert.equal(r.json.alertes[0].action, 'masquer')
  })

  it('refuse un filtre inconnu', async () => {
    const r = await appel('GET', '/alerts?statut=perdu')
    assert.equal(r.statut, 400)
  })
})

describe('GET et PATCH /alerts/:id', () => {
  it("renvoie le détail d'une alerte", async () => {
    await appel('POST', '/events', evenement())
    const r = await appel('GET', '/alerts/6f1c2b0e-8a4d-4c1e-9f3a-2d7b5e0c9a11')
    assert.equal(r.statut, 200)
    assert.equal(r.json.regle, 'm1.iban')
  })

  it('répond 404 pour une alerte inconnue', async () => {
    const r = await appel('GET', '/alerts/00000000-0000-0000-0000-000000000000')
    assert.equal(r.statut, 404)
  })

  it('change le statut et ajoute un commentaire', async () => {
    await appel('POST', '/events', evenement())
    const r = await appel('PATCH', '/alerts/6f1c2b0e-8a4d-4c1e-9f3a-2d7b5e0c9a11', {
      statut: 'traite',
      commentaire: 'Utilisateur prévenu',
    })
    assert.equal(r.statut, 200)
    assert.equal(r.json.statut, 'traite')
    assert.equal(r.json.commentaire, 'Utilisateur prévenu')
  })

  it('refuse un statut inconnu', async () => {
    await appel('POST', '/events', evenement())
    const r = await appel('PATCH', '/alerts/6f1c2b0e-8a4d-4c1e-9f3a-2d7b5e0c9a11', {
      statut: 'perdu',
    })
    assert.equal(r.statut, 400)
  })
})
