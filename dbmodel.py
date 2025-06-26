import sqlite3  # מביא כלים לעבודה עם בסיס נתונים פשוט
import threading  # מביא כלים לעבודה עם כמה דברים במקביל
import os
from datetime import datetime

class PortfolioModel:  # הקלאס שמנהל את בסיס הנתונים של התיק
    """מחלקה שמנהלת את מסד הנתונים של תיק ההשקעות"""
    
    def __init__(self):
        """יוצר את מסד הנתונים"""
        # שימוש במסד נתונים בענן או מקומי
        db_path = os.environ.get('DATABASE_URL', 'investments.db')
        if db_path.startswith('postgres://'):
            # אם זה PostgreSQL, נשתמש ב-SQLite כרגע
            db_path = 'investments.db'
        
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """יוצר את הטבלאות במסד הנתונים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # טבלת ניירות ערך
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS securities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
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
    
    def add_security(self, name, amount, price, industry, variance, security_type):
        """מוסיף נייר ערך חדש למסד הנתונים"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO securities (name, amount, price, industry, variance, security_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, amount, price, industry, variance, security_type))
        
        conn.commit()
        conn.close()
        return f"נייר הערך {name} נוסף בהצלחה"
    
    def get_all_securities(self):
        """מחזיר את כל ניירות הערך"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM securities')
        securities = cursor.fetchall()
        
        conn.close()
        
        # ממיר לרשימת מילונים
        result = []
        for sec in securities:
            result.append({
                'id': sec[0],
                'name': sec[1],
                'amount': sec[2],
                'price': sec[3],
                'industry': sec[4],
                'variance': sec[5],
                'security_type': sec[6],
                'created_at': sec[7]
            })
        
        return result
    
    def update_price(self, name, new_price):
        """מעדכן מחיר של נייר ערך"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE securities SET price = ? WHERE name = ?', (new_price, name))
        
        conn.commit()
        conn.close()
    
    def remove_security(self, name):
        """מוחק נייר ערך מהמסד"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM securities WHERE name = ?', (name,))
        
        conn.commit()
        conn.close()

    def get_connection(self):  # פונקציה שיוצרת חיבור חדש לבסיס הנתונים
        """יוצר חיבור חדש לבסיס הנתונים"""
        # יוצר חיבור חדש לבסיס הנתונים
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return conn  # מחזיר את החיבור
    
    def create_tables(self):  # פונקציה שיוצרת את הטבלה במסד הנתונים אם היא לא קיימת
        conn = self.get_connection()  # מקבל חיבור למסד הנתונים
        cursor = conn.cursor()  # יוצר סמן לביצוע פעולות על מסד הנתונים
        # יוצר טבלה חדשה בשם investments אם היא לא קיימת כבר
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS investments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- מזהה ייחודי שעולה אוטומטית לכל נייר ערך
                name TEXT UNIQUE,  -- שם המניה או האג"ח (חייב להיות ייחודי)
                price REAL,  -- מחיר המניה במספר עשרוני
                amount REAL,  -- כמות המניות שנרכשו במספר עשרוני
                industry TEXT,  -- הענף שאליו שייך נייר הערך (טכנולוגיה, בנקאות וכו')
                variance TEXT,  -- רמת השונות במחיר (נמוך/גבוה)
                security_type TEXT  -- סוג נייר הערך (מניה רגילה, אג"ח ממשלתי וכו')
            )
        ''')
        conn.commit()  # שומר את השינויים במסד הנתונים בקובץ
        conn.close()  # סוגר את החיבור למסד הנתונים

    def execute_query(self, query, params=None):  # פונקציה כללית לביצוע כל סוג של שאילתה
        """פונקציה כללית לביצוע שאילתות - מאפשרת להריץ כל פקודת SQL"""
        conn = self.get_connection()  # מקבל חיבור למסד הנתונים
        cursor = conn.cursor()  # יוצר סמן לביצוע פעולות
        if params:  # אם יש פרמטרים נוספים לשאילתה
            cursor.execute(query, params)  # מריץ את השאילתה עם הפרמטרים
        else:  # אם אין פרמטרים
            cursor.execute(query)  # מריץ את השאילתה בלי פרמטרים

        # בודק אם זו שאילתת בחירה (SELECT) שמחזירה תוצאות
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()  # מקבל את כל התוצאות
            conn.close()  # סוגר את החיבור
            return results  # מחזיר את התוצאות
        else:  # אם זו פעולת עדכון, הוספה או מחיקה
            conn.commit()  # שומר את השינויים במסד הנתונים
            conn.close()  # סוגר את החיבור
            return None  # לא מחזיר כלום 