"""Set known password for the user account"""
import sys; sys.path.insert(0, '.')
import bcrypt
from app.db.database import engine
from sqlalchemy import text

password = "test123"
salt = bcrypt.gensalt()
pw_hash = bcrypt.hashpw(password.encode(), salt).decode()

with engine.connect() as conn:
    conn.execute(text("UPDATE usuarios SET password_hash = :h WHERE email = :e"), {"h": pw_hash, "e": "gonzifracchia@gmail.com"})
    conn.commit()
    print(f"Password for gonzifracchia@gmail.com set to: {password}")
