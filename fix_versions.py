#!/usr/bin/env python3
"""
סקריפט לתיקון ובדיקת גרסאות Flask ו-Werkzeug
מונע בעיות תאימות ומבטיח שהמערכת עובדת
"""

import subprocess
import sys
import pkg_resources

# מפת תאימות גרסאות
VERSION_COMPATIBILITY = {
    "Flask": {
        "2.2.5": {"werkzeug": "2.2.3", "flask-wtf": "1.1.1"},
        "2.3.3": {"werkzeug": "2.3.7", "flask-wtf": "1.1.1"},
        "3.0.0": {"werkzeug": "3.0.0", "flask-wtf": "1.2.1"}
    }
}

# הגרסאות המומלצות (יציבות מקסימלית)
RECOMMENDED_VERSIONS = {
    "Flask": "2.2.5",
    "Werkzeug": "2.2.3", 
    "Flask-WTF": "1.1.1",
    "WTForms": "3.0.1",
    "Flask-Login": "0.6.3"
}

def run_command(cmd):
    """מריץ פקודה ומחזיר את התוצאה"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True,
                               text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def get_installed_version(package_name):
    """מקבל את הגרסה המותקנת של חבילה"""
    try:
        return pkg_resources.get_distribution(package_name).version
    except pkg_resources.DistributionNotFound:
        return None


def check_compatibility():
    """בודק תאימות בין הגרסאות הנוכחיות"""
    print("🔍 בודק תאימות גרסאות...")
    
    flask_version = get_installed_version("Flask")
    werkzeug_version = get_installed_version("Werkzeug")
    
    if not flask_version or not werkzeug_version:
        print("❌ לא נמצאו גרסאות Flask או Werkzeug")
        return False
    
    print(f"📦 Flask נוכחי: {flask_version}")
    print(f"⚙️  Werkzeug נוכחי: {werkzeug_version}")
    
    # בדיקה ידנית לתאימות Flask 2.2.5 + Werkzeug 2.2.3
    if (flask_version.startswith("2.2") and 
            werkzeug_version.startswith("2.2")):
        print("✅ הגרסאות תואמות!")
        return True
    elif (flask_version.startswith("2.3") and 
          werkzeug_version.startswith("2.3")):
        print("✅ הגרסאות תואמות!")
        return True
    else:
        print("❌ הגרסאות לא תואמות!")
        return False


def update_requirements_file():
    """מעדכן את קובץ requirements.txt עם הגרסאות המומלצות"""
    print("📝 מעדכן קובץ requirements.txt...")
    
    requirements_content = f"""# requirements.txt - ספריות למערכת מקומית בלבד
# מערכת ניהול תיק השקעות עם MySQL ו-Ollama

# Flask - הבסיס של האתר (גרסאות תואמות)
Flask=={RECOMMENDED_VERSIONS['Flask']}
Flask-Login=={RECOMMENDED_VERSIONS['Flask-Login']}
Flask-WTF=={RECOMMENDED_VERSIONS['Flask-WTF']}
WTForms=={RECOMMENDED_VERSIONS['WTForms']}
Werkzeug=={RECOMMENDED_VERSIONS['Werkzeug']}

# MySQL מקומי
mysql-connector-python==8.0.33

# גרפים ונתונים
matplotlib==3.7.2
numpy==1.24.3
pandas==2.0.3

# API למחירי מניות
requests==2.31.0
urllib3==2.0.4
yfinance==0.2.18

# Ollama מקומי
ollama==0.1.9

# ספריות עזר
python-dateutil==2.8.2
pytz==2023.3
"""
    
    with open("requirements.txt", "w", encoding="utf-8") as f:
        f.write(requirements_content)
    
    print("✅ קובץ requirements.txt עודכן!")

def install_compatible_versions():
    """מתקין את הגרסאות התואמות"""
    print("📦 מתקין גרסאות תואמות...")
    
    # עדכון קובץ requirements
    update_requirements_file()
    
    # התקנה עם כפיית גרסאות
    success, stdout, stderr = run_command("pip install -r requirements.txt --force-reinstall")
    
    if success:
        print("✅ התקנה הושלמה בהצלחה!")
        return True
    else:
        print(f"❌ שגיאה בהתקנה: {stderr}")
        return False

def test_flask_import():
    """בודק שFlask נטען בהצלחה"""
    print("🧪 בודק שFlask עובד...")
    
    try:
        import flask
        import werkzeug
        print(f"✅ Flask {flask.__version__} נטען בהצלחה!")
        print(f"✅ Werkzeug {werkzeug.__version__} נטען בהצלחה!")
        
        # בדיקה שהאפליקציה נטענת
        try:
            from app import app
            print("✅ האפליקציה נטענת בהצלחה!")
            return True
        except Exception as e:
            print(f"❌ שגיאה בטעינת האפליקציה: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ שגיאה בייבוא Flask: {e}")
        return False

def create_version_lock():
    """יוצר קובץ נעילת גרסאות למניעת שינויים עתידיים"""
    print("🔒 יוצר קובץ נעילת גרסאות...")
    
    lock_content = f"""# version_lock.txt - קובץ נעילת גרסאות
# נוצר אוטומטית על ידי fix_versions.py
# אל תשנה קובץ זה ידנית!

FLASK_VERSION={RECOMMENDED_VERSIONS['Flask']}
WERKZEUG_VERSION={RECOMMENDED_VERSIONS['Werkzeug']}
FLASK_WTF_VERSION={RECOMMENDED_VERSIONS['Flask-WTF']}
LAST_CHECK={pkg_resources.get_distribution("Flask").version if get_installed_version("Flask") else "unknown"}
STATUS=LOCKED
"""
    
    with open("version_lock.txt", "w", encoding="utf-8") as f:
        f.write(lock_content)
    
    print("✅ קובץ נעילת גרסאות נוצר!")

def main():
    """הפונקציה הראשית"""
    print("=" * 50)
    print("🔧 כלי תיקון גרסאות Flask ו-Werkzeug")
    print("=" * 50)
    
    # שלב 1: בדיקת תאימות נוכחית
    if check_compatibility():
        print("\n✅ הגרסאות כבר תואמות!")
        
        # בדיקה שהאפליקציה עובדת
        if test_flask_import():
            print("🎉 הכל עובד מצוין!")
            create_version_lock()
            return True
        else:
            print("⚠️  יש בעיה עם האפליקציה, מתחיל תיקון...")
    else:
        print("\n⚠️  נמצאו בעיות תאימות, מתחיל תיקון...")
    
    # שלב 2: תיקון הגרסאות
    if install_compatible_versions():
        print("\n🔄 בודק שוב לאחר התיקון...")
        
        # שלב 3: בדיקה חוזרת
        if check_compatibility() and test_flask_import():
            print("\n🎉 התיקון הושלם בהצלחה!")
            create_version_lock()
            
            print("\n📋 הגרסאות הסופיות:")
            for package in RECOMMENDED_VERSIONS:
                current_version = get_installed_version(package)
                if current_version:
                    print(f"   {package}: {current_version}")
            
            print("\n💡 טיפים למניעת בעיות עתידיות:")
            print("   1. הרץ את הסקריפט הזה לפני כל עבודה")
            print("   2. אל תעדכן חבילות Flask ידנית")
            print("   3. השתמש בגרסאות הנעולות ב-requirements.txt")
            
            return True
        else:
            print("\n❌ התיקון נכשל, בדוק את השגיאות למעלה")
            return False
    else:
        print("\n❌ התקנת הגרסאות החדשות נכשלה")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 