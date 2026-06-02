# GT7 League Hub

Site web complet et déployable pour un championnat GT7.

## Installation locale

```bash
npm install
npm run dev
```

Puis ouvre l'adresse affichée par Vite, généralement `http://localhost:5173`.

## Build production

```bash
npm run build
```

Le site final est généré dans le dossier `dist/`.

## Déploiement

### Netlify / Vercel
- Build command : `npm run build`
- Publish directory : `dist`

### Hébergement statique simple
Tu peux aussi envoyer directement le contenu du dossier `dist/` sur ton hébergeur.

## Note npm

Le projet contient un fichier `.npmrc` qui force le registre public officiel :

```bash
registry=https://registry.npmjs.org/
```

Si npm tente encore d'utiliser un registre privé, lance :

```bash
npm config set registry https://registry.npmjs.org/
npm cache clean --force
```
