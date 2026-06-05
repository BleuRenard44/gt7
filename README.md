# GT7 Race Control Ultra

Version ultra complète du dashboard GT7.

## Nouvelles vues

- **Race Control** : vue desktop complète pour l'organisation.
- **Teams Mobile** : dashboard par équipe optimisé téléphone.
- **Car Detail** : vue voiture complète avec télémétrie détaillée.
- **Public Screen** : écran public/stream plus lisible.
- **Tracks** : enregistrement automatique du circuit.
- **Tools** : pénalités, incidents, pit stops.
- **Events** : journal live + exports.

## Fonctionnalités

- workers illimités
- plusieurs consoles par worker
- circuit automatique depuis coordonnées GT7
- affichage voitures sur tracé
- équipes/pilotes/relais
- dashboard mobile par équipe
- QR/access links pour chaque équipe
- vue voiture complète
- jauges throttle/brake/fuel/tyres/températures
- session flags/timer
- pénalités/incidents/pit stops
- exports CSV/JSON
- persistance locale
- responsive automatique

## Lancement

```bash
docker compose up --build backend frontend
```

Dashboard :

```text
http://localhost:3000
```

Worker :

```bash
cd worker
./install.sh
cp .env.example .env
nano .env
./run.sh
```

## Accès téléphone équipe

Depuis un téléphone sur le même réseau ou à distance :

```text
http://IP:3000/team/SOURCE_ID
```

Exemple :

```text
http://IP:3000/team/lan-a%3A192.168.1.101
```

Depuis l'app, va dans **Teams Mobile**, sélectionne une équipe, puis partage l'URL affichée.

## Accès distant

Dans `docker-compose.yml`, change :

```yaml
VITE_API_BASE_URL: http://IP_PUBLIQUE:8000
VITE_WS_URL: ws://IP_PUBLIQUE:8000/ws
```

Puis :

```bash
docker compose down
docker compose build --no-cache frontend
docker compose up -d
```


## Ajouts Performance

Cette version ajoute :

- pneus live
- usure moyenne
- estimation usure par tour
- estimation tours restants
- chronos best/last lap
- secteurs S1/S2/S3
- delta leader
- delta voiture devant
- classement performance
- heatmap freinage / accélération / coast
- export performance CSV

Les secteurs sont calculés automatiquement en divisant la progression du circuit enregistré en 3 parties.
Le delta est estimé avec la progression sur circuit et la vitesse moyenne.


## Mise à jour heatmap

La carte a maintenant :

- bouton Heatmap ON/OFF
- filtre heatmap : toutes zones / freinage / accélération / coast
- toggle circuit fin / large
- voitures plus petites en mode circuit fin
- lignes de circuit affinées
