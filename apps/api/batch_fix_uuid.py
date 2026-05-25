"""
Batch fix UUID imports in all remaining model files
"""
import re

# List of files and their UUID column replacements
FILES_TO_FIX = [
    "app/models/batch.py",
    "app/models/deployment.py",
    "app/models/progress.py",
    "app/models/training.py",
    "app/models/maverick_skill.py",
    "app/models/audit.py",
    "app/models/ai_insights.py",
    "app/models/batch_trainer.py",
    "app/models/batch_job_schedule.py",
    "app/models/trainer_feedback.py",
    "app/models/requirement_workflow.py",
    "app/models/ai_usage.py",
]

def fix_file(filepath):
    """Fix UUID in a model file"""
    print(f"\n📄 {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Step 1: Replace all UUID(as_uuid=True) with GUID
        content = re.sub(r'UUID\(as_uuid=True\)', 'GUID', content)
        
        # Step 2: Update import line
        # If file has JSONB, keep it
        if ', JSONB' in content:
            content = re.sub(
                r'from sqlalchemy\.dialects\.postgresql import UUID, JSONB',
                'from sqlalchemy.dialects.postgresql import JSONB',
                content
            )
        else:
            # Remove UUID import entirely if no JSONB
            content = re.sub(
                r'from sqlalchemy\.dialects\.postgresql import UUID\n',
                '',
                content
            )
        
        # Step 3: Add GUID import after database import
        if 'from .types import GUID' not in content:
            content = re.sub(
                r'(from \.\.database import Base)',
                r'from .types import GUID\n\1',
                content
            )
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ Fixed")
            return True
        else:
            print(f"   ⏭️ No changes")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 70)
    print("🔧 Batch fixing UUID imports")
    print("=" * 70)
    
    fixed = 0
    for file in FILES_TO_FIX:
        if fix_file(file):
            fixed += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Fixed {fixed}/{len(FILES_TO_FIX)} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
