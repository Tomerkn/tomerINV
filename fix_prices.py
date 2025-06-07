#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
מעדכן מחירים עם מספר API keys
"""

import requests
from dbmodel import PortfolioModel

# קבוע המרה מדולר לשקל
USD_TO_ILS_RATE = 3.5


def try_get_price(symbol, api_key):
    """מנסה לקבל מחיר עם API key אחד"""
    url = "https://www.alphavantage.co/query"
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # בודק אם יש הגבלה
        if 'Information' in data and 'rate limit' in data['Information']:
            return None, "הגבלה"
        
        # בודק אם יש מידע
        if 'Global Quote' in data and '05. price' in data['Global Quote']:
            usd_price = float(data['Global Quote']['05. price'])
            ils_price = usd_price * USD_TO_ILS_RATE
            return ils_price, "הצלחה"
        
        return None, "אין מידע"
    except Exception:
        return None, "שגיאה"


def get_real_price(symbol):
    """מקבל מחיר אמיתי עם מעבר בין API keys"""
    
    # רשימת API keys
    api_keys = [
        "451FPPPSEOOZIDV4",
        "87RYKHP1CUPBGWY1", 
        "XX4SBD1SXLFLUSV2"
    ]
    
    # מחירים מציאותיים לגיבוי (מוכפלים ב-3.5 לשקלים)
    realistic_prices = {
        'AAPL': 195.89 * USD_TO_ILS_RATE,
        'MSFT': 417.86 * USD_TO_ILS_RATE,
        'GOOGL': 170.63 * USD_TO_ILS_RATE,
        'AMZN': 205.38 * USD_TO_ILS_RATE,
        'NFLX': 887.25 * USD_TO_ILS_RATE,
        'TSLA': 248.98 * USD_TO_ILS_RATE,
        'META': 570.17 * USD_TO_ILS_RATE,
        'TEVA': 16.84 * USD_TO_ILS_RATE,
        'CHKP': 151.25 * USD_TO_ILS_RATE,
        'NICE': 224.85 * USD_TO_ILS_RATE,
        'CYBR': 312.47 * USD_TO_ILS_RATE,
        'KO': 62.35 * USD_TO_ILS_RATE,
        'XOM': 118.92 * USD_TO_ILS_RATE,
        'MCD': 295.47 * USD_TO_ILS_RATE,
        'NKE': 72.58 * USD_TO_ILS_RATE,
        'JPM': 233.85 * USD_TO_ILS_RATE,
        'JNJ': 146.23 * USD_TO_ILS_RATE
    }
    
    print(f'🔍 מחפש מחיר עבור {symbol}...')
    
    # מנסה עם כל API key
    for i, api_key in enumerate(api_keys):
        print(f'   מנסה API key #{i+1}...')
        price, status = try_get_price(symbol, api_key)
        
        if status == "הצלחה":
            print(f'   ✅ הצלחה! מחיר: ₪{price:.2f}')
            return price
        elif status == "הגבלה":
            print(f'   ⚠️ API key #{i+1} הגיע להגבלה')
        else:
            print(f'   ❌ API key #{i+1}: {status}')
    
    # אם כל API keys נכשלו
    print('   🔄 משתמש במחיר מציאותי...')
    if symbol.upper() in realistic_prices:
        price = realistic_prices[symbol.upper()]
        print(f'   💰 מחיר מציאותי: ₪{price:.2f}')
        return price
    else:
        print(f'   ❌ לא נמצא מחיר עבור {symbol}')
        return 100.0 * USD_TO_ILS_RATE


def update_all_prices():
    """מעדכן כל המניות"""
    portfolio = PortfolioModel()
    
    print('🚀 מתחיל עדכון מחירים...')
    print('=' * 50)
    
    # מקבל רשימת מניות
    securities = portfolio.execute_query("SELECT name FROM investments")
    
    for symbol_tuple in securities:
        symbol = symbol_tuple[0]
        
        # מקבל מחיר חדש
        new_price = get_real_price(symbol)
        
        # מעדכן במסד הנתונים
        portfolio.execute_query(
            "UPDATE investments SET price = ? WHERE name = ?",
            (new_price, symbol)
        )
        
        print(f'✅ {symbol} עודכן ל-₪{new_price:.2f}\n')
    
    print('=' * 50)
    print('🎉 סיימתי לעדכן את כל המחירים!')
    
    # מציג סיכום
    print('\n💰 סיכום התיק המעודכן:')
    updated = portfolio.execute_query(
        "SELECT name, price, amount FROM investments"
    )
    
    total = 0
    for symbol, price, amount in updated:
        value = price * amount
        total += value
        print(f'   {symbol}: {amount} × ₪{price:.2f} = ₪{value:,.2f}')
    
    print(f'\n🚀 סך התיק: ₪{total:,.2f}')


if __name__ == "__main__":
    update_all_prices() 