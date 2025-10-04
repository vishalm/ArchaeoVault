"""
Custom exceptions for ArchaeoVault.

This module defines custom exception classes for different types
of errors that can occur in the application.
"""

from typing import Any, Dict, Optional


class ArchaeoVaultError(Exception):
    """Base exception class for ArchaeoVault."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary."""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class ValidationError(ArchaeoVaultError):
    """Raised when data validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None):
        super().__init__(message, error_code="VALIDATION_ERROR")
        self.field = field
        self.value = value
        self.details.update({
            "field": field,
            "value": str(value) if value is not None else None
        })


class AuthenticationError(ArchaeoVaultError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", user_id: Optional[str] = None):
        super().__init__(message, error_code="AUTHENTICATION_ERROR")
        self.user_id = user_id
        self.details.update({"user_id": user_id})


class AuthorizationError(ArchaeoVaultError):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", user_id: Optional[str] = None, resource: Optional[str] = None):
        super().__init__(message, error_code="AUTHORIZATION_ERROR")
        self.user_id = user_id
        self.resource = resource
        self.details.update({
            "user_id": user_id,
            "resource": resource
        })


class ServiceError(ArchaeoVaultError):
    """Raised when a service operation fails."""
    
    def __init__(self, message: str, service_name: Optional[str] = None, operation: Optional[str] = None):
        super().__init__(message, error_code="SERVICE_ERROR")
        self.service_name = service_name
        self.operation = operation
        self.details.update({
            "service_name": service_name,
            "operation": operation
        })


class DatabaseError(ServiceError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, query: Optional[str] = None, operation: Optional[str] = None):
        super().__init__(message, service_name="database", operation=operation)
        self.query = query
        self.details.update({"query": query})


class CacheError(ServiceError):
    """Raised when cache operations fail."""
    
    def __init__(self, message: str, key: Optional[str] = None, operation: Optional[str] = None):
        super().__init__(message, service_name="cache", operation=operation)
        self.key = key
        self.details.update({"key": key})


class StorageError(ServiceError):
    """Raised when storage operations fail."""
    
    def __init__(self, message: str, file_id: Optional[str] = None, operation: Optional[str] = None):
        super().__init__(message, service_name="storage", operation=operation)
        self.file_id = file_id
        self.details.update({"file_id": file_id})


class AIAgentError(ServiceError):
    """Raised when AI agent operations fail."""
    
    def __init__(self, message: str, agent_type: Optional[str] = None, operation: Optional[str] = None):
        super().__init__(message, service_name="ai_agent", operation=operation)
        self.agent_type = agent_type
        self.details.update({"agent_type": agent_type})


class ConfigurationError(ArchaeoVaultError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(message, error_code="CONFIGURATION_ERROR")
        self.config_key = config_key
        self.details.update({"config_key": config_key})


class ExternalServiceError(ArchaeoVaultError):
    """Raised when external service calls fail."""
    
    def __init__(self, message: str, service_name: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message, error_code="EXTERNAL_SERVICE_ERROR")
        self.service_name = service_name
        self.status_code = status_code
        self.details.update({
            "service_name": service_name,
            "status_code": status_code
        })


class RateLimitError(ArchaeoVaultError):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", limit: Optional[int] = None, 
                 window: Optional[int] = None, retry_after: Optional[int] = None):
        super().__init__(message, error_code="RATE_LIMIT_ERROR")
        self.limit = limit
        self.window = window
        self.retry_after = retry_after
        self.details.update({
            "limit": limit,
            "window": window,
            "retry_after": retry_after
        })


class TimeoutError(ArchaeoVaultError):
    """Raised when operations timeout."""
    
    def __init__(self, message: str = "Operation timed out", timeout: Optional[float] = None, 
                 operation: Optional[str] = None):
        super().__init__(message, error_code="TIMEOUT_ERROR")
        self.timeout = timeout
        self.operation = operation
        self.details.update({
            "timeout": timeout,
            "operation": operation
        })


class ResourceNotFoundError(ArchaeoVaultError):
    """Raised when a requested resource is not found."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        super().__init__(message, error_code="RESOURCE_NOT_FOUND")
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details.update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })


class ConflictError(ArchaeoVaultError):
    """Raised when there's a conflict with the current state."""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, resource_id: Optional[str] = None):
        super().__init__(message, error_code="CONFLICT_ERROR")
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details.update({
            "resource_type": resource_type,
            "resource_id": resource_id
        })


class BusinessLogicError(ArchaeoVaultError):
    """Raised when business logic validation fails."""
    
    def __init__(self, message: str, rule: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        super().__init__(message, error_code="BUSINESS_LOGIC_ERROR")
        self.rule = rule
        self.context = context or {}
        self.details.update({
            "rule": rule,
            "context": context
        })
