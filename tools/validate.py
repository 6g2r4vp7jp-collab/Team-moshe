#!/usr/bin/env python3
"""Sanity checks for the OR MOSHE BRAND marketing system. Exit 1 on any error.

Checks: SKILL.md frontmatter, referenced workflow/template files exist, CSV headers and
status values, achievements JSON, no secrets committed, sample data is flagged.
"""
import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".claude" / "skills" / "or-moshe-marketing"
errors, warnings = [], []

CSV_SCHEMAS = {
    "marketing/content_calendar.csv": (["date", "platform", "format", "pillar", "title", "hook", "caption_he", "caption_en", "cta", "assets", "status", "notes"],
                                       {"status": {"idea", "draft", "ready", "approved", "published"}}),
    "marketing/tasks.csv": (["due", "area", "task", "owner", "status", "needs_approval", "notes"],
                            {"status": {"open", "done"}, "needs_approval": {"yes", "no"}}),
    "crm/sponsors.csv": (["company", "category", "contact_name", "contact_channel", "status", "package", "value", "last_contact", "next_followup", "notes", "is_sample"],
                         {"status": {"research", "draft", "approved_to_send", "sent", "replied", "meeting", "won", "lost", "no_reply"}}),
    "crm/promotions.csv": (["organization", "country", "type", "contact_name", "contact_channel", "verified_contact", "status", "weight_class", "last_contact", "next_followup", "notes", "is_sample"],
                           {"status": {"research", "draft", "approved_to_send", "sent", "replied", "meeting", "won", "lost", "no_reply"}}),
    "crm/club_leads.csv": (["date", "name", "phone_or_handle", "source", "age_group", "program", "status", "trial_date", "next_followup", "notes", "consent_media", "is_sample"],
                           {"status": {"new", "contacted", "trial_booked", "trial_done", "joined", "not_now", "lost"}}),
    "crm/media_consents.csv": (["name", "is_minor", "guardian_name", "consent_date", "scope", "expires", "notes"], {}),
    "analytics/insights_template.csv": (["date", "post_id", "format", "pillar", "title", "views", "reach", "avg_watch_time_sec", "likes", "comments", "shares", "saves", "follows", "profile_visits"], {}),
}
DATE_COLS = {"date", "due", "last_contact", "next_followup", "trial_date", "consent_date", "expires"}


def check_skill():
    f = SKILL / "SKILL.md"
    if not f.exists():
        errors.append("SKILL.md missing")
        return
    text = f.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        errors.append("SKILL.md: no YAML frontmatter")
        return
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    if fm.get("name") != "or-moshe-marketing":
        errors.append(f"SKILL.md: name must be 'or-moshe-marketing' (got {fm.get('name')!r})")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", fm.get("name", "")):
        errors.append("SKILL.md: name must be lowercase letters, digits, hyphens")
    desc = fm.get("description", "")
    if not desc:
        errors.append("SKILL.md: description missing")
    elif len(desc) > 1024:
        errors.append(f"SKILL.md: description is {len(desc)} chars (max 1024)")
    for ref in sorted(set(re.findall(r"`((?:workflows|templates)/[\w./-]+\.md)`", text))):
        if not (SKILL / ref).exists():
            errors.append(f"SKILL.md references missing file {ref}")
    for wf in (SKILL / "workflows").glob("*.md"):
        for ref in set(re.findall(r"`(templates/[\w.-]+\.md)`", wf.read_text(encoding="utf-8"))):
            if not (SKILL / ref).exists():
                errors.append(f"{wf.name} references missing {ref}")
        for ref in set(re.findall(r"`((?:tools|brand|crm|marketing|analytics|docs)/[\w./-]+\.(?:py|sh|md|csv|json))`", wf.read_text(encoding="utf-8"))):
            is_output = ref.startswith(("analytics/data/", "analytics/reports/", "marketing/out/", "reels/out/"))
            if not is_output and not (ROOT / ref).exists() and "<" not in ref and "*" not in ref:
                errors.append(f"{wf.name} references missing {ref}")


def check_csvs():
    import datetime as dt
    for rel, (cols, enums) in CSV_SCHEMAS.items():
        f = ROOT / rel
        if not f.exists():
            errors.append(f"{rel} missing")
            continue
        with f.open(encoding="utf-8-sig", newline="") as fh:
            rd = csv.reader(fh)
            header = next(rd, [])
            if header != cols:
                errors.append(f"{rel}: header mismatch\n    expected {cols}\n    got      {header}")
                continue
            for n, row in enumerate(rd, 2):
                if len(row) != len(cols):
                    errors.append(f"{rel}:{n}: {len(row)} fields, expected {len(cols)} (unquoted comma?)")
                    continue
                r = dict(zip(cols, row))
                for k, allowed in enums.items():
                    if r[k] and r[k] not in allowed:
                        errors.append(f"{rel}:{n}: {k}={r[k]!r} not in {sorted(allowed)}")
                for k in DATE_COLS & set(cols):
                    if r[k]:
                        try:
                            dt.date.fromisoformat(r[k])
                        except ValueError:
                            errors.append(f"{rel}:{n}: {k}={r[k]!r} is not YYYY-MM-DD")
                if "is_sample" in r and "[דוגמה]" in json.dumps(r, ensure_ascii=False) and r["is_sample"] != "yes":
                    errors.append(f"{rel}:{n}: row looks like sample data but is_sample != yes")


def check_achievements():
    f = ROOT / "brand" / "achievements.json"
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        errors.append(f"achievements.json: {e}")
        return
    for a in data["achievements"]:
        for k in ("id", "title_he", "title_en", "verified"):
            if k not in a:
                errors.append(f"achievements.json: {a.get('id')} missing {k}")
        if a.get("verified") and not a.get("source"):
            errors.append(f"achievements.json: {a['id']} is verified but has no source")
    unv = [a["id"] for a in data["achievements"] if not a.get("verified")]
    if unv:
        warnings.append(f"{len(unv)} achievements not verified yet: {', '.join(unv)}")


def check_secrets():
    pat = re.compile(r"(EAA[A-Za-z0-9]{40,}|IGQV[A-Za-z0-9_-]{40,}|ya29\.[A-Za-z0-9_-]{30,}|AIza[0-9A-Za-z_-]{35})")
    for f in ROOT.rglob("*"):
        if f.is_file() and ".git" not in f.parts and f.suffix in {".md", ".csv", ".json", ".py", ".js", ".sh", ".txt", ".html", ".env"} and f.stat().st_size < 2_000_000:
            if pat.search(f.read_text(encoding="utf-8", errors="ignore")):
                errors.append(f"possible access token in {f.relative_to(ROOT)}")


def check_data_folder():
    for f in (ROOT / "analytics" / "data").glob("*.csv"):
        if "SAMPLE" in f.read_text(encoding="utf-8", errors="ignore") or "[דוגמה]" in f.read_text(encoding="utf-8", errors="ignore"):
            errors.append(f"analytics/data/{f.name} contains sample markers. Sample data belongs in analytics/sample/")


def main():
    check_skill()
    check_csvs()
    check_achievements()
    check_secrets()
    check_data_folder()
    for w in warnings:
        print("⚠️ ", w)
    for e in errors:
        print("❌", e)
    if errors:
        sys.exit(1)
    print("✅ all checks passed")


if __name__ == "__main__":
    main()
