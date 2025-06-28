#!/bin/bash

echo "עצירת שירותי מערכת ניהול תיק השקעות"
echo "======================================"

# עצירת כל השירותים
echo "עוצר שירותים..."
docker-compose down

echo "כל השירותים נעצרו"

# מחיקת נתונים (אופציונלי)
echo "האם למחוק את כל הנתונים? (y/n)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    echo "מוחק נתונים..."
    docker-compose down -v
    docker system prune -f
    echo "כל הנתונים נמחקו"
fi

echo "המערכת נעצרה בהצלחה"

git push origin main 