# זה הקובץ שמנהל את כל הנתונים של התיק – שומר, מוסיף, מוחק, מעדכן, הכל
# עובד אך ורק עם מסד נתונים בענן (PostgreSQL)

# ייבוא ספריות
import os  # ספריה לעבודה עם קבצי מערכת
import random  # ספריה ליצירת מספרים אקראיים
import time  # ספריה לעבודה עם זמן
import requests  # ספריה לבקשות HTTP
import yfinance as yf  # ספריה לקבלת נתוני מניות מהאינטרנט
from abc import ABC, abstractmethod  # ספריה למחלקות אבסטרקטיות

print("=== התחלת טעינת dbmodel.py ===")
print("=== ייבוא ספריות הושלם ===")

# בדיקת זמינות PostgreSQL
try:
    import psycopg2  # ספריית PostgreSQL
    print("ספריות PostgreSQL זמינות")
    POSTGRES_AVAILABLE = True
except ImportError:
    print("ספריות PostgreSQL לא זמינות")
    POSTGRES_AVAILABLE = False

print("=== סיום בדיקת זמינות PostgreSQL ===")

# קבוע המרה מדולר לשקל
USD_TO_ILS_RATE = 3.5


class Security(ABC):  # פה אני יוצר מחלקה בסיס לכל נייר ערך – כמו תבנית
    """פה אני יוצר תבנית לכל נייר ערך – מניה או אג"ח"""
    
    def __init__(self, name, price=None):
        """פה אני מתחיל נייר ערך חדש עם שם ומחיר"""
        self.name = name  # שם הנייר ערך (למשל "אפל" או "אג"ח ממשלתי")
        self.amount = 0  # כמה יחידות יש לי (בהתחלה 0)
        if price is None:
            # אם לא נתנו מחיר, אני יוצר מחיר מדומה
            self.price = random.uniform(10, 100)
        else:
            self.price = price  # המחיר שנתנו לי
    
    @abstractmethod
    def calculate_value(self):
        """פה אני מחשב כמה שווה הנייר ערך – כל סוג מחשב אחרת"""
        pass
    
    def update_price(self, new_price):
        """פה אני מעדכן את המחיר של הנייר ערך"""
        self.price = new_price
    
    def __str__(self):
        """פה אני מחזיר תיאור יפה של הנייר ערך"""
        return f"{self.name} - מחיר: {self.price:.2f}, כמות: {self.amount}"


class Stock(Security):  # פה אני יוצר מחלקה למניות – כמו חלק בחברה
    """פה אני יוצר מניה – כמו לקנות חלק קטן בחברה"""
    
    def __init__(self, name, amount=0, price=None):
        """פה אני מתחיל מניה חדשה"""
        super().__init__(name, price)  # קורא למחלקה הבסיס
        self.amount = amount  # כמה מניות יש לי
        # כמה דיבידנד המניה נותנת (0-5%)
        self.dividend_yield = random.uniform(0, 0.05)
        # כמה המחיר משתנה (10-30%)
        self.volatility = random.uniform(0.1, 0.3)
    
    def calculate_value(self):
        """פה אני מחשב כמה שווה המניה – מחיר כפול כמות"""
        return self.price * self.amount
    
    def calculate_dividend(self):
        """פה אני מחשב כמה דיבידנד אני מקבל מהמניה"""
        return self.calculate_value() * self.dividend_yield
    
    def simulate_price_change(self):
        """פה אני מדמה שינוי במחיר המניה – כמו במציאות"""
        # פה אני יוצר שינוי אקראי במחיר (עלייה או ירידה)
        change_percent = random.uniform(-self.volatility, self.volatility)
        self.price *= (1 + change_percent)
        return self.price
    
    def __str__(self):
        """פה אני מחזיר תיאור יפה של המניה"""
        return (f"מניה: {self.name} - מחיר: {self.price:.2f}, "
                f"כמות: {self.amount}, ערך: {self.calculate_value():.2f}")


class Bond(Security):  # פה אני יוצר מחלקה לאג"חים – כמו הלוואה
    """פה אני יוצר אג"ח – כמו להלוות כסף ולקבל ריבית"""
    
    def __init__(self, name, amount=0, price=None, coupon_rate=None):
        """פה אני מתחיל אג"ח חדש"""
        super().__init__(name, price)
        self.amount = amount  # כמה אג"חים יש לי
        if coupon_rate is None:
            # אם לא נתנו ריבית, אני יוצר ריבית מדומה
            self.coupon_rate = random.uniform(0.02, 0.08)  # ריבית 2-8%
        else:
            self.coupon_rate = coupon_rate  # הריבית שנתנו לי
        # כמה שנים עד שהאג"ח מסתיים
        self.maturity_years = random.randint(1, 10)
    
    def calculate_value(self):
        """פה אני מחשב כמה שווה האג"ח – מחיר כפול כמות"""
        return self.price * self.amount
    
    def calculate_coupon_payment(self):
        """פה אני מחשב כמה ריבית אני מקבל מהאג"ח"""
        return self.calculate_value() * self.coupon_rate
    
    def get_yield_to_maturity(self):
        """פה אני מחשב את התשואה עד לפדיון – כמה אני מרוויח עד הסוף"""
        # זה חישוב מורכב, אז אני מחזיר קירוב פשוט
        return (self.coupon_rate + 
                (100 - self.price) / (self.price * self.maturity_years))
    
    def __str__(self):
        """פה אני מחזיר תיאור יפה של האג"ח"""
        return (f'אג"ח: {self.name} - מחיר: {self.price:.2f}, '
                f'כמות: {self.amount}, ריבית: {self.coupon_rate*100:.1f} אחוז')


class Broker:  # מחלקה שמטפלת בקבלת מחירי מניות מהאינטרנט
    """מחלקה שמטפלת בקבלת מחירי מניות מהאינטרנט"""
    
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

    @staticmethod
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

    @staticmethod
    def get_multiple_prices(symbols):
        """מביאה מחירים של כמה מניות בבת אחת"""
        prices = {}
        for symbol in symbols:
            price = Broker.get_stock_price(symbol)  # מביא מחיר לכל מניה
            if price is not None:
                prices[symbol] = price
            time.sleep(0.1)  # מחכה קצת בין בקשות (לא לעבור על מגבלות)
        return prices

    @staticmethod
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

    @staticmethod
    def get_price_history(symbol, period='1y'):
        """מביאה היסטוריית מחירים של מניה"""
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)  # מביא נתונים לתקופה מסוימת
            return data
        except Exception as e:
            print(f'בעיה עם {symbol}: {e}')
            return None


class Portfolio:  # פה אני יוצר מחלקה לתיק השקעות – כמו תיק עם כל הניירות ערך
    """פה אני יוצר תיק השקעות – כמו תיק עם כל המניות והאג"חים שלי"""
    
    def __init__(self):
        """פה אני מתחיל תיק ריק"""
        self.securities = []  # רשימה של כל הניירות ערך שיש לי
        self.total_value = 0  # ערך כולל של התיק
    
    def add_security(self, security):
        """פה אני מוסיף נייר ערך לתיק – כמו לשים משהו בתיק"""
        self.securities.append(security)
        self._update_total_value()
    
    def remove_security(self, security_name):
        """פה אני מוציא נייר ערך מהתיק – כמו להוציא משהו מהתיק"""
        for i, security in enumerate(self.securities):
            if security.name == security_name:
                del self.securities[i]
                self._update_total_value()
                return True
        return False
    
    def _update_total_value(self):
        """פה אני מחשב את הערך הכולל של התיק"""
        self.total_value = sum(security.calculate_value() 
                              for security in self.securities)
    
    def get_portfolio_summary(self):
        """פה אני מחזיר סיכום של התיק – מה יש לי וכמה שווה הכל"""
        summary = {
            'total_value': self.total_value,
            'num_securities': len(self.securities),
            'stocks': [],
            'bonds': []
        }
        
        for security in self.securities:
            if isinstance(security, Stock):
                summary['stocks'].append({
                    'name': security.name,
                    'value': security.calculate_value(),
                    'dividend': security.calculate_dividend()
                })
            elif isinstance(security, Bond):
                summary['bonds'].append({
                    'name': security.name,
                    'value': security.calculate_value(),
                    'coupon': security.calculate_coupon_payment()
                })
        
        return summary
    
    def __str__(self):
        """פה אני מחזיר תיאור יפה של התיק"""
        summary = self.get_portfolio_summary()
        result = f"תיק השקעות - ערך כולל: {self.total_value:.2f}\n"
        result += f"מספר ניירות ערך: {summary['num_securities']}\n"
        
        if summary['stocks']:
            result += "\nמניות:\n"
            for stock in summary['stocks']:
                result += (f"  {stock['name']}: {stock['value']:.2f} "
                          f"(דיבידנד: {stock['dividend']:.2f})\n")
        
        if summary['bonds']:
            result += '\nאג"חים:\n'
            for bond in summary['bonds']:
                result += (f"  {bond['name']}: {bond['value']:.2f} "
                          f"(ריבית: {bond['coupon']:.2f})\n")
        
        return result


class RiskManager:  # פה אני יוצר מנהל סיכונים – כמו בודק בטיחות
    """פה אני מחשב סיכונים של ניירות ערך – כמה מסוכן זה להשקיע בזה"""
    
    @staticmethod
    def calculate_risk(security_type, industry, variance):
        """פה אני מחשב כמה מסוכן נייר ערך מסוים – ציון בין 1 ל-10"""
        risk_score = 0
        
        # פה אני בודק איזה סוג נייר ערך זה
        if security_type == 'מניה רגילה':
            risk_score += 3  # מניות יותר מסוכנות
        elif security_type == 'אגח ממשלתית':
            risk_score += 1  # אג"ח ממשלתיות פחות מסוכנות
        elif security_type == 'אגח קונצרנית':
            risk_score += 2  # אג"ח של חברות בינוניות
        
        # פה אני בודק באיזה תחום זה
        industry_risks = {
            'טכנולוגיה': 3,  # טכנולוגיה מאוד מסוכנת
            'תחבורה': 2,  # תחבורה בינונית
            'אנרגיה': 2,  # אנרגיה בינונית
            'בריאות': 2,  # בריאות בינונית
            'תעשייה': 1,  # תעשייה פחות מסוכנת
            'פיננסים': 2,  # פיננסים בינוניים
            'נדלן': 2,  # נדלן בינוני
            'צריכה פרטית': 1  # צריכה פחות מסוכנת
        }
        risk_score += industry_risks.get(industry, 2)
        
        # פה אני בודק כמה המחיר משתנה
        if variance == 'גבוה':
            risk_score += 2  # אם המחיר משתנה הרבה – יותר מסוכן
        elif variance == 'נמוך':
            risk_score += 0  # אם המחיר יציב – פחות מסוכן
        
        # פה אני מחזיר ציון בין 1 ל-10
        return min(max(risk_score, 1), 10)
    
    @staticmethod
    def get_risk_description(risk_score):
        """פה אני מחזיר הסבר על רמת הסיכון במילים פשוטות"""
        if risk_score <= 2:
            return "סיכון נמוך מאוד – כמו לשים כסף בבנק"
        elif risk_score <= 4:
            return "סיכון נמוך – כמו לקנות דירה"
        elif risk_score <= 6:
            return "סיכון בינוני – כמו לפתוח עסק קטן"
        elif risk_score <= 8:
            return "סיכון גבוה – כמו לקנות מניות טכנולוגיה"
        else:
            return "סיכון גבוה מאוד – כמו לקנות מניות של חברות קטנות"
    
    @staticmethod
    def calculate_portfolio_risk(portfolio):
        """פה אני מחשב את הסיכון הכללי של כל התיק"""
        if not portfolio:
            return 0
        
        total_risk = 0
        total_value = 0
        
        for item in portfolio:
            # פה אני מחשב סיכון של כל נייר ערך
            risk = RiskManager.calculate_risk(
                item['security_type'],
                item['industry'],
                item['variance']
            )
            value = item['price'] * item['amount']
            total_risk += risk * value  # סיכון כפול ערך
            total_value += value
        
        if total_value == 0:
            return 0
        
        # פה אני מחזיר ממוצע משוקלל של הסיכון
        return total_risk / total_value


class PortfolioController:  # פה אני יוצר מנהל תיק השקעות – כמו יועץ השקעות חכם
    """פה אני מנהל את כל התיק – קונה, מוכר, מחשב סיכונים, מקבל ייעוץ מהבינה המלאכותית"""
    
    def __init__(self, portfolio_model):
        """פה אני מתחיל את המנהל עם מסד הנתונים והבינה המלאכותית"""
        self.portfolio_model = portfolio_model  # מסד הנתונים של התיק
        print("אתחול מנהל תיק השקעות")
    
    def buy_security(self, security, industry, variance, security_type):
        """פה אני קונה מניה/אג"ח חדשה לתיק – כמו ללכת לסופר ולקנות מוצר"""
        try:
            # פה אני שומר את הנייר ערך במסד הנתונים
            self.portfolio_model.add_security(
                security.name,  # שם המניה/אג"ח
                security.amount,  # כמה לקנות
                security.price,  # במחיר כמה
                industry,  # באיזה תחום (טכנולוגיה, בריאות וכו')
                variance,  # כמה המחיר משתנה (נמוך/גבוה)
                security_type  # איזה סוג (מניה/אג"ח)
            )
            return f"קניתי {security.amount} יחידות של {security.name} במחיר {security.price}"
        except Exception as e:
            return f"שגיאה בקנייה: {str(e)}"
    
    def sell_security(self, security_name, amount):
        """פה אני מוכר מניה/אג"ח מהתיק – כמו למכור משהו שקניתי קודם"""
        try:
            # פה אני מוחק את הנייר ערך מהמסד
            self.portfolio_model.remove_security(security_name)
            return f"מכרתי {amount} יחידות של {security_name}"
        except Exception as e:
            return f"שגיאה במכירה: {str(e)}"
    
    def get_portfolio(self):
        """פה אני מביא את כל התיק – רשימה של כל מה שיש לי"""
        print("=== התחלת get_portfolio ===")
        try:
            print("קורא get_all_securities מהמודל")
            securities = self.portfolio_model.get_all_securities()
            print(f"קיבלתי {len(securities)} ניירות ערך מהמודל")
            portfolio = []
            for sec in securities:
                portfolio.append({
                    'name': sec['name'],  # שם המניה/אג"ח
                    'amount': sec['amount'],  # כמה יש לי
                    'price': sec['price'],  # במחיר כמה
                    'industry': sec['industry'],  # באיזה תחום
                    'variance': sec['variance'],  # כמה משתנה
                    'security_type': sec['security_type']  # איזה סוג
                })
            print(f"החזרתי {len(portfolio)} ניירות ערך")
            return portfolio
        except Exception as e:
            print(f"שגיאה בקבלת התיק: {str(e)}")
            return []
    
    def get_advice(self, portfolio, risk_profile):
        """פה אני מקבל ייעוץ מהבינה המלאכותית – כמו לדבר עם יועץ השקעות חכם"""
        print("=== התחלת get_advice ===")
        try:
            # פה אני מכין מידע על התיק בשביל הבינה המלאכותית
            portfolio_info = []
            for item in portfolio:
                portfolio_info.append({
                    'name': item['name'],
                    'amount': item['amount'],
                    'price': item['price'],
                    'industry': item['industry'],
                    'security_type': item['security_type']
                })
            
            print(f"שולח {len(portfolio_info)} ניירות ערך לבינה המלאכותית")
            # פה אני שולח את המידע לבינה המלאכותית ומקבל ייעוץ
            # advice = self.ai_agent.get_investment_advice(portfolio_info, risk_profile)
            advice = "ייעוץ מהבינה המלאכותית - לפתח בהמשך"
            print("קיבלתי ייעוץ מהבינה המלאכותית")
            return advice
        except Exception as e:
            print(f"שגיאה בקבלת ייעוץ: {str(e)}")
            return f"לא הצלחתי לקבל ייעוץ: {str(e)}"
    
    def calculate_total_value(self):
        """פה אני מחשב כמה שווה כל התיק שלי ביחד"""
        portfolio = self.get_portfolio()
        total = 0
        for item in portfolio:
            total += item['price'] * item['amount']  # מחיר כפול כמות
        return total
    
    def update_prices(self):
        """פה אני מעדכן את כל המחירים בתיק – כמו לבדוק מחירים חדשים"""
        try:
            portfolio = self.get_portfolio()
            for item in portfolio:
                # פה אני מביא מחיר חדש מהאינטרנט
                new_price = self._get_current_price(item['name'])
                if new_price:
                    # self.portfolio_model.update_price(item['name'], new_price)
                    pass  # לפתח בהמשך
            return "כל המחירים עודכנו"
        except Exception as e:
            return f"שגיאה בעדכון מחירים: {str(e)}"
    
    def _get_current_price(self, symbol):
        """פה אני מביא מחיר נוכחי מהאינטרנט (או מדומה)"""
        # פה אני יכול להביא מחיר אמיתי מהאינטרנט
        # כרגע אני משתמש במחיר מדומה
        return random.uniform(10, 100)  # מחיר בין 10 ל-100


class PortfolioModel:  # פה אני יוצר מחלקה שמנהלת את כל הנתונים של התיק שלי
    """פה אני שומר את כל המידע של התיק – מניות, אג"חים, מחירים, כמויות וכו'"""

    def __init__(self):
        self.DATABASE_URL = os.environ.get('DATABASE_URL')
        print("=== התחלת יצירת PortfolioModel ===")
        print(f"DATABASE_URL מהסביבה: {self.DATABASE_URL}")
        
        if self.DATABASE_URL:
            print("משתמש ב-PostgreSQL בענן")
            self.use_postgres = True
        else:
            print("לא מוגדר DATABASE_URL, משתמש ב-SQLite מקומי")
            self.use_postgres = False
            self.db_file = 'investments.db'
        
        print("=== סיום יצירת PortfolioModel ===")
        self.init_db()  # יוצר את הטבלאות אם צריך

    def get_connection(self):
        """יוצר חיבור למסד הנתונים"""
        print("=== התחלת get_connection ===")
        if self.use_postgres:
            print(f"מתחבר ל-PostgreSQL: {self.DATABASE_URL}")
            import psycopg2
            conn = psycopg2.connect(self.DATABASE_URL)
            print("חיבור ל-PostgreSQL הצליח")
            return conn
        else:
            print(f"מתחבר ל-SQLite: {self.db_file}")
            import sqlite3
            conn = sqlite3.connect(self.db_file)
            print("חיבור ל-SQLite הצליח")
            return conn

    @property
    def db_url(self):
        """מחזיר את כתובת מסד הנתונים"""
        return self.DATABASE_URL if self.use_postgres else self.db_file

    def get_connection_info(self):
        """מחזיר מידע על החיבור למסד הנתונים"""
        try:
            conn = self.get_connection()
            conn_test = "הצליח" if conn else "נכשל"
            conn.close()
            
            return {
                'type': 'PostgreSQL' if self.use_postgres else 'SQLite',
                'url': self.db_url,
                'status': 'מחובר',
                'details': f'חיבור למסד נתונים {conn_test}'
            }
        except Exception as e:
            return {
                'type': 'PostgreSQL' if self.use_postgres else 'SQLite',
                'url': self.db_url,
                'status': 'שגיאה בחיבור',
                'details': f'שגיאה: {str(e)}'
            }

    def init_db(self):
        """יוצר את הטבלאות אם צריך"""
        print("=== התחלת init_db ===")
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if self.use_postgres:
                print("יוצר טבלת משתמשים ב-PostgreSQL")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        email VARCHAR(120) UNIQUE,
                        role VARCHAR(20) DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                print("יוצר טבלת השקעות ב-PostgreSQL")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investments (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(120) UNIQUE NOT NULL,
                        amount INTEGER NOT NULL,
                        price FLOAT NOT NULL,
                        industry VARCHAR(120),
                        variance FLOAT,
                        security_type VARCHAR(50)
                    )
                ''')
            else:
                print("יוצר טבלת משתמשים ב-SQLite")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        email TEXT UNIQUE,
                        role TEXT DEFAULT 'user',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                print("יוצר טבלת השקעות ב-SQLite")
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS investments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT UNIQUE NOT NULL,
                        amount REAL NOT NULL,
                        price REAL NOT NULL,
                        industry TEXT,
                        variance REAL,
                        security_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
            
            conn.commit()
            conn.close()
            print("טבלאות נוצרו בהצלחה")
        except Exception as e:
            print(f"שגיאה ביצירת טבלאות: {e}")
            raise

    def get_user_by_id(self, user_id):
        """פה אני מחזיר משתמש לפי מזהה"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            placeholder = '%s' if self.use_postgres else '?'
            cursor.execute(f'SELECT id, username, password_hash, email, role FROM users WHERE id = {placeholder}', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'password_hash': user[2],
                    'email': user[3],
                    'role': user[4] if user[4] else 'user'
                }
            return None
        except Exception as e:
            print(f"שגיאה ב-get_user_by_id: {e}")
            return None

    def get_user_by_username(self, username):
        """פה אני מחזיר משתמש לפי שם משתמש"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            placeholder = '%s' if self.use_postgres else '?'
            cursor.execute(f'SELECT id, username, password_hash, email, role FROM users WHERE username = {placeholder}', (username,))
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'username': user[1],
                    'password_hash': user[2],
                    'email': user[3],
                    'role': user[4] if user[4] else 'user'
                }
            return None
        except Exception as e:
            print(f"שגיאה ב-get_user_by_username: {e}")
            return None

    def create_user(self, username, password, email=None):
        """פה אני יוצר משתמש חדש"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            placeholder = '%s' if self.use_postgres else '?'
            cursor.execute(f'''
                INSERT INTO users (username, password_hash, email)
                VALUES ({placeholder}, {placeholder}, {placeholder})
            ''', (username, password, email))
                
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"שגיאה ב-create_user: {e}")
            return False

    def create_user_with_role(self, username, password, role='user', email=None):
        """פה אני יוצר משתמש חדש עם תפקיד"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            placeholder = '%s' if self.use_postgres else '?'
            cursor.execute(f'''
                INSERT INTO users (username, password_hash, email, role)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
            ''', (username, password, email, role))
                
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"שגיאה ב-create_user_with_role: {e}")
            return False

    def create_default_users(self):
        """פה אני יוצר משתמשי ברירת מחדל - admin ו-user"""
        print("=== התחלת יצירת משתמשי ברירת מחדל ===")
        
        try:
            # בדיקה אם המשתמש admin כבר קיים
            admin_user = self.get_user_by_username('admin')
            if not admin_user:
                # יצירת משתמש admin
                if self.create_user_with_role('admin', 'admin', 'admin', 'admin@portfolio.com'):
                    print('משתמש מנהל נוצר: admin / admin')
                else:
                    print('שגיאה ביצירת משתמש מנהל')
            else:
                print('משתמש מנהל כבר קיים')
            
            # בדיקה אם המשתמש user כבר קיים
            regular_user = self.get_user_by_username('user')
            if not regular_user:
                # יצירת משתמש רגיל
                if self.create_user_with_role('user', 'user', 'user', 'user@portfolio.com'):
                    print('משתמש רגיל נוצר: user / user')
                else:
                    print('שגיאה ביצירת משתמש רגיל')
            else:
                print('משתמש רגיל כבר קיים')
                
            print("=== סיום יצירת משתמשי ברירת מחדל ===")
            return True
            
        except Exception as e:
            print(f"שגיאה ביצירת משתמשי ברירת מחדל: {e}")
            return False

    def add_security(self, name, amount, price, industry, variance, security_type):
        """פה אני מוסיף מניה/אג"ח חדשה לתיק"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f'''
            INSERT INTO investments (name, amount, price, industry, variance, security_type)
            VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        ''', (name, amount, price, industry, variance, security_type))
            
        conn.commit()
        conn.close()
        return f"נייר הערך {name} נוסף בהצלחה"

    def get_all_securities(self):
        """פה אני מחזיר את כל המניות והאג"חים שיש לי בתיק, כמו רשימה בסופר"""
        print("=== התחלת get_all_securities ===")
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM investments')
            securities = cursor.fetchall()
            conn.close()
            result = []
            for sec in securities:
                result.append({
                    'id': sec[0],
                    'name': sec[1],
                    'amount': float(sec[2]),
                    'price': float(sec[3]),
                    'industry': sec[4],
                    'variance': sec[5],
                    'security_type': sec[6],
                    'created_at': sec[7] if len(sec) > 7 else None
                })
            print(f"נמצאו {len(result)} ניירות ערך")
            return result
        except Exception as e:
            print(f"שגיאה ב-get_all_securities: {e}")
            raise

    def remove_security(self, name):
        """פה אני מוחק מניה/אג"ח מהתיק"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        placeholder = '%s' if self.use_postgres else '?'
        cursor.execute(f'DELETE FROM investments WHERE name = {placeholder}', (name,))
            
        conn.commit()
        conn.close()
        return f"נייר הערך {name} נמחק בהצלחה"

    def update_security_price(self, name, new_price):
        """פה אני מעדכן מחיר של נייר ערך ספציפי"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            placeholder = '%s' if self.use_postgres else '?'
            cursor.execute(f'UPDATE investments SET price = {placeholder} WHERE name = {placeholder}', (new_price, name))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return f"מחיר {name} עודכן ל-{new_price:.2f} ₪"
            else:
                conn.close()
                return f"לא נמצא נייר ערך בשם {name}"
                
        except Exception as e:
            print(f"שגיאה בעדכון מחיר עבור {name}: {e}")
            raise

    def create_tables(self):
        """יוצר את כל הטבלאות במסד הנתונים"""
        print("=== התחלת create_tables ===")
        self.init_db()
        print("create_tables הושלם בהצלחה")

    def execute_query(self, query, params=None):
        """פונקציה כללית לביצוע כל סוג של שאילתה - תואמת לגרסה המקורית של SQLite"""
        conn = self.get_connection()  # מקבל חיבור למסד הנתונים
        cursor = conn.cursor()  # יוצר סמן לביצוע פעולות
        
        try:
            if params:  # אם יש פרמטרים נוספים לשאילתה
                cursor.execute(query, params)  # מריץ את השאילתה עם הפרמטרים
            else:  # אם אין פרמטרים
                cursor.execute(query)  # מריץ את השאילתה בלי פרמטרים

            # בודק אם זו שאילתת בחירה (SELECT) שמחזירה תוצאות
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()  # מקבל את כל התוצאות
                conn.close()  # סוגר את החיבור
                return results  # מחזיר את התוצאות
            else:  # אם זו פעולת עדכון, הוספה או מחיקה
                conn.commit()  # שומר את השינויים במסד הנתונים
                conn.close()  # סוגר את החיבור
                return None  # לא מחזיר כלום
        except Exception as e:
            conn.close()
            print(f"שגיאה ב-execute_query: {e}")
            raise

    def get_securities(self):
        """פונקציה לשליפת כל ניירות הערך מהתיק - תואמת לגרסה המקורית של SQLite"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # שולף את השם והמחיר של כל ניירות הערך מהטבלה
            cursor.execute("SELECT name, price FROM investments")
            results = cursor.fetchall()  # מקבל את כל התוצאות כרשימה
            conn.close()  # סוגר את החיבור למסד הנתונים
            return results  # מחזיר את רשימת ניירות הערך
        except Exception as e:
            print(f"שגיאה ב-get_securities: {e}")
            return []

# מחלקות מיוחדות יותר שיורשות מהמחלקות הבסיסיות

class RegularStock(Stock):  # מחלקה למניה רגילה - יורשת מ-Stock
    """מחלקה למניה רגילה - הסוג הנפוץ ביותר של מניות"""
    
    def __init__(self, name, amount=0, price=None):
        """פונקציה שמתחילה מניה רגילה"""
        super().__init__(name, amount, price)  # קוראת לפונקציה של מחלקת המניה הבסיסית
        self.stock_type = "מניה רגילה"


class PreferredStock(Stock):  # מחלקה למניה מועדפת - יורשת מ-Stock
    """מחלקה למניה מועדפת - מניה עם זכויות מיוחדות"""
    
    def __init__(self, name, amount=0, price=None):
        """פונקציה שמתחילה מניה מועדפת"""
        super().__init__(name, amount, price)  # קוראת לפונקציה של מחלקת המניה הבסיסית
        self.stock_type = "מניה מועדפת"
        # מניות מועדפות בדרך כלל נותנות דיבידנד גבוה יותר
        self.dividend_yield = random.uniform(0.04, 0.08)  # 4-8%


class CorporateBond(Bond):  # מחלקה לאג"ח קונצרני - יורשת מ-Bond
    """מחלקה לאג"ח קונצרני - אג"ח שמנפיקות חברות פרטיות"""
    
    def __init__(self, name, amount=0, price=None, coupon_rate=None):
        """פונקציה שמתחילה אג"ח קונצרני"""
        super().__init__(name, amount, price, coupon_rate)  # קוראת לפונקציה של מחלקת האג"ח הבסיסית
        self.bond_type = "אג\"ח קונצרני"
        # אג"חים קונצרניים בדרך כלל נותנים ריבית גבוהה יותר (יותר סיכון)
        if coupon_rate is None:
            self.coupon_rate = random.uniform(0.04, 0.12)  # ריבית 4-12%


class GovernmentalBond(Bond):  # מחלקה לאג"ח ממשלתי - יורשת מ-Bond
    """מחלקה לאג"ח ממשלתי - אג"ח שמנפיקה הממשלה"""
    
    def __init__(self, name, amount=0, price=None, coupon_rate=None):
        """פונקציה שמתחילה אג"ח ממשלתי"""
        super().__init__(name, amount, price, coupon_rate)  # קוראת לפונקציה של מחלקת האג"ח הבסיסית
        self.bond_type = "אג\"ח ממשלתי"
        # אג"חים ממשלתיים בדרך כלל נותנים ריבית נמוכה יותר (פחות סיכון)
        if coupon_rate is None:
            self.coupon_rate = random.uniform(0.01, 0.05)  # ריבית 1-5%


print("=== סיום טעינת dbmodel.py ===") 