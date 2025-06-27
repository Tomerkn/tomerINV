#!/bin/bash

echo "=== עצירת מערכת ההשקעות ==="

# עצירת כל השירותים
docker-compose down

echo "✅ כל השירותים נעצרו"

# מחיקת volumes (אופציונלי)
read -p "האם למחוק את כל הנתונים? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "מחיקת volumes..."
    docker-compose down -v
    echo "✅ כל הנתונים נמחקו"
fi

echo "=== מערכת ההשקעות נעצרה ===" 