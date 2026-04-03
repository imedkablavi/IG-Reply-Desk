# IG Reply Desk

IG Reply Desk is a FastAPI backend for Instagram automation. It receives webhook events, queues outgoing work, and gives operators day-to-day controls through Telegram.

## Project Identity

- Repository name: ig-reply-desk
- One-line description: Reliable Instagram webhook and auto-reply backend with Redis queues, worker controls, and Telegram-based operations.
- GitHub About text: Backend service for Instagram webhooks and auto-replies, built with FastAPI, Redis queues, and Telegram operator controls.
- Suggested topics: fastapi, instagram, webhook, automation, redis, postgres, telegram-bot, background-workers, saas-backend

## What this service does

- Handles Instagram webhook events from Meta
- Pushes reply jobs into Redis queues
- Processes messages through workers instead of direct inline sends
- Gives operators runtime controls through Telegram commands

## Key folders

- `app/api/` webhook endpoints
- `app/services/` reply logic, worker management, and scheduling
- `app/bot/` Telegram handlers and keyboards
- `app/routers/ops.py` operations and health endpoints
- `docker-compose.yml` local stack (app, Postgres, Redis)

## Run locally

1. Create `.env` from `.env.example`.
2. Add your Meta and Telegram credentials.
3. Start the stack:

```bash
docker compose up --build
```

The API will be available at `http://localhost:8000`.

## Useful endpoints

- `GET /health` quick health check
- `GET /ops/status` queue and worker status
- `GET /instagram/webhook` Meta webhook verification
- `POST /instagram/webhook` incoming Instagram events

## Practical notes

- In local mode, database tables are created at startup.
- Redis and Postgres should be reachable before processing live traffic.
- Environment files, logs, and local test artifacts are intentionally excluded from Git.
