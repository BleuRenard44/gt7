#!/usr/bin/env bash
set -euo pipefail

if [ ! -d .venv ]; then
  echo "Environnement virtuel absent. Lance ./install.sh avant."
  exit 1
fi

. .venv/bin/activate
python -m app.main "$@"
