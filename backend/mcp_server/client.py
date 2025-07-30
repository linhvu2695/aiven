"""
HTTP client for making requests to the Aiven API
"""

import json
import httpx
from typing import Any, Dict, Optional

from mcp_server.config import config


class AivenAPIClient:
    """HTTP client for interacting with the Aiven FastAPI backend"""
    
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or config.api_url
        
    async def request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to the FastAPI backend"""
        url = f"{self.base_url}{endpoint}"
        
        async with httpx.AsyncClient(timeout=config.timeout) as client:
            try:
                if method.upper() == "GET":
                    response = await client.get(url, params=data or {})
                elif method.upper() == "POST":
                    if files:
                        response = await client.post(url, data=data, files=files)
                    else:
                        response = await client.post(url, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                    
                response.raise_for_status()
                return response.json()
                
            except httpx.HTTPError as e:
                return {"error": f"Request failed: {str(e)}"}
            except Exception as e:
                return {"error": f"Unexpected error: {str(e)}"}
    
    def format_response(self, result: Dict[str, Any]) -> str:
        """Format API response as JSON string"""
        return json.dumps(result, indent=2)