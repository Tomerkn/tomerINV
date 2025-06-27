# הוראות פריסה בענן

## פריסה ב-Railway

### 1. הכנה
- וודא שיש לך חשבון ב-Railway
- וודא שהקוד נמצא ב-GitHub

### 2. פריסה
1. היכנס ל-Railway Dashboard
2. לחץ על "New Project"
3. בחר "Deploy from GitHub repo"
4. בחר את הרפוזיטורי שלך
5. לחץ על "Deploy Now"

### 3. הגדרת משתני סביבה
בתוך הפרויקט ב-Railway, היכנס ל-Variables והוסף:

```
DATABASE_URL=postgresql://username:password@host:port/database
OLLAMA_URL=https://your-ngrok-url.ngrok.io
```

### 4. מסד נתונים
1. הוסף שירות PostgreSQL חדש
2. העתק את ה-DATABASE_URL
3. הוסף אותו למשתני הסביבה

## פריסה ב-Render

### 1. הכנה
- וודא שיש לך חשבון ב-Render
- וודא שהקוד נמצא ב-GitHub

### 2. פריסה
1. היכנס ל-Render Dashboard
2. לחץ על "New +"
3. בחר "Web Service"
4. חבר את הרפוזיטורי שלך
5. הגדר:
   - Name: tomerINV
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app --bind 0.0.0.0:$PORT`

### 3. הגדרת משתני סביבה
הוסף את המשתנים הבאים:
```
DATABASE_URL=postgresql://username:password@host:port/database
OLLAMA_URL=https://your-ngrok-url.ngrok.io
```

## פריסה עם Docker

### 1. פריסה מקומית
```bash
# בניית התמונה
docker build -t tomerinv .

# הרצה
docker run -p 4000:4000 -e DATABASE_URL=your_db_url tomerinv
```

### 2. עם docker-compose
```bash
# הרצה עם מסד נתונים
docker-compose up --build
```

## בדיקת הפריסה

### 1. בדיקת לוגים
- היכנס ללוגים של השירות
- חפש את ההדפסות הבאות:
  - "=== התחלת טעינת האפליקציה ==="
  - "=== Flask app נוצר בהצלחה ==="
  - "=== יצירת מופעי המחלקות ==="
  - "=== האפליקציה מוכנה להפעלה ==="

### 2. בדיקת חיבור למסד נתונים
חפש בלוגים:
- "מתחבר ל-Postgres עם SQLAlchemy"
- "חיבור ל-Postgres הצליח"
- "טבלאות נוצרו בהצלחה"

### 3. בדיקת האתר
- היכנס לכתובת האתר
- נסה להתחבר עם:
  - שם משתמש: admin
  - סיסמה: admin

## פתרון בעיות

### 1. שגיאת itsdangerous
```bash
pip install itsdangerous==2.1.2
```

### 2. שגיאת matplotlib
```bash
pip install matplotlib==3.7.2
```

### 3. שגיאת sniffio
```bash
pip install sniffio==1.3.0
```

### 4. בעיות חיבור למסד נתונים
- וודא שה-DATABASE_URL נכון
- וודא שמסד הנתונים זמין
- בדוק את הלוגים לפרטי השגיאה

### 5. בעיות עם Ollama
- וודא שה-OLLAMA_URL נכון
- וודא ש-Ollama רץ ונגיש
- בדוק את הלוגים לפרטי השגיאה

# הוראות פריסה עם Docker

## סקירה כללית
האפליקציה כוללת 3 שירותים:
1. **web** - האפליקציה הראשית (Flask)
2. **db** - מסד נתונים PostgreSQL
3. **ollama** - שירות בינה מלאכותית עם מודל Llama3.1 8B

## דרישות מערכת
- **RAM:** מינימום 8GB (מומלץ 16GB)
- **CPU:** 8 vCPU
- **דיסק:** 20GB פנוי
- **Docker & Docker Compose**

## הוראות הפעלה

### 1. הכנה
```bash
# שכפול הפרויקט
git clone <repository-url>
cd tomerINV

# יצירת קובץ .env (אופציונלי)
cp .env.example .env
```

### 2. הפעלת האפליקציה
```bash
# בנייה והפעלה של כל השירותים
docker-compose up -d

# צפייה בלוגים
docker-compose logs -f

# צפייה בלוגים של שירות ספציפי
docker-compose logs -f web
docker-compose logs -f ollama
docker-compose logs -f db
```

### 3. בדיקת סטטוס
```bash
# בדיקת שירותים
docker-compose ps

# בדיקת זיכרון
docker stats

# בדיקת האפליקציה
curl http://localhost:4000/health
```

## כתובות גישה
- **האפליקציה:** http://localhost:4000
- **Ollama API:** http://localhost:11434
- **PostgreSQL:** localhost:5432

## ניהול השירותים

### עצירת השירותים
```bash
docker-compose down
```

### הפעלה מחדש
```bash
docker-compose restart
```

### עדכון קוד
```bash
# עצירה
docker-compose down

# בנייה מחדש
docker-compose build --no-cache

# הפעלה
docker-compose up -d
```

### ניקוי נתונים
```bash
# מחיקת כל הנתונים (זהירות!)
docker-compose down -v
docker volume rm tomerinv_postgres_data tomerinv_ollama_data
```

## פתרון בעיות

### בעיות זיכרון
אם יש בעיות זיכרון, עדכן את `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 4G  # במקום 6G
```

### בעיות חיבור
```bash
# בדיקת לוגים
docker-compose logs ollama
docker-compose logs web

# בדיקת רשת
docker network ls
docker network inspect tomerinv_default
```

### איטיות
- בדוק שהמודל נטען: `docker-compose logs ollama`
- בדוק זיכרון: `docker stats`
- שקול מודל קטן יותר: `llama3.1:3b`

## משתמשים לדוגמה
- **admin / admin123**
- **demo_user / password123**

## תמיכה
לבעיות נוספות, בדוק את הלוגים או פנה לעזרה. 