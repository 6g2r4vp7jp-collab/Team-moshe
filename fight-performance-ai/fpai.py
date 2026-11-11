#!/usr/bin/env python3
"""Fight Performance AI - שלב 1: חיבור ל-WHOOP ובדיקת משיכת נתונים.

  python3 fpai.py setup                 שמירת Client ID/Secret מקומית (מחוץ לריפו)
  python3 fpai.py login                 התחברות (מחשב מקומי, דפדפן נפתח אוטומטית)
  python3 fpai.py start                 התחברות מרחוק - שלב א: מדפיס כתובת אישור
  python3 fpai.py finish "<URL>"        התחברות מרחוק - שלב ב: הכתובת שאליה הופניתם
  python3 fpai.py status                מצב החיבור
  python3 fpai.py test [--days N|--all] משיכת נתונים ובדיקת כיסוי
  python3 fpai.py logout                ביטול הגישה ומחיקת הטוקנים
"""
from __future__ import annotations

import argparse
import getpass
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone

from fpai import auth, config, whoop


def cmd_setup(_):
    print("פרטי האפליקציה מ-https://developer-dashboard.whoop.com (נשמרים ב-%s, הרשאות 600)" % config.client_file())
    cid = input("Client ID: ").strip()
    secret = getpass.getpass("Client Secret (לא יוצג): ").strip()
    redirect = input(f"Redirect URI [{config.DEFAULT_REDIRECT_URI}]: ").strip() or config.DEFAULT_REDIRECT_URI
    if not cid or not secret:
        sys.exit("Client ID ו-Secret נדרשים.")
    config.write_private_json(config.client_file(),
                              {"client_id": cid, "client_secret": secret, "redirect_uri": redirect})
    print("נשמר. ודאו שה-Redirect URI הזה רשום גם ב-Developer Dashboard.")


def cmd_login(_):
    auth.login_local()
    print("✅ מחובר ל-WHOOP.")
    cmd_status(None)


def cmd_start(_):
    url = auth.build_authorize_url()
    print("1. פתחו את הכתובת הבאה בדפדפן ואשרו את הגישה:\n")
    print(url)
    print("\n2. אחרי האישור הדפדפן יעבור לכתובת שמתחילה ב-redirect URI (ייתכן שהדף לא ייטען - זה תקין).")
    print("   העתיקו את הכתובת המלאה משורת הכתובת והריצו:  python3 fpai.py finish \"<URL>\"")
    print("   (הקוד חד-פעמי, תקף דקות ספורות, ולא שמיש בלי ה-Client Secret.)")


def cmd_finish(a):
    auth.finish(a.url)
    print("✅ מחובר ל-WHOOP.")
    cmd_status(None)


def cmd_status(_):
    s = auth.status()
    if not s["connected"]:
        print("לא מחובר.")
        return
    print(f"מחובר | refresh token: {'כן' if s['has_refresh_token'] else 'לא'} | "
          f"access token בתוקף עוד {s['access_token_valid_for_sec'] // 60} דק'")
    print(f"scopes: {s['scope']}")


def _date_range(records, key):
    vals = sorted(r[key] for r in records if r.get(key))
    return (vals[0][:10], vals[-1][:10]) if vals else ("-", "-")


def _coverage(records, getter):
    """Share of records where a measured value is actually present."""
    present = [getter(r) for r in records]
    present = [v for v in present if v is not None]
    return len(present), len(records)


def _sc(r, *keys):
    v = r.get("score") or {}
    for k in keys:
        if not isinstance(v, dict):
            return None
        v = v.get(k)
    return v


def cmd_test(a):
    end = datetime.now(timezone.utc)
    start = None if a.all else end - timedelta(days=a.days)
    label = "כל ההיסטוריה הזמינה" if a.all else f"{a.days} הימים האחרונים"
    print(f"== בדיקת משיכת נתונים: {label} ==\n")

    prof = whoop.profile()
    print(f"פרופיל: {prof.get('first_name', '?')} (user_id קיים: {'user_id' in prof})")
    try:
        body = whoop.body_measurement()
        print(f"מדידות גוף: גובה {body.get('height_meter')} מ' | משקל {body.get('weight_kilogram')} ק\"ג | "
              f"דופק מקסימלי (לפי WHOOP) {body.get('max_heart_rate')}")
    except whoop.ApiError as e:
        print(f"מדידות גוף: שגיאה {e}")

    raw = {"profile_keys": sorted(prof.keys())}
    checks = {
        "cycles": [("Strain", lambda r: _sc(r, "strain")),
                   ("דופק ממוצע", lambda r: _sc(r, "average_heart_rate"))],
        "recovery": [("Recovery %", lambda r: _sc(r, "recovery_score")),
                     ("HRV (rMSSD)", lambda r: _sc(r, "hrv_rmssd_milli")),
                     ("דופק מנוחה", lambda r: _sc(r, "resting_heart_rate")),
                     ("SpO2", lambda r: _sc(r, "spo2_percentage")),
                     ("טמפ' עור", lambda r: _sc(r, "skin_temp_celsius"))],
        "sleep": [("ביצועי שינה %", lambda r: _sc(r, "sleep_performance_percentage")),
                  ("קצב נשימה", lambda r: _sc(r, "respiratory_rate"))],
        "workouts": [("Strain אימון", lambda r: _sc(r, "strain")),
                     ("זמן באזורי דופק", lambda r: _sc(r, "zone_durations"))],
    }
    for name in whoop.COLLECTIONS:
        try:
            recs = whoop.fetch_collection(name, start=start, end=end)
        except whoop.ApiError as e:
            print(f"\n[{name}] ❌ {e}")
            continue
        raw[name] = recs
        key = "created_at" if name == "recovery" else "start"
        first, last = _date_range(recs, key)
        states = Counter(r.get("score_state") for r in recs)
        print(f"\n[{name}] ✅ {len(recs)} רשומות | {first} → {last} | score_state: {dict(states)}")
        for lbl, g in checks[name]:
            n, tot = _coverage(recs, g)
            print(f"   {lbl}: קיים ב-{n}/{tot}")
        if name == "workouts" and recs:
            sports = Counter(r.get("sport_name") for r in recs)
            print(f"   סוגי אימון: {dict(sports.most_common(8))}")
        if name == "recovery" and recs:
            r = recs[0]
            print(f"   אחרון: Recovery {_sc(r, 'recovery_score')}% | HRV {_sc(r, 'hrv_rmssd_milli')} ms | "
                  f"RHR {_sc(r, 'resting_heart_rate')} | calibrating={_sc(r, 'user_calibrating')}")

    out = config.raw_dir() / f"test_pull_{end.strftime('%Y%m%dT%H%M%S')}.json"
    config.write_private_json(out, raw)
    print(f"\nהנתונים הגולמיים נשמרו (מחוץ לריפו): {out}")


def cmd_logout(_):
    auth.logout()
    print("הגישה בוטלה והטוקנים נמחקו.")


def main():
    p = argparse.ArgumentParser(description="Fight Performance AI - WHOOP connection")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup").set_defaults(f=cmd_setup)
    sub.add_parser("login").set_defaults(f=cmd_login)
    sub.add_parser("start").set_defaults(f=cmd_start)
    f = sub.add_parser("finish")
    f.add_argument("url")
    f.set_defaults(f=cmd_finish)
    sub.add_parser("status").set_defaults(f=cmd_status)
    t = sub.add_parser("test")
    t.add_argument("--days", type=int, default=30)
    t.add_argument("--all", action="store_true")
    t.set_defaults(f=cmd_test)
    sub.add_parser("logout").set_defaults(f=cmd_logout)
    a = p.parse_args()
    try:
        a.f(a)
    except (config.MissingCredentials, auth.AuthError, whoop.ApiError) as e:
        sys.exit(f"❌ {e}")


if __name__ == "__main__":
    main()
