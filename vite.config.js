import { defineConfig } from 'vite'

// Remplace 'gt7' par le nom exact de ton dépôt GitHub
export default defineConfig({
  base: '/gt7/',        // nécessaire pour GitHub Pages
  build: {
    outDir: 'dist',     // dossier de build
    emptyOutDir: true,  // vide le dossier dist avant build
  },
  server: {
    host: true,         // rend le serveur accessible sur le réseau local
    port: 5173,         // port par défaut
  }
})