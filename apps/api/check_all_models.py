"""
Comprehensive check for all model files to find any remaining PostgreSQL-specific types
"""
import re
from pathlib import Path

model_files = [
    "app/models/ai_insights.py",
    "app/models/ai_usage.py",
    "app/models/assessment.py",
    "app/models/audit.py",
    "app/models/batch.py",
    "app/models/batch_job_schedule.py",
    "app/models/batch_trainer.py",
    "app/models/deployment.py",
    "app/models/maverick.py",
    "app/models/maverick_skill.py",
    "app/models/pipeline.py",
    "app/models/progress.py",
    "app/models/requirement_workflow.py",
    "app/models/trainer_feedback.py",
    "app/models/training.py",
    "app/models/user.py",
]

print("=" * 80)
print("🔍 COMPREHENSIVE MODEL FILE CHECK")
print("=" * 80)

issues_found = []

for filepath in model_files:
    print(f"\n📄 Checking: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for UUID(as_uuid=True)
        uuid_matches = re.findall(r'UUID\(as_uuid=True\)', content)
        if uuid_matches:
            count = len(uuid_matches)
            print(f"   ❌ Found {count} UUID(as_uuid=True) usage(s)")
            issues_found.append(f"{filepath}: {count} UUID(as_uuid=True)")
        
        # Check for Column(JSONB
        jsonb_matches = re.findall(r'Column\([^)]*JSONB', content)
        if jsonb_matches:
            count = len(jsonb_matches)
            print(f"   ❌ Found {count} Column(JSONB usage(s)")
            issues_found.append(f"{filepath}: {count} JSONB columns")
        
        # Check for Column(ARRAY
        array_matches = re.findall(r'Column\([^)]*ARRAY\(', content)
        if array_matches:
            count = len(array_matches)
            print(f"   ❌ Found {count} Column(ARRAY usage(s)")
            issues_found.append(f"{filepath}: {count} ARRAY columns")
        
        # Check for PostgreSQL imports
        if 'from sqlalchemy.dialects.postgresql import UUID' in content:
            if 'UUID' not in content.replace('UUID(as_uuid=True)', '').replace('from sqlalchemy.dialects.postgresql import UUID', ''):
                print(f"   ⚠️  Has UUID import but no usage (safe)")
            else:
                print(f"   ❌ Has PostgreSQL UUID import and usage")
                issues_found.append(f"{filepath}: PostgreSQL UUID import")
        
        if not uuid_matches and not jsonb_matches and not array_matches:
            print(f"   ✅ Clean - No PostgreSQL-specific types")
    
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        issues_found.append(f"{filepath}: Error - {e}")

print("\n" + "=" * 80)
if issues_found:
    print(f"❌ FOUND {len(issues_found)} ISSUE(S):")
    for issue in issues_found:
        print(f"   - {issue}")
else:
    print("✅ ALL FILES CLEAN - NO POSTGRESQL-SPECIFIC TYPES FOUND!")
print("=" * 80)
