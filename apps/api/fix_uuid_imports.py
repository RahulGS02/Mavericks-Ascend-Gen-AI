"""
Script to fix UUID imports in all model files for SQLite compatibility
"""
import re
from pathlib import Path

# List of model files that need fixing
MODEL_FILES = [
    "app/models/pipeline.py",
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
]

def fix_file(filepath):
    """Fix UUID usage in a single file"""
    print(f"\n📄 Processing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes = 0
    
    # Replace UUID(as_uuid=True) with GUID
    new_content, count = re.subn(r'UUID\(as_uuid=True\)', 'GUID', content)
    changes += count
    if count > 0:
        print(f"   ✅ Replaced {count} UUID(as_uuid=True) with GUID")
    
    # Update import statement
    import_pattern = r'from sqlalchemy\.dialects\.postgresql import UUID(, JSONB)?'
    if 'JSONB' in new_content:
        replacement = r'from sqlalchemy.dialects.postgresql import JSONB'
    else:
        replacement = ''
    
    new_content2, count2 = re.subn(import_pattern, replacement, new_content)
    if count2 > 0:
        print(f"   ✅ Updated import statement")
        changes += count2
   
    # Add GUID import if not present and if we made UUID changes
    if changes > 0 and 'from .types import GUID' not in new_content2:
        # Find the last import line before the Base import
        base_import_match = re.search(r'from \.\.database import Base', new_content2)
        if base_import_match:
            insert_pos = base_import_match.start()
            new_content2 = new_content2[:insert_pos] + 'from .types import GUID\n' + new_content2[insert_pos:]
            print(f"   ✅ Added GUID import")
    
    if new_content2 != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content2)
        print(f"   ✨ File updated successfully ({changes} changes)")
        return True
    else:
        print(f"   ⏭️  No changes needed")
        return False

def main():
    print("=" * 70)
    print("🔧 Fixing UUID imports for SQLite compatibility")
    print("=" * 70)
    
    total_fixed = 0
    
    for model_file in MODEL_FILES:
        if fix_file(model_file):
            total_fixed += 1
    
    print("\n" + "=" * 70)
    print(f"✅ Fixed {total_fixed}/{len(MODEL_FILES)} files")
    print("=" * 70)

if __name__ == "__main__":
    main()
