"""
Clear maverick skills to regenerate with new AI feedback
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.maverick_skill import MaverickSkill

def clear_skills():
    db = SessionLocal()
    try:
        # Delete all maverick skills
        count = db.query(MaverickSkill).delete()
        db.commit()
        print(f"✅ Cleared {count} skill records")
        print("   Skills will be regenerated with new AI feedback on next assessment.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🗑️  Clearing old skill data...")
    clear_skills()
