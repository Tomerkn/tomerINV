# זה הקובץ שמנהל את כל הנתונים של התיק – שומר, מוסיף, מוחק, מעדכן, הכל
# אפשר לעבוד עם קובץ במחשב (SQLite) או עם מסד נתונים בענן (PostgreSQL)

print("=== התחלת טעינת dbmodel.py ===")

import sqlite3  # פה אני מביא כלי שמאפשר לי לשמור נתונים בקובץ במחשב
import os  # כלי לעבודה עם קבצים וסביבה

print("=== ייבוא sqlite3 ו-os הושלם ===")

# פה אני מנסה להביא חיבור למסד נתונים בענן (PostgreSQL), ואם אין – עובד רגיל
try:
    import psycopg2  # זה בשביל לעבוד עם מסד נתונים בענן
    import psycopg2.extras
    import sqlalchemy
    POSTGRES_AVAILABLE = True
    print("ספריות PostgreSQL זמינות")
except ImportError:
    POSTGRES_AVAILABLE = False
    print("ספריות PostgreSQL לא זמינות")

print("=== סיום בדיקת זמינות PostgreSQL ===")

class PortfolioModel:  # פה אני יוצר מחלקה שמנהלת את כל הנתונים של התיק שלי
    """פה אני שומר את כל המידע של התיק – מניות, אג"חים, מחירים, כמויות וכו'"""

    def __init__(self):
        """פה אני בודק אם יש מסד נתונים בענן, ואם לא – עובד עם קובץ במחשב"""
        print("=== התחלת יצירת PortfolioModel ===")
        self.db_url = os.environ.get('DATABASE_URL')  # כתובת למסד בענן (אם יש)
        print(f"DATABASE_URL מהסביבה: {self.db_url}")
        self.use_postgres = False  # האם לעבוד בענן או לא
        if self.db_url and POSTGRES_AVAILABLE:
            try:
                if self.db_url.startswith('postgres://') or \
                   self.db_url.startswith('postgresql://'):
                    self.use_postgres = True  # עובד בענן
                    print("משתמש ב-PostgreSQL בענן")
                else:
                    self.db_url = 'investments.db'  # עובד מקומי
                    print("משתמש ב-SQLite מקומי")
            except Exception as e:
                print(f"שגיאה בבדיקת DATABASE_URL: {e}")
                self.db_url = 'investments.db'
                print("משתמש ב-SQLite מקומי")
        else:
            self.db_url = 'investments.db'
            print("משתמש ב-SQLite מקומי")
        print("=== סיום יצירת PortfolioModel ===")
        self.init_db()  # יוצר את הטבלאות אם צריך

    def get_connection(self):
        """פה אני פותח חיבור למסד הנתונים (או קובץ או ענן)"""
        print("=== התחלת get_connection ===")
        if self.use_postgres:
            print(f"מתחבר ל-Postgres עם SQLAlchemy: {self.db_url}")
            try:
                engine = sqlalchemy.create_engine(self.db_url)
                connection = engine.raw_connection()
                print("חיבור ל-Postgres הצליח")
                return connection
            except Exception as e:
                print(f"שגיאה בחיבור ל-Postgres: {e}")
                raise
        else:
            print(f"מתחבר ל-SQLite: {self.db_url}")
            try:
                connection = sqlite3.connect(self.db_url, check_same_thread=False)
                print("חיבור ל-SQLite הצליח")
                return connection
            except Exception as e:
                print(f"שגיאה בחיבור ל-SQLite: {e}")
                raise

    def init_db(self):
        """פה אני יוצר את הטבלאות אם הן לא קיימות – פעם אחת וזהו"""
        print("=== התחלת init_db ===")
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if self.use_postgres:
                # פה אני יוצר טבלה בענן
                print("יוצר טבלה ב-Postgres")
                cursor.execute('''
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
            else:
                # פה אני יוצר טבלה בקובץ במחשב
                print("יוצר טבלה ב-SQLite")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        amount REAL NOT NULL,
                        price REAL NOT NULL,
                        industry TEXT,
                        variance TEXT,
                        security_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            conn.commit()
            conn.close()
            print("טבלאות נוצרו בהצלחה")
        except Exception as e:
            print(f"שגיאה ביצירת טבלאות: {e}")
            raise

    def add_security(self, name, amount, price, industry, variance, security_type):
        """פה אני מוסיף מניה/אג"ח חדשה לתיק"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if self.use_postgres:
            cursor.execute('''
                INSERT INTO investments (name, amount, price, industry, variance, security_type)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (name, amount, price, industry, variance, security_type))
        else:
            cursor.execute('''
                INSERT INTO investments (name, amount, price, industry, variance, security_type)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, amount, price, industry, variance, security_type))
        conn.commit()
        conn.close()
        return f"נייר הערך {name} נוסף בהצלחה"

    def get_all_securities(self):
        """פה אני מחזיר את כל המניות והאג"חים שיש לי בתיק, כמו רשימה בסופר"""
        print("=== התחלת get_all_securities ===")
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM investments')
            securities = cursor.fetchall()
            conn.close()
            result = []
            for sec in securities:
                result.append({
                    'id': sec[0],
                    'name': sec[1],
                    'amount': float(sec[2]),
                    'price': float(sec[3]),
                    'industry': sec[4],
                    'variance': sec[5],
                    'security_type': sec[6],
                    'created_at': sec[7] if len(sec) > 7 else None
                })
            print(f"נמצאו {len(result)} ניירות ערך")
            return result
        except Exception as e:
            print(f"שגיאה ב-get_all_securities: {e}")
            raise

    def update_price(self, name, new_price):
        """פה אני מעדכן מחיר של מניה/אג"ח לפי שם"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if self.use_postgres:
            cursor.execute('UPDATE investments SET price = %s WHERE name = %s',
                           (new_price, name))
        else:
            cursor.execute('UPDATE investments SET price = ? WHERE name = ?',
                           (new_price, name))
        conn.commit()
        conn.close()

    def remove_security(self, name):
        """פה אני מוחק מניה/אג"ח מהתיק לפי שם"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if self.use_postgres:
            cursor.execute('DELETE FROM investments WHERE name = %s', (name,))
        else:
            cursor.execute('DELETE FROM investments WHERE name = ?', (name,))
        conn.commit()
        conn.close()

    def create_tables(self):
        """פה אני דואג שתמיד יהיו טבלאות במסד (למקרה שמריצים על מסד ריק)"""
        print("=== התחלת create_tables ===")
        try:
            self.init_db()
            print("create_tables הושלם בהצלחה")
        except Exception as e:
            print(f"שגיאה ב-create_tables: {e}")
            raise

    def execute_query(self, query, params=None):
        """פה אני מריץ כל פקודת SQL שצריך – בחירה, עדכון, מחיקה וכו'"""
        conn = self.get_connection()
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            conn.close()
            return results
        else:
            conn.commit()
            conn.close()
            return None 

print("=== סיום טעינת dbmodel.py ===") 