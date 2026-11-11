# Fight Performance AI - שלב 1: חיבור ל-WHOOP

מערכת אישית לניתוח כושר לקראת קרבות קיקבוקסינג ומואי תאי, מבוססת על ה-API הרשמי של WHOOP (v2).
**שלב זה כולל רק את החיבור ובדיקת משיכת הנתונים.** שאר המערכת תיבנה אחרי אישור שהחיבור עובד.

## 1. יצירת אפליקציה ב-WHOOP (חד-פעמי)
1. היכנסו ל-<https://developer-dashboard.whoop.com> עם חשבון ה-WHOOP שלכם וצרו Team ואז App.
2. Scopes: סמנו `read:recovery`, `read:cycles`, `read:sleep`, `read:workout`, `read:profile`, `read:body_measurement`
   (וגם `offline`, אם הוא מופיע כאפשרות).
3. Redirect URI: `http://localhost:8765/callback`
4. שמרו את ה-Client ID וה-Client Secret. **אל תדביקו את ה-Secret בצ'אט ואל תכניסו אותו לקוד.**

## 2. שמירת פרטי הגישה (מחוץ לריפו)
אחת מהאפשרויות:
- `python3 fpai.py setup` - שומר ב-`~/.config/fight-performance-ai/client.json` עם הרשאות 600 (ה-Secret מוקלד בלי להיות מוצג).
- משתני סביבה: `WHOOP_CLIENT_ID`, `WHOOP_CLIENT_SECRET` (ואופציונלית `WHOOP_REDIRECT_URI`).

## 3. התחברות
- **על המחשב שלכם:** `python3 fpai.py login` - הדפדפן נפתח, מאשרים, והחיבור נקלט אוטומטית.
- **מסשן ענן:** `python3 fpai.py start`, פותחים את הכתובת ומאשרים. הדפדפן יעבור ל-`localhost` ולא ייטען (זה תקין).
  מעתיקים את הכתובת המלאה משורת הכתובת ומריצים `python3 fpai.py finish "<URL>"`.

## 4. בדיקה
```
python3 fpai.py status
python3 fpai.py test --days 30     # או --all לכל ההיסטוריה
```
הבדיקה מציגה לכל סוג נתון כמה רשומות התקבלו, את טווח התאריכים, את `score_state`, ובכמה רשומות כל מדד קיים בפועל.

## אבטחה
- טוקנים ונתונים גולמיים נשמרים ב-`~/.config/fight-performance-ai/` (הרשאות 600/700), לא בריפו.
- `state` אקראי (8 תווים) נבדק מול הערך שנשמר, כהגנה מפני CSRF. ניסיון התחברות פג אחרי 15 דקות.
- WHOOP מחליף את ה-refresh token בכל רענון, והקוד שומר תמיד את החדש.
- `python3 fpai.py logout` מבטל את הגישה אצל WHOOP ומוחק את הטוקנים.

## מה ה-API מספק ומה לא
| קיים | לא קיים |
|---|---|
| Recovery %, HRV (rMSSD), דופק מנוחה, SpO2, טמפ' עור | דופק רציף / שנייה-אחר-שנייה |
| שינה: שלבים, ביצועים, יעילות, עקביות, קצב נשימה, חוב שינה | VO2max, HRR בין סיבובים |
| Strain יומי, דופק ממוצע/מקסימלי, קילוג'אול | |
| אימונים: סוג, Strain, דופק ממוצע/מקס', זמן בכל אזור דופק, מרחק | |
