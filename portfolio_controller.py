import sqlite3  # ייבוא ספרייה לעבודה עם מסד נתונים של SQLite
from dbmodel import PortfolioModel  # ייבוא מחלקת ניהול מסד הנתונים שיצרנו
from ollamamodel import AI_Agent  # ייבוא מחלקת הבינה המלאכותית לייעוץ
import broker  # ייבוא מודול לקבלת מחירי מניות מהאינטרנט

class PortfolioController:  # מחלקה ראשית שמנהלת את כל פעולות תיק ההשקעות
    def __init__(self, model):  # פונקציה שמתחילה את הקונטרולר
        self.model = model  # שומר את מסד הנתונים למשתנה פנימי של המחלקה
        self.ollama_model = AI_Agent()  # יוצר מופע של הבינה המלאכותית לייעוץ

    def buy_security(self, security, industry=None, variance=None, security_type=None):  # פונקציה לרכישת נייר ערך חדש לתיק
        """רכישת נייר ערך והוספתו למסד הנתונים"""
        try:  # מנסה לבצע את הפעולה
            # קבלת המחיר הנוכחי של המניה מהאינטרנט
            price = broker.Broker.update_price(security.name)
            # הוספת המניה למסד הנתונים או עדכון הכמות אם היא כבר קיימת
            self.model.execute_query(
                "INSERT INTO investments (name, price, amount, industry, variance, security_type) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(name) "
                "DO UPDATE SET amount = amount + excluded.amount, price = excluded.price, industry = excluded.industry, variance = excluded.variance, security_type = excluded.security_type",
                (security.name, price, security.amount, industry, variance, security_type)
            )
            return f"נייר ערך {security.name} נוסף בהצלחה!"  # מחזיר הודעת הצלחה
        except sqlite3.IntegrityError:  # אם יש שגיאה במסד הנתונים
            return "נייר הערך כבר קיים בתיק ההשקעות."  # מחזיר הודעת שגיאה



    def remove_security(self, name):  # פונקציה למחיקה מלאה של נייר ערך מהתיק
        """מחיקה מלאה של נייר ערך מהתיק"""
        # מוחק את נייר הערך לגמרי מהמסד נתונים
        self.model.execute_query("DELETE FROM investments WHERE name = ?", (name,))
        return f"נייר הערך {name} נמחק בהצלחה מהתיק"

    def get_portfolio(self):  # פונקציה לקבלת כל ניירות הערך בתיק
        """שליפת כל ניירות הערך בתיק ההשקעות"""
        # שולף את כל המידע הנחוץ לחישוב סיכון
        rows = self.model.execute_query("SELECT name, price, amount, industry, variance, security_type FROM investments")
        if rows:  # אם יש תוצאות
            portfolio = []
            for row in rows:
                # חישוב רמת סיכון לכל השקעה
                risk_level = RiskManager.calculate_risk(
                    row[5] if row[5] else "מניה רגילה",  # security_type
                    row[3] if row[3] else "צריכה פרטית",  # industry
                    row[4] if row[4] else "נמוך"  # variance
                )
                
                portfolio.append({
                    "name": row[0], 
                    "price": row[1], 
                    "amount": row[2],
                    "industry": row[3] if row[3] else "לא מוגדר",
                    "variance": row[4] if row[4] else "לא מוגדר", 
                    "security_type": row[5] if row[5] else "לא מוגדר",
                    "risk_level": risk_level
                })
            return portfolio
        return []  # מחזיר רשימה רקה אם אין השקעות

    def get_advice(self, question):  # פונקציה לקבלת ייעוץ מהבינה המלאכותית
        """קבלת ייעוץ מסוכן AI"""
        # שולח את השאלה לבינה המלאכותית ומחזיר את התשובה
        return self.ollama_model.get_advice(question)

class RiskManager:  # מחלקה לחישוב סיכונים של השקעות
    # מילון שמגדיר רמת סיכון לכל ענף - ככל שהמספר גבוה יותר, הסיכון גבוה יותר
    RISK_SCALE = {
        "טכנולוגיה": 6,      # ענף עם סיכון גבוה - מחירים משתנים הרבה
        "תחבורה": 5,         # ענף עם סיכון בינוני-גבוה
        "אנרגיה": 4,         # ענף עם סיכון בינוני
        "בריאות": 4,         # ענף עם סיכון בינוני
        "תעשייה": 3,         # ענף עם סיכון בינוני-נמוך
        "פיננסים": 3,        # ענף עם סיכון בינוני-נמוך
        "נדלן": 2,           # ענף עם סיכון נמוך
        "צריכה פרטית": 1     # ענף עם סיכון הכי נמוך
    }

    # מילון שמגדיר רמת סיכון לפי שונות המחירים
    VARIATION_SCALE = {
        "נמוך": 1,   # שונות נמוכה - מחירים יציבים
        "גבוה": 2    # שונות גבוהה - מחירים משתנים הרבה
    }

    @staticmethod  # פונקציה סטטית שלא צריכה מופע של המחלקה
    def calculate_risk(security_type, sector, variation):  # פונקציה לחישוב סיכון כולל
        # מקבל את רמת הסיכון הבסיסית של הענף
        base_risk = RiskManager.RISK_SCALE.get(sector, 1)
        # מקבל את רמת השונות
        variation_risk = RiskManager.VARIATION_SCALE.get(variation, 1)

        # חישוב סיכון לפי סוג נייר הערך
        if security_type == "אגח ממשלתית":
            return base_risk * variation_risk * 0.5  # אג"ח ממשלתי - סיכון נמוך יותר
        elif security_type == "אגח קונצרנית":
            return base_risk * variation_risk * 0.1  # אג"ח קונצרני - סיכון נמוך מאוד
        return base_risk * variation_risk  # מניה רגילה - סיכון מלא 