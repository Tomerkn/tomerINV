#!/bin/bash

# סקריפט הפעלה לאפליקציה בסביבת Docker
echo "=== התחלת הפעלת האפליקציה בסביבת Docker ==="
echo "=== תאריך בנייה: $(date) ==="

# בדיקת משתני סביבה
echo "PORT: $PORT"
echo "DATABASE_URL: $DATABASE_URL"
echo "OLLAMA_URL: $OLLAMA_URL"

# הגדרת פורט ברירת מחדל אם לא מוגדר
if [ -z "$PORT" ]; then
    export PORT=4000
    echo "הגדרת פורט ברירת מחדל: $PORT"
fi

# המתנה למסד הנתונים
echo "=== ממתין למסד הנתונים PostgreSQL ==="
until python -c "
import psycopg2
import os
import time
try:
    conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
    conn.close()
    print('מסד הנתונים זמין!')
    exit(0)
except:
    print('מסד הנתונים עדיין לא זמין...')
    exit(1)
"; do
    echo "ממתין למסד הנתונים..."
    sleep 5
done

# המתנה ל-Ollama
echo "=== ממתין ל-Ollama ==="
until curl -s http://ollama:11434/api/tags > /dev/null; do
    echo "ממתין ל-Ollama..."
    sleep 5
done

# יצירת טבלאות במסד הנתונים
echo "=== יצירת טבלאות במסד הנתונים ==="
python -c "
import os
import sys
sys.path.append('/app')
try:
    from dbmodel import PortfolioModel
    model = PortfolioModel()
    model.create_tables()
    print('טבלאות נוצרו בהצלחה')
except Exception as e:
    print(f'שגיאה ביצירת טבלאות: {e}')
"

# הזרקת נתוני דוגמה אם המסד ריק
echo "=== בדיקת תוכן מסד הנתונים ==="
python -c "
import os
import sys
sys.path.append('/app')
try:
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
except Exception as e:
    print(f'שגיאה בבדיקת מסד הנתונים: {e}')
"

# הפעלת האפליקציה
echo "=== הפעלת האפליקציה על פורט $PORT ==="
echo "=== האפליקציה זמינה ב: http://localhost:$PORT ==="
echo "=== Ollama זמין ב: http://localhost:11434 ==="

exec gunicorn --bind 0.0.0.0:$PORT --timeout 30 --workers 2 --preload --access-logfile - --error-logfile - app:app 