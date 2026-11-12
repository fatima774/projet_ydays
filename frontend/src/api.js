// Appels à l'API CyberSentinel (backend/).
// L'adresse se change dans un fichier frontend/.env : VITE_API_URL=http://...
const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:3000'

// Récupère les alertes. `filtres` : { action, statut, type_donnee, ... }
export async function recupererAlertes(filtres = {}) {
  const params = new URLSearchParams({ limite: '200' })
  for (const [cle, valeur] of Object.entries(filtres)) {
    if (valeur) params.set(cle, valeur)
  }

  const reponse = await fetch(`${API_URL}/alerts?${params}`)
  if (!reponse.ok) {
    throw new Error(`L'API a répondu ${reponse.status}`)
  }
  return reponse.json() // { total, alertes: [...] }
}
