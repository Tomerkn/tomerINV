#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
קובץ להוספת מניות דוגמה לתיק ההשקעות
יריץ אוטומטית והוסיף מניות מעניינות ומגוונות
"""

from dbmodel import PortfolioModel


def add_sample_stocks():
    """מוסיף מניות דוגמה מגוונות לתיק"""
    
    # יוצר חיבור למסד הנתונים
    portfolio = PortfolioModel()
    
    # מניות טכנולוגיה
    tech_stocks = [
        ("אפל", 150.50, 10, "טכנולוגיה", "נמוך", "מניה רגילה"),
        ("מיקרוסופט", 280.25, 8, "טכנולוגיה", "נמוך", "מניה רגילה"),
        ("גוגל", 2500.75, 3, "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("אמזון", 3200.40, 2, "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("נטפליקס", 450.60, 5, "טכנולוגיה", "גבוה", "מניה רגילה")
    ]
    
    # מניות ישראליות
    israeli_stocks = [
        ("טבע", 45.30, 20, "בריאות", "גבוה", "מניה רגילה"),
        ("הדסים", 78.90, 12, "בריאות", "נמוך", "מניה רגילה"),
        ("בנק הפועלים", 25.60, 25, "פיננסים", "נמוך", "מניה רגילה"),
        ("בזק", 15.40, 30, "תחבורה", "נמוך", "מניה רגילה"),
        ("אלביט", 180.20, 6, "תעשייה", "גבוה", "מניה רגילה")
    ]
    
    # מניות צריכה ואנרגיה
    other_stocks = [
        ("קוקה קולה", 58.75, 15, "צריכה פרטית", "נמוך", "מניה רגילה"),
        ("אקסון מוביל", 65.20, 10, "אנרגיה", "גבוה", "מניה רגילה"),
        ("מקדונלדס", 250.30, 4, "צריכה פרטית", "נמוך", "מניה רגילה"),
        ("נייקי", 135.80, 7, "צריכה פרטית", "גבוה", "מניה רגילה")
    ]
    
    # אגחות ממשלתיות ישראליות
    bonds = [
        ("אג\"ח ממשלתי 2030", 1000.00, 5, "פיננסים", "נמוך", 
         "אגח ממשלתית"),
        ("אג\"ח ממשלתי 2025", 995.50, 8, "פיננסים", "נמוך", 
         "אגח ממשלתית"),
        ("אג\"ח קונצרני עזריאלי", 102.30, 10, "נדלן", "נמוך", 
         "אגח קונצרנית")
    ]
    
    # מוסיף את כל המניות
    all_stocks = tech_stocks + israeli_stocks + other_stocks + bonds
    
    print("🚀 מתחיל להוסיף מניות לתיק...")
    print("=" * 50)
    
    added_count = 0
    for stock_data in all_stocks:
        name, price, amount, industry, variance, security_type = stock_data
        
        try:
            # מוסיף את המניה למסד הנתונים
            portfolio.add_security(name, price, industry, variance, 
                                   security_type)
            
            # מעדכן את הכמות בטבלה
            portfolio.execute_query(
                "UPDATE investments SET amount = ? WHERE name = ?", 
                (amount, name)
            )
            
            print(f"✅ נוספה: {name} - {amount} יחידות ב-₪{price:.2f}")
            added_count += 1
            
        except Exception as e:
            print(f"❌ שגיאה בהוספת {name}: {e}")
    
    print("=" * 50)
    print(f"🎉 סיימתי! נוספו {added_count} מניות לתיק")
    
    # מציג סיכום התיק
    print("\n📊 סיכום התיק:")
    securities = portfolio.execute_query(
        "SELECT name, price, amount, industry, security_type FROM investments"
    )
    
    total_value = 0
    for security in securities:
        name, price, amount, industry, sec_type = security
        value = price * amount
        total_value += value
        print(f"   {name}: {amount} יחידות × ₪{price:.2f} = "
              f"₪{value:,.2f} ({industry})")
    
    print(f"\n💰 סך הכל התיק שווה: ₪{total_value:,.2f}")
    print(f"📈 מספר ניירות ערך: {len(securities)}")


if __name__ == "__main__":
    add_sample_stocks() 