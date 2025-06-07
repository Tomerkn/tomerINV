#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקת מה בדיוק מחזיר Alpha Vantage API
"""

import requests
import json


def debug_alpha_vantage():
    """בודק מה בדיוק מחזיר ה-API"""
    
    API_KEY = "451FPPPSEOOZIDV4"
    BASE_URL = "https://www.alphavantage.co/query"
    
    symbols = ['AAPL', 'MSFT']
    
    for symbol in symbols:
        print(f'\n🔍 בודק {symbol}...')
        print('=' * 50)
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol,
            'apikey': API_KEY
        }
        
        try:
            response = requests.get(BASE_URL, params=params)
            print(f'Status Code: {response.status_code}')
            
            data = response.json()
            print('תשובה מלאה מה-API:')
            print(json.dumps(data, indent=2))
            
            # בדיקה אם יש הגבלה
            if 'Note' in data:
                print('⚠️ יש הגבלה של API!')
                print(data['Note'])
            
            # בדיקה אם יש שגיאה
            if 'Error Message' in data:
                print('❌ שגיאה:')
                print(data['Error Message'])
            
            # בדיקה אם יש המידע שאנחנו מצפים לו
            if 'Global Quote' in data:
                print('✅ המידע נמצא!')
                quote = data['Global Quote']
                if '05. price' in quote:
                    price = quote['05. price']
                    print(f'💰 מחיר: ${price}')
                else:
                    print('❌ אין מחיר בתשובה')
                    print('מפתחות זמינים:', list(quote.keys()))
            else:
                print('❌ אין Global Quote בתשובה')
                print('מפתחות זמינים:', list(data.keys()))
            
        except Exception as e:
            print(f'❌ שגיאה: {e}')
        
        print('=' * 50)


if __name__ == "__main__":
    debug_alpha_vantage() 