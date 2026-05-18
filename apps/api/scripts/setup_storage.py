"""
Setup Supabase Storage buckets using REST API
Run with: python scripts/setup_storage.py
"""
import sys
from pathlib import Path
import requests
import warnings

# Disable SSL warnings for development
warnings.filterwarnings('ignore')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings

def setup_storage_buckets():
    """Create required storage buckets in Supabase using REST API"""

    print("🗄️  Setting up Supabase Storage buckets...")
    print(f"📡 Connecting to: {settings.SUPABASE_URL}\n")

    # Supabase Storage API endpoints
    base_url = f"{settings.SUPABASE_URL}/storage/v1"
    headers = {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY,
        "Content-Type": "application/json"
    }

    try:
        
        buckets_to_create = [
            {
                "id": "resumes",
                "name": "resumes",
                "public": True,
                "file_size_limit": 5242880,  # 5MB
            },
            {
                "id": "excel-files",
                "name": "excel-files",
                "public": True,
                "file_size_limit": 10485760,  # 10MB
            },
            {
                "id": "uploads",
                "name": "uploads",
                "public": True,
                "file_size_limit": 10485760,  # 10MB
            }
        ]

        # Get existing buckets
        response = requests.get(
            f"{base_url}/bucket",
            headers=headers,
            verify=False  # Disable SSL verification
        )

        if response.status_code == 200:
            existing_buckets = response.json()
            existing_bucket_names = [b.get('name') or b.get('id') for b in existing_buckets]
            print(f"📋 Found {len(existing_buckets)} existing buckets")
        else:
            print(f"⚠️  Could not list buckets: {response.status_code}")
            existing_bucket_names = []

        # Create buckets
        for bucket_config in buckets_to_create:
            bucket_id = bucket_config["id"]

            if bucket_id in existing_bucket_names:
                print(f"   ⏭️  Bucket '{bucket_id}' already exists")
            else:
                try:
                    response = requests.post(
                        f"{base_url}/bucket",
                        headers=headers,
                        json=bucket_config,
                        verify=False  # Disable SSL verification
                    )

                    if response.status_code in [200, 201]:
                        print(f"   ✓ Created bucket: {bucket_id}")
                    else:
                        print(f"   ⚠️  Could not create '{bucket_id}': {response.status_code} - {response.text}")
                except Exception as e:
                    print(f"   ⚠️  Error creating bucket '{bucket_id}': {e}")
        
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
