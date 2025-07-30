"""
MCP Resources for Aiven API

This package contains all the MCP resources that provide information
and documentation to AI agents.
"""

from .api_docs import register_api_docs_resource
from .config import register_config_resource

__all__ = [
    "register_api_docs_resource",
    "register_config_resource"
]