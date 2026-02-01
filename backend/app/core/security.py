import bcrypt
from datetime import datetime, timedelta
from jose import jwt

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Optimized Speed for Production
BCRYPT_ROUNDS = 10 

def hash_password(password: str) -> str:
    """Hash a password using raw bcrypt library with optimized rounds."""
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password using raw bcrypt library."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False

def needs_rehash(hashed_password: str) -> bool:
    """Check if the password hash needs to be updated to the target rounds."""
    try:
        # Example format: $2b$12$salt...
        # We assume standard modular crypt format
        parts = hashed_password.split('$')
        if len(parts) > 2:
            rounds = int(parts[2])
            return rounds > BCRYPT_ROUNDS
    except Exception:
        pass
    return False

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
