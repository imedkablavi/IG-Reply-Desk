# Instagram Auto Reply System

FastAPI service for handling Instagram webhooks, queuing replies, and managing operator workflows through Telegram.

## What is in the project

- `app/` application code
- `app/api/` webhook endpoints
- `app/services/` reply flow, workers, scheduler, and account settings
- `app/bot/` Telegram bot handlers
- `docker-compose.yml` local stack for app, Postgres, and Redis

## Local run

1. Copy `.env.example` to `.env`.
2. Fill in the Meta and Telegram values.
3. Start the stack:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Useful endpoints

- `GET /health` basic health check
- `GET /ops/status` queue and worker status
- `GET /instagram/webhook` Meta webhook verification
- `POST /instagram/webhook` Meta webhook events

## Notes

- For local runs, tables are created on startup.
- Redis and Postgres are expected to be available before the app starts handling traffic.
- `.env`, logs, tests, and local reference HTML files are ignored by Git on purpose.
