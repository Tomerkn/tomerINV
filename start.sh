#!/bin/bash

# סקריפט הפעלה לאפליקציה
echo "=== התחלת הפעלת האפליקציה ==="

# בדיקת משתני סביבה
echo "PORT: $PORT"
echo "DATABASE_URL: $DATABASE_URL"
echo "OLLAMA_URL: $OLLAMA_URL"

# הגדרת פורט ברירת מחדל אם לא מוגדר
if [ -z "$PORT" ]; then
    export PORT=4000
    echo "הגדרת פורט ברירת מחדל: $PORT"
fi

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

# הזרקת נתוני דוגמה אם המסד ריק
echo "=== בדיקת תוכן מסד הנתונים ==="
python -c "
import os
import sys
sys.path.append('/app')
from dbmodel import PortfolioModel
model = PortfolioModel()
securities = model.get_all_securities()
if not securities:
    print('מסד הנתונים ריק - מזריק נתוני דוגמה...')
    from inject_sample_data import inject_sample_data
    inject_sample_data()
    print('נתוני דוגמה הוזרקו בהצלחה')
else:
    print(f'מסד הנתונים מכיל {len(securities)} ניירות ערך')
"

# הפעלת האפליקציה המלאה
echo "=== הפעלת האפליקציה המלאה על פורט $PORT ==="
exec gunicorn --bind 0.0.0.0:$PORT --timeout 30 --workers 4 --preload --access-logfile - --error-logfile - app:app 