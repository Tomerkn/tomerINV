# מערכת ניהול תיק השקעות - מקומית

מערכת פשוטה לניהול תיק השקעות עם MySQL מקומי ו-Ollama AI.

## 🚀 התקנה והפעלה מהירה

### דרישות מקדימות
- Python 3.8+
- MySQL מותקן ופועל
- אופציונלי: Ollama עם מודל llama3.1:8b

### הפעלה מהירה

```bash
# 1. התקן ספריות
pip install -r requirements.txt

# 2. הגדר המערכת
python setup_local.py

# 3. הפעל המערכת
python run_local.py
```

או פשוט:
```bash
python app.py
```

### הגדרת MySQL

```bash
# macOS
brew install mysql
brew services start mysql

# Ubuntu/Debian
sudo apt-get install mysql-server
sudo systemctl start mysql
```

### הגדרת Ollama (אופציונלי)

```bash
# הורד מ: https://ollama.ai
ollama pull llama3.1:8b
ollama serve
```

## 📱 שימוש במערכת

1. **גש לכתובת:** http://localhost:5000
2. **התחבר עם:**
   - מנהל: `admin` / `admin`
   - משתמש: `user` / `user`

## 🎯 תכונות

- ✅ ניהול תיק השקעות
- ✅ הוספה/הסרה של מניות ואג"ח
- ✅ עדכון מחירים מ-API
- ✅ גרפים ודוחות
- ✅ ייעוץ AI (עם Ollama)
- ✅ ניהול משתמשים

## 🔧 הגדרות

הקובץ `.env` נוצר אוטומטית עם ההגדרות הבסיסיות:

```bash
DATABASE_URL=localhost
OLLAMA_URL=http://localhost:11434
SECRET_KEY=local-portfolio-secret-key-2024
```

## 🐛 פתרון בעיות

### MySQL לא פועל
```bash
# macOS
mysql.server start
# או
brew services start mysql

# Linux
sudo systemctl start mysql
```

### Ollama לא פועל
```bash
ollama serve
```

### שגיאות בהתקנה
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📁 מבנה הקבצים

```
├── app.py              # האפליקציה הראשית
├── dbmodel.py          # מסד נתונים
├── ollamamodel.py      # בינה מלאכותית
├── run_local.py        # הפעלה מקומית
├── setup_local.py      # הגדרה מקומית
├── requirements.txt    # ספריות נדרשות
└── templates/          # דפי HTML
```

## 🚀 הפעלה

```bash
python run_local.py
```

המערכת תפעל על http://localhost:5000 