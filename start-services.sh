#!/bin/bash

echo "=== התחלת הפעלת מערכת ההשקעות ==="
echo "מערכת עם 3 שירותים נפרדים:"
echo "1. Flask App (inv_web01)"
echo "2. PostgreSQL (inv_db_Postgres)" 
echo "3. Ollama (ollama)"

# בדיקה אם Docker מותקן
if ! command -v docker &> /dev/null; then
    echo "שגיאה: Docker לא מותקן!"
    exit 1
fi

# בדיקה אם Docker Compose מותקן
if ! command -v docker-compose &> /dev/null; then
    echo "שגיאה: Docker Compose לא מותקן!"
    exit 1
fi

echo "=== בונה ומפעיל את כל השירותים ==="

# בנייה והפעלה של כל השירותים
docker-compose up --build -d

echo "=== המתן להפעלת השירותים ==="
sleep 10

# בדיקת סטטוס השירותים
echo "=== בדיקת סטטוס השירותים ==="
docker-compose ps

echo "=== בדיקת חיבור למסד נתונים ==="
sleep 5

# בדיקת חיבור למסד נתונים
if docker-compose exec postgres pg_isready -U postgres; then
    echo "✅ PostgreSQL פועל בהצלחה"
else
    echo "❌ בעיה עם PostgreSQL"
fi

echo "=== בדיקת חיבור ל-Ollama ==="
sleep 5

# בדיקת חיבור ל-Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama פועל בהצלחה"
else
    echo "❌ בעיה עם Ollama"
fi

echo "=== בדיקת חיבור לאפליקציה ==="
sleep 5

# בדיקת חיבור לאפליקציה
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Flask App פועל בהצלחה"
else
    echo "❌ בעיה עם Flask App"
fi

echo ""
echo "=== מערכת ההשקעות מוכנה! ==="
echo "🌐 האפליקציה: http://localhost:8080"
echo "🗄️  PostgreSQL: localhost:5432"
echo "🤖 Ollama: http://localhost:11434"
echo ""
echo "פקודות שימושיות:"
echo "  docker-compose logs -f flask-app    # לוגים של האפליקציה"
echo "  docker-compose logs -f postgres     # לוגים של מסד הנתונים"
echo "  docker-compose logs -f ollama       # לוגים של Ollama"
echo "  docker-compose down                 # עצירת כל השירותים"
echo "  docker-compose restart flask-app    # הפעלה מחדש של האפליקציה" 