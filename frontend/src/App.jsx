import ListeAlertes from './components/ListeAlertes'
import './App.css'

function App() {
  return (
    <>
      <header className="barre">
        <span className="logo">
          <svg
            width="20"
            height="22"
            viewBox="0 0 20 22"
            fill="none"
            stroke="#2EE6D6"
            strokeWidth="1.8"
            strokeLinejoin="round"
            aria-hidden="true"
          >
            <path d="M10 1.5 18 4.5V10c0 5-3.4 8.6-8 10.5C5.4 18.6 2 15 2 10V4.5z" />
            <circle cx="10" cy="10.5" r="2.2" fill="#2EE6D6" stroke="none" />
          </svg>
          CyberSentinel
        </span>
        <nav aria-label="Navigation principale">
          <a href="#" aria-current="page">Alertes</a>
        </nav>
      </header>

      <main className="contenu">
        <ListeAlertes />
      </main>
    </>
  )
}

export default App
