from typing import Optional
from app.utils.string.string_utils import (
    validate_required_fields,
    validate_exactly_one_field,
    is_empty_string
)


class MockCreateRequest:
    def __init__(self, name: Optional[str] = None, email: Optional[str] = None, age: Optional[int] = None):
        self.name = name
        self.email = email
        self.age = age


class MockImageRequest:
    def __init__(self, filename: Optional[str] = None, file_data: Optional[bytes] = None, 
                 base64_data: Optional[str] = None, source_url: Optional[str] = None):
        self.filename = filename
        self.file_data = file_data
        self.base64_data = base64_data
        self.source_url = source_url


class TestValidateRequiredFields:
    """Test cases for validate_required_fields function"""
    
    def test_valid_request_with_all_fields(self):
        """Test validation passes when all required fields are present"""
        request = MockCreateRequest(name="John Doe", email="john@example.com")
        is_valid, error_msg = validate_required_fields(request, ["name", "email"])
        
        assert is_valid is True
        assert error_msg == ""
    
    def test_valid_request_with_extra_fields(self):
        """Test validation passes when required fields are present along with extra fields"""
        request = MockCreateRequest(name="John Doe", email="john@example.com", age=30)
        is_valid, error_msg = validate_required_fields(request, ["name", "email"])
        
        assert is_valid is True
        assert error_msg == ""
    
    def test_missing_required_field_none(self):
        """Test validation fails when required field is None"""
        request = MockCreateRequest(name=None, email="john@example.com")
        is_valid, error_msg = validate_required_fields(request, ["name", "email"])
        
        assert is_valid is False
        assert "Invalid mockcreaterequest info. Missing value for field: name" in error_msg
    
    def test_missing_required_field_empty_string(self):
        """Test validation fails when required field is empty string"""
        request = MockCreateRequest(name="", email="john@example.com")
        is_valid, error_msg = validate_required_fields(request, ["name", "email"])
        
        assert is_valid is False
        assert "Invalid mockcreaterequest info. Missing value for field: name" in error_msg
    
    def test_missing_required_field_whitespace_only(self):
        """Test validation fails when required field is whitespace only"""
        request = MockCreateRequest(name="   ", email="john@example.com")
        is_valid, error_msg = validate_required_fields(request, ["name", "email"])
        
        assert is_valid is False
        assert "Invalid mockcreaterequest info. Missing value for field: name" in error_msg
    
    def test_multiple_missing_fields_returns_first_error(self):
        """Test validation returns error for first missing field encountered"""
        request = MockCreateRequest(name=None, email=None)
        is_valid, error_msg = validate_required_fields(request, ["name", "email"])
        
        assert is_valid is False
        assert "Invalid mockcreaterequest info. Missing value for field: name" in error_msg
    
    def test_nonexistent_field(self):
        """Test validation fails when required field doesn't exist on object"""
        request = MockCreateRequest(name="John Doe")
        is_valid, error_msg = validate_required_fields(request, ["name", "nonexistent_field"])
        
        assert is_valid is False
        assert "Invalid mockcreaterequest info. Missing value for field: nonexistent_field" in error_msg
    
    def test_empty_required_fields_list(self):
        """Test validation passes when no fields are required"""
        request = MockCreateRequest()
        is_valid, error_msg = validate_required_fields(request, [])
        
        assert is_valid is True
        assert error_msg == ""
    
    def test_non_string_field_validation(self):
        """Test validation works with non-string fields"""
        request = MockCreateRequest(name="John Doe", age=30)
        is_valid, error_msg = validate_required_fields(request, ["name", "age"])
        
        assert is_valid is True
        assert error_msg == ""
    
    def test_class_name_in_error_message(self):
        """Test that class name is correctly extracted for error messages"""
        request = MockImageRequest(filename=None)
        is_valid, error_msg = validate_required_fields(request, ["filename"])
        
        assert is_valid is False
        assert "Invalid mockimagerequest info. Missing value for field: filename" in error_msg


class TestValidateExactlyOneField:
    """Test cases for validate_exactly_one_field function"""
    
    def test_exactly_one_field_provided_first(self):
        """Test validation passes when exactly one field is provided (first option)"""
        request = MockImageRequest(file_data=b"image_data")
        is_valid, error_msg = validate_exactly_one_field(
            request, ["file_data", "base64_data", "source_url"]
        )
        
        assert is_valid is True
        assert error_msg == ""
    
    def test_exactly_one_field_provided_middle(self):
        """Test validation passes when exactly one field is provided (middle option)"""
        request = MockImageRequest(base64_data="base64_string")
        is_valid, error_msg = validate_exactly_one_field(
            request, ["file_data", "base64_data", "source_url"]
        )
        
        assert is_valid is True
        assert error_msg == ""
    
    def test_exactly_one_field_provided_last(self):
        """Test validation passes when exactly one field is provided (last option)"""
        request = MockImageRequest(source_url="https://example.com/image.jpg")
        is_valid, error_msg = validate_exactly_one_field(
            request, ["file_data", "base64_data", "source_url"]
        )
        
        assert is_valid is True
        assert error_msg == ""
    
    def test_no_fields_provided(self):
        """Test validation fails when no fields are provided"""
        request = MockImageRequest()
        is_valid, error_msg = validate_exactly_one_field(
            request, ["file_data", "base64_data", "source_url"]
        )
        
        assert is_valid is False
        assert "Invalid mockimagerequest info. Must provide one of: file_data, base64_data, source_url" in error_msg
    
    def test_multiple_fields_provided(self):
        """Test validation fails when multiple fields are provided"""
        request = MockImageRequest(file_data=b"data", base64_data="base64")
        is_valid, error_msg = validate_exactly_one_field(
            request, ["file_data", "base64_data", "source_url"]
        )
        
        assert is_valid is False
        assert "Invalid mockimagerequest info. Provide only one of: file_data, base64_data, source_url" in error_msg
    
    def test_all_fields_provided(self):
        """Test validation fails when all fields are provided"""
        request = MockImageRequest(
            file_data=b"data", 
            base64_data="base64", 
            source_url="https://example.com"
        )
        is_valid, error_msg = validate_exactly_one_field(
            request, ["file_data", "base64_data", "source_url"]
        )
        
        assert is_valid is False
        assert "Invalid mockimagerequest info. Provide only one of: file_data, base64_data, source_url" in error_msg
    
    def test_empty_field_list(self):
        """Test validation fails when field list is empty"""
        request = MockImageRequest(file_data=b"data")
        is_valid, error_msg = validate_exactly_one_field(request, [])
        
        assert is_valid is False
        assert "Invalid request. Must provide at least one field." in error_msg
    
    def test_single_field_in_list(self):
        """Test validation works with single field in list"""
        request = MockImageRequest(file_data=b"data")
        is_valid, error_msg = validate_exactly_one_field(request, ["file_data"])
        
        assert is_valid is True
        assert error_msg == ""
    
    def test_nonexistent_fields(self):
        """Test validation handles nonexistent fields correctly"""
        request = MockImageRequest()
        is_valid, error_msg = validate_exactly_one_field(
            request, ["nonexistent1", "nonexistent2"]
        )
        
        assert is_valid is False
        assert "Invalid mockimagerequest info. Must provide one of: nonexistent1, nonexistent2" in error_msg


class TestIsEmptyString:
    """Test cases for is_empty_string function"""
    
    def test_none_value(self):
        """Test that None is considered empty"""
        assert is_empty_string(None) is True
    
    def test_empty_string(self):
        """Test that empty string is considered empty"""
        assert is_empty_string("") is True
    
    def test_whitespace_only_string(self):
        """Test that whitespace-only string is considered empty"""
        assert is_empty_string("   ") is True
        assert is_empty_string("\t") is True
        assert is_empty_string("\n") is True
        assert is_empty_string("  \t\n  ") is True
    
    def test_valid_string(self):
        """Test that valid string is not considered empty"""
        assert is_empty_string("hello") is False
        assert is_empty_string("  hello  ") is False
        assert is_empty_string("123") is False
