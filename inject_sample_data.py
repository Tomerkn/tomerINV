# סקריפט להזרקת נתוני דוגמה ישירות למסד הנתונים בענן (PostgreSQL)
# עובד גם מקומית אם רוצים
# מריץ אותו פעם אחת וזהו

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# נתוני דוגמה
sample_securities = [
    ("אפל", 10, 150.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
    ("גוגל", 5, 2800.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
    ("אגח ממשלתי", 100, 100.0, "פיננסים", "נמוך", "אגח ממשלתית"),
    ("טסלה", 3, 800.0, "תחבורה", "גבוה", "מניה רגילה"),
    ("מיקרוסופט", 8, 300.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
    ("אמזון", 2, 1500.0, "טכנולוגיה", "גבוה", "מניה רגילה")
]

# מקבל את כתובת המסד מהסביבה או מהמשתמש
DATABASE_URL = os.environ.get('DATABASE_URL')
if not DATABASE_URL:
    DATABASE_URL = input("הכנס את כתובת ה-DATABASE_URL שלך (Postgres): ")

print(f"מתחבר ל-DB: {DATABASE_URL}")

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    # מוודא שהטבלה קיימת
    cur.execute('''
        CREATE TABLE IF NOT EXISTS investments (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            industry VARCHAR(100),
            variance VARCHAR(50),
            security_type VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    print("הטבלה investments קיימת!")

    # בודק אם יש כבר נתונים
    cur.execute("SELECT COUNT(*) FROM investments")
    count = cur.fetchone()[0]
    if count > 0:
        print(f"כבר יש {count} ניירות ערך במסד. לא מוזרקים נתונים כפולים.")
    else:
        for name, amount, price, industry, variance, security_type in sample_securities:
            cur.execute(
                """
                INSERT INTO investments (name, amount, price, industry, variance, security_type)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (name) DO NOTHING
                """,
                (name, amount, price, industry, variance, security_type)
            )
            print(f"נוסף: {name}")
        conn.commit()
        print("הנתונים הוזרקו בהצלחה!")
    cur.close()
    conn.close()
except Exception as e:
    print(f"שגיאה: {e}") 