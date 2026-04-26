"""
Custom error classes and error handling utilities
"""


class ValidationError(Exception):
    """Raised when input validation fails"""
    pass


class ServiceError(Exception):
    """Raised when a service encounters an error"""
    pass


class AuthenticationError(Exception):
    """Raised when API authentication fails"""
    pass


def handle_error(error_type: str, message: str, details: dict = None):
    """
    Standardized error handling
    
    Args:
        error_type: Type of error (validation, service, auth, etc)
        message: Error message
        details: Additional error details
    """
    error_response = {
        'error': True,
        'type': error_type,
        'message': message,
        'details': details or {}
    }
    return error_response
