# מערכת ניהול תיק השקעות

מערכת Flask לניהול תיק השקעות עם בינה מלאכותית (Ollama) ומסד נתונים PostgreSQL.

## פריסה בענן - Railway

### הוראות פריסה ל-Railway

1. **התחבר ל-Railway**:
   - היכנס ל-[railway.app](https://railway.app)
   - התחבר עם GitHub

2. **צור פרויקט חדש**:
   - לחץ על "New Project"
   - בחר "Deploy from GitHub repo"
   - בחר את הרפוזיטורי שלך

3. **הגדר משתני סביבה**:
   - הוסף `DATABASE_URL` עם כתובת PostgreSQL
   - הוסף `OLLAMA_URL` (אופציונלי - אם יש לך Ollama בענן)

4. **פרוס**:
   - Railway יזהה את ה-Dockerfile ויפרוס אוטומטית
   - האפליקציה תהיה זמינה בכתובת שניתנת

### סקריפט פריסה מהיר

```bash
./deploy.sh
# בחר אפשרות 1 (Railway)
```

## הרצה מקומית

### דרישות מקדימות

- Python 3.11+
- PostgreSQL (מקומי או בענן)
- Ollama (אופציונלי)

### התקנה

1. **שכפל את הפרויקט**:
   ```bash
   git clone <your-repo-url>
   cd tomerINV
   ```

2. **התקן תלויות**:
   ```bash
   pip install -r requirements.txt
   ```

3. **הגדר משתני סביבה**:
   ```bash
   export DATABASE_URL="postgresql://username:password@host:port/database"
   export PORT=4000
   export OLLAMA_URL="http://localhost:11434"  # אופציונלי
   ```

4. **הרץ את האפליקציה**:
   ```bash
   python app.py
   ```

### הרצה עם Docker

```bash
# הרצת האפליקציה בלבד
docker-compose up web

# הרצת האפליקציה + Ollama
docker-compose up
```

## תכונות

### ניהול תיק השקעות
- הוספת מניות ואגרות חוב
- מעקב אחר מחירים וערכים
- חישוב סיכונים
- גרפים ויזואליים

### בינה מלאכותית
- ייעוץ השקעות חכם
- ניתוח סיכונים
- המלצות מותאמות אישית

### אבטחה
- מערכת כניסה מאובטחת
- הרשאות משתמשים
- הצפנת סיסמאות

### ממשק משתמש
- עיצוב מודרני וידידותי
- תמיכה מלאה בעברית
- תצוגה מותאמת למובייל

## פיתוח

### מבנה הפרויקט

```
tomerINV/
├── app.py              # האפליקציה הראשית
├── dbmodel.py          # מודל מסד הנתונים
├── ollamamodel.py      # מודל בינה מלאכותית
├── templates/          # תבניות HTML
├── requirements.txt    # תלויות Python
├── Dockerfile         # קונפיגורציה ל-Docker
└── docker-compose.yml # קונפיגורציה ל-Docker Compose
```

### הוספת תכונות חדשות

1. **הוסף נתיב חדש ב-app.py**:
   ```python
   @app.route('/new-feature')
   def new_feature():
       return render_template('new_feature.html')
   ```

2. **צור תבנית HTML**:
   ```html
   <!-- templates/new_feature.html -->
   {% extends "base.html" %}
   {% block content %}
   <!-- התוכן שלך כאן -->
   {% endblock %}
   ```

### בדיקות

```bash
# בדיקת חיבור למסד נתונים
curl http://localhost:4000/health

# בדיקת חיבור ל-Ollama
curl http://localhost:4000/ollama-test
```

## תמיכה

אם יש לך בעיות או שאלות:
1. בדוק את הלוגים של האפליקציה
2. וודא שמסד הנתונים פועל
3. בדוק את משתני הסביבה
4. פתח issue ב-GitHub

## רישיון

פרויקט זה מוגן תחת רישיון MIT.
