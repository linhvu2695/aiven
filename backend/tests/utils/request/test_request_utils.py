import pytest
import logging
from datetime import datetime
from enum import Enum
from typing import Optional
from unittest.mock import patch, MagicMock
from pydantic import BaseModel

from app.utils.request.request_utils import build_update_data


class MockEnum(str, Enum):
    """Mock enum for testing enum handling"""
    OPTION_A = "option_a"
    OPTION_B = "option_b"
    OPTION_C = "option_c"


class MockRequestModel(BaseModel):
    """Mock Pydantic model for testing"""
    name: Optional[str] = None
    description: Optional[str] = None
    age: Optional[int] = None
    created_at: Optional[datetime] = None
    status: Optional[MockEnum] = None
    score: Optional[float] = None
    is_active: Optional[bool] = None


class MockObjectWithValue:
    """Mock object that has a 'value' attribute (like enums)"""
    def __init__(self, value):
        self.value = value


class MockObjectWithoutValue:
    """Mock object that doesn't have a 'value' attribute"""
    def __init__(self, data):
        self.data = data
    
    def __str__(self):
        return f"MockObject({self.data})"


class MockObjectSerializationError:
    """Mock object that raises AttributeError during serialization"""
    def __str__(self):
        raise AttributeError("Cannot serialize this object")


class TestBuildUpdateData:
    """Test cases for build_update_data function"""

    def test_basic_string_field(self):
        """Test basic string field handling"""
        request = MockRequestModel(name="Test Plant")
        result = build_update_data(request, ["name"])
        
        assert result == {"name": "Test Plant"}

    def test_multiple_string_fields(self):
        """Test multiple string fields"""
        request = MockRequestModel(name="Test Plant", description="A beautiful plant")
        result = build_update_data(request, ["name", "description"])
        
        assert result == {
            "name": "Test Plant", 
            "description": "A beautiful plant"
        }

    def test_integer_field(self):
        """Test integer field handling"""
        request = MockRequestModel(age=5)
        result = build_update_data(request, ["age"])
        
        assert result == {"age": "5"}

    def test_float_field(self):
        """Test float field handling"""
        request = MockRequestModel(score=95.5)
        result = build_update_data(request, ["score"])
        
        assert result == {"score": "95.5"}

    def test_boolean_field(self):
        """Test boolean field handling"""
        request = MockRequestModel(is_active=True)
        result = build_update_data(request, ["is_active"])
        
        assert result == {"is_active": "True"}

    def test_datetime_field(self):
        """Test datetime field serialization to ISO format"""
        test_datetime = datetime(2024, 1, 15, 10, 30, 45)
        request = MockRequestModel(created_at=test_datetime)
        result = build_update_data(request, ["created_at"])
        
        assert result == {"created_at": "2024-01-15T10:30:45"}

    def test_enum_field(self):
        """Test enum field handling using the value attribute"""
        request = MockRequestModel(status=MockEnum.OPTION_A)
        result = build_update_data(request, ["status"])
        
        assert result == {"status": "option_a"}

    def test_none_fields_excluded(self):
        """Test that None fields are excluded from result"""
        request = MockRequestModel(name="Test Plant", description=None, age=None)
        result = build_update_data(request, ["name", "description", "age"])
        
        assert result == {"name": "Test Plant"}

    def test_mixed_types(self):
        """Test handling of mixed data types"""
        test_datetime = datetime(2024, 1, 15, 10, 30, 45)
        request = MockRequestModel(
            name="Test Plant",
            age=5,
            created_at=test_datetime,
            status=MockEnum.OPTION_B,
            is_active=True,
            score=87.3
        )
        result = build_update_data(request, ["name", "age", "created_at", "status", "is_active", "score"])
        
        expected = {
            "name": "Test Plant",
            "age": "5",
            "created_at": "2024-01-15T10:30:45",
            "status": "option_b",
            "is_active": "True",
            "score": "87.3"
        }
        assert result == expected

    def test_empty_fields_list(self):
        """Test with empty fields list"""
        request = MockRequestModel(name="Test Plant", age=5)
        result = build_update_data(request, [])
        
        assert result == {}

    def test_nonexistent_field(self):
        """Test handling of non-existent fields"""
        request = MockRequestModel(name="Test Plant")
        
        with patch('logging.getLogger') as mock_logger:
            mock_warning_logger = MagicMock()
            mock_logger.return_value = mock_warning_logger
            
            result = build_update_data(request, ["name", "nonexistent_field"])
            
            assert result == {"name": "Test Plant"}
            mock_warning_logger.warning.assert_called_with(
                "Field nonexistent_field not found in request"
            )

    def test_object_with_value_attribute(self):
        """Test handling of objects with 'value' attribute (like enums)"""
        # Create a mock request with an object that has a value attribute
        request = MockRequestModel()
        setattr(request, "name", MockObjectWithValue("test_value"))
        
        result = build_update_data(request, ["name"])
        
        assert result == {"name": "test_value"}

    def test_object_without_value_attribute(self):
        """Test handling of objects without 'value' attribute (falls back to str())"""
        request = MockRequestModel()
        setattr(request, "name", MockObjectWithoutValue("test_data"))
        
        result = build_update_data(request, ["name"])
        
        assert result == {"name": "MockObject(test_data)"}

    def test_serialization_error_handling(self):
        """Test handling of serialization errors"""
        request = MockRequestModel()
        setattr(request, "name", MockObjectSerializationError())
        
        with patch('logging.getLogger') as mock_logger:
            mock_warning_logger = MagicMock()
            mock_logger.return_value = mock_warning_logger
            
            result = build_update_data(request, ["name"])
            
            assert result == {}
            mock_warning_logger.warning.assert_called_with(
                "Field name cannot be serialized"
            )

    def test_partial_field_selection(self):
        """Test selecting only some fields from a model with many fields"""
        request = MockRequestModel(
            name="Test Plant",
            description="Beautiful plant",
            age=5,
            status=MockEnum.OPTION_A,
            is_active=True
        )
        
        # Only select name and age
        result = build_update_data(request, ["name", "age"])
        
        assert result == {"name": "Test Plant", "age": "5"}

    def test_datetime_microseconds(self):
        """Test datetime with microseconds"""
        test_datetime = datetime(2024, 1, 15, 10, 30, 45, 123456)
        request = MockRequestModel(created_at=test_datetime)
        result = build_update_data(request, ["created_at"])
        
        assert result == {"created_at": "2024-01-15T10:30:45.123456"}

    def test_all_none_fields(self):
        """Test when all fields are None"""
        request = MockRequestModel()  # All fields are None by default
        result = build_update_data(request, ["name", "description", "age"])
        
        assert result == {}

    def test_duplicate_fields_in_list(self):
        """Test handling of duplicate field names in the fields list"""
        request = MockRequestModel(name="Test Plant")
        result = build_update_data(request, ["name", "name", "name"])
        
        # Should only include the field once
        assert result == {"name": "Test Plant"}

    def test_zero_values(self):
        """Test handling of zero values (should not be excluded)"""
        request = MockRequestModel(age=0, score=0.0, is_active=False)
        result = build_update_data(request, ["age", "score", "is_active"])
        
        assert result == {
            "age": "0",
            "score": "0.0", 
            "is_active": "False"
        }

    def test_empty_string_included(self):
        """Test that empty strings are included (not treated as None)"""
        request = MockRequestModel(name="", description="valid description")
        result = build_update_data(request, ["name", "description"])
        
        assert result == {
            "name": "",
            "description": "valid description"
        }
