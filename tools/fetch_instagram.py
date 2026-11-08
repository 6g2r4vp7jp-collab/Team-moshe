#!/usr/bin/env python3
"""Pull Instagram Insights via the Meta Graph API into analytics/data/ (read-only).

Only READ endpoints are used. This script never publishes, comments, or changes anything.

Auth (never commit the token):
  - Cloud session: the token is stored as a network secret for graph.facebook.com and
    injected by the proxy. Set IG_TOKEN_VIA_PROXY=1.
  - Local: export IG_ACCESS_TOKEN=... (or put it in .env, which is git-ignored).
Also required: IG_USER_ID (Instagram professional account id, not secret).

Usage:
  python3 tools/fetch_instagram.py --check
  python3 tools/fetch_instagram.py --days 14
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "analytics" / "data"
API = "https://graph.facebook.com/v21.0"
MEDIA_METRICS = {"REELS": "views,reach,likes,comments,shares,saved,ig_reels_avg_watch_time,follows,profile_visits",
                 "FEED": "views,reach,likes,comments,shares,saved,follows,profile_visits"}


def load_env():
    f = ROOT / ".env"
    if f.exists():
        for line in f.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def get(path, **params):
    tok = os.environ.get("IG_ACCESS_TOKEN")
    if tok:
        params["access_token"] = tok
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": "Bearer proxy"} if not tok else {})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def configured():
    return bool(os.environ.get("IG_USER_ID")) and bool(
        os.environ.get("IG_ACCESS_TOKEN") or os.environ.get("IG_TOKEN_VIA_PROXY"))


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--days", type=int, default=14)
    a = ap.parse_args()
    if not configured():
        print("Instagram API: לא מחובר. חסרים IG_USER_ID ו-IG_ACCESS_TOKEN / IG_TOKEN_VIA_PROXY. ראה docs/CONNECTIONS.md")
        sys.exit(1)
    uid = os.environ["IG_USER_ID"]
    if a.check:
        try:
            me = get(uid, fields="username,followers_count,media_count")
            print(f"Instagram API: מחובר כ-@{me.get('username')}")
        except Exception as e:  # noqa: BLE001
            print(f"Instagram API: החיבור נכשל ({type(e).__name__}). בדוק טוקן והרשאות.")
            sys.exit(1)
        return
    since = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)
    media = get(f"{uid}/media", fields="id,caption,media_product_type,media_type,timestamp,permalink", limit=50)
    rows = []
    for m in media.get("data", []):
        ts = dt.datetime.fromisoformat(m["timestamp"].replace("+0000", "+00:00"))
        if ts < since:
            continue
        kind = "REELS" if m.get("media_product_type") == "REELS" else "FEED"
        try:
            ins = get(f"{m['id']}/insights", metric=MEDIA_METRICS[kind])
            vals = {i["name"]: i["values"][0]["value"] for i in ins.get("data", [])}
        except Exception:  # noqa: BLE001  (metric unavailable for this media -> leave blank, never guess)
            vals = {}
        wt = vals.get("ig_reels_avg_watch_time")
        rows.append({
            "date": ts.date().isoformat(), "post_id": m["id"],
            "format": "reel" if kind == "REELS" else ("carousel" if m.get("media_type") == "CAROUSEL_ALBUM" else "post"),
            "pillar": "", "title": (m.get("caption") or "").split("\n")[0][:60],
            "views": vals.get("views", ""), "reach": vals.get("reach", ""),
            "avg_watch_time_sec": round(wt / 1000, 1) if isinstance(wt, (int, float)) else "",
            "likes": vals.get("likes", ""), "comments": vals.get("comments", ""), "shares": vals.get("shares", ""),
            "saves": vals.get("saved", ""), "follows": vals.get("follows", ""),
            "profile_visits": vals.get("profile_visits", ""), "permalink": m.get("permalink", ""),
        })
    OUT.mkdir(parents=True, exist_ok=True)
    f = OUT / f"posts_api_{dt.date.today().isoformat()}.csv"
    with f.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else ["date"])
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} posts to {f.relative_to(ROOT)}. מלא את עמודת pillar ידנית לניתוח לפי עמודי תוכן.")


if __name__ == "__main__":
    main()
