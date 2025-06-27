#!/bin/bash

# סקריפט הפעלה לאפליקציה
echo "=== התחלת הפעלת האפליקציה ==="

# בדיקת משתני סביבה
echo "PORT: $PORT"
echo "DATABASE_URL: $DATABASE_URL"
echo "OLLAMA_URL: $OLLAMA_URL"

# יצירת טבלאות במסד הנתונים
echo "=== יצירת טבלאות במסד הנתונים ==="
python -c "
import os
import sys
sys.path.append('/app')
from dbmodel import PortfolioModel
model = PortfolioModel()
model.create_tables()
print('טבלאות נוצרו בהצלחה')
"

# הפעלת האפליקציה
echo "=== הפעלת האפליקציה ==="
exec gunicorn --bind 0.0.0.0:$PORT --timeout 30 --workers 4 --preload --access-logfile - --error-logfile - app:app 