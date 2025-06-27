#!/bin/bash

echo "הפעלת שירותי מערכת ניהול תיק השקעות"
echo "======================================"

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

echo "מתחיל שירותים..."

# הפעלת PostgreSQL
echo "מפעיל PostgreSQL..."
docker-compose up -d postgres

# המתנה שהמסד יהיה זמין
sleep 5

# בדיקת PostgreSQL
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "PostgreSQL פועל בהצלחה"
else
    echo "בעיה עם PostgreSQL"
fi

# הפעלת Ollama
echo "מפעיל Ollama..."
docker-compose up -d ollama

# המתנה ש-Ollama יהיה זמין
sleep 10

# בדיקת Ollama
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "Ollama פועל בהצלחה"
else
    echo "בעיה עם Ollama"
fi

# הפעלת Flask App
echo "מפעיל Flask App..."
docker-compose up -d web

# המתנה שהאפליקציה תהיה זמינה
sleep 5

# בדיקת Flask App
if curl -s http://localhost:8080/health > /dev/null; then
    echo "Flask App פועל בהצלחה"
else
    echo "בעיה עם Flask App"
fi

echo ""
echo "כל השירותים פועלים!"
echo "האפליקציה: http://localhost:8080"
echo ""
echo "Ollama: http://localhost:11434" 