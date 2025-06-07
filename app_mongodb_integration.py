"""
דוגמה לאינטגרציה של MongoDB Atlas עם האפליקציה הקיימת
קובץ זה מראה איך להחליף את SQLite ב-MongoDB Atlas
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv

# טעינת משתני סביבה
load_dotenv()

# יבוא מודולים
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# הגדרת Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ניסיון לחיבור ל-MongoDB Atlas
portfolio_controller = None
db_type = "SQLite"

try:
    # נסיון חיבור ל-MongoDB Atlas
    if all([
        os.getenv('MONGODB_USERNAME'),
        os.getenv('MONGODB_PASSWORD'), 
        os.getenv('MONGODB_CLUSTER_URL')
    ]):
        from mongodb_atlas_controller import MongoDBAtlasManager, MongoDBPortfolioController
        
        print("🔄 מנסה להתחבר ל-MongoDB Atlas...")
        mongo_manager = MongoDBAtlasManager()
        portfolio_controller = MongoDBPortfolioController(mongo_manager)
        db_type = "MongoDB Atlas"
        print("✅ התחברות מוצלחת ל-MongoDB Atlas!")
        
    else:
        raise Exception("משתני סביבה ל-MongoDB לא מוגדרים")
        
except Exception as e:
    # חזרה ל-SQLite במקרה של שגיאה
    print(f"⚠️ שגיאה בחיבור ל-MongoDB Atlas: {e}")
    print("🔄 חוזר ל-SQLite...")
    
    from portfolio_controller import PortfolioController
    portfolio_controller = PortfolioController()
    db_type = "SQLite"
    print("✅ משתמש ב-SQLite")

@login_manager.user_loader
def load_user(user_id):
    # כאן תוכל להוסיף לוגיקה לטעינת משתמשים
    # עבור MongoDB או SQLite
    return None

@app.route('/')
@login_required
def dashboard():
    """דף הבית עם מידע על התיק"""
    try:
        holdings = portfolio_controller.get_portfolio()
        total_value = portfolio_controller.get_total_portfolio_value() if hasattr(portfolio_controller, 'get_total_portfolio_value') else 0
        
        return render_template('dashboard.html', 
                             holdings=holdings,
                             total_value=total_value,
                             db_type=db_type)
    except Exception as e:
        flash(f"שגיאה בטעינת הדשבורד: {e}", 'error')
        return render_template('dashboard.html', holdings=[], total_value=0, db_type=db_type)

@app.route('/portfolio')
@login_required
def portfolio():
    """דף תיק השקעות"""
    try:
        holdings = portfolio_controller.get_portfolio()
        total_value = portfolio_controller.get_total_portfolio_value() if hasattr(portfolio_controller, 'get_total_portfolio_value') else 0
        
        return render_template('portfolio.html',
                             holdings=holdings, 
                             total_value=total_value,
                             db_type=db_type)
    except Exception as e:
        flash(f"שגיאה בטעינת התיק: {e}", 'error')
        return render_template('portfolio.html', holdings=[], total_value=0, db_type=db_type)

@app.route('/buy_security', methods=['GET', 'POST'])
@login_required
def buy_security():
    """רכישת נייר ערך"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            amount = float(request.form.get('amount', 0))
            industry = request.form.get('industry')
            variance = request.form.get('variance') 
            security_type = request.form.get('security_type')
            
            result = portfolio_controller.buy_security(name, amount, industry, variance, security_type)
            
            if "✅" in result:
                flash(result, 'success')
            else:
                flash(result, 'error')
                
        except Exception as e:
            flash(f"שגיאה ברכישה: {e}", 'error')
        
        return redirect(url_for('portfolio'))
    
    return render_template('buy_security.html', db_type=db_type)

@app.route('/portfolio/delete/<security_name>', methods=['POST'])
@login_required
def delete_security(security_name):
    """מחיקת נייר ערך"""
    try:
        result = portfolio_controller.remove_security(security_name)
        
        if "✅" in result:
            flash(result, 'success')
        else:
            flash(result, 'error')
            
    except Exception as e:
        flash(f"שגיאה במחיקה: {e}", 'error')
    
    return redirect(url_for('portfolio'))

@app.route('/update_price', methods=['POST'])
@login_required 
def update_price():
    """עדכון מחיר נייר ערך"""
    try:
        data = request.get_json()
        name = data.get('name')
        new_price = float(data.get('price', 0))
        
        if hasattr(portfolio_controller, 'update_security_price'):
            result = portfolio_controller.update_security_price(name, new_price)
        else:
            # fallback לממשק הישן
            result = f"עדכון מחיר לא זמין ב-{db_type}"
        
        return jsonify({
            'success': "✅" in result,
            'message': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f"שגיאה בעדכון מחיר: {e}"
        })

@app.route('/api/portfolio')
@login_required
def api_portfolio():
    """API לקבלת נתוני תיק במבנה JSON"""
    try:
        holdings = portfolio_controller.get_portfolio()
        total_value = portfolio_controller.get_total_portfolio_value() if hasattr(portfolio_controller, 'get_total_portfolio_value') else 0
        
        return jsonify({
            'success': True,
            'holdings': holdings,
            'total_value': total_value,
            'db_type': db_type,
            'count': len(holdings)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'db_type': db_type
        })

@app.route('/health')
def health_check():
    """בדיקת בריאות המערכת"""
    try:
        # בדיקה בסיסית של חיבור מסד נתונים
        holdings = portfolio_controller.get_portfolio()
        
        return jsonify({
            'status': 'healthy',
            'db_type': db_type,
            'holdings_count': len(holdings),
            'timestamp': str(datetime.utcnow())
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'db_type': db_type,
            'error': str(e),
            'timestamp': str(datetime.utcnow())
        }), 500

# דוגמה להגדרות MongoDB באמצעות משתני סביבה
def setup_mongodb_env_example():
    """
    דוגמה להגדרת משתני סביבה ל-MongoDB Atlas
    יצור קובץ .env עם הערכים הבאים:
    """
    example_env = """
# MongoDB Atlas Configuration
MONGODB_USERNAME=investment_user
MONGODB_PASSWORD=your_strong_password_here
MONGODB_CLUSTER_URL=cluster0.abc123.mongodb.net
MONGODB_DATABASE=investment_portfolio

# Flask Configuration  
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
"""
    
    print("📝 דוגמה לקובץ .env:")
    print(example_env)

if __name__ == '__main__':
    from datetime import datetime
    
    print(f"\n🚀 מתחיל שרת Flask עם {db_type}")
    print(f"🕐 זמן: {datetime.now()}")
    
    if db_type == "SQLite":
        print("💡 להשתמש ב-MongoDB Atlas:")
        print("   1. צור חשבון במונגו אטלס")
        print("   2. הגדר משתני סביבה")
        print("   3. התקן: pip install -r requirements_mongodb.txt")
        setup_mongodb_env_example()
    
    app.run(debug=True, port=5000) 