"""
BSMSchema Introspector - Extract field documentation from bsmschema models

bsmschema uses attribute docstrings (strings after field definitions) instead of
Field(description=...), so we need to parse the source code to extract them.
"""

import inspect
import re
from typing import Dict, Optional

from pydantic import BaseModel


class BSMSchemaIntrospector:
    """Extract field documentation from bsmschema Pydantic models."""

    @staticmethod
    def get_field_docstrings(model_class: type[BaseModel]) -> Dict[str, str]:
        """
        Extract field docstrings from a bsmschema model class.

        bsmschema uses attribute docstrings like:
            FieldName: Type
            \"\"\"Docstring for this field.\"\"\"

        Args:
            model_class: Pydantic model class from bsmschema

        Returns:
            Dict mapping field names to their docstrings
        """
        try:
            source = inspect.getsource(model_class)
        except (OSError, TypeError):
            return {}

        # Pattern to match: field_name: Type\n    """docstring"""
        # Also handles r"""docstring""" for raw strings
        pattern = r'(\w+):\s*[\w\[\]|,\s\(\)\.\'\"]+\n\s+[r]?"""([^"]+)"""'
        matches = re.findall(pattern, source, re.DOTALL)

        docstrings = {}
        for field_name, docstring in matches:
            # Clean up the docstring (remove extra whitespace, newlines)
            cleaned = ' '.join(docstring.strip().split())
            docstrings[field_name] = cleaned

        return docstrings

    @staticmethod
    def get_field_info(model_class: type[BaseModel], field_name: str) -> Optional[str]:
        """
        Get documentation for a specific field.

        Args:
            model_class: Pydantic model class
            field_name: Name of the field

        Returns:
            Docstring for the field, or None if not found
        """
        docstrings = BSMSchemaIntrospector.get_field_docstrings(model_class)
        return docstrings.get(field_name)
