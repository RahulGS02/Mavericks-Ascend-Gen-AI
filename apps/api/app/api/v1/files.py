"""
File upload/download API endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import io

from ...schemas.file import FileUploadResponse, FileDeleteResponse, FileListResponse
from ...services import storage
from ...config import settings
from ...utils.dependencies import get_current_user
from ...models.user import User

router = APIRouter()


def validate_file_size(file: UploadFile, max_size: int, file_type: str):
    """Validate file size"""
    # Read file to get size
    file_content = file.file.read()
    file_size = len(file_content)
    
    # Reset file pointer
    file.file.seek(0)
    
    if file_size > max_size:
        max_mb = max_size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"{file_type} file size exceeds {max_mb}MB limit"
        )
    
    return file_content, file_size


def validate_file_type(content_type: str, allowed_types: list, file_type: str):
    """Validate file type"""
    if content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {file_type} file type. Allowed: {', '.join(allowed_types)}"
        )


@router.post("/upload/resume", response_model=FileUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload resume file (PDF, DOC, DOCX)
    
    - **Max size**: 5MB
    - **Allowed types**: PDF, DOC, DOCX
    """
    # Validate file type
    validate_file_type(
        file.content_type,
        settings.allowed_resume_types,
        "Resume"
    )
    
    # Validate file size
    file_content, file_size = validate_file_size(
        file,
        settings.MAX_RESUME_SIZE,
        "Resume"
    )
    
    try:
        # Upload to Supabase
        result = storage.upload_resume(
            file_content,
            file.filename,
            file.content_type
        )
        
        return FileUploadResponse(
            success=True,
            message="Resume uploaded successfully",
            file_path=result["file_path"],
            public_url=result["public_url"],
            bucket=result["bucket"],
            file_name=file.filename,
            file_size=file_size,
            content_type=file.content_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload resume: {str(e)}"
        )


@router.post("/upload/excel", response_model=FileUploadResponse)
async def upload_excel(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload Excel file (XLS, XLSX, CSV)
    
    - **Max size**: 10MB
    - **Allowed types**: XLS, XLSX, CSV
    """
    # Validate file type
    validate_file_type(
        file.content_type,
        settings.allowed_excel_types,
        "Excel"
    )
    
    # Validate file size
    file_content, file_size = validate_file_size(
        file,
        settings.MAX_EXCEL_SIZE,
        "Excel"
    )
    
    try:
        # Upload to Supabase
        result = storage.upload_excel(
            file_content,
            file.filename,
            file.content_type
        )
        
        return FileUploadResponse(
            success=True,
            message="Excel file uploaded successfully",
            file_path=result["file_path"],
            public_url=result["public_url"],
            bucket=result["bucket"],
            file_name=file.filename,
            file_size=file_size,
            content_type=file.content_type
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload Excel file: {str(e)}"
        )


@router.get("/download/{bucket}/{file_path:path}")
async def download_file(
    bucket: str,
    file_path: str,
    current_user: User = Depends(get_current_user)
):
    """
    Download file from storage
    
    - **bucket**: Bucket name (resumes, excel-files, uploads)
    - **file_path**: Path to file in bucket
    """
    try:
        file_content = storage.download_file(file_path, bucket)
        
        # Extract filename from path
        filename = file_path.split("/")[-1]
        
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File not found: {str(e)}"
        )
