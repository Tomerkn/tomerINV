# ייבוא ספריות Flask לבניית אפליקציית הווב
from flask import Flask, render_template, redirect, url_for, flash, Response, request, jsonify
# ייבוא ספריות לניהול משתמשים והתחברות
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# ייבוא ספריות לטפסים ואימות נתונים
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange
# ייבוא decorator לאבטחת פונקציות
from functools import wraps
# ייבוא ספריות מערכת ויומנים
import logging
import os
import sys
import io
# ייבוא ספרייה ליצירת גרפים
import matplotlib
matplotlib.use('Agg')  # הגדרת backend לשרת (ללא GUI)
import matplotlib.pyplot as plt

# ייבוא מודלים מקומיים - מסד נתונים ובינה מלאכותית
try:
    from dbmodel import PortfolioModel, Broker  # מסד נתונים ומחירי מניות
    print("ייבוא dbmodel הצליח")
except Exception as e:
    print(f" שגיאה בייבוא dbmodel: {str(e)}")
    sys.exit(1)  # יציאה מהתוכנית בשל שגיאה קריטית

try:
    from ollamamodel import AI_Agent  # מודל הבינה המלאכותית לייעוץ השקעות
    print(" ייבוא Ollama הצליח")
except ImportError:
    # Fallback לOllama - מחלקה חלופית אם AI לא זמין
    class AI_Agent:
        def __init__(self):
            self.model = "llama3.1:8b"
            self.ollama_available = False
        
        def get_advice(self, portfolio_data=None):
            # ייעוץ השקעות בסיסי כשאין AI
            return """ייעוץ השקעות בסיסי:
1. פיזור השקעות - השקע בענפים שונים
2. השקעה לטווח ארוך - סבלנות היא מפתח  
3. מחקר לפני השקעה - הכר את החברות
4. ניהול סיכונים - השקע רק מה שאתה יכול להפסיד"""

# הגדרות בסיסיות של האפליקציה
logging.basicConfig(level=logging.INFO)  # הגדרת רמת יומן למידע
logger = logging.getLogger(__name__)  # יצירת logger לקובץ זה

app = Flask(__name__)  # יצירת אפליקציית Flask
# מפתח אבטחה מאובטח לשרת או מקומי
app.secret_key = os.environ.get('SECRET_KEY', 'local-portfolio-secret-key-2024')

# הגדרת מערכת התחברות Flask-Login
login_manager = LoginManager(app)  # יצירת מנהל התחברות
login_manager.login_view = 'login'  # דף ברירת מחדל להתחברות
login_manager.login_message = 'אנא התחבר כדי לגשת לדף זה'  # הודעה לגישה מוגבלת
login_manager.login_message_category = 'warning'  # סוג ההודעה לעיצוב

# הוספת פילטר עזר לעיצוב בתבניות Jinja2
@app.template_filter('nl2br')
def nl2br_filter(text):
    """מחליף קפיצות שורה ב-<br> tags לתצוגה נכונה ב-HTML"""
    if text is None:
        return ''
    return text.replace('\n', '<br>\n')

# רישום הפילטר במנוע התבניות
app.jinja_env.filters['nl2br'] = nl2br_filter

# מערכת Cache פשוטה לשיפור ביצועים
portfolio_cache = {
    'data': None,  # נתוני התיק
    'last_update': None,  # זמן עדכון אחרון
    'cache_duration': 30  # תוקף ה-cache בשניות
}

def get_cached_portfolio():
    """מחזיר נתוני תיק מה-cache או טוען מחדש מהמסד"""
    import time
    
    current_time = time.time()  # זמן נוכחי
    
    # בדיקה אם הcache תקף או שצריך לרענן
    if (portfolio_cache['data'] is None or 
        portfolio_cache['last_update'] is None or 
        current_time - portfolio_cache['last_update'] > portfolio_cache['cache_duration']):
        
        try:
            # טעינת נתונים טריים מהמסד
            portfolio_cache['data'] = portfolio_model.get_all_securities()
            portfolio_cache['last_update'] = current_time
            print(f"נתוני תיק נטענו מחדש - {len(portfolio_cache['data'])} ניירות ערך")
        except Exception as e:
            print(f"שגיאה בטעינת נתוני תיק: {str(e)}")
            # שימוש ב-cache ישן אם יש שגיאה
            if portfolio_cache['data'] is not None:
                print("משתמש בנתונים מהקיים")
            else:
                portfolio_cache['data'] = []
    
    return portfolio_cache['data']

def clear_portfolio_cache():
    """מנקה את הcache לאחר עדכון נתונים"""
    portfolio_cache['data'] = None
    portfolio_cache['last_update'] = None
    print("קיים תיק נוקה")

# קבועים גלובליים
CONVERSION_RATE = 3.5  # שער המרה מדולר לשקל

# מחלקת User למערכת ההזדהות
class User(UserMixin):
    """מחלקה המייצגת משתמש במערכת - תואמת ל-Flask-Login"""
    def __init__(self, id, username, password_hash, role='user'):
        self.id = id  # מזהה ייחודי של המשתמש
        self.username = username  # שם המשתמש
        self.password_hash = password_hash  # סיסמה מוצפנת
        self.role = role  # תפקיד המשתמש (user/admin)
    
    def check_password(self, password):
        """בדיקת סיסמה פשוטה - בפרויקט אמיתי היינו משתמשים בהצפנה"""
        return self.password_hash == password
    
    def is_admin(self):
        """בדיקה אם המשתמש הוא מנהל"""
        return self.role == 'admin'

@login_manager.user_loader
def load_user(user_id):
    """פונקציה נדרשת ל-Flask-Login - טוענת משתמש לפי ID"""
    try:
        if 'portfolio_model' in globals():  # בדיקה שהמודל קיים
            user_data = portfolio_model.get_user_by_id(int(user_id))
            if user_data:
                return User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    role=user_data.get('role', 'user')
                )
    except Exception as e:
        logger.error(f"שגיאה בטעינת משתמש: {str(e)}")
    return None

# דקורטור לבדיקת הרשאות מנהל
def admin_required(f):
    """דקורטור המוודא שרק מנהל יכול לגשת לפונקציה"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('גישה נדחתה - נדרשות הרשאות מנהל', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# יצירת מופעי המודלים הראשיים
try:
    portfolio_model = PortfolioModel()  # מסד הנתונים
    print("PortfolioModel נוצר בהצלחה")
except Exception as e:
    print(f"שגיאה ביצירת PortfolioModel: {str(e)}")
    sys.exit(1)

try:
    ai_agent = AI_Agent()  # הבינה המלאכותית
    print("AI_Agent נוצר בהצלחה")
except Exception as e:
    print(f"AI_Agent לא זמין: {str(e)}")
    ai_agent = None

# טפסים (Forms) - שכבת ה-View
class LoginForm(FlaskForm):
    """טופס התחברות למערכת"""
    username = StringField('שם משתמש', validators=[DataRequired()])
    password = PasswordField('סיסמה', validators=[DataRequired()])
    submit = SubmitField('התחבר')

class SecurityForm(FlaskForm):
    """טופס בסיסי להוספת נייר ערך """
    # רשימת מניות פופולריות מ-S&P 500
    sp500_stocks = [
        ("AAPL", "Apple Inc"), ("MSFT", "Microsoft Corp"), ("GOOG", "Alphabet Inc"), 
        ("AMZN", "Amazon.com Inc"), ("META", "Meta Platforms Inc"), ("NVDA", "NVIDIA Corp"),
        ("TSLA", "Tesla Inc"), ("JPM", "JPMorgan Chase"), ("V", "Visa Inc"), ("MA", "Mastercard Inc")
    ]
    
    # רשימה נפתחת לבחירת מניה
    stock_dropdown = SelectField('בחר מניה', choices=[('', '--- בחר מניה ---')] + sp500_stocks, default='')
    name = StringField('שם נייר הערך', validators=[DataRequired()])
    amount = FloatField('כמות', validators=[DataRequired()])
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
    submit = SubmitField('הוסף')

class AddSecurityForm(FlaskForm):
    """טופס מפורט להוספת נייר ערך - כולל מניות S&P 500 ואגרות חוב"""
    # רשימה מקיפה של מניות S&P 500 הפופולריות ביותר מקובצות לפי ענפים
    sp500_stocks = [
        ('', '--- בחר מניה ---'),
        # טכנולוגיה - המניות הגדולות ביותר
        ("AAPL", "Apple Inc"), ("MSFT", "Microsoft Corp"), ("GOOG", "Alphabet Inc"), 
        ("AMZN", "Amazon.com Inc"), ("META", "Meta Platforms Inc"), ("NVDA", "NVIDIA Corp"),
        ("TSLA", "Tesla Inc"), ("ADBE", "Adobe Inc"), ("CRM", "Salesforce Inc"), 
        ("NFLX", "Netflix Inc"), ("ORCL", "Oracle Corp"), ("CSCO", "Cisco Systems"),
        ("INTC", "Intel Corp"), ("QCOM", "Qualcomm Inc"), ("IBM", "IBM Corp"),
        ("PYPL", "PayPal Holdings"), ("AVGO", "Broadcom Inc"), ("TXN", "Texas Instruments"),
        ("AMD", "Advanced Micro Devices"), ("AMAT", "Applied Materials"),
        
        # פיננסים - בנקאות ושירותים פיננסיים
        ("JPM", "JPMorgan Chase"), ("V", "Visa Inc"), ("MA", "Mastercard Inc"),
        ("BAC", "Bank of America"), ("WFC", "Wells Fargo"), ("MS", "Morgan Stanley"),
        ("SCHW", "Charles Schwab"), ("SPGI", "S&P Global"), ("BLK", "BlackRock Inc"),
        ("GS", "Goldman Sachs"), ("AXP", "American Express"), ("COF", "Capital One"),
        
        # בריאות - תרופות וציוד רפואי
        ("UNH", "UnitedHealth Group"), ("LLY", "Eli Lilly"), ("ABBV", "AbbVie Inc"),
        ("MRK", "Merck & Co"), ("ABT", "Abbott Labs"), ("TMO", "Thermo Fisher"),
        ("AMGN", "Amgen Inc"), ("MDT", "Medtronic plc"), ("PFE", "Pfizer Inc"),
        ("DHR", "Danaher Corp"), ("BMY", "Bristol Myers Squibb"), ("GILD", "Gilead Sciences"),
        
        # צריכה ויומיום
        ("WMT", "Walmart Inc"), ("PG", "Procter & Gamble"), ("HD", "Home Depot"),
        ("COST", "Costco Wholesale"), ("PEP", "PepsiCo Inc"), ("KO", "Coca-Cola Co"),
        ("MCD", "McDonald's Corp"), ("NKE", "Nike Inc"), ("LOW", "Lowe's Cos"),
        ("SBUX", "Starbucks Corp"), ("TGT", "Target Corp"), ("DIS", "Walt Disney Co"),
        
        # אנרגיה ותעשייה
        ("XOM", "Exxon Mobil"), ("CVX", "Chevron Corp"), ("NEE", "NextEra Energy"),
        ("LIN", "Linde plc"), ("HON", "Honeywell Intl"), ("RTX", "RTX Corp"),
        ("CAT", "Caterpillar Inc"), ("DE", "Deere & Co"), ("MMM", "3M Company"),
        ("GE", "General Electric"), ("BA", "Boeing Co"), ("LMT", "Lockheed Martin"),
        
        # תחבורה ולוגיסטיקה
        ("UPS", "United Parcel Service"), ("FDX", "FedEx Corp"), ("UNP", "Union Pacific"),
        ("CSX", "CSX Corp"), ("NSC", "Norfolk Southern"), ("DAL", "Delta Air Lines"),
        ("AAL", "American Airlines"), ("UAL", "United Airlines"), ("LUV", "Southwest Airlines"),
        
        # נדלן
        ("PLD", "Prologis Inc"), ("AMT", "American Tower"), ("CCI", "Crown Castle"),
        ("EQIX", "Equinix Inc"), ("SPG", "Simon Property Group"), ("O", "Realty Income Corp"),
        ("PSA", "Public Storage"), ("EXR", "Extended Stay America"), ("VTR", "Ventas Inc"),
        
        # תקשורת ומדיה
        ("VZ", "Verizon Communications"), ("T", "AT&T Inc"), ("CMCSA", "Comcast Corp"),
        ("CHTR", "Charter Communications"), ("TMUS", "T-Mobile US"), ("DISH", "DISH Network"),
        
        # חומרים וכימיה
        ("APD", "Air Products & Chemicals"), ("SHW", "Sherwin-Williams"), ("ECL", "Ecolab Inc"),
        ("FCX", "Freeport-McMoRan"), ("NEM", "Newmont Corp"), ("DD", "DuPont de Nemours"),
        
        # שירותי אוכל ומסעדות
        ("YUM", "Yum! Brands"), ("QSR", "Restaurant Brands International"), ("DPZ", "Domino's Pizza"),
        ("CMG", "Chipotle Mexican Grill"), ("DNKN", "Dunkin' Brands"),
        
        # קמעונאות
        ("AMZN", "Amazon.com Inc"), ("EBAY", "eBay Inc"), ("ETSY", "Etsy Inc"),
        
        # ביטוח
        ("BRK-B", "Berkshire Hathaway"), ("PRU", "Prudential Financial"), ("AIG", "American International Group"),
        ("MET", "MetLife Inc"), ("ALL", "Allstate Corp"), ("TRV", "Travelers Companies"),
        
        # אגרות חוב וחלופות
        ("", "--- אגרות חוב ---"),
        ("TLT", "אגח ממשלתי ארוך טווח"), ("IEF", "אגח ממשלתי בינוני טווח"), 
        ("SHY", "אגח ממשלתי קצר טווח"), ("LQD", "iShares iBoxx $ Investment Grade Corporate Bond ETF"),
        ("HYG", "אגח קונצרני תשואה גבוהה"), ("EMB", "אגח שווקים מתפתחים")
    ]
    
    # שדות הטופס עם אימותים
    stock_dropdown = SelectField('בחר מניה או נייר ערך', choices=sp500_stocks, default='')
    name = StringField('שם נייר הערך', validators=[DataRequired()], 
                      render_kw={"placeholder": "שם החברה יתמלא אוטומטית"})
    amount = IntegerField('כמות', validators=[DataRequired(), NumberRange(min=1)], 
                         render_kw={"placeholder": "מספר היחידות"})
    industry = StringField('ענף', validators=[DataRequired()], 
                          render_kw={"placeholder": "טכנולוגיה, בנקאות, וכו'"})
    variance = FloatField('סטיית תקן', validators=[DataRequired(), NumberRange(min=0)], 
                         render_kw={"placeholder": "רמת הסיכון"})
    security_type = SelectField('סוג נייר ערך', 
                               choices=[('מניה', 'מניה'), ('אגח ממשלתית', 'אגח ממשלתית'), ('אגח קונצרנית', 'אגח קונצרנית')],
                               default='מניה')
    submit = SubmitField('הוסף נייר ערך')

# Controllers (Routes) - הלוגיקה העיקרית של האפליקציה

@app.route('/simple-login', methods=['GET', 'POST'])
def simple_login():
    """דף התחברות פשוט ללא CSRF - לבדיקות מהירות"""
    try:
        if current_user.is_authenticated:  # אם כבר מחובר
            return redirect(url_for('portfolio'))
        
        if request.method == 'POST':  # אם זה בקשת התחברות
            username = request.form.get('username')
            password = request.form.get('password')
            
            print(f"ניסיון התחברות פשוט: {username}")
            
            user_data = portfolio_model.get_user_by_username(username)
            
            if user_data:  # אם המשתמש קיים
                user = User(
                    id=user_data['id'],
                    username=user_data['username'],
                    password_hash=user_data['password_hash'],
                    role=user_data.get('role', 'user')
                )
                
                if user.check_password(password):  # אם הסיסמה נכונה
                    login_user(user)
                    print("התחברות הצליחה!")
                    return redirect(url_for('portfolio'))
                else:
                    flash('שם משתמש או סיסמה שגויים', 'danger')
            else:
                flash('שם משתמש או סיסמה שגויים', 'danger')
        
        return '''
        <!DOCTYPE html>
        <html lang="he" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <title>התחברות פשוטה</title>
            <style>
                body { font-family: Arial; text-align: center; margin-top: 100px; }
                .form { max-width: 300px; margin: 0 auto; }
                input { width: 100%; padding: 10px; margin: 10px 0; }
                button { width: 100%; padding: 15px; background: #007bff; color: white; border: none; }
            </style>
        </head>
        <body>
            <div class="form">
                <h2>התחברות למערכת</h2>
                <form method="POST">
                    <input type="text" name="username" placeholder="שם משתמש" required>
                    <input type="password" name="password" placeholder="סיסמה" required>
                    <button type="submit">התחבר</button>
                </form>
                <p>admin/admin או user/user</p>
            </div>
        </body>
        </html>
        '''
    except Exception as e:
        return f"שגיאה: {str(e)}"

@app.route('/simple-login-post', methods=['POST'])
def simple_login_post():
    """טיפול בהתחברות פשוטה - גרסה חלופית"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')
        
        user_data = portfolio_model.get_user_by_username(username)
        
        if user_data and user_data['password_hash'] == password:
            user = User(
                id=user_data['id'],
                username=user_data['username'],
                password_hash=user_data['password_hash'],
                role=user_data.get('role', 'user')
            )
            login_user(user)
            return redirect(url_for('portfolio'))
        else:
            return redirect(url_for('simple_login'))
    except Exception as e:
        return f"שגיאה: {str(e)}"

@app.route('/login', methods=['GET', 'POST'])
def login():
    """דף התחברות ראשי עם אבטחה מלאה"""
    try:
        if current_user.is_authenticated:  # אם כבר מחובר
            print("משתמש כבר מחובר, מפנה לדף הבית")
            return redirect(url_for('index'))
        
        # יצירת טבלאות ומשתמשי ברירת מחדל במידת הצורך
        print("יוצר טבלאות במסד הנתונים...")
        portfolio_model.create_tables()
        print("טבלאות נוצרו בהצלחה")
        
        print("יוצר משתמשי ברירת מחדל...")
        portfolio_model.create_default_users()
        print("משתמשי ברירת מחדל נוצרו בהצלחה")
        
        form = LoginForm()  # יצירת טופס התחברות
        
        if request.method == 'POST':  # טיפול בבקשת התחברות
            print(f"שיטת הבקשה: POST")
            if form.validate_on_submit():  # אימות הטופס
                username = form.username.data
                password = form.password.data
                
                print(f"ניסיון התחברות עם שם משתמש: {username}")
                
                user_data = portfolio_model.get_user_by_username(username)
                
                print(f"משתמש נמצא במסד: {user_data is not None}")
                
                if user_data:  # אם המשתמש קיים
                    user = User(
                        id=user_data['id'],
                        username=user_data['username'],
                        password_hash=user_data['password_hash'],
                        role=user_data.get('role', 'user')
                    )
                    
                    if user.check_password(password):  # אם הסיסמה נכונה
                        print("סיסמה נכונה, מתחבר...")
                        login_user(user)
                        print("התחברות הצליחה")
                        next_page = request.args.get('next')  # דף הבא לאחר התחברות
                        return redirect(next_page) if next_page else redirect(url_for('index'))
                    else:
                        print("סיסמה שגויה")
                        flash('שם משתמש או סיסמה שגויים', 'danger')
                else:
                    print("משתמש לא נמצא")
                    flash('שם משתמש או סיסמה שגויים', 'danger')
            else:
                print("טופס לא תקין")
                for field, errors in form.errors.items():
                    for error in errors:
                        print(f"שגיאה ב-{field}: {error}")
                        flash(f'שגיאה ב-{field}: {error}', 'danger')
        else:
            print(f"שיטת הבקשה: GET")
        
        print("מציג דף כניסה")
        return render_template('login.html', form=form)
    except Exception as e:
        logger.error(f"שגיאה בפונקציית login: {str(e)}")
        flash('שגיאה פנימית בשרת. אנא נסה שוב מאוחר יותר.', 'danger')
        return render_template('login.html', form=LoginForm())

@app.route('/logout')
@login_required
def logout():
    """יציאה מהמערכת"""
    logout_user()  # ניתוק המשתמש
    return redirect(url_for('login'))

@app.route('/')
def index():
    """דף הבית - מציג סיכום התיק או מפנה להתחברות"""
    if current_user.is_authenticated:  # אם המשתמש מחובר
        try:
            # טעינה מהירה של נתוני התיק מה-cache
            portfolio_data = portfolio_model.get_all_securities()
            
            # התחלת טעינת ייעוץ AI ברקע לשיפור ביצועים
            start_background_ai_advice(portfolio_data)
            
            # אם יש הרבה ניירות ערך, הצג רק סיכום
            if len(portfolio_data) > 10:
                total_assets = sum(security['price'] * security['amount'] for security in portfolio_data)
                asset_count = len(portfolio_data)
                
                # הצג רק 5 המניות היקרות ביותר לדמו
                top_securities = sorted(portfolio_data, key=lambda x: x['price'] * x['amount'], reverse=True)[:5]
                
                return render_template('index.html', 
                                     portfolio=top_securities, 
                                     total_value=total_assets,
                                     asset_count=asset_count,
                                     show_summary=True)
            else:
                # אם יש מעט ניירות ערך, הצג הכל
                total_assets = sum(security['price'] * security['amount'] for security in portfolio_data)
                asset_count = len(portfolio_data)
                
                return render_template('index.html', 
                                     portfolio=portfolio_data, 
                                     total_value=total_assets,
                                     asset_count=asset_count,
                                     show_summary=False)
                
        except Exception as e:
            flash(f'שגיאה בטעינת נתוני התיק: {str(e)}', 'danger')
            return render_template('index.html', portfolio=[], total_value=0, asset_count=0, show_summary=False)
    else:
        return redirect(url_for('login'))  # הפנייה להתחברות

@app.route('/portfolio')
@login_required
def portfolio():
    """דף התיק המלא עם פגינציה לביצועים טובים"""
    try:
        # פגינציה - חלוקה לעמודים
        page = request.args.get('page', 1, type=int)  # מספר עמוד נוכחי
        per_page = 20  # מספר ניירות ערך בכל עמוד
        
        portfolio_data = portfolio_model.get_all_securities()
        
        # התחלת טעינת ייעוץ AI ברקע
        start_background_ai_advice(portfolio_data)
        
        # חישוב נתונים כלליים
        total_securities = len(portfolio_data)
        total_value = sum(security['price'] * security['amount'] for security in portfolio_data)
        
        # חלוקה לעמודים
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_data = portfolio_data[start_idx:end_idx]
        
        # הוספת חישובי סיכון לכל נייר ערך
        risk_levels = {
            'טכנולוגיה': 6, 'תחבורה': 5, 'אנרגיה': 4,
            'בריאות': 4, 'תעשייה': 3, 'פיננסים': 3,
            'נדלן': 2, 'צריכה פרטית': 1
        }
        
        for security in paginated_data:
            security['value'] = security['price'] * security['amount']
            security['risk_level'] = risk_levels.get(security.get('industry', ''), 3)
            
            if total_value > 0:
                security['percentage'] = (security['value'] / total_value) * 100
            else:
                security['percentage'] = 0
        
        # מידע על פגינציה
        total_pages = (total_securities + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('portfolio.html', 
                             portfolio=paginated_data, 
                             total_value=total_value,
                             current_page=page,
                             total_pages=total_pages,
                             has_prev=has_prev,
                             has_next=has_next,
                             total_securities=total_securities)
    except Exception as e:
        flash(f'שגיאה בטעינת תיק ההשקעות: {str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/portfolio/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_security():
    form = AddSecurityForm()
    
    if form.validate_on_submit():
        symbol = None
        stock_name = form.name.data
        default_price = 350.0
        
        # אם נבחרה מניה מהרשימה
        if form.stock_dropdown.data and form.stock_dropdown.data != '':
            symbol = form.stock_dropdown.data
            symbol_to_name = dict([(choice[0], choice[1]) for choice in AddSecurityForm.sp500_stocks if choice[0]])
            stock_name = symbol_to_name.get(symbol, symbol)
            
            # נסה לקבל מחיר אמיתי מה-API
            try:
                # שימוש בפונקציה הסטטית update_price במקום get_stock_price
                real_price = Broker.update_price(symbol)
                if real_price is not None:
                    default_price = real_price  # הפונקציה כבר מחזירה במטבע מקומי
                    print(f"קיבלתי מחיר אמיתי עבור {symbol}: ₪{real_price:.2f}")
                else:
                    default_price = 350.0  # מחיר ברירת מחדל
                    print(f"לא הצלחתי לקבל מחיר אמיתי עבור {symbol}, משתמש במחיר ברירת מחדל")
            except Exception as e:
                default_price = 350.0  # מחיר ברירת מחדל אם יש שגיאה
                print(f"שגיאה בקבלת מחיר עבור {symbol}: {e}")
        
        try:
            result = portfolio_model.add_security(
                stock_name, symbol if symbol else stock_name, form.amount.data, default_price, 
                form.industry.data, form.variance.data, form.security_type.data
            )
            if result:
                flash(f'נוסף בהצלחה: {stock_name} ({symbol if symbol else "ללא סמל"}) - מחיר: ₪{default_price:.2f}', 'success')
                return redirect(url_for('portfolio'))
            else:
                flash('שגיאה בהוספת נייר הערך', 'danger')
        except Exception as e:
            flash(f'שגיאה: {str(e)}', 'danger')
    
    return render_template('add_security.html', form=form)

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
        new_price = Broker.update_price(symbol)
        
        if new_price is not None:
            portfolio_model.update_security_price(symbol, new_price)
            flash(f'מחיר {symbol} עודכן בהצלחה ל-{new_price:.2f} ₪', 'success')
        else:
            flash(f'לא ניתן לקבל מחיר עדכני עבור {symbol}', 'warning')
    except Exception as e:
        flash(f'שגיאה בעדכון מחיר {symbol}: {str(e)}', 'danger')
    
    return redirect(url_for('portfolio'))

@app.route('/update-all-prices')
@login_required
@admin_required
def update_all_prices():
    try:
        securities = portfolio_model.get_all_securities()
        if not securities:
            flash('אין ניירות ערך בתיק לעדכון', 'warning')
            return redirect(url_for('portfolio'))
        
        updated_count = 0
        total_count = len(securities)
        
        for security in securities:
            try:
                symbol = security['name']
                new_price = Broker.update_price(symbol)
                
                if new_price is not None:
                    portfolio_model.update_security_price(symbol, new_price)
                    updated_count += 1
            except Exception as e:
                print(f"שגיאה בעדכון {symbol}: {str(e)}")
        
        if updated_count > 0:
            flash(f'עודכנו {updated_count} מתוך {total_count} ניירות ערך בהצלחה', 'success')
        else:
            flash('לא ניתן היה לעדכן אף מחיר', 'warning')
    except Exception as e:
        flash(f'שגיאה בעדכון המחירים: {str(e)}', 'danger')
    
    return redirect(url_for('portfolio'))

@app.route('/graph')
@login_required
def graph():
    try:
        portfolio_data = get_cached_portfolio()
        
        total_value = 0
        for security in portfolio_data:
            security['value'] = security['price'] * security['amount']
            total_value += security['value']
        
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
        portfolio_data = get_cached_portfolio()
        
        # הגדרת פונט שתומך בעברית
        plt.rcParams['font.family'] = ['Arial Unicode MS', 'Tahoma', 'Arial Hebrew', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['text.usetex'] = False
        
        # הגדרות מיוחדות לתמיכה בעברית
        import matplotlib
        matplotlib.use('Agg')  # השתמש ב-backend שתומך טוב יותר בעברית
        
        # תמיכה בטקסט דו-כיווני (BiDi) לעברית
        try:
            from bidi.algorithm import get_display
            use_bidi = True
        except ImportError:
            use_bidi = False
        
        if not portfolio_data:
            fig, ax = plt.subplots(figsize=(8, 6))
            no_data_text = 'אין נתונים להצגה'
            if use_bidi:
                no_data_text = get_display(no_data_text)
            ax.text(0.5, 0.5, no_data_text, ha='center', va='center', 
                   transform=ax.transAxes, fontsize=16, fontweight='bold')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
        else:
            # עיבוד שמות בעברית לתצוגה נכונה
            labels = []
            for item in portfolio_data:
                label_text = item['name']
                if use_bidi:
                    # עיבוד הטקסט בעברית לכיוון נכון
                    processed_text = get_display(label_text)
                    labels.append(processed_text)
                else:
                    labels.append(label_text)
            
            sizes = [item['price'] * item['amount'] for item in portfolio_data]
            
            # צבעים יפים ומגוונים לגרף עוגה - כל חברה בצבע שונה
            beautiful_colors = [
                '#FF6B6B',  # אדום בהיר יפה
                '#4ECDC4',  # טורקיז
                '#45B7D1',  # כחול בהיר
                '#96CEB4',  # ירוק מנטה
                '#FFEAA7',  # צהוב זהב
                '#DDA0DD',  # סגול בהיר
                '#FFA07A',  # כתום אלמון
                '#98D8C8',  # ירוק ים
                '#F7DC6F',  # צהוב לימון
                '#BB8FCE',  # סגול לבנדר
                '#85C1E9',  # כחול שמיים
                '#82E0AA',  # ירוק מינט
                '#F8C471',  # כתום אפרסק
                '#F1948A',  # ורוד סלמון
                '#85CDFD',  # כחול תכלת
                '#A8E6CF',  # ירוק פסטל
                '#FFB6B9',  # ורוד פסטל
                '#C7CEEA',  # סגול פסטל
                '#FFAAA5',  # אדום פסטל
                '#B4E7CE'   # ירוק אקווה
            ]
            
            # בחירת צבעים לפי מספר החברות
            colors = beautiful_colors[:len(labels)]
            
            # אם יש יותר חברות מצבעים, נחזור על הצבעים
            if len(labels) > len(beautiful_colors):
                colors = (beautiful_colors * ((len(labels) // len(beautiful_colors)) + 1))[:len(labels)]
            
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # יצירת גרף עוגה עם תמיכה משופרת בעברית
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                            startangle=90, colors=colors,
                                            textprops={'fontsize': 11, 'fontweight': 'bold'})
            
            # הגדרת כיוון טקסט משופר
            for text in texts:
                text.set_fontweight('bold')
                text.set_fontsize(11)
                text.set_horizontalalignment('center')
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            ax.axis('equal')
        
        # עיבוד כותרת בעברית
        title_text = 'התפלגות תיק ההשקעות'
        if use_bidi:
            title_text = get_display(title_text)
        ax.set_title(title_text, fontsize=16, fontweight='bold', pad=20)
        
        img = io.BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=300)
        img.seek(0)
        plt.close()
        
        return Response(img.getvalue(), mimetype='image/png')
    except Exception as e:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f'שגיאה: {str(e)}', ha='center', va='center',
               transform=ax.transAxes, fontsize=12)
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return Response(img.getvalue(), mimetype='image/png')

# Cache עבור ייעוץ AI
advice_cache = {
    'advice': None,
    'timestamp': 0,
    'portfolio_hash': None
}

def get_portfolio_hash(portfolio_data):
    """יוצר hash של נתוני התיק לבדיקת שינויים"""
    if not portfolio_data:
        return "empty"
    
    # יצירת מחרוזת ייחודית מנתוני התיק
    portfolio_str = ""
    for security in sorted(portfolio_data, key=lambda x: x['name']):
        portfolio_str += f"{security['name']}_{security['amount']}_{security['price']}_"
    
    import hashlib
    return hashlib.md5(portfolio_str.encode()).hexdigest()

def get_cached_advice(portfolio_data):
    """מחזיר ייעוץ מ-cache אם זמין ורלוונטי"""
    import time
    
    current_time = time.time()
    cache_duration = 1800  # 30 דקות
    
    # בדיקה אם יש cache תקף
    if advice_cache['advice'] and advice_cache['timestamp']:
        time_diff = current_time - advice_cache['timestamp']
        current_hash = get_portfolio_hash(portfolio_data)
        
        # אם התיק לא השתנה והזמן לא פג
        if (time_diff < cache_duration and 
            advice_cache['portfolio_hash'] == current_hash):
            print("מחזיר ייעוץ מ-cache")
            return advice_cache['advice']
    
    return None

def update_advice_cache(advice, portfolio_data):
    """מעדכן את cache הייעוץ"""
    import time
    
    advice_cache['advice'] = advice
    advice_cache['timestamp'] = time.time()
    advice_cache['portfolio_hash'] = get_portfolio_hash(portfolio_data)
    print("ייעוץ נשמר ב-cache")

def get_ai_advice_async(portfolio_data):
    """מקבל ייעוץ מ-AI באופן אסינכרוני"""
    try:
        print(f"get_ai_advice_async התקרא עם {len(portfolio_data)} ניירות ערך")
        if 'ai_agent' in globals() and ai_agent is not None:
            print("ai_agent זמין")
            if hasattr(ai_agent, 'get_advice'):
                print("קורא לai_agent.get_advice...")
                result = ai_agent.get_advice(portfolio_data)
                print(f"ai_agent החזיר: {len(result) if result else 0} תווים")
                return result
            else:
                print("ai_agent אין לו get_advice")
        else:
            print("ai_agent לא זמין")
    except Exception as e:
        print(f"שגיאה בקבלת ייעוץ מ-AI: {e}")
        import traceback
        traceback.print_exc()
    return None


def start_background_ai_advice(portfolio_data):
    """מתחיל טעינת ייעוץ AI ברקע - לא חוסם"""
    try:
        # בדוק אם כבר יש ייעוץ תקף ב-cache
        cached_advice = get_cached_advice(portfolio_data)
        if cached_advice:
            print("יש כבר ייעוץ תקף ב-cache - לא צריך טעינה ברקע")
            return
        
        print("אין ייעוץ ב-cache, מתחיל טעינת AI ברקע...")
        
        import threading
        
        def background_task():
            try:
                ai_advice = get_ai_advice_async(portfolio_data)
                if ai_advice and len(ai_advice.strip()) > 100:
                    update_advice_cache(ai_advice, portfolio_data)
                    print("ייעוץ AI נטען בהצלחה ונשמר ב-cache ברקע")
                else:
                    print("לא התקבל ייעוץ טוב מ-AI ברקע")
            except Exception as e:
                print(f"שגיאה בטעינת ייעוץ AI ברקע: {e}")
        
        # הרץ ברקע ללא המתנה
        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        print(f"שגיאה בהתחלת טעינה ברקע: {e}")

@app.route('/advice')
@login_required
def advice():
    """דף ייעוץ השקעות"""
    try:
        print("נכנס לפונקציה advice")
        
        # בדיקת authentication מפורטת
        if not current_user.is_authenticated:
            print("משתמש לא מחובר - מפנה לדף התחברות")
            flash('אנא התחבר כדי לצפות בייעוץ', 'warning')
            return redirect(url_for('login'))
        
        print(f"משתמש מחובר: {current_user.username}")
        
        # טען נתוני תיק
        portfolio_data = get_cached_portfolio()
        
        # בדוק אם יש ייעוץ ב-cache (שנטען ברקע)
        cached_advice = get_cached_advice(portfolio_data)
        if cached_advice:
            print("מצאתי ייעוץ ב-cache - מציג על הדף")
            return render_template('advice.html', 
                                 advice=cached_advice, 
                                 from_cache=True, 
                                 loading_ai=False)
        
        # אם אין ייעוץ ב-cache, התחל טעינה ברקע
        print("אין ייעוץ ב-cache, מתחיל טעינה ברקע...")
        start_background_ai_advice(portfolio_data)
        
        # נסה לקבל ייעוץ AI ישירות עם timeout ארוך יותר
        print("מנסה לקבל ייעוץ AI ישירות...")
        try:
            ai_advice = get_ai_advice_async(portfolio_data)
            if ai_advice and len(ai_advice.strip()) > 100:
                print("הצלחתי לקבל ייעוץ AI ישירות - מציג על הדף!")
                update_advice_cache(ai_advice, portfolio_data)
                return render_template('advice.html', 
                                     advice=ai_advice, 
                                     from_cache=False, 
                                     loading_ai=False)
            else:
                print("ייעוץ AI קצר מדי או ריק")
        except Exception as e:
            print(f"שגיאה בקבלת ייעוץ AI ישירות: {e}")
        
        # אם לא הצליח, חכה יותר זמן לטעינה ברקע
        import time
        for i in range(8):  # חכה עד 8 שניות
            time.sleep(1)
            cached_advice = get_cached_advice(portfolio_data)
            if cached_advice:
                print(f"ייעוץ AI נטען ברקע אחרי {i+1} שניות!")
                return render_template('advice.html', 
                                     advice=cached_advice, 
                                     from_cache=True, 
                                     loading_ai=False)
        
        print("ייעוץ AI לא הסתיים בזמן, מחזיר ניתוח מהיר")
        
        # ניתוח מהיר של התיק תוך המתנה ל-AI
        total_value = sum(security['price'] * security['amount'] for security in portfolio_data)
        stock_count = len(portfolio_data)
        
        # חישוב התפלגות ענפים
        industries = {}
        for security in portfolio_data:
            industry = security.get('industry', 'לא מוגדר')
            if industry not in industries:
                industries[industry] = 0
            industries[industry] += security['price'] * security['amount']
        
        # מציאת 3 המניות הגדולות
        top_holdings = sorted(portfolio_data, key=lambda x: x['price'] * x['amount'], reverse=True)[:3]
        
        static_advice = f"""ניתוח מהיר לתיק שלך (הבינה המלאכותית מכינה ניתוח מפורט...):

סיכום התיק:
• סך הערך: {total_value:,.0f} ש״ח
• מספר ניירות ערך: {stock_count}

ההחזקות הגדולות שלך:"""

        for i, holding in enumerate(top_holdings, 1):
            value = holding['price'] * holding['amount']
            percentage = (value / total_value) * 100 if total_value > 0 else 0
            static_advice += f"\n{i}. {holding['name']}: {value:,.0f} ש״ח ({percentage:.1f}%)"
        
        static_advice += f"""

התפלגות לפי ענפים:"""
        
        for industry, value in sorted(industries.items(), key=lambda x: x[1], reverse=True):
            percentage = (value / total_value) * 100 if total_value > 0 else 0
            static_advice += f"\n• {industry}: {value:,.0f} ש״ח ({percentage:.1f}%)"
        
        static_advice += """

המלצות ראשוניות:
• הפיזור נראה סביר
• יש ריכוז במניות טכנולוגיה - שקול איזון
• כדאי לבחון הוספת אגרות חוב
• זמן טוב לעדכן מחירים

לחץ "קבל ייעוץ חדש" לניתוח מקצועי מלא."""
        
        print("מחזיר ניתוח מהיר לתיק")
        return render_template('advice.html', 
                             advice=static_advice, 
                             from_cache=False, 
                             loading_ai=True)
        
    except Exception as e:
        print(f"שגיאה כללית בדף הייעוץ: {str(e)}")
        import traceback
        traceback.print_exc()
        flash('שגיאה בטעינת דף הייעוץ. אנא נסה שוב מאוחר יותר.', 'danger')
        return redirect(url_for('portfolio'))

@app.route('/refresh-advice')
@login_required
def refresh_advice():
    """מרענן את הייעוץ ומאלץ קבלת ייעוץ חדש מ-AI"""
    try:
        # נקה את ה-cache
        advice_cache['advice'] = None
        advice_cache['timestamp'] = 0
        advice_cache['portfolio_hash'] = None
        
        print("cache נוקה, מפנה לדף ייעוץ")
        return redirect(url_for('advice'))
        
    except Exception as e:
        flash(f'שגיאה ברענון הייעוץ: {str(e)}', 'danger')
        return redirect(url_for('advice'))

@app.route('/get-fresh-advice')
@login_required
def get_fresh_advice():
    """API endpoint לקבלת ייעוץ חדש מ-AI"""
    try:
        portfolio_data = get_cached_portfolio()
        
        # בדוק אם יש ייעוץ חדש ב-cache (מהטעינה ברקע)
        cached_advice = get_cached_advice(portfolio_data)
        if cached_advice:
            print("✅ מחזיר ייעוץ מ-cache")
            return jsonify({
                'success': True,
                'advice': cached_advice,
                'from_cache': True
            })
        
        # אם אין ייעוץ ב-cache, נסה לקבל מ-AI ישירות
        print("🔄 מנסה לקבל ייעוץ חדש מ-AI...")
        try:
            ai_advice = get_ai_advice_async(portfolio_data)
            if ai_advice and len(ai_advice.strip()) > 100:
                print(f"✅ ייעוץ AI הושלם ונשמר ב-cache")
                update_advice_cache(ai_advice, portfolio_data)
                return jsonify({
                    'success': True,
                    'advice': ai_advice,
                    'from_cache': False
                })
            else:
                print("⚠️ ייעוץ AI קצר מדי או ריק")
        except Exception as ai_error:
            print(f"❌ שגיאה בקבלת ייעוץ מ-AI: {ai_error}")
        
        return jsonify({
            'success': False,
            'message': 'הבינה המלאכותית עדיין עובדת... נסה שוב בעוד רגע'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'שגיאה: {str(e)}'
        })

@app.route('/risk')
@login_required
def risk():
    """דף ניהול סיכונים"""
    try:
        portfolio_data = get_cached_portfolio()
        
        # חישוב רמות סיכון
        risk_levels = {
            'טכנולוגיה': 6, 'תחבורה': 5, 'אנרגיה': 4,
            'בריאות': 4, 'תעשייה': 3, 'פיננסים': 3,
            'נדלן': 2, 'צריכה פרטית': 1
        }
        
        total_value = 0
        high_risk_value = 0
        medium_risk_value = 0
        low_risk_value = 0
        
        for security in portfolio_data:
            security_value = security['price'] * security['amount']
            total_value += security_value
            
            industry = security.get('industry', 'לא מוגדר')
            risk_level = risk_levels.get(industry, 3)
            
            if risk_level >= 5:
                high_risk_value += security_value
            elif risk_level >= 3:
                medium_risk_value += security_value
            else:
                low_risk_value += security_value
            
            security['risk_level'] = risk_level
            security['value'] = security_value
        
        # חישוב אחוזי סיכון
        if total_value > 0:
            high_risk_percentage = (high_risk_value / total_value) * 100
            medium_risk_percentage = (medium_risk_value / total_value) * 100
            low_risk_percentage = (low_risk_value / total_value) * 100
        else:
            high_risk_percentage = medium_risk_percentage = low_risk_percentage = 0
        
        risk_summary = {
            'high_risk': {'value': high_risk_value, 'percentage': high_risk_percentage},
            'medium_risk': {'value': medium_risk_value, 'percentage': medium_risk_percentage},
            'low_risk': {'value': low_risk_value, 'percentage': low_risk_percentage},
            'total_value': total_value
        }
        
        return render_template('risk.html', portfolio=portfolio_data, risk_summary=risk_summary)
    except Exception as e:
        flash(f'שגיאה בטעינת דף הסיכונים: {str(e)}', 'danger')
        return redirect(url_for('portfolio'))

@app.route('/health')
def health_check():
    """בדיקת סטטוס המערכת"""
    return jsonify({"status": "OK", "message": "מערכת פועלת תקין"})

@app.route('/api-keys-status')
@login_required
@admin_required
def api_keys_status():
    """בדיקת סטטוס מפתחות API"""
    try:
        # מידע על כל המפתחות
        api_keys_info = []
        
        # גישה בטוחה לאטריביוטים של Broker
        try:
            # ייבוא מחדש של מחלקת Broker
            from dbmodel import Broker as BrokerClass
            
            # בדיקה שהאטריביוטים קיימים ובטיפוס הנכון
            if hasattr(BrokerClass, 'API_KEYS'):
                api_keys_raw = BrokerClass.API_KEYS
                if isinstance(api_keys_raw, list):
                    keys_list = api_keys_raw.copy()  # יצירת עותק בטוח
                else:
                    print(f"Broker.API_KEYS is not a list: {type(api_keys_raw)}")
                    keys_list = ["451FPPPSEOOZIDV4", "XX4SBD1SXLFLUSV2"]
            else:
                print("Broker.API_KEYS attribute not found")
                keys_list = ["451FPPPSEOOZIDV4", "XX4SBD1SXLFLUSV2"]
            
            if hasattr(BrokerClass, 'current_key_index'):
                current_index_raw = BrokerClass.current_key_index
                if isinstance(current_index_raw, int):
                    current_index = current_index_raw
                else:
                    print(f"Broker.current_key_index is not an int: {type(current_index_raw)}")
                    current_index = 0
            else:
                print("Broker.current_key_index attribute not found")
                current_index = 0
                
        except Exception as import_error:
            print(f"Error importing or accessing Broker class: {import_error}")
            keys_list = ["451FPPPSEOOZIDV4", "XX4SBD1SXLFLUSV2"]
            current_index = 0
        
        # וידוי שהאינדקס תקין
        if current_index < 0 or current_index >= len(keys_list):
            current_index = 0
        
        # בניית מידע על כל מפתח
        for i, key in enumerate(keys_list):
            try:
                if key is None:
                    continue
                    
                key_str = str(key)
                is_current = (i == current_index)
                
                if key_str == "DEMO":
                    key_display = "DEMO"
                else:
                    key_display = key_str[:8] + "..." if len(key_str) > 8 else key_str
                
                api_keys_info.append({
                    'index': i,
                    'key': key_display,
                    'full_key': key_str,
                    'is_current': is_current,
                    'status': '✓ פעיל' if is_current else '⏸ זמין',
                    'type': 'מפתח הדגמה' if key_str == "DEMO" else 'מפתח פרימיום'
                })
            except Exception as key_process_error:
                print(f"Error processing key at index {i}: {key_process_error}")
                continue
        
        # בדיקת חיבור עם המפתח הנוכחי
        connection_status = "⚠ לא נבדק"
        last_test_price = "לא זמין"
        
        try:
            # ניסוי לבדוק את ה-API עם מניית בדיקה
            from dbmodel import Broker as TestBroker
            
            if hasattr(TestBroker, 'update_price') and callable(TestBroker.update_price):
                test_result = TestBroker.update_price('AAPL')
                
                if test_result is not None and isinstance(test_result, (int, float)) and test_result > 0:
                    connection_status = "✓ מחובר"
                    last_test_price = f"${float(test_result):.2f}"
                else:
                    connection_status = " לא זמין"
                    last_test_price = "מחיר לא התקבל"
            else:
                connection_status = " פונקציה לא זמינה"
                last_test_price = "שירות לא פעיל"
                
        except Exception as test_error:
            connection_status = " שגיאה בבדיקה"
            last_test_price = f"שגיאה: {str(test_error)[:30]}..."
        
        # הכנת נתוני התצוגה
        api_status = {
            'api_keys': api_keys_info,
            'current_key_index': current_index,
            'total_keys': len(keys_list),
            'connection_status': connection_status,
            'last_test_price': last_test_price
        }
        
        return render_template('api_keys.html', api_status=api_status)
        
    except Exception as global_error:
        # טיפול בשגיאה כללית
        error_message = f"שגיאה כללית במערכת מפתחות API: {str(global_error)}"
        print(f"Global API Status Error: {error_message}")
        flash(error_message, 'danger')
        
        # חזרת סטטוס בסיסי במקום שגיאה
        basic_status = {
            'api_keys': [
                {'index': 0, 'key': '451FPPPS...', 'full_key': '451FPPPSEOOZIDV4', 'is_current': True, 'status': '✓ פעיל', 'type': 'מפתח פרימיום'},
                {'index': 1, 'key': 'XX4SBD1S...', 'full_key': 'XX4SBD1SXLFLUSV2', 'is_current': False, 'status': '⏸ זמין', 'type': 'מפתח פרימיום'}
            ],
            'current_key_index': 0,
            'total_keys': 2,
            'connection_status': "⚠ לא נבדק",
            'last_test_price': "לא זמין"
        }
        
        return render_template('api_keys.html', api_status=basic_status)

@app.route('/debug-database')
@login_required
@admin_required
def debug_database():
    """דף בדיקת מסד נתונים"""
    try:
        portfolio_data = get_cached_portfolio()
        
        debug_info = {
            'total_securities': len(portfolio_data),
            'database_type': 'PostgreSQL' if portfolio_model.database_url else 'SQLite',
            'securities': portfolio_data[:10] if portfolio_data else []  # הצג רק 10 ראשונים
        }
        
        return render_template('debug_db.html', debug_info=debug_info)
    except Exception as e:
        flash(f'שגיאה בבדיקת מסד הנתונים: {str(e)}', 'danger')
        return redirect(url_for('portfolio'))

@app.route('/test-api')
@login_required
@admin_required
def test_api():
    """בדיקת API"""
    try:
        # בדיקת חיבור ל-Alpha Vantage
        test_result = Broker.update_price('AAPL')
        
        if test_result:
            api_test = {
                'status': 'success',
                'message': f'API פועל תקין - מחיר AAPL: ${test_result:.2f}',
                'price': test_result
            }
        else:
            api_test = {
                'status': 'warning',
                'message': 'API זמין אך לא הצליח לקבל מחיר',
                'price': None
            }
        
        return jsonify(api_test)
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'שגיאה בבדיקת API: {str(e)}',
            'price': None
        })

@app.route('/setup-database')
@login_required
@admin_required
def setup_database():
    """הגדרת מסד נתונים מלא עם נתוני דוגמה"""
    import traceback
    
    try:
        print("=== התחלת הגדרת מסד נתונים מלא ===")
        
        # יצירת טבלאות
        print("יוצר טבלאות...")
        portfolio_model.create_tables()
        print("טבלאות נוצרו בהצלחה")
        
        # יצירת משתמשי ברירת מחדל
        print("מוסיף משתמשים...")
        portfolio_model.create_default_users()
        print("משתמשי ברירת מחדל נוצרו בהצלחה")
        
        # בדיקה אם יש כבר נתונים
        print("מוסיף נתוני דוגמה...")
        existing_securities = portfolio_model.get_all_securities()
        
        sample_securities = []
        
        if len(existing_securities) < 6:
            # ניקוי טבלה אם צריך
            try:
                conn = portfolio_model.get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM securities")
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"שגיאה בניקוי טבלה: {e}")
            
            # הוספת נתוני דוגמה
            sample_securities = [
                ("אפל", "AAPL", 10, 150.0, "טכנולוגיה", 0.25, "מניה"),
                ("גוגל", "GOOGL", 5, 2800.0, "טכנולוגיה", 0.22, "מניה"),
                ("אגח ממשלתי", "GOVT", 100, 100.0, "פיננסים", 0.05,
                 "אגח ממשלתית"),
                ("טסלה", "TSLA", 3, 800.0, "תחבורה", 0.35, "מניה"),
                ("מיקרוסופט", "MSFT", 8, 300.0, "טכנולוגיה", 0.20, "מניה"),
                ("אמזון", "AMZN", 2, 1500.0, "צריכה פרטית", 0.28, "מניה")
            ]
            
            for security_data in sample_securities:
                try:
                    portfolio_model.add_security(*security_data)
                    sec_name = security_data[0]
                    sec_amount = security_data[2]
                    sec_price = security_data[3]
                    print(f"נוסף: {sec_name} - {sec_amount} יחידות ב-{sec_price} ₪")
                except Exception as e:
                    print(f"שגיאה בהוספת {security_data[0]}: {e}")
        else:
            existing_count = len(existing_securities)
            print(f"כבר יש {existing_count} ניירות ערך במסד הנתונים")
            sample_securities = existing_securities[:6]  # השתמש בקיימים
        
        print("=== סיום הגדרת מסד נתונים מלא ===")
        
        # מידע על מה שנוצר
        total_users = 2  # admin + user
        total_securities = len(sample_securities)
        
        success_message = f"""
        <div class="alert alert-success">
            <h4>✅ מסד הנתונים הוגדר בהצלחה!</h4>
            <h3>מה שנוצר:</h3>
            <ul>
                <li><strong>משתמשים:</strong> {total_users} 
                (admin/admin ו-user/user)</li>
                <li><strong>ניירות ערך:</strong> {total_securities} 
                מניות ואגרות חוב</li>
                <li><strong>טבלאות:</strong> כל הטבלאות נוצרו בהצלחה</li>
            </ul>
            <p><a href="/portfolio" class="btn btn-primary">
            עבור לתיק השקעות</a></p>
        </div>
        """
        
        return success_message
        
    except Exception as e:
        error_message = f"שגיאה בהגדרת מסד נתונים: {str(e)}"
        print(error_message)
        traceback.print_exc()
        
        return f"""
        <div class="alert alert-danger">
            <h4>❌ שגיאה בהגדרת מסד הנתונים</h4>
            <p>{error_message}</p>
            <p><a href="/debug-database" class="btn btn-secondary">
            בדוק מסד נתונים</a></p>
        </div>
        """


@app.route('/check-env')
def check_env():
    """בדיקת משתני סביבה"""
    try:
        env_info = {
            'DATABASE_URL': os.environ.get('DATABASE_URL', 'לא מוגדר'),
            'PORT': os.environ.get('PORT', '8080'),
            'OLLAMA_URL': os.environ.get('OLLAMA_URL', 'לא מוגדר'),
            'SECRET_KEY': ('***מוגדר***' if os.environ.get('SECRET_KEY') 
                          else 'לא מוגדר')
        }
        
        # בדיקת חיבור למסד נתונים
        try:
            conn = portfolio_model.get_connection()
            conn.close()
            db_status = "✅ מחובר"
        except Exception as e:
            db_status = f"❌ שגיאה: {str(e)}"
        
        return f"""
        <div class="container mt-4">
            <h2>בדיקת משתני סביבה</h2>
            <div class="card">
                <div class="card-body">
                    <h4>משתני סביבה:</h4>
                    <ul>
                        <li><strong>DATABASE_URL:</strong> 
                        {env_info['DATABASE_URL']}</li>
                        <li><strong>PORT:</strong> {env_info['PORT']}</li>
                        <li><strong>OLLAMA_URL:</strong> 
                        {env_info['OLLAMA_URL']}</li>
                        <li><strong>SECRET_KEY:</strong> 
                        {env_info['SECRET_KEY']}</li>
                    </ul>
                    
                    <h4>סטטוס מסד נתונים:</h4>
                    <p>{db_status}</p>
                    
                    <div class="mt-3">
                        <a href="/setup-database" class="btn btn-primary">
                        הגדר מסד נתונים</a>
                        <a href="/debug-database" class="btn btn-secondary">
                        בדוק נתונים</a>
                    </div>
                </div>
            </div>
        </div>
        """
    except Exception as e:
        return f"שגיאה: {str(e)}"


@app.route('/db-admin')
@login_required
@admin_required
def db_admin():
    """דף ניהול מסד נתונים"""
    print("=== התחלת פונקציית db_admin ===")
    
    try:
        # קבלת סטטיסטיקות בסיסיות
        securities = portfolio_model.get_all_securities()
        
        admin_info = {
            'total_securities': len(securities),
            'database_type': ('PostgreSQL' if portfolio_model.database_url 
                             else 'SQLite'),
            'recent_securities': securities[:5] if securities else []
        }
        
        print("=== סיום פונקציית db_admin ===")
        return render_template('debug_db.html', debug_info=admin_info)
        
    except Exception as e:
        flash(f'שגיאה בטעינת דף ניהול: {str(e)}', 'danger')
        return redirect(url_for('portfolio'))


@app.route('/db-status')
def db_status():
    """בדיקת סטטוס מסד נתונים"""
    try:
        print("=== התחלת בדיקת סטטוס מסד נתונים ===")
        
        # בדיקת חיבור
        conn = portfolio_model.get_connection()
        
        # בדיקת טבלאות
        cursor = conn.cursor()
        if portfolio_model.database_url:  # PostgreSQL
            cursor.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public';"
            )
        else:  # SQLite
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';"
            )
        
        tables = cursor.fetchall()
        conn.close()
        
        print("=== סיום בדיקת סטטוס מסד נתונים ===")
        
        return jsonify({
            'status': 'success',
            'database_type': ('PostgreSQL' if portfolio_model.database_url 
                             else 'SQLite'),
            'tables_count': len(tables),
            'tables': [table[0] for table in tables]
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })


@app.route('/update-lqd-name')
@login_required
@admin_required
def update_lqd_name():
    """עדכון שם LQD לשם ברור יותר"""
    try:
        # חיפוש והחלפה של LQD
        securities = portfolio_model.get_all_securities()
        
        for security in securities:
            name = security.get('name', '')
            symbol = security.get('symbol', '')
            if 'LQD' in name or 'LQD' in symbol:
                # עדכון לשם ברור יותר
                new_name = "קרן אגרות חוב קונצרניות"
                portfolio_model.update_security_name(security['name'], new_name)
                flash(f'עודכן: {security["name"]} → {new_name}', 'success')
        
        return redirect(url_for('portfolio'))
        
    except Exception as e:
        flash(f'שגיאה בעדכון: {str(e)}', 'danger')
        return redirect(url_for('portfolio'))



def prepare_ai_in_background():
    """מכין את ה-AI ברקע כדי שהתגובות יהיו מהירות"""
    try:
        print("מכין בינה מלאכותית ברקע...")
        import threading
        import time
        
        def warm_up_ai():
            try:
                time.sleep(3)  # חכה שהשרת יתחיל
                if 'ai_agent' in globals() and ai_agent:
                    print("מחמם את ה-AI עם שאלת דוגמה...")
                    # שלח שאלה פשוטה כדי שהמודל יטען לזיכרון
                    sample_portfolio = [
                        {'name': 'אפל', 'amount': 10, 'price': 150, 
                         'industry': 'טכנולוגיה', 'security_type': 'מניה'}
                    ]
                    result = ai_agent.get_advice(sample_portfolio)
                    if result and len(result) > 50:
                        print("בינה מלאכותית מוכנה ומהירה!")
                    else:
                        print("בינה מלאכותית לא מוכנה")
                else:
                    print("בינה מלאכותית לא זמינה")
            except Exception as e:
                print(f"שגיאה בהכנת AI: {e}")
        
        # הרץ ברקע
        thread = threading.Thread(target=warm_up_ai)
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        print(f"שגיאה בהכנת AI ברקע: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f" מפעיל את השרת על פורט {port}")
    print(" מערכת ניהול תיק השקעות - גרסה מקומית")
    print(f" היכנס ל: http://localhost:{port}")
    print(" משתמשים: admin/admin (מנהל) או user/user (משתמש)")
    
    # הכן את ה-AI ברקע לתגובות מהירות
    prepare_ai_in_background()
    
    app.run(host='0.0.0.0', port=port, debug=True)

