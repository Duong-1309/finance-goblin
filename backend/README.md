# Finance Goblin — Backend

FastAPI service that exposes device state to the ESP32.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`.
Swagger UI is at `http://localhost:8000/docs`.

## Configuration

Copy `.env.example` to `.env` and fill in values (added in OPS-001):

```bash
cp .env.example .env
```

## Tests

```bash
pytest
```
