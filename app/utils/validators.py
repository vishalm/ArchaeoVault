"""
Validation utilities for ArchaeoVault.

This module provides validation functions for various data types
and formats used throughout the application.
"""

import re
import uuid
from typing import Any, List, Optional, Tuple, Union

from .exceptions import ValidationError


def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_uuid(uuid_string: str) -> bool:
    """
    Validate UUID format.
    
    Args:
        uuid_string: UUID string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not uuid_string or not isinstance(uuid_string, str):
        return False
    
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False


def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """
    Validate file type based on filename extension.
    
    Args:
        filename: Filename to validate
        allowed_types: List of allowed MIME types
        
    Returns:
        True if valid, False otherwise
    """
    if not filename or not isinstance(filename, str):
        return False
    
    import mimetypes
    file_type, _ = mimetypes.guess_type(filename)
    
    if not file_type:
        return False
    
    return file_type in allowed_types


def validate_file_size(file_size: int, max_size: int) -> bool:
    """
    Validate file size.
    
    Args:
        file_size: File size in bytes
        max_size: Maximum allowed size in bytes
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(file_size, int) or file_size < 0:
        return False
    
    return file_size <= max_size


def validate_coordinates(latitude: float, longitude: float) -> bool:
    """
    Validate geographic coordinates.
    
    Args:
        latitude: Latitude value
        longitude: Longitude value
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        return False
    
    return -90 <= latitude <= 90 and -180 <= longitude <= 180


def validate_password_strength(password: str) -> Tuple[bool, List[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    if not password or not isinstance(password, str):
        errors.append("Password is required")
        return False, errors
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return len(errors) == 0, errors


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(pattern.match(url))


def validate_date_range(start_date: str, end_date: str) -> bool:
    """
    Validate date range (start_date should be before end_date).
    
    Args:
        start_date: Start date string (ISO format)
        end_date: End date string (ISO format)
        
    Returns:
        True if valid, False otherwise
    """
    try:
        from datetime import datetime
        
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        return start < end
    except (ValueError, TypeError):
        return False


def validate_json_schema(data: Any, schema: dict) -> Tuple[bool, List[str]]:
    """
    Validate data against JSON schema.
    
    Args:
        data: Data to validate
        schema: JSON schema
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    try:
        import jsonschema
        jsonschema.validate(data, schema)
        return True, []
    except jsonschema.ValidationError as e:
        return False, [e.message]
    except Exception as e:
        return False, [str(e)]


def validate_artifact_data(data: dict) -> Tuple[bool, List[str]]:
    """
    Validate artifact data structure.
    
    Args:
        data: Artifact data dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'material', 'period']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Required field '{field}' is missing")
    
    # Validate material
    if 'material' in data:
        valid_materials = ['ceramic', 'metal', 'stone', 'bone', 'wood', 'textile', 'glass', 'ivory', 'shell', 'other']
        if data['material'] not in valid_materials:
            errors.append(f"Invalid material: {data['material']}")
    
    # Validate period
    if 'period' in data:
        valid_periods = ['paleolithic', 'mesolithic', 'neolithic', 'bronze_age', 'iron_age', 
                        'classical', 'medieval', 'renaissance', 'modern', 'unknown']
        if data['period'] not in valid_periods:
            errors.append(f"Invalid period: {data['period']}")
    
    # Validate condition score
    if 'condition_score' in data:
        try:
            score = int(data['condition_score'])
            if not (1 <= score <= 10):
                errors.append("Condition score must be between 1 and 10")
        except (ValueError, TypeError):
            errors.append("Condition score must be a number")
    
    # Validate dimensions
    if 'dimensions' in data and isinstance(data['dimensions'], dict):
        for key, value in data['dimensions'].items():
            try:
                float_value = float(value)
                if float_value <= 0:
                    errors.append(f"Dimension '{key}' must be positive")
            except (ValueError, TypeError):
                errors.append(f"Dimension '{key}' must be a number")
    
    return len(errors) == 0, errors


def validate_civilization_data(data: dict) -> Tuple[bool, List[str]]:
    """
    Validate civilization data structure.
    
    Args:
        data: Civilization data dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'civilization_type', 'time_period']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Required field '{field}' is missing")
    
    # Validate civilization type
    if 'civilization_type' in data:
        valid_types = ['empire', 'kingdom', 'city_state', 'tribal', 'nomadic', 
                      'agricultural', 'urban', 'other']
        if data['civilization_type'] not in valid_types:
            errors.append(f"Invalid civilization type: {data['civilization_type']}")
    
    # Validate time period
    if 'time_period' in data and isinstance(data['time_period'], dict):
        period = data['time_period']
        if 'start_year' not in period or 'end_year' not in period:
            errors.append("Time period must have start_year and end_year")
        else:
            try:
                start_year = int(period['start_year'])
                end_year = int(period['end_year'])
                if start_year > end_year:
                    errors.append("Start year must be before end year")
            except (ValueError, TypeError):
                errors.append("Time period years must be numbers")
    
    return len(errors) == 0, errors


def validate_excavation_data(data: dict) -> Tuple[bool, List[str]]:
    """
    Validate excavation data structure.
    
    Args:
        data: Excavation data dictionary
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    # Required fields
    required_fields = ['site_name', 'site_type', 'excavation_method']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Required field '{field}' is missing")
    
    # Validate site type
    if 'site_type' in data:
        valid_types = ['settlement', 'burial', 'ritual', 'industrial', 'defensive', 
                      'agricultural', 'temporary', 'other']
        if data['site_type'] not in valid_types:
            errors.append(f"Invalid site type: {data['site_type']}")
    
    # Validate excavation method
    if 'excavation_method' in data:
        valid_methods = ['stratigraphic', 'arbitrary', 'mixed', 'mechanical', 'manual']
        if data['excavation_method'] not in valid_methods:
            errors.append(f"Invalid excavation method: {data['excavation_method']}")
    
    # Validate dates
    if 'start_date' in data and 'end_date' in data:
        if not validate_date_range(data['start_date'], data['end_date']):
            errors.append("Start date must be before end date")
    
    return len(errors) == 0, errors
