# מערכת ניהול תיק השקעות

מערכת Flask לניהול תיק השקעות עם בינה מלאכותית (Ollama) ומסד נתונים PostgreSQL.

## 🚀 פריסה בענן

### אפשרות 1: Railway (מומלץ)

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

### אפשרות 2: Heroku

1. **התקן Heroku CLI**:
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Windows
   # הורד מ: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **התחבר ל-Heroku**:
   ```bash
   heroku login
   ```

3. **צור אפליקציה**:
   ```bash
   heroku create your-app-name
   ```

4. **הוסף מסד נתונים**:
   ```bash
   heroku addons:create heroku-postgresql:mini
   ```

5. **הגדר משתני סביבה**:
   ```bash
   heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)
   ```

6. **פרוס**:
   ```bash
   git push heroku main
   ```

### אפשרות 3: Docker Compose (מקומי)

להרצה מקומית עם Docker:

```bash
# הפעל את כל השירותים
docker-compose up --build

# או ברקע
docker-compose up -d --build
```

## 🔧 משתני סביבה נדרשים

- `DATABASE_URL`: כתובת PostgreSQL (נדרש)
- `PORT`: פורט להרצה (נקבע אוטומטית בענן)
- `OLLAMA_URL`: כתובת Ollama (אופציונלי)

## 📁 מבנה הפרויקט

```
tomerINV/
├── app.py                 # האפליקציה הראשית
├── dbmodel.py            # מודל מסד הנתונים
├── ollamamodel.py        # חיבור ל-Ollama
├── templates/            # תבניות HTML
├── static/               # קבצים סטטיים
├── Dockerfile           # הגדרת Docker
├── docker-compose.yml   # הגדרת שירותים מקומיים
├── railway.json         # הגדרת Railway
├── Procfile             # הגדרת Heroku
└── requirements.txt     # תלויות Python
```

## 🛠️ פיתוח מקומי

```bash
# התקן תלויות
pip install -r requirements.txt

# הגדר משתני סביבה
export DATABASE_URL="your_postgresql_url"
export PORT=4000

# הפעל את האפליקציה
python app.py
```

## 🔍 בדיקת בריאות

האפליקציה כוללת נתיב `/health` לבדיקת בריאות:

```bash
curl http://your-app-url/health
```

## 📊 תכונות

- ✅ ניהול משתמשים והרשאות
- ✅ הוספת/עריכת/מחיקת השקעות
- ✅ חישובי סיכון ורווח
- ✅ גרפים ותרשימים
- ✅ ייעוץ בינה מלאכותית (Ollama)
- ✅ פריסה בענן
- ✅ מסד נתונים PostgreSQL

## 🚨 הערות חשובות

1. **מסד הנתונים**: חייב להיות PostgreSQL בענן
2. **Ollama**: אופציונלי - האפליקציה תעבוד גם בלי
3. **אבטחה**: משתמש admin/admin כברירת מחדל
4. **נתונים**: האפליקציה תוסיף נתונים לדוגמה אם המסד ריק
