---
name: fight-performance-ai
description: Fight Performance AI - personal performance system for a pro kickboxing / Muay Thai fighter, connected to WHOOP via the official OAuth 2.0 API. Use when the user asks about their WHOOP data (recovery, HRV, resting HR, sleep, strain, workouts), wants to connect/reconnect WHOOP, or asks for training-load guidance. Phase 1: connection and data-pull verification only.
---

# Fight Performance AI (שלב 1 - חיבור WHOOP)

All code lives in `fight-performance-ai/` at the repo root. Run commands from that folder.

## Rules
- Never print, log, commit or ask the user to paste the Client Secret, access token or refresh token.
  Secrets live only in env vars (`WHOOP_CLIENT_ID`, `WHOOP_CLIENT_SECRET`) or `$FPAI_HOME/client.json` (0600).
- Use only real values returned by the WHOOP API. If a field is missing, `score_state` is not `SCORED`,
  or `user_calibrating` is true, say so explicitly; never estimate or fill in.
- The API has no continuous heart-rate stream. Do not claim to measure between-round HR recovery from it.
- Reply to the user in Hebrew.

## Commands
| Purpose | Command |
|---|---|
| Save app credentials (interactive, local machine) | `python3 fpai.py setup` |
| Log in on a local machine | `python3 fpai.py login` |
| Log in from a remote/cloud session | `python3 fpai.py start`, then `python3 fpai.py finish "<redirected URL>"` |
| Connection status | `python3 fpai.py status` |
| Test data pull | `python3 fpai.py test --days 30` or `--all` |
| Revoke and delete tokens | `python3 fpai.py logout` |

## Official API facts (verified against developer.whoop.com + OpenAPI spec)
- Auth: `https://api.prod.whoop.com/oauth/oauth2/auth`, token: `.../oauth/oauth2/token`, state = 8 chars.
- `offline` scope is required for a refresh token. Refresh tokens rotate on every use.
- Base: `https://api.prod.whoop.com/developer` + `/v2/cycle`, `/v2/recovery`, `/v2/activity/sleep`,
  `/v2/activity/workout`, `/v2/user/profile/basic`, `/v2/user/measurement/body`.
- Collections: `start`, `end`, `limit` (max 25), `nextToken`. Rate limit: 100/min, 10,000/day.

## Not yet built (waiting for the user to confirm the connection works)
Trend analysis, manual entry of fitness tests and sessions, reports, Hebrew dashboard.
