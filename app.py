from flask import (
    Flask, render_template, redirect, url_for, flash, Response, request,
    jsonify
)
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, logout_user,
    current_user
)
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, FloatField,
    SelectField
)
from wtforms.validators import DataRequired
from functools import wraps
import logging
import os
import sys
import traceback
import time
import io
import requests
import matplotlib
matplotlib.use('Agg')  # השתמש ב-backend שלא דורש GUI
import matplotlib.pyplot as plt
import random

print("=== התחלת ייבוא ספריות ===")
print("=== בדיקת משתני סביבה ===")
DATABASE_URL = os.environ.get('DATABASE_URL')
PORT = int(os.environ.get('PORT', 4000))
OLLAMA_URL = os.environ.get('OLLAMA_URL')
print(f"DATABASE_URL: {DATABASE_URL}")
print(f"PORT: {PORT}")
print(f"OLLAMA_URL: {OLLAMA_URL}")
print("=== סיום בדיקת משתני סביבה ===")

# מביאים הקלסים שיצרנו בקבצים אחרים
print("=== התחלת ייבוא dbmodel ===")
try:
    from dbmodel import PortfolioModel, Broker
    print("=== סיום ייבוא dbmodel ===")
except Exception as e:
    print(f"שגיאה בייבוא dbmodel: {str(e)}")
    sys.exit(1)

print("=== התחלת ייבוא ollamamodel ===")
try:
    from ollamamodel import AI_Agent
    print("=== סיום טעינת ollamamodel.py ===")
    print("=== סיום ייבוא ollamamodel ===")
except ImportError as e:
    print(f"שגיאה בייבוא ollamamodel: {str(e)}")
    print("=== יוצר AI_Agent מקומי ===")
    # יצירת AI_Agent פשוט במקרה של בעיה בייבוא
    class AI_Agent:
        def __init__(self):
            self.model = "llama3.1:8b"
            self.ollama_available = False
            print("AI_Agent פשוט נוצר")
        
        def get_advice(self):
            return """
ייעוץ השקעות בסיסי:

עקרונות חשובים:
1. פיזור השקעות - אל תשים הכל על מניה אחת
2. השקעה לטווח ארוך - סבלנות היא מפתח
3. מחקר לפני השקעה - הכר את החברות
4. ניהול סיכונים - השקע רק מה שאתה יכול להפסיד

סוגי השקעות:
• מניות - פוטנציאל גבוה, סיכון גבוה
• אגרות חוב - יציבות יותר, תשואה נמוכה יותר
• קרנות נאמנות - פיזור אוטומטי

זכור: השקעות כרוכות בסיכון!
            """
    print("=== סיום ייבוא ollamamodel ===")
except Exception as e:
    print(f"שגיאה כללית בייבוא ollamamodel: {str(e)}")
    # יצירת AI_Agent פשוט במקרה של בעיה
    class AI_Agent:
        def __init__(self):
            self.model = "llama3.1:8b"
            self.ollama_available = False
        
        def get_advice(self):
            return "ייעוץ השקעות בסיסי זמין"
    print("=== סיום ייבוא ollamamodel ===")

print("=== התחלת טעינת האפליקציה ===")

# הוספת לוגים מפורטים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# יוצרים את האתר - זה הדבר הכי חשוב
app = Flask(__name__)  # זה יוצר את האתר שלנו
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey')  # מפתח חשאי לאבטחה
login_manager = LoginManager(app)  # דבר שמנהל כניסה למערכת
login_manager.init_app(app)  # מחברים אותו לאתר
login_manager.login_view = 'login'  # איפה לשלוח אנשים שלא התחברו
login_manager.login_message = 'אנא התחבר כדי לגשת לדף זה'  # הודעה בעברית
login_manager.login_message_category = 'warning'  # סוג ההודעה
print("=== Flask app נוצר בהצלחה ===")
print("=== SECRET_KEY מוגדר ===")
print("=== LoginManager מוגדר ===")

# קבוע המרה מדולר לשקל
CONVERSION_RATE = 3.5
print(f"=== קבוע המרה מוגדר: {CONVERSION_RATE} ===")

# פונקציית עזר להמיר מדולר לשקל
def usd_to_ils(usd_price):
    """מחזיר מחיר בשקלים מתוך מחיר בדולרים"""
    return usd_price * CONVERSION_RATE

# הקלאס של המשתמשים באתר
class User(UserMixin):  # קלאס שמייצג משתמש
    def __init__(self, id, username, password_hash, role='user'):  # יוצר משתמש חדש
        self.id = id  # מספר של המשתמש
        self.username = username  # שם משתמש (admin או user)
        self.password_hash = password_hash  # הסיסמה מוצפנת
        self.role = role  # סוג משתמש: 'admin' (מנהל) או 'user' (מפעיל)
    
    def check_password(self, password):  # בודק אם הסיסמה נכונה
        return self.password_hash == password  # השוואה פשוטה של הסיסמה
    
    def is_admin(self):  # בודק אם המשתמש הוא מנהל
        return self.role == 'admin'  # מחזיר אמת אם הוא מנהל

# רשימת המשתמשים המורשים במערכת עם סיסמאות פשוטות
USERS = {
    # מנהל עם הרשאות מלאות - יכול לבצע כל פעולה
    'admin': User('1', 'admin', 'admin', 'admin'),
    # מפעיל עם הרשאות צפייה בלבד - לא יכול לערוך
    'user': User('2', 'user', 'user', 'user')
}

@login_manager.user_loader  # פונקציה שמוצאת משתמש לפי מספר זיהוי
def load_user(user_id):  # מקבלת מספר זיהוי של משתמש
    try:
        # בדיקה אם portfolio_model קיים
        if 'portfolio_model' in globals():
            user_data = portfolio_model.get_user_by_id(int(user_id))
            if user_data:
                # יוצר אובייקט User מהנתונים במסד
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    role=user_data.get('role', 'user')
                )
        return None
    except Exception as e:
        logger.error(f"שגיאה בטעינת משתמש: {str(e)}")
        return None

# דקורטור (פונקציה עוטפת) לבדיקת הרשאות מנהל
def admin_required(f):  # מקבלת פונקציה ועוטפת אותה בבדיקת הרשאות
    @wraps(f)  # שומר על המטא-דאטה של הפונקציה המקורית
    def decorated_function(*args, **kwargs):  # הפונקציה החדשה שבודקת הרשאות
        # בודק אם המשתמש מחובר ואם יש לו הרשאות מנהל
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('גישה נדחתה - נדרשות הרשאות מנהל', 'danger')  # מציג הודעת שגיאה
            return redirect(url_for('index'))  # מפנה לדף הבית
        return f(*args, **kwargs)  # אם יש הרשאות, מבצע את הפונקציה המקורית
    return decorated_function  # מחזיר את הפונקציה החדשה

# יצירת מופעים של המחלקות שנצטרך לאורך כל האפליקציה
print("=== יצירת מופעי המחלקות ===")
print("=== התחלת יצירת PortfolioModel ===")
try:
    portfolio_model = PortfolioModel()  # יוצר את מסד הנתונים
    print("=== סיום יצירת PortfolioModel ===")
except Exception as e:
    print(f"שגיאה ביצירת PortfolioModel: {str(e)}")
    logger.error(f"שגיאה ביצירת PortfolioModel: {str(e)}")
    traceback.print_exc()
    sys.exit(1)

print("=== התחלת יצירת AI_Agent ===")
try:
    ai_agent = AI_Agent()  # יוצר את הסוכן הבינה המלאכותית
    print("=== AI Agent נוצר בהצלחה ===")
except Exception as e:
    print(f"שגיאה ביצירת AI_Agent: {str(e)}")
    logger.error(f"שגיאה ביצירת AI_Agent: {str(e)}")
    ai_agent = None

print("=== סיום יצירת מופעי המחלקות ===")

# הגדרת כל הטפסים שהמשתמשים יוכלו למלא באתר
class LoginForm(FlaskForm):  # טופס כניסה למערכת
    username = StringField('שם משתמש', validators=[DataRequired()])  # שדה שם משתמש (חובה)
    password = PasswordField('סיסמה', validators=[DataRequired()])  # שדה סיסמה מוסתרת (חובה)
    submit = SubmitField('התחבר')  # כפתור כניסה

class SecurityForm(FlaskForm):  # טופס להוספת נייר ערך חדש לתיק
    # רשימת מניות מה-API (S&P 500)
    sp500_stocks = [
        ("AAPL", "Apple Inc"), ("MSFT", "Microsoft Corp"), ("GOOG", "Alphabet Inc"), ("AMZN", "Amazon.com Inc"),
        ("META", "Meta Platforms Inc"), ("NVDA", "NVIDIA Corp"), ("ADBE", "Adobe Inc"), ("CSCO", "Cisco Systems"),
        ("ORCL", "Oracle Corp"), ("QCOM", "Qualcomm Inc"), ("INTC", "Intel Corp"), ("JPM", "JPMorgan Chase"),
        ("V", "Visa Inc"), ("MA", "Mastercard Inc"), ("BAC", "Bank of America"), ("WFC", "Wells Fargo"),
        ("MS", "Morgan Stanley"), ("SCHW", "Charles Schwab"), ("SPGI", "S&P Global"), ("BLK", "BlackRock Inc"),
        ("UNH", "UnitedHealth Group"), ("LLY", "Eli Lilly"), ("ABBV", "AbbVie Inc"), ("MRK", "Merck & Co"),
        ("ABT", "Abbott Labs"), ("TMO", "Thermo Fisher"), ("AMGN", "Amgen Inc"), ("MDT", "Medtronic plc"),
        ("WMT", "Walmart Inc"), ("PG", "Procter & Gamble"), ("HD", "Home Depot"), ("COST", "Costco Wholesale"),
        ("PEP", "PepsiCo Inc"), ("KO", "Coca-Cola Co"), ("MCD", "McDonald's Corp"), ("NKE", "Nike Inc"),
        ("LOW", "Lowe's Cos"), ("PM", "Philip Morris"), ("XOM", "Exxon Mobil"), ("CVX", "Chevron Corp"),
        ("NEE", "NextEra Energy"), ("LIN", "Linde plc"), ("DHR", "Danaher Corp"), ("HON", "Honeywell Intl"),
        ("RTX", "RTX Corp"), ("TSLA", "Tesla Inc"), ("UNP", "Union Pacific"), ("UPS", "United Parcel Service"),
        ("PLD", "Prologis Inc"), ("AMT", "American Tower"), ("CCI", "Crown Castle")
    ]
    stock_dropdown = SelectField('בחר מניה מה-API', choices=[('', '--- בחר מניה ---')] + sp500_stocks, default='')
    name = StringField('שם נייר הערך', validators=[DataRequired()])  # שדה לשם המניה (חובה)
    amount = FloatField('כמות', validators=[DataRequired()])  # שדה לכמות שרוצים לקנות (חובה)
    industry = SelectField('ענף', choices=[
        ('טכנולוגיה', 'טכנולוגיה'), ('תחבורה', 'תחבורה'), ('אנרגיה', 'אנרגיה'),
        ('בריאות', 'בריאות'), ('תעשייה', 'תעשייה'), ('פיננסים', 'פיננסים'),
        ('נדלן', 'נדלן'), ('צריכה פרטית', 'צריכה פרטית')
    ])
    variance = SelectField('רמת שונות', choices=[('נמוך', 'נמוך'), ('גבוה', 'גבוה')])
    security_type = SelectField('סוג נייר הערך', choices=[
        ('מניה רגילה', 'מניה רגילה'), ('אגח ממשלתית', 'אגח ממשלתית'), 
        ('אגח קונצרנית', 'אגח קונצרנית')
    ])
    submit = SubmitField('הוסף')  # כפתור שליחה

@app.route('/login', methods=['GET', 'POST'])  # נתיב לדף כניסה, מקבל בקשות GET (להראות דף) ו-POST (לשלוח טופס)
def login():  # פונקציה שמטפלת בכניסה למערכת
    try:
        print("=== התחלת פונקציית login ===")
        print(f"שיטת הבקשה: {request.method}")
        
        if current_user.is_authenticated:  # בודק אם המשתמש כבר מחובר
            print("משתמש כבר מחובר, מפנה לדף הבית")
            return redirect(url_for('index'))  # אם כן, מפנה אותו לדף הבית
        
        # וודא שמסד הנתונים נוצר
        print("יוצר טבלאות במסד הנתונים...")
        portfolio_model.create_tables()
        print("טבלאות נוצרו בהצלחה")
        
        # יצירת משתמשי ברירת מחדל
        print("יוצר משתמשי ברירת מחדל...")
        portfolio_model.create_default_users()
        print("משתמשי ברירת מחדל נוצרו בהצלחה")
        
        form = LoginForm()  # יוצר טופס כניסה חדש
        print(f"טופס נוצר, validate_on_submit: {form.validate_on_submit()}")
        
        if form.validate_on_submit():  # בודק אם הטופס נשלח ועבר אימות
            username = form.username.data
            password = form.password.data
            print(f"ניסיון התחברות עם שם משתמש: {username}")
            
            # מחפש את המשתמש במסד הנתונים
            user_data = portfolio_model.get_user_by_username(username)
            print(f"משתמש נמצא במסד: {user_data is not None}")
            
            if user_data:
                # יוצר אובייקט User מהנתונים במסד
                user = User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    role=user_data.get('role', 'user')
                )
                
                if user.check_password(password):  # בודק אם הסיסמה נכונה
                    print("סיסמה נכונה, מתחבר...")
                    login_user(user)  # מחבר את המשתמש למערכת
                    print("התחברות הצליחה")
                    return redirect(url_for('index'))  # מפנה אותו לדף הבית
                else:
                    print("סיסמה שגויה")
                    flash('שם משתמש או סיסמה שגויים', 'danger')
            else:
                print("משתמש לא נמצא")
                flash('שם משתמש או סיסמה שגויים', 'danger')
        
        print("מציג דף כניסה")
        return render_template('login.html', form=form)  # מציג את דף הכניסה עם הטופס
    except Exception as e:
        # לוג השגיאה לבדיקה
        print(f"שגיאה בדף הכניסה: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('שגיאה פנימית בשרת. אנא נסה שוב מאוחר יותר.', 'danger')
        return render_template('login.html', form=LoginForm())

@app.route('/logout')  # נתיב ליציאה מהמערכת
@login_required  # דקורטור שדורש שהמשתמש יהיה מחובר
def logout():  # פונקציה שמטפלת ביציאה מהמערכת
    logout_user()  # מנתק את המשתמש מהמערכת
    return redirect(url_for('login'))  # מפנה אותו חזרה לדף הכניסה

@app.route('/clear-session')  # נתיב לניקוי session
def clear_session():
    """מנקה את ה-session ומפנה להתחברות"""
    logout_user()
    return redirect(url_for('login'))

@app.route('/')  # נתיב לדף הבית הראשי של האתר
def index():  # פונקציה שמציגה את דף הבית
    try:
        print("=== התחלת נתיב index ===")
        
        # בדיקה בטוחה יותר של סטטוס המשתמש
        try:
            is_authenticated = current_user.is_authenticated
            print(f"משתמש מחובר: {is_authenticated}")
        except Exception as e:
            print(f"שגיאה בבדיקת סטטוס משתמש: {e}")
            is_authenticated = False
        
        if is_authenticated:
            print("מציג דף בית למשתמש מחובר")
            # קבלת נתוני תיק ההשקעות להצגה בדף הבית
            portfolio_data = portfolio_model.get_all_securities()
            total_assets = sum(security['price'] * security['amount'] for security in portfolio_data)
            asset_count = len(portfolio_data)
            
            return render_template('index.html', 
                                 portfolio=portfolio_data, 
                                 total_assets=total_assets, 
                                 asset_count=asset_count)
        else:
            print("מפנה לדף התחברות")
            return redirect(url_for('login'))
            
    except Exception as e:
        print(f"שגיאה בנתיב הראשי: {str(e)}")
        import traceback
        traceback.print_exc()
        # במקום להחזיר שגיאה, ננסה להפנות לדף התחברות
        try:
            return redirect(url_for('login'))
        except:
            return "שגיאה בטעינת הדף", 500

@app.route('/portfolio')  # נתיב לדף התיק ההשקעות המלא
@login_required  # דקורטור שדורש שהמשתמש יהיה מחובר
def portfolio():  # פונקציה שמציגה את תיק ההשקעות המלא
    try:
        portfolio_data = portfolio_model.get_all_securities()  # מקבל את כל ניירות הערך
        # חישוב הערך הכולל מכפל מחיר וכמות
        total_value = sum(security['price'] * security['amount'] for security in portfolio_data)
        
        # חישוב רמת סיכון לכל נייר ערך
        risk_levels = {
            'טכנולוגיה': 6,
            'תחבורה': 5,
            'אנרגיה': 4,
            'בריאות': 4,
            'תעשייה': 3,
            'פיננסים': 3,
            'נדלן': 2,
            'צריכה פרטית': 1,
            'Technology': 6,  # תמיכה באנגלית
            'Healthcare': 4,
            'Financial': 3,
            'Consumer': 1
        }
        
        # הוספת total_value ורמת סיכון לכל נייר ערך להצגה בתבנית
        for security in portfolio_data:
            security['total_value'] = security['price'] * security['amount']
            
            # הוספת רמת סיכון לפי ענף (עם ערך ברירת מחדל)
            industry = security.get('industry', 'לא מוגדר')
            security['risk_level'] = risk_levels.get(industry, 3)  # ברירת מחדל: 3
            
            # אם אין ענף, נוסיף ערך ברירת מחדל
            if not industry or industry == 'לא מוגדר':
                security['industry'] = 'לא מוגדר'
        
        return render_template('portfolio.html', portfolio=portfolio_data, total_value=total_value)  # מציג את הדף
    except Exception as e:
        flash(f'שגיאה בטעינת תיק ההשקעות: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/portfolio/add', methods=['GET', 'POST'])  # נתיב להוספת נייר ערך חדש
@login_required  # דקורטור שדורש שהמשתמש יהיה מחובר
@admin_required  # דקורטור שדורש הרשאות מנהל
def add_security():  # פונקציה להוספת נייר ערך חדש לתיק
    form = SecurityForm()  # יוצר טופס הוספת נייר ערך
    # אם נבחרה מניה מה-dropdown, נעדכן את שדה השם אוטומטית
    if form.stock_dropdown.data and form.stock_dropdown.data != '':
        # מצא את שם המניה לפי הסימול
        symbol_to_name = dict(SecurityForm.sp500_stocks)
        form.name.data = symbol_to_name.get(form.stock_dropdown.data, form.stock_dropdown.data)
    if form.validate_on_submit():  # בודק אם הטופס נשלח ועבר אימות
        security = {
            'name': form.name.data,  # שם נייר הערך
            'amount': form.amount.data,  # כמות
            'price': 0  # מחיר התחלתי (יתעדכן אחר כך)
        }
        try:
            result = portfolio_model.add_security(security['name'], security['amount'], security['price'], form.industry.data, form.variance.data, form.security_type.data)  # מוסיף את נייר הערך לתיק
            if result:
                flash('נייר הערך נוסף בהצלחה!', 'success')  # מציג הודעת הצלחה
                return redirect(url_for('portfolio'))  # מפנה לדף התיק
            else:
                flash('שגיאה בהוספת נייר הערך', 'danger')  # מציג הודעת שגיאה
        except Exception as e:
            flash(f'שגיאה: {str(e)}', 'danger')  # מציג הודעת שגיאה מפורטת
    return render_template('add_security.html', form=form)  # מציג את דף הוספת נייר ערך

@app.route('/portfolio/delete/<security_name>', methods=['POST'])
@login_required
@admin_required
def delete_security(security_name):
    try:
        portfolio_model.remove_security(security_name)
        flash('נייר הערך נמחק בהצלחה!', 'success')
    except Exception as e:
        flash(f'שגיאה במחיקת נייר הערך: {str(e)}', 'danger')
    return redirect(url_for('portfolio'))

@app.route('/update-price/<symbol>')
@login_required
@admin_required
def update_single_price(symbol):
    try:
        # קבלת המחיר הנוכחי מהמסד נתונים
        portfolio_data = portfolio_model.get_all_securities()
        current_item = None
        for item in portfolio_data:
            if item['name'] == symbol:
                current_item = item
                break
        
        if not current_item:
            flash(f'❌ לא נמצא נייר ערך בשם {symbol}', 'danger')
            return redirect(url_for('portfolio'))
        
        current_price = current_item['price']
        
        # מיפוי סמלים למניות
        symbol_mapping = {
            'Apple Inc': 'AAPL', 'אפל': 'AAPL',
            'Microsoft Corp': 'MSFT', 'מיקרוסופט': 'MSFT',
            'Alphabet Inc': 'GOOG', 'גוגל': 'GOOG',
            'Amazon.com Inc': 'AMZN', 'אמזון': 'AMZN',
            'Meta Platforms Inc': 'META', 'מטא': 'META',
            'NVIDIA Corp': 'NVDA', 'נווידיה': 'NVDA',
            'Tesla Inc': 'TSLA', 'טסלה': 'TSLA',
            'JPMorgan Chase': 'JPM',
            'Visa Inc': 'V', 'ויזה': 'V',
            'Walmart Inc': 'WMT', 'וולמארט': 'WMT'
        }
        
        api_symbol = symbol_mapping.get(symbol)
        
        if not api_symbol:
            flash(f'⚠️ לא נמצא סמל API עבור {symbol} - לא ניתן לעדכן', 'warning')
            return redirect(url_for('portfolio'))
        
        flash(f'🔍 מקבל מחיר עדכני עבור {symbol} ({api_symbol})...', 'info')
        
        # קבלת מחיר חדש מה-API
        new_price = Broker.update_price(api_symbol)
        
        if new_price and new_price > 0:
            # בדיקה אם המחיר השתנה משמעותית
            price_change = abs(new_price - current_price) / current_price * 100
            
            if price_change > 1:  # אם השינוי גדול מ-1%
                # עדכון המחיר במסד הנתונים
                portfolio_model.update_security_price(symbol, new_price)
                
                change_direction = "📈" if new_price > current_price else "📉"
                flash(f'{change_direction} {symbol}: ₪{current_price:.2f} → ₪{new_price:.2f} ({price_change:+.1f}%)', 'success')
            else:
                flash(f'✅ {symbol}: מחיר לא השתנה משמעותית (₪{current_price:.2f})', 'info')
        else:
            flash(f'❌ לא הצלחתי לקבל מחיר חדש עבור {symbol}', 'error')
            
    except Exception as e:
        flash(f'❌ שגיאה בעדכון מחיר {symbol}: {str(e)}', 'error')
    return redirect(url_for('portfolio'))

@app.route('/update-all-prices')
@app.route('/graph')
@login_required
def graph():
    try:
        portfolio_data = portfolio_model.get_all_securities()
        
        # חישוב הערך הכולל ואחוזים לכל נייר ערך
        total_value = 0
        for security in portfolio_data:
            security['value'] = security['price'] * security['amount']
            total_value += security['value']
        
        # חישוב אחוזים
        for security in portfolio_data:
            if total_value > 0:
                security['percentage'] = (security['value'] / total_value) * 100
            else:
                security['percentage'] = 0
        
        return render_template('graph.html', portfolio=portfolio_data, total_value=total_value)
    except Exception as e:
        flash(f'שגיאה בטעינת גרפים: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/pie-chart.png')
@login_required
def generate_pie_chart():
    try:
        portfolio_data = portfolio_model.get_all_securities()
        
        # הגדרת פונט וכיוון לעברית
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['text.usetex'] = False
        
        if not portfolio_data:
            # אם אין נתונים, יצור גרף ריק
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.text(0.5, 0.5, 'אין נתונים להצגה', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, fontfamily='DejaVu Sans')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        else:
            # יצירת גרף עוגה
            labels = [item['name'] for item in portfolio_data]
            # חישוב הערך הכולל מכפל מחיר וכמות
            sizes = [item['price'] * item['amount'] for item in portfolio_data]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # יצירת גרף עוגה עם הגדרות עברית מתאימות
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                            startangle=90, textprops={'fontsize': 10, 'fontfamily': 'DejaVu Sans'})
            ax.axis('equal')
            
            # הגדרת עיצוב טקסט עם תיקון כיוון עברית
            for text in texts:
                text.set_fontfamily('DejaVu Sans')
                text.set_fontsize(10)
                text.set_horizontalalignment('center')
                # תיקון כיוון הטקסט לעברית
                current_text = text.get_text()
                if current_text and any('\u0590' <= char <= '\u05FF' 
                                       for char in current_text):
                    # אם יש תווים עבריים, הפוך את הכיוון
                    text.set_text(current_text[::-1])
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontfamily('DejaVu Sans')
                autotext.set_fontsize(9)
        
        # שמירת הגרף לתמונה
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=300, 
                   facecolor='white', edgecolor='none')
        img.seek(0)
        plt.close()
        
        return Response(img.getvalue(), mimetype='image/png')
    except Exception as e:
        # במקרה של שגיאה, החזר תמונה ריקה
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f'שגיאה: {str(e)}', ha='center', va='center', 
               transform=ax.transAxes, fontsize=12, fontfamily='DejaVu Sans')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', facecolor='white')
        img.seek(0)
        plt.close()
        
        return Response(img.getvalue(), mimetype='image/png')

# טיפול שגיאות כללי
@app.errorhandler(500)
def internal_error(error):
    logger.error(f"שגיאה פנימית בשרת: {error}")
    logger.error(f"פרטי השגיאה: {str(error)}")
    return render_template('error.html', error="שגיאה פנימית בשרת"), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"דף לא נמצא: {error}")
    return render_template('error.html', error="הדף שחיפשת לא נמצא"), 404

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"שגיאה לא צפויה: {str(e)}")
    traceback.print_exc()
    return render_template('error.html', error="שגיאה לא צפויה"), 500

@app.route('/test')
def test():
    """נתיב בדיקה פשוט"""
    return "האפליקציה עובדת!"

@app.route('/dbtest')
def dbtest():
    """בדיקת מסד נתונים - מראה אילו טבלאות קיימות"""
    print("=== התחלת בדיקת מסד נתונים ===")
    try:
        print("מנסה להתחבר למסד הנתונים...")
        conn = portfolio_model.get_connection()
        print("חיבור למסד הנתונים הצליח!")
        
        cursor = conn.cursor()
        print("cursor נוצר בהצלחה")
        
        # בודק אילו טבלאות קיימות
        if portfolio_model.use_postgres:
            print("משתמש ב-PostgreSQL")
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        else:
            print("משתמש ב-SQLite")
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        
        tables = cursor.fetchall()
        print(f"נמצאו {len(tables)} טבלאות")
        
        # בודק תוכן של טבלת securities אם היא קיימת
        securities_count = 0
        if any('securities' in str(table).lower() for table in tables):
            print("טבלת securities קיימת, בודק תוכן...")
            cursor.execute("SELECT COUNT(*) FROM securities")
            securities_count = cursor.fetchone()[0]
            print(f"מספר ניירות ערך בטבלה: {securities_count}")
        
        conn.close()
        print("חיבור נסגר בהצלחה")
        
        result = f"""
        <h2>בדיקת מסד נתונים - הצליחה!</h2>
        <p><strong>סוג מסד:</strong> {'PostgreSQL' if portfolio_model.use_postgres else 'SQLite'}</p>
        <p><strong>כתובת:</strong> {portfolio_model.db_url}</p>
        <p><strong>מספר טבלאות:</strong> {len(tables)}</p>
        <p><strong>מספר ניירות ערך:</strong> {securities_count}</p>
        <h3>טבלאות קיימות:</h3>
        <ul>
        {''.join([f'<li>{table[0] if isinstance(table, tuple) else table}</li>' for table in tables])}
        </ul>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """
        
        print("=== סיום בדיקת מסד נתונים ===")
        return result
        
    except Exception as e:
        print(f"שגיאה בבדיקת מסד נתונים: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"""
        <h2>שגיאה בבדיקת מסד נתונים</h2>
        <p><strong>סוג מסד:</strong> {'PostgreSQL' if portfolio_model.use_postgres else 'SQLite'}</p>
        <p><strong>כתובת:</strong> {portfolio_model.db_url}</p>
        <p><strong>שגיאה:</strong> {str(e)}</p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

def require_database_url():
    import os
    if not os.environ.get('DATABASE_URL') and (os.environ.get('RAILWAY_STATIC_URL') or os.environ.get('RENDER') or os.environ.get('FLY_APP_NAME')):
        print("אזהרה: DATABASE_URL לא מוגדר בסביבת ענן")
        return False
    return True

@app.route('/create-tables')
def create_tables():
    """יוצר טבלאות אם הן לא קיימות"""
    print("=== התחלת יצירת טבלאות ===")
    try:
        portfolio_model.create_tables()
        
        # יצירת משתמשי ברירת מחדל
        print("יוצר משתמשי ברירת מחדל...")
        portfolio_model.create_default_users()
        print("משתמשי ברירת מחדל נוצרו בהצלחה")
        
        result = """
        <h2>יצירת טבלאות - הצליחה!</h2>
        <p>הטבלאות נוצרו בהצלחה במסד הנתונים.</p>
        <p>משתמשי ברירת מחדל נוצרו:</p>
        <ul>
            <li><strong>admin</strong> - סיסמה: admin (מנהל)</li>
            <li><strong>user</strong> - סיסמה: user (משתמש רגיל)</li>
        </ul>
        
        <h3>טבלאות שנוצרו:</h3>
        <ul>
            <li><strong>securities</strong> - ניירות ערך</li>
            <li><strong>investments</strong> - השקעות</li>
            <li><strong>users</strong> - משתמשים</li>
        </ul>
        
        <h3>השלב הבא:</h3>
        <p><a href="/add-sample-data">הוסף נתונים לדוגמה</a></p>
        <p><a href="/db-status">בדוק סטטוס מסד נתונים</a></p>
        
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """
        
        print("=== סיום יצירת טבלאות ===")
        return result
        
    except Exception as e:
        print(f"שגיאה ביצירת טבלאות: {str(e)}")
        return f"""
        <h2>שגיאה ביצירת טבלאות</h2>
        <p>שגיאה: {str(e)}</p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

@app.route('/add-sample-data')
def add_sample_data():
    """מוסיף נתונים לדוגמה למסד הנתונים"""
    print("=== התחלת הוספת נתונים לדוגמה ===")
    try:
        # הוספת ניירות ערך לדוגמה
        sample_securities = [
            ('AAPL', 'Apple Inc.', 'Technology', 150.25, 2.5, 50000000, 2500000000000, 25.5, 0.6),
            ('MSFT', 'Microsoft Corporation', 'Technology', 320.75, 1.8, 30000000, 2400000000000, 30.2, 0.8),
            ('GOOGL', 'Alphabet Inc.', 'Technology', 2800.50, 3.2, 20000000, 1800000000000, 28.1, 0.0),
            ('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary', 3300.25, -1.2, 25000000, 1600000000000, 45.3, 0.0),
            ('TSLA', 'Tesla Inc.', 'Automotive', 850.75, 5.8, 40000000, 800000000000, 120.5, 0.0),
            ('NVDA', 'NVIDIA Corporation', 'Technology', 450.30, 4.1, 35000000, 1100000000000, 35.2, 0.2),
            ('META', 'Meta Platforms Inc.', 'Technology', 280.90, 2.7, 28000000, 750000000000, 22.8, 0.0),
            ('JNJ', 'Johnson & Johnson', 'Healthcare', 165.40, 1.2, 15000000, 400000000000, 18.3, 2.8),
            ('V', 'Visa Inc.', 'Financial', 240.60, 2.1, 20000000, 500000000000, 32.1, 0.7),
            ('JPM', 'JPMorgan Chase & Co.', 'Financial', 140.80, 1.5, 25000000, 420000000000, 12.8, 2.9)
        ]
        
        conn = portfolio_model.get_connection()
        cursor = conn.cursor()
        
        for security in sample_securities:
            if portfolio_model.use_postgres:
                cursor.execute("""
                    INSERT INTO securities (symbol, name, sector, price, change_percent, volume, market_cap, pe_ratio, dividend_yield)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (symbol) DO UPDATE SET
                        name = EXCLUDED.name,
                        sector = EXCLUDED.sector,
                        price = EXCLUDED.price,
                        change_percent = EXCLUDED.change_percent,
                        volume = EXCLUDED.volume,
                        market_cap = EXCLUDED.market_cap,
                        pe_ratio = EXCLUDED.pe_ratio,
                        dividend_yield = EXCLUDED.dividend_yield
                """, security)
            else:
                cursor.execute("""
                    INSERT OR REPLACE INTO securities (symbol, name, sector, price, change_percent, volume, market_cap, pe_ratio, dividend_yield)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, security)
        
        conn.commit()
        conn.close()
        
        result = f"""
        <h2>הוספת נתונים לדוגמה - הצליחה!</h2>
        <p>נוספו {len(sample_securities)} ניירות ערך לדוגמה למסד הנתונים.</p>
        
        <h3>ניירות ערך שנוספו:</h3>
        <ul>
        """
        
        for symbol, name, sector, price, change, volume, market_cap, pe, dividend in sample_securities:
            result += f"<li><strong>{symbol}</strong> - {name} ({sector}) - ${price}</li>"
        
        result += """
        </ul>
        
        <h3>השלב הבא:</h3>
        <p><a href="/db-status">בדוק סטטוס מסד נתונים</a></p>
        <p><a href="/portfolio">צפייה בתיק השקעות</a></p>
        
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """
        
        print("=== סיום הוספת נתונים לדוגמה ===")
        return result
        
    except Exception as e:
        print(f"שגיאה בהוספת נתונים לדוגמה: {str(e)}")
        return f"""
        <h2>שגיאה בהוספת נתונים לדוגמה</h2>
        <p>שגיאה: {str(e)}</p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

@app.route('/db-admin')
def db_admin():
    """נתיב ראשי לניהול מסד הנתונים"""
    print("=== התחלת פונקציית db_admin ===")
    
    html = """
    <h1>ניהול מסד נתונים</h1>
    <p>ברוכים הבאים לניהול מסד הנתונים של האפליקציה!</p>
    
    <h2>פעולות זמינות:</h2>
    <ul>
        <li><a href="/test">בדיקת האפליקציה</a> - בודק שהאפליקציה עובדת</li>
        <li><a href="/connection-test">בדיקת חיבור מפורטת</a> - בודק חיבור למסד הנתונים</li>
        <li><a href="/dbtest">בדיקת מסד נתונים</a> - מראה אילו טבלאות קיימות</li>
        <li><a href="/db-status">סטטוס מסד נתונים</a> - מראה תוכן המסד</li>
        <li><a href="/create-tables">יצירת טבלאות</a> - יוצר טבלאות אם הן לא קיימות</li>
        <li><a href="/add-sample-data">הוספת נתונים לדוגמה</a> - מוסיף מניות לדוגמה</li>
        <li><a href="/inject-cloud-data">הזרקת נתונים לענן</a> - מזריק נתונים למסד PostgreSQL בענן</li>
        <li><a href="/ollama-test">בדיקת Ollama</a> - בודק חיבור לבינה מלאכותית</li>
        <li><a href="/env-test">בדיקת משתני סביבה</a> - מראה משתני סביבה</li>
    </ul>
    
    <h2>מידע על המסד:</h2>
    <p><strong>סוג מסד:</strong> {}</p>
    <p><strong>כתובת:</strong> {}</p>
    
    <h2>קישורים מהירים:</h2>
    <p><a href="/portfolio">צפייה בתיק השקעות</a></p>
    <p><a href="/">דף הבית</a></p>
    """.format(
        'PostgreSQL' if portfolio_model.use_postgres else 'SQLite',
        portfolio_model.db_url
    )
    
    print("=== סיום פונקציית db_admin ===")
    return html

@app.route('/ollama-test')
def ollama_test():
    """בדיקת חיבור ל-Ollama"""
    print("=== התחלת בדיקת Ollama ===")
    try:
        # בדיקת זמינות Ollama
        ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        print(f"בודק Ollama בכתובת: {ollama_url}")
        
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        
        if response.status_code == 200:
            result = f"""
            <h2>בדיקת Ollama - הצליחה!</h2>
            <p><strong>כתובת:</strong> {ollama_url}</p>
            <p><strong>סטטוס:</strong> זמין ופועל</p>
            <p><strong>תגובה:</strong> {response.status_code}</p>
            
            <h3>מודלים זמינים:</h3>
            <pre>{response.text}</pre>
            
            <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
            """
        else:
            result = f"""
            <h2>בדיקת Ollama - בעיה</h2>
            <p><strong>כתובת:</strong> {ollama_url}</p>
            <p><strong>סטטוס:</strong> לא זמין</p>
            <p><strong>תגובה:</strong> {response.status_code}</p>
            
            <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
            """
        
        print("=== סיום בדיקת Ollama ===")
        return result
        
    except Exception as e:
        print(f"שגיאה בבדיקת Ollama: {str(e)}")
        return f"""
        <h2>שגיאה בבדיקת Ollama</h2>
        <p>שגיאה: {str(e)}</p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

@app.route('/env-test')
def env_test():
    """בדיקת משתני סביבה"""
    print("=== התחלת בדיקת משתני סביבה ===")
    
    env_vars = {
        'DATABASE_URL': os.environ.get('DATABASE_URL', 'לא מוגדר'),
        'OLLAMA_URL': os.environ.get('OLLAMA_URL', 'לא מוגדר'),
        'PORT': os.environ.get('PORT', 'לא מוגדר'),
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'לא מוגדר'),
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'לא מוגדר')
    }
    
    result = """
    <h2>בדיקת משתני סביבה</h2>
    <p>הנה משתני הסביבה המוגדרים:</p>
    
    <table border="1">
        <tr><th>משתנה</th><th>ערך</th></tr>
    """
    
    for var_name, var_value in env_vars.items():
        # מסתיר ערכים רגישים
        if 'SECRET' in var_name or 'PASSWORD' in var_name:
            display_value = '*** מוסתר ***' if var_value != 'לא מוגדר' else var_value
        else:
            display_value = var_value
        result += f"<tr><td>{var_name}</td><td>{display_value}</td></tr>"
    
    result += """
    </table>
    
    <h3>הסבר:</h3>
    <ul>
        <li><strong>DATABASE_URL:</strong> כתובת למסד הנתונים (PostgreSQL או SQLite)</li>
        <li><strong>OLLAMA_URL:</strong> כתובת לשרת Ollama (בינה מלאכותית)</li>
        <li><strong>PORT:</strong> פורט להרצת האפליקציה</li>
        <li><strong>FLASK_ENV:</strong> סביבת Flask (development/production)</li>
        <li><strong>SECRET_KEY:</strong> מפתח סודי לאפליקציה</li>
    </ul>
    
    <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
    """
    
    print("=== סיום בדיקת משתני סביבה ===")
    return result

@app.route('/db-status')
def db_status():
    """מראה סטטוס מפורט של מסד הנתונים"""
    print("=== התחלת בדיקת סטטוס מסד נתונים ===")
    try:
        conn = portfolio_model.get_connection()
        cursor = conn.cursor()
        
        # בודק טבלאות
        if portfolio_model.use_postgres:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        
        tables = cursor.fetchall()
        
        # בודק תוכן של כל טבלה
        table_info = []
        for table in tables:
            table_name = table[0] if isinstance(table, tuple) else table
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                table_info.append((table_name, count))
            except:
                table_info.append((table_name, "שגיאה"))
        
        conn.close()
        
        result = f"""
        <h2>סטטוס מסד נתונים</h2>
        <p><strong>סוג מסד:</strong> {'PostgreSQL' if portfolio_model.use_postgres else 'SQLite'}</p>
        <p><strong>כתובת:</strong> {portfolio_model.db_url}</p>
        <p><strong>מספר טבלאות:</strong> {len(tables)}</p>
        
        <h3>תוכן הטבלאות:</h3>
        <table border="1">
            <tr><th>שם טבלה</th><th>מספר רשומות</th></tr>
        """
        
        for table_name, count in table_info:
            result += f"<tr><td>{table_name}</td><td>{count}</td></tr>"
        
        result += """
        </table>
        
        <h3>פעולות זמינות:</h3>
        <ul>
            <li><a href="/create-tables">יצירת טבלאות</a></li>
            <li><a href="/add-sample-data">הוספת נתונים לדוגמה</a></li>
            <li><a href="/inject-cloud-data">הזרקת נתונים לענן</a></li>
        </ul>
        
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """
        
        print("=== סיום בדיקת סטטוס מסד נתונים ===")
        return result
        
    except Exception as e:
        print(f"שגיאה בבדיקת סטטוס: {str(e)}")
        return f"""
        <h2>שגיאה בבדיקת סטטוס מסד נתונים</h2>
        <p>שגיאה: {str(e)}</p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

@app.route('/connection-test')
def connection_test():
    """נתיב לבדיקת חיבור מפורטת"""
    print("=== התחלת בדיקת חיבור מפורטת ===")
    
    try:
        # בדיקת חיבור למסד הנתונים
        connection_info = portfolio_model.get_connection_info()
        
        html = f"""
        <h1>בדיקת חיבור מפורטת</h1>
        
        <h2>מסד נתונים:</h2>
        <ul>
            <li><strong>סוג:</strong> {connection_info['type']}</li>
            <li><strong>כתובת:</strong> {connection_info['url']}</li>
            <li><strong>סטטוס:</strong> {connection_info['status']}</li>
        </ul>
        
        <h2>פרטי חיבור:</h2>
        <pre>{connection_info['details']}</pre>
        
        <h2>בדיקות נוספות:</h2>
        <ul>
            <li><a href="/dbtest">בדיקת טבלאות</a></li>
            <li><a href="/db-status">סטטוס מסד נתונים</a></li>
            <li><a href="/ollama-test">בדיקת AI</a></li>
        </ul>
        
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """
        
        print("=== סיום בדיקת חיבור מפורטת ===")
        return html
        
    except Exception as e:
        print(f"שגיאה בבדיקת חיבור: {str(e)}")
        return f"""
        <h1>שגיאה בבדיקת חיבור</h1>
        <p>שגיאה: {str(e)}</p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

@app.route('/inject-cloud-data')
def inject_cloud_data():
    """הזרקת נתונים למסד הנתונים PostgreSQL בענן"""
    print("=== התחלת הזרקת נתונים לענן ===")
    try:
        conn = portfolio_model.get_connection()
        cursor = conn.cursor()
        
        # יצירת טבלאות
        print("יוצר טבלאות...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(120) UNIQUE,
                role VARCHAR(20) DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investments (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                industry VARCHAR(100),
                variance VARCHAR(50),
                security_type VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("טבלאות נוצרו בהצלחה")
        
        # הוספת ניירות ערך לדוגמה
        print("מוסיף ניירות ערך...")
        securities = [
            ('אפל', 10, 150.25, 'טכנולוגיה', 'גבוה', 'מניה רגילה'),
            ('מיקרוסופט', 8, 320.75, 'טכנולוגיה', 'בינוני', 'מניה רגילה'),
            ('גוגל', 5, 2800.50, 'טכנולוגיה', 'גבוה', 'מניה רגילה'),
            ('אמזון', 2, 3300.25, 'צריכה פרטית', 'גבוה', 'מניה רגילה'),
            ('טסלה', 3, 850.75, 'תחבורה', 'גבוה', 'מניה רגילה'),
            ('אגח ממשלתי', 100, 100.00, 'פיננסים', 'נמוך', 'אגח ממשלתית'),
            ('אגח קונצרנית', 50, 95.50, 'תעשייה', 'בינוני', 'אגח קונצרנית'),
            ('נדלן', 20, 75.25, 'נדלן', 'בינוני', 'מניה רגילה'),
            ('בריאות', 15, 120.80, 'בריאות', 'בינוני', 'מניה רגילה'),
            ('אנרגיה', 25, 45.30, 'אנרגיה', 'גבוה', 'מניה רגילה')
        ]
        
        for security in securities:
            if portfolio_model.use_postgres:
                cursor.execute("""
                    INSERT INTO investments (name, amount, price, industry, variance, security_type)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (name) DO UPDATE SET
                        amount = EXCLUDED.amount,
                        price = EXCLUDED.price,
                        industry = EXCLUDED.industry,
                        variance = EXCLUDED.variance,
                        security_type = EXCLUDED.security_type
                """, security)
            else:
                # SQLite doesn't support ON CONFLICT with EXCLUDED, so we use INSERT OR REPLACE
                cursor.execute("""
                    INSERT OR REPLACE INTO investments (name, amount, price, industry, variance, security_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, security)
        
        # הוספת משתמשים לדוגמה
        print("מוסיף משתמשים...")
        # משתמש בסיסמאות פשוטות כמו שביקשת
        admin_password_hash = 'admin'
        user_password_hash = 'user'
        
        users = [
            ('admin', admin_password_hash, 'admin@example.com', 'admin'),
            ('user', user_password_hash, 'user@example.com', 'user')
        ]
        
        for user in users:
            if portfolio_model.use_postgres:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email, role)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (username) DO UPDATE SET
                        password_hash = EXCLUDED.password_hash,
                        email = EXCLUDED.email,
                        role = EXCLUDED.role
                """, user)
            else:
                # SQLite version
                cursor.execute("""
                    INSERT OR REPLACE INTO users (username, password_hash, email, role)
                    VALUES (?, ?, ?, ?)
                """, user)
        
        conn.commit()
        
        # בדיקת התוצאה
        cursor.execute("SELECT COUNT(*) FROM investments")
        investments_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"הזרקת נתונים הושלמה: {investments_count} השקעות, {users_count} משתמשים")
        
        result = f"""
        <h2>הזרקת נתונים לענן - הצליחה!</h2>
        <p>הנתונים הוזרקו בהצלחה למסד הנתונים PostgreSQL בענן.</p>
        
        <h3>סיכום הנתונים שהוזרקו:</h3>
        <ul>
            <li><strong>השקעות:</strong> {investments_count}</li>
            <li><strong>משתמשים:</strong> {users_count}</li>
        </ul>
        
        <h3>פרטי התחברות:</h3>
        <p><strong>מנהל:</strong> שם משתמש: admin | סיסמה: admin</p>
        <p><strong>משתמש:</strong> שם משתמש: user | סיסמה: user</p>
        
        <h3>קישורים מהירים:</h3>
        <p><a href="/login">התחברות למערכת</a></p>
        <p><a href="/portfolio">צפייה בתיק השקעות</a></p>
        <p><a href="/db-admin">ניהול מסד נתונים</a></p>
        <p><a href="/">דף הבית</a></p>
        """
        
        print("=== סיום הזרקת נתונים לענן ===")
        return result
        
    except Exception as e:
        print(f"שגיאה בהזרקת נתונים: {str(e)}")
        return f"""
        <h2>שגיאה בהזרקת נתונים</h2>
        <p>שגיאה: {str(e)}</p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

print("=== כל הנתיבים נרשמו בהצלחה ===")
print("=== האפליקציה מוכנה להפעלה ===")
print("=== סיום טעינת האפליקציה ===")

# נתיב בדיקת בריאות
@app.route('/health')
def health_check():
    """נתיב לבדיקת בריאות האפליקציה - נדרש ל-Railway"""
    try:
        # בדיקה בסיסית שהאפליקציה עובדת - ללא חיבור למסד נתונים
        from datetime import datetime
        import os
        port = os.environ.get('PORT', '4000')
        return {
            'status': 'healthy',
            'message': 'Application is running',
            'timestamp': datetime.now().isoformat(),
            'port': port
        }, 200
    except Exception as e:
        from datetime import datetime
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500

@app.route('/health-simple')
def health_simple():
    """נתיב פשוט לבדיקת בריאות - מחזיר טקסט פשוט"""
    return "OK", 200

@app.route('/ping')
def ping():
    """נתיב ping לבדיקת בריאות - Railway יכול להשתמש בו"""
    return "OK", 200

@app.route('/api/status')
def api_status():
    """נתיב API שמחזיר JSON עם סטטוס האפליקציה"""
    try:
        import os
        port = os.environ.get('PORT', '4000')
        return jsonify({
            'message': 'האפליקציה עובדת!',
            'port': port,
            'status': 'success',
            'app_type': 'full_app',
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug')
def debug_info():
    """נתיב לבדיקת מידע על המערכת"""
    try:
        info = {
            'database_url': os.environ.get('DATABASE_URL', 'לא מוגדר'),
            'port': os.environ.get('PORT', 'לא מוגדר'),
            'ollama_url': os.environ.get('OLLAMA_URL', 'לא מוגדר'),
            'use_postgres': portfolio_model.use_postgres,
            'db_url': portfolio_model.db_url
        }
        
        # בדיקת חיבור למסד
        try:
            securities = portfolio_model.get_all_securities()
            info['database_connection'] = 'עובד'
            info['securities_count'] = len(securities)
        except Exception as e:
            info['database_connection'] = f'שגיאה: {str(e)}'
            info['securities_count'] = 0
            
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/setup-database')
def setup_database():
    """
    נתיב להגדרת מסד הנתונים המלא - יוצר טבלאות, משתמשים, ומזריק 20 ניירות ערך אמיתיים (10 מהעולם, 10 מהארץ) עם מחירים בזמן אמת מ-Alpha Vantage API
    """
    print("=== התחלת הגדרת מסד נתונים מלא ===")
    
    # הגדרת רשימות ניירות ערך אמיתיים
    world_securities = [
        ("AAPL", "Apple Inc", "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("MSFT", "Microsoft Corp", "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("TSLA", "Tesla Inc", "תחבורה", "גבוה", "מניה רגילה"),
        ("AMZN", "Amazon.com Inc", "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("GOOG", "Alphabet Inc", "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("META", "Meta Platforms Inc", "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("NVDA", "NVIDIA Corp", "טכנולוגיה", "גבוה", "מניה רגילה"),
        ("JPM", "JPMorgan Chase", "פיננסים", "נמוך", "מניה רגילה"),
        ("WMT", "Walmart Inc", "צריכה פרטית", "נמוך", "מניה רגילה"),
        ("V", "Visa Inc", "פיננסים", "נמוך", "מניה רגילה")
    ]
    
    israel_securities = [
        ('TEVA', 'Teva Pharmaceutical', 'בריאות', 'גבוה', 'מניה רגילה'),
        ('CHKP', 'Check Point Software', 'טכנולוגיה', 'גבוה', 'מניה רגילה'),
        ('NICE', 'NICE Ltd', 'טכנולוגיה', 'גבוה', 'מניה רגילה'),
        ('CYBR', 'CyberArk Software', 'טכנולוגיה', 'גבוה', 'מניה רגילה'),
        ('WIX', 'Wix.com Ltd', 'טכנולוגיה', 'גבוה', 'מניה רגילה'),
        ('MNDY', 'Monday.com Ltd', 'טכנולוגיה', 'גבוה', 'מניה רגילה'),
        ('ZIM', 'ZIM Integrated Shipping', 'תחבורה', 'גבוה', 'מניה רגילה'),
        ('FVRR', 'Fiverr International', 'טכנולוגיה', 'גבוה', 'מניה רגילה'),
        ('ORMP', 'Oramed Pharmaceuticals', 'בריאות', 'גבוה', 'מניה רגילה'),
        ('RDWR', 'Radware Ltd', 'טכנולוגיה', 'גבוה', 'מניה רגילה')
    ]
    
    try:
        # יצירת טבלאות
        print("יוצר טבלאות...")
        portfolio_model.create_tables()
        print("טבלאות נוצרו בהצלחה")
        
        # הוספת משתמשים
        print("מוסיף משתמשים...")
        conn = portfolio_model.get_connection()
        cursor = conn.cursor()
        # משתמש בסיסמאות פשוטות כמו שביקשת
        admin_password_hash = 'admin'
        demo_password_hash = 'user'
        
        # בדיקה אם משתמש admin כבר קיים
        if portfolio_model.use_postgres:
            cursor.execute('SELECT id FROM users WHERE username = %s', ('admin',))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, role)
                    VALUES (%s, %s, %s, %s)
                ''', ('admin', admin_password_hash, 'admin@example.com', 'admin'))
        else:
            cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, role)
                    VALUES (?, ?, ?, ?)
                ''', ('admin', admin_password_hash, 'admin@example.com', 'admin'))
        
        # בדיקה אם משתמש user כבר קיים
        if portfolio_model.use_postgres:
            cursor.execute('SELECT id FROM users WHERE username = %s', ('user',))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, role)
                    VALUES (%s, %s, %s, %s)
                ''', ('user', demo_password_hash, 'demo@example.com', 'user'))
        else:
            cursor.execute('SELECT id FROM users WHERE username = ?', ('user',))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO users (username, password_hash, email, role)
                    VALUES (?, ?, ?, ?)
                ''', ('user', demo_password_hash, 'demo@example.com', 'user'))
        
        conn.commit()
        conn.close()
        print("משתמשים נוספו בהצלחה")
        
        # בדיקה אם כבר יש ניירות ערך
        existing_securities = portfolio_model.get_all_securities()
        total_securities = len(world_securities) + len(israel_securities)
        
        if len(existing_securities) > 0:
            print(f"כבר יש {len(existing_securities)} ניירות ערך במסד הנתונים")
            print("=== סיום הגדרת מסד נתונים מלא ===")
            result = f"""
            <h2>הגדרת מסד נתונים - הושלמה!</h2>
            <p>המסד הנתונים כבר מכיל {len(existing_securities)} ניירות ערך.</p>
            <h3>מה קיים:</h3>
            <ul>
                <li><strong>טבלאות:</strong> users, securities, investments</li>
                <li><strong>משתמשים:</strong> admin, user</li>
                <li><strong>ניירות ערך:</strong> {len(existing_securities)} מניות ואגרות חוב</li>
                <li><strong>ניירות ערך זמינים להוספה:</strong> {total_securities} (10 מהעולם + 10 מישראל)</li>
            </ul>
            <h3>פרטי התחברות:</h3>
            <p><strong>מנהל:</strong> שם משתמש: admin | סיסמה: admin</p>
            <p><strong>משתמש:</strong> שם משתמש: user | סיסמה: user</p>
            <h3>קישורים מהירים:</h3>
            <p><a href="/login">התחברות למערכת</a></p>
            <p><a href="/portfolio">צפייה בתיק השקעות</a></p>
            <p><a href="/">דף הבית</a></p>
            """
            return result
        
        # הוספת 20 ניירות ערך אמיתיים עם מחירים מ-Alpha Vantage API
        print("מוסיף ניירות ערך אמיתיים עם מחירים מ-Alpha Vantage API...")
        
        # כמות ברירת מחדל לכל נייר ערך
        default_amount = 10
        added_count = 0
        failed_count = 0
        
        # הזרקת מניות מהעולם
        for symbol, name, industry, variance, security_type in world_securities:
            try:
                print(f"מביא מחיר אמיתי עבור {symbol} ({name})...")
                # קבלת מחיר אמיתי מ-Alpha Vantage API
                real_price = Broker.update_price(symbol)
                
                if real_price and real_price > 0:
                    portfolio_model.add_security(name, default_amount, real_price, industry, variance, security_type)
                    print(f"✅ נוסף: {name} ({symbol}) - {default_amount} יחידות ב-{real_price:.2f} ₪ (מחיר אמיתי)")
                    added_count += 1
                else:
                    print(f"❌ לא הצלחתי לקבל מחיר אמיתי עבור {symbol} - מדלג")
                    failed_count += 1
                    
                # עיכוב קטן בין בקשות כדי לא לעבור על מגבלות ה-API
                time.sleep(0.5)
                    
            except Exception as e:
                print(f"❌ שגיאה בהוספת {name} ({symbol}): {e}")
                failed_count += 1
        
        # הזרקת מניות ישראליות
        for symbol, name, industry, variance, security_type in israel_securities:
            try:
                print(f"מביא מחיר אמיתי עבור {symbol} ({name})...")
                # קבלת מחיר אמיתי מ-Alpha Vantage API
                real_price = Broker.update_price(symbol)
                
                if real_price and real_price > 0:
                    portfolio_model.add_security(name, default_amount, real_price, industry, variance, security_type)
                    print(f"✅ נוסף: {name} ({symbol}) - {default_amount} יחידות ב-{real_price:.2f} ₪ (מחיר אמיתי)")
                    added_count += 1
                else:
                    print(f"❌ לא הצלחתי לקבל מחיר אמיתי עבור {symbol} - מדלג")
                    failed_count += 1
                    
                # עיכוב קטן בין בקשות
                time.sleep(0.5)
                    
            except Exception as e:
                print(f"❌ שגיאה בהוספת {name} ({symbol}): {e}")
                failed_count += 1
        
        print("=== סיום הגדרת מסד נתונים מלא ===")
        
        if added_count == 0:
            result = f"""
            <h2>⚠️ בעיה בהגדרת מסד נתונים</h2>
            <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <p><strong>לא הצלחתי להוסיף ניירות ערך עם מחירים אמיתיים!</strong></p>
                <p>נכשלו {failed_count} ניירות ערך מתוך {total_securities}.</p>
            </div>
            
            <h3>סיבות אפשריות:</h3>
            <ul>
                <li>בעיה עם Alpha Vantage API</li>
                <li>מגבלת קריאות API</li>
                <li>בעיית חיבור לאינטרנט</li>
                <li>מפתח API לא תקין</li>
            </ul>
            
            <h3>פתרונות:</h3>
            <ul>
                <li>בדוק את חיבור האינטרנט</li>
                <li>נסה שוב מאוחר יותר</li>
                <li>בדוק את מפתח Alpha Vantage API</li>
            </ul>
            
            <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
            """
        else:
            result = f"""
            <h2>✅ הגדרת מסד נתונים - הצליחה!</h2>
            <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <p>המסד הנתונים הוגדר בהצלחה עם כל הטבלאות, המשתמשים ו-{added_count} ניירות ערך אמיתיים.</p>
                {f'<p style="color: #856404;">⚠️ {failed_count} ניירות ערך נכשלו (לא הצלחתי לקבל מחיר אמיתי)</p>' if failed_count > 0 else ''}
            </div>
            
            <h3>מה שנוצר:</h3>
            <ul>
                <li><strong>טבלאות:</strong> users, securities, investments</li>
                <li><strong>משתמשים:</strong> admin, user</li>
                <li><strong>ניירות ערך:</strong> {added_count} מניות ואגרות חוב (מחירים אמיתיים מ-Alpha Vantage API)</li>
            </ul>
            
            <h3>פרטי התחברות:</h3>
            <p><strong>מנהל:</strong> שם משתמש: admin | סיסמה: admin</p>
            <p><strong>משתמש:</strong> שם משתמש: user | סיסמה: user</p>
            
            <h3>קישורים מהירים:</h3>
            <p><a href="/login">התחברות למערכת</a></p>
            <p><a href="/portfolio">צפייה בתיק השקעות</a></p>
            <p><a href="/update-all-prices">עדכון מחירים</a></p>
            <p><a href="/">דף הבית</a></p>
            """
        return result
    except Exception as e:
        print(f"שגיאה בהגדרת מסד נתונים: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"""
        <h2>❌ שגיאה בהגדרת מסד נתונים</h2>
        <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 10px 0;">
            <p><strong>שגיאה:</strong> {str(e)}</p>
        </div>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

@app.route('/check-env')
def check_env():
    """נתיב לבדיקת משתני סביבה מפורטת"""
    try:
        import os
        env_info = {
            'DATABASE_URL': os.environ.get('DATABASE_URL', 'לא מוגדר'),
            'PORT': os.environ.get('PORT', 'לא מוגדר'),
            'OLLAMA_URL': os.environ.get('OLLAMA_URL', 'לא מוגדר'),
            'FLASK_ENV': os.environ.get('FLASK_ENV', 'לא מוגדר'),
            'SECRET_KEY': os.environ.get('SECRET_KEY', 'לא מוגדר')
        }
        
        # בדיקת חיבור למסד
        try:
            conn = portfolio_model.get_connection()
            conn.close()
            env_info['database_connection'] = 'עובד'
        except Exception as e:
            env_info['database_connection'] = f'שגיאה: {str(e)}'
        
        html = """
        <h2>בדיקת משתני סביבה</h2>
        <table border="1" style="width: 100%; border-collapse: collapse;">
            <tr><th>משתנה</th><th>ערך</th></tr>
        """
        
        for key, value in env_info.items():
            html += f"<tr><td>{key}</td><td>{value}</td></tr>"
        
        html += """
        </table>
        
        <h3>המלצות:</h3>
        <ul>
            <li>אם DATABASE_URL לא מוגדר - הגדר אותו לכתובת PostgreSQL</li>
            <li>אם database_connection לא עובד - בדוק את כתובת ה-DATABASE_URL</li>
        </ul>
        
        <h3>פעולות:</h3>
        <p><a href="/setup-database">הגדר מסד נתונים מלא</a></p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """
        
        return html
        
    except Exception as e:
        return f"שגיאה: {str(e)}"

@app.route('/ollama-status')
def ollama_status():
    """נתיב לבדיקת סטטוס Ollama"""
    try:
        import requests
        import os
        
        ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        
        # בדיקת זמינות Ollama
        try:
            response = requests.get(f"{ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [model.get('name', '') for model in models]
                
                html = f"""
                <h2>סטטוס Ollama AI</h2>
                <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h3 style="color: #155724; margin: 0;">✅ Ollama פועל וזמין</h3>
                    <p><strong>כתובת:</strong> {ollama_url}</p>
                    <p><strong>מודלים זמינים:</strong> {len(models)}</p>
                </div>
                
                <h3>מודלים מותקנים:</h3>
                <ul>
                """
                
                for model_name in model_names:
                    html += f"<li>{model_name}</li>"
                
                html += """
                </ul>
                
                <h3>בדיקות נוספות:</h3>
                <p><a href="/advice">בדוק ייעוץ השקעות עם AI</a></p>
                <p><a href="/risk">בדוק ניתוח סיכונים עם AI</a></p>
                <p><a href="/health">בדיקת בריאות כללית</a></p>
                """
                
                return html
            else:
                return f"""
                <h2>סטטוס Ollama AI</h2>
                <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 10px 0;">
                    <h3 style="color: #721c24; margin: 0;">❌ Ollama לא זמין</h3>
                    <p><strong>כתובת:</strong> {ollama_url}</p>
                    <p><strong>קוד תגובה:</strong> {response.status_code}</p>
                </div>
                
                <h3>פתרון בעיות:</h3>
                <ul>
                    <li>וודא ש-Ollama רץ</li>
                    <li>בדוק את משתנה הסביבה OLLAMA_URL</li>
                    <li>בדוק את הלוגים של שירות Ollama</li>
                </ul>
                """
                
        except requests.exceptions.RequestException as e:
            return f"""
            <h2>סטטוס Ollama AI</h2>
            <div style="background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3 style="color: #721c24; margin: 0;">❌ שגיאה בחיבור ל-Ollama</h3>
                <p><strong>כתובת:</strong> {ollama_url}</p>
                <p><strong>שגיאה:</strong> {str(e)}</p>
            </div>
            
            <h3>פתרון בעיות:</h3>
            <ul>
                <li>וודא ש-Ollama רץ</li>
                <li>בדוק את משתנה הסביבה OLLAMA_URL</li>
                <li>בדוק את הלוגים של שירות Ollama</li>
            </ul>
            """
            
    except Exception as e:
        return f"""
        <h2>שגיאה בבדיקת Ollama</h2>
        <p>שגיאה: {str(e)}</p>
        """

@app.route('/api-keys-status')
@login_required
@admin_required
def api_keys_status():
    """מציג מצב מפתחות ה-API ומאפשר ניהול שלהם"""
    try:
        # קבלת מידע על מצב המפתחות
        status = Broker.get_api_keys_status()
        
        return render_template('api_keys.html', 
                             total_keys=status['total_keys'],
                             current_key_index=status['current_key_index'],
                             current_key=status['current_key'],
                             available_keys=status['available_keys'])
        
    except Exception as e:
        flash(f'שגיאה בקבלת מצב מפתחות: {str(e)}', 'danger')
        return redirect(url_for('portfolio'))

@app.route('/reset-api-rotation')
@login_required
@admin_required
def reset_api_rotation():
    """מאפס את רוטציה המפתחות למפתח הראשון"""
    try:
        Broker.reset_key_rotation()
        flash('רוטציה המפתחות אופסה למפתח הראשון', 'success')
    except Exception as e:
        flash(f'שגיאה באיפוס רוטציה: {str(e)}', 'danger')
    return redirect(url_for('api_keys_status'))

@app.route('/test-current-api-key')
@login_required
@admin_required
def test_current_api_key():
    """בודק את המפתח הנוכחי עם בקשת מחיר לדוגמה"""
    try:
        # בדיקה עם מניית Apple
        test_symbol = 'AAPL'
        print(f"בודק מפתח נוכחי עם מניית {test_symbol}")
        
        price = Broker.update_price(test_symbol)
        
        if price and price > 0:
            flash(f'המפתח הנוכחי עובד! מחיר {test_symbol}: ₪{price:.2f}', 'success')
        else:
            flash(f'המפתח הנוכחי לא עובד או הגיע למגבלה', 'warning')
            
    except Exception as e:
        flash(f'שגיאה בבדיקת מפתח: {str(e)}', 'danger')
    
    return redirect(url_for('api_keys_status'))

# מפעילים את האתר
def initialize_app():
    """אתחול האפליקציה - יוצר טבלאות ובודק נתונים"""
    print("=== התחלת אתחול האפליקציה ===")
    
    # יצירת טבלאות במסד הנתונים
    print("=== יצירת טבלאות במסד הנתונים ===")
    portfolio_model.create_tables()
    print("=== טבלאות נוצרו בהצלחה ===")
    
    # בדיקת תוכן מסד הנתונים
    print("=== בדיקת תוכן מסד הנתונים ===")
    securities = portfolio_model.get_all_securities()
    print(f"מסד הנתונים מכיל {len(securities)} ניירות ערך")
    
    print("=== סיום אתחול האפליקציה ===")

# הגדרת פונט שתומך בעברית
plt.rcParams['font.family'] = ['Arial']  # הגדרת פונט שתומך בעברית

# הוספת פילטר nl2br עבור Jinja2
def nl2br(value):
    """המרת שורות חדשות ל-<br> tags"""
    if value is None:
        return ""
    return value.replace('\n', '<br>')

app.jinja_env.filters['nl2br'] = nl2br

@app.route('/favicon.ico')
def favicon():
if __name__ == '__main__':
    print("=== התחלת הפעלת האפליקציה ===")
    
    # אתחול האפליקציה
    initialize_app()
    
    # קבלת פורט מהסביבה (עבור Railway/Heroku)
    port = int(os.environ.get('PORT', 4000))
    print(f"=== האפליקציה רצה על פורט {port} ===")
    
    # הפעלת האפליקציה
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # כשמריצים עם gunicorn, רק מאתחלים את הטבלאות
    print("=== אתחול עבור gunicorn ===")
    try:
        portfolio_model.create_tables()
        print("=== טבלאות נוצרו בהצלחה ===")
    except Exception as e:
        print(f"שגיאה באתחול: {e}")
    print("=== סיום אתחול עבור gunicorn ===")
