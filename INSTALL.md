# הוראות התקנה מלאות

## שלב 1: התקנת Docker Desktop

### על macOS:
1. **התקנה אוטומטית:**
   ```bash
   ./setup.sh
   ```

2. **התקנה ידנית:**
   ```bash
   # התקנת Docker Desktop
   brew install --cask docker
   
   # הפעלת Docker Desktop
   open /Applications/Docker.app
   ```

3. **המתנה לאתחול:**
   - המתן עד שסמל הדולפין יהיה ירוק
   - זה יכול לקחת 2-3 דקות

### על Linux:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose

# CentOS/RHEL
sudo yum install docker docker-compose

# הפעלת שירות Docker
sudo systemctl start docker
sudo systemctl enable docker

# הוספת המשתמש לקבוצת docker
sudo usermod -aG docker $USER
```

## שלב 2: בדיקת התקנה

```bash
# בדיקת Docker
docker --version

# בדיקת Docker Compose
docker-compose --version

# בדיקת הרצה
docker run hello-world
```

## שלב 3: הפעלת האפליקציה

### אפשרות 1: הפעלה אוטומטית
```bash
./setup.sh
```

### אפשרות 2: הפעלה ידנית
```bash
# ניקוי סביבה קיימת
./cleanup.sh

# בנייה והפעלה
docker-compose up -d --build

# צפייה בלוגים
docker-compose logs -f
```

## שלב 4: בדיקת האפליקציה

### כתובות גישה:
- **האפליקציה:** http://localhost:4000
- **Ollama API:** http://localhost:11434
- **PostgreSQL:** localhost:5432

### משתמשים לדוגמה:
- **admin / admin123**
- **demo_user / password123**

## שלב 5: ניהול השירותים

### פקודות שימושיות:
```bash
# צפייה בסטטוס
docker-compose ps

# צפייה בלוגים
docker-compose logs -f

# צפייה בלוגים של שירות ספציפי
docker-compose logs -f web
docker-compose logs -f ollama
docker-compose logs -f db

# עצירת השירותים
docker-compose down

# הפעלה מחדש
docker-compose restart

# עדכון קוד
docker-compose up -d --build

# ניקוי מלא
./cleanup.sh
```

## פתרון בעיות

### בעיה: Docker לא זמין
```bash
# בדיקה אם Docker Desktop רץ
ps aux | grep Docker

# הפעלה מחדש
open /Applications/Docker.app
```

### בעיה: פורט תפוס
```bash
# בדיקת פורטים בשימוש
lsof -i :4000
lsof -i :11434
lsof -i :5432

# שינוי פורט ב-docker-compose.yml
ports:
  - "4001:4000"  # במקום 4000:4000
```

### בעיה: זיכרון לא מספיק
```bash
# בדיקת זיכרון
docker stats

# עדכון מגבלות ב-docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G  # במקום 6G
```

### בעיה: מודל לא נטען
```bash
# בדיקת לוגים של Ollama
docker-compose logs ollama

# הורדה ידנית של המודל
docker-compose exec ollama ollama pull llama3.1:8b
```

## דרישות מערכת

### מינימום:
- **RAM:** 8GB
- **CPU:** 4 vCPU
- **דיסק:** 20GB פנוי

### מומלץ:
- **RAM:** 16GB
- **CPU:** 8 vCPU
- **דיסק:** 50GB פנוי

## תמיכה

לבעיות נוספות:
1. בדוק את הלוגים: `docker-compose logs -f`
2. בדוק זיכרון: `docker stats`
3. בדוק רשת: `docker network ls`
4. פנה לעזרה עם הלוגים המלאים 