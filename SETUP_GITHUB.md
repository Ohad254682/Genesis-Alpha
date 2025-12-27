# הוראות העלאה ל-GitHub

## לפני ההעלאה - וידוא אבטחה

### 1. בדוק שאין API keys בקוד
הקוד כבר מוגן - אין API keys hardcoded. ה-API key נקרא רק מ:
- Environment variable (`OPENAI_API_KEY`)
- קובץ `.env` (לא נכלל ב-git)
- קובץ `api_key.txt` (לא נכלל ב-git)

### 2. וודא ש-.gitignore מעודכן
הקובץ `.gitignore` כבר כולל:
- `api_key.txt`
- `.env`
- `.cursor/` (debug logs)
- `*.log`

## שלבי העלאה ל-GitHub

### שלב 1: אתחול Git Repository

```bash
# אתחל repository חדש
git init

# הוסף את כל הקבצים
git add .

# בדוק מה נוסף (וודא שאין api_key.txt או .env)
git status

# צור commit ראשון
git commit -m "Initial commit: Genesis Alpha - AI-powered stock analysis app"
```

### שלב 2: חיבור ל-GitHub Repository

```bash
# הוסף את ה-remote repository
git remote add origin https://github.com/Ohad254682/Genesis-Alpha.git

# בדוק את ה-remote
git remote -v
```

### שלב 3: העלאה ל-GitHub

```bash
# העלה את הקוד
git branch -M main
git push -u origin main
```

## יצירת .env.example (אופציונלי)

אם תרצה, צור קובץ `.env.example` עם תוכן:
```
OPENAI_API_KEY=your-api-key-here
```

זה יעזור למשתמשים אחרים להבין איך להגדיר את ה-API key.

## בדיקה אחרונה לפני העלאה

הרץ את הפקודות הבאות כדי לוודא שאין קבצים רגישים:

```bash
# בדוק אם api_key.txt נכלל
git check-ignore api_key.txt
# אמור להחזיר: api_key.txt

# בדוק אם .env נכלל
git check-ignore .env
# אמור להחזיר: .env

# בדוק מה נוסף ל-git
git status
```

## הערות חשובות

1. **לעולם אל תעלה API keys** - הם כבר ב-.gitignore
2. **הקוד מוכן להעלאה** - כל הקבצים הרגישים מוגנים
3. **אם יש לך API key ב-`api_key.txt`** - הוא לא יועלה כי הוא ב-.gitignore

## אם כבר יש repository קיים ב-GitHub

אם ה-repository כבר קיים עם קבצים, תצטרך לעשות pull קודם:

```bash
git pull origin main --allow-unrelated-histories
# פתור conflicts אם יש
git push -u origin main
```

