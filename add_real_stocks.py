#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
הוספת מניות אמיתיות עם סמלים של Alpha Vantage API
כל המניות עם הסמלים הנכונים לעדכון מחירים אמיתי
"""

from dbmodel import PortfolioModel


def add_real_stocks():
    """מוסיף מניות אמיתיות עם סמלים נכונים של Alpha Vantage"""
    
    # יוצר חיבור למסד הנתונים
    portfolio = PortfolioModel()
    
    # מניות טכנולוגיה אמריקאיות - סמלים אמיתיים
    tech_stocks = [
        ("AAPL", 150.00, 10, "טכנולוגיה", "נמוך", "מניה רגילה"),
        ("MSFT", 280.00, 8, "טכנולוגיה", "נמוך", "מניה רגילה"),
        ("GOOGL", 130.00, 5, "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("AMZN", 150.00, 4, "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("NFLX", 400.00, 3, "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("TSLA", 200.00, 5, "רכב", "גבוה", "מניה רגילה"),
        ("META", 300.00, 6, "טכנולוגיה", "גבוה", "מניה רגילה")
    ]
    
    # מניות ישראליות בבורסה האמריקאית
    israeli_stocks = [
        ("TEVA", 15.00, 25, "בריאות", "גבוה", "מניה רגילה"),
        ("CHKP", 140.00, 8, "טכנולוגיה", "נמוך", "מניה רגילה"),
        ("NICE", 180.00, 5, "טכנולוגיה", "נמוך", "מניה רגילה"),
        ("CYBR", 200.00, 4, "טכנולוגיה", "גבוה", "מניה רגילה")
    ]
    
    # מניות אמריקאיות מגוונות
    american_stocks = [
        ("KO", 60.00, 15, "צריכה פרטית", "נמוך", "מניה רגילה"),
        ("XOM", 100.00, 10, "אנרגיה", "גבוה", "מניה רגילה"),
        ("MCD", 280.00, 4, "צריכה פרטית", "נמוך", "מניה רגילה"),
        ("NKE", 100.00, 8, "צריכה פרטית", "גבוה", "מניה רגילה"),
        ("JPM", 150.00, 6, "פיננסים", "נמוך", "מניה רגילה"),
        ("JNJ", 170.00, 7, "בריאות", "נמוך", "מניה רגילה")
    ]
    
    # מוחק מניות קיימות עם שמות בעברית
    print("🧹 מנקה מניות ישנות...")
    portfolio.execute_query("DELETE FROM investments")
    
    # מוסיף את כל המניות החדשות
    all_stocks = tech_stocks + israeli_stocks + american_stocks
    
    print("🚀 מתחיל להוסיף מניות אמיתיות עם סמלים נכונים...")
    print("=" * 60)
    
    added_count = 0
    for stock_data in all_stocks:
        symbol, price, amount, industry, variance, security_type = stock_data
        
        try:
            # מוסיף את המניה למסד הנתונים
            portfolio.add_security(symbol, price, industry, variance, 
                                   security_type)
            
            # מעדכן את הכמות בטבלה
            portfolio.execute_query(
                "UPDATE investments SET amount = ? WHERE name = ?", 
                (amount, symbol)
            )
            
            print(f"✅ נוספה: {symbol} - {amount} יחידות ב-${price:.2f}")
            added_count += 1
            
        except Exception as e:
            print(f"❌ שגיאה בהוספת {symbol}: {e}")
    
    print("=" * 60)
    print(f"🎉 סיימתי! נוספו {added_count} מניות אמיתיות לתיק")
    
    # מציג סיכום התיק
    print("\n📊 סיכום התיק החדש:")
    securities = portfolio.execute_query(
        "SELECT name, price, amount, industry, security_type FROM investments"
    )
    
    total_value = 0
    for security in securities:
        symbol, price, amount, industry, sec_type = security
        value = price * amount
        total_value += value
        print(f"   {symbol}: {amount} יחידות × ${price:.2f} = "
              f"${value:,.2f} ({industry})")
    
    print(f"\n💰 סך הכל התיק שווה: ${total_value:,.2f}")
    print(f"📈 מספר ניירות ערך: {len(securities)}")


if __name__ == "__main__":
    add_real_stocks() 