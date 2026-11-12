// Envoie 3 faux événements à l'API, pour tester sans le proxy.
// Utilisation : node scripts/envoyer-exemples.js   (l'API doit tourner)
import { randomUUID } from 'node:crypto'

const API = process.env.API_URL ?? 'http://localhost:3000'
const maintenant = new Date().toISOString()
const requete = randomUUID()

const evenements = [
  {
    id: randomUUID(),
    requete_id: requete,
    date: maintenant,
    source: { poste: 'pc-test-01', module: 'M1' },
    site_ia: 'chatgpt.com',
    type_donnee: 'IBAN',
    regle: 'm1.iban',
    detecteur: 'regle',
    score: 1.0,
    etiquette: 'finance',
    explication: 'IBAN français valide (clé de contrôle correcte) détecté dans le prompt.',
    action: 'bloquer',
    extrait_masque: '…virer 1 200 € sur FR76 **** **** **** **** **** 189 avant…',
    version_modele: null,
    latence_ms: 4,
  },
  {
    id: randomUUID(),
    requete_id: requete,
    date: maintenant,
    source: { poste: 'pc-test-01', module: 'M1' },
    site_ia: 'chatgpt.com',
    type_donnee: 'EMAIL',
    regle: 'm1.email',
    detecteur: 'regle',
    score: 1.0,
    etiquette: 'identite',
    explication: 'Adresse e-mail détectée dans le prompt.',
    action: 'masquer',
    extrait_masque: '…envoie la confirmation à j****@e******.fr ce soir…',
    version_modele: null,
    latence_ms: 4,
  },
  {
    id: randomUUID(),
    date: maintenant,
    source: { poste: 'pc-test-02', module: 'M2' },
    site_ia: 'pypi.org',
    type_donnee: 'PAQUET_SUSPECT',
    regle: 'm2.typosquatting',
    detecteur: 'regle',
    score: 0.9,
    explication: 'Nom très proche du paquet connu « requests ».',
    action: 'alerter',
    extrait_masque: 'pip install reqeusts',
    latence_ms: 12,
  },
]

const reponse = await fetch(`${API}/events`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(evenements),
})
console.log(reponse.status, await reponse.json())
