# מחלקות שמייצגות סוגים שונים של ניירות ערך במערכת

class Security:  # מחלקת בסיס שמייצגת נייר ערך כלשהו
    def __init__(self, name):  # פונקציה שמתחילה נייר ערך עם שם
        self.name = name  # שם נייר הערך (לדוגמה: "אפל", "מיקרוסופט")

class Stock(Security):  # מחלקה שמייצגת מניה - יורשת מהמחלקה Security
    def __init__(self, name, amount):  # פונקציה שמתחילה מניה חדשה
        super().__init__(name)  # קוראת לפונקציה של המחלקה האם כדי להגדיר את השם
        self.amount = amount  # כמות המניות שיש לנו

class Bond(Security):  # מחלקה שמייצגת אג"ח - יורשת מהמחלקה Security
    def __init__(self, name):  # פונקציה שמתחילה אג"ח חדש
        super().__init__(name)  # קוראת לפונקציה של המחלקה האם כדי להגדיר את השם

# מחלקות מיוחדות יותר שיורשות מהמחלקות הבסיסיות

class RegularStock(Stock):  # מחלקה למניה רגילה - יורשת מ-Stock
    def __init__(self, name, amount):  # פונקציה שמתחילה מניה רגילה
        super().__init__(name, amount)  # קוראת לפונקציה של מחלקת המניה הבסיסית

class PreferredStock(Stock):  # מחלקה למניה מועדפת - יורשת מ-Stock
    def __init__(self, name, amount):  # פונקציה שמתחילה מניה מועדפת
        super().__init__(name, amount)  # קוראת לפונקציה של מחלקת המניה הבסיסית

class CorporateBond(Bond):  # מחלקה לאג"ח קונצרני - יורשת מ-Bond
    def __init__(self, name):  # פונקציה שמתחילה אג"ח קונצרני
        super().__init__(name)  # קוראת לפונקציה של מחלקת האג"ח הבסיסית

class GovernmentalBond(Bond):  # מחלקה לאג"ח ממשלתי - יורשת מ-Bond
    def __init__(self, name):  # פונקציה שמתחילה אג"ח ממשלתי
        super().__init__(name)  # קוראת לפונקציה של מחלקת האג"ח הבסיסית 