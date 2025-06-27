# מערכת ניהול תיק השקעות - 3 שירותים נפרדים

מערכת לניהול תיק השקעות עם 3 שירותים נפרדים:
1. **Flask App** - אפליקציית ווב לניהול התיק
2. **PostgreSQL** - מסד נתונים
3. **Ollama** - שרת בינה מלאכותית

## 🏗️ ארכיטקטורה

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │   PostgreSQL    │    │     Ollama      │
│   (inv_web01)   │    │ (inv_db_Postgres)│    │    (ollama)     │
│                 │    │                 │    │                 │
│ Port: 8080      │    │ Port: 5432      │    │ Port: 11434     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 הפעלה מהירה

### דרישות מקדימות
- Docker
- Docker Compose

### הפעלה
```bash
# הפעלת כל השירותים
chmod +x start-services.sh
./start-services.sh

# או ידנית
docker-compose up --build -d
```

### עצירה
```bash
# עצירת כל השירותים
chmod +x stop-services.sh
./stop-services.sh

# או ידנית
docker-compose down
```

## 🌐 גישה לשירותים

- **אפליקציה**: http://localhost:8080
- **מסד נתונים**: localhost:5432
- **Ollama**: http://localhost:11434

## 📊 פרטי התחברות

### משתמשים מוכנים
- **מנהל**: `admin` / `admin`
- **משתמש**: `user` / `user`

### מסד נתונים
- **מסד**: `investments`
- **משתמש**: `postgres`
- **סיסמה**: `password`

## 🔧 ניהול השירותים

### צפייה בלוגים
```bash
# לוגים של האפליקציה
docker-compose logs -f flask-app

# לוגים של מסד הנתונים
docker-compose logs -f postgres

# לוגים של Ollama
docker-compose logs -f ollama
```

### הפעלה מחדש
```bash
# הפעלה מחדש של אפליקציה
docker-compose restart flask-app

# הפעלה מחדש של מסד נתונים
docker-compose restart postgres

# הפעלה מחדש של Ollama
docker-compose restart ollama
```

### בדיקת סטטוס
```bash
# סטטוס כל השירותים
docker-compose ps

# בדיקת בריאות האפליקציה
curl http://localhost:8080/health

# בדיקת חיבור למסד נתונים
docker-compose exec postgres pg_isready -U postgres

# בדיקת חיבור ל-Ollama
curl http://localhost:11434/api/tags
```

## 📁 מבנה הקבצים

```
tomerINV/
├── app.py                 # אפליקציית Flask הראשית
├── dbmodel.py            # מודל מסד הנתונים
├── ollamamodel.py        # מודל בינה מלאכותית
├── docker-compose.yml    # הגדרת 3 השירותים
├── Dockerfile            # בניית תמונת האפליקציה
├── start-services.sh     # סקריפט הפעלה
├── stop-services.sh      # סקריפט עצירה
├── requirements.txt      # תלויות Python
└── templates/            # תבניות HTML
```

## 🎯 פונקציות עיקריות

### ניהול תיק השקעות
- הוספת/הסרת ניירות ערך
- מעקב אחר מחירים
- חישוב ערך כולל
- ניתוח סיכונים

### בינה מלאכותית
- ייעוץ השקעות
- ניתוח מגמות
- המלצות פורטפוליו

### דוחות וגרפים
- גרף עוגה של התיק
- ניתוח סיכונים
- דוחות ביצועים

## 🔍 נתיבים עיקריים

- `/` - דף הבית
- `/portfolio` - תיק ההשקעות
- `/advice` - ייעוץ AI
- `/risk` - ניתוח סיכונים
- `/graph` - גרפים ודוחות
- `/health` - בדיקת בריאות
- `/check-env` - בדיקת משתני סביבה

## 🛠️ פיתוח

### הרצה מקומית (ללא Docker)
```bash
# הגדרת משתני סביבה
export DATABASE_URL="postgresql://postgres:password@localhost:5432/investments"
export OLLAMA_URL="http://localhost:11434"

# התקנת תלויות
pip install -r requirements.txt

# הפעלת האפליקציה
python app.py
```

### בנייה מחדש
```bash
# בנייה מחדש של כל השירותים
docker-compose build --no-cache

# בנייה מחדש של שירות ספציפי
docker-compose build flask-app
```

## 📈 ניירות ערך כלולים

המערכת מגיעה עם 20 ניירות ערך אמיתיים:
- **10 מניות עולמיות**: Apple, Google, Microsoft, Amazon, Tesla, Meta, NVIDIA, Netflix, Adobe, Salesforce
- **10 מניות ישראליות**: טבע, בזק, מכתשים, דלק, פלקס, מגדל, כלל, איי.די.בי, דיסנט, מנורה

## 🔐 אבטחה

- סיסמאות מוצפנות
- ניהול הרשאות (מנהל/משתמש)
- הגנה מפני CSRF
- חיבור מאובטח למסד נתונים

## 🚨 פתרון בעיות

### בעיות נפוצות

1. **פורט תפוס**
   ```bash
   # בדיקת פורטים בשימוש
   lsof -i :8080
   lsof -i :5432
   lsof -i :11434
   ```

2. **בעיות חיבור למסד נתונים**
   ```bash
   # בדיקת חיבור
   docker-compose exec postgres psql -U postgres -d investments
   ```

3. **בעיות עם Ollama**
   ```bash
   # בדיקת מודלים
   curl http://localhost:11434/api/tags
   
   # הורדת מודל
   docker-compose exec ollama ollama pull llama3.1:8b
   ```

### לוגים מפורטים
```bash
# כל הלוגים
docker-compose logs

# לוגים של שירות ספציפי
docker-compose logs flask-app
```

## 📞 תמיכה

לבעיות או שאלות:
1. בדוק את הלוגים: `docker-compose logs`
2. בדוק את הסטטוס: `docker-compose ps`
3. הפעל מחדש: `docker-compose restart`

---

**מערכת ניהול תיק השקעות** - פרויקט סיום פיתוח מערכות ווב 2025
