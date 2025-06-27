# מערכת ניהול תיק השקעות

מערכת Flask לניהול תיק השקעות עם בינה מלאכותית (Ollama) ומסד נתונים PostgreSQL.

## 🚀 פריסה בענן - Railway

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

## 🏃‍♂️ הרצה מקומית

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
   export DATABASE_URL="postgresql://username:password@localhost:5432/dbname"
   export PORT=4000
   export OLLAMA_URL="http://localhost:11434"  # אופציונלי
   ```

4. **הרץ את האפליקציה**:
   ```bash
   python app.py
   ```

### הרצה עם Docker

```bash
# הרצה עם Docker Compose (כולל Ollama)
docker-compose up

# או רק האפליקציה
docker build -t portfolio-app .
docker run -p 4000:4000 -e DATABASE_URL="your-postgres-url" portfolio-app
```

## 📊 תכונות

- **ניהול תיק השקעות**: הוספה, עריכה ומחיקה של השקעות
- **ניתוח סיכונים**: חישוב וריאנס וסטיית תקן
- **בינה מלאכותית**: ייעוץ השקעות עם Ollama
- **ממשק משתמש**: דפי אינטרנט נוחים לשימוש
- **מסד נתונים**: PostgreSQL לעמידות ומהירות

## 🗄️ מבנה מסד הנתונים

### טבלת משתמשים (users)
- `id`: מזהה ייחודי
- `username`: שם משתמש
- `password_hash`: סיסמה מוצפנת

### טבלת השקעות (investments)
- `id`: מזהה ייחודי
- `name`: שם ההשקעה
- `amount`: כמות יחידות
- `price`: מחיר ליחידה
- `industry`: ענף
- `variance`: וריאנס
- `security_type`: סוג נייר ערך

## 🔧 פיתוח

### מבנה הפרויקט

```
tomerINV/
├── app.py                 # האפליקציה הראשית
├── dbmodel.py            # מודל מסד הנתונים
├── ollamamodel.py        # מודל AI
├── templates/            # תבניות HTML
├── static/               # קבצים סטטיים
├── requirements.txt      # תלויות Python
├── Dockerfile           # קונפיגורציה ל-Docker
├── docker-compose.yml   # קונפיגורציה ל-Docker Compose
└── railway.json         # קונפיגורציה ל-Railway
```

### הוספת תכונות חדשות

1. **הוסף נתיב חדש ב-`app.py`**
2. **צור תבנית HTML ב-`templates/`**
3. **עדכן את מודל הנתונים ב-`dbmodel.py` אם נדרש**
4. **בדוק שהכל עובד מקומית**
5. **דחוף ל-Git ו-Railway יעדכן אוטומטית**

## 🆘 פתרון בעיות

### בעיות נפוצות

**האפליקציה לא מתחברת למסד הנתונים**:
- ודא ש-`DATABASE_URL` מוגדר נכון
- בדוק שהמסד זמין ונגיש

**Ollama לא עובד**:
- ודא ש-Ollama פועל על `localhost:11434`
- או הגדר `OLLAMA_URL` לכתובת הנכונה

**האפליקציה לא נפתחת**:
- בדוק שהפורט פנוי
- נסה פורט אחר עם `export PORT=4001`

## 📞 תמיכה

אם יש לך בעיות או שאלות:
1. בדוק את הלוגים ב-Railway
2. בדוק את משתני הסביבה
3. ודא שכל התלויות מותקנות

---

**מערכת ניהול תיק השקעות** - פותח עם ❤️ ב-Python ו-Flask
