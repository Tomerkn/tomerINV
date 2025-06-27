#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט להוספת נתונים אמיתיים למסד הנתונים
מוסיף מניות אמיתיות עם מחירים מעודכנים מ-Alpha Vantage API
"""

import sqlite3  # ספרייה שמאפשרת לי לעבוד עם מסד נתונים מקומי (קובץ)
import yfinance as yf  # ספרייה שמביאה נתונים אמיתיים מהאינטרנט על מניות

# פה אני מגדיר את שם קובץ מסד הנתונים
DB_PATH = 'investments.db'  # זה הקובץ שבו נשמרים כל הנתונים

# פה אני מגדיר אילו מניות להכניס (אפשר להוסיף או לשנות)
stocks = [
    {'symbol': 'AAPL', 'name': 'Apple'},
    {'symbol': 'MSFT', 'name': 'Microsoft'},
    {'symbol': 'GOOGL', 'name': 'Google'},
    {'symbol': 'AMZN', 'name': 'Amazon'},
    {'symbol': 'TSLA', 'name': 'Tesla'}
]

def get_latest_price(symbol):
    """מביא את המחיר האחרון של מניה מהאינטרנט"""
    try:
        stock = yf.Ticker(symbol)  # יוצר אובייקט של המניה
        data = stock.history(period='1d')  # מביא נתונים של יום אחד
        if not data.empty:
            return data['Close'][0]  # מחזיר את מחיר הסגירה
        else:
            return None
    except Exception as e:
        print(f'בעיה עם {symbol}: {e}')
        return None

def insert_stocks_to_db():
    """מכניס את כל המניות למסד הנתונים"""
    conn = sqlite3.connect(DB_PATH)  # פותח חיבור למסד הנתונים
    cursor = conn.cursor()  # יוצר סמן (כמו עכבר) לעבודה מול הטבלאות

    # עובר על כל מניה ברשימה
    for stock in stocks:
        price = get_latest_price(stock['symbol'])  # מביא מחיר אמיתי
        if price is not None:
            # מוסיף למסד הנתונים
            cursor.execute(
                'INSERT INTO securities (name, symbol, price, type) VALUES (?, ?, ?, ?)',
                (stock['name'], stock['symbol'], price, 'stock')
            )
            print(f"הוספתי את {stock['name']} במחיר {price}")
        else:
            print(f"לא הצלחתי להביא מחיר ל-{stock['name']}")

    conn.commit()  # שומר את כל השינויים
    conn.close()  # סוגר את החיבור
    print('סיימתי להכניס מניות למסד הנתונים!')

if __name__ == '__main__':
    print("מתחיל הוספת נתונים אמיתיים למסד הנתונים...")
    insert_stocks_to_db()  # מריץ את הפונקציה הראשית 