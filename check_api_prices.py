#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקת מחירים אמיתיים מ-Alpha Vantage API
"""

from broker import Broker
import time


def check_real_api_prices():
    """בודק מחירים אמיתיים מ-API"""
    
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NFLX', 'TSLA', 'META']
    
    print('🔍 בודק מחירים אמיתיים מ-Alpha Vantage API...')
    print('=' * 60)
    
    real_prices = {}
    
    for symbol in symbols:
        try:
            print(f'📡 מבקש מחיר עבור {symbol}...')
            price = Broker.update_price(symbol)
            real_prices[symbol] = price
            print(f'📈 {symbol}: ${price:.2f} ✅')
            time.sleep(2)  # המתנה בין בקשות
        except Exception as e:
            print(f'❌ שגיאה עם {symbol}: {e}')
            real_prices[symbol] = None
    
    print('=' * 60)
    print('📊 סיכום מחירים אמיתיים:')
    
    for symbol, price in real_prices.items():
        if price:
            print(f'   {symbol}: ${price:.2f}')
        else:
            print(f'   {symbol}: לא זמין')
    
    return real_prices


if __name__ == "__main__":
    check_real_api_prices() 