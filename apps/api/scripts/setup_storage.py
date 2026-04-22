"""
Setup Supabase Storage buckets
Run with: python scripts/setup_storage.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from supabase import create_client
from app.config import settings

def setup_storage_buckets():
    """Create required storage buckets in Supabase"""
    
    print("🗄️  Setting up Supabase Storage buckets...")
    
    try:
        # Initialize Supabase client
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        
        buckets_to_create = [
            {
                "name": "resumes",
                "public": True,
                "file_size_limit": 5242880,  # 5MB
                "allowed_mime_types": [
                    "application/pdf",
                    "application/msword",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ]
            },
            {
                "name": "excel-files",
                "public": True,
                "file_size_limit": 10485760,  # 10MB
                "allowed_mime_types": [
                    "application/vnd.ms-excel",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "text/csv"
                ]
            },
            {
                "name": "uploads",
                "public": True,
                "file_size_limit": 10485760,  # 10MB
                "allowed_mime_types": None  # All types
            }
        ]
        
        # Get existing buckets
        existing_buckets = supabase.storage.list_buckets()
        existing_bucket_names = [b.name for b in existing_buckets]
        
        print(f"📋 Found {len(existing_buckets)} existing buckets")
        
        # Create buckets
        for bucket_config in buckets_to_create:
            bucket_name = bucket_config["name"]
            
            if bucket_name in existing_bucket_names:
                print(f"   ⏭️  Bucket '{bucket_name}' already exists")
            else:
                try:
                    supabase.storage.create_bucket(
                        bucket_name,
                        options={
                            "public": bucket_config["public"],
                            "file_size_limit": bucket_config["file_size_limit"],
                            "allowed_mime_types": bucket_config["allowed_mime_types"]
                        }
                    )
                    print(f"   ✓ Created bucket: {bucket_name}")
                except Exception as e:
                    print(f"   ⚠️  Error creating bucket '{bucket_name}': {e}")
        
        print("\n✅ Storage setup complete!")
        print("\n📦 Available buckets:")
        print("   • resumes - For resume files (PDF, DOC, DOCX)")
        print("   • excel-files - For Excel files (XLS, XLSX, CSV)")
        print("   • uploads - For general file uploads")
        
    except Exception as e:
        print(f"\n❌ Error setting up storage: {e}")
        print("\nPlease check:")
        print("1. SUPABASE_URL is correct in .env")
        print("2. SUPABASE_SERVICE_KEY is correct in .env")
        print("3. Your Supabase project is active")
        sys.exit(1)


if __name__ == "__main__":
    setup_storage_buckets()
