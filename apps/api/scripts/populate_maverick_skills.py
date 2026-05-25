"""
Populate maverick_skills table from existing JSON skills

This script migrates skills from mavericks.skills and mavericks.ai_extracted_skills JSON columns
to the maverick_skills table so that the AI Talent Search feature works correctly.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from app.database import SessionLocal

# Import all models to ensure relationships are properly configured
from app.models import *  # This imports all models
from app.models.maverick import Maverick
from app.models.maverick_skill import MaverickSkill, ProficiencyLevel

def populate_skills():
    db = SessionLocal()
    try:
        print("🔄 Populating maverick_skills table from JSON skills...")
        print()
        
        # Get all mavericks
        mavericks = db.query(Maverick).all()
        print(f"📊 Found {len(mavericks)} mavericks")
        print()
        
        total_skills_created = 0
        mavericks_updated = 0
        
        for maverick in mavericks:
            # Collect all unique skills from both JSON fields
            all_skills = set()
            
            # From self-declared skills
            if maverick.skills and isinstance(maverick.skills, list):
                all_skills.update([str(s).strip() for s in maverick.skills if s])
            
            # From AI-extracted skills
            if maverick.ai_extracted_skills and isinstance(maverick.ai_extracted_skills, list):
                all_skills.update([str(s).strip() for s in maverick.ai_extracted_skills if s])
            
            if not all_skills:
                print(f"   ⚠️  {maverick.name}: No skills found")
                continue
            
            # Check existing skills in maverick_skills table
            existing_skills = db.query(MaverickSkill).filter(
                MaverickSkill.maverick_id == maverick.id
            ).all()
            
            existing_skill_names = {skill.skill_name.lower() for skill in existing_skills}
            skills_created_for_maverick = 0
            
            # Create missing skills
            for skill_name in all_skills:
                if not skill_name or skill_name.lower() in existing_skill_names:
                    continue
                
                # Create new skill with default proficiency
                new_skill = MaverickSkill(
                    maverick_id=maverick.id,
                    skill_name=skill_name,
                    category="TECHNICAL",  # Default category
                    proficiency_score=60.0,  # Default intermediate level
                    proficiency_level=ProficiencyLevel.INTERMEDIATE.value,
                    self_declared=60.0  # Mark as self-declared
                )
                db.add(new_skill)
                skills_created_for_maverick += 1
                total_skills_created += 1
            
            if skills_created_for_maverick > 0:
                mavericks_updated += 1
                print(f"   ✅ {maverick.name}: Created {skills_created_for_maverick} skills ({', '.join(sorted(all_skills))})")
        
        # Commit all changes
        db.commit()
        
        print()
        print("=" * 60)
        print("✅ Migration Complete!")
        print("=" * 60)
        print(f"   📊 Mavericks processed: {len(mavericks)}")
        print(f"   📊 Mavericks updated: {mavericks_updated}")
        print(f"   📊 Skills created: {total_skills_created}")
        print()
        print("🎯 AI Talent Search is now ready to use!")
        print()
        
    except Exception as e:
        db.rollback()
        print()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  Maverick Skills Migration")
    print("=" * 60)
    print()
    populate_skills()
