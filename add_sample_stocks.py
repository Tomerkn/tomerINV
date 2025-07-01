#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
add_sample_stocks.py - סקריפט להוספת מניות דוגמה למסד הנתונים

סקריפט זה מוסיף מניות אמריקאיות וישראליות לתיק ההשקעות לצורך הדגמה.
זה כולל מניות טכנולוגיה, בנקאות, בריאות ואגרות חוב.
"""

import os  # לעבודה עם משתני סביבה
import sys  # לעבודה עם נתיב המערכת

# הוסף את התיקייה הנוכחית ל-path כדי שנוכל לייבא מודולים מקומיים
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dbmodel import PortfolioModel  # ייבא את מודל מסד הנתונים


def add_sample_stocks():
    """מוסיף מניות דוגמה למסד הנתונים - אמריקאיות וישראליות"""
    
    # הגדרת משתני סביבה לחיבור למסד הנתונים בשרת
    os.environ['DATABASE_URL'] = "postgresql://postgres:WaPnQYjKJlhQJKCoNYbZxQRldTRJmTWW@shortline.proxy.rlwy.net:23148/railway"
    
    # יצירת מופע של מודל התיק
    portfolio_model = PortfolioModel()  # יצירת חיבור למסד הנתונים
    
    # יצירת טבלאות ומשתמשי ברירת מחדל
    portfolio_model.init_db()  # ווידוא שהטבלאות קיימות
    portfolio_model.create_default_users()  # יצירת משתמשי ברירת מחדל
    
    # רשימת מניות דוגמה - אמריקאיות וישראליות
    sample_stocks = [
        # מניות אמריקאיות מובילות (מחירים סבירים)
        {
            'name': 'Apple Inc',  # שם החברה
            'symbol': 'AAPL',  # סמל המניה בבורסה
            'amount': 5,  # כמות המניות
            'price': 185.50,  # מחיר למניה בשקלים
            'industry': 'טכנולוגיה',  # ענף החברה
            'variance': 0.25,  # רמת סיכון (סטיית תקן)
            'security_type': 'מניה'  # סוג נייר הערך
        },
        {
            'name': 'Microsoft Corp',
            'symbol': 'MSFT',
            'amount': 3,
            'price': 340.75,
            'industry': 'טכנולוגיה',
            'variance': 0.22,
            'security_type': 'מניה'
        },
        {
            'name': 'Johnson & Johnson',
            'symbol': 'JNJ',
            'amount': 8,
            'price': 162.30,
            'industry': 'בריאות',
            'variance': 0.15,  # סיכון נמוך יותר (חברת תרופות יציבה)
            'security_type': 'מניה'
        },
        {
            'name': 'Walmart Inc',
            'symbol': 'WMT',
            'amount': 10,
            'price': 165.75,
            'industry': 'צריכה פרטית',
            'variance': 0.12,  # סיכון נמוך (קמעונאות יציבה)
            'security_type': 'מניה'
        },
        {
            'name': 'JPMorgan Chase',
            'symbol': 'JPM',
            'amount': 6,
            'price': 195.40,
            'industry': 'פיננסים',
            'variance': 0.18,  # סיכון בינוני (בנקאות)
            'security_type': 'מניה'
        },
        {
            'name': 'Visa Inc',
            'symbol': 'V',
            'amount': 4,
            'price': 285.20,
            'industry': 'פיננסים',
            'variance': 0.20,  # סיכון בינוני
            'security_type': 'מניה'
        },
        
        # מניות ישראליות הנסחרות בארה"ב (ADR)
        {
            'name': 'Check Point Software',  # צ'ק פוינט
            'symbol': 'CHKP',
            'amount': 8,
            'price': 145.80,
            'industry': 'טכנולוגיה',
            'variance': 0.28,  # סיכון גבוה יותר (טכנולוגיה ישראלית)
            'security_type': 'מניה'
        },
        {
            'name': 'Teva Pharmaceutical',  # טבע תעשיות פרמצבטיות
            'symbol': 'TEVA',
            'amount': 25,
            'price': 12.45,  # מחיר נמוך למניה
            'industry': 'בריאות',
            'variance': 0.35,  # סיכון גבוה (חברה במשבר)
            'security_type': 'מניה'
        },
        {
            'name': 'NICE Ltd',  # נייס מערכות
            'symbol': 'NICE',
            'amount': 6,
            'price': 195.30,
            'industry': 'טכנולוגיה',
            'variance': 0.30,  # סיכון גבוה (טכנולוגיה)
            'security_type': 'מניה'
        },
        {
            'name': 'CyberArk Software',  # סייבר ארק
            'symbol': 'CYBR',
            'amount': 4,
            'price': 285.75,
            'industry': 'טכנולוגיה',
            'variance': 0.32,  # סיכון גבוה (אבטחת סייבר)
            'security_type': 'מניה'
        },
        {
            'name': 'Fiverr International',  # פייבר
            'symbol': 'FVRR',
            'amount': 12,
            'price': 28.90,  # מחיר נמוך (מניה צעירה)
            'industry': 'טכנולוגיה',
            'variance': 0.45,  # סיכון גבוה מאוד (חברה צעירה)
            'security_type': 'מניה'
        },
        {
            'name': 'Wix.com Ltd',  # וויקס
            'symbol': 'WIX',
            'amount': 8,
            'price': 89.25,
            'industry': 'טכנולוגיה',
            'variance': 0.38,  # סיכון גבוה
            'security_type': 'מניה'
        },
        {
            'name': 'Monday.com Ltd',  # מאנדיי
            'symbol': 'MNDY',
            'amount': 5,
            'price': 245.60,
            'industry': 'טכנולוגיה',
            'variance': 0.42,  # סיכון גבוה
            'security_type': 'מניה'
        },
        
        # אגרות חוב בטוחות (לאיזון התיק)
        {
            'name': 'אגח ממשלתי ארה"ב',
            'symbol': 'TLT',  # ETF של אגרות חוב ארוכות טווח
            'amount': 30,
            'price': 95.20,
            'industry': 'נדלן',  # קטגוריה לאגרות חוב
            'variance': 0.08,  # סיכון נמוך מאוד
            'security_type': 'אגח ממשלתית'
        },
        {
            'name': 'iShares iBoxx $ Investment Grade Corporate Bond ETF',
            'symbol': 'LQD',  # ETF של אגרות חוב קונצרניות
            'amount': 20,
            'price': 105.45,
            'industry': 'נדלן',  # קטגוריה לאגרות חוב
            'variance': 0.10,  # סיכון נמוך
            'security_type': 'אגח קונצרנית'
        }
    ]
    
    print("🚀 מתחיל הוספת מניות דוגמה למסד נתונים PostgreSQL...")
    print(f"📊 מוסיף {len(sample_stocks)} מניות (אמריקאיות וישראליות)")
    
    # בדיקה אם כבר יש מניות במסד
    existing_stocks = portfolio_model.get_all_securities()  # קבל רשימת מניות קיימות
    if existing_stocks:  # אם יש כבר מניות
        print(f"⚠️ יש כבר {len(existing_stocks)} מניות במסד הנתונים")
        # שאל את המשתמש אם למחוק הכל ולהתחיל מחדש
        response = input("האם למחוק את כל המניות הקיימות ולהתחיל מחדש? (y/N): ")
        if response.lower() == 'y':
            # מחיקת כל הניירות הקיימים
            for stock in existing_stocks:
                portfolio_model.remove_security(stock['name'])  # מחק כל מניה
            print("🗑️ מחקתי את כל המניות הקיימות")
        else:
            print("❌ מבטל הוספת מניות")
            return  # יציאה מהפונקציה
    
    # הוספת המניות החדשות
    added_count = 0  # מונה מניות שנוספו
    american_count = 0  # מונה מניות אמריקאיות
    israeli_count = 0  # מונה מניות ישראליות
    
    for stock in sample_stocks:  # עבור על כל מניה ברשימה
        try:
            # הוסף את המניה למסד הנתונים
            result = portfolio_model.add_security(
                stock['name'],  # שם החברה
                stock['symbol'],  # סמל המניה
                stock['amount'],  # כמות
                stock['price'],  # מחיר
                stock['industry'],  # ענף
                stock['variance'],  # סיכון
                stock['security_type']  # סוג נייר ערך
            )
            
            if result:  # אם ההוספה הצליחה
                # זיהוי מניות ישראליות לפי סמל
                israeli_symbols = ['CHKP', 'TEVA', 'NICE', 'CYBR', 'FVRR', 'WIX', 'MNDY']
                if stock['symbol'] in israeli_symbols:
                    flag = "🇮🇱"  # דגל ישראל
                    israeli_count += 1
                elif stock['symbol'] in ['TLT', 'LQD']:  # אגרות חוב
                    flag = "🏛️"  # סמל ממשלה
                else:  # מניות אמריקאיות
                    flag = "🇺🇸"  # דגל אמריקה
                    american_count += 1
                    
                # הדפס הודעת הצלחה עם פרטי המניה
                print(f"✅ {flag} נוסף: {stock['name']} ({stock['symbol']}) - {stock['amount']} יחידות ב-₪{stock['price']:.2f}")
                added_count += 1
            else:
                print(f"❌ שגיאה בהוספת: {stock['name']}")
                
        except Exception as e:
            print(f"❌ שגיאה בהוספת {stock['name']}: {str(e)}")
    
    # סיכום התהליך
    print(f"\n🎉 הושלם! נוספו {added_count} מתוך {len(sample_stocks)} מניות")
    print(f"   🇺🇸 מניות אמריקאיות: {american_count}")
    print(f"   🇮🇱 מניות ישראליות: {israeli_count}")
    print(f"   🏛️ אגרות חוב: {len(sample_stocks) - american_count - israeli_count}")
    
    # הצגת סיכום התיק
    final_stocks = portfolio_model.get_all_securities()  # קבל רשימה מעודכנת
    total_value = sum(stock['price'] * stock['amount'] for stock in final_stocks)  # חשב ערך כולל
    
    print(f"\n📊 סיכום התיק:")
    print(f"   💼 מספר ניירות ערך: {len(final_stocks)}")
    print(f"   💰 שווי כולל: ₪{total_value:,.2f}")
    
    # פירוט לפי ענפים
    industries = {}  # מילון לאחסון נתוני ענפים
    for stock in final_stocks:
        industry = stock['industry']  # קבל ענף
        if industry not in industries:
            # אתחל אם לא קיים
            industries[industry] = {'count': 0, 'value': 0}
        industries[industry]['count'] += 1  # הוסף למניין
        industries[industry]['value'] += stock['price'] * stock['amount']  # הוסף לערך
    
    print(f"\n🏭 פירוט לפי ענפים:")
    for industry, data in industries.items():  # עבור על כל ענף
        percentage = (data['value'] / total_value) * 100 if total_value > 0 else 0  # חשב אחוז
        print(f"   {industry}: {data['count']} מניות, ₪{data['value']:,.2f} ({percentage:.1f}%)")
    
    # רשימת החברות הישראליות
    print(f"\n🌟 המניות הישראליות כוללות:")
    israeli_stocks = ['CHKP', 'TEVA', 'NICE', 'CYBR', 'FVRR', 'WIX', 'MNDY']
    for stock in final_stocks:
        if stock['symbol'] in israeli_stocks:  # אם זו מניה ישראלית
            print(f"   🇮🇱 {stock['name']} ({stock['symbol']}) - ענף {stock['industry']}")


if __name__ == "__main__":
    add_sample_stocks()  # הפעל את הפונקציה הראשית 