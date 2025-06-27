# זה הקובץ שמנהל את כל הלוגיקה של התיק – קנייה, מכירה, חישוב סיכונים, ייעוץ מהבינה המלאכותית
# פה אני מחליט מה לקנות, מה למכור, איך לחשב סיכון, ואיך לקבל ייעוץ חכם

print("=== התחלת טעינת portfolio_controller.py ===")

from ollamamodel import AI_Agent  # מביא את המחלקה שמדברת עם הבינה המלאכותית
import random  # כלי ליצירת מספרים אקראיים (למחירים מדומים)

print("=== ייבוא ספריות הושלם ===")


class PortfolioController:  # פה אני יוצר מנהל תיק השקעות – כמו יועץ השקעות חכם
    """פה אני מנהל את כל התיק – קונה, מוכר, מחשב סיכונים, מקבל ייעוץ מהבינה המלאכותית"""
    
    def __init__(self, portfolio_model):
        """פה אני מתחיל את המנהל עם מסד הנתונים והבינה המלאכותית"""
        self.portfolio_model = portfolio_model  # מסד הנתונים של התיק
        self.ai_agent = AI_Agent()  # הבינה המלאכותית שנותנת ייעוץ
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
            advice = self.ai_agent.get_investment_advice(portfolio_info, risk_profile)
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
                    self.portfolio_model.update_price(item['name'], new_price)
            return "כל המחירים עודכנו"
        except Exception as e:
            return f"שגיאה בעדכון מחירים: {str(e)}"
    
    def _get_current_price(self, symbol):
        """פה אני מביא מחיר נוכחי מהאינטרנט (או מדומה)"""
        # פה אני יכול להביא מחיר אמיתי מהאינטרנט
        # כרגע אני משתמש במחיר מדומה
        return random.uniform(10, 100)  # מחיר בין 10 ל-100


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

print("=== סיום טעינת portfolio_controller.py ===") 