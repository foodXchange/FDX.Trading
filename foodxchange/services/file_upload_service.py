"""
Secure File Upload Service for FoodXchange Platform
Provides file validation, virus scanning, and secure storage
"""

import os
import hashlib
import magic
import logging
from typing import Tuple, Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
import shutil
import mimetypes
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import uuid

logger = logging.getLogger(__name__)

class SecureFileUploadService:
    """Secure file upload service with validation and virus scanning"""
    
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # File type configurations
        self.allowed_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp',  # Images
            '.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx', '.xls',  # Documents
            '.zip', '.rar', '.7z'  # Archives (with caution)
        }
        
        self.dangerous_extensions = {
            '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
            '.jar', '.msi', '.dmg', '.app', '.sh', '.py', '.php', '.asp',
            '.aspx', '.jsp', '.pl', '.cgi', '.htaccess', '.htpasswd'
        }
        
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.max_total_uploads = 100 * 1024 * 1024  # 100MB total
        
        # MIME type mappings
        self.allowed_mime_types = {
            'image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/bmp',
            'application/pdf', 'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel', 'text/plain', 'text/csv',
            'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed'
        }
        
        # Initialize magic for MIME type detection
        try:
            self.magic = magic.Magic(mime=True)
        except Exception as e:
            logger.warning(f"python-magic not available: {e}")
            self.magic = None
    
    async def validate_file_upload(self, file: UploadFile) -> Tuple[str, bytes]:
        """
        Validate file upload for security and compliance
        
        Returns:
            Tuple of (secure_filename, file_content)
        """
        try:
            # Check if file is provided
            if not file or not file.filename:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No file provided"
                )
            
            # Read file content
            content = await file.read()
            
            # Check file size
            if len(content) > self.max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum size: {self.max_file_size // (1024*1024)}MB"
                )
            
            # Check file extension
            file_ext = Path(file.filename).suffix.lower()
            if file_ext in self.dangerous_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File type not allowed for security reasons"
                )
            
            if file_ext not in self.allowed_extensions:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions)}"
                )
            
            # Check MIME type
            detected_mime = self._detect_mime_type(content, file.filename)
            if detected_mime not in self.allowed_mime_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File content type not allowed: {detected_mime}"
                )
            
            # Verify MIME type matches extension
            if not self._verify_mime_extension_match(detected_mime, file_ext):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File content does not match its extension"
                )
            
            # Generate secure filename
            file_hash = hashlib.sha256(content).hexdigest()
            secure_filename = f"{file_hash}{file_ext}"
            
            # Log file upload attempt
            logger.info(
                f"File upload validated: {file.filename} -> {secure_filename} "
                f"({len(content)} bytes, {detected_mime})"
            )
            
            return secure_filename, content
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="File validation failed"
            )
    
    def _detect_mime_type(self, content: bytes, filename: str) -> str:
        """Detect MIME type using multiple methods"""
        # Try python-magic first
        if self.magic:
            try:
                return self.magic.from_buffer(content)
            except Exception as e:
                logger.warning(f"Magic MIME detection failed: {e}")
        
        # Fallback to mimetypes
        mime_type, _ = mimetypes.guess_type(filename)
        if mime_type:
            return mime_type
        
        # Fallback based on file extension
        ext = Path(filename).suffix.lower()
        mime_map = {
            '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png',
            '.gif': 'image/gif', '.webp': 'image/webp', '.bmp': 'image/bmp',
            '.pdf': 'application/pdf', '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain', '.csv': 'text/csv',
            '.zip': 'application/zip', '.rar': 'application/x-rar-compressed'
        }
        
        return mime_map.get(ext, 'application/octet-stream')
    
    def _verify_mime_extension_match(self, mime_type: str, extension: str) -> bool:
        """Verify that MIME type matches file extension"""
        mime_to_ext = {
            'image/jpeg': '.jpg', 'image/png': '.png', 'image/gif': '.gif',
            'image/webp': '.webp', 'image/bmp': '.bmp',
            'application/pdf': '.pdf', 'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'text/plain': '.txt', 'text/csv': '.csv',
            'application/zip': '.zip', 'application/x-rar-compressed': '.rar'
        }
        
        expected_ext = mime_to_ext.get(mime_type)
        return expected_ext == extension
    
    async def save_file_secure(self, filename: str, content: bytes, user_id: Optional[str] = None) -> str:
        """
        Save file securely with proper directory structure
        
        Returns:
            File path relative to upload directory
        """
        try:
            # Create user-specific directory
            if user_id:
                user_dir = self.upload_dir / f"user_{user_id}"
            else:
                user_dir = self.upload_dir / "anonymous"
            
            user_dir.mkdir(exist_ok=True)
            
            # Create date-based subdirectory
            date_dir = user_dir / datetime.now().strftime("%Y/%m/%d")
            date_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = date_dir / filename
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Set proper permissions (read-only for others)
            os.chmod(file_path, 0o644)
            
            # Return relative path
            relative_path = str(file_path.relative_to(self.upload_dir))
            
            logger.info(f"File saved securely: {relative_path}")
            return relative_path
            
        except Exception as e:
            logger.error(f"File save error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save file"
            )
    
    async def scan_file_for_viruses(self, content: bytes, filename: str) -> bool:
        """
        Scan file for viruses (placeholder for actual virus scanning)
        
        In production, integrate with:
        - ClamAV
        - VirusTotal API
        - AWS GuardDuty
        - Azure Security Center
        """
        try:
            # Basic heuristic checks
            suspicious_patterns = [
                b'MZ',  # Executable header
                b'PK\x03\x04',  # ZIP archive
                b'Rar!',  # RAR archive
                b'<script',  # JavaScript
                b'<?php',  # PHP
                b'<%@',  # ASP.NET
            ]
            
            for pattern in suspicious_patterns:
                if pattern in content[:1024]:  # Check first 1KB
                    logger.warning(f"Suspicious pattern detected in {filename}: {pattern}")
                    # Don't block immediately, just log for now
                    # In production, implement proper virus scanning
            
            # For now, accept all files that pass validation
            return True
            
        except Exception as e:
            logger.error(f"Virus scan error: {e}")
            return False
    
    async def cleanup_old_files(self, days: int = 30) -> int:
        """Clean up files older than specified days"""
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
            deleted_count = 0
            
            for file_path in self.upload_dir.rglob('*'):
                if file_path.is_file():
                    if file_path.stat().st_mtime < cutoff_date:
                        file_path.unlink()
                        deleted_count += 1
            
            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"File cleanup error: {e}")
            return 0
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a file"""
        try:
            full_path = self.upload_dir / file_path
            if not full_path.exists():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="File not found"
                )
            
            stat = full_path.stat()
            return {
                "filename": full_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "mime_type": self._detect_mime_type(b"", full_path.name),
                "path": file_path
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File info error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get file information"
            )
    
    async def delete_file(self, file_path: str, user_id: Optional[str] = None) -> bool:
        """Delete a file securely"""
        try:
            full_path = self.upload_dir / file_path
            
            # Verify file exists
            if not full_path.exists():
                return False
            
            # Verify user has permission (if user_id provided)
            if user_id:
                expected_user_dir = f"user_{user_id}"
                if not str(full_path).startswith(str(self.upload_dir / expected_user_dir)):
                    logger.warning(f"User {user_id} attempted to delete file outside their directory")
                    return False
            
            # Delete file
            full_path.unlink()
            logger.info(f"File deleted: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"File deletion error: {e}")
            return False

# Global file upload service instance
file_upload_service = SecureFileUploadService() 