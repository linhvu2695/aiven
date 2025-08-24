import logging
from typing import Any, Dict, List
from datetime import datetime
from pydantic import BaseModel


def build_update_data(request: BaseModel, fields: List[str]) -> Dict[str, Any]:
    """
    Build an update dictionary containing only non-None fields from a request object.

    Args:
        request: The Pydantic request model containing the data
        fields: List of field names to check and include if not None

    Returns:
        Dictionary containing only the non-None fields

    Example:
        update_data = build_update_data(
            request=plant_request,
            fields=["name", "description", "location", "watering_frequency_days"],
        )
    """
    update_data = {}
    
    for field_name in fields:
        field_value = getattr(request, field_name, None)
        if field_value is not None:
            # Handle special cases for data serialization
            try:
                if isinstance(field_value, datetime):
                    update_data[field_name] = field_value.isoformat()
                elif hasattr(field_value, "value"):  # Handle enums
                    update_data[field_name] = field_value.value
                else:
                    update_data[field_name] = str(field_value)  # Handle other types
            except AttributeError:
                logging.getLogger("uvicorn.warning").warning(f"Field {field_name} cannot be serialized")
        else:
            logging.getLogger("uvicorn.warning").warning(f"Field {field_name} not found in request")

    return update_data