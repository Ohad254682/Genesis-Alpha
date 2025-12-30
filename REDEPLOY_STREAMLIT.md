# איך לעשות Redeploy ב-Streamlit Community Cloud

## הבעיה
השינויים נדחפו ל-GitHub, אבל Streamlit לא מעדכן אוטומטית. צריך לעשות **Redeploy ידני**.

## פתרון - Redeploy ידני

### שלב 1: לך ל-Streamlit Community Cloud
1. לך ל-[https://share.streamlit.io/](https://share.streamlit.io/)
2. התחבר לחשבון שלך

### שלב 2: מצא את האפליקציה
1. לחץ על **"Manage apps"** או **"Your apps"**
2. מצא את האפליקציה שלך: `genesis-alpha-itxbyhmcwnbhopszxu7w4n`

### שלב 3: Redeploy
1. לחץ על **"⚙️ Settings"** או **"Manage app"** ליד האפליקציה
2. גלול למטה למצוא את כפתור **"Redeploy"** או **"Always rerun"**
3. לחץ על **"Redeploy"** או **"Save"**

### שלב 4: המתן
- Streamlit יתחיל לבנות מחדש את האפליקציה
- זה יכול לקחת 1-3 דקות
- תראה הודעת "Building..." או "Deploying..."

### שלב 5: בדיקה
- לאחר שהבנייה מסתיימת, רענן את הדף
- השינויים אמורים להופיע

---

## פתרון חלופי - Clear Cache

אם Redeploy לא עוזר:

1. לך ל-**Settings** של האפליקציה
2. מצא **"Clear cache"** או **"Clear app cache"**
3. לחץ על זה
4. לחץ על **"Redeploy"** שוב

---

## אם זה עדיין לא עובד

### בדוק שהשינויים ב-GitHub:
1. לך ל-[https://github.com/Ohad254682/Genesis-Alpha](https://github.com/Ohad254682/Genesis-Alpha)
2. ודא שהקובץ `app/main.py` כולל את השינויים
3. בדוק את ה-commit האחרון: "Make landing page mobile-friendly..."

### בדוק את ה-Branch:
1. ב-Streamlit Settings, ודא שה-Branch הוא `main`
2. ודא שה-Main file path הוא `app/main.py`

### נסה Push נוסף:
אם השינויים לא ב-GitHub, נסה:
```bash
git push origin main --force
```

---

## טיפים

✅ **Redeploy ידני** - תמיד עובד, גם אם Auto-deploy לא עובד  
✅ **Clear Cache** - עוזר אם יש בעיות עם cache ישן  
✅ **המתן 2-3 דקות** - הבנייה לוקחת זמן  
✅ **רענן את הדף** - אחרי שהבנייה מסתיימת

---

## קישורים שימושיים

- [Streamlit Community Cloud Dashboard](https://share.streamlit.io/)
- [GitHub Repository](https://github.com/Ohad254682/Genesis-Alpha)
- [Streamlit Documentation](https://docs.streamlit.io/)

