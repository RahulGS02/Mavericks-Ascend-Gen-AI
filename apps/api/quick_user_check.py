"""Quick user check with print output"""
import sys
sys.stdout = sys.stderr  # Force output to stderr to bypass buffering

print("Starting user check...", flush=True)

try:
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import verify_password
    
    print("Imports successful", flush=True)
    
    db = SessionLocal()
    print("Database connected", flush=True)
    
    email = "MaverickOne@mail.com"
    password = "MaverickOne@1"
    
    print(f"\nSearching for: {email}", flush=True)
    
    # Try exact match first
    user = db.query(User).filter(User.email == email).first()
    print(f"Exact match result: {user}", flush=True)
    
    if not user:
        # Try case-insensitive
        user = db.query(User).filter(User.email.ilike(email)).first()
        print(f"Case-insensitive result: {user}", flush=True)
    
    if user:
        print(f"\n✅ USER FOUND!", flush=True)
        print(f"Email: {user.email}", flush=True)
        print(f"Name: {user.name}", flush=True)
        print(f"Role: {user.role.value}", flush=True)
        
        # Test password
        matches = verify_password(password, user.password_hash)
        print(f"\nPassword test: {matches}", flush=True)
        
        if matches:
            print(f"✅ PASSWORD CORRECT - Login should work!", flush=True)
        else:
            print(f"❌ PASSWORD WRONG - This is the problem!", flush=True)
    else:
        print(f"\n❌ USER NOT FOUND in database", flush=True)
        
        # Show recent users
        print(f"\nRecent users:", flush=True)
        recent = db.query(User).order_by(User.created_at.desc()).limit(3).all()
        for u in recent:
            print(f"  - {u.email}", flush=True)
    
    db.close()
    print("\nDone!", flush=True)
    
except Exception as e:
    print(f"ERROR: {str(e)}", flush=True)
    import traceback
    traceback.print_exc()
