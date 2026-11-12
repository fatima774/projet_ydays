import { useCallback, useEffect, useRef, useState } from 'react'
import { recupererAlertes } from '../api'
import './ListeAlertes.css'

// Toutes les combien de millisecondes on redemande les alertes à l'API
const INTERVALLE_MS = 10000

// Textes affichés à l'écran
const LIBELLES_ACTION = {
  bloquer: 'Bloqué',
  masquer: 'Masqué',
  alerter: 'Alerté',
}
const LIBELLES_STATUT = {
  nouveau: 'Nouveau',
  en_cours: 'En cours',
  traite: 'Traité',
  faux_positif: 'Faux positif',
}

// Transforme "2026-11-12T10:42:07.000Z" en "12/11 10:42" (heure UTC)
function formaterDate(iso) {
  const d = new Date(iso)
  const jour = String(d.getUTCDate()).padStart(2, '0')
  const mois = String(d.getUTCMonth() + 1).padStart(2, '0')
  const heure = String(d.getUTCHours()).padStart(2, '0')
  const minute = String(d.getUTCMinutes()).padStart(2, '0')
  return `${jour}/${mois} ${heure}:${minute}`
}

function formaterHeure(date) {
  return date.toLocaleTimeString('fr-FR')
}

function ListeAlertes() {
  // Les alertes reçues de l'API
  const [alertes, setAlertes] = useState([])
  const [total, setTotal] = useState(0)
  // État de la connexion à l'API
  const [chargee, setChargee] = useState(false)
  const [erreur, setErreur] = useState(null)
  const [derniereMaj, setDerniereMaj] = useState(null)
  // Nombre d'alertes arrivées depuis la dernière actualisation
  const [nouvelles, setNouvelles] = useState(0)
  // Filtres choisis par l'utilisateur
  const [action, setAction] = useState('')
  const [recherche, setRecherche] = useState('')

  // Les identifiants déjà affichés, pour repérer les nouvelles alertes
  const idsConnus = useRef(null)

  // Demande les alertes à l'API et met l'écran à jour
  const charger = useCallback(async () => {
    try {
      const resultat = await recupererAlertes({ action })
      const ids = new Set(resultat.alertes.map((a) => a.id))
      if (idsConnus.current) {
        const arrivees = [...ids].filter((id) => !idsConnus.current.has(id))
        setNouvelles(arrivees.length)
      }
      idsConnus.current = ids
      setAlertes(resultat.alertes)
      setTotal(resultat.total)
      setErreur(null)
    } catch {
      setErreur("Impossible de joindre l'API. Elle est peut-être arrêtée (docker compose up).")
    } finally {
      setChargee(true)
      setDerniereMaj(new Date())
    }
  }, [action])

  // Au chargement, puis toutes les 10 secondes : on redemande les alertes.
  // Quand l'onglet est caché, on arrête pour ne pas charger l'API pour rien.
  useEffect(() => {
    idsConnus.current = null // nouveau filtre : on ne compte pas de « nouvelles »
    charger()
    const minuteur = setInterval(() => {
      if (document.visibilityState === 'visible') charger()
    }, INTERVALLE_MS)
    return () => clearInterval(minuteur)
  }, [charger])

  // La recherche se fait dans le navigateur, sur les alertes déjà reçues
  const texte = recherche.trim().toLowerCase()
  const alertesAffichees = alertes.filter(
    (a) =>
      texte === '' ||
      `${a.source.poste} ${a.site_ia} ${a.type_donnee}`.toLowerCase().includes(texte),
  )

  return (
    <section className="liste">
      <div className="liste-entete">
        <div>
          <h1>Alertes</h1>
          <p className="discret">
            Requêtes où une donnée sensible ou un paquet suspect a été détecté
          </p>
        </div>
        <div className="actualisation">
          <span className="discret" aria-live="polite">
            {derniereMaj
              ? `Mis à jour à ${formaterHeure(derniereMaj)} · toutes les ${INTERVALLE_MS / 1000} s`
              : 'Chargement…'}
          </span>
          <button type="button" className="bouton" onClick={charger}>
            Actualiser
          </button>
        </div>
      </div>

      {erreur && (
        <p className="message message-erreur" role="alert">
          {erreur}
        </p>
      )}
      {nouvelles > 0 && (
        <p className="message message-info" role="status">
          {nouvelles === 1 ? '1 nouvelle alerte' : `${nouvelles} nouvelles alertes`}
        </p>
      )}

      <div className="filtres">
        <div className="champ champ-large">
          <label htmlFor="recherche">Rechercher</label>
          <input
            id="recherche"
            type="search"
            placeholder="Poste, site, type de donnée…"
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
          />
        </div>
        <div className="champ">
          <label htmlFor="action">Décision</label>
          <select id="action" value={action} onChange={(e) => setAction(e.target.value)}>
            <option value="">Toutes</option>
            <option value="bloquer">Bloqué</option>
            <option value="masquer">Masqué</option>
            <option value="alerter">Alerté</option>
          </select>
        </div>
      </div>

      <div className="tableau-cadre">
        <table>
          <thead>
            <tr>
              <th>Date (UTC)</th>
              <th>Poste</th>
              <th>Site</th>
              <th>Donnée</th>
              <th>Règle</th>
              <th>Score</th>
              <th>Décision</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            {alertesAffichees.map((a) => (
              <tr key={a.id}>
                <td className="mono">{formaterDate(a.date)}</td>
                <td className="nowrap">{a.source.poste}</td>
                <td>{a.site_ia}</td>
                <td>
                  <div>{a.type_donnee}</div>
                  <div className="extrait">{a.extrait_masque}</div>
                </td>
                <td className="mono">{a.regle}</td>
                <td className="mono">{a.score.toFixed(2).replace('.', ',')}</td>
                <td>
                  <span className={`badge badge-${a.action}`}>{LIBELLES_ACTION[a.action]}</span>
                </td>
                <td className="nowrap">{LIBELLES_STATUT[a.statut] ?? a.statut}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {chargee && !erreur && alertesAffichees.length === 0 && (
          <p className="vide">Aucune alerte pour le moment.</p>
        )}
      </div>

      <p className="discret">
        {alertesAffichees.length} alerte(s) affichée(s) sur {total}
      </p>
    </section>
  )
}

export default ListeAlertes
