#!/usr/bin/env bash
set -euo pipefail
docker build -t gt7-dashboard-backend:local ./backend
docker build -t gt7-dashboard-frontend:local ./frontend
