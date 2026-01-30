from app.db.database import SessionLocal, engine, Base
from app.db.models import User
from app.core.security import hash_password
from sqlalchemy import text

def verify_db():
    try:
        # Create session
        db = SessionLocal()
        print("Session created.")

        # Check if tables exist
        print("Checking tables...")
        # This will create tables if they don't exist (useful for first run with new DB)
        Base.metadata.create_all(bind=engine)
        print("Tables checked/created.")

        test_email = "test_manual@example.com"
        
        # Check if user exists
        existing_user = db.query(User).filter(User.email == test_email).first()
        if existing_user:
            print(f"User {test_email} already exists. ID: {existing_user.id}")
            # Delete for clean test if needed, or just use it
            # db.delete(existing_user)
            # db.commit()
        else:
            print(f"Creating user {test_email}...")
            new_user = User(
                email=test_email,
                password_hash=hash_password("password123")
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            print(f"User created successfully. ID: {new_user.id}")

        # Verify retrieval
        user = db.query(User).filter(User.email == test_email).first()
        if user:
            print(f"Verification: Retrieved user {user.email} from DB.")
        else:
            print("Verification FAILED: Could not retrieve user after creation.")

        db.close()
        print("Database verification complete.")

    except Exception as e:
        print(f"Database verification FAILED with error: {e}")

if __name__ == "__main__":
    verify_db()
