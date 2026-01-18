"""
Unit tests for type utilities
"""

import pytest
from typing import Dict, List, Optional, Union

from app.utils.type.type_utils import is_type_match


class TestIsTypeMatch:
    """Tests for is_type_match function"""

    # ============== None expected_type ==============
    
    def test_none_expected_type_returns_true(self):
        assert is_type_match("any value", None) is False
        assert is_type_match(123, None) is False
        assert is_type_match({"key": "value"}, None) is False
        assert is_type_match(None, None) is True

    # ============== Basic types ==============
    
    def test_str_type_match(self):
        """String value should match str type"""
        assert is_type_match("hello", str) is True
        assert is_type_match("", str) is True
        assert is_type_match(None, str) is True
    
    def test_str_type_mismatch(self):
        """Non-string value should not match str type"""
        assert is_type_match(123, str) is False
        assert is_type_match({"key": "value"}, str) is False
        assert is_type_match(["a", "b"], str) is False

    def test_int_type_match(self):
        """Integer value should match int type"""
        assert is_type_match(42, int) is True
        assert is_type_match(0, int) is True
        assert is_type_match(-100, int) is True
        assert is_type_match(None, int) is True

    def test_int_type_mismatch(self):
        """Non-integer value should not match int type"""
        assert is_type_match("42", int) is False
        assert is_type_match(3.14, int) is False

    def test_float_type_match(self):
        """Float value should match float type"""
        assert is_type_match(3.14, float) is True
        assert is_type_match(0.0, float) is True
        assert is_type_match(None, float) is True

    def test_float_type_mismatch(self):
        """Non-float value should not match float type"""
        assert is_type_match(42, float) is False
        assert is_type_match("3.14", float) is False

    def test_bool_type(self):
        """Boolean value should match bool type"""
        assert is_type_match(True, bool) is True
        assert is_type_match(False, bool) is True
        assert is_type_match(None, bool) is True

    def test_dict_type_match(self):
        """Dict value should match dict type"""
        assert is_type_match({}, dict) is True
        assert is_type_match({"key": "value"}, dict) is True
        assert is_type_match({"key": [1, 2, 3]}, dict) is True
        assert is_type_match({"key": {"subkey": "value"}}, dict) is True
        assert is_type_match(None, dict) is True

    def test_dict_type_mismatch(self):
        """Non-dict value should not match dict type"""
        assert is_type_match(1, dict) is False
        assert is_type_match(True, dict) is False
        assert is_type_match("not a dict", dict) is False
        assert is_type_match([1, 2, 3], dict) is False

    def test_list_type_match(self):
        """List value should match list type"""
        assert is_type_match([], list) is True
        assert is_type_match([1, 2, 3], list) is True
        assert is_type_match(["a", "b"], list) is True
        assert is_type_match(None, list) is True

    def test_list_type_mismatch(self):
        """Non-list value should not match list type"""
        assert is_type_match("not a list", list) is False
        assert is_type_match({"key": "value"}, list) is False
        assert is_type_match(1, list) is False
        assert is_type_match(True, list) is False

    # ============== Union types ==============
    
    def test_union_type_first_match(self):
        """Value matching first type in Union should match"""
        assert is_type_match("hello", Union[str, int]) is True  # type: ignore[arg-type]

    def test_union_type_second_match(self):
        """Value matching second type in Union should match"""
        assert is_type_match(42, Union[str, int]) is True  # type: ignore[arg-type]

    def test_union_type_no_match(self):
        """Value matching none of the Union types should not match"""
        assert is_type_match(3.14, Union[str, int]) is False  # type: ignore[arg-type]
        assert is_type_match({"key": "value"}, Union[str, int]) is False  # type: ignore[arg-type]

    # ============== Optional types (Union[T, None]) ==============
    
    def test_optional_type_with_value(self):
        """Non-None value should match Optional type"""
        assert is_type_match("hello", Optional[str]) is True  # type: ignore[arg-type]

    def test_optional_type_with_none(self):
        """None should match Optional type"""
        assert is_type_match(None, Optional[str]) is True  # type: ignore[arg-type]

    def test_optional_type_wrong_value(self):
        """Wrong type value should not match Optional type"""
        assert is_type_match(123, Optional[str]) is False  # type: ignore[arg-type]

    # ============== Generic types (List[T], Dict[K, V]) ==============
    
    def test_generic_list_type_match(self):
        """List value should match List[T] generic type"""
        assert is_type_match([1, 2, 3], List[int]) is True
        assert is_type_match(["a", "b"], List[str]) is True
        # Note: is_type_match only checks the container type, not element types
        assert is_type_match(["a", "b"], List[int]) is True

    def test_generic_list_type_mismatch(self):
        """Non-list value should not match List[T] generic type"""
        assert is_type_match("not a list", List[str]) is False
        assert is_type_match({"key": "value"}, List[str]) is False

    def test_generic_dict_type_match(self):
        """Dict value should match Dict[K, V] generic type"""
        assert is_type_match({"key": "value"}, Dict[str, str]) is True
        assert is_type_match({1: "one"}, Dict[int, str]) is True
        # Note: is_type_match only checks the container type, not key/value types
        assert is_type_match({1: 2}, Dict[str, str]) is True

    def test_generic_dict_type_mismatch(self):
        """Non-dict value should not match Dict[K, V] generic type"""
        assert is_type_match("not a dict", Dict[str, str]) is False
        assert is_type_match([1, 2, 3], Dict[str, str]) is False

    # ============== Edge cases ==============
    
    def test_none_value_with_non_optional_type(self):
        """None value should match any type (for mock flexibility)"""
        assert is_type_match(None, str) is True
        assert is_type_match(None, int) is True
        assert is_type_match(None, dict) is True

    def test_nested_union_optional(self):
        """Nested Union with Optional should work"""
        assert is_type_match("hello", Optional[Union[str, int]]) is True  # type: ignore[arg-type]
        assert is_type_match(42, Optional[Union[str, int]]) is True  # type: ignore[arg-type]
        assert is_type_match(None, Optional[Union[str, int]]) is True  # type: ignore[arg-type]
        assert is_type_match(3.14, Optional[Union[str, int]]) is False  # type: ignore[arg-type]
