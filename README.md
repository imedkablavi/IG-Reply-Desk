# IG Reply Desk

IG Reply Desk is a backend service for Instagram automation.
It receives Meta webhook events, moves outgoing work into Redis queues, and gives operators clear controls through Telegram.

The goal is simple: keep replies reliable under load, while still giving the team operational control.

## Project identity

- Repository name: ig-reply-desk
- One-line description: Instagram webhook and auto-reply backend with Redis queues, worker controls, and Telegram operations.
- GitHub About text: FastAPI backend for Instagram webhooks, queued replies, and operator workflows via Telegram.
- Suggested topics: fastapi, instagram, webhook, automation, redis, postgres, telegram-bot, worker-queue, backend

## What this service does

- Receives Instagram events from Meta webhooks
- Queues reply jobs in Redis instead of sending inline
- Processes jobs through workers for better stability and throughput
- Exposes operator actions and safety controls in Telegram

## Main folders

- `app/api/`: webhook endpoints
- `app/services/`: reply engine, worker orchestration, account settings
- `app/bot/`: Telegram commands and interaction flows
- `app/routers/ops.py`: health and operational endpoints
- `docker-compose.yml`: local app + Postgres + Redis stack

## Local setup

1. Create `.env` from `.env.example`.
2. Fill all required Meta and Telegram credentials.
3. Start the stack:

```bash
docker compose up --build
```

Service URL:

`http://localhost:8000`

## Useful endpoints

- `GET /health`: basic service health
- `GET /ops/status`: worker and queue status
- `GET /instagram/webhook`: Meta verification endpoint
- `POST /instagram/webhook`: incoming Instagram webhook events

## Security hardening checklist

- Verify webhook signatures on every incoming Meta event.
- Keep tokens and secrets only in environment variables (never in source control).
- Rotate Meta and Telegram tokens on a fixed schedule.
- Use least-privilege access for DB, Redis, and bot credentials.
- Add rate limiting on public webhook routes.
- Log events without leaking PII or credential values.
- Restrict `/ops/*` endpoints behind authentication and role checks.

## Operational notes

- Local startup creates required database tables.
- Redis and Postgres must be healthy before handling production traffic.
- Environment files, logs, and local artifacts are intentionally excluded from Git.
