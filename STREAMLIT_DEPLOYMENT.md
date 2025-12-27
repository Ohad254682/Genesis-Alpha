# הוראות העלאה ל-Streamlit Community Cloud

## שלב 1: הוספת OPENAI_API_KEY כ-Secret ב-Streamlit

### א. לאחר יצירת האפליקציה ב-Streamlit Community Cloud:

1. לחץ על **"Settings"** או **"⚙️ Manage app"** בתפריט האפליקציה
2. לחץ על **"Secrets"** בתפריט הצד
3. לחץ על **"Edit secrets"** או **"New secret"**

### ב. הוסף את ה-Secret הבא:

```toml
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

**⚠️ חשוב:**
- החלף את `sk-your-actual-api-key-here` ב-API key האמיתי שלך מ-OpenAI
- אין צורך להוסיף מרכאות כפולות סביב הערך - Streamlit עושה זאת אוטומטית
- לחץ על **"Save"** לאחר הוספת ה-Secret

### ג. איפה למצוא את ה-API Key שלך:

1. לך ל-[OpenAI Platform](https://platform.openai.com/api-keys)
2. התחבר לחשבון שלך
3. לחץ על **"Create new secret key"** (או השתמש בקיים)
4. העתק את ה-API key (הוא מופיע רק פעם אחת!)

---

## שלב 2: בדיקה שהקוד משתמש ב-Secret

הקוד שלך כבר מוכן להשתמש ב-Secret! הוא מחפש את `OPENAI_API_KEY` בסדר הבא:

1. **Environment variable** (Streamlit Secrets משתמש בזה)
2. קובץ `.env`
3. קובץ `api_key.txt`

**הקוד כבר מוכן - אין צורך בשינויים!**

---

## שלב 3: Deploy האפליקציה

1. לך ל-[Streamlit Community Cloud](https://share.streamlit.io/)
2. לחץ על **"New app"**
3. בחר את ה-repository: `Ohad254682/Genesis-Alpha`
4. בחר את ה-branch: `main`
5. הגדר את Main file path: `app/main.py`
6. לחץ על **"Deploy"**

---

## פתרון בעיות

### אם האפליקציה לא מוצאת את ה-API Key:

1. ודא שה-Secret נקרא בדיוק `OPENAI_API_KEY` (ללא רווחים)
2. ודא שהערך מתחיל ב-`sk-`
3. נסה ל-Redeploy את האפליקציה (Settings → Redeploy)
4. בדוק את ה-Logs באפליקציה לראות שגיאות

### אם יש שגיאת Import:

ודא ש-`requirements.txt` כולל את כל התלויות הנדרשות.

---

## הערות חשובות

✅ **אל תכלול את ה-API key בקוד** - הוא כבר ב-`.gitignore`  
✅ **השתמש ב-Streamlit Secrets** - זה הדרך הבטוחה ביותר  
✅ **ה-API key לא יוצג בקוד** - הוא נשמר בצורה מאובטחת ב-Streamlit

