#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_local.py - סקריפט התקנה והגדרה של המערכת למחשב המקומי

קובץ זה מבצע את כל ההכנות הנדרשות להפעלת מערכת ניהול תיק השקעות במחשב האישי.
הוא בודק דרישות, מתקין ספריות, יוצר מסד נתונים ומגדיר את כל הפרמטרים הנדרשים.
"""

# ייבוא ספריות מערכת
import os  # לעבודה עם קבצים ומשתני סביבה
import sys  # לעבודה עם המערכת ויציאה מהתוכנית
import subprocess  # להפעלת פקודות מערכת כמו pip install


def print_header():
    """מדפיס כותרת מעוצבת לתחילת התהליך"""
    print("=" * 60)
    print("הגדרת מערכת ניהול תיק השקעות - גרסה מקומית")
    print("=" * 60)
    print()


def check_mysql():
    """בודק אם MySQL מותקן וזמין במחשב המקומי"""
    print("בודק חיבור ל-MySQL...")
    try:
        import mysql.connector
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        print(" MySQL זמין ופועל!")
        conn.close()
        return True
    except Error as e:
        print(f" שגיאה בחיבור ל-MySQL: {e}")
        print("\n הוראות להתקנת MySQL:")
        print("1. הורד MySQL מהאתר הרשמי")
        print("2. התקן עם הגדרות ברירת מחדל")
        print("3. וודא שהשרת פועל")
        print("4. נסה שוב")
        return False

def create_database():
    """יוצר את מסד הנתונים המקומי 'investments' אם הוא לא קיים"""
    print("יוצר מסד נתונים...")
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS investments")
        print(" מסד הנתונים 'investments' נוצר בהצלחה!")
        conn.close()
        return True
    except Error as e:
        print(f" שגיאה ביצירת מסד הנתונים: {e}")
        return False

def check_ollama():
    """בודק אם שירות Ollama זמין ופועל במחשב לבינה מלאכותית"""
    print(" בודק חיבור ל-Ollama...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print(" Ollama זמין ופועל!")
            return True
        else:
            print(" Ollama לא מגיב כראוי")
            return False
    except Exception as e:
        print(f" שגיאה בחיבור ל-Ollama: {e}")
        print("\n הוראות להתקנת Ollama:")
        print("1. הורד Ollama מהאתר הרשמי")
        print("2. התקן והפעל את השרת")
        print("3. הורד מודל: ollama pull llama3.1:8b")
        print("4. נסה שוב")
        return False

def install_requirements():
    """מתקין את כל הספריות הנדרשות מקובץ requirements.txt"""
    print(" מתקין ספריות נדרשות...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("הספריות הותקנו בהצלחה!")
        return True
    except subprocess.CalledProcessError as e:
        print(f" שגיאה בהתקנת הספריות: {e}")
        return False

def create_env_file():
    """יוצר קובץ .env עם הגדרות מקומיות"""
    print(" יוצר קובץ הגדרות...")
    env_content = """# קובץ .env - הגדרות המערכת
# הקובץ הזה מכיל את כל ההגדרות החשובות של המערכת

# הגדרות מסד נתונים
DATABASE_URL=localhost

# הגדרות בינה מלאכותית
OLLAMA_URL=http://localhost:11434

# הגדרות אבטחה
SECRET_KEY=your-secret-key-here-change-this-in-production

# הגדרות נוספות
FLASK_ENV=development
FLASK_DEBUG=True
"""
    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print(" קובץ .env נוצר בהצלחה!")
        return True
    except Exception as e:
        print(f" שגיאה ביצירת קובץ .env: {e}")
        return False

def test_system():
    """בודק שהמערכת עובדת"""
    print(" בודק שהמערכת עובדת...")
    try:
        # בדיקת ייבוא הספריות
        import flask
        import mysql.connector
        import ollama
        print(" כל הספריות נטענו בהצלחה!")
        
        # בדיקת חיבור למסד הנתונים
        from dbmodel import PortfolioModel
        model = PortfolioModel()
        print("חיבור למסד הנתונים עובד!")
        
        # בדיקת חיבור ל-Ollama
        from ollamamodel import AI_Agent
        agent = AI_Agent()
        print("חיבור ל-Ollama עובד!")
        
        return True
    except Exception as e:
        print(f"שגיאה בבדיקת המערכת: {e}")
        return False

def main():
    """הפונקציה הראשית"""
    print_header()
    
    print("מתחיל הגדרת המערכת...")
    print()
    
    # בדיקת MySQL
    if not check_mysql():
        return False
    
    # יצירת מסד הנתונים
    if not create_database():
        return False
    
    # בדיקת Ollama
    if not check_ollama():
        print(" אזהרה: Ollama לא זמין. המערכת תעבוד עם ייעוץ פשוט.")
    
    # התקנת ספריות
    if not install_requirements():
        return False
    
    # יצירת קובץ .env
    if not create_env_file():
        return False
    
    # בדיקת המערכת
    if not test_system():
        return False
    
    print()
    print(" הגדרת המערכת הושלמה בהצלחה!")
    print()
    print("הוראות הפעלה:")
    print("1. הרץ: python app.py")
    print("2. פתח בדפדפן: http://localhost:5000")
    print("3. התחבר עם משתמש: admin, סיסמה: admin")
    print()
    print("🔧 הגדרות נוספות:")
    print("- MySQL: localhost (משתמש: root, סיסמה: ריקה)")
    print("- Ollama: http://localhost:11434")
    print("- מודל: llama3.1:8b")
    print()
    print("📞 אם יש בעיות, בדוק:")
    print("- MySQL פועל ונגיש")
    print("- Ollama פועל עם המודל הנכון")
    print("- כל הספריות הותקנו")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n הגדרת המערכת נכשלה. בדוק את השגיאות למעלה.")
        sys.exit(1) 