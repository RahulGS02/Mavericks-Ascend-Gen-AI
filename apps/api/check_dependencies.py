"""
Check if all required dependencies are installed
"""
import sys

print("=" * 80)
print("🔍 Checking Dependencies for Natural Language Query Feature")
print("=" * 80)

required_packages = {
    "Core": [
        ("fastapi", "FastAPI framework"),
        ("sqlalchemy", "Database ORM"),
        ("pydantic", "Data validation"),
        ("python-dotenv", "Environment variables"),
    ],
    "AI": [
        ("auggie", "Auggie SDK for AI"),
    ],
    "Excel": [
        ("pandas", "Data manipulation"),
        ("openpyxl", "Excel file generation"),
    ],
    "Database": [
        ("psycopg2", "PostgreSQL adapter"),
    ]
}

all_installed = True
missing_packages = []

for category, packages in required_packages.items():
    print(f"\n📦 {category} Packages:")
    for package_name, description in packages:
        try:
            # Try to import the package
            if package_name == "python-dotenv":
                import dotenv
                version = dotenv.__version__ if hasattr(dotenv, '__version__') else "unknown"
            elif package_name == "auggie":
                import auggie
                version = auggie.__version__ if hasattr(auggie, '__version__') else "unknown"
            else:
                module = __import__(package_name)
                version = module.__version__ if hasattr(module, '__version__') else "unknown"
            
            print(f"   ✅ {package_name:20} v{version:10} - {description}")
        except ImportError:
            print(f"   ❌ {package_name:20} {'NOT INSTALLED':10} - {description}")
            all_installed = False
            missing_packages.append(package_name)

print("\n" + "=" * 80)
print("📊 DEPENDENCY CHECK SUMMARY")
print("=" * 80)

if all_installed:
    print("\n✅ ALL DEPENDENCIES INSTALLED!")
    print("   Ready to run Natural Language Query feature!")
else:
    print(f"\n❌ {len(missing_packages)} package(s) missing:")
    for pkg in missing_packages:
        print(f"   - {pkg}")
    
    print("\n💡 To install missing packages:")
    print("   cd apps/api")
    print("   pip install -r requirements.txt")
    
    print("\n   Or install individually:")
    for pkg in missing_packages:
        # Map package names to pip install names
        pip_name = pkg
        if pkg == "python-dotenv":
            pip_name = "python-dotenv"
        elif pkg == "auggie":
            pip_name = "auggie-sdk"
        print(f"   pip install {pip_name}")

print("\n" + "=" * 80)

sys.exit(0 if all_installed else 1)
