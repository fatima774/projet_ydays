FROM node:22-alpine

WORKDIR /app

# Installer les dépendances d'abord (mis en cache tant que package.json ne change pas)
COPY package*.json ./
RUN npm install --omit=dev

COPY src ./src
COPY scripts ./scripts

ENV NODE_ENV=production
EXPOSE 3000

# Ne pas lancer l'API en root
USER node
CMD ["node", "src/server.js"]
