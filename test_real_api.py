#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקת Alpha Vantage API עם הסמלים האמיתיים החדשים
"""

from broker import Broker
from dbmodel import PortfolioModel
import time


def test_real_api():
    """בודק מחירים אמיתיים עם הסמלים החדשים"""
    
    portfolio = PortfolioModel()
    
    print('🔍 בודק מחירים אמיתיים עם הסמלים החדשים...')
    print('=' * 60)
    
    # מקבל רשימת כל המניות מהתיק
    securities = portfolio.execute_query(
        "SELECT name FROM investments LIMIT 5"  # רק 5 ראשונות לבדיקה
    )
    
    real_prices = {}
    
    for symbol_tuple in securities:
        symbol = symbol_tuple[0]
        try:
            print(f'📡 מבקש מחיר עבור {symbol}...')
            price = Broker.update_price(symbol)
            real_prices[symbol] = price
            print(f'📈 {symbol}: ${price:.2f} ✅')
            time.sleep(2)  # המתנה של 2 שניות בין בקשות
        except Exception as e:
            print(f'❌ שגיאה עם {symbol}: {e}')
            real_prices[symbol] = None
    
    print('=' * 60)
    print(f'✅ בדקתי {len(real_prices)} מניות')
    
    # מציג תוצאות
    print('\n📊 תוצאות מ-Alpha Vantage API:')
    for symbol, price in real_prices.items():
        if price:
            print(f'   {symbol}: ${price:.2f} 🔥')
        else:
            print(f'   {symbol}: לא זמין ❌')
    
    return real_prices


def update_all_with_real_prices():
    """מעדכן את כל המניות עם מחירים אמיתיים"""
    
    portfolio = PortfolioModel()
    
    print('\n🔄 מעדכן את כל התיק עם מחירים אמיתיים...')
    print('=' * 60)
    
    # מקבל את כל המניות
    securities = portfolio.execute_query("SELECT name FROM investments")
    
    updated_count = 0
    for symbol_tuple in securities:
        symbol = symbol_tuple[0]
        try:
            print(f'🔄 מעדכן {symbol}...')
            real_price = Broker.update_price(symbol)
            
            # מעדכן במסד הנתונים
            portfolio.execute_query(
                "UPDATE investments SET price = ? WHERE name = ?",
                (real_price, symbol)
            )
            
            print(f'✅ {symbol}: עודכן ל-${real_price:.2f}')
            updated_count += 1
            time.sleep(2)  # המתנה בין בקשות
            
        except Exception as e:
            print(f'❌ {symbol}: {e}')
    
    print('=' * 60)
    print(f'🎉 עודכנו {updated_count} מניות עם מחירים אמיתיים!')
    
    # מציג סיכום חדש
    print('\n💰 סיכום התיק עם מחירים אמיתיים:')
    updated_securities = portfolio.execute_query(
        "SELECT name, price, amount FROM investments"
    )
    
    total_value = 0
    for symbol, price, amount in updated_securities:
        value = price * amount
        total_value += value
        print(f'   {symbol}: {amount} × ${price:.2f} = ${value:,.2f}')
    
    print(f'\n🚀 סך התיק עם מחירים אמיתיים: ${total_value:,.2f}')


if __name__ == "__main__":
    # בדיקה ראשונית
    test_real_api()
    
    # עדכון מלא
    answer = input('\n❓ לעדכן את כל התיק עם מחירים אמיתיים? (y/n): ')
    if answer.lower() == 'y':
        update_all_with_real_prices() 