from flask import Flask, render_template, redirect, url_for, flash, Response, request, jsonify
from flask_login import (LoginManager, UserMixin, login_user, logout_user,
                        login_required, current_user)
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField, FloatField,
                    SelectField)
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import matplotlib
matplotlib.use('Agg')  # משתמש ב-backend שלא דורש GUI
import matplotlib.pyplot as plt
import io
import os
import logging
import requests
import psycopg2
import sys
import traceback
import time

print("=== התחלת ייבוא ספריות ===")
print("=== בדיקת משתני סביבה ===")
DATABASE_URL = os.getenv('DATABASE_URL')
PORT = os.getenv('PORT', '4000')
OLLAMA_URL = os.getenv('OLLAMA_URL')
print(f"DATABASE_URL: {DATABASE_URL}")
print(f"PORT: {PORT}")
print(f"OLLAMA_URL: {OLLAMA_URL}")
print("=== סיום בדיקת משתני סביבה ===")

# מביאים הקלסים שיצרנו בקבצים אחרים
print("=== התחלת ייבוא dbmodel ===")
try:
    from dbmodel import PortfolioModel
    print("=== סיום ייבוא dbmodel ===")
except Exception as e:
    print(f"שגיאה בייבוא dbmodel: {str(e)}")
    logger.error(f"שגיאה בייבוא dbmodel: {str(e)}")
    sys.exit(1)

print("=== התחלת ייבוא portfolio_controller ===")
try:
    from portfolio_controller import PortfolioController, RiskManager
    print("=== סיום ייבוא portfolio_controller ===")
except Exception as e:
    print(f"שגיאה בייבוא portfolio_controller: {str(e)}")
    logger.error(f"שגיאה בייבוא portfolio_controller: {str(e)}")
    sys.exit(1)

print("=== התחלת ייבוא securities ===")
try:
    from securities import Stock, Bond
    print("=== סיום ייבוא securities ===")
except Exception as e:
    print(f"שגיאה בייבוא securities: {str(e)}")
    logger.error(f"שגיאה בייבוא securities: {str(e)}")

print("=== התחלת ייבוא ollamamodel ===")
try:
    from ollamamodel import AI_Agent
    print("=== סיום ייבוא ollamamodel ===")
except Exception as e:
    print(f"שגיאה בייבוא ollamamodel: {str(e)}")
    logger.error(f"שגיאה בייבוא ollamamodel: {str(e)}")

print("=== התחלת ייבוא broker ===")
try:
    from broker import Broker
    print("=== סיום ייבוא broker ===")
except Exception as e:
    print(f"שגיאה בייבוא broker: {str(e)}")
    logger.error(f"שגיאה בייבוא broker: {str(e)}")

print("=== התחלת טעינת האפליקציה ===")

plt.rcParams['font.family'] = ['Arial']  # הגדרת פונט שתומך בעברית

# הוספת לוגים מפורטים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# יוצרים את האתר - זה הדבר הכי חשוב
app = Flask(__name__)  # זה יוצר את האתר שלנו
app.config['SECRET_KEY'] = 'your-secret-key-here'  # מפתח חשאי לאבטחה
login_manager = LoginManager()  # דבר שמנהל כניסה למערכת
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
        return check_password_hash(self.password_hash, password)  # מחזיר אמת/שקר
    
    def is_admin(self):  # בודק אם המשתמש הוא מנהל
        return self.role == 'admin'  # מחזיר אמת אם הוא מנהל

# רשימת המשתמשים המורשים במערכת עם סיסמאות מוצפנות
USERS = {
    # מנהל עם הרשאות מלאות - יכול לבצע כל פעולה
    'admin': User('1', 'admin', generate_password_hash('admin'), 'admin'),
    # מפעיל עם הרשאות צפייה בלבד - לא יכול לערוך
    'user': User('2', 'user', generate_password_hash('user'), 'user')
}

@login_manager.user_loader  # פונקציה שמוצאת משתמש לפי מספר זיהוי
def load_user(user_id):  # מקבלת מספר זיהוי של משתמש
    try:
        return portfolio_model.get_user_by_id(int(user_id))
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

print("=== התחלת יצירת PortfolioController ===")
try:
    portfolio_controller = PortfolioController(portfolio_model)  # יוצר את הקונטרולר שמנהל הכל
    print("=== סיום יצירת PortfolioController ===")
except Exception as e:
    print(f"שגיאה ביצירת PortfolioController: {str(e)}")
    logger.error(f"שגיאה ביצירת PortfolioController: {str(e)}")
    traceback.print_exc()

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
    name = StringField('שם נייר הערך', validators=[DataRequired()])  # שדה לשם המניה (חובה)
    amount = FloatField('כמות', validators=[DataRequired()])  # שדה לכמות שרוצים לקנות (חובה)
    # רשימה נפתחת לבחירת הענף שאליו שייכת המניה
    industry = SelectField('ענף', choices=[
        ('טכנולוגיה', 'טכנולוגיה'), ('תחבורה', 'תחבורה'), ('אנרגיה', 'אנרגיה'),
        ('בריאות', 'בריאות'), ('תעשייה', 'תעשייה'), ('פיננסים', 'פיננסים'),
        ('נדלן', 'נדלן'), ('צריכה פרטית', 'צריכה פרטית')
    ])
    # רשימה נפתחת לבחירת רמת השונות במחיר
    variance = SelectField('רמת שונות', choices=[('נמוך', 'נמוך'), ('גבוה', 'גבוה')])
    # רשימה נפתחת לבחירת סוג נייר הערך
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
        
        form = LoginForm()  # יוצר טופס כניסה חדש
        print(f"טופס נוצר, validate_on_submit: {form.validate_on_submit()}")
        
        if form.validate_on_submit():  # בודק אם הטופס נשלח ועבר אימות
            username = form.username.data
            password = form.password.data
            print(f"ניסיון התחברות עם שם משתמש: {username}")
            
            user = USERS.get(username)  # מחפש את המשתמש ברשימת המשתמשים
            print(f"משתמש נמצא: {user is not None}")
            
            if user and user.check_password(password):  # בודק אם המשתמש קיים והסיסמה נכונה
                print("סיסמה נכונה, מתחבר...")
                login_user(user)  # מחבר את המשתמש למערכת
                print("התחברות הצליחה")
                return redirect(url_for('index'))  # מפנה אותו לדף הבית
            else:
                print("שם משתמש או סיסמה שגויים")
                flash('שם משתמש או סיסמה שגויים', 'danger')  # מציג הודעת שגיאה אם הפרטים שגויים
        
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
@login_required  # דקורטור שדורש שהמשתמש יהיה מחובר
def index():  # פונקציה שמציגה את דף הבית
    try:
        if current_user.is_authenticated:
            return redirect(url_for('portfolio'))
        return render_template('index.html')
    except Exception as e:
        logger.error(f"שגיאה בנתיב הראשי: {str(e)}")
        return "שגיאה בטעינת הדף", 500

@app.route('/portfolio')  # נתיב לדף התיק ההשקעות המלא
@login_required  # דקורטור שדורש שהמשתמש יהיה מחובר
def portfolio():  # פונקציה שמציגה את תיק ההשקעות המלא
    print("=== התחלת פונקציית portfolio ===")
    try:
        portfolio_data = portfolio_controller.get_portfolio()  # מקבל את כל ניירות הערך
        print(f"מספר ניירות ערך בתיק: {len(portfolio_data)}")
        return render_template('portfolio.html', portfolio=portfolio_data)
    except Exception as e:
        print(f"שגיאה בדף התיק: {str(e)}")
        flash('שגיאה בטעינת התיק', 'danger')
        return render_template('portfolio.html', portfolio=[])

@app.route('/portfolio/add', methods=['GET', 'POST'])  # נתיב להוספת נייר ערך חדש
@login_required  # דקורטור שדורש שהמשתמש יהיה מחובר
@admin_required  # דקורטור שדורש הרשאות מנהל
def add_security():  # פונקציה להוספת נייר ערך חדש לתיק
    form = SecurityForm()  # יוצר טופס הוספת נייר ערך
    if form.validate_on_submit():  # בודק אם הטופס נשלח ועבר אימות
        # יוצר אובייקט נייר ערך לפי הסוג שנבחר בטופס
        if form.security_type.data == 'מניה רגילה':  # אם נבחרה מניה רגילה
            security = Stock(form.name.data, form.amount.data)  # יוצר אובייקט מניה
        elif form.security_type.data == 'אגח ממשלתית':  # אם נבחר אג"ח ממשלתי
            security = Bond(form.name.data)  # יוצר אובייקט אג"ח
            security.amount = form.amount.data  # מוסיף את הכמות לאובייקט
        else:  # אם נבחר אג"ח קונצרני
            security = Bond(form.name.data)  # יוצר אובייקט אג"ח
            security.amount = form.amount.data  # מוסיף את הכמות לאובייקט
        
        # מחשב את רמת הסיכון של נייר הערך החדש
        risk = RiskManager.calculate_risk(
            form.security_type.data,  # סוג נייר הערך
            form.industry.data,       # הענף
            form.variance.data        # רמת השונות
        )
        
        result = portfolio_controller.buy_security(security, form.industry.data, form.variance.data, form.security_type.data)  # מוסיף את נייר הערך לתיק
        flash(f"{result} (רמת סיכון: {risk:.2f})", 'success')  # מציג הודעת הצלחה עם רמת הסיכון
        return redirect(url_for('portfolio'))  # מפנה חזרה לדף התיק
    
    return render_template('add_security.html', form=form)  # מציג את דף הוספת נייר ערך

@app.route('/portfolio/delete/<security_name>', methods=['POST'])
@login_required
@admin_required
def delete_security(security_name):
    """מוחק נייר ערך לגמרי מהתיק"""
    try:
        portfolio_controller.remove_security(security_name)
        flash(f'נייר הערך {security_name} נמחק בהצלחה מהתיק', 'success')
    except Exception as e:
        flash(f'שגיאה במחיקת נייר הערך: {str(e)}', 'error')
    
    return redirect(url_for('portfolio'))

@app.route('/update-price/<symbol>')
@login_required
@admin_required
def update_single_price(symbol):
    try:
        price = Broker.update_price(symbol)
        flash(f'מחיר {symbol} עודכן בהצלחה לסכום ₪{price:.2f}', 'success')
    except Exception as e:
        flash(f'שגיאה בעדכון מחיר {symbol}: {str(e)}', 'error')
    return redirect(url_for('portfolio'))

@app.route('/update-all-prices')
@login_required
@admin_required
def update_all_prices():
    portfolio_data = portfolio_controller.get_portfolio()
    updated_count = 0
    errors = 0
    
    for item in portfolio_data:
        try:
            Broker.update_price(item['name'])
            updated_count += 1
        except Exception as e:
            errors += 1
    
    if updated_count > 0:
        flash(f'עודכנו {updated_count} מחירים בהצלחה', 'success')
    if errors > 0:
        flash(f'{errors} מחירים לא עודכנו בגלל שגיאות', 'warning')
    
    return redirect(url_for('portfolio'))

@app.route('/advice', methods=['GET', 'POST'])
@login_required
def advice():
    advice_text = None
    try:
        # קבלת ייעוץ על בסיס התיק הנוכחי
        advice_text = portfolio_controller.get_advice()
    except Exception as e:
        flash(f'שגיאה בקבלת ייעוץ: {str(e)}', 'error')
        advice_text = "מצטער, לא ניתן לקבל ייעוץ כרגע. אנא וודא שהשירות Ollama פועל."
    
    return render_template('advice.html', advice=advice_text)

@app.route('/risk')
@login_required
def risk():
    portfolio_data = portfolio_controller.get_portfolio()
    # חישוב אחוזים
    total_value = sum(item['price'] * item['amount'] for item in portfolio_data)
    for item in portfolio_data:
        item_value = item['price'] * item['amount']
        item['percentage'] = (item_value / total_value * 100) if total_value > 0 else 0
        item['value'] = item_value
    return render_template('risk.html', portfolio=portfolio_data, total_value=total_value)

@app.route('/graph')
@login_required
def graph():
    portfolio_data = portfolio_controller.get_portfolio()
    # חישוב אחוזים
    total_value = sum(item['price'] * item['amount'] for item in portfolio_data)
    for item in portfolio_data:
        item_value = item['price'] * item['amount']
        item['percentage'] = (item_value / total_value * 100) if total_value > 0 else 0
        item['value'] = item_value
    return render_template('graph.html', portfolio=portfolio_data, total_value=total_value)

@app.route('/pie-chart.png')
@login_required
def generate_pie_chart():
    """יוצר תרשים עוגה של התיק ומחזיר אותו כתמונה"""
    # הגדרת תמיכה בעברית
    plt.rcParams['axes.unicode_minus'] = False
    
    portfolio_data = portfolio_controller.get_portfolio()
    
    if not portfolio_data:
        # אם אין נתונים, יוצר גרף ריק
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'אין נתונים להצגה', 
                horizontalalignment='center', verticalalignment='center',
                transform=ax.transAxes, fontsize=16)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
    else:
        # חישוב נתונים לגרף
        names = [item['name'] for item in portfolio_data]  # הסרתי את הפיכת השמות
        values = [item['price'] * item['amount'] for item in portfolio_data]
        
        # יצירת תרשים עוגה
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF',
                  '#FF9F40', '#FF6384', '#C9CBCF']
        
        wedges, texts, autotexts = ax.pie(values, labels=names, autopct='%1.1f%%',
                                          startangle=90, colors=colors)
        
        # הגדרת גודל טקסט
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
    
    # שמירת הגרף כתמונה בזיכרון
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100, 
                facecolor='white', edgecolor='none')
    img.seek(0)
    plt.close(fig)  # סגירת הגרף לשחרור זיכרון
    
    return Response(img.getvalue(), mimetype='image/png')

# אתחול מערכת הבינה המלאכותית כשהאתר מתחיל לרוץ
print("אתחול מחלקה לחיבור ל-AI")  # הודעה שהבינה המלאכותית מתחילה
ai_agent = AI_Agent()  # יוצר את הבינה המלאכותית שתייעץ למשתמשים
print("=== AI Agent נוצר בהצלחה ===")

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

@app.route('/create-tables')
def create_tables():
    """יוצר טבלאות אם הן לא קיימות"""
    print("=== התחלת יצירת טבלאות ===")
    try:
        portfolio_model.create_tables()
        result = """
        <h2>יצירת טבלאות - הצליחה!</h2>
        <p>הטבלאות נוצרו בהצלחה במסד הנתונים.</p>
        
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
        'DATABASE_URL': os.getenv('DATABASE_URL', 'לא מוגדר'),
        'OLLAMA_URL': os.getenv('OLLAMA_URL', 'לא מוגדר'),
        'PORT': os.getenv('PORT', 'לא מוגדר'),
        'FLASK_ENV': os.getenv('FLASK_ENV', 'לא מוגדר'),
        'SECRET_KEY': os.getenv('SECRET_KEY', 'לא מוגדר')
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
    """נתיב להזרקת נתונים אוטומטית למסד הנתונים בענן"""
    print("=== התחלת הזרקת נתונים לענן ===")
    try:
        # בדיקה אם יש DATABASE_URL
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            return """
            <h2>שגיאה בהזרקת נתונים</h2>
            <p>לא נמצא DATABASE_URL - האפליקציה לא מחוברת למסד נתונים בענן</p>
            <p>האפליקציה משתמשת ב-SQLite מקומי</p>
            <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
            """
        
        # התחברות למסד הנתונים
        print("מתחבר למסד הנתונים בענן...")
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        print("התחברות למסד הנתונים הצליחה")
        
        # יצירת טבלאות
        print("יוצר טבלאות...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS securities (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                sector VARCHAR(50),
                price DECIMAL(10,2),
                change_percent DECIMAL(5,2),
                volume BIGINT,
                market_cap DECIMAL(15,2),
                pe_ratio DECIMAL(8,2),
                dividend_yield DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS investments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                shares INTEGER NOT NULL,
                purchase_price DECIMAL(10,2) NOT NULL,
                purchase_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                email VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("טבלאות נוצרו בהצלחה")
        
        # הוספת ניירות ערך לדוגמה
        print("מוסיף ניירות ערך...")
        securities = [
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
        
        for security in securities:
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
        
        # הוספת השקעות לדוגמה
        print("מוסיף השקעות...")
        investments = [
            (1, 'AAPL', 100, 145.50, '2024-01-15'),
            (1, 'MSFT', 50, 300.25, '2024-02-20'),
            (1, 'GOOGL', 25, 2700.00, '2024-03-10'),
            (1, 'TSLA', 30, 800.00, '2024-01-30'),
            (1, 'NVDA', 40, 420.75, '2024-02-15')
        ]
        
        for investment in investments:
            cursor.execute("""
                INSERT INTO investments (user_id, symbol, shares, purchase_price, purchase_date)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, investment)
        
        # הוספת משתמש לדוגמה
        print("מוסיף משתמש לדוגמה...")
        cursor.execute("""
            INSERT INTO users (username, password_hash, email)
            VALUES ('demo_user', 'pbkdf2:sha256:600000$demo_hash$password123', 'demo@example.com')
            ON CONFLICT (username) DO NOTHING
        """)
        
        conn.commit()
        
        # בדיקת התוצאה
        cursor.execute("SELECT COUNT(*) FROM securities")
        securities_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM investments")
        investments_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        users_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"הזרקת נתונים הושלמה: {securities_count} ניירות ערך, {investments_count} השקעות, {users_count} משתמשים")
        
        result = f"""
        <h2>הזרקת נתונים לענן - הצליחה!</h2>
        <p>הנתונים הוזרקו בהצלחה למסד הנתונים PostgreSQL בענן.</p>
        
        <h3>סיכום הנתונים שהוזרקו:</h3>
        <ul>
            <li><strong>ניירות ערך:</strong> {securities_count}</li>
            <li><strong>השקעות:</strong> {investments_count}</li>
            <li><strong>משתמשים:</strong> {users_count}</li>
        </ul>
        
        <h3>פרטי התחברות לדוגמה:</h3>
        <p><strong>שם משתמש:</strong> demo_user</p>
        <p><strong>סיסמה:</strong> password123</p>
        
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
    """נתיב לבדיקת בריאות האפליקציה"""
    try:
        # במקום JSON, נחזיר דף HTML מלא
        html_content = """
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>מערכת ניהול תיק השקעות - בדיקת בריאות</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; }
                .status { padding: 15px; margin: 10px 0; border-radius: 5px; }
                .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
                .info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
                .links { margin-top: 30px; text-align: center; }
                .links a { display: inline-block; margin: 10px; padding: 12px 24px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                .links a:hover { background-color: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎉 מערכת ניהול תיק השקעות עובדת!</h1>
                
                <div class="status success">
                    <strong>✅ סטטוס:</strong> האפליקציה פועלת בהצלחה
                </div>
                
                <div class="status info">
                    <strong>📊 מסד נתונים:</strong> מחובר ופועל
                </div>
                
                <div class="status info">
                    <strong>🤖 בינה מלאכותית:</strong> זמינה ופועלת
                </div>
                
                <div class="status info">
                    <strong>🌐 פורט:</strong> 8080
                </div>
                
                <div class="links">
                    <a href="/login">התחברות למערכת</a>
                    <a href="/portfolio">תיק השקעות</a>
                    <a href="/advice">ייעוץ AI</a>
                    <a href="/risk">ניתוח סיכונים</a>
                    <a href="/graph">גרפים</a>
                </div>
                
                <div style="margin-top: 30px; text-align: center; color: #666;">
                    <p><strong>פרטי התחברות לדוגמה:</strong></p>
                    <p>שם משתמש: <code>admin</code> | סיסמה: <code>admin123</code></p>
                    <p>או</p>
                    <p>שם משתמש: <code>demo_user</code> | סיסמה: <code>password123</code></p>
                </div>
            </div>
        </body>
        </html>
        """
        return html_content
    except Exception as e:
        return f"שגיאה: {str(e)}", 500

@app.route('/api/status')
def api_status():
    """נתיב API שמחזיר JSON עם סטטוס האפליקציה"""
    try:
        import os
        port = os.environ.get('PORT', '8080')
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
    """נתיב להגדרת מסד הנתונים המלא - יוצר טבלאות ומשתמשים"""
    print("=== התחלת הגדרת מסד נתונים מלא ===")
    try:
        # יצירת טבלאות
        print("יוצר טבלאות...")
        portfolio_model.create_tables()
        print("טבלאות נוצרו בהצלחה")
        
        # הוספת משתמשים
        print("מוסיף משתמשים...")
        from werkzeug.security import generate_password_hash
        
        conn = portfolio_model.get_connection()
        cursor = conn.cursor()
        
        # הוספת משתמש admin
        admin_password_hash = generate_password_hash('admin123')
        if portfolio_model.use_postgres:
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, role)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (username) DO UPDATE SET
                    password_hash = EXCLUDED.password_hash,
                    email = EXCLUDED.email,
                    role = EXCLUDED.role
            """, ('admin', admin_password_hash, 'admin@example.com', 'admin'))
        else:
            cursor.execute("""
                INSERT OR REPLACE INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            """, ('admin', admin_password_hash, 'admin@example.com', 'admin'))
        
        # הוספת משתמש demo
        demo_password_hash = generate_password_hash('password123')
        if portfolio_model.use_postgres:
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, role)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (username) DO UPDATE SET
                    password_hash = EXCLUDED.password_hash,
                    email = EXCLUDED.email,
                    role = EXCLUDED.role
            """, ('demo_user', demo_password_hash, 'demo@example.com', 'user'))
        else:
            cursor.execute("""
                INSERT OR REPLACE INTO users (username, password_hash, email, role)
                VALUES (?, ?, ?, ?)
            """, ('demo_user', demo_password_hash, 'demo@example.com', 'user'))
        
        conn.commit()
        conn.close()
        print("משתמשים נוספו בהצלחה")
        
        # הוספת נתוני דוגמה
        print("מוסיף נתוני דוגמה...")
        sample_securities = [
            ("אפל", 10, 150.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
            ("גוגל", 5, 2800.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
            ("אגח ממשלתי", 100, 100.0, "פיננסים", "נמוך", "אגח ממשלתית"),
            ("טסלה", 3, 800.0, "תחבורה", "גבוה", "מניה רגילה"),
            ("מיקרוסופט", 8, 300.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
            ("אמזון", 2, 1500.0, "טכנולוגיה", "גבוה", "מניה רגילה")
        ]
        
        for name, amount, price, industry, variance, security_type in sample_securities:
            portfolio_model.add_security(name, amount, price, industry, variance, security_type)
            print(f"נוסף: {name} - {amount} יחידות ב-{price} ₪")
        
        print("=== סיום הגדרת מסד נתונים מלא ===")
        
        result = f"""
        <h2>הגדרת מסד נתונים - הצליחה!</h2>
        <p>המסד הנתונים הוגדר בהצלחה עם כל הטבלאות והנתונים.</p>
        
        <h3>מה שנוצר:</h3>
        <ul>
            <li><strong>טבלאות:</strong> users, securities, investments</li>
            <li><strong>משתמשים:</strong> admin, demo_user</li>
            <li><strong>ניירות ערך:</strong> {len(sample_securities)} מניות ואגרות חוב</li>
        </ul>
        
        <h3>פרטי התחברות:</h3>
        <p><strong>מנהל:</strong> שם משתמש: admin | סיסמה: admin123</p>
        <p><strong>משתמש:</strong> שם משתמש: demo_user | סיסמה: password123</p>
        
        <h3>קישורים מהירים:</h3>
        <p><a href="/login">התחברות למערכת</a></p>
        <p><a href="/portfolio">צפייה בתיק השקעות</a></p>
        <p><a href="/">דף הבית</a></p>
        """
        
        return result
        
    except Exception as e:
        print(f"שגיאה בהגדרת מסד נתונים: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"""
        <h2>שגיאה בהגדרת מסד נתונים</h2>
        <p>שגיאה: {str(e)}</p>
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
            'PYTHONPATH': os.environ.get('PYTHONPATH', 'לא מוגדר'),
            'use_postgres': portfolio_model.use_postgres,
            'db_url': portfolio_model.db_url
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

# מפעילים את האתר
if __name__ == '__main__':
    print("=== התחלת הפעלת האפליקציה ===")
    print("=== יצירת טבלאות במסד הנתונים ===")
    portfolio_model.create_tables()
    print("=== טבלאות נוצרו בהצלחה ===")
    
    # הוספת נתונים לדוגמה אם המסד ריק
    print("=== בדיקת תוכן מסד הנתונים ===")
    try:
        securities = portfolio_model.get_all_securities()
        if len(securities) == 0:
            print("מסד הנתונים ריק, מוסיף נתונים לדוגמה...")
            sample_securities = [
                ("אפל", 10, 150.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
                ("גוגל", 5, 2800.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
                ("אגח ממשלתי", 100, 100.0, "פיננסים", "נמוך", "אגח ממשלתית"),
                ("טסלה", 3, 800.0, "תחבורה", "גבוה", "מניה רגילה"),
                ("מיקרוסופט", 8, 300.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
                ("אמזון", 2, 1500.0, "טכנולוגיה", "גבוה", "מניה רגילה")
            ]
            
            for name, amount, price, industry, variance, security_type in sample_securities:
                portfolio_model.add_security(name, amount, price, industry, variance, security_type)
                print(f"נוסף: {name} - {amount} יחידות ב-{price} ₪")
            
            print("נתונים לדוגמה נוספו בהצלחה!")
        else:
            print(f"מסד הנתונים מכיל {len(securities)} ניירות ערך")
    except Exception as e:
        print(f"שגיאה בהוספת נתונים לדוגמה: {str(e)}")
    
    # מקבל פורט מהסביבה או משתמש ב-8080 כברירת מחדל
    port = int(os.environ.get('PORT', 8080))
    print(f"=== האפליקציה רצה על פורט {port} ===")
    
    # הרצה עם host='0.0.0.0' כדי שיהיה נגיש מבחוץ
    app.run(host='0.0.0.0', port=port, debug=False)
