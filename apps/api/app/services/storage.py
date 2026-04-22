"""
Supabase Storage service for file upload/download
"""
from supabase import create_client, Client
from typing import Optional
import os
from datetime import datetime
from ..config import settings

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

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
    Upload file to Supabase Storage
    
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
    
    # Upload to Supabase
    response = supabase.storage.from_(bucket_name).upload(
        path=file_path,
        file=file_content,
        file_options={"content-type": content_type} if content_type else {}
    )
    
    # Get public URL
    public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
    
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
    Download file from Supabase Storage
    
    Args:
        file_path: Path to file in bucket
        bucket_name: Bucket name
        
    Returns:
        File content as bytes
    """
    response = supabase.storage.from_(bucket_name).download(file_path)
    return response


def delete_file(file_path: str, bucket_name: str = GENERAL_BUCKET) -> bool:
    """
    Delete file from Supabase Storage
    
    Args:
        file_path: Path to file in bucket
        bucket_name: Bucket name
        
    Returns:
        True if successful
    """
    try:
        supabase.storage.from_(bucket_name).remove([file_path])
        return True
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
    return supabase.storage.from_(bucket_name).get_public_url(file_path)


def create_signed_url(
    file_path: str,
    bucket_name: str = GENERAL_BUCKET,
    expires_in: int = 3600
) -> str:
    """
    Create signed URL for private file access
    
    Args:
        file_path: Path to file in bucket
        bucket_name: Bucket name
        expires_in: Expiration time in seconds (default 1 hour)
        
    Returns:
        Signed URL string
    """
    response = supabase.storage.from_(bucket_name).create_signed_url(
        file_path,
        expires_in
    )
    return response.get("signedURL", "")


def list_files(bucket_name: str = GENERAL_BUCKET, folder: str = "") -> list:
    """
    List files in a bucket/folder
    
    Args:
        bucket_name: Bucket name
        folder: Folder path (optional)
        
    Returns:
        List of file objects
    """
    response = supabase.storage.from_(bucket_name).list(folder)
    return response
