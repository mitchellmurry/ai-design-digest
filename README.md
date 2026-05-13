# ai-design-digest

Daily AI/design/product digest pipeline.

## Bootstrap

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

If `python3 -m venv` fails with `ensurepip is not available`, install the OS venv package first (example on Debian/Ubuntu: `sudo apt install python3.13-venv`).

## Run tests

```bash
pytest -q
```

## Run pipeline

```bash
python3 -m src.pipeline
```

## Environment

No environment variables are required for the core local test suite.

Telegram sending and deployment integrations can be configured later without blocking core tests.
