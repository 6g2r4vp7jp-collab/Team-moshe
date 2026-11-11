"""Minimal WHOOP Developer API v2 client.

Endpoints and limits come from the official OpenAPI spec
(https://api.prod.whoop.com/developer/doc/openapi.json):
  collections accept start, end, limit (max 25) and nextToken.
Rate limits: 100 requests/minute, 10,000/day.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

from . import auth, config

COLLECTIONS = {
    "cycles": "/v2/cycle",
    "recovery": "/v2/recovery",
    "sleep": "/v2/activity/sleep",
    "workouts": "/v2/activity/workout",
}
MAX_LIMIT = 25


class ApiError(RuntimeError):
    def __init__(self, status: int, path: str, detail: str = ""):
        super().__init__(f"WHOOP API {path} returned HTTP {status} {detail}".strip())
        self.status = status


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def get(path: str, params: dict | None = None, _retried: bool = False) -> dict:
    url = config.API_BASE + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    req = urllib.request.Request(
        url, headers={"Authorization": f"Bearer {auth.get_access_token()}", "Accept": "application/json",
                   "User-Agent": config.USER_AGENT}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        if e.code == 401 and not _retried:
            auth.refresh()
            return get(path, params, _retried=True)
        if e.code == 429:
            wait = int(e.headers.get("X-RateLimit-Reset", "60") or 60)
            print(f"  rate limit - waiting {wait}s")
            time.sleep(wait + 1)
            return get(path, params, _retried=_retried)
        raise ApiError(e.code, path, e.reason) from None


def fetch_collection(name: str, start: datetime | None = None, end: datetime | None = None,
                     max_records: int | None = None) -> list[dict]:
    path = COLLECTIONS[name]
    params = {
        "limit": MAX_LIMIT,
        "start": _iso(start) if start else None,
        "end": _iso(end) if end else None,
    }
    records: list[dict] = []
    while True:
        page = get(path, params)
        records.extend(page.get("records", []))
        token = page.get("next_token")
        if not token or (max_records and len(records) >= max_records):
            break
        params["nextToken"] = token
    return records[:max_records] if max_records else records


def profile() -> dict:
    return get("/v2/user/profile/basic")


def body_measurement() -> dict:
    return get("/v2/user/measurement/body")
