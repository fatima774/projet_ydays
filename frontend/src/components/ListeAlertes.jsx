import { useState } from 'react'
import { alertes } from '../data/alertes'
import './ListeAlertes.css'

// Texte affiché pour chaque action
const LIBELLES = {
  bloquer: 'Bloqué',
  masquer: 'Masqué',
  alerter: 'Alerté',
}

// Transforme "2026-11-03T08:42:00Z" en "03/11 08:42"
function formaterDate(iso) {
  const d = new Date(iso)
  const jour = String(d.getUTCDate()).padStart(2, '0')
  const mois = String(d.getUTCMonth() + 1).padStart(2, '0')
  const heure = String(d.getUTCHours()).padStart(2, '0')
  const minute = String(d.getUTCMinutes()).padStart(2, '0')
  return `${jour}/${mois} ${heure}:${minute}`
}

function ListeAlertes() {
  // Ce que l'utilisateur a choisi dans les filtres
  const [action, setAction] = useState('toutes')
  const [recherche, setRecherche] = useState('')

  // On garde seulement les alertes qui correspondent aux filtres
  const texte = recherche.trim().toLowerCase()
  const alertesFiltrees = alertes.filter((a) => {
    const bonneAction = action === 'toutes' || a.action === action
    const bonTexte =
      texte === '' ||
      `${a.source} ${a.site} ${a.type}`.toLowerCase().includes(texte)
    return bonneAction && bonTexte
  })

  return (
    <section className="liste">
      <div className="liste-entete">
        <div>
          <h1>Alertes</h1>
          <p className="discret">
            Requêtes où une donnée sensible ou un paquet suspect a été détecté
          </p>
        </div>
      </div>

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
          <select
            id="action"
            value={action}
            onChange={(e) => setAction(e.target.value)}
          >
            <option value="toutes">Toutes</option>
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
            {alertesFiltrees.map((a) => (
              <tr key={a.id}>
                <td className="mono">{formaterDate(a.date)}</td>
                <td className="nowrap">{a.source}</td>
                <td>{a.site}</td>
                <td>
                  <div>{a.type}</div>
                  <div className="extrait">{a.extrait}</div>
                </td>
                <td className="mono">{a.regle}</td>
                <td className="mono">{a.score.toFixed(2).replace('.', ',')}</td>
                <td>
                  <span className={`badge badge-${a.action}`}>
                    {LIBELLES[a.action]}
                  </span>
                </td>
                <td className="nowrap">{a.statut}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {alertesFiltrees.length === 0 && (
          <p className="vide">Aucune alerte ne correspond à ces filtres.</p>
        )}
      </div>

      <p className="discret">
        {alertesFiltrees.length} alerte(s) affichée(s) sur {alertes.length}
      </p>
    </section>
  )
}

export default ListeAlertes
