.RECIPEPREFIX := >
.PHONY: train test lint clean

train:
>PYTHONPATH=. python run/pipeline/training/train.py

test:
>PYTHONPATH=. python -m pytest -q tests/

lint:
>ruff check src/
>mypy src/

clean:
>python -c "import shutil; from pathlib import Path; [shutil.rmtree(p, ignore_errors=True) for p in [Path('outputs/__pycache__'), Path('.mypy_cache'), Path('.ruff_cache')]]"
