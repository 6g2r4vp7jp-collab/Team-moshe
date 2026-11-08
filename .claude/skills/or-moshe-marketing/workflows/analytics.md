# תהליך: ניתוח ביצועים ודוח שבועי

## מקורות נתונים (לפי סדר עדיפות)
1. **Instagram Graph API** (אחרי חיבור מורשה, ראה `workflows/connections.md`): `python3 tools/fetch_instagram.py`, שכותב ל-`analytics/data/`.
2. **ייצוא CSV ידני:** Meta Business Suite → Insights → Content → Export, או Professional Dashboard. שומרים ב-`analytics/data/`.
3. **הזנה ידנית:** אור כותב את המספרים, ואתה מכניס אותם לקובץ CSV לפי התבנית `analytics/insights_template.csv`.

`analytics/sample/` מכיל **נתוני דוגמה בלבד** לבדיקת המערכת. אסור לצטט אותם כנתונים אמיתיים.

## עמודות (תבנית `analytics/insights_template.csv`)
`date,post_id,format,pillar,title,views,reach,avg_watch_time_sec,likes,comments,shares,saves,follows,profile_visits`
ובקובץ נפרד `analytics/data/weekly_kpis.csv`:
`week_start,followers_total,new_followers,profile_visits,sponsor_inquiries,club_inquiries,club_signups`

שמות עמודות מיצוא של Meta (באנגלית או בעברית) ממופים אוטומטית ב-`tools/weekly_report.py` (טבלת `COLUMN_ALIASES`). עמודה שלא זוהתה מדווחת ולא מנוחשת.

## הרצה
```
python3 tools/weekly_report.py                       # נתונים אמיתיים מ-analytics/data
python3 tools/weekly_report.py --sample              # נתוני דוגמה (הדוח מסומן כדוגמה)
python3 tools/weekly_report.py --week 2026-11-01     # שבוע מסוים
```
פלט: `analytics/reports/weekly_<week>.md`, וגם `dashboard/data.js` מתעדכן בבנייה הבאה.

## מה הדוח עושה
- סיכום שבוע מול שבוע קודם (רק אם יש לשניהם נתונים)
- 3 התכנים המובילים לפי ציון מעורבות משוקלל: `(shares*3 + saves*2 + comments + follows*4) / reach`
- ביצועים לפי עמוד תוכן ולפי פורמט
- זמן צפייה: אם חסר, כתוב "לא זמין". לא מחשבים מספר במקומו.
- המלצות: כל המלצה מצוטטת עם הנתון שמאחוריה. אם יש פחות מ-3 פוסטים בשבוע, הדוח אומר שאין מספיק נתונים להסקה.

## כשאתה מציג את הדוח לאור
1. שורה אחת: מה הכי עבד השבוע ולמה (לפי הנתונים).
2. 2–3 המלצות לשבוע הבא, כל אחת עם הנתון שמאחוריה.
3. מה חסר כדי לדעת יותר (למשל: "אין נתוני זמן צפייה, מומלץ לחבר API").
