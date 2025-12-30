# ארכיטקטורת הפרויקט - Genesis Alpha 📈

## סקירה כללית

**Genesis Alpha** הוא אפליקציית Streamlit לניתוח מניות ואופטימיזציה של תיק השקעות, המונעת על ידי Generative AI. הפרויקט בנוי בארכיטקטורה מודולרית עם הפרדת אחריות ברורה.

---

## מבנה הפרויקט

```
Genesis-Alpha/
├── app/                    # שכבת המצגת (Presentation Layer)
│   └── main.py            # נקודת הכניסה הראשית - UI ו-Logic של Streamlit
│
├── utils/                  # שכבת הלוגיקה העסקית (Business Logic Layer)
│   ├── data_cache.py      # ניהול Cache מרכזי לנתוני מניות
│   ├── date_utils.py       # פונקציות עזר לחישוב תאריכים
│   ├── kpi_calculator.py  # חישוב KPIs (RSI, Bollinger Bands, P/E, Beta, MACD)
│   ├── llm_utils.py       # אינטגרציה עם OpenAI/LangChain
│   ├── portfolio_optimizer.py  # אופטימיזציה של תיק השקעות (MPT, Black-Litterman, Risk Parity)
│   └── visualizations.py   # יצירת גרפים ותרשימים
│
├── config/                 # שכבת התצורה (Configuration Layer)
│   └── settings.py         # הגדרות ברירת מחדל ו-API keys
│
├── assets/                 # משאבים סטטיים
│   ├── logos/
│   ├── backgrounds/
│   └── videos/
│
└── requirements.txt        # תלויות Python
```

---

## ארכיטקטורה בשכבות (Layered Architecture)

### 1. **שכבת המצגת (Presentation Layer) - `app/main.py`**

**תפקיד**: ניהול UI, אינטראקציה עם המשתמש, וקואורדינציה בין הרכיבים.

**מאפיינים עיקריים**:
- **Streamlit Framework**: UI מבוסס Python
- **Session State Management**: ניהול מצב המשתמש
- **Tab-based Navigation**: ניווט בין תכונות שונות
- **Landing Page**: דף נחיתה מותאם למובייל
- **Custom CSS**: עיצוב מותאם אישית

**תכונות**:
- דף בית עם אנימציות
- חילוץ Tickers עם GenAI
- תצוגת KPIs
- ויזואליזציות טכניות
- אופטימיזציה של תיק השקעות
- המלצות AI

**Caching Strategy**:
```python
@st.cache_data(ttl=3600)  # Cache ל-1 שעה
@st.cache_data(ttl=1800)  # Cache ל-30 דקות (AI recommendations)
```

---

### 2. **שכבת הלוגיקה העסקית (Business Logic Layer) - `utils/`**

#### **`data_cache.py`** - ניהול Cache מרכזי
**תפקיד**: נקודת גישה מרכזית לנתוני מניות עם caching.

**מאפיינים**:
- **Centralized Caching**: כל קריאות yfinance עוברות דרך פונקציה אחת
- **Retry Logic**: טיפול בשגיאות רשת עם retry אוטומטי
- **TTL (Time To Live)**: Cache תקף ל-1 שעה
- **Error Handling**: טיפול בשגיאות connection

**פונקציות עיקריות**:
- `get_ticker_history()` - היסטוריית מחירים
- `get_ticker_info()` - מידע על החברה
- `get_multiple_tickers_history()` - נתונים מרובי מניות

#### **`kpi_calculator.py`** - חישוב מדדי ביצוע
**תפקיד**: חישוב KPIs טכניים למניות.

**KPIs מחושבים**:
- **RSI (Relative Strength Index)**: מדד מומנטום
- **Bollinger Bands**: ניתוח תנודתיות
- **P/E Ratio**: יחס מחיר/רווח
- **Beta**: תנודתיות יחסית לשוק
- **MACD**: ניתוח מגמות

**מאפיינים**:
- שימוש ב-`data_cache.py` למניעת קריאות כפולות
- Caching של תוצאות
- טיפול בשגיאות per-ticker

#### **`portfolio_optimizer.py`** - אופטימיזציה של תיק השקעות
**תפקיד**: חישוב הקצאות אופטימליות לתיק השקעות.

**שיטות אופטימיזציה**:
1. **Modern Portfolio Theory (MPT)**: מקסימיזציה של Sharpe Ratio
2. **Black-Litterman Model**: שילוב תחזיות שוק עם דעות משקיע
3. **Risk Parity**: איזון סיכון בין נכסים

**מאפיינים**:
- שימוש ב-`PyPortfolioOpt` library
- חישוב covariance matrix
- אופטימיזציה עם `scipy.optimize`
- טיפול בנתונים חסרים

#### **`llm_utils.py`** - אינטגרציה עם AI
**תפקיד**: ניהול תקשורת עם OpenAI API.

**מאפיינים**:
- **LangChain Integration**: שימוש ב-`ChatOpenAI`
- **Retry Logic**: טיפול בשגיאות connection
- **Exponential Backoff**: המתנה הולכת וגדלה בין retries
- **Caching**: Cache של תגובות AI (24 שעות)
- **Error Handling**: טיפול ב-rate limits ו-API errors

**פונקציות**:
- `initialize_llm()` - אתחול מודל
- `get_llm_response()` - קבלת תגובה מ-LLM

#### **`visualizations.py`** - יצירת גרפים
**תפקיד**: יצירת ויזואליזציות לנתוני מניות.

**גרפים נתמכים**:
- RSI charts
- Bollinger Bands
- P/E Ratios comparison
- Beta comparison
- MACD signals

**טכנולוגיות**:
- `matplotlib` - גרפים סטטיים
- `plotly` - גרפים אינטראקטיביים

#### **`date_utils.py`** - פונקציות עזר לתאריכים
**תפקיד**: חישוב טווחי תאריכים לניתוח.

---

### 3. **שכבת התצורה (Configuration Layer) - `config/settings.py`**

**תפקיד**: ניהול הגדרות ו-API keys.

**מאפיינים**:
- **Multiple API Key Sources**: תמיכה ב-3 מקורות:
  1. Environment variable (`OPENAI_API_KEY`)
  2. `.env` file
  3. `api_key.txt` (backward compatibility)
- **Default Settings**: ערכי ברירת מחדל
- **Security**: API keys לא נשמרים בקוד

**הגדרות ברירת מחדל**:
- `DEFAULT_YEARS = 2`
- `DEFAULT_RISK_FREE_RATE_MPT = 0.04`
- `DEFAULT_RISK_FREE_RATE_BL = 0.001`
- `DEFAULT_ASSETS = [...]`

---

## דפוסי עיצוב (Design Patterns)

### 1. **Singleton Pattern**
- `st.session_state` - ניהול מצב גלובלי של האפליקציה
- LLM instance - מופע יחיד לכל session

### 2. **Caching Pattern**
- `@st.cache_data` - caching אוטומטי של Streamlit
- TTL-based invalidation
- Cache key based on function parameters

### 3. **Retry Pattern**
- Retry logic עם exponential backoff
- טיפול בשגיאות connection
- Graceful degradation

### 4. **Dependency Injection**
- פונקציות מקבלות dependencies כפרמטרים
- קל לבדיקה (testability)

### 5. **Separation of Concerns**
- הפרדה ברורה בין UI, Business Logic, ו-Data Access
- כל מודול אחראי על תחום אחד

---

## זרימת נתונים (Data Flow)

```
User Input (Streamlit UI)
    ↓
app/main.py (Coordination)
    ↓
utils/ (Business Logic)
    ↓
data_cache.py (Data Access)
    ↓
yfinance API / OpenAI API
    ↓
Cache (Streamlit)
    ↓
Response to User
```

### דוגמה: חישוב KPIs

1. **User Input**: משתמש בוחר מניות
2. **main.py**: קורא ל-`calculate_kpis()`
3. **kpi_calculator.py**: קורא ל-`get_ticker_history()` מ-`data_cache.py`
4. **data_cache.py**: בודק cache → אם אין, קורא ל-yfinance
5. **yfinance**: מחזיר נתונים
6. **data_cache.py**: שומר ב-cache ומחזיר
7. **kpi_calculator.py**: מחשב KPIs
8. **main.py**: מציג למשתמש

---

## ניהול Cache

### אסטרטגיית Caching

**3 רמות Cache**:

1. **Streamlit Cache** (`@st.cache_data`):
   - TTL: 1 שעה (נתוני מניות)
   - TTL: 30 דקות (AI recommendations)
   - TTL: 24 שעות (LLM responses)

2. **Centralized Data Cache** (`data_cache.py`):
   - נקודת גישה אחת לכל נתוני yfinance
   - מונע קריאות כפולות

3. **Session State**:
   - שמירת מצב המשתמש
   - KPIs מחושבים
   - Tickers נבחרים

### Cache Invalidation

- **Time-based**: TTL אוטומטי
- **Parameter-based**: Cache key משתנה לפי פרמטרים
- **Manual**: `st.cache_data.clear()` (אם נדרש)

---

## טיפול בשגיאות (Error Handling)

### רמות טיפול בשגיאות:

1. **Connection Errors**:
   - Retry עם exponential backoff
   - הודעות ברורות למשתמש
   - Graceful degradation

2. **API Errors**:
   - טיפול ב-rate limits
   - Validation של API keys
   - הודעות שגיאה ברורות

3. **Data Errors**:
   - Validation של נתונים
   - טיפול בנתונים חסרים
   - Fallback values

### Retry Strategy:

```python
max_retries = 3
retry_delay = 2 * (attempt + 1)  # Exponential backoff
```

---

## ביטחון (Security)

### API Keys:

- **לא נשמרים בקוד**
- **3 מקורות תמיכה**:
  1. Environment variables (מומלץ)
  2. `.env` file (לא ב-git)
  3. `api_key.txt` (backward compatibility, לא ב-git)

### `.gitignore`:

```
.env
api_key.txt
*.key
*.pem
```

---

## ביצועים (Performance)

### אופטימיזציות:

1. **Caching**: מניעת קריאות API כפולות
2. **Pre-loading**: טעינה מראש של נתונים
3. **Lazy Loading**: טעינה רק כשצריך
4. **Background Processing**: חישוב KPIs ברקע

### Bottlenecks פוטנציאליים:

1. **yfinance API**: יכול להיות איטי
   - **פתרון**: Caching + Retry logic

2. **OpenAI API**: יקר ואיטי
   - **פתרון**: Caching + TTL ארוך

3. **Portfolio Optimization**: חישובים כבדים
   - **פתרון**: Caching + Optional dependency

---

## תלויות (Dependencies)

### Core Dependencies:

- **streamlit**: Framework ל-UI
- **pandas**: עיבוד נתונים
- **numpy**: חישובים מספריים
- **yfinance**: נתוני מניות

### AI Dependencies:

- **langchain-openai**: אינטגרציה עם OpenAI
- **openai**: OpenAI SDK

### Financial Dependencies:

- **scipy**: אופטימיזציה
- **PyPortfolioOpt**: אופטימיזציה של תיק השקעות

### Visualization:

- **matplotlib**: גרפים סטטיים
- **plotly**: גרפים אינטראקטיביים

---

## הרחבה עתידית (Future Extensions)

### אפשרויות להרחבה:

1. **Database Integration**: שמירת נתונים ב-DB
2. **Real-time Updates**: WebSockets לעדכונים בזמן אמת
3. **User Authentication**: מערכת משתמשים
4. **Portfolio Tracking**: מעקב אחר תיקים אמיתיים
5. **Alerts**: התראות על שינויים
6. **Backtesting**: בדיקת אסטרטגיות היסטוריות

---

## סיכום

הפרויקט בנוי בארכיטקטורה **מודולרית** ו-**שכבתית** עם:

✅ **הפרדת אחריות ברורה**  
✅ **Caching אגרסיבי** לביצועים  
✅ **טיפול בשגיאות חזק**  
✅ **ביטחון** - API keys לא בקוד  
✅ **קלות תחזוקה** - קוד מאורגן  
✅ **קלות הרחבה** - מודולים נפרדים  

הארכיטקטורה מאפשרת:
- פיתוח מהיר
- תחזוקה קלה
- הרחבה פשוטה
- ביצועים טובים
- אמינות גבוהה

