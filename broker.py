import requests  # ייבוא ספריית בקשות HTTP

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