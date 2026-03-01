"""Reset all seed user passwords to known values."""
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()
try:
    users = db.query(User).all()
    print(f"Resetting passwords for {len(users)} users...")
    
    for user in users:
        if user.role.value == 'artisan':
            new_pass = 'maalem123'
        else:
            new_pass = 'client123'
        user.password_hash = get_password_hash(new_pass)
    
    db.commit()
    print("Done! New passwords:")
    print("  All artisans: maalem123")
    print("  All clients:  client123")
    print()
    users = db.query(User).all()
    for u in users:
        role = u.role.value
        pw = 'maalem123' if role == 'artisan' else 'client123'
        print(f"  {u.email} / {pw}  ({u.full_name})")
finally:
    db.close()
