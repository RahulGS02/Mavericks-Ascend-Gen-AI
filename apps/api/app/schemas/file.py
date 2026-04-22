"""
File upload/download schemas
"""
from pydantic import BaseModel
from typing import Optional


class FileUploadResponse(BaseModel):
    """Response schema for file upload"""
    success: bool
    message: str
    file_path: str
    public_url: str
    bucket: str
    file_name: str
    file_size: int
    content_type: str


class FileDownloadResponse(BaseModel):
    """Response schema for file download"""
    file_name: str
    content_type: str
    file_size: int


class FileDeleteResponse(BaseModel):
    """Response schema for file deletion"""
    success: bool
    message: str


class FileListItem(BaseModel):
    """Single file item in list"""
    name: str
    id: str
    created_at: str
    updated_at: str
    last_accessed_at: Optional[str] = None
    metadata: Optional[dict] = None


class FileListResponse(BaseModel):
    """Response schema for file listing"""
    files: list[FileListItem]
    count: int
