# Instagram Auto Reply SaaS - Operational Runbook

## 1. Morning Check (5 Minutes)
**Role:** On-Call Engineer / Owner
**Time:** 09:00 AM

1.  **Check Status Page:**
    *   Visit `/ops/status` (via Admin Tool or Postman).
    *   Verify `system_status` is `OPERATIONAL`.
    *   Verify `workers_alive` > 0.
    *   Verify `total_queue_backlog` < 50.
2.  **Check Telegram Alerts:**
    *   Look for "SILENCE DETECTED" or "CRITICAL" messages in Admin Channel.
3.  **Check Meta Permissions:**
    *   Run `/setup_check` in Telegram Bot to verify tokens are valid.

## 2. Live Monitoring
**Role:** Automated + On-Call
**Frequency:** 24/7

*   **Alerts:**
    *   `SILENCE DETECTED`: Logic Failure. Workers might be stuck.
    *   `QUEUE BACKLOG`: High Load. Consider adding workers.
    *   `HEARTBEAT ALERT`: Webhook failure. Check Meta connection.
*   **Actions:**
    *   If Queue > 1000: Check `/health_report`. If one account is spamming, use `/lock_account {id}`.
    *   If Silence Detected: Check logs. If stuck, restart workers.

## 3. Incident Response

### Scenario A: Global Outage (Meta Down or Bug)
1.  **Activate Kill Switch:**
    *   Command: `/pause_all`
    *   Effect: Stops processing but keeps receiving webhooks.
2.  **Diagnose:**
    *   Check logs: `tail -f app.log`
    *   Check Meta Status: `developers.facebook.com/status`
3.  **Fix & Resume:**
    *   Deploy fix or wait for Meta.
    *   Command: `/resume_all`

### Scenario B: Rogue Account (Spam/Loop)
1.  **Identify:**
    *   Alert: "High Load Account {id}"
2.  **Isolate:**
    *   Command: `/lock_account {id}`
    *   Effect: Messages for this account go to DLQ. Others unaffected.
3.  **Investigate:**
    *   Command: `/deadletters {id}`
4.  **Resolve:**
    *   Fix loop/configuration.
    *   Command: `/unlock_account {id}`

### Scenario C: Silence (No Replies)
1.  **Check:** Are webhooks arriving? (`/ops/status` -> `incoming_rate`)
2.  **If Incoming OK but Outgoing 0:**
    *   Workers are likely stuck or crashing.
    *   Action: Restart Worker Process.

## 4. Night Safety Check
**Role:** On-Call
**Time:** 11:00 PM

1.  **Review Daily Stats:**
    *   Command: `/stats`
    *   Ensure `human_replies` vs `auto_replies` ratio is healthy.
2.  **Check DLQ:**
    *   Command: `/deadletters {id}` (Random check).
3.  **Sleep Mode:**
    *   Ensure no `global_kill_switch` is accidentally active.

## 5. Weekly Maintenance
**Day:** Sunday

1.  **Database Cleanup:**
    *   Verify `data_retention_cleanup` ran successfully.
2.  **Token Refresh:**
    *   Verify tokens were refreshed (Logs).
3.  **Performance Review:**
    *   Check `avg_processing_time` trend. If increasing, plan scaling.

## 6. Comment Keyword -> Private DM (Video/Reels)
**Goal:** If a user comments on a video with a keyword, send DM automatically.

1.  **Configure from Telegram Bot**
    *   Open `💬 رد خاص للتعليقات`.
    *   Add keyword + DM response.
2.  **Set owner-facing texts (optional)**
    *   Open `📝 تخصيص نصوص الحساب`.
    *   Update:
        *   Welcome text
        *   Fallback text
        *   Soft welcome text
3.  **Webhook payload must include `changes`**
    *   Feature listens to `entry[].changes[]` where `field = comments`.
    *   Supported media types:
        *   `VIDEO`
        *   `REELS`
        *   `IGTV`

### Manual Test Payload (Example)
Use this payload for local verification:

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
            "text": "ممكن السعر",
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

Reference file: `tests/payloads/comment_video_keyword.json`

### Expected Result
1.  Comment is matched against account comment rules.
2.  DM is queued in `queue:{account_id}`.
3.  Worker sends DM through Graph API.
4.  Activity log contains `COMMENT_DM_TRIGGERED`.

### Negative Checks
1.  If media type is `IMAGE` -> no DM is sent.
2.  If keyword not matched -> no DM is sent.
3.  Duplicate comment event (`same comment id`) -> ignored by deduplication.
