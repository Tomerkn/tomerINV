#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
המרת מחירים מדולר לשקל במסד הנתונים
"""

from dbmodel import PortfolioModel

# קבוע המרה מדולר לשקל
USD_TO_ILS_RATE = 3.5


def convert_all_prices_to_ils():
    """ממיר את כל המחירים במסד הנתונים מדולר לשקל"""
    
    portfolio = PortfolioModel()
    
    print('🔄 ממיר מחירים מדולר לשקל...')
    print('=' * 50)
    
    # מקבל את כל המניות עם המחירים הנוכחיים
    securities = portfolio.execute_query(
        "SELECT name, price FROM investments"
    )
    
    if not securities:
        print('❌ לא נמצאו ניירות ערך בתיק')
        return
    
    print('💱 מחירים לפני ההמרה (בדולר):')
    for name, price in securities:
        print(f'   {name}: ${price:.2f}')
    
    print('\n🔄 מבצע המרה לשקלים...')
    
    # מעדכן כל מחיר במסד הנתונים
    updated_count = 0
    for name, usd_price in securities:
        ils_price = usd_price * USD_TO_ILS_RATE
        
        portfolio.execute_query(
            "UPDATE investments SET price = ? WHERE name = ?",
            (ils_price, name)
        )
        
        print(f'✅ {name}: ${usd_price:.2f} → ₪{ils_price:.2f}')
        updated_count += 1
    
    print('=' * 50)
    print(f'🎉 עודכנו {updated_count} מחירים לשקלים')
    
    # מציג סיכום חדש
    print('\n💰 מחירים חדשים (בשקלים):')
    updated_securities = portfolio.execute_query(
        "SELECT name, price, amount FROM investments"
    )
    
    total_value = 0
    for name, price, amount in updated_securities:
        value = price * amount
        total_value += value
        print(f'   {name}: {amount} × ₪{price:.2f} = ₪{value:,.2f}')
    
    print(f'\n🚀 סך התיק בשקלים: ₪{total_value:,.2f}')
    print(f'💵 (בערך ${total_value/USD_TO_ILS_RATE:,.2f} בדולר)')


if __name__ == '__main__':
    convert_all_prices_to_ils() 