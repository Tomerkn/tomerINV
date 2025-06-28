"""
קובץ ליצירת משתמשי ברירת מחדל במערכת
"""

import os
import sys

# הוספת הנתיב הנוכחי ל-PYTHONPATH כדי לאפשר ייבוא מקומי
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dbmodel import PortfolioModel

def create_default_users():
    """יוצר משתמשי ברירת מחדל - admin ו-user"""
    print("=== התחלת יצירת משתמשי ברירת מחדל ===")
    
    try:
        # יצירת מופע של מודל מסד הנתונים
        portfolio_model = PortfolioModel()
        
        # וידוא שהטבלאות קיימות
        portfolio_model.create_tables()
        print("טבלאות וודאו/נוצרו בהצלחה")
        
        # יצירת משתמשי ברירת מחדל
        success = portfolio_model.create_default_users()
        
        if success:
            print("משתמשי ברירת מחדל נוצרו בהצלחה!")
            print("פרטי המשתמשים:")
            print("   מנהל: admin / admin")
            print("   משתמש: user / user")
        else:
            print("שגיאה ביצירת משתמשי ברירת מחדל")
            
    except Exception as e:
        print(f"שגיאה: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_default_users() 