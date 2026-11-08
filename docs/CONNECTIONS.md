# חיבורים חיצוניים: מצב והוראות הגדרה

**נבדק:** 8.11.2026, בסשן הענן של Claude Code.

| חיבור | מצב | מה אפשר לעשות היום |
|---|---|---|
| **Google Drive** | ✅ מחובר (מחבר Google Drive של claude.ai, החשבון של אור) | התיקייה "Team Moshe" נמצאה: 3 סרטוני MOV (אחד מהם 965MB) ו-2 קובצי MP3. קריאה והורדה לעריכה. **אין** מחיקה, שינוי או שיתוף בלי אישור |
| **Instagram / Meta Graph API** | ❌ לא מחובר | ייצוא CSV ידני ל-`analytics/data/`. ההגדרה מתוארת בהמשך |
| **כלי וידאו** | ✅ FFmpeg 6.1 (libass, fribidi, harfbuzz, x264), ImageMagick, Node 22, Playwright | עריכה מלאה כולל כתוביות בעברית. אין צורך בהתקנה |
| **גיליונות** | ✅ חלקי: pandas ו-openpyxl מקומית; יצירת Google Sheets אפשרית דרך מחבר הדרייב | ה-CRM הוא CSV בפרויקט. אפשר להעביר ל-Google Sheets פרטי (באישור) |
| **פרסום ותזמון** | ❌ אין | פרסום ידני דרך Meta Business Suite או האפליקציה |

> ⚠️ **מוזיקה בדרייב:** בתיקייה יש קובץ "Interstellar – Cornfield Chase (Hans Zimmer)". זו מוזיקה מוגנת בזכויות יוצרים. אסור להשתמש בה במודעות ממומנות או בחומר לספונסרים, וגם ברילס אורגני היא עלולה להיחסם או להשתיק את הסרטון. ההמלצה: לבחור את השיר מתוך ספריית אינסטגרם בזמן ההעלאה, או להשתמש בפסקול המקורי שנוצר בקוד (`promo/README.md`).

---

## Instagram Insights: שתי דרכים

### דרך א': ייצוא CSV (בלי שום חיבור, אפשר כבר היום)
1. Meta Business Suite → **Insights** → **Content** → בוחרים טווח (7 או 28 ימים) → **Export data** → CSV.
2. שומרים את הקובץ ב-`analytics/data/` (למשל `posts_2026-11-08.csv`).
3. מדדים שבועיים (עוקבים, כניסות לפרופיל) ממלאים ב-`analytics/data/weekly_kpis.csv`.
4. `python3 tools/weekly_report.py`. הסקריפט ממפה אוטומטית שמות עמודות באנגלית ובעברית.

### דרך ב': Graph API (אוטומטי, קריאה בלבד)
**דרישות:** חשבון אינסטגרם מקצועי (Business או Creator) שמקושר לעמוד פייסבוק.

1. https://developers.facebook.com → **My Apps** → **Create App** → סוג **Business**.
2. מוסיפים את המוצר **Instagram Graph API** (Instagram API with Facebook Login).
3. ב-**Graph API Explorer** בוחרים את האפליקציה ומבקשים **רק** את ההרשאות:
   `instagram_basic`, `instagram_manage_insights`, `pages_show_list`, `pages_read_engagement`.
   **לא** לבקש `instagram_content_publish` או `ads_management`. אין בהן צורך לקריאת נתונים, והן מאפשרות פעולות חיצוניות.
4. מייצרים **Long-lived token** (60 יום), או עדיף **System User token** ב-Business Settings, שלא פג מהר.
5. מוצאים את `IG_USER_ID`: ב-Explorer שולחים `GET /me/accounts?fields=instagram_business_account`.
6. **שמירת הטוקן באופן מאובטח, לעולם לא בצ'אט ולא בגיט:**
   - **בסשן ענן של Claude Code:** תגיד לי "חבר אינסטגרם". אציג טופס מאובטח ששומר את הטוקן כ-network secret עבור `graph.facebook.com`. אני לא רואה את הערך. אחר כך מגדירים `IG_USER_ID` ו-`IG_TOKEN_VIA_PROXY=1` כמשתני סביבה (לא סודיים).
   - **במחשב מקומי:** קובץ `.env` בשורש הפרויקט (כבר ב-`.gitignore`):
     ```
     IG_USER_ID=1784...
     IG_ACCESS_TOKEN=EAA...
     ```
7. בדיקה: `python3 tools/fetch_instagram.py --check`. משיכה: `python3 tools/fetch_instagram.py --days 14`.

## Google Sheets (אופציונלי)
אם תרצה CRM שאפשר לערוך מהטלפון: באישורך אצור Google Sheet פרטי בדרייב שלך עם הלשוניות ספונסרים, ארגונים, פניות למכון והסכמות. הגיליון לא ישותף עם אף אחד. הקבצים בפרויקט יישארו הגיבוי.

## כלי תזמון (אופציונלי, החלטה שלך)
| כלי | יתרון | הערה |
|---|---|---|
| Meta Business Suite | חינם, רשמי, מתזמן רילס וסטוריז | מומלץ להתחלה |
| Later / Metricool / Buffer | לוח ויזואלי, טיקטוק | בתשלום. חיבור ל-Claude רק דרך API או MCP, אחרי אישור |

בכל מקרה, **אני לא מפרסם ולא מתזמן בלי אישור מפורש לכל פרסום.**

## הדשבורד באייפון
`dashboard/index.html` הוא קובץ סטטי. אפשרויות:
1. **קישור פרטי ב-claude.ai** (Artifact פרטי, נפתח באייפון). אני מפרסם רק אם תבקש.
2. GitHub Pages פרטי, או כל אחסון סטטי.
3. פתיחה מקומית במחשב.
