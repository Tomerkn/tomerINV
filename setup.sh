#!/bin/bash

# סקריפט התקנה מלא לאפליקציית ניהול תיק השקעות
echo "=== התקנת אפליקציית ניהול תיק השקעות ==="
echo "=== תאריך: $(date) ==="

# צבעים להודעות
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# פונקציה להדפסת הודעות
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# בדיקת מערכת הפעלה
print_status "בדיקת מערכת הפעלה..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    print_status "מערכת macOS זוהתה"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_status "מערכת Linux זוהתה"
else
    print_error "מערכת הפעלה לא נתמכת: $OSTYPE"
    exit 1
fi

# בדיקת Homebrew (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    if ! command -v brew &> /dev/null; then
        print_error "Homebrew לא מותקן. אנא התקן Homebrew תחילה"
        exit 1
    fi
    print_status "Homebrew זמין"
fi

# התקנת Docker
print_status "בדיקת Docker..."
if ! command -v docker &> /dev/null; then
    print_warning "Docker לא מותקן. מתחיל התקנה..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        print_status "התקנת Docker Desktop..."
        brew install --cask docker
        
        print_status "הפעלת Docker Desktop..."
        open /Applications/Docker.app
        
        print_warning "אנא המתן עד ש-Docker Desktop יסיים להתחיל (סמל הדולפין יהיה ירוק)"
        print_warning "לחץ Enter כשתסיים..."
        read -r
    else
        print_error "התקנת Docker על Linux דורשת הרשאות root"
        exit 1
    fi
else
    print_status "Docker כבר מותקן"
fi

# בדיקת Docker Compose
print_status "בדיקת Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose לא מותקן. מתחיל התקנה..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install docker-compose
    fi
else
    print_status "Docker Compose זמין"
fi

# המתנה ל-Docker
print_status "ממתין ל-Docker..."
until docker info &> /dev/null; do
    print_warning "Docker עדיין לא זמין. ממתין..."
    sleep 5
done
print_status "Docker זמין!"

# ניקוי סביבה קיימת
print_status "ניקוי סביבה קיימת..."
docker-compose down -v 2>/dev/null || true
docker system prune -f

# בניית הפרויקט
print_status "בניית הפרויקט..."
docker-compose build --no-cache

# הפעלת השירותים
print_status "הפעלת השירותים..."
docker-compose up -d

# המתנה לאתחול
print_status "ממתין לאתחול השירותים..."
sleep 30

# בדיקת סטטוס
print_status "בדיקת סטטוס השירותים..."
docker-compose ps

# בדיקת זיכרון
print_status "בדיקת שימוש זיכרון..."
docker stats --no-stream

# בדיקת האפליקציה
print_status "בדיקת האפליקציה..."
sleep 10
if curl -s http://localhost:4000 > /dev/null; then
    print_status "האפליקציה זמינה!"
else
    print_warning "האפליקציה עדיין לא זמינה. בדוק את הלוגים..."
fi

echo ""
echo "=== התקנה הושלמה! ==="
echo ""
echo "כתובות גישה:"
echo "- האפליקציה: http://localhost:4000"
echo "- Ollama API: http://localhost:11434"
echo "- PostgreSQL: localhost:5432"
echo ""
echo "פקודות שימושיות:"
echo "- צפייה בלוגים: docker-compose logs -f"
echo "- עצירת השירותים: docker-compose down"
echo "- הפעלה מחדש: docker-compose restart"
echo "- עדכון קוד: docker-compose up -d --build"
echo ""
echo "משתמשים לדוגמה:"
echo "- admin / admin123"
echo "- demo_user / password123" 