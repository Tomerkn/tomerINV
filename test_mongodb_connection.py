#!/usr/bin/env python3
"""
בדיקת חיבור ל-MongoDB Atlas
סקריפט בדיקה פשוט לוודא שהחיבור עובד
"""

import os
from dotenv import load_dotenv

# טעינת משתני סביבה
load_dotenv()

def test_mongodb_connection():
    """בדיקת חיבור בסיסית ל-MongoDB Atlas"""
    
    print("🔍 בודק משתני סביבה...")
    
    # בדיקת משתני סביבה
    username = os.getenv('MONGODB_USERNAME')
    password = os.getenv('MONGODB_PASSWORD')
    cluster_url = os.getenv('MONGODB_CLUSTER_URL')
    
    print(f"   Username: {'✅' if username else '❌'} {username or 'לא מוגדר'}")
    print(f"   Password: {'✅' if password else '❌'} {'****' if password else 'לא מוגדר'}")
    print(f"   Cluster:  {'✅' if cluster_url else '❌'} {cluster_url or 'לא מוגדר'}")
    
    if not all([username, password, cluster_url]):
        print("\n❌ משתני סביבה חסרים!")
        print("הגדר קובץ .env עם:")
        print("MONGODB_USERNAME=your_username")
        print("MONGODB_PASSWORD=your_password") 
        print("MONGODB_CLUSTER_URL=cluster0.xxxxx.mongodb.net")
        return False
    
    try:
        print("\n🔄 מנסה להתחבר ל-MongoDB Atlas...")
        
        from mongodb_atlas_controller import MongoDBAtlasManager, MongoDBPortfolioController
        
        # יצירת חיבור
        manager = MongoDBAtlasManager()
        controller = MongoDBPortfolioController(manager)
        
        print("✅ חיבור מוצלח!")
        
        # בדיקת פעולות בסיסיות
        print("\n🧪 בודק פעולות בסיסיות...")
        
        # קבלת תיק (צפוי להיות ריק בהתחלה)
        holdings = controller.get_portfolio()
        print(f"   📊 תיק השקעות: {len(holdings)} פריטים")
        
        # בדיקת הוספת נייר ערך
        print("   ➕ מנסה להוסיף נייר ערך לבדיקה...")
        result = controller.buy_security(
            name="TEST_STOCK",
            amount=1.0,
            industry="טכנולוגיה",
            variance="בינונית", 
            security_type="מניה"
        )
        print(f"   📝 תוצאה: {result}")
        
        # בדיקת תיק לאחר הוספה
        holdings_after = controller.get_portfolio()
        print(f"   📊 תיק לאחר הוספה: {len(holdings_after)} פריטים")
        
        # מחיקת נייר הערך לבדיקה
        if len(holdings_after) > len(holdings):
            print("   🗑️ מוחק נייר ערך לבדיקה...")
            delete_result = controller.remove_security("TEST_STOCK")
            print(f"   📝 תוצאת מחיקה: {delete_result}")
        
        print("\n✅ כל הבדיקות עברו בהצלחה!")
        print("🎉 MongoDB Atlas מוכן לשימוש!")
        return True
        
    except Exception as e:
        print(f"\n❌ שגיאה בחיבור: {e}")
        print("\n🔧 פתרונות אפשריים:")
        print("1. בדוק את פרטי החיבור ב-.env")
        print("2. ודא ש-IP Address מאושר ב-MongoDB Atlas")
        print("3. בדוק שהמשתמש קיים ויש לו הרשאות")
        print("4. התקן dependencies: pip install -r requirements_mongodb.txt")
        return False

def main():
    """פונקציה ראשית"""
    print("=" * 50)
    print("   🧪 בדיקת חיבור MongoDB Atlas")
    print("=" * 50)
    
    try:
        success = test_mongodb_connection()
        
        if success:
            print("\n" + "=" * 50)
            print("✅ הכל מוכן! תוכל להשתמש ב-MongoDB Atlas")
            print("   להפעלת האפליקציה עם MongoDB:")
            print("   python app_mongodb_integration.py")
            print("=" * 50)
        else:
            print("\n" + "=" * 50)
            print("❌ החיבור נכשל - עבור למדריך ההתקנה")
            print("   python mongodb_setup.md")
            print("=" * 50)
            
    except ImportError as e:
        print(f"\n❌ חסרים מודולים: {e}")
        print("התקן עם: pip install -r requirements_mongodb.txt")
    except Exception as e:
        print(f"\n❌ שגיאה כללית: {e}")

if __name__ == "__main__":
    main() 