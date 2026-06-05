

## Correction Python 3.14

Cette version retire `pydantic` du worker autonome.
Le worker fonctionne sans compiler `pydantic-core` / PyO3.

Si tu avais déjà créé un environnement virtuel avec l'ancienne version :

```bash
rm -rf .venv
./install.sh
./run.sh
```
