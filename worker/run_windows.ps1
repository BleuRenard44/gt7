if (-Not (Test-Path ".venv")) {
  py -m venv .venv
  .\.venv\Scripts\pip install --upgrade pip
  .\.venv\Scripts\pip install -r requirements.txt
}

if (-Not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
}

.\.venv\Scripts\python -m app.main @args
