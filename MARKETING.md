# OR MOSHE BRAND: מערכת השיווק

מערכת שיווק אישית לאור משה ול-Team Moshe, שפועלת בתוך Claude Code.

## איך משתמשים
כתוב ב-Claude Code:
```
/or-moshe-marketing
```
או פשוט בקש בשפה רגילה: "תכין לי תוכן לשבוע הבא", "ערוך לי רילס מקטעי GFN", "תכין מדיה קיט", "דוח שבועי".
הסקיל (`.claude/skills/or-moshe-marketing/SKILL.md`) מנתב כל בקשה לתהליך המתאים.

## מבנה
```
.claude/skills/or-moshe-marketing/
  SKILL.md                 מנהל השיווק: כללים, ניתוב, מצב ברירת מחדל
  workflows/               תהליך לכל תחום (תוכן, רילס, קריירה, מכון, ניתוח, חיבורים)
  templates/               תבניות: תיק ספורטאי, מדיה קיט, הצעת חסות, פניות, קמפיין מכון
brand/                     פרופיל, הישגים (עם סטטוס אימות), טון, קהלים
marketing/                 תוכנית 30 יום, לוח תוכן (CSV), משימות
crm/                       ספונסרים, ארגונים, פניות למכון, הסכמות צילום
analytics/
  data/                    נתוני Insights אמיתיים (ריק עד ייצוא או חיבור)
  sample/                  נתוני דוגמה בלבד, לבדיקה
  reports/                 דוחות שבועיים
dashboard/                 ממשק ניהול (index.html), מותאם לאייפון
tools/                     סקריפטים: דוח, דשבורד, בדיקות, Instagram API, עריכת רילס
docs/CONNECTIONS.md        מצב החיבורים והוראות הגדרה מאובטחות
```

## פקודות
| פעולה | פקודה |
|---|---|
| בדיקת תקינות | `python3 tools/validate.py` |
| דוח שבועי | `python3 tools/weekly_report.py` (או `--sample`) |
| עדכון הדשבורד | `python3 tools/build_dashboard.py`, ואז לפתוח את `dashboard/index.html` |
| בדיקת כלי וידאו | `bash tools/reels/check_tools.sh` |
| מלאי סרטונים | `python3 tools/reels/inventory.py promo/raw` |
| רינדור רילס מ-EDL | `python3 tools/reels/render_edl.py reels/edl/<name>.json` |
| גרסאות לפלטפורמות | `bash tools/reels/make_variants.sh reels/out/<name>.mp4` |
| Instagram API | `python3 tools/fetch_instagram.py --check` |

## כללים
- שום פרסום, הודעה לספונסר או לארגון, מודעה בתשלום או שינוי בדרייב, בלי אישור מפורש של אור.
- לא ממציאים נתונים, תארים או תוצאות. נתוני דוגמה מסומנים "[דוגמה]".
- תארים רק מ-`brand/achievements.json`. כרגע **אף תואר עדיין לא אומת**.
- ילדים בתוכן: רק עם הסכמה ב-`crm/media_consents.csv`.
