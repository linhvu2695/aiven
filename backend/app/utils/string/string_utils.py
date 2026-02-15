from datetime import datetime
from typing import Any, List, Tuple, Optional


def validate_required_fields(request: Any, required_fields: List[str]) -> Tuple[bool, str]:
    """
    Validate that required fields are present and not empty in a request object.
    
    Args:
        request: The request object to validate
        required_fields: List of field names that are required
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    for field in required_fields:
        value = getattr(request, field, None)
        if value is None or (isinstance(value, str) and value.strip() == ""):
            error_msg = f"Invalid {request.__class__.__name__.lower()} info. Missing value for field: {field}"
            return False, error_msg
    
    return True, ""


def validate_exactly_one_field(request: Any, field_names: List[str]) -> Tuple[bool, str]:
    """
    Validate that exactly one of the specified fields is provided.
    
    Args:
        request: The request object to validate
        field_names: List of field names where exactly one must be provided
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not field_names or len(field_names) == 0:
        return False, "Invalid request. Must provide at least one field."
    
    values = [getattr(request, field, None) for field in field_names]
    provided_count = sum(1 for value in values if value is not None)
    
    if provided_count == 0:
        field_list = ", ".join(field_names)
        error_msg = f"Invalid {request.__class__.__name__.lower()} info. Must provide one of: {field_list}"
        return False, error_msg
    elif provided_count > 1:
        field_list = ", ".join(field_names)
        error_msg = f"Invalid {request.__class__.__name__.lower()} info. Provide only one of: {field_list}"
        return False, error_msg
    
    return True, ""


def is_empty_string(value: Optional[str]) -> bool:
    """
    Check if a value is None or an empty/whitespace-only string.
    
    Args:
        value: The value to check
    
    Returns:
        bool: True if the value is None or empty/whitespace string
    """
    return value is None or (isinstance(value, str) and value.strip() == "")


def parse_int(value, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def parse_datetime(value) -> Optional[datetime]:
    if not value or value == "":
        return None
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None


def parse_list(value, separator: str = ",") -> List[str]:
    if isinstance(value, list):
        return value
    if not value or value == "":
        return []
    return [item.strip() for item in value.split(separator) if item.strip()]

