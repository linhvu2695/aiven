"""
Type utilities for runtime type checking and validation.
"""

from typing import Any, Union, get_origin, get_args


def is_type_match(value: Any, expected_type: Any) -> bool:
    """
    Check if a value matches the expected type at runtime.
    
    Handles:
    - `None` expected_type: returns True only if value is None
    - `None` value: returns True (`None` matches any type for flexibility)
    - Basic types: `str`, `int`, `float`, `bool`, `dict`, `list`
    - Union types: `Union[str, int]`, `Optional[str]`
    - Generic types: `List[str]`, `Dict[str, int]` (checks container only)
    
    Args:
        value: The value to check
        expected_type: The expected type (can be None, basic type, Union, or generic)
        
    Returns:
        bool: True if value matches expected_type, False otherwise
        
    Examples:
        >>> is_type_match("hello", str)
        True
        >>> is_type_match(42, str)
        False
        >>> is_type_match("hello", Union[str, int])
        True
        >>> is_type_match(None, Optional[str])
        True
    """
    if expected_type is None:
        return value is None
    if value is None:
        return True  # None matches any type for mock flexibility
    
    origin = get_origin(expected_type)
    
    # Handle Union types (e.g., Optional[str] = Union[str, None])
    if origin is Union:
        args = get_args(expected_type)
        return any(is_type_match(value, arg) for arg in args)
    
    # Handle basic types (no generic parameters)
    if origin is None:
        return isinstance(value, expected_type)
    
    # Handle generic types like List[str], Dict[str, int]
    # Only checks the container type, not element types
    return isinstance(value, origin)
