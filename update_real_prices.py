#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
עדכון מחירים אמיתיים מ-Alpha Vantage API
"""

from dbmodel import PortfolioModel
from broker import Broker
import time


def update_portfolio_with_real_prices():
    """מעדכן מחירים אמיתיים לכל המניות בתיק"""
    
    portfolio = PortfolioModel()
    
    # מפה של שמות עברית לסמלים אמריקאיים
    symbol_map = {
        'אפל': 'AAPL',
        'מיקרוסופט': 'MSFT', 
        'גוגל': 'GOOGL',
        'אמזון': 'AMZN',
        'נטפליקס': 'NFLX',
        'טבע': 'TEVA',
        'aapl': 'AAPL'  # אם יש כזה מהבדיקות הקודמות
    }
    
    print('🔄 מעדכן מחירים אמיתיים מ-Alpha Vantage...')
    print('=' * 50)
    
    # מקבל את כל המניות מהתיק
    securities = portfolio.execute_query(
        "SELECT name FROM investments"
    )
    
    updated_count = 0
    errors = 0
    
    for security in securities:
        name = security[0]
        
        # בודק אם יש מיפוי לסמל אמריקאי
        if name in symbol_map:
            symbol = symbol_map[name]
            try:
                print(f'📡 מעדכן {name} ({symbol})...')
                new_price = Broker.update_price(symbol)
                
                # מעדכן במסד הנתונים
                portfolio.execute_query(
                    "UPDATE investments SET price = ? WHERE name = ?",
                    (new_price, name)
                )
                
                print(f'✅ {name}: ${new_price:.2f}')
                updated_count += 1
                time.sleep(1)  # המתנה כדי לא להציף את ה-API
                
            except Exception as e:
                print(f'❌ שגיאה עם {name}: {e}')
                errors += 1
        else:
            print(f'⏭️  מדלג על {name} (אין מיפוי API)')
    
    print('=' * 50)
    print(f'✅ עודכנו {updated_count} מחירים')
    if errors > 0:
        print(f'❌ {errors} שגיאות')
    
    # מציג סיכום עדכני
    print('\n📊 תיק עדכני:')
    all_securities = portfolio.execute_query(
        "SELECT name, price, amount FROM investments"
    )
    
    total_value = 0
    for name, price, amount in all_securities:
        value = price * amount
        total_value += value
        print(f'   {name}: ${price:.2f} × {amount} = ${value:,.2f}')
    
    print(f'\n💰 סך הכל: ${total_value:,.2f}')


if __name__ == "__main__":
    update_portfolio_with_real_prices() 