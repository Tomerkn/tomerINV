# -*- coding: utf-8 -*-
"""
dbmodel.py - מודל מסד הנתונים למערכת ניהול תיק השקעות
כאן מוגדרות כל הפונקציות לעבודה עם מסד הנתונים
"""

import os  # לעבודה עם משתני סביבה
import sqlite3  # לעבודה עם SQLite
import requests  # לבקשות HTTP למחירי מניות

# קבועים
USD_TO_ILS_RATE = 3.5  # שער המרה מדולר לשקל קבוע

# בדיקת PostgreSQL - האם הספרייה מותקנת
try:
    import psycopg2  # ספרייה לחיבור PostgreSQL
    POSTGRESQL_AVAILABLE = True  # PostgreSQL זמין
except ImportError:
    POSTGRESQL_AVAILABLE = False  # PostgreSQL לא זמין


class PortfolioModel:
    """מודל מסד הנתונים לניהול תיק השקעות - תומך PostgreSQL ו-SQLite"""
    
    def __init__(self):
        """אתחול מסד נתונים - PostgreSQL לשרת או SQLite למקומי"""
        self.db_path = "investments.db"  # נתיב קובץ SQLite מקומי
        
        # קבלת URL מסד נתונים מהסביבה (לשרת)
        database_url = os.environ.get('DATABASE_URL')
        
        if database_url:  # אם יש URL - עובדים עם PostgreSQL בשרת
            self.use_postgresql = True
            self.database_url = database_url
        else:  # אחרת עובדים עם SQLite במחשב המקומי
            self.use_postgresql = False
        
        self.init_db()  # אתחול טבלאות במסד הנתונים
    
    def get_connection(self):
        """יצירת חיבור למסד הנתונים - PostgreSQL או SQLite"""
        if self.use_postgresql:  # אם עובדים עם PostgreSQL
            try:
                from urllib.parse import urlparse  # לפירוק URL
                result = urlparse(self.database_url)  # פרק את ה-URL
                
                # התחבר ל-PostgreSQL עם הפרמטרים מה-URL
                conn = psycopg2.connect(
                    database=result.path[1:],  # שם מסד הנתונים (ללא /)
                    user=result.username,  # שם משתמש
                    password=result.password,  # סיסמה
                    host=result.hostname,  # כתובת שרת
                    port=result.port  # פורט
                )
                return conn
            except Exception as e:
                print(f"❌ שגיאה בחיבור ל-PostgreSQL: {e}")
                return None
        else:  # אם עובדים עם SQLite
            try:
                conn = sqlite3.connect(self.db_path)  # התחבר לקובץ SQLite
                conn.row_factory = sqlite3.Row  # החזר תוצאות כ-dictionary
                return conn
            except Exception as e:
                print(f"❌ שגיאה בחיבור ל-SQLite: {e}")
                return None
    
    def init_db(self):
        """יצירת טבלאות במסד הנתונים - משתמשים וניירות ערך"""
        conn = self.get_connection()  # קבל חיבור למסד
        if not conn:  # אם אין חיבור
            return
        
        cursor = conn.cursor()  # יצר cursor לביצוע פקודות SQL
        
        if self.use_postgresql:  # אם PostgreSQL
            # יצירת טבלת משתמשים עם PostgreSQL syntax
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role VARCHAR(20) DEFAULT 'user'
                )
            """)
            
            # יצירת טבלת ניירות ערך עם PostgreSQL syntax
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS securities (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    symbol VARCHAR(10),
                    amount DECIMAL(15,2) DEFAULT 0,
                    price DECIMAL(15,2) DEFAULT 0,
                    industry VARCHAR(50),
                    variance VARCHAR(20),
                    security_type VARCHAR(50)
                )
            """)
        else:  # אם SQLite
            # יצירת טבלת משתמשים עם SQLite syntax
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    role TEXT DEFAULT 'user'
                )
            """)
            
            # יצירת טבלת ניירות ערך עם SQLite syntax
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS securities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    symbol TEXT,
                    amount REAL DEFAULT 0,
                    price REAL DEFAULT 0,
                    industry TEXT,
                    variance TEXT,
                    security_type TEXT
                )
            """)
        
        conn.commit()  # שמור שינויים
        cursor.close()  # סגור cursor
        conn.close()  # סגור חיבור
    
    def create_tables(self):
        """אליאס למתודה init_db - יצירת טבלאות במסד הנתונים"""
        return self.init_db()
    
    def create_default_users(self):
        """יצירת משתמשי ברירת מחדל - admin ו-user"""
        conn = self.get_connection()  # קבל חיבור
        if not conn:
            return
        
        cursor = conn.cursor()  # יצר cursor
        
        # בדיקה אם המשתמש admin קיים כבר
        if self.use_postgresql:  # PostgreSQL syntax
            cursor.execute("SELECT id FROM users WHERE username = %s", ('admin',))
        else:  # SQLite syntax
            cursor.execute("SELECT id FROM users WHERE username = ?", ('admin',))
        
        if not cursor.fetchone():  # אם admin לא קיים
            if self.use_postgresql:  # הוסף admin ב-PostgreSQL
                query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
                cursor.execute(query, ('admin', 'admin', 'admin'))
            else:  # הוסף admin ב-SQLite
                query = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
                cursor.execute(query, ('admin', 'admin', 'admin'))
        
        # בדיקה אם המשתמש user קיים כבר
        if self.use_postgresql:  # PostgreSQL syntax
            cursor.execute("SELECT id FROM users WHERE username = %s", ('user',))
        else:  # SQLite syntax
            cursor.execute("SELECT id FROM users WHERE username = ?", ('user',))
        
        if not cursor.fetchone():  # אם user לא קיים
            if self.use_postgresql:  # הוסף user ב-PostgreSQL
                query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
                cursor.execute(query, ('user', 'user', 'user'))
            else:  # הוסף user ב-SQLite
                query = "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)"
                cursor.execute(query, ('user', 'user', 'user'))
        
        conn.commit()  # שמור שינויים
        cursor.close()  # סגור cursor
        conn.close()  # סגור חיבור
    
    def get_user_by_username(self, username):
        """קבלת משתמש לפי שם משתמש - לצורך התחברות"""
        conn = self.get_connection()  # קבל חיבור למסד
        if not conn:
            return None
        
        cursor = conn.cursor()  # יצר cursor
        
        if self.use_postgresql:  # PostgreSQL query
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        else:  # SQLite query
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        
        user = cursor.fetchone()  # קבל תוצאה ראשונה
        
        if user:  # אם נמצא משתמש
            if self.use_postgresql:  # המר ל-dictionary ב-PostgreSQL
                user_dict = dict(zip([desc[0] for desc in cursor.description], user))
            else:  # ב-SQLite זה כבר dictionary
                user_dict = dict(user)
        else:
            user_dict = None  # אם לא נמצא
        
        cursor.close()  # סגור cursor
        conn.close()  # סגור חיבור
        return user_dict  # החזר את נתוני המשתמש
    
    def get_user_by_id(self, user_id):
        """קבלת משתמש לפי ID - לצורך Flask-Login"""
        conn = self.get_connection()  # קבל חיבור למסד
        if not conn:
            return None
        
        cursor = conn.cursor()  # יצר cursor
        
        if self.use_postgresql:  # PostgreSQL query
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        else:  # SQLite query
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        
        user = cursor.fetchone()  # קבל תוצאה ראשונה
        
        if user:  # אם נמצא משתמש
            if self.use_postgresql:  # המר ל-dictionary ב-PostgreSQL
                user_dict = dict(zip([desc[0] for desc in cursor.description], user))
            else:  # ב-SQLite זה כבר dictionary
                user_dict = dict(user)
        else:
            user_dict = None  # אם לא נמצא
        
        cursor.close()  # סגור cursor
        conn.close()  # סגור חיבור
        return user_dict  # החזר את נתוני המשתמש
    
    def add_security(self, name, symbol, amount, price, industry, variance, security_type):
        """הוספת נייר ערך למסד הנתונים"""
        conn = self.get_connection()  # קבל חיבור למסד
        if not conn:
            return False
        
        cursor = conn.cursor()  # יצר cursor
        try:
            if self.use_postgresql:  # PostgreSQL syntax
                cursor.execute("""
                    INSERT INTO securities (name, symbol, amount, price, industry, variance, security_type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (name, symbol, amount, price, industry, variance, security_type))
            else:  # SQLite syntax
                cursor.execute("""
                    INSERT INTO securities (name, symbol, amount, price, industry, variance, security_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, symbol, amount, price, industry, variance, security_type))
            
            conn.commit()  # שמור שינויים
            return True  # הצלחה
        except Exception as e:
            print(f"❌ שגיאה בהוספת נייר ערך: {e}")
            return False  # כישלון
        finally:
            cursor.close()  # סגור cursor
            conn.close()  # סגור חיבור
    
    def get_all_securities(self):
        """קבלת כל ניירות הערך מהתיק - ממוין לפי שם"""
        conn = self.get_connection()  # קבל חיבור למסד
        if not conn:
            return []  # רשימה ריקה אם אין חיבור
        
        cursor = conn.cursor()  # יצר cursor
        cursor.execute("SELECT * FROM securities ORDER BY name")  # שאילתה ממוינת
        securities = cursor.fetchall()  # קבל את כל התוצאות
        
        if securities:  # אם יש תוצאות
            if self.use_postgresql:  # המר ל-dictionary list ב-PostgreSQL
                securities_list = [dict(zip([desc[0] for desc in cursor.description], row)) for row in securities]
            else:  # ב-SQLite זה כבר dictionary list
                securities_list = [dict(row) for row in securities]
        else:
            securities_list = []  # רשימה ריקה אם אין תוצאות
        
        cursor.close()  # סגור cursor
        conn.close()  # סגור חיבור
        return securities_list  # החזר את הרשימה
    
    def remove_security(self, name):
        """הסרת נייר ערך מהתיק לפי שם"""
        conn = self.get_connection()  # קבל חיבור למסד
        if not conn:
            return False
        
        cursor = conn.cursor()  # יצר cursor
        try:
            if self.use_postgresql:  # PostgreSQL syntax
                cursor.execute("DELETE FROM securities WHERE name = %s", (name,))
            else:  # SQLite syntax
                cursor.execute("DELETE FROM securities WHERE name = ?", (name,))
            
            conn.commit()  # שמור שינויים
            return cursor.rowcount > 0  # החזר True אם נמחק משהו
        except Exception as e:
            print(f"❌ שגיאה בהסרת נייר ערך: {e}")
            return False  # כישלון
        finally:
            cursor.close()  # סגור cursor
            conn.close()  # סגור חיבור
    
    def update_security_price(self, name, new_price):
        """עדכון מחיר נייר ערך קיים"""
        conn = self.get_connection()  # קבל חיבור למסד
        if not conn:
            return False
        
        cursor = conn.cursor()  # יצר cursor
        try:
            if self.use_postgresql:  # PostgreSQL syntax
                cursor.execute("UPDATE securities SET price = %s WHERE name = %s", (new_price, name))
            else:  # SQLite syntax
                cursor.execute("UPDATE securities SET price = ? WHERE name = ?", (new_price, name))
            
            conn.commit()  # שמור שינויים
            return True  # הצלחה
        except Exception as e:
            print(f"❌ שגיאה בעדכון מחיר: {e}")
            return False  # כישלון
        finally:
            cursor.close()  # סגור cursor
            conn.close()  # סגור חיבור
    
    def update_security_name(self, old_name, new_name):
        """עדכון שם נייר ערך - לשיפור שמות"""
        conn = self.get_connection()  # קבל חיבור למסד
        if not conn:
            return False
        
        cursor = conn.cursor()  # יצר cursor
        try:
            if self.use_postgresql:  # PostgreSQL syntax
                cursor.execute("UPDATE securities SET name = %s WHERE name = %s", (new_name, old_name))
            else:  # SQLite syntax
                cursor.execute("UPDATE securities SET name = ? WHERE name = ?", (new_name, old_name))
            
            conn.commit()  # שמור שינויים
            return cursor.rowcount > 0  # החזר True אם עודכן משהו
        except Exception as e:
            print(f"❌ שגיאה בעדכון שם נייר ערך: {e}")
            return False  # כישלון
        finally:
            cursor.close()  # סגור cursor
            conn.close()  # סגור חיבור


class Broker:
    """שירות קבלת מחירי מניות מ-API של Alpha Vantage"""
    
    # מפתחות API - מספר מפתחות לגיבוי
    API_KEYS = [
        "451FPPPSEOOZIDV4",  # מפתח ראשי
        "XX4SBD1SXLFLUSV2"   # מפתח גיבוי
    ]
    current_key_index = 0  # אינדקס המפתח הנוכחי
    BASE_URL = "https://www.alphavantage.co/query"  # כתובת בסיס של ה-API
    
    @classmethod
    def get_current_api_key(cls):
        """קבלת המפתח הנוכחי"""
        return cls.API_KEYS[cls.current_key_index]
    
    @classmethod
    def rotate_api_key(cls):
        """מעבר למפתח הבא - אם המפתח הנוכחי חסום"""
        cls.current_key_index = (cls.current_key_index + 1) % len(cls.API_KEYS)
        return cls.get_current_api_key()
    
    @staticmethod
    def update_price(symbol):
        """קבלת מחיר עדכני של מניה מה-API"""
        try:
            current_key = Broker.get_current_api_key()  # קבל מפתח נוכחי
            print(f"🔍 מנסה לקבל מחיר עבור {symbol} עם מפתח {Broker.current_key_index + 1}")
            
            # פרמטרים לבקשת API
            params = {
                'function': 'GLOBAL_QUOTE',  # סוג הבקשה - ציטוט גלובלי
                'symbol': symbol,  # סמל המניה
                'apikey': current_key  # מפתח ה-API
            }
            
            # שליחת בקשה ל-API עם timeout
            response = requests.get(Broker.BASE_URL, params=params, timeout=10)
            data = response.json()  # המרה ל-JSON
            
            print(f"📊 תגובת API עבור {symbol}: {data}")
            
            # בדיקת תוצאת API
            if 'Global Quote' in data and '05. price' in data['Global Quote']:
                current_price = data['Global Quote']['05. price']  # קבל מחיר נוכחי
                ils_price = float(current_price) * USD_TO_ILS_RATE  # המר לשקלים
                print(f"💰 קיבלתי מחיר עבור {symbol}: ${current_price} = ₪{ils_price:.2f}")
                return ils_price  # החזר מחיר בשקלים
            elif 'Error Message' in data:  # אם יש שגיאה
                print(f"❌ שגיאת API עבור {symbol}: {data['Error Message']}")
                return None
            elif 'Note' in data:  # אם יש הגבלת קצב
                print(f"⚠️ הגבלת API עבור {symbol}: {data['Note']}")
                # נסה לסובב למפתח הבא
                Broker.rotate_api_key()
                print(f"🔄 עברתי למפתח {Broker.current_key_index + 1}")
                return None
            else:  # אם אין מידע
                print(f"❓ לא נמצא מידע על {symbol}")
                return None
                
        except Exception as e:
            print(f"❌ שגיאה בקבלת מחיר עבור {symbol}: {e}")
            return None
