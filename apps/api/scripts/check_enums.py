"""
Check what enum values actually exist in the database
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.DATABASE_URL)

with engine.connect() as conn:
    # Check profilestatus enum
    result = conn.execute(text("""
        SELECT e.enumlabel 
        FROM pg_enum e 
        JOIN pg_type t ON e.enumtypid = t.oid 
        WHERE t.typname = 'profilestatus'
        ORDER BY e.enumsortorder
    """))
    
    print("ProfileStatus enum values in database:")
    for row in result:
        print(f"  - '{row[0]}'")
    
    # Check deploymentstatus enum
    result = conn.execute(text("""
        SELECT e.enumlabel 
        FROM pg_enum e 
        JOIN pg_type t ON e.enumtypid = t.oid 
        WHERE t.typname = 'deploymentstatus'
        ORDER BY e.enumsortorder
    """))
    
    print("\nDeploymentStatus enum values in database:")
    for row in result:
        print(f"  - '{row[0]}'")
