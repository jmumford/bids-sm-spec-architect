"""
Model Discovery - Dynamically discover transformation models

This module provides utilities to automatically discover all transformation
Pydantic models from the transformation_models module without hardcoding imports.
"""

import inspect
from typing import Dict, Type

from pydantic import BaseModel


def discover_transformation_models() -> Dict[str, Type[BaseModel]]:
    """
    Automatically discover all transformation instruction models.

    Scans the transformation_models module for classes ending in 'Instruction'
    and builds a mapping from transformation name (from Name field) to model class.

    Returns:
        Dict mapping transformation names to Pydantic model classes
        Example: {'Convolve': ConvolveInstruction, 'Scale': ScaleInstruction, ...}
    """
    from stats_spec_architect.validation import transformation_models

    # Get all classes from the module
    all_classes = inspect.getmembers(transformation_models, inspect.isclass)

    # Filter for Instruction classes (subclasses of BaseModel)
    transformation_map = {}

    for class_name, cls in all_classes:
        # Check if it's an Instruction class and a BaseModel
        if (
            class_name.endswith('Instruction')
            and issubclass(cls, BaseModel)
            and cls != BaseModel
        ):
            # Extract the transformation name from the Name field's Literal value
            if 'Name' in cls.model_fields:
                name_field = cls.model_fields['Name']
                if hasattr(name_field, 'default'):
                    transform_name = name_field.default
                    transformation_map[transform_name] = cls

    return transformation_map


def get_transformation_names() -> list[str]:
    """
    Get list of available transformation names.

    This is a convenience wrapper that calls discover_transformation_models()
    and returns just the names.

    Returns:
        Sorted list of transformation names
    """
    models = discover_transformation_models()
    return sorted(models.keys())
