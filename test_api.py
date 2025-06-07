#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקת Alpha Vantage API - מחירים אמיתיים
"""

from broker import Broker
import time


def test_alpha_vantage():
    """בודק מחירים אמיתיים מ-Alpha Vantage API"""
    
    # מניות לבדיקה
    stocks_to_check = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'TEVA']
    
    print('🔍 בודק מחירים אמיתיים מ-Alpha Vantage API...')
    print('=' * 60)
    
    real_prices = {}
    
    for stock in stocks_to_check:
        try:
            print(f'📡 מבקש מחיר עבור {stock}...')
            price = Broker.update_price(stock)
            real_prices[stock] = price
            print(f'📈 {stock}: ${price:.2f}')
            time.sleep(1)  # המתנה של שנייה כדי לא להציף את ה-API
        except Exception as e:
            print(f'❌ שגיאה עם {stock}: {e}')
            real_prices[stock] = None
    
    print('=' * 60)
    print('✅ סיכום מחירים אמיתיים:')
    
    for stock, price in real_prices.items():
        if price:
            print(f'   {stock}: ${price:.2f}')
        else:
            print(f'   {stock}: לא זמין')
    
    return real_prices


if __name__ == "__main__":
    test_alpha_vantage() 