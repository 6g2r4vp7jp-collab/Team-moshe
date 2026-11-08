#!/usr/bin/env python3
"""Weekly Instagram performance report for OR MOSHE BRAND.

Reads real Insights CSVs from analytics/data/ (or analytics/sample/ with --sample),
writes analytics/reports/weekly_<week>.md and .json. Never invents values: a metric that
is missing from the source is reported as missing, not estimated.

Usage:
  python3 tools/weekly_report.py [--sample] [--week YYYY-MM-DD]
"""
import argparse
import csv
import datetime as dt
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "analytics" / "data"
SAMPLE = ROOT / "analytics" / "sample"
REPORTS = ROOT / "analytics" / "reports"
CRM = ROOT / "crm"

METRICS = ["views", "reach", "avg_watch_time_sec", "likes", "comments", "shares",
           "saves", "follows", "profile_visits"]

# Normalised header (lowercase, spaces collapsed) -> canonical column.
COLUMN_ALIASES = {
    "date": "date", "publish time": "date", "published": "date", "תאריך": "date", "זמן פרסום": "date",
    "post_id": "post_id", "post id": "post_id", "מזהה פוסט": "post_id", "id": "post_id",
    "format": "format", "post type": "format", "media type": "format", "סוג פוסט": "format",
    "pillar": "pillar", "title": "title", "description": "title", "caption": "title", "תיאור": "title",
    "views": "views", "plays": "views", "video views": "views", "צפיות": "views",
    "reach": "reach", "accounts reached": "reach", "טווח הגעה": "reach", "חשבונות שהגיעו אליהם": "reach",
    "avg_watch_time_sec": "avg_watch_time_sec", "average watch time": "avg_watch_time_sec",
    "average watch time (seconds)": "avg_watch_time_sec", "זמן צפייה ממוצע": "avg_watch_time_sec",
    "likes": "likes", "לייקים": "likes", "comments": "comments", "תגובות": "comments",
    "shares": "shares", "שיתופים": "shares", "saves": "saves", "שמירות": "saves",
    "follows": "follows", "new follows": "follows", "מעקבים": "follows", "עוקבים חדשים": "follows",
    "profile_visits": "profile_visits", "profile visits": "profile_visits", "ביקורים בפרופיל": "profile_visits",
    "permalink": "permalink", "קישור": "permalink",
}
KPI_FIELDS = ["followers_total", "new_followers", "profile_visits", "sponsor_inquiries",
              "club_inquiries", "club_signups"]
PILLAR_HE = {"fighter": "לוחם", "coach": "מאמן", "club": "Team Moshe", "behind": "מאחורי הקלעים",
             "cta": "הנעה לפעולה", "": "לא מסווג"}


def norm(h):
    return re.sub(r"\s+", " ", (h or "").strip().lstrip("﻿").lower())


def to_num(v):
    if v is None:
        return None
    s = str(v).strip().replace(",", "")
    if s in ("", "-", "—", "n/a", "na"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


def to_date(v):
    s = (v or "").strip()
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)  # ISO, with or without time
    if m:
        return dt.date.fromisoformat(m.group(1))
    head = s.split(" ")[0]
    # Meta exports from US-locale accounts use M/D/Y; Israeli manual entry uses D.M.Y.
    for f in ("%m/%d/%Y", "%d.%m.%Y"):
        try:
            return dt.datetime.strptime(head, f).date()
        except ValueError:
            continue
    return None


def week_start(d):  # Israeli week: Sunday
    return d - dt.timedelta(days=(d.weekday() + 1) % 7)


def load_posts(folder):
    posts, unknown, files = [], set(), []
    for f in sorted(folder.glob("*.csv")):
        if f.name.startswith("weekly_kpis") or f.name.endswith("weekly_kpis.csv"):
            continue
        files.append(f.name)
        with f.open(encoding="utf-8-sig", newline="") as fh:
            rd = csv.DictReader(fh)
            mapping = {}
            for h in rd.fieldnames or []:
                c = COLUMN_ALIASES.get(norm(h))
                if c:
                    mapping[h] = c
                else:
                    unknown.add(h)
            for row in rd:
                p = {c: row[h] for h, c in mapping.items()}
                d = to_date(p.get("date"))
                if not d:
                    continue
                p["date"] = d
                for m in METRICS:
                    p[m] = to_num(p.get(m))
                p["format"] = (p.get("format") or "").strip().lower()
                p["pillar"] = (p.get("pillar") or "").strip().lower()
                posts.append(p)
    return posts, sorted(unknown), files


def load_kpis(folder):
    f = folder / ("sample_weekly_kpis.csv" if folder == SAMPLE else "weekly_kpis.csv")
    out = {}
    if f.exists():
        with f.open(encoding="utf-8-sig", newline="") as fh:
            for r in csv.DictReader(fh):
                d = to_date(r.get("week_start"))
                if d:
                    out[week_start(d)] = {k: to_num(r.get(k)) for k in KPI_FIELDS}
    return out


def crm_counts(ws, include_sample):
    """Counts inquiries/sign-ups logged in the CRM during the week."""
    we = ws + dt.timedelta(days=7)
    res = {"club_inquiries": 0, "club_signups": 0, "sponsor_inquiries": 0}
    f = CRM / "club_leads.csv"
    if f.exists():
        for r in csv.DictReader(f.open(encoding="utf-8")):
            if r.get("is_sample") == "yes" and not include_sample:
                continue
            d = to_date(r.get("date"))
            if d and ws <= d < we:
                res["club_inquiries"] += 1
                if r.get("status") == "joined":
                    res["club_signups"] += 1
    f = CRM / "sponsors.csv"
    if f.exists():
        for r in csv.DictReader(f.open(encoding="utf-8")):
            if r.get("is_sample") == "yes" and not include_sample:
                continue
            d = to_date(r.get("last_contact"))
            if d and ws <= d < we and r.get("status") in ("replied", "meeting", "won"):
                res["sponsor_inquiries"] += 1
    return res


def total(posts, m):
    vals = [p[m] for p in posts if p.get(m) is not None]
    return sum(vals) if vals else None


def score(p):
    reach = p.get("reach")
    if not reach:
        return None
    g = lambda k: p.get(k) or 0
    return (g("shares") * 3 + g("saves") * 2 + g("comments") + g("follows") * 4) / reach


def pct(a, b):
    if a is None or b in (None, 0):
        return None
    return (a - b) / b * 100


def fmt(v, d=0):
    if v is None:
        return "חסר"
    return f"{v:,.{d}f}"


def group(posts, key):
    g = defaultdict(list)
    for p in posts:
        g[p.get(key) or ""].append(p)
    rows = []
    for k, ps in g.items():
        sc = [s for s in (score(p) for p in ps) if s is not None]
        rows.append({"key": k, "posts": len(ps), "reach": total(ps, "reach"), "views": total(ps, "views"),
                     "avg_score": sum(sc) / len(sc) if sc else None})
    return sorted(rows, key=lambda r: r["avg_score"] or 0, reverse=True)


def recommendations(cur, prev, by_pillar, by_format, top):
    recs = []
    if len(cur) < 3:
        return [f"השבוע יש רק {len(cur)} פוסטים, וזה לא מספיק כדי להסיק מסקנות. כדאי להגיע ל-4 רילסים בשבוע לפני שמשנים כיוון."]
    scored = [r for r in by_pillar if r["avg_score"] is not None and r["key"]]
    if len(scored) >= 2:
        b, w = scored[0], scored[-1]
        recs.append(f"עמוד התוכן '{PILLAR_HE.get(b['key'], b['key'])}' הוביל במעורבות "
                    f"(ציון {b['avg_score']*100:.2f} מול {w['avg_score']*100:.2f} ב'{PILLAR_HE.get(w['key'], w['key'])}'). "
                    f"כדאי להוסיף פוסט אחד מהסוג הזה בשבוע הבא."
                    + (f" (זהירות: מבוסס על {b['posts']} פוסט בלבד.)" if b["posts"] < 2 else ""))
    if top:
        t = top[0]
        recs.append(f"הפוסט המוביל, '{t['title']}', הביא {fmt(t.get('shares'))} שיתופים ו-{fmt(t.get('saves'))} שמירות. "
                    f"כדאי לעשות לו המשך (חלק 2, או אותו הוק עם קטע אחר).")
    wt = [p["avg_watch_time_sec"] for p in cur if p.get("avg_watch_time_sec") is not None and p.get("format") == "reel"]
    if wt:
        avg = sum(wt) / len(wt)
        if avg < 8:
            recs.append(f"זמן הצפייה הממוצע ברילס הוא {avg:.1f} שניות. כדאי לקצר את הפתיחה ולשים את המכה החזקה ב-1.5 השניות הראשונות.")
    else:
        recs.append("אין נתוני זמן צפייה. כדי לקבל אותם צריך לחבר את ה-API או לייצא אותם מהאפליקציה.")
    fr = [r for r in by_format if r["avg_score"] is not None and r["key"]]
    if len(fr) >= 2:
        recs.append(f"לפי פורמט: '{fr[0]['key']}' מוביל (ציון {fr[0]['avg_score']*100:.2f}) מול '{fr[-1]['key']}' "
                    f"({fr[-1]['avg_score']*100:.2f}).")
    cf, pf = total(cur, "follows"), total(prev, "follows")
    ch = pct(cf, pf)
    if ch is not None and ch < -15:
        recs.append(f"מעקבים מפוסטים ירדו ב-{abs(ch):.0f}% לעומת השבוע הקודם. כדאי להוסיף CTA של 'תעקבו לחלק 2' בשני רילסים.")
    return recs[:5]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", action="store_true", help="use analytics/sample (clearly marked)")
    ap.add_argument("--week", help="week start (any date in the week), YYYY-MM-DD")
    a = ap.parse_args()
    folder = SAMPLE if a.sample else DATA
    posts, unknown, files = load_posts(folder)
    if not posts:
        print(f"אין נתונים ב-{folder.relative_to(ROOT)}. הוסף ייצוא Insights (CSV), או הרץ עם --sample לבדיקה.")
        sys.exit(2)
    ws = week_start(dt.date.fromisoformat(a.week)) if a.week else max(week_start(p["date"]) for p in posts)
    pws = ws - dt.timedelta(days=7)
    cur = [p for p in posts if week_start(p["date"]) == ws]
    prev = [p for p in posts if week_start(p["date"]) == pws]
    kpis = load_kpis(folder)
    kc, kp = dict(kpis.get(ws, {})), dict(kpis.get(pws, {}))
    crm = crm_counts(ws, include_sample=a.sample)
    for k, v in crm.items():
        if kc.get(k) is None and (v or folder == DATA):
            kc[k] = v
    for p in cur:
        p["score"] = score(p)
    top = sorted([p for p in cur if p["score"] is not None], key=lambda p: p["score"], reverse=True)[:3]
    by_pillar, by_format = group(cur, "pillar"), group(cur, "format")
    recs = recommendations(cur, prev, by_pillar, by_format, top)

    summary = []
    for m, label in [("views", "צפיות"), ("reach", "חשיפה (סכום לפי פוסט)"), ("shares", "שיתופים"),
                     ("saves", "שמירות"), ("follows", "עוקבים מפוסטים"), ("profile_visits", "כניסות לפרופיל (מפוסטים)")]:
        c, p_ = total(cur, m), total(prev, m)
        summary.append({"metric": m, "label": label, "current": c, "previous": p_ if prev else None,
                        "change_pct": pct(c, p_) if prev else None})
    wt = [p["avg_watch_time_sec"] for p in cur if p.get("avg_watch_time_sec") is not None]
    is_sample = folder == SAMPLE
    report = {
        "week_start": ws.isoformat(), "is_sample": is_sample, "source_files": files,
        "unrecognised_columns": unknown, "posts_count": len(cur), "prev_posts_count": len(prev),
        "summary": summary, "avg_watch_time_sec": (sum(wt) / len(wt)) if wt else None,
        "kpis": kc, "kpis_prev": kp,
        "top_posts": [{k: (v.isoformat() if isinstance(v, dt.date) else v) for k, v in p.items()} for p in top],
        "by_pillar": by_pillar, "by_format": by_format, "recommendations": recs,
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    stem = f"weekly_{ws.isoformat()}" + ("_SAMPLE" if is_sample else "")
    (REPORTS / f"{stem}.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, default=str), encoding="utf-8")

    we = ws + dt.timedelta(days=6)
    L = []
    if is_sample:
        L += ["> ⚠️ **נתוני דוגמה.** הדוח הזה נוצר מ-analytics/sample לצורך בדיקת המערכת. אין לצטט אותו.", ""]
    L += [f"# דוח שבועי: {ws:%d.%m} – {we:%d.%m.%Y}", "",
          f"פוסטים השבוע: **{len(cur)}** (שבוע קודם: {len(prev) if prev else 'אין נתונים'})", "",
          "## סיכום", "| מדד | השבוע | שבוע קודם | שינוי |", "|---|---|---|---|"]
    for s in summary:
        ch = "" if s["change_pct"] is None else f"{s['change_pct']:+.0f}%"
        L.append(f"| {s['label']} | {fmt(s['current'])} | {fmt(s['previous']) if prev else 'אין'} | {ch} |")
    L.append(f"| זמן צפייה ממוצע (רילס) | {fmt(report['avg_watch_time_sec'], 1) + ' שנ׳' if wt else 'לא זמין'} | | |")
    L += ["", "## מדדי חשבון ופניות", "| מדד | השבוע | שבוע קודם |", "|---|---|---|"]
    names = {"followers_total": "סה\"כ עוקבים", "new_followers": "עוקבים חדשים", "profile_visits": "כניסות לפרופיל",
             "sponsor_inquiries": "פניות מספונסרים", "club_inquiries": "פניות למכון", "club_signups": "הרשמות למכון"}
    for k in KPI_FIELDS:
        L.append(f"| {names[k]} | {fmt(kc.get(k))} | {fmt(kp.get(k))} |")
    L += ["", "## התכנים המובילים (ציון מעורבות)",
          "ציון = (שיתופים×3 + שמירות×2 + תגובות + מעקבים×4) ÷ חשיפה", "",
          "| # | תאריך | פוסט | צפיות | חשיפה | שיתופים | שמירות | ציון |", "|---|---|---|---|---|---|---|---|"]
    for i, p in enumerate(top, 1):
        L.append(f"| {i} | {p['date']:%d.%m} | {p.get('title') or p.get('post_id')} | {fmt(p.get('views'))} | "
                 f"{fmt(p.get('reach'))} | {fmt(p.get('shares'))} | {fmt(p.get('saves'))} | {p['score']*100:.2f} |")
    L += ["", "## לפי עמוד תוכן", "| עמוד | פוסטים | חשיפה | ציון ממוצע |", "|---|---|---|---|"]
    for r in by_pillar:
        L.append(f"| {PILLAR_HE.get(r['key'], r['key'])} | {r['posts']} | {fmt(r['reach'])} | "
                 f"{'' if r['avg_score'] is None else f'{r['avg_score']*100:.2f}'} |")
    L += ["", "## המלצות לשבוע הבא (מבוססות נתונים)"] + [f"{i}. {r}" for i, r in enumerate(recs, 1)]
    if unknown:
        L += ["", f"_עמודות שלא זוהו ולא נכללו: {', '.join(unknown)}_"]
    L += ["", f"_מקור: {', '.join(files)}_"]
    (REPORTS / f"{stem}.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote analytics/reports/{stem}.md")


if __name__ == "__main__":
    main()
