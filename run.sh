#!/bin/bash

# סקריפט הפעלה מהיר לאפליקציה עם Docker
echo "=== הפעלת אפליקציית ניהול תיק השקעות ==="
echo "=== תאריך: $(date) ==="

# בדיקת Docker
if ! command -v docker &> /dev/null; then
    echo "שגיאה: Docker לא מותקן"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "שגיאה: Docker Compose לא מותקן"
    exit 1
fi

# עצירת שירותים קיימים
echo "=== עצירת שירותים קיימים ==="
docker-compose down

# בנייה והפעלה
echo "=== בנייה והפעלת השירותים ==="
docker-compose up -d --build

# המתנה קצרה
echo "=== ממתין לאתחול השירותים ==="
sleep 10

# בדיקת סטטוס
echo "=== בדיקת סטטוס השירותים ==="
docker-compose ps

echo ""
echo "=== האפליקציה מוכנה! ==="
echo "כתובת האפליקציה: http://localhost:4000"
echo "כתובת Ollama: http://localhost:11434"
echo ""
echo "לצפייה בלוגים: docker-compose logs -f"
echo "לעצירה: docker-compose down" 