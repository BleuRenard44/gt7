# Lancement sur Windows

## Prerequis

- Windows 10 ou 11
- Python 3.10+ installe depuis python.org
- Pendant l'installation de Python, coche `Add python.exe to PATH` si possible.

## Installation

Double-clique sur `install.bat`, ou lance dans PowerShell :

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

Le script cree `.venv`, installe les dependances et cree `.env` si absent.

## Configuration

Edite `.env` :

```env
WORKER_ID=lan-a
BACKEND_URL=http://127.0.0.1:8000
GT7_TARGETS=
GT7_SCAN_CIDRS=192.168.1.0/24
GT7_SCAN_RANGES=
GT7_ALLOW_ANY_SOURCE=true
```

Si la console PS5 a une IP fixe, tu peux mettre par exemple :

```env
GT7_TARGETS=192.168.1.42
GT7_SCAN_CIDRS=
```

## Lancement

Double-clique sur `run.bat`, ou lance :

```powershell
.\run.ps1
```

Arguments utiles :

```powershell
.\run.ps1 --interfaces
.\run.ps1 --print-targets
.\run.ps1 --check
.\run.ps1 --debug
```

## Pare-feu Windows

Au premier lancement, Windows peut demander une autorisation reseau pour Python. Autorise le reseau prive, sinon les paquets UDP GT7 risquent d'etre bloques.

Ports utilises par defaut :

- Reception UDP : `33740`
- Heartbeat UDP : `33739`

## Probleme d'execution PowerShell

Utilise `install.bat` et `run.bat`, ils lancent automatiquement PowerShell avec `ExecutionPolicy Bypass` pour ce script uniquement.
