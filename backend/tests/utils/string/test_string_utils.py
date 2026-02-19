from datetime import datetime
from typing import Optional
from app.utils.string.string_utils import (
    validate_required_fields,
    validate_exactly_one_field,
    is_empty_string,
    parse_int,
    parse_datetime,
    extract_value,
    parse_list,
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


class TestParseInt:
    """Test cases for parse_int function"""

    def test_valid_integer_string(self):
        """Test parsing valid integer string"""
        assert parse_int("42") == 42
        assert parse_int("0") == 0
        assert parse_int("-10") == -10

    def test_valid_integer(self):
        """Test passing integer returns as-is"""
        assert parse_int(42) == 42
        assert parse_int(0) == 0

    def test_invalid_string_returns_default(self):
        """Test invalid string returns default"""
        assert parse_int("abc") == 0
        assert parse_int("12.5") == 0
        assert parse_int("") == 0

    def test_custom_default(self):
        """Test custom default value"""
        assert parse_int("abc", default=-1) == -1
        assert parse_int(None, default=99) == 99

    def test_none_returns_default(self):
        """Test None returns default"""
        assert parse_int(None) == 0
        assert parse_int(None, default=5) == 5


class TestParseDatetime:
    """Test cases for parse_datetime function"""

    def test_us_format_with_time(self):
        """Test US format with AM/PM time"""
        result = parse_datetime("1/29/2026 5:08:49 AM")
        assert result == datetime(2026, 1, 29, 5, 8, 49)
        result = parse_datetime("12/31/2025 11:59:59 PM")
        assert result == datetime(2025, 12, 31, 23, 59, 59)

    def test_named_month_formats(self):
        """Test named month formats"""
        assert parse_datetime("02 March, 2026") == datetime(2026, 3, 2)
        assert parse_datetime("02 March 2026") == datetime(2026, 3, 2)
        assert parse_datetime("March 02, 2026") == datetime(2026, 3, 2)

    def test_iso_format(self):
        """Test ISO 8601 format"""
        assert parse_datetime("2026-01-29T05:08:49") == datetime(2026, 1, 29, 5, 8, 49)
        assert parse_datetime("2026-01-29") == datetime(2026, 1, 29)

    def test_empty_or_none_returns_none(self):
        """Test empty values return None"""
        assert parse_datetime(None) is None
        assert parse_datetime("") is None

    def test_invalid_format_returns_none(self):
        """Test invalid format returns None"""
        assert parse_datetime("not a date") is None
        assert parse_datetime("32/13/2026") is None


class TestExtractValue:
    """Test cases for extract_value function"""

    def test_dict_with_value_key(self):
        """Test extracting Value from dict"""
        assert extract_value({"Value": "hello"}) == "hello"
        assert extract_value({"Value": 123}) == "123"
        assert extract_value({"Value": ""}) == ""

    def test_dict_without_value_key(self):
        """Test dict without Value key returns empty string"""
        assert extract_value({"other": "key"}) == ""
        assert extract_value({}) == ""

    def test_non_dict_returns_string(self):
        """Test non-dict returns string representation"""
        assert extract_value("hello") == "hello"
        assert extract_value(42) == "42"
        assert extract_value(True) == "True"

    def test_none_returns_empty_string(self):
        """Test None returns empty string"""
        assert extract_value(None) == ""


class TestParseList:
    """Test cases for parse_list function"""

    def test_comma_separated_string(self):
        """Test comma-separated string parsing"""
        assert parse_list("a, b, c") == ["a", "b", "c"]
        assert parse_list("single") == ["single"]

    def test_strips_whitespace(self):
        """Test whitespace is stripped from items"""
        assert parse_list("  a  ,  b  ,  c  ") == ["a", "b", "c"]

    def test_empty_string_returns_empty_list(self):
        """Test empty string returns empty list"""
        assert parse_list("") == []
        assert parse_list(None) == []

    def test_already_list_returns_as_is(self):
        """Test list input returns unchanged"""
        assert parse_list(["a", "b", "c"]) == ["a", "b", "c"]
        assert parse_list([]) == []

    def test_custom_separator(self):
        """Test custom separator"""
        assert parse_list("a|b|c", separator="|") == ["a", "b", "c"]
        assert parse_list("a;b;c", separator=";") == ["a", "b", "c"]
