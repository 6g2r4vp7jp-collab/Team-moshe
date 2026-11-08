# תהליך: חיבורים חיצוניים

**לעולם אל תניח שחיבור קיים. בדוק בכל הפעלה.** המצב המלא וההוראות נמצאים ב-`docs/CONNECTIONS.md`.

## בדיקה מהירה
| חיבור | איך בודקים |
|---|---|
| Google Drive | חפש כלי `mcp__Google_Drive__search_files` (דרך ToolSearch). אם קיים, חפש את התיקייה `Team Moshe` |
| Instagram / Meta Graph API | `python3 tools/fetch_instagram.py --check` (בודק אם הוגדר טוקן דרך פרוקסי או משתנה סביבה, בלי להדפיס אותו) |
| כלי וידאו | `bash tools/reels/check_tools.sh` |
| גיליונות | Google Drive MCP יכול ליצור Google Sheets; מקומית יש pandas ו-openpyxl |
| תזמון ופרסום | אין חיבור. פרסום ידני דרך Meta Business Suite או האפליקציה |

## חוקים
- חיבור חדש = שאל את אור קודם, והסבר מה החיבור יכול לעשות ומה לא.
- הרשאות מינימליות: לקריאת Insights מספיקים `instagram_basic`, `instagram_manage_insights`, `pages_show_list`, `pages_read_engagement`. **לא** מבקשים `instagram_content_publish` או `ads_management` עד שאור מחליט שהוא רוצה פרסום/מודעות דרך המערכת.
- טוקנים: רק דרך מנגנון הסודות של הסביבה (בענן: network secret ל-`graph.facebook.com`; מקומית: משתנה סביבה או קובץ `.env` שמופיע ב-`.gitignore`). אף פעם לא בצ'אט ולא בקובץ בגיט.
- בדרייב: קריאה והורדה מותרות למשימות שאור ביקש. יצירה, שינוי, שיתוף ומחיקה רק באישור.
