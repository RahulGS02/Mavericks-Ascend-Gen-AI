"""
Migration Runner: Execute all migrations in order
Description: Runs all workflow migrations with verification
Date: 2026-05-16
"""

import sys
import os
import importlib.util

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_migration(filename):
    """Dynamically load a migration module"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    spec = importlib.util.spec_from_file_location(filename.replace('.py', ''), filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_all_migrations():
    """Run all migrations in order"""
    
    migrations = [
        '001_create_requirement_workflow_tables.py',
        '002_create_workflow_constraints.py',
        '003_update_existing_data.py',
    ]
    
    print("=" * 80)
    print("RUNNING ALL MIGRATIONS")
    print("=" * 80)
    print(f"\nTotal migrations to run: {len(migrations)}\n")
    
    for i, migration_file in enumerate(migrations, 1):
        print(f"\n{'=' * 80}")
        print(f"Migration {i}/{len(migrations)}: {migration_file}")
        print(f"{'=' * 80}\n")
        
        try:
            migration = load_migration(migration_file)
            migration.upgrade()
            print(f"\n✅ {migration_file} completed successfully!\n")
        except Exception as e:
            print(f"\n❌ ERROR in {migration_file}: {e}\n")
            import traceback
            traceback.print_exc()
            
            response = input("\nContinue with remaining migrations? (yes/no): ")
            if response.lower() != 'yes':
                print("Migration aborted.")
                return False
    
    print("\n" + "=" * 80)
    print("✅ ALL MIGRATIONS COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    
    return True


def rollback_all_migrations():
    """Rollback all migrations in reverse order"""
    
    migrations = [
        '003_update_existing_data.py',
        '002_create_workflow_constraints.py',
        '001_create_requirement_workflow_tables.py',
    ]
    
    print("=" * 80)
    print("⚠️  ROLLING BACK ALL MIGRATIONS")
    print("=" * 80)
    print(f"\nTotal migrations to rollback: {len(migrations)}\n")
    
    confirm = input("⚠️  This will DELETE all workflow data. Are you sure? (type 'yes' to confirm): ")
    if confirm != 'yes':
        print("Rollback cancelled.")
        return False
    
    for i, migration_file in enumerate(migrations, 1):
        print(f"\n{'=' * 80}")
        print(f"Rollback {i}/{len(migrations)}: {migration_file}")
        print(f"{'=' * 80}\n")
        
        try:
            migration = load_migration(migration_file)
            migration.downgrade()
            print(f"\n✅ {migration_file} rolled back successfully!\n")
        except Exception as e:
            print(f"\n❌ ERROR in {migration_file}: {e}\n")
            import traceback
            traceback.print_exc()
            
            response = input("\nContinue with remaining rollbacks? (yes/no): ")
            if response.lower() != 'yes':
                print("Rollback aborted.")
                return False
    
    print("\n" + "=" * 80)
    print("✅ ALL MIGRATIONS ROLLED BACK!")
    print("=" * 80)
    
    return True


def verify_migrations():
    """Run verification script"""
    
    print("\n" + "=" * 80)
    print("RUNNING VERIFICATION")
    print("=" * 80 + "\n")
    
    try:
        verification = load_migration('verify_migrations.py')
        success = verification.verify()
        return success
    except Exception as e:
        print(f"\n❌ VERIFICATION FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point"""
    
    print("\n" + "=" * 80)
    print("REQUIREMENT WORKFLOW MIGRATION TOOL")
    print("=" * 80)
    print("\nOptions:")
    print("  1. Run all migrations (upgrade)")
    print("  2. Rollback all migrations (downgrade)")
    print("  3. Verify migrations")
    print("  4. Run migrations + verify")
    print("  5. Exit")
    print()
    
    choice = input("Select option (1-5): ").strip()
    
    if choice == '1':
        success = run_all_migrations()
        if success:
            print("\n✅ Migrations completed! Run option 3 to verify.")
    
    elif choice == '2':
        rollback_all_migrations()
    
    elif choice == '3':
        verify_migrations()
    
    elif choice == '4':
        print("\n🚀 Running migrations and verification...\n")
        if run_all_migrations():
            print("\n🔍 Verifying migrations...\n")
            verify_migrations()
    
    elif choice == '5':
        print("Exiting...")
        sys.exit(0)
    
    else:
        print("❌ Invalid option. Please select 1-5.")
        main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
