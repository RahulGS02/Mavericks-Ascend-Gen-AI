"""
Quick script to fix remaining UUID(as_uuid=True) references
"""
import re

files = [
    "app/models/deployment.py",
    "app/models/progress.py",
    "app/models/training.py",
    "app/models/maverick_skill.py",
]

for filepath in files:
    print(f"\n📄 Fixing: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Replace all UUID(as_uuid=True) with GUID
    content = re.sub(r'UUID\(as_uuid=True\)', 'GUID', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ Fixed!")
    else:
        print(f"   ⏭️  No changes needed")

print("\n✅ Done!")
