"""
Helper utilities for ArchaeoVault.

This module provides various helper functions for common operations
used throughout the application.
"""

import hashlib
import math
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


def generate_uuid() -> str:
    """Generate a new UUID string."""
    return str(uuid.uuid4())


def format_datetime(dt: datetime, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object
        format_string: Format string
        
    Returns:
        Formatted datetime string
    """
    if dt is None:
        return ""
    
    return dt.strftime(format_string)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Human readable size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed_file"
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    # Limit length
    if len(filename) > 255:
        name, ext = Path(filename).stem, Path(filename).suffix
        filename = name[:255 - len(ext)] + ext
    
    return filename


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points using Haversine formula.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        
    Returns:
        Distance in kilometers
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    # Earth's radius in kilometers
    r = 6371
    
    return c * r


def calculate_bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate bearing from first point to second point.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        
    Returns:
        Bearing in degrees (0-360)
    """
    # Convert to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    
    y = math.sin(dlon) * math.cos(lat2_rad)
    x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
         math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))
    
    bearing = math.atan2(y, x)
    bearing = math.degrees(bearing)
    bearing = (bearing + 360) % 360
    
    return bearing


def generate_hash(data: Union[str, bytes], algorithm: str = "sha256") -> str:
    """
    Generate hash of data.
    
    Args:
        data: Data to hash
        algorithm: Hash algorithm (md5, sha1, sha256, sha512)
        
    Returns:
        Hash string
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    if algorithm == "md5":
        return hashlib.md5(data).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(data).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(data).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(data).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def truncate_string(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated string
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten nested dictionary.
    
    Args:
        d: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size.
    
    Args:
        lst: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def remove_duplicates(lst: List[Any], key: Optional[callable] = None) -> List[Any]:
    """
    Remove duplicates from list while preserving order.
    
    Args:
        lst: List to deduplicate
        key: Optional key function for comparison
        
    Returns:
        List without duplicates
    """
    seen = set()
    result = []
    
    for item in lst:
        if key:
            item_key = key(item)
        else:
            item_key = item
        
        if item_key not in seen:
            seen.add(item_key)
            result.append(item)
    
    return result


def get_nested_value(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """
    Get nested value from dictionary using dot notation.
    
    Args:
        data: Dictionary to search
        key_path: Dot-separated key path (e.g., "user.profile.name")
        default: Default value if key not found
        
    Returns:
        Value at key path or default
    """
    keys = key_path.split('.')
    current = data
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    
    return current


def set_nested_value(data: Dict[str, Any], key_path: str, value: Any) -> None:
    """
    Set nested value in dictionary using dot notation.
    
    Args:
        data: Dictionary to modify
        key_path: Dot-separated key path (e.g., "user.profile.name")
        value: Value to set
    """
    keys = key_path.split('.')
    current = data
    
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value


def is_valid_email(email: str) -> bool:
    """
    Check if email address is valid.
    
    Args:
        email: Email address to check
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_url(url: str) -> bool:
    """
    Check if URL is valid.
    
    Args:
        url: URL to check
        
    Returns:
        True if valid, False otherwise
    """
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(pattern.match(url))


def get_current_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def parse_timestamp(timestamp: str) -> Optional[datetime]:
    """
    Parse timestamp string to datetime object.
    
    Args:
        timestamp: Timestamp string
        
    Returns:
        Datetime object or None if invalid
    """
    try:
        # Try parsing with timezone info
        if timestamp.endswith('Z'):
            timestamp = timestamp[:-1] + '+00:00'
        
        return datetime.fromisoformat(timestamp)
    except (ValueError, TypeError):
        return None


def mask_sensitive_data(data: str, visible_chars: int = 4) -> str:
    """
    Mask sensitive data for logging.
    
    Args:
        data: Data to mask
        visible_chars: Number of characters to keep visible
        
    Returns:
        Masked data string
    """
    if not data or len(data) <= visible_chars:
        return "*" * len(data) if data else ""
    
    return data[:visible_chars] + "*" * (len(data) - visible_chars)
