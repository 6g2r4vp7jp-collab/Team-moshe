"""Generates the initial 30-day content calendar (marketing/content_calendar.csv).

Run once; afterwards edit the CSV directly (or via the skill). Re-running overwrites it,
so it refuses to run if the file exists unless --force is given.
"""
import csv
import datetime as dt
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "marketing" / "content_calendar.csv"
START = dt.date(2026, 11, 9)  # Monday, day 1 of the plan

FIELDS = ["date", "platform", "format", "pillar", "title", "hook", "caption_he",
          "caption_en", "cta", "assets", "status", "notes"]

# (day offset, platform, format, pillar, title, hook, caption_he, caption_en, cta, assets, status, notes)
ITEMS = [
    # Week 1: foundations
    (0, "instagram", "story", "behind", "סקר: מה אתם רוצים לראות?", "סקר 4 אפשרויות",
     "מה בא לכם לראות פה יותר?", "", "הצבעה בסקר", "תמונה מהמכון", "idea", "נותן נתון על הקהל"),
    (1, "instagram", "reel", "fighter", "סרטון התדמית הרשמי", "אור בהילוך איטי בזירה, 'אור משה'",
     "15 שנה. מעל 200 קרבות. וזה רק החלק שרואים.", "15 years. 200+ fights. This is the part you see.",
     "תעקבו, יש עוד", "promo/final/TEAM_MOSHE_promo_HD_your_music.mp4", "ready",
     "מוזיקה: לבחור מספריית אינסטגרם בהעלאה, או גרסת v31 שקטה + שיר מהספרייה"),
    (2, "instagram", "carousel", "fighter", "ההישגים שלי, שקופית לכל תואר", "שקופית 1: '18'",
     "18 פעמים אלוף ישראל. אבל השקופית האחרונה היא החשובה באמת →", "",
     "שמרו", "תמונות פודיום מהדרייב", "idea", "⚠️ לאמת תארים לפני פרסום"),
    (3, "instagram", "reel", "coach", "טיפ: הטעות שכולם עושים בלו קיק", "'אתה בועט עם הרגל הלא נכונה'",
     "רוב המתחילים בועטים עם הכף. ככה זה צריך להיראות.", "Most beginners kick with the foot. Here's the fix.",
     "שמרו לאימון הבא", "צריך לצלם: 3 שוטים במכון", "idea", ""),
    (4, "instagram", "story", "club", "יום במכון", "6 פריימים: מהבוקר עד אימון הערב",
     "", "", "שאלה: 'מה הייתם רוצים לשאול מאמן?'", "צריך לצלם", "idea", "ילדים רק עם הסכמה"),
    (5, "instagram", "reel", "fighter", "GFN: הקרב בהיכל מנורה", "המכה הכי חזקה מהקרב, הילוך איטי",
     "היכל מנורה. GFN. הרגע שבו הקהל קם.", "Menora Arena. GFN.", "תתייגו מישהו שהיה שם",
     "Drive: Team Moshe (קטעי GFN)", "idea", "⚠️ לאמת שם האירוע, תאריך ותוצאה"),
    # Week 2: fighter authority + English
    (7, "instagram", "reel", "fighter", "ברכיים: הנשק שלי", "ברך מעופפת בהילוך איטי, 0:00",
     "אם הייתי צריך לבחור מכה אחת לכל החיים: ברך.", "If I had to pick one weapon for life: the knee.",
     "תעקבו", "Drive: IMG_7991.MOV + קטעי אליפות אירופה", "idea", "רילס עריכה לפי workflows/reels-editing.md"),
    (8, "instagram", "story", "behind", "שאלות ותשובות", "סטיקר שאלה: 'תשאלו אותי הכל על קרבות'",
     "", "", "", "", "idea", ""),
    (9, "instagram", "carousel", "coach", "5 דברים שלמדתי ב-200 קרבות", "'200 קרבות. 5 שיעורים.'",
     "5 דברים שלמדתי ב-200 קרבות. מספר 4 כאב הכי הרבה.", "5 lessons from 200 fights.",
     "שמרו ושתפו", "טקסט על רקע שחור-זהב", "idea", ""),
    (10, "instagram", "reel", "fighter", "Highlight באנגלית (גרסה ל-IG)", "הקומבינציה הכי טובה, 0:00",
     "", "Or Moshe | Muay Thai | Israel. Available for fights. DM for bookings.",
     "DM for bookings", "reels/out/highlight_9x16.mp4 (ייווצר)", "idea", "קהל: ארגונים בחו\"ל"),
    (12, "instagram", "reel", "behind", "יום לפני קרב / חיתוך משקל", "'נשארו לי 1.2 קילו ו-14 שעות'",
     "מה שלא רואים ביום לפני.", "The part nobody films.", "תעקבו לקרב הבא",
     "צריך לצלם (לפני הקרב הבא)", "idea", "אם אין קרב קרוב: להחליף ברילס אימון"),
    # Week 3: club recruitment
    (14, "instagram", "reel", "club", "הילדים של Team Moshe", "ילד בן 8 עושה קומבינציה מושלמת",
     "ילד שמתאמן לא מחפש מכות. הוא פשוט מפסיק לפחד.", "", "אימון ניסיון לילדים: הודעה",
     "צריך לצלם", "idea", "רק ילדים עם הסכמה ב-crm/media_consents.csv"),
    (15, "instagram", "story", "club", "מה קורה באימון ניסיון", "5 פריימים: מגיעים, חימום, פדים, סיום, חיוך",
     "", "", "קישור לוואטסאפ", "", "idea", ""),
    (16, "instagram", "carousel", "club", "שאלות של הורים", "'האם זה אלים?'",
     "השאלות ששואלים אותי הכי הרבה הורים, והתשובות הכנות.", "", "שלחו 'ניסיון'", "", "idea", ""),
    (17, "instagram", "reel", "club", "אף פעם לא מאוחר: מבוגרים מתחילים", "מתאמן בן 40 בפעם הראשונה מול מתאמן אחרי שנה",
     "אף פעם לא התאמנת? מעולה. ככה כולם התחילו.", "", "שלחו 'ניסיון'", "צריך לצלם (באישור המתאמן)", "idea", ""),
    (19, "instagram", "reel", "coach", "תרגיל לבית: 3 דקות", "'אין לך שק? אין בעיה'",
     "3 דקות, בלי ציוד. תעשו את זה הערב.", "3 minutes, no equipment.", "שמרו", "צריך לצלם", "idea", ""),
    (19, "facebook", "post", "club", "פוסט קהילתי לקבוצות היישובים", "",
     "שלום שכנים, אני אור מ-Team Moshe בלוחמי הגטאות...", "", "אימון ניסיון", "", "idea",
     "אור מפרסם בעצמו, אחרי אישור הנוסח"),
    # Week 4: sponsors + push
    (21, "instagram", "reel", "fighter", "קומבינציות סיום", "3 סיומים ב-10 שניות",
     "", "Finishers.", "תעקבו", "Drive: קטעי קרבות", "idea", "לא להכניס קטעים שבהם אור מופל"),
    (22, "instagram", "story", "behind", "תודה לשותפים / ציוד", "", "", "", "", "", "idea", "רק אם יש שותף אמיתי"),
    (23, "instagram", "carousel", "fighter", "הדרך: מגיל X עד היום", "תמונה ראשונה מגיל צעיר",
     "", "", "שמרו", "תמונות ישנות (לבקש מאור)", "idea", "⚠️ שנים מדויקות"),
    (24, "instagram", "reel", "club", "תזכורת: אימון ניסיון", "'נשארו מקומות בקבוצת [ימים]'",
     "", "", "שלחו 'ניסיון'", "", "idea", "לכתוב 'מקומות אחרונים' רק אם זה נכון"),
    (26, "instagram", "reel", "behind", "שבוע של מאמן-לוחם", "ספירה לאחור: 5 אימונים, 3 קבוצות, 1 קרב",
     "", "", "תעקבו", "", "idea", ""),
    # Days 28-30: review
    (28, "instagram", "reel", "coach", "טכניקה בהילוך איטי: טיפ (Teep)", "טיפ בהילוך איטי מזווית צד",
     "הבעיטה הכי משעממת היא זו שמנצחת קרבות.", "The most boring kick wins fights.", "שמרו", "צריך לצלם", "idea", ""),
    (29, "instagram", "story", "behind", "סיכום חודש + סקר", "", "", "", "סקר", "", "idea", "לפני כן: דוח חודשי"),
]


def main():
    if OUT.exists() and "--force" not in sys.argv:
        sys.exit(f"{OUT} exists. Use --force to overwrite.")
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(FIELDS)
        for off, *rest in ITEMS:
            w.writerow([(START + dt.timedelta(days=off)).isoformat(), *rest])
    print(f"wrote {len(ITEMS)} rows to {OUT}")


if __name__ == "__main__":
    main()
