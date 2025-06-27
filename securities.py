# זה הקובץ שמגדיר מה זה מניה ומה זה אג"ח – כמו להסביר מה זה דולר ומה זה שקל
# פה אני יוצר מחלקות שמתנהגות כמו ניירות ערך אמיתיים

print("=== התחלת טעינת securities.py ===")

import random  # כלי ליצירת מספרים אקראיים (למחירים מדומים)
from abc import ABC, abstractmethod  # כלים ליצירת מחלקות בסיס (לא חשוב להבין)

print("=== ייבוא ספריות הושלם ===")


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
        self.dividend_yield = random.uniform(0, 0.05)  # כמה דיבידנד המניה נותנת (0-5%)
        self.volatility = random.uniform(0.1, 0.3)  # כמה המחיר משתנה (10-30%)
    
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
        return f"מניה: {self.name} - מחיר: {self.price:.2f}, כמות: {self.amount}, ערך: {self.calculate_value():.2f}"


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
        self.maturity_years = random.randint(1, 10)  # כמה שנים עד שהאג"ח מסתיים
    
    def calculate_value(self):
        """פה אני מחשב כמה שווה האג"ח – מחיר כפול כמות"""
        return self.price * self.amount
    
    def calculate_coupon_payment(self):
        """פה אני מחשב כמה ריבית אני מקבל מהאג"ח"""
        return self.calculate_value() * self.coupon_rate
    
    def get_yield_to_maturity(self):
        """פה אני מחשב את התשואה עד לפדיון – כמה אני מרוויח עד הסוף"""
        # זה חישוב מורכב, אז אני מחזיר קירוב פשוט
        return self.coupon_rate + (100 - self.price) / (self.price * self.maturity_years)
    
    def __str__(self):
        """פה אני מחזיר תיאור יפה של האג"ח"""
        return f'אג"ח: {self.name} - מחיר: {self.price:.2f}, כמות: {self.amount}, ריבית: {self.coupon_rate*100:.1f} אחוז'


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
        self.total_value = sum(security.calculate_value() for security in self.securities)
    
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
                result += f"  {stock['name']}: {stock['value']:.2f} (דיבידנד: {stock['dividend']:.2f})\n"
        
        if summary['bonds']:
            result += '\nאג"חים:\n'
            for bond in summary['bonds']:
                result += f"  {bond['name']}: {bond['value']:.2f} (ריבית: {bond['coupon']:.2f})\n"
        
        return result 