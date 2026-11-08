# תהליך: קידום קריירת הלחימה

## עיקרון
כל חומר שיוצא החוצה (לארגון, למאצ'מייקר, לספונסר, לעיתונאי) הוא **טיוטה** עד שאור מאשר. תארים רק מ-`brand/achievements.json`. מה שלא מאומת מסומן "⚠️ לאמת".

## תוצרים ותבניות
| תוצר | תבנית | יעד |
|---|---|---|
| תיק ספורטאי (עברית + אנגלית) | `templates/athlete-profile.md` | `marketing/out/athlete_profile_<lang>.md` (ואז PDF) |
| Media Kit לספונסרים | `templates/media-kit.md` | `marketing/out/media_kit.md` |
| הצעת חסות | `templates/sponsor-proposal.md` | `marketing/out/proposal_<sponsor>.md` |
| פנייה למאצ'מייקר/ארגון | `templates/outreach-messages.md` | טיוטה בצ'אט ושורה ב-`crm/promotions.csv` |
| Highlight | `workflows/reels-editing.md` | `reels/out/highlight_*.mp4` |

PDF: אחרי אישור התוכן, אפשר להמיר עם סקיל ה-PDF או עם Playwright מ-HTML.

## מדיה קיט: מה חייב להיות
1. מי זה אור, בשתי שורות
2. הישגים מאומתים (מקסימום 6, החזקים ביותר)
3. נתוני קהל: **רק מנתונים אמיתיים** מ-`analytics/data/`. אם אין, כתוב "יעודכן לאחר חיבור Insights" ואל תשים מספרים.
4. קהל היעד: מי עוקב (גיל/מיקום, אם יש נתונים), חברי המועדון, אירועים
5. חבילות חסות (Bronze / Silver / Gold). מחירים רק אחרי שאור קבע אותם; עד אז "לפי סיכום".
6. מה הספונסר מקבל: לוגו על המכנסיים/החולצה, אזכורים, תוכן ייעודי, נוכחות במכון, הופעה באירוע
7. יצירת קשר

## אסטרטגיית חשיפה בינלאומית
- רשימת יעד ב-`crm/promotions.csv`. ארגונים לבדיקה: ONE Championship, GLORY, Enfusion, Kunlun Fight, Superbon/Rajadamnern World Series, Thai Fight, ARENA, וקידומים אירופאיים. **לפני פנייה: לאמת איש קשר וערוץ רשמי** (אתר רשמי/אינסטגרם מאומת). אל תנחש כתובות מייל.
- נכסים: Highlight באנגלית, רקורד מסודר (W-L-D לפי שנה ותחרות, רק אחרי אימות), תמונות מקצועיות, משקל ושכבת משקל, זמינות.
- תוכן באנגלית 1–2 פעמים בשבוע, תיוג ארגונים ולוחמים אחרי קרבות אמיתיים בלבד.
- מעקב: כל פנייה היא שורה ב-CRM עם `status` ו-`next_followup` (תזכורת אחרי 7–10 ימים, מקסימום 2 תזכורות).

## עבודה עם ה-CRM
`crm/sponsors.csv` ו-`crm/promotions.csv`:
`status`: `research` → `draft` → `approved_to_send` → `sent` → `replied` → `meeting` → `won` / `lost` / `no_reply`
- אתה מעדכן ל-`draft` ומציג את ההודעה.
- רק אחרי "מאשר" מאור: `approved_to_send`. השליחה עצמה נעשית על ידי אור, או דרך כלי מחובר אחרי אישור נוסף לשליחה הספציפית.
- תשובות שאור מדביק: עדכן `last_contact`, `status`, `notes`.
