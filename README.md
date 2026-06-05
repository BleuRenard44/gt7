# GT7 Dashboard avec worker télémétrie réel

Ce projet contient :

- Backend FastAPI + WebSocket
- Frontend React/Vite
- Worker GT7 UDP réel
- Déchiffrement Salsa20 du paquet GT7
- Heartbeat UDP vers les consoles
- Ingestion HTTP vers le backend
- Gestion équipes / pilotes / relais
- Docker Compose
- GitHub Pages workflow

## Architecture

```text
PS5 #1 ---- UDP 33740 ----\
PS5 #2 ---- UDP 33740 ----- worker ---- HTTP ---- backend ---- WebSocket ---- frontend
PS5 #3 ---- UDP 33740 ----/
PS5 #4 ---- UDP 33740 ---/
```

Le worker écoute les paquets GT7, les décode, puis envoie la télémétrie au backend.

## Lancement Docker

```bash
docker compose up --build
```

Frontend :

```text
http://localhost:3000
```

Backend docs :

```text
http://localhost:8000/docs
```

## Configuration

Dans `docker-compose.yml` :

```yaml
GT7_CONSOLES: 192.168.1.101,192.168.1.102,192.168.1.103,192.168.1.104
```

Remplace par les vraies IP des PS5.

## Ports nécessaires

Sur le PC qui lance le worker :

```text
UDP entrant 33740
UDP sortant 33739
TCP 8000 backend
TCP 3000 frontend
```

## Important

Pour que GT7 envoie la télémétrie :

1. La console et le PC doivent être sur le même LAN.
2. GT7 doit être lancé.
3. Il faut être en piste.
4. Les IP des consoles doivent être correctes.
5. Le firewall doit autoriser UDP 33739/33740.

## Si tu es sur Podman

```bash
systemctl --user enable --now podman.socket
docker compose up --build
```

## Mode worker

Le service `worker` est celui qui récupère les vraies données GT7.

Logs :

```bash
docker compose logs -f worker
```

## Fichiers importants

```text
worker/app/gt7_protocol.py     Déchiffrement + parsing GT7
worker/app/main.py             Worker multi-consoles
backend/app/main.py            API + WebSocket + ingestion télémétrie
frontend/src/                  Dashboard
```
