import os
import shutil
import sys

# Set environment variable to simulate HF Space BEFORE imports
os.environ["SPACE_ID"] = "fake-space-id"

# Mock git repo dir (app root)
FAKE_HOME = os.path.join(os.getcwd(), "fake_hf_home")
if os.path.exists(FAKE_HOME):
    shutil.rmtree(FAKE_HOME) # Clean start
os.makedirs(FAKE_HOME, exist_ok=True)

# Copy actual code/db to fake app dir
FAKE_APP_DIR = os.path.join(FAKE_HOME, "app")
os.makedirs(FAKE_APP_DIR, exist_ok=True)

# Copy app module
# We need to copy 'app' folder to FAKE_HOME so we can import it
if os.path.exists("app"):
    shutil.copytree("app", os.path.join(FAKE_HOME, "app"), dirs_exist_ok=True)

if os.path.exists("app.db"):
    shutil.copy("app.db", os.path.join(FAKE_HOME, "app.db"))

# Change sys.path to include FAKE_HOME so we import from THERE
sys.path.insert(0, FAKE_HOME)

# Change CWD to FAKE_HOME (root of the app)
os.chdir(FAKE_HOME)
print(f"Simulating HF execution in: {os.getcwd()}")

# NOW import app modules
from app.db.database import engine, SessionLocal, DATABASE_URL
# We need to handle DB_FILE import safely as it might not be exported if logic is weird
try:
    from app.db.database import DB_FILE
except ImportError:
    DB_FILE = "UNDEFINED"

from app.api.auth import login as auth_login, LoginRequest
from app.db import models
from app.db.init_db import init_db

print(f"Expected DB_FILE: {DB_FILE}")
print(f"Expected DATABASE_URL: {DATABASE_URL}")

# Run Init
try:
    init_db()
    print("init_db() executed successfully.")
except Exception as e:
    print(f"init_db() failed: {e}")

# Verify File Exists
if os.path.exists(DB_FILE):
    print(f"SUCCESS: DB File created at {DB_FILE}")
else:
    print(f"FAILURE: DB File NOT found at {DB_FILE}")

# Verify Users
try:
    session = SessionLocal()
    count = session.query(models.User).count()
    print(f"User Count in Production DB: {count}")
    
    users = session.query(models.User).all()
    print(f"Total Users: {len(users)}")
    
    from app.core.security import verify_password
    
    for u in users:
        print(f"--- Checking User: {u.email} ---")
        # Try common passwords
        for pw in ["password", "password123", "test", "123456"]:
            if verify_password(pw, u.password_hash):
                print(f"✅ VALID CREDENTIAL: {u.email} / {pw}")
                break
        else:
            print(f"❌ Could not crack password for {u.email}")
    else:
        print("FAILURE: No users found!")
            
    session.close()
except Exception as e:
    print(f"Verification Failed: {e}")
