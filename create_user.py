from app import app, db, User

def create_default_user():
    with app.app_context():
        # Create database tables
        db.create_all()
        
        # Check if user exists
        existing_user = User.query.filter_by(username='admin').first()
        if not existing_user:
            # Create default user
            user = User(name='מנהל', username='admin')
            user.set_password('admin')
            db.session.add(user)
            db.session.commit()
            print('משתמש ברירת מחדל נוצר: admin / admin')
        else:
            print('משתמש קיים כבר')

if __name__ == '__main__':
    create_default_user() 