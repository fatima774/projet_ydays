// Point d'entrée : connecte la base puis démarre l'API.
import { creerApp } from './app.js'
import { creerBase } from './db.js'

const base = creerBase({
  host: process.env.DB_HOST ?? 'localhost',
  port: Number(process.env.DB_PORT ?? 3306),
  user: process.env.DB_USER ?? 'cybersentinel',
  password: process.env.DB_PASSWORD ?? 'cybersentinel',
  database: process.env.DB_NAME ?? 'cybersentinel',
})

const app = creerApp(base, {
  origineFront: process.env.FRONT_ORIGIN ?? 'http://localhost:5173',
})

const port = Number(process.env.PORT ?? 3000)
app.listen(port, () => {
  console.log(`API CyberSentinel sur http://localhost:${port}`)
})
