"""
Validator Introspector - Extract enum values from Pydantic field validators

This module dynamically extracts valid enum values from @field_validator functions
by parsing their source code. This allows the GUI to stay synchronized with the
Pydantic models without hardcoding values.
"""

import inspect
import re
from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel


class ValidatorIntrospector:
    """Extract enum values from Pydantic field validators."""

    @staticmethod
    def get_validator_enum_values(
        model_class: type[BaseModel], field_name: str
    ) -> Optional[List[str]]:
        """
        Extract enum values from a field validator by parsing its source code.

        Args:
            model_class: Pydantic model class
            field_name: Name of the field with a validator

        Returns:
            List of valid values if found, None otherwise
        """
        # Check if model has decorators
        if not hasattr(model_class, '__pydantic_decorators__'):
            return None

        # Get field validators
        field_validators = model_class.__pydantic_decorators__.field_validators
        if not field_validators:
            return None

        # Find validator for this field
        validator_func = None
        for validator_name, decorator in field_validators.items():
            if field_name in decorator.info.fields:
                validator_func = decorator.func
                break

        if not validator_func:
            return None

        # Get source code of validator
        try:
            source = inspect.getsource(validator_func)
        except (OSError, TypeError):
            return None

        # Look for patterns like: valid_X = ['a', 'b', 'c']
        # Common patterns:
        # - valid_models = [...]
        # - if v not in [...]
        # - if v is not None and v not in [...]

        # Pattern 1: valid_X = [...]
        match = re.search(r'valid_\w+ = \[(.*?)\]', source, re.DOTALL)
        if match:
            values_str = match.group(1)
            values = re.findall(r"'([^']+)'", values_str)
            if values:
                return values

        # Pattern 2: if v not in [...]
        match = re.search(r'if v.*?not in \[(.*?)\]', source, re.DOTALL)
        if match:
            values_str = match.group(1)
            values = re.findall(r"'([^']+)'", values_str)
            if values:
                return values

        # Pattern 3: Must be one of: a, b, c (from error message)
        match = re.search(r'must be one of: ([^"\']*)', source, re.IGNORECASE)
        if match:
            values_str = match.group(1)
            values = [v.strip() for v in values_str.split(',') if v.strip()]
            if values:
                return values

        return None

    @staticmethod
    def build_validator_enum_map(
        transformation_models: Dict[str, type[BaseModel]],
    ) -> Dict[Tuple[str, str], List[str]]:
        """
        Build a map of (transformation_name, field_name) -> valid_values
        by introspecting all transformation models.

        Args:
            transformation_models: Dict mapping transformation names to model classes

        Returns:
            Dict mapping (transform_name, field_name) to list of valid values
        """
        enum_map = {}

        for transform_name, model_class in transformation_models.items():
            # Check all fields in the model
            for field_name in model_class.model_fields.keys():
                values = ValidatorIntrospector.get_validator_enum_values(
                    model_class, field_name
                )
                if values:
                    enum_map[(transform_name, field_name)] = values

        return enum_map
