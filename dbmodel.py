import sqlite3  # מביא כלים לעבודה עם בסיס נתונים פשוט
import threading  # מביא כלים לעבודה עם כמה דברים במקביל

class PortfolioModel:  # הקלאס שמנהל את בסיס הנתונים של התיק
    def __init__(self):  # פונקציה שרצה כשיוצרים דבר חדש מהקלאס הזה
        self.db_name = "investments.db"  # שם הקובץ שבו נשמרות כל ההשקעות
        self.create_tables()  # קוראת לפונקציה שיוצרת את הטבלאות
    
    def get_connection(self):  # פונקציה שיוצרת חיבור חדש לבסיס הנתונים
        """יוצר חיבור חדש לבסיס הנתונים"""
        # יוצר חיבור חדש לבסיס הנתונים
        conn = sqlite3.connect(self.db_name, check_same_thread=False)
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

    def add_security(self, name, price, industry, variance, security_type):  # פונקציה להוספת נייר ערך חדש
        # מקבלת פרטי נייר ערך ומוסיפה אותו למסד הנתונים
        conn = self.get_connection()  # מקבל חיבור למסד הנתונים
        cursor = conn.cursor()  # יוצר סמן לביצוע פעולות
        try:  # מנסה לבצע את הפעולה
            # מכניס נייר ערך חדש לטבלה עם כל הפרטים
            cursor.execute("INSERT INTO investments (name, price, industry, variance, security_type) VALUES (?, ?, ?, ?, ?)",
                                (name, price, industry, variance, security_type))
            conn.commit()  # שומר את השינויים במסד הנתונים
        except sqlite3.IntegrityError:  # אם יש שגיאה (כנראה כי הנייר ערך כבר קיים)
            print("נייר הערך כבר קיים בתיק ההשקעות.")  # מדפיס הודעת שגיאה
        finally:  # בכל מקרה בסוף
            conn.close()  # סוגר את החיבור למסד הנתונים

    def remove_security(self, name):  # פונקציה למחיקת נייר ערך מהתיק
        conn = self.get_connection()  # מקבל חיבור למסד הנתונים
        cursor = conn.cursor()  # יוצר סמן לביצוע פעולות
        # מוחק את נייר הערך מהטבלה לפי השם
        cursor.execute("DELETE FROM investments WHERE name = ?", (name,))
        conn.commit()  # שומר את השינויים במסד הנתונים
        conn.close()  # סוגר את החיבור למסד הנתונים

    def get_securities(self):  # פונקציה לשליפת כל ניירות הערך מהתיק
        conn = self.get_connection()  # מקבל חיבור למסד הנתונים
        cursor = conn.cursor()  # יוצר סמן לביצוע פעולות
        # שולף את השם והמחיר של כל ניירות הערך מהטבלה
        cursor.execute("SELECT name, price FROM investments")
        results = cursor.fetchall()  # מקבל את כל התוצאות כרשימה
        conn.close()  # סוגר את החיבור למסד הנתונים
        return results  # מחזיר את רשימת ניירות הערך
    
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