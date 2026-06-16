"""Set known password for admin"""
import sys; sys.path.insert(0, '.')
import bcrypt
from app.db.database import engine
from sqlalchemy import text

password = "admin123"
salt = bcrypt.gensalt()
pw_hash = bcrypt.hashpw(password.encode(), salt).decode()

with engine.connect() as conn:
    conn.execute(text("UPDATE usuarios SET password_hash = :h WHERE email = :e"), {"h": pw_hash, "e": "admin@admin.com"})
    conn.commit()
    print(f"Password for admin@admin.com set to: {password}")
    print(f"Hash: {pw_hash}")
