import requests  # ייבוא ספריית בקשות HTTP
import yfinance as yf  # ספרייה שמביאה נתונים מהבורסה האמריקאית
import time  # ספרייה לעיכובים בין בקשות

#API_KEY = '87RYKHP1CUPBGWY1'  # מפתח API לשימוש ב-Alpha Vantage
API_KEY = '451FPPPSEOOZIDV4'  # API KEY 2 למטרת בדיקות עקב הגבלת פניות
#API_KEY = 'XX4SBD1SXLFLUSV2'  # API KEY 3 למטרת בדיקות עקב הגבלת פניות

# קבוע המרה מדולר לשקל
USD_TO_ILS_RATE = 3.5

class Broker:  # מחלקה שמטפלת בקבלת מחירי מניות מהאינטרנט
    # מפתח API של Alpha Vantage לקבלת מידע על מחירי מניות
    API_KEY = "451FPPPSEOOZIDV4"
    # כתובת בסיס של שירות Alpha Vantage לקבלת נתוני מניות
    BASE_URL = "https://www.alphavantage.co/query"
    
    @staticmethod  # פונקציה סטטית שלא צריכה מופע של המחלקה
    def update_price(symbol):  # פונקציה לקבלת מחיר עדכני של מניה
        """קבלת מחיר עדכני של מניה מ-Alpha Vantage API"""
        # יצירת רשימה של פרמטרים לשליחה לשירות
        params = {
            'function': 'GLOBAL_QUOTE',  # סוג הבקשה - קבלת מחיר נוכחי
            'symbol': symbol,  # סמל המניה (לדוגמה: AAPL, TSLA)
            'apikey': Broker.API_KEY  # המפתח שלנו לגישה לשירות
        }
        
        try:  # מנסה לבצע את הבקשה
            # שולח בקשה HTTP לשירות Alpha Vantage
            response = requests.get(Broker.BASE_URL, params=params)
            # הופך את התשובה מ-JSON לאובייקט פייתון
            data = response.json()
            
            # בודק אם יש את המידע הדרוש בתשובה
            if 'Global Quote' in data:
                # מחלץ את המחיר הנוכחי מהתשובה
                current_price = data['Global Quote']['05. price']
                # ממיר מדולר לשקל
                ils_price = float(current_price) * USD_TO_ILS_RATE
                return ils_price  # מחזיר את המחיר בשקלים
            else:  # אם אין מידע על המניה
                print(f"לא נמצא מידע על {symbol}")  # מדפיס הודעת שגיאה
                return 100.0 * USD_TO_ILS_RATE  # מחזיר מחיר ברירת מחדל בשקלים
                
        except Exception as e:  # אם יש שגיאה בתקשורת עם השירות
            print(f"שגיאה בקבלת מחיר עבור {symbol}: {e}")  # מדפיס את השגיאה
            return 100.0 * USD_TO_ILS_RATE  # מחזיר מחיר ברירת מחדל בשקלים 

# פונקציה שמביאה מחיר אמיתי של מניה מהבורסה

def get_stock_price(symbol):
    """מביאה את המחיר הנוכחי של מניה מהבורסה"""
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

# פונקציה שמביאה מחירים של כמה מניות בבת אחת

def get_multiple_prices(symbols):
    """מביאה מחירים של כמה מניות בבת אחת"""
    prices = {}
    for symbol in symbols:
        price = get_stock_price(symbol)  # מביא מחיר לכל מניה
        if price is not None:
            prices[symbol] = price
        time.sleep(0.1)  # מחכה קצת בין בקשות (לא לעבור על מגבלות)
    return prices

# פונקציה שמדמה מסחר (קנייה ומכירה)

def simulate_trade(symbol, action, amount, current_price):
    """מדמה מסחר – קנייה או מכירה של מניות"""
    if action == 'buy':
        # מדמה קנייה
        total_cost = amount * current_price
        print(f'קניתי {amount} מניות של {symbol} במחיר {current_price}')
        return total_cost
    elif action == 'sell':
        # מדמה מכירה
        total_revenue = amount * current_price
        print(f'מכרתי {amount} מניות של {symbol} במחיר {current_price}')
        return total_revenue
    else:
        print('פעולה לא מוכרת')
        return 0

# פונקציה שמביאה מידע מפורט על מניה

def get_stock_info(symbol):
    """מביאה מידע מפורט על מניה"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info  # מביא מידע כללי על המניה
        
        # בוחר רק את המידע החשוב
        important_info = {
            'name': info.get('longName', 'לא ידוע'),
            'sector': info.get('sector', 'לא ידוע'),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'dividend_yield': info.get('dividendYield', 0)
        }
        
        return important_info
    except Exception as e:
        print(f'בעיה עם {symbol}: {e}')
        return None

# פונקציה שמביאה היסטוריית מחירים

def get_price_history(symbol, period='1y'):
    """מביאה היסטוריית מחירים של מניה"""
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)  # מביא נתונים לתקופה מסוימת
        return data
    except Exception as e:
        print(f'בעיה עם {symbol}: {e}')
        return None

# אם מריצים את הקובץ הזה ישירות – תבדוק כמה מניות
if __name__ == '__main__':
    print('בודק מחירים של מניות פופולריות...')
    
    # רשימת מניות לבדיקה
    test_symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
    
    # מביא מחירים
    prices = get_multiple_prices(test_symbols)
    
    # מציג תוצאות
    for symbol, price in prices.items():
        print(f'{symbol}: ${price:.2f}') 