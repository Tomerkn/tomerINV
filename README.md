# אפליקציית ניהול תיק השקעות

אפליקציית Flask לניהול תיק השקעות עם בינה מלאכותית, מסד נתונים PostgreSQL, ומודל Llama3.1 8B.

## תכונות עיקריות

- ניהול תיק השקעות אישי
- מעקב אחר מניות וניירות ערך
- ייעוץ השקעות מבוסס בינה מלאכותית
- ניתוח סיכונים
- גרפים ואינדיקטורים
- ממשק משתמש בעברית

## התקנה מהירה

### דרישות מערכת
- **RAM:** מינימום 8GB (מומלץ 16GB)
- **CPU:** 4 vCPU ומעלה
- **דיסק:** 20GB פנוי
- **Docker & Docker Compose**

### הפעלה אוטומטית
```bash
# הורדת הפרויקט
git clone <repository-url>
cd tomerINV

# הפעלת סקריפט ההתקנה
./setup.sh
```

### הפעלה ידנית
```bash
# התקנת Docker (אם לא מותקן)
brew install --cask docker  # macOS
open /Applications/Docker.app

# הפעלת האפליקציה
docker-compose up -d --build

# צפייה בלוגים
docker-compose logs -f
```

## כתובות גישה

- **האפליקציה:** http://localhost:4000
- **Ollama API:** http://localhost:11434
- **PostgreSQL:** localhost:5432

## משתמשים לדוגמה

- **admin / admin123**
- **demo_user / password123**

## ארכיטקטורה

האפליקציה כוללת 3 שירותים:

1. **web** - האפליקציה הראשית (Flask)
2. **db** - מסד נתונים PostgreSQL
3. **ollama** - שירות בינה מלאכותית עם מודל Llama3.1 8B

## ניהול השירותים

### פקודות שימושיות
```bash
# צפייה בסטטוס
docker-compose ps

# צפייה בלוגים
docker-compose logs -f

# עצירת השירותים
docker-compose down

# הפעלה מחדש
docker-compose restart

# עדכון קוד
docker-compose up -d --build

# ניקוי מלא
./cleanup.sh
```

## פיתוח

### הרצה מקומית (ללא Docker)
```bash
# התקנת תלויות
pip install -r requirements.txt

# הפעלת האפליקציה
python app.py
```

### מבנה הפרויקט
```
tomerINV/
├── app.py                 # האפליקציה הראשית
├── dbmodel.py            # מודל מסד הנתונים
├── portfolio_controller.py # בקר תיק השקעות
├── ollamamodel.py        # מודל בינה מלאכותית
├── securities.py         # ניהול ניירות ערך
├── broker.py             # סימולציית ברוקר
├── docker-compose.yml    # הגדרות Docker
├── Dockerfile           # תמונת האפליקציה
├── requirements.txt     # תלויות Python
├── setup.sh            # סקריפט התקנה
├── cleanup.sh          # סקריפט ניקוי
├── templates/          # תבניות HTML
├── public/            # קבצים סטטיים
└── instance/          # נתונים מקומיים
```

## פתרון בעיות

### בעיות נפוצות

1. **Docker לא זמין**
   ```bash
   open /Applications/Docker.app
   ```

2. **פורט תפוס**
   ```bash
   lsof -i :4000
   docker-compose down
   ```

3. **זיכרון לא מספיק**
   ```bash
   docker stats
   # עדכן מגבלות ב-docker-compose.yml
   ```

4. **מודל לא נטען**
   ```bash
   docker-compose logs ollama
   ```

### לוגים מפורטים
```bash
# לוגים של כל השירותים
docker-compose logs -f

# לוגים של שירות ספציפי
docker-compose logs -f web
docker-compose logs -f ollama
docker-compose logs -f db
```

## תרומה

1. Fork את הפרויקט
2. צור branch חדש
3. בצע שינויים
4. שלח Pull Request

## רישיון

MIT License

## תמיכה

לבעיות נוספות, בדוק את הלוגים או פנה לעזרה עם פרטי השגיאה.
