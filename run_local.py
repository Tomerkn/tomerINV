#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_local.py - הפעלת המערכת המקומית

סקריפט פשוט להפעלת מערכת ניהול תיק השקעות במחשב האישי.
זה הקובץ שמפעיל את כל המערכת במחשב המקומי עם MySQL ו-Ollama.
"""

import os  # לעבודה עם מערכת הקבצים ומשתני סביבה
import sys  # לעבודה עם המערכת ויציאה מהתוכנית
import subprocess  # להפעלת פקודות shell


def check_requirements():
    """בדיקת דרישות מקדימות - Python, MySQL ו-Ollama"""
    print("בודק דרישות מקדימות...")
    
    # בדיקת גרסת Python
    if sys.version_info < (3, 8):  # דרוש Python 3.8 או חדש יותר
        print("דרוש Python 3.8 ומעלה")
        return False
    
    print("גרסת Python תקינה")
    
    # בדיקת MySQL connector - ספרייה לחיבור ל-MySQL
    try:
        __import__('mysql.connector')  # ניסיון לייבא את הספרייה
        print("MySQL connector זמין")
    except ImportError:
        print("MySQL connector לא מותקן")
        print("   התקן עם: pip install mysql-connector-python")
        return False
    
    # בדיקת Ollama - ספרייה לבינה מלאכותית
    try:
        __import__('ollama')  # ניסיון לייבא את הספרייה
        print("Ollama library זמינה")
    except ImportError:
        print("Ollama library לא מותקנת")
        print("   התקן עם: pip install ollama")
    
    return True  # הכל בסדר, אפשר להמשיך


def set_environment():
    """הגדרת משתני סביבה למערכת מקומית"""
    print("מגדיר משתני סביבה...")
    
    # הגדרות MySQL מקומי - שרת מסד הנתונים
    os.environ.setdefault('DATABASE_URL', 'localhost')  # כתובת מסד נתונים
    os.environ.setdefault('DB_HOST', 'localhost')  # שרת מסד נתונים
    os.environ.setdefault('DB_PORT', '3306')  # פורט MySQL סטנדרטי
    os.environ.setdefault('DB_USER', 'root')  # משתמש ברירת מחדל
    os.environ.setdefault('DB_PASSWORD', '')  # סיסמה ריקה (מקומי)
    os.environ.setdefault('DB_NAME', 'portfolio_db')  # שם מסד הנתונים
    
    # הגדרות Ollama מקומי - שרת הבינה המלאכותית
    # כתובת Ollama המקומית
    os.environ.setdefault('OLLAMA_URL', 'http://localhost:11434')
    
    # הגדרות Flask - שרת האתר
    os.environ.setdefault('FLASK_ENV', 'development')  # סביבת פיתוח
    # מפתח אבטחה למערכת
    os.environ.setdefault('SECRET_KEY', 'local-portfolio-secret-key-2024')
    
    print("משתני סביבה הוגדרו")


def install_requirements():
    """התקנת ספריות נחוצות מקובץ requirements.txt"""
    print("📦 מתקין ספריות נחוצות...")
    try:
        # הפעל pip install עם requirements.txt
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ])
        print("✅ כל הספריות הותקנו בהצלחה")
        return True
    except subprocess.CalledProcessError:
        print("❌ שגיאה בהתקנת ספריות")
        return False


def main():
    """פונקציה ראשית - מנהלת את כל התהליך"""
    print("=" * 60)
    print("מערכת ניהול תיק השקעות - הפעלה מקומית")
    print("=" * 60)
    print()
    
    # בדיקת דרישות מקדימות
    if not check_requirements():
        print("\nהפעלה נכשלה - דרישות לא מתקיימות")
        return False
    
    # הגדרת משתני סביבה
    set_environment()
    
    # התקנת ספריות אם נדרש
    try:
        __import__('mysql.connector')  # בדיקה אם MySQL זמין
        __import__('flask')  # בדיקה אם Flask זמין
        __import__('matplotlib')  # בדיקה אם matplotlib זמין
    except ImportError:
        print("מתקין ספריות חסרות...")
        if not install_requirements():
            print("לא ניתן להתקין ספריות")
            return False
    
    # הוראות למשתמש לפני הפעלה
    print("\nהוראות הפעלה:")
    print("1. וודא ש-MySQL רץ במחשב")
    print("   (mysql.server start או brew services start mysql)")
    print("2. אופציונלי: הפעל Ollama (ollama serve)")
    print("3. המערכת תפעל על: http://localhost:5000")
    print("4. התחבר עם: admin/admin (מנהל) או user/user (משתמש)")
    print()
    
    # הפעלת האפליקציה הראשית
    print("מפעיל את המערכת...")
    try:
        from app import app  # ייבוא האפליקציה הראשית
        # הפעלת השרת על פורט 5000
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nהמערכת הופסקה על ידי המשתמש")
    except Exception as e:
        print(f"\nשגיאה בהפעלת המערכת: {str(e)}")
        return False
    
    return True


if __name__ == "__main__":
    success = main()  # הפעל את הפונקציה הראשית
    sys.exit(0 if success else 1)  # יציאה עם קוד הצלחה/כישלון 