# MongoDB Atlas Setup Guide
מדריך התקנה והגדרה ל-MongoDB Atlas

## שלב 1: יצירת חשבון MongoDB Atlas

1. **הירשמות לחשבון חינמי:**
   - לך ל-[MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
   - לחץ על "Try Free" 
   - הירשם עם אימייל או Google

2. **יצירת Cluster חינמי:**
   - בחר "Create a deployment"
   - בחר "FREE" tier (M0 Sandbox)
   - בחר region קרוב (למשל Frankfurt/Ireland)
   - לחץ "Create Deployment"

## שלב 2: הגדרת אבטחה

### יצירת משתמש מסד נתונים:
```
Username: investment_user
Password: [צור סיסמה חזקה]
```

### הגדרת Network Access:
- לך ל-"Network Access" בתפריט השמאלי
- לחץ "Add IP Address"
- בחר "Allow access from anywhere" (0.0.0.0/0) לפיתוח
- **הערה**: בסביבת ייצור, הגדר רק IP ספציפיים

## שלב 3: השגת Connection String

1. לך ל-"Database" > "Connect"
2. בחר "Drivers"
3. בחר Python version 3.6+
4. העתק את ה-Connection String:
```
mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

## שלב 4: הגדרה בקוד

### הוספת משתני סביבה:
יצור קובץ `.env`:
```env
# MongoDB Atlas Configuration
MONGODB_USERNAME=investment_user
MONGODB_PASSWORD=your_strong_password
MONGODB_CLUSTER_URL=cluster0.xxxxx.mongodb.net
MONGODB_DATABASE=investment_portfolio
```

### התקנת dependencies:
```bash
pip install -r requirements_mongodb.txt
```

## שלב 5: שימוש בקוד

### דוגמה בסיסית:
```python
from mongodb_atlas_controller import MongoDBAtlasManager, MongoDBPortfolioController

# יצירת מנהל מסד נתונים
db_manager = MongoDBAtlasManager()

# יצירת controller לתיק השקעות
portfolio_controller = MongoDBPortfolioController(db_manager)

# שימוש בממשק הקיים
holdings = portfolio_controller.get_portfolio()
result = portfolio_controller.buy_security("AAPL", 10, "טכנולוגיה", "בינונית", "מניה")
```

### אינטגרציה עם Flask:
```python
# app.py
from mongodb_atlas_controller import MongoDBAtlasManager, MongoDBPortfolioController

# יצירת instance גלובלי
mongo_manager = MongoDBAtlasManager()
portfolio_controller = MongoDBPortfolioController(mongo_manager)

# השתמש במקום portfolio_controller הקיים
@app.route('/portfolio')
@login_required
def portfolio():
    holdings = portfolio_controller.get_portfolio()
    total_value = portfolio_controller.get_total_portfolio_value()
    return render_template('portfolio.html', holdings=holdings, total_value=total_value)
```

## שלב 6: מעבר מ-SQLite ל-MongoDB

### תמיכה דו-צדדית:
```python
# הוספה לקובץ הקיים
try:
    # נסה MongoDB Atlas
    from mongodb_atlas_controller import MongoDBAtlasManager, MongoDBPortfolioController
    mongo_manager = MongoDBAtlasManager()
    portfolio_controller = MongoDBPortfolioController(mongo_manager)
    print("✅ משתמש ב-MongoDB Atlas")
except Exception as e:
    # חזור ל-SQLite
    from portfolio_controller import PortfolioController
    portfolio_controller = PortfolioController()
    print(f"⚠️ חוזר ל-SQLite: {e}")
```

## יתרונות MongoDB Atlas:

### 🎯 **חינמי עד 512MB**
- מספיק למספר רב של השקעות
- אין הגבלת זמן

### 🚀 **ביצועים**
- חיפושים מהירים עם אינדקסים
- Aggregation pipelines חזקים

### 🔒 **אבטחה**
- הצפנה אוטומטית
- Network isolation
- גיבויים אוטומטיים

### 📊 **מבנה נתונים**
- Collections נפרדים לנורמליזציה
- קשרים בין documents
- שמירת היסטוריית מחירים

## Collections Structure:

```javascript
// industries
{
  "_id": ObjectId,
  "industry_code": "TECH",
  "industry_name": "טכנולוגיה", 
  "base_risk_score": 3,
  "description": "חברות טכנולוגיה"
}

// securities  
{
  "_id": ObjectId,
  "name": "Apple Inc",
  "symbol": "AAPL",
  "industry_id": ObjectId("..."),
  "type_id": ObjectId("..."),
  "variance_id": ObjectId("..."),
  "current_price": 150.0,
  "created_at": ISODate,
  "updated_at": ISODate
}

// holdings
{
  "_id": ObjectId,
  "user_id": 1,
  "security_id": ObjectId("..."),
  "quantity": 10.0,
  "avg_purchase_price": 145.0,
  "first_purchase_date": ISODate,
  "last_updated": ISODate  
}
```

## פתרון בעיות נפוצות:

### שגיאת חיבור:
```
ServerSelectionTimeoutError
```
**פתרון**: בדוק את ה-IP whitelist ופרטי החיבור

### שגיאת אימות:
```
Authentication failed
```
**פתרון**: בדוק username/password ב-Database Access

### חיבור איטי:
**פתרון**: בחר region קרוב יותר בפעם הבאה

---

**מוכן להתחיל! 🚀**
הקוד תואם למערכת הקיימת ויעבד עם כל הפיצ'רים הנוכחיים. 