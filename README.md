# GT7 Race Dashboard

Dashboard temps réel pour courses Gran Turismo 7 multi-consoles sur réseau local.

## Fonctionnalités

- Backend FastAPI
- WebSocket temps réel
- Frontend React/Vite
- Gestion équipes
- Gestion pilotes
- Gestion relais
- Scoreboard live
- Carte circuit live
- Mode simulation intégré pour tester sans PS5
- Docker Compose
- Manifests Kubernetes
- Workflow GitHub Pages
- Endpoint healthcheck

## Lancement local avec Docker

```bash
docker compose up --build
```

Frontend :

```text
http://localhost:3000
```

Backend API :

```text
http://localhost:8000/docs
```

WebSocket :

```text
ws://localhost:8000/ws
```

## Lancement local sans Docker

Backend :

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.main
```

Frontend :

```bash
cd frontend
npm install
npm run dev
```

## Configuration consoles

Modifie `backend/app/config.py` ou utilise les variables d'environnement :

```bash
GT7_CONSOLES=192.168.1.101,192.168.1.102,192.168.1.103,192.168.1.104
GT7_MODE=simulator
```

Modes disponibles :

```text
simulator
udp-placeholder
```

Le mode `simulator` permet de tester tout le dashboard immédiatement.

Le mode `udp-placeholder` contient la structure prête pour brancher le vrai parser GT7 UDP.

## GitHub Pages

Le frontend peut être publié sur GitHub Pages avec :

```text
.github/workflows/deploy-pages.yml
```

Ajoute un secret GitHub :

```text
GH_PAT
```

Puis configure Pages sur la branche `gh-pages`.

## Production LAN

Pour récupérer l'UDP depuis le LAN, utilise le backend en `network_mode: host` sous Linux.

```yaml
network_mode: host
```

C'est déjà configuré dans `docker-compose.yml`.

## Notes GT7

GT7 expose de la télémétrie UDP locale avec heartbeat. Le vrai décodage doit être branché dans :

```text
backend/app/telemetry/gt7_udp.py
```

Le projet reste totalement buildable même sans PS5 grâce au simulateur.
