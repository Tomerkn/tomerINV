# מסד נתונים בענן עם מודל 3NF

## עקרונות התכנון

### כללי נורמליזציה שיושמו:

**1NF (First Normal Form):**
- ✅ כל שדה מכיל ערך אטומי אחד
- ✅ אין ערכים מרובים באותו שדה
- ✅ כל רשומה ייחודית עם מפתח ראשי

**2NF (Second Normal Form):**
- ✅ עומד ב-1NF
- ✅ כל שדה שאינו חלק מהמפתח תלוי במלואו במפתח הראשי

**3NF (Third Normal Form):**
- ✅ עומד ב-2NF
- ✅ אין תלות טרנזיטיבית
- ✅ כל שדה תלוי רק במפתח הראשי ולא בשדות אחרים

## מבנה הטבלאות המנורמל

### טבלאות נתוני ייחוס (Reference Tables)

```sql
-- ענפים כלכליים
CREATE TABLE industries (
    industry_id SERIAL PRIMARY KEY,
    industry_name VARCHAR(100) UNIQUE NOT NULL,
    industry_code VARCHAR(10) UNIQUE NOT NULL,
    base_risk_score INTEGER NOT NULL,
    description TEXT
);

-- סוגי ניירות ערך
CREATE TABLE security_types (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    type_code VARCHAR(10) UNIQUE NOT NULL,
    risk_multiplier DECIMAL(3,1) NOT NULL,
    description TEXT
);

-- רמות שונות
CREATE TABLE variance_levels (
    variance_id SERIAL PRIMARY KEY,
    variance_name VARCHAR(20) UNIQUE NOT NULL,
    variance_code VARCHAR(5) UNIQUE NOT NULL,
    variance_multiplier DECIMAL(3,1) NOT NULL,
    description TEXT
);
```

### טבלאות ישויות עיקריות

```sql
-- משתמשים
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- ניירות ערך (עומד בכללי 3NF)
CREATE TABLE securities (
    security_id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    -- מפתחות זרים לטבלאות ייחוס מנורמלות
    industry_id INTEGER REFERENCES industries(industry_id),
    type_id INTEGER REFERENCES security_types(type_id),
    variance_id INTEGER REFERENCES variance_levels(variance_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- תיקי השקעות
CREATE TABLE portfolios (
    portfolio_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    portfolio_name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- החזקות בתיק (הפרדה בין נתוני נייר ערך לנתוני החזקה)
CREATE TABLE portfolio_holdings (
    holding_id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(portfolio_id),
    security_id INTEGER REFERENCES securities(security_id),
    quantity DECIMAL(15,4) NOT NULL DEFAULT 0,
    avg_purchase_price DECIMAL(15,4) NOT NULL DEFAULT 0,
    first_purchase_date DATE NOT NULL,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- היסטוריית מחירים (הפרדה בין נתוני נייר ערך לנתוני מחיר)
CREATE TABLE price_history (
    price_id SERIAL PRIMARY KEY,
    security_id INTEGER REFERENCES securities(security_id),
    price DECIMAL(15,4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'ILS',
    price_date TIMESTAMP NOT NULL,
    source VARCHAR(50)
);

-- עסקאות (רישום מלא של כל עסקה)
CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(portfolio_id),
    security_id INTEGER REFERENCES securities(security_id),
    transaction_type VARCHAR(10) NOT NULL, -- BUY, SELL, DIVIDEND
    quantity DECIMAL(15,4) NOT NULL,
    price_per_unit DECIMAL(15,4) NOT NULL,
    total_amount DECIMAL(15,4) NOT NULL,
    currency VARCHAR(3) DEFAULT 'ILS',
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);
```

## יתרונות המודל המנורמל

### 1. ביצועים משופרים
- **אינדקסים ממוקדים** על מפתחות זרים
- **חיפושים מהירים** בטבלאות ייחוס קטנות
- **JOIN operations** יעילים

### 2. שלמות נתונים
- **אילוצי מפתח זר** מבטיחים עקביות
- **אין כפילות נתונים** - כל מידע במקום אחד
- **עדכונים קלים** - שינוי במקום אחד משפיע בכל מקום

### 3. גמישות ותחזוקה
- **הוספת ענפים חדשים** ללא שינוי מבנה
- **הרחבה קלה** של מאפייני סיכון
- **מעקב מלא** אחר עסקאות והיסטוריה

## הגדרות ספקי ענן

### AWS RDS (PostgreSQL)
```python
AWS_CONFIG = {
    'provider': 'aws',
    'host': 'your-instance.region.rds.amazonaws.com',
    'port': 5432,
    'database': 'investment_3nf',
    'username': 'postgres',
    'password': 'your-password',
    'ssl_mode': 'require'
}
```

### Google Cloud SQL
```python
GCP_CONFIG = {
    'provider': 'gcp',
    'host': 'project:region:instance',
    'port': 5432,
    'database': 'investment_3nf',
    'username': 'postgres',
    'password': 'your-password'
}
```

### Azure Database for PostgreSQL
```python
AZURE_CONFIG = {
    'provider': 'azure',
    'host': 'your-server.postgres.database.azure.com',
    'port': 5432,
    'database': 'investment_3nf',
    'username': 'username@your-server',
    'password': 'your-password',
    'ssl_mode': 'require'
}
```

## דוגמה לחישוב סיכון מנורמל

במודל הקיים:
```
risk = industry_id * type_multiplier * variance_multiplier
```

במודל המנורמל:
```python
def calculate_risk_level(security):
    base_risk = security.industry.base_risk_score  # מהטבלה industries
    type_mult = security.security_type.risk_multiplier  # מהטבלה security_types  
    var_mult = security.variance_level.variance_multiplier  # מהטבלה variance_levels
    
    return base_risk * type_mult * var_mult
```

## יתרונות עבור המערכת הקיימת

### 1. תואמות לאחור
- **ממשק זהה** - הקונטרולר החדש תואם למערכת הקיימת
- **נתוני סיכון זהים** - אותה נוסחת חישוב
- **פונקציונליות מלאה** - כל הפיצ'רים נשמרים

### 2. שדרוגים עתידיים
- **מעקב עסקאות מפורט** - כל קנייה ומכירה נרשמת
- **היסטוריית מחירים** - מעקב אחר שינויי שווי
- **ניהול משתמשים מתקדם** - תמיכה במספר משתמשים
- **רפורטים מתקדמים** - ניתוח ביצועים לאורך זמן

### 3. מעבר חלק
```python
# המערכת הקיימת
from portfolio_controller import PortfolioController
controller = PortfolioController()

# המערכת החדשה
from cloud_3nf_db import CloudDatabaseManager, CloudPortfolioController
db = CloudDatabaseManager(LOCAL_CONFIG)
controller = CloudPortfolioController(db)

# אותו ממשק!
portfolio = controller.get_portfolio()
controller.buy_security("AAPL", 10, "טכנולוגיה", "גבוהה", "מניה רגילה")
```

## התקנה ושימוש

### 1. התקנת חבילות נדרשות
```bash
pip install SQLAlchemy psycopg2-binary python-dotenv
```

### 2. הגדרת משתני סביבה
```bash
export DB_TYPE=postgresql
export DB_HOST=your-cloud-host
export DB_NAME=investment_3nf
export DB_USER=postgres
export DB_PASSWORD=your-password
```

### 3. יצירת מסד הנתונים
```python
from cloud_3nf_db import CloudDatabaseManager, LOCAL_CONFIG

# יצירת מנהל מסד נתונים
db_manager = CloudDatabaseManager(LOCAL_CONFIG)

# יצירת סכמה ואכלוס נתוני ייחוס
db_manager.create_database_schema()

# בדיקת חיבור
if db_manager.test_connection():
    print("✅ מסד הנתונים מוכן לשימוש")
```

המודל החדש מספק בסיס איתן ומתקדם למערכת ניהול השקעות עם כל היתרונות של מסד נתונים מנורמל בענן! 🚀 