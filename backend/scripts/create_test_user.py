from app.db.database import SessionLocal
from app.db.models import User
from app.core.security import hash_password

def create_test_user():
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == 'test@example.com').first()
        if not user:
            db.add(User(email='test@example.com', password_hash=hash_password('password123')))
            db.commit()
            print('Test user created: test@example.com / password123')
        else:
            print('Test user already exists')
    finally:
        db.close()

if __name__ == '__main__':
    create_test_user()
