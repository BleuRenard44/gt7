$ErrorActionPreference = "Stop"

Set-Location -Path $PSScriptRoot

function Get-PythonCommand {
    $commands = @("py -3", "python", "python3")
    foreach ($cmd in $commands) {
        try {
            if ($cmd -eq "py -3") {
                & py -3 --version *> $null
                if ($LASTEXITCODE -eq 0) { return "py -3" }
            } else {
                & $cmd --version *> $null
                if ($LASTEXITCODE -eq 0) { return $cmd }
            }
        } catch {}
    }
    throw "Python 3 est introuvable. Installe Python depuis https://www.python.org/downloads/windows/ puis relance ce script."
}

$python = Get-PythonCommand
Write-Host "Python detecte: $python"

if (-not (Test-Path ".venv")) {
    Write-Host "Creation de l'environnement virtuel..."
    if ($python -eq "py -3") {
        & py -3 -m venv .venv
    } else {
        & $python -m venv .venv
    }
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "L'environnement virtuel Windows est invalide: $venvPython introuvable. Supprime le dossier .venv puis relance install.ps1."
}

Write-Host "Mise a jour de pip..."
& $venvPython -m pip install --upgrade pip

Write-Host "Installation des dependances..."
& $venvPython -m pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Fichier .env cree depuis .env.example"
}

Write-Host "Installation OK. Edite .env si besoin, puis lance run.ps1 ou run.bat."
