# Operations Runbook - IG Reply Desk

This runbook is for daily operations. Keep it simple: check status, react fast, and isolate issues early.

## Morning check (5 minutes)

1. Open `/ops/status` and confirm:
- `system_status = OPERATIONAL`
- `workers_alive > 0`
- `total_queue_backlog < 50`

2. Review Telegram admin alerts:
- Treat `SILENCE DETECTED` and `CRITICAL` as high priority.

3. Run `/setup_check` in the bot:
- Confirms tokens and integration basics are still valid.

## Live monitoring

### Key alerts

- `SILENCE DETECTED`: workers may be stuck or not processing.
- `QUEUE BACKLOG`: incoming load is higher than processing capacity.
- `HEARTBEAT ALERT`: webhook delivery or connectivity issue.

### Fast actions

- If queue size is above 1000:
    check `/health_report`; if one account is causing the spike, run `/lock_account {id}`.
- If incoming events are present but outgoing replies are zero:
    restart worker processes.

## Incident response

### A) Full outage (Meta issue or internal bug)

1. Pause processing:
- `/pause_all`

2. Investigate:
- review application logs
- check Meta status page

3. Resume when stable:
- `/resume_all`

### B) Single noisy account (loop or spam)

1. Identify affected account from alerts.
2. Isolate it:
- `/lock_account {id}`

3. Inspect failed items:
- `/deadletters {id}`

4. Recover after fix:
- `/unlock_account {id}`

### C) No outgoing replies

1. Verify incoming rate in `/ops/status`.
2. If incoming > 0 and outgoing = 0:
- restart worker services immediately.

## End-of-day safety check

1. Run `/stats` and review reply mix (human vs auto).
2. Sample dead letters with `/deadletters {id}`.
3. Confirm `global_kill_switch` is not left enabled.

## Weekly maintenance

1. Confirm retention cleanup jobs completed.
2. Verify token refresh is healthy.
3. Review average processing time trend; scale workers if latency keeps rising.

## Feature flow: keyword in comment -> private DM

### Setup

1. In Telegram, open `💬 رد خاص للتعليقات`.
2. Add keyword and DM response.
3. Optionally update account copy in `📝 تخصيص نصوص الحساب`.

### Event requirements

- Webhook payload must include `entry[].changes[]`.
- `field` must be `comments`.
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

Reference sample:
`tests/payloads/comment_video_keyword.json`

### Expected result

1. Comment matches active keyword rules.
2. DM job is pushed to `queue:{account_id}`.
3. Worker sends DM through Graph API.
4. Activity log includes `COMMENT_DM_TRIGGERED`.

### Negative checks

1. Media type is `IMAGE` -> no DM is sent.
2. No keyword match -> no DM is sent.
3. Duplicate event with same comment ID -> ignored by deduplication.
