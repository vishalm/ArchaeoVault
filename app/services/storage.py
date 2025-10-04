"""
Storage management service for ArchaeoVault.

This module provides file storage functionality supporting both local
and cloud storage (AWS S3) following 12-Factor App principles.
"""

import asyncio
import hashlib
import logging
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import aiofiles
import boto3
from botocore.exceptions import ClientError

from ..config import StorageSettings


class StorageManager:
    """
    File storage management service.
    
    This class provides unified file storage functionality supporting
    both local filesystem and cloud storage (AWS S3).
    """
    
    def __init__(self, settings: StorageSettings):
        self.settings = settings
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Storage configuration
        self.storage_type = settings.storage_type
        self.storage_path = Path(settings.storage_path)
        self.max_upload_size = settings.max_upload_size_mb * 1024 * 1024  # Convert to bytes
        self.allowed_types = settings.allowed_file_types
        
        # AWS S3 configuration
        self.s3_client = None
        self.s3_bucket = settings.aws_s3_bucket
        
        # Connection state
        self.is_initialized = False
        
        self.logger.info("Storage manager initialized with type: %s", self.storage_type)
    
    async def initialize(self) -> None:
        """Initialize storage system."""
        try:
            if self.storage_type == "local":
                await self._initialize_local_storage()
            elif self.storage_type == "s3":
                await self._initialize_s3_storage()
            else:
                raise ValueError(f"Unsupported storage type: {self.storage_type}")
            
            self.is_initialized = True
            self.logger.info("Storage system initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize storage: %s", e)
            raise e
    
    async def _initialize_local_storage(self) -> None:
        """Initialize local filesystem storage."""
        # Create storage directory if it doesn't exist
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        subdirs = ["artifacts", "excavations", "reports", "temp"]
        for subdir in subdirs:
            (self.storage_path / subdir).mkdir(exist_ok=True)
        
        self.logger.info("Local storage initialized at %s", self.storage_path)
    
    async def _initialize_s3_storage(self) -> None:
        """Initialize AWS S3 storage."""
        if not self.settings.aws_access_key_id or not self.settings.aws_secret_access_key:
            raise ValueError("AWS credentials not provided")
        
        if not self.s3_bucket:
            raise ValueError("S3 bucket not specified")
        
        # Create S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key,
            region_name=self.settings.aws_region
        )
        
        # Test S3 connection
        try:
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
            self.logger.info("S3 storage initialized with bucket: %s", self.s3_bucket)
        except ClientError as e:
            self.logger.error("Failed to connect to S3 bucket: %s", e)
            raise e
    
    async def upload_file(self, file_data: bytes, filename: str, 
                         category: str = "general", 
                         metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Upload a file to storage.
        
        Args:
            file_data: File content as bytes
            filename: Original filename
            category: File category (artifacts, excavations, reports, etc.)
            metadata: Additional metadata
            
        Returns:
            Upload result with file information
        """
        if not self.is_initialized:
            raise Exception("Storage not initialized")
        
        # Validate file
        await self._validate_file(file_data, filename)
        
        # Generate unique filename
        file_id = self._generate_file_id(file_data, filename)
        file_extension = Path(filename).suffix
        unique_filename = f"{file_id}{file_extension}"
        
        # Determine storage path
        if self.storage_type == "local":
            file_path = self.storage_path / category / unique_filename
            await self._upload_to_local(file_data, file_path)
            file_url = f"/storage/{category}/{unique_filename}"
        elif self.storage_type == "s3":
            s3_key = f"{category}/{unique_filename}"
            await self._upload_to_s3(file_data, s3_key, metadata)
            file_url = f"https://{self.s3_bucket}.s3.{self.settings.aws_region}.amazonaws.com/{s3_key}"
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
        
        # Create file info
        file_info = {
            "file_id": file_id,
            "original_filename": filename,
            "stored_filename": unique_filename,
            "file_size": len(file_data),
            "file_type": mimetypes.guess_type(filename)[0] or "application/octet-stream",
            "category": category,
            "file_url": file_url,
            "upload_date": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.logger.info("File uploaded successfully: %s", file_id)
        return file_info
    
    async def download_file(self, file_id: str, category: str = "general") -> bytes:
        """
        Download a file from storage.
        
        Args:
            file_id: File identifier
            category: File category
            
        Returns:
            File content as bytes
        """
        if not self.is_initialized:
            raise Exception("Storage not initialized")
        
        if self.storage_type == "local":
            return await self._download_from_local(file_id, category)
        elif self.storage_type == "s3":
            return await self._download_from_s3(file_id, category)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
    
    async def delete_file(self, file_id: str, category: str = "general") -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_id: File identifier
            category: File category
            
        Returns:
            True if deleted successfully
        """
        if not self.is_initialized:
            return False
        
        try:
            if self.storage_type == "local":
                return await self._delete_from_local(file_id, category)
            elif self.storage_type == "s3":
                return await self._delete_from_s3(file_id, category)
            else:
                return False
                
        except Exception as e:
            self.logger.error("Failed to delete file %s: %s", file_id, e)
            return False
    
    async def get_file_info(self, file_id: str, category: str = "general") -> Optional[Dict[str, Any]]:
        """
        Get file information.
        
        Args:
            file_id: File identifier
            category: File category
            
        Returns:
            File information or None if not found
        """
        if not self.is_initialized:
            return None
        
        try:
            if self.storage_type == "local":
                return await self._get_local_file_info(file_id, category)
            elif self.storage_type == "s3":
                return await self._get_s3_file_info(file_id, category)
            else:
                return None
                
        except Exception as e:
            self.logger.error("Failed to get file info for %s: %s", file_id, e)
            return None
    
    async def list_files(self, category: str = "general", 
                        prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List files in a category.
        
        Args:
            category: File category
            prefix: Optional filename prefix filter
            
        Returns:
            List of file information
        """
        if not self.is_initialized:
            return []
        
        try:
            if self.storage_type == "local":
                return await self._list_local_files(category, prefix)
            elif self.storage_type == "s3":
                return await self._list_s3_files(category, prefix)
            else:
                return []
                
        except Exception as e:
            self.logger.error("Failed to list files in category %s: %s", category, e)
            return []
    
    async def _validate_file(self, file_data: bytes, filename: str) -> None:
        """Validate file before upload."""
        # Check file size
        if len(file_data) > self.max_upload_size:
            raise ValueError(f"File too large. Maximum size: {self.max_upload_size} bytes")
        
        # Check file type
        file_type = mimetypes.guess_type(filename)[0]
        if file_type and file_type not in self.allowed_types:
            raise ValueError(f"File type not allowed. Allowed types: {self.allowed_types}")
    
    def _generate_file_id(self, file_data: bytes, filename: str) -> str:
        """Generate unique file ID based on content and filename."""
        content_hash = hashlib.sha256(file_data).hexdigest()[:16]
        timestamp = int(datetime.utcnow().timestamp())
        return f"{timestamp}_{content_hash}"
    
    async def _upload_to_local(self, file_data: bytes, file_path: Path) -> None:
        """Upload file to local storage."""
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_data)
    
    async def _upload_to_s3(self, file_data: bytes, s3_key: str, 
                           metadata: Optional[Dict[str, Any]] = None) -> None:
        """Upload file to S3."""
        extra_args = {}
        if metadata:
            extra_args['Metadata'] = {str(k): str(v) for k, v in metadata.items()}
        
        self.s3_client.put_object(
            Bucket=self.s3_bucket,
            Key=s3_key,
            Body=file_data,
            **extra_args
        )
    
    async def _download_from_local(self, file_id: str, category: str) -> bytes:
        """Download file from local storage."""
        # Find file by ID (this is a simplified implementation)
        category_path = self.storage_path / category
        for file_path in category_path.glob(f"{file_id}*"):
            async with aiofiles.open(file_path, 'rb') as f:
                return await f.read()
        
        raise FileNotFoundError(f"File {file_id} not found in category {category}")
    
    async def _download_from_s3(self, file_id: str, category: str) -> bytes:
        """Download file from S3."""
        # Find file by ID (this is a simplified implementation)
        response = self.s3_client.list_objects_v2(
            Bucket=self.s3_bucket,
            Prefix=f"{category}/{file_id}"
        )
        
        if 'Contents' not in response:
            raise FileNotFoundError(f"File {file_id} not found in category {category}")
        
        s3_key = response['Contents'][0]['Key']
        response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=s3_key)
        return response['Body'].read()
    
    async def _delete_from_local(self, file_id: str, category: str) -> bool:
        """Delete file from local storage."""
        category_path = self.storage_path / category
        for file_path in category_path.glob(f"{file_id}*"):
            file_path.unlink()
            return True
        return False
    
    async def _delete_from_s3(self, file_id: str, category: str) -> bool:
        """Delete file from S3."""
        # Find file by ID (this is a simplified implementation)
        response = self.s3_client.list_objects_v2(
            Bucket=self.s3_bucket,
            Prefix=f"{category}/{file_id}"
        )
        
        if 'Contents' not in response:
            return False
        
        s3_key = response['Contents'][0]['Key']
        self.s3_client.delete_object(Bucket=self.s3_bucket, Key=s3_key)
        return True
    
    async def _get_local_file_info(self, file_id: str, category: str) -> Optional[Dict[str, Any]]:
        """Get local file information."""
        category_path = self.storage_path / category
        for file_path in category_path.glob(f"{file_id}*"):
            stat = file_path.stat()
            return {
                "file_id": file_id,
                "filename": file_path.name,
                "file_size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "file_path": str(file_path)
            }
        return None
    
    async def _get_s3_file_info(self, file_id: str, category: str) -> Optional[Dict[str, Any]]:
        """Get S3 file information."""
        # Find file by ID (this is a simplified implementation)
        response = self.s3_client.list_objects_v2(
            Bucket=self.s3_bucket,
            Prefix=f"{category}/{file_id}"
        )
        
        if 'Contents' not in response:
            return None
        
        s3_key = response['Contents'][0]['Key']
        response = self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_key)
        
        return {
            "file_id": file_id,
            "filename": s3_key.split('/')[-1],
            "file_size": response['ContentLength'],
            "created_at": response['LastModified'].isoformat(),
            "modified_at": response['LastModified'].isoformat(),
            "s3_key": s3_key,
            "metadata": response.get('Metadata', {})
        }
    
    async def _list_local_files(self, category: str, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """List local files."""
        category_path = self.storage_path / category
        files = []
        
        for file_path in category_path.iterdir():
            if file_path.is_file():
                if prefix and not file_path.name.startswith(prefix):
                    continue
                
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "file_size": stat.st_size,
                    "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "file_path": str(file_path)
                })
        
        return files
    
    async def _list_s3_files(self, category: str, prefix: Optional[str] = None) -> List[Dict[str, Any]]:
        """List S3 files."""
        response = self.s3_client.list_objects_v2(
            Bucket=self.s3_bucket,
            Prefix=f"{category}/"
        )
        
        files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                filename = obj['Key'].split('/')[-1]
                if prefix and not filename.startswith(prefix):
                    continue
                
                files.append({
                    "filename": filename,
                    "file_size": obj['Size'],
                    "created_at": obj['LastModified'].isoformat(),
                    "modified_at": obj['LastModified'].isoformat(),
                    "s3_key": obj['Key']
                })
        
        return files
    
    def get_storage_info(self) -> Dict[str, Any]:
        """Get storage system information."""
        return {
            "storage_type": self.storage_type,
            "storage_path": str(self.storage_path),
            "max_upload_size_mb": self.max_upload_size // (1024 * 1024),
            "allowed_types": self.allowed_types,
            "is_initialized": self.is_initialized,
            "s3_bucket": self.s3_bucket if self.storage_type == "s3" else None
        }
    
    def is_connected(self) -> bool:
        """Check if storage is connected."""
        return self.is_initialized
