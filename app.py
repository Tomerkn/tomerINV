from flask import Flask, render_template, redirect, url_for, flash, Response, request
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

print("=== התחלת ייבוא ספריות ===")
print(f"=== בדיקת משתני סביבה ===")
print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"PORT: {os.environ.get('PORT')}")
print(f"OLLAMA_URL: {os.environ.get('OLLAMA_URL')}")
print(f"=== סיום בדיקת משתני סביבה ===")

# מביאים הקלסים שיצרנו בקבצים אחרים
print("=== התחלת ייבוא dbmodel ===")
from dbmodel import PortfolioModel
print("=== סיום ייבוא dbmodel ===")

print("=== התחלת ייבוא portfolio_controller ===")
from portfolio_controller import PortfolioController, RiskManager
print("=== סיום ייבוא portfolio_controller ===")

print("=== התחלת ייבוא securities ===")
from securities import Stock, Bond
print("=== סיום ייבוא securities ===")

print("=== התחלת ייבוא ollamamodel ===")
from ollamamodel import AI_Agent
print("=== סיום ייבוא ollamamodel ===")

print("=== התחלת ייבוא broker ===")
import broker
print("=== סיום ייבוא broker ===")

print("=== התחלת טעינת האפליקציה ===")

plt.rcParams['font.family'] = ['Arial']  # הגדרת פונט שתומך בעברית

# הוספת לוגים מפורטים
logging.basicConfig(level=logging.DEBUG)
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
USD_TO_ILS_RATE = 3.5
print(f"=== קבוע המרה מוגדר: {USD_TO_ILS_RATE} ===")

# פונקציית עזר להמיר מדולר לשקל
def usd_to_ils(usd_price):
    """מחזיר מחיר בשקלים מתוך מחיר בדולרים"""
    return usd_price * USD_TO_ILS_RATE

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
    for user in USERS.values():  # עובר על כל המשתמשים ברשימה
        if user.id == user_id:  # אם מצא משתמש עם מספר הזיהוי הנכון
            return user  # מחזיר את המשתמש
    return None  # אם לא מצא משתמש, מחזיר ריק

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
portfolio_model = PortfolioModel()  # יוצר את מסד הנתונים
print("PortfolioModel נוצר בהצלחה")
print("=== סיום יצירת PortfolioModel ===")

print("=== התחלת יצירת PortfolioController ===")
portfolio_controller = PortfolioController(portfolio_model)  # יוצר את הקונטרולר שמנהל הכל
print("PortfolioController נוצר בהצלחה")
print("=== סיום יצירת PortfolioController ===")

print("=== התחלת יצירת AI_Agent ===")
ai_agent = AI_Agent()  # יוצר את הסוכן הבינה המלאכותית
print("=== AI Agent נוצר בהצלחה ===")

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
        print("=== התחלת פונקציית index ===")
        print(f"משתמש מחובר: {current_user.is_authenticated}")
        if current_user.is_authenticated:
            print(f"שם משתמש: {current_user.username}")
            print(f"תפקיד: {current_user.role}")
        
        # וודא שמסד הנתונים נוצר
        print("יוצר טבלאות במסד הנתונים...")
        portfolio_model.create_tables()
        print("טבלאות נוצרו בהצלחה")
        
        print("מקבל נתוני תיק...")
        portfolio = portfolio_controller.get_portfolio()  # מקבל את כל ניירות הערך בתיק
        print(f"מספר ניירות ערך בתיק: {len(portfolio)}")
        
        # מחשב את הערך הכולל של התיק על ידי כפל מחיר בכמות לכל נייר ערך
        total_value = sum(item['price'] * item['amount'] for item in portfolio)
        print(f"ערך כולל של התיק: {total_value}")
        
        print("מציג דף הבית")
        return render_template('index.html', portfolio=portfolio, total_value=total_value)  # מציג את דף הבית עם הנתונים
    except Exception as e:
        print(f"שגיאה בדף הבית: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('שגיאה בטעינת דף הבית. אנא נסה שוב.', 'danger')
        return render_template('error.html', error="שגיאה בטעינת דף הבית")

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
        price = broker.Broker.update_price(symbol)
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
            broker.Broker.update_price(item['name'])
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
    logger.error(f"שגיאה כללית: {str(e)}")
    import traceback
    logger.error(f"פרטי השגיאה: {traceback.format_exc()}")
    return render_template('error.html', error="שגיאה לא צפויה"), 500

@app.route('/test')
def test():
    """נתיב בדיקה פשוט"""
    print("=== התחלת פונקציית test ===")
    print("מישהו התחבר לנתיב הבדיקה")
    print("=== סיום פונקציית test ===")
    return "האפליקציה עובדת! 🎉"

@app.route('/dbtest')
def dbtest():
    """נתיב בדיקה למסד הנתונים - מראה אילו טבלאות קיימות"""
    print("=== התחלת פונקציית dbtest ===")
    try:
        print("מתחבר למסד הנתונים...")
        conn = portfolio_model.get_connection()
        cursor = conn.cursor()
        
        print("בודק אילו טבלאות קיימות...")
        if portfolio_model.use_postgres:
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        else:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        
        tables = cursor.fetchall()
        conn.close()
        
        print(f"נמצאו {len(tables)} טבלאות")
        result = f"<h2>בדיקת מסד נתונים</h2>"
        result += f"<p><strong>סוג מסד:</strong> {'PostgreSQL' if portfolio_model.use_postgres else 'SQLite'}</p>"
        result += f"<p><strong>כתובת:</strong> {portfolio_model.db_url}</p>"
        result += f"<p><strong>מספר טבלאות:</strong> {len(tables)}</p>"
        result += f"<p><strong>טבלאות:</strong></p><ul>"
        
        for table in tables:
            table_name = table[0] if isinstance(table, tuple) else table
            result += f"<li>{table_name}</li>"
        
        result += "</ul>"
        print("=== סיום פונקציית dbtest ===")
        return result
        
    except Exception as e:
        print(f"שגיאה בבדיקת מסד: {str(e)}")
        return f"<h2>שגיאה בבדיקת מסד נתונים</h2><p>שגיאה: {str(e)}</p>"

@app.route('/create-tables')
def create_tables():
    """נתיב שיוצר טבלאות במסד הנתונים"""
    print("=== התחלת פונקציית create_tables ===")
    try:
        print("יוצר טבלאות במסד הנתונים...")
        portfolio_model.create_tables()
        print("טבלאות נוצרו בהצלחה")
        return "<h2>יצירת טבלאות</h2><p>הטבלאות נוצרו בהצלחה! 🎉</p><p><a href='/dbtest'>בדוק טבלאות</a></p>"
    except Exception as e:
        print(f"שגיאה ביצירת טבלאות: {str(e)}")
        return f"<h2>שגיאה ביצירת טבלאות</h2><p>שגיאה: {str(e)}</p>"

@app.route('/add-sample-data')
def add_sample_data():
    """נתיב שמוסיף נתונים לדוגמה למסד הנתונים"""
    print("=== התחלת פונקציית add_sample_data ===")
    try:
        print("מוסיף נתונים לדוגמה...")
        
        # יוצר כמה מניות לדוגמה
        sample_securities = [
            ("אפל", 10, 150.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
            ("גוגל", 5, 2800.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
            ("אגח ממשלתי", 100, 100.0, "פיננסים", "נמוך", "אגח ממשלתית"),
            ("טסלה", 3, 800.0, "תחבורה", "גבוה", "מניה רגילה"),
            ("מיקרוסופט", 8, 300.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
            ("אמזון", 2, 1500.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
            ("ניוטלה", 15, 50.0, "מזון", "בינוני", "מניה רגילה"),
            ("פייסבוק", 12, 200.0, "טכנולוגיה", "גבוה", "מניה רגילה"),
            ("נטפליקס", 6, 400.0, "בידור", "גבוה", "מניה רגילה"),
            ("אגח קונצרנית", 50, 120.0, "פיננסים", "נמוך", "אגח קונצרנית")
        ]
        
        added_count = 0
        for name, amount, price, industry, variance, security_type in sample_securities:
            try:
                portfolio_model.add_security(name, amount, price, industry, variance, security_type)
                print(f"נוסף: {name}")
                added_count += 1
            except Exception as e:
                print(f"שגיאה בהוספת {name}: {str(e)}")
        
        print(f"נתונים לדוגמה נוספו בהצלחה! נוספו {added_count} ניירות ערך")
        
        # בודק את התוכן הסופי
        all_securities = portfolio_model.get_all_securities()
        
        result = f"""
        <h2>✅ הוספת נתונים לדוגמה - הצליחה!</h2>
        <p>נוספו {added_count} ניירות ערך למסד הנתונים.</p>
        <p>סה"כ ניירות ערך במסד: {len(all_securities)}</p>
        
        <h3>ניירות ערך שנוספו:</h3>
        <ul>
        {''.join([f'<li>{sec["name"]} - {sec["amount"]} יחידות ב-{sec["price"]} ₪ ({sec["industry"]})</li>' for sec in all_securities])}
        </ul>
        
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        <p><a href="/portfolio">צפייה בתיק השקעות</a></p>
        """
        
        return result
        
    except Exception as e:
        print(f"שגיאה בהוספת נתונים: {str(e)}")
        return f"""
        <h2>❌ שגיאה בהוספת נתונים</h2>
        <p>שגיאה: {str(e)}</p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

@app.route('/db-admin')
def db_admin():
    """נתיב ראשי לניהול מסד הנתונים"""
    print("=== התחלת פונקציית db_admin ===")
    
    html = """
    <h1>🗄️ ניהול מסד נתונים</h1>
    <p>ברוכים הבאים לניהול מסד הנתונים של האפליקציה!</p>
    
    <h2>🔧 פעולות זמינות:</h2>
    <ul>
        <li><a href="/test">✅ בדיקת האפליקציה</a> - בודק שהאפליקציה עובדת</li>
        <li><a href="/connection-test">🔌 בדיקת חיבור מפורטת</a> - בודק חיבור למסד הנתונים</li>
        <li><a href="/dbtest">📋 בדיקת מסד נתונים</a> - מראה אילו טבלאות קיימות</li>
        <li><a href="/db-status">📊 סטטוס מסד נתונים</a> - מראה תוכן המסד</li>
        <li><a href="/create-tables">🏗️ יצירת טבלאות</a> - יוצר טבלאות אם הן לא קיימות</li>
        <li><a href="/add-sample-data">➕ הוספת נתונים לדוגמה</a> - מוסיף מניות לדוגמה</li>
        <li><a href="/ollama-test">🤖 בדיקת Ollama</a> - בודק חיבור לבינה מלאכותית</li>
        <li><a href="/env-test">⚙️ בדיקת משתני סביבה</a> - מראה משתני סביבה</li>
    </ul>
    
    <h2>📈 מידע על המסד:</h2>
    <p><strong>סוג מסד:</strong> {}</p>
    <p><strong>כתובת:</strong> {}</p>
    
    <h2>🚀 קישורים מהירים:</h2>
    <p><a href="/portfolio">📈 צפייה בתיק השקעות</a></p>
    <p><a href="/">🏠 דף הבית</a></p>
    """.format(
        'PostgreSQL' if portfolio_model.use_postgres else 'SQLite',
        portfolio_model.db_url
    )
    
    print("=== סיום פונקציית db_admin ===")
    return html

@app.route('/ollama-test')
def ollama_test():
    """בדיקת חיבור ל-Ollama"""
    try:
        print("=== בדיקת חיבור ל-Ollama ===")
        ollama_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        print(f"מנסה להתחבר ל-Ollama ב: {ollama_url}")
        
        # בדיקה פשוטה אם השרת זמין
        response = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if response.status_code == 200:
            return f"✅ Ollama זמין ב-{ollama_url}<br>תגובה: {response.text[:200]}..."
        else:
            return f"❌ Ollama לא זמין ב-{ollama_url}<br>סטטוס: {response.status_code}"
    except Exception as e:
        return f"❌ שגיאה בחיבור ל-Ollama: {str(e)}"

@app.route('/env-test')
def env_test():
    """בדיקת משתני סביבה"""
    print("=== בדיקת משתני סביבה ===")
    env_vars = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'PORT': os.environ.get('PORT'),
        'OLLAMA_URL': os.environ.get('OLLAMA_URL'),
        'RAILWAY_ENVIRONMENT': os.environ.get('RAILWAY_ENVIRONMENT'),
        'RAILWAY_PROJECT_ID': os.environ.get('RAILWAY_PROJECT_ID')
    }
    
    result = "<h2>משתני סביבה:</h2>"
    for key, value in env_vars.items():
        if value:
            result += f"<p><strong>{key}:</strong> {value}</p>"
        else:
            result += f"<p><strong>{key}:</strong> <span style='color: red;'>לא מוגדר</span></p>"
    
    return result

@app.route('/db-status')
def db_status():
    """בדיקת סטטוס מסד הנתונים"""
    try:
        print("=== בדיקת סטטוס מסד הנתונים ===")
        securities = portfolio_model.get_all_securities()
        
        # מחשב ערך כולל
        total_value = sum(sec['price'] * sec['amount'] for sec in securities)
        
        result = f"""
        <h2>📊 סטטוס מסד הנתונים</h2>
        <p><strong>סוג מסד:</strong> {'PostgreSQL' if portfolio_model.use_postgres else 'SQLite'}</p>
        <p><strong>כתובת:</strong> {portfolio_model.db_url}</p>
        <p><strong>מספר ניירות ערך:</strong> {len(securities)}</p>
        <p><strong>ערך כולל:</strong> {total_value:.2f} ₪</p>
        
        <h3>ניירות ערך במסד:</h3>
        """
        
        if len(securities) > 0:
            result += "<ul>"
            for sec in securities:
                value = sec['price'] * sec['amount']
                result += f'<li><strong>{sec["name"]}</strong> - {sec["amount"]} יחידות ב-{sec["price"]} ₪ (ערך: {value:.2f} ₪) - {sec["industry"]}</li>'
            result += "</ul>"
        else:
            result += "<p><em>אין ניירות ערך במסד הנתונים</em></p>"
            result += "<p><a href='/add-sample-data'>הוסף נתונים לדוגמה</a></p>"
        
        result += """
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        <p><a href="/portfolio">צפייה בתיק השקעות</a></p>
        """
        
        return result
        
    except Exception as e:
        return f"""
        <h2>❌ שגיאה בבדיקת מסד הנתונים</h2>
        <p>שגיאה: {str(e)}</p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

@app.route('/connection-test')
def connection_test():
    """בדיקת חיבור מפורטת למסד הנתונים"""
    print("=== בדיקת חיבור מפורטת למסד הנתונים ===")
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
        <h2>✅ בדיקת חיבור למסד הנתונים - הצליחה!</h2>
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
        
        print("=== סיום בדיקת חיבור מפורטת ===")
        return result
        
    except Exception as e:
        print(f"שגיאה בבדיקת חיבור: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"""
        <h2>❌ שגיאה בבדיקת חיבור למסד הנתונים</h2>
        <p><strong>סוג מסד:</strong> {'PostgreSQL' if portfolio_model.use_postgres else 'SQLite'}</p>
        <p><strong>כתובת:</strong> {portfolio_model.db_url}</p>
        <p><strong>שגיאה:</strong> {str(e)}</p>
        <p><a href="/db-admin">חזרה לניהול מסד נתונים</a></p>
        """

print("=== כל הנתיבים נרשמו בהצלחה ===")
print("=== האפליקציה מוכנה להפעלה ===")
print("=== סיום טעינת האפליקציה ===")

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
    
    # מקבל פורט מהסביבה או משתמש ב-4000 כברירת מחדל
    port = int(os.environ.get('PORT', 4000))
    print(f"=== האפליקציה רצה על פורט {port} ===")
    
    # הרצה עם host='0.0.0.0' כדי שיהיה נגיש מבחוץ
    app.run(host='0.0.0.0', port=port, debug=False)
