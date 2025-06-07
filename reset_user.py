from app import app, db, User

def reset_admin_user():
    with app.app_context():
        # Delete existing user
        existing_user = User.query.filter_by(username='admin').first()
        if existing_user:
            db.session.delete(existing_user)
            db.session.commit()
            print('משתמש קיים נמחק')
        
        # Create new user
        user = User(name='מנהל', username='admin')
        user.set_password('admin')
        db.session.add(user)
        db.session.commit()
        print('משתמש חדש נוצר: admin / admin')

if __name__ == '__main__':
    reset_admin_user() 