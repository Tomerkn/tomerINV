# הוראות פריסה לענן

## סקירה כללית

האפליקציה מוכנה לפריסה בענן עם:
- **Nginx Reverse Proxy** - פורט 80/443
- **PostgreSQL** - מסד נתונים יציב
- **Ollama** - שירות בינה מלאכותית
- **Flask App** - האפליקציה הראשית

## אפשרויות פריסה

### 1. VPS/Cloud Server (DigitalOcean, AWS, Google Cloud)

#### דרישות מערכת:
- **RAM:** מינימום 8GB (מומלץ 16GB)
- **CPU:** 4 vCPU ומעלה
- **דיסק:** 50GB SSD
- **מערכת הפעלה:** Ubuntu 20.04/22.04

#### הוראות התקנה:

```bash
# התחברות לשרת
ssh root@your-server-ip

# עדכון המערכת
apt update && apt upgrade -y

# התקנת Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# התקנת Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# הורדת הפרויקט
git clone <repository-url>
cd tomerINV

# הפעלת פריסה
./deploy-cloud.sh
```

### 2. Railway

#### הוראות:
1. הירשם ל-Railway
2. חבר את הפרויקט GitHub
3. הגדר משתני סביבה:
   ```
   PORT=4000
   SECRET_KEY=your-secret-key-here
   ```
4. Railway יזהה את `docker-compose.yml` ויפרוס אוטומטית

### 3. Render

#### הוראות:
1. הירשם ל-Render
2. צור Web Service חדש
3. חבר את הפרויקט GitHub
4. הגדר:
   - **Build Command:** `docker-compose -f docker-compose.prod.yml build`
   - **Start Command:** `docker-compose -f docker-compose.prod.yml up`
   - **Port:** 4000

## כתובות גישה בענן

### אחרי פריסה:
- **האפליקציה:** `http://your-server-ip`
- **או:** `http://your-domain.com`
- **או:** `https://your-domain.com` (עם SSL)

### דוגמאות:
- `http://192.168.1.100` (IP מקומי)
- `http://35.123.45.67` (IP ציבורי)
- `https://myapp.com` (דומיין)

## הגדרת דומיין

### 1. רכישת דומיין
- Namecheap, GoDaddy, או כל ספק אחר

### 2. הגדרת DNS
```
A Record: @ -> your-server-ip
A Record: www -> your-server-ip
```

### 3. הוספת SSL (Let's Encrypt)
```bash
# התקנת Certbot
apt install certbot python3-certbot-nginx

# יצירת SSL
certbot --nginx -d your-domain.com
```

## אבטחה

### 1. Firewall
```bash
# פתיחת פורטים נדרשים
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

### 2. משתני סביבה
```bash
# יצירת קובץ .env
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
PORT=4000
FLASK_ENV=production
EOF
```

### 3. עדכון סיסמאות
```bash
# עדכון סיסמת PostgreSQL
docker-compose -f docker-compose.prod.yml exec db psql -U postgres -c "ALTER USER postgres PASSWORD 'new-password';"
```

## ניהול השירותים

### פקודות שימושיות:
```bash
# צפייה בסטטוס
docker-compose -f docker-compose.prod.yml ps

# צפייה בלוגים
docker-compose -f docker-compose.prod.yml logs -f

# צפייה בלוגים של שירות ספציפי
docker-compose -f docker-compose.prod.yml logs -f web
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f ollama

# עצירת השירותים
docker-compose -f docker-compose.prod.yml down

# הפעלה מחדש
docker-compose -f docker-compose.prod.yml restart

# עדכון קוד
git pull
docker-compose -f docker-compose.prod.yml up -d --build

# גיבוי מסד נתונים
docker-compose -f docker-compose.prod.yml exec db pg_dump -U postgres investments > backup.sql

# שחזור מסד נתונים
docker-compose -f docker-compose.prod.yml exec -T db psql -U postgres investments < backup.sql
```

## ניטור וביצועים

### 1. בדיקת זיכרון
```bash
docker stats
```

### 2. בדיקת לוגים
```bash
# לוגים של Nginx
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/access.log

# לוגים של האפליקציה
docker-compose -f docker-compose.prod.yml logs -f web
```

### 3. בדיקת בריאות
```bash
curl http://your-domain.com/health
```

## פתרון בעיות

### בעיה: האפליקציה לא נגישה
```bash
# בדיקת שירותים
docker-compose -f docker-compose.prod.yml ps

# בדיקת לוגים
docker-compose -f docker-compose.prod.yml logs -f

# בדיקת פורטים
netstat -tlnp | grep :80
```

### בעיה: זיכרון לא מספיק
```bash
# בדיקת זיכרון
free -h
docker stats

# עדכון מגבלות
# ערוך docker-compose.prod.yml והקטן memory limits
```

### בעיה: מודל לא נטען
```bash
# בדיקת לוגים של Ollama
docker-compose -f docker-compose.prod.yml logs ollama

# הורדה ידנית
docker-compose -f docker-compose.prod.yml exec ollama ollama pull llama3.1:8b
```

## גיבוי ושחזור

### גיבוי יומי:
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U postgres investments > backup_$DATE.sql
gzip backup_$DATE.sql
```

### הוספה ל-cron:
```bash
# עריכת crontab
crontab -e

# הוספת גיבוי יומי בשעה 2:00
0 2 * * * /path/to/backup.sh
```

## תמיכה

לבעיות נוספות:
1. בדוק את הלוגים: `docker-compose -f docker-compose.prod.yml logs -f`
2. בדוק זיכרון: `docker stats`
3. בדוק רשת: `docker network ls`
4. פנה לעזרה עם הלוגים המלאים 