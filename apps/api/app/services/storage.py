"""
Supabase Storage service using REST API (bypasses SSL issues)
"""
import requests
from typing import Optional
from datetime import datetime
import warnings

# Disable SSL warnings
warnings.filterwarnings('ignore')
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from ..config import settings

# Supabase Storage API base URL
STORAGE_API_URL = f"{settings.SUPABASE_URL}/storage/v1"

# Common headers for all requests
def get_headers():
    return {
        "Authorization": f"Bearer {settings.SUPABASE_SERVICE_KEY}",
        "apikey": settings.SUPABASE_SERVICE_KEY
    }

# Storage buckets
RESUME_BUCKET = "resumes"
EXCEL_BUCKET = "excel-files"
GENERAL_BUCKET = "uploads"


def upload_file(
    file_content: bytes,
    file_name: str,
    bucket_name: str = GENERAL_BUCKET,
    content_type: Optional[str] = None
) -> dict:
    """
    Upload file to Supabase Storage using REST API

    Args:
        file_content: File content as bytes
        file_name: Name of the file
        bucket_name: Bucket to upload to
        content_type: MIME type of the file

    Returns:
        dict with file_path and public_url
    """
    # Create unique file path with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"{timestamp}_{file_name}"

    # Upload using REST API
    headers = get_headers()
    if content_type:
        headers["Content-Type"] = content_type

    response = requests.post(
        f"{STORAGE_API_URL}/object/{bucket_name}/{file_path}",
        headers=headers,
        data=file_content,
        verify=False  # Disable SSL verification
    )

    if response.status_code not in [200, 201]:
        raise Exception(f"Upload failed: {response.status_code} - {response.text}")

    # Get public URL
    public_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_path}"

    return {
        "file_path": file_path,
        "public_url": public_url,
        "bucket": bucket_name
    }


def upload_resume(file_content: bytes, file_name: str, content_type: str) -> dict:
    """Upload resume to resumes bucket"""
    return upload_file(file_content, file_name, RESUME_BUCKET, content_type)


def upload_excel(file_content: bytes, file_name: str, content_type: str) -> dict:
    """Upload Excel file to excel-files bucket"""
    return upload_file(file_content, file_name, EXCEL_BUCKET, content_type)


def download_file(file_path: str, bucket_name: str = GENERAL_BUCKET) -> bytes:
    """
    Download file from Supabase Storage using REST API

    Args:
        file_path: Path to file in bucket
        bucket_name: Bucket name

    Returns:
        File content as bytes
    """
    response = requests.get(
        f"{STORAGE_API_URL}/object/{bucket_name}/{file_path}",
        headers=get_headers(),
        verify=False  # Disable SSL verification
    )

    if response.status_code != 200:
        raise Exception(f"Download failed: {response.status_code}")

    return response.content


def delete_file(file_path: str, bucket_name: str = GENERAL_BUCKET) -> bool:
    """
    Delete file from Supabase Storage using REST API

    Args:
        file_path: Path to file in bucket
        bucket_name: Bucket name

    Returns:
        True if successful
    """
    try:
        response = requests.delete(
            f"{STORAGE_API_URL}/object/{bucket_name}/{file_path}",
            headers=get_headers(),
            verify=False  # Disable SSL verification
        )
        return response.status_code in [200, 204]
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def get_file_url(file_path: str, bucket_name: str = GENERAL_BUCKET) -> str:
    """
    Get public URL for a file

    Args:
        file_path: Path to file in bucket
        bucket_name: Bucket name

    Returns:
        Public URL string
    """
    return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{file_path}"


def create_signed_url(
    file_path: str,
    bucket_name: str = GENERAL_BUCKET,
    expires_in: int = 3600
) -> str:
    """
    Create signed URL for private file access using REST API

    Args:
        file_path: Path to file in bucket
        bucket_name: Bucket name
        expires_in: Expiration time in seconds (default 1 hour)

    Returns:
        Signed URL string
    """
    response = requests.post(
        f"{STORAGE_API_URL}/object/sign/{bucket_name}/{file_path}",
        headers=get_headers(),
        json={"expiresIn": expires_in},
        verify=False  # Disable SSL verification
    )

    if response.status_code == 200:
        return response.json().get("signedURL", "")
    return ""


def list_files(bucket_name: str = GENERAL_BUCKET, folder: str = "") -> list:
    """
    List files in a bucket/folder using REST API

    Args:
        bucket_name: Bucket name
        folder: Folder path (optional)

    Returns:
        List of file objects
    """
    response = requests.post(
        f"{STORAGE_API_URL}/object/list/{bucket_name}",
        headers=get_headers(),
        json={"prefix": folder} if folder else {},
        verify=False  # Disable SSL verification
    )

    if response.status_code == 200:
        return response.json()
    return []
