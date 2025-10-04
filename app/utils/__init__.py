"""
Utility modules for ArchaeoVault.

This module contains helper functions, logging configuration,
exception handling, and other utility functionality.
"""

from .logging import setup_logging
from .exceptions import (
    ArchaeoVaultError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ServiceError,
    DatabaseError,
    CacheError,
    StorageError,
    AIAgentError
)
from .validators import (
    validate_email,
    validate_uuid,
    validate_file_type,
    validate_file_size,
    validate_coordinates
)
from .helpers import (
    generate_uuid,
    format_datetime,
    format_file_size,
    sanitize_filename,
    calculate_distance,
    calculate_bearing
)

__all__ = [
    # Logging
    "setup_logging",
    
    # Exceptions
    "ArchaeoVaultError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "ServiceError",
    "DatabaseError",
    "CacheError",
    "StorageError",
    "AIAgentError",
    
    # Validators
    "validate_email",
    "validate_uuid",
    "validate_file_type",
    "validate_file_size",
    "validate_coordinates",
    
    # Helpers
    "generate_uuid",
    "format_datetime",
    "format_file_size",
    "sanitize_filename",
    "calculate_distance",
    "calculate_bearing",
]
