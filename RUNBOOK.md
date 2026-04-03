# Operations Runbook - IG Reply Desk

This runbook is written for real daily use.
Follow it in order, escalate early, and avoid risky manual fixes during incidents.

## Morning checks (about 5 minutes)

1. Open `/ops/status` and verify:
- `system_status = OPERATIONAL`
- `workers_alive > 0`
- `total_queue_backlog < 50`

2. Review Telegram admin alerts:
- Treat `SILENCE DETECTED` and `CRITICAL` as immediate action items.

3. Run `/setup_check` in the bot:
- Confirm tokens and baseline integration health.

## Live monitoring

### Alert meaning

- `SILENCE DETECTED`: workers may be stalled or not consuming jobs.
- `QUEUE BACKLOG`: incoming workload is exceeding processing capacity.
- `HEARTBEAT ALERT`: webhook delivery or connectivity problem.

### First actions

- Queue above 1000:
    check `/health_report`; if a single account is causing load, run `/lock_account {id}`.
- Incoming events > 0 but outgoing replies = 0:
    restart worker services and re-check `/ops/status`.

## Incident response playbook

### A) Full outage (Meta issue or internal failure)

1. Pause processing:
- `/pause_all`

2. Investigate quickly:
- review app logs
- check Meta platform status

3. Resume only when stable:
- `/resume_all`

### B) Noisy account (loop, spam, bad rules)

1. Identify the account from alerts.
2. Isolate it:
- `/lock_account {id}`

3. Inspect failed/blocked items:
- `/deadletters {id}`

4. Recover after root cause is fixed:
- `/unlock_account {id}`

### C) No outgoing replies

1. Confirm incoming rate in `/ops/status`.
2. If incoming exists and outgoing is zero:
- restart workers immediately.

## Security response checklist

Run this checklist if you suspect token leak, abuse, or unauthorized access.

1. Pause processing: `/pause_all`.
2. Rotate Meta and Telegram tokens.
3. Revoke old credentials and active sessions.
4. Audit logs for unusual sources, spikes, or command misuse.
5. Resume only after verification checks pass.

## End-of-day checks

1. Run `/stats` and review reply quality (human vs auto ratio).
2. Inspect a sample of dead letters with `/deadletters {id}`.
3. Confirm `global_kill_switch` is not left enabled.

## Weekly maintenance

1. Confirm retention cleanup jobs completed.
2. Verify token rotation and expiration windows.
3. Review processing latency trend and scale workers when needed.

## Feature flow: comment keyword to private DM

### Setup

1. In Telegram, open `💬 رد خاص للتعليقات`.
2. Add keyword and DM text.
3. Optionally update account copy in `📝 تخصيص نصوص الحساب`.

### Event requirements

- Webhook payload includes `entry[].changes[]`.
- `field` equals `comments`.
- Supported media types: `VIDEO`, `REELS`, `IGTV`.

### Local payload example

```json
{
    "object": "instagram",
    "entry": [
        {
            "id": "YOUR_INSTAGRAM_PAGE_ID",
            "time": 1710000000,
            "changes": [
                {
                    "field": "comments",
                    "value": {
                        "id": "17890000000000001",
                        "text": "Can I get the price?",
                        "from": {
                            "id": "17840000000000001",
                            "username": "test_user"
                        },
                        "media": {
                            "id": "17910000000000001",
                            "media_product_type": "VIDEO"
                        }
                    }
                }
            ]
        }
    ]
}
```

### Expected result

1. Comment matches an active keyword rule.
2. DM job is queued in `queue:{account_id}`.
3. Worker sends DM through Graph API.
4. Activity log records `COMMENT_DM_TRIGGERED`.

### Negative checks

1. Media type is `IMAGE` -> no DM is sent.
2. No keyword match -> no DM is sent.
3. Duplicate comment ID -> event is ignored by deduplication.
