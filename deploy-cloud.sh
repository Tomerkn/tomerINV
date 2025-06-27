#!/bin/bash

# סקריפט פריסה לענן
echo "=== פריסת אפליקציה לענן ==="
echo "=== תאריך: $(date) ==="

# צבעים
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# בדיקת משתני סביבה
print_status "בדיקת משתני סביבה..."

# הגדרת משתנים ברירת מחדל
export PORT=${PORT:-4000}
export SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}

print_info "PORT: $PORT"
print_info "SECRET_KEY: ${SECRET_KEY:0:10}..."

# בדיקת Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker לא מותקן"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose לא מותקן"
    exit 1
fi

# ניקוי סביבה קיימת
print_status "ניקוי סביבה קיימת..."
docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true
docker system prune -f

# בניית הפרויקט
print_status "בניית הפרויקט..."
docker-compose -f docker-compose.prod.yml build --no-cache

# הפעלת השירותים
print_status "הפעלת השירותים..."
docker-compose -f docker-compose.prod.yml up -d

# המתנה לאתחול
print_status "ממתין לאתחול השירותים..."
sleep 45

# בדיקת סטטוס
print_status "בדיקת סטטוס השירותים..."
docker-compose -f docker-compose.prod.yml ps

# בדיקת זיכרון
print_status "בדיקת שימוש זיכרון..."
docker stats --no-stream

# קבלת כתובת IP של השרת
print_status "קבלת כתובת השרת..."
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || echo "localhost")
print_info "כתובת השרת: $SERVER_IP"

# בדיקת האפליקציה
print_status "בדיקת האפליקציה..."
sleep 10

# בדיקה עם curl
if curl -s http://localhost > /dev/null; then
    print_status "האפליקציה זמינה!"
else
    print_warning "האפליקציה עדיין לא זמינה. בדוק את הלוגים..."
fi

echo ""
echo "=== פריסה הושלמה! ==="
echo ""
echo "כתובות גישה:"
echo "- האפליקציה: http://$SERVER_IP"
echo "- האפליקציה (מקומי): http://localhost"
echo "- Ollama API: http://$SERVER_IP:11434 (אם חשוף)"
echo "- PostgreSQL: $SERVER_IP:5432 (אם חשוף)"
echo ""
echo "פקודות שימושיות:"
echo "- צפייה בלוגים: docker-compose -f docker-compose.prod.yml logs -f"
echo "- עצירת השירותים: docker-compose -f docker-compose.prod.yml down"
echo "- הפעלה מחדש: docker-compose -f docker-compose.prod.yml restart"
echo "- עדכון קוד: docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "משתמשים לדוגמה:"
echo "- admin / admin123"
echo "- demo_user / password123"
echo ""
echo "הערות חשובות:"
echo "1. האפליקציה רצה על פורט 80 (HTTP)"
echo "2. מומלץ להוסיף SSL/HTTPS"
echo "3. שנה את SECRET_KEY בסביבת ייצור"
echo "4. הגדר firewall לפתיחת פורט 80" 