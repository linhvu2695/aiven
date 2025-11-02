import tempfile


def create_temp_local_file(file_data: bytes, suffix: str) -> str:
    """Create a temporary local file with the given suffix
        
    Returns:
        The path to the temporary file
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(file_data)
        temp_path = temp_file.name
    return temp_path