"""
Widget Factory - Auto-generate widgets from Pydantic models

This module creates tkinter/ttkbootstrap widgets based on Pydantic model field definitions.
"""

from typing import Any, Dict, List, Type, get_args, get_origin

import ttkbootstrap as tb
from pydantic import BaseModel
from pydantic.fields import FieldInfo
from ttkbootstrap.constants import *


class WidgetFactory:
    """
    Factory class to create GUI widgets from Pydantic model fields.

    Usage:
        factory = WidgetFactory()
        widget = factory.create_widget_for_field(parent, field_name, field_info)
    """

    def __init__(self, transformation_models: Dict[str, Type[BaseModel]] = None):
        """
        Initialize widget factory.

        Args:
            transformation_models: Optional dict of transformation name -> Pydantic model.
                                 If provided, will auto-detect validator enums.
        """
        self.label_width = 25

        # Auto-detect validator enums from Pydantic models (if provided)
        self.validator_enums = {}
        if transformation_models:
            from stats_spec_architect.gui_v2.validator_introspector import (
                ValidatorIntrospector,
            )

            self.validator_enums = ValidatorIntrospector.build_validator_enum_map(
                transformation_models
            )

    def _get_python_type(self, annotation):
        """Extract the actual Python type from type annotations."""
        import typing

        origin = get_origin(annotation)

        # Handle Optional[X] (which is Union[X, None]) -> X
        if origin is typing.Union:
            args = get_args(annotation)
            if args:
                # Get first non-None type and recurse
                for arg in args:
                    if arg is not type(None):
                        return self._get_python_type(arg)

        # Handle List[X] -> list
        if origin is list or origin is List:
            return list

        # Handle Dict[X, Y] -> dict
        if origin is dict or origin is Dict:
            return dict

        # If it's already a basic type, return it
        if annotation in (str, int, float, bool, list, dict):
            return annotation

        # For Literal types, we'll handle in caller
        return annotation

    def _is_literal(self, annotation):
        """Check if annotation is a Literal type."""
        return str(get_origin(annotation)).endswith('.Literal')

    def _get_literal_values(self, annotation):
        """Extract values from Literal type."""
        if self._is_literal(annotation):
            return get_args(annotation)
        return None

    def _is_optional(self, field_info: FieldInfo):
        """Check if field is optional (has default or is Optional)."""
        return not field_info.is_required()

    def _make_label_text(self, field_name: str, field_info: FieldInfo, python_type):
        """Create label text with (req/opt, type) suffix."""
        req_opt = 'opt' if self._is_optional(field_info) else 'req'

        # Determine type string
        if python_type == list:
            type_str = 'list of strings'
        elif python_type == dict:
            type_str = 'dict'
        elif python_type == str:
            type_str = 'str'
        elif python_type == bool:
            type_str = 'bool'
        elif python_type == int:
            type_str = 'int'
        elif python_type == float:
            type_str = 'float'
        else:
            type_str = None

        if type_str:
            return f'{field_name} ({req_opt}, {type_str})'
        else:
            return f'{field_name} ({req_opt})'

    def _create_label_entry(
        self,
        parent_frame,
        label_text: str,
        entry_width: int = 25,
        default_value: Any = None,
    ):
        """
        Create a label with entry widget.

        Args:
            parent_frame: Parent widget
            label_text: Label text
            entry_width: Width of entry widget
            default_value: Default value to pre-populate (will be converted to string)
        """
        widget_pair_frame = tb.Frame(parent_frame)
        widget_pair_frame.pack(fill=X, expand=NO, pady=2)

        label_widget = tb.Label(
            master=widget_pair_frame, text=label_text, width=self.label_width
        )
        label_widget.grid(row=0, column=0, padx=5)

        entry_widget = tb.Entry(master=widget_pair_frame, width=entry_width)
        entry_widget.grid(row=0, column=1, padx=5)

        # Pre-populate with default value if provided
        if default_value is not None:
            entry_widget.insert(0, str(default_value))

        return entry_widget

    def _create_label_combobox(
        self,
        parent_frame,
        label_text: str,
        values: List[Any],
        default_value: Any = None,
    ):
        """
        Create a label with combobox widget.

        Args:
            parent_frame: Parent widget
            label_text: Label text
            values: List of values for combobox
            default_value: Default value to select (will find index automatically)
        """
        widget_pair_frame = tb.Frame(parent_frame)
        widget_pair_frame.pack(fill=X, expand=NO, pady=2)

        label_widget = tb.Label(
            master=widget_pair_frame, text=label_text, width=self.label_width
        )
        label_widget.grid(row=0, column=0, padx=5)

        combobox_widget = tb.Combobox(master=widget_pair_frame, values=values, width=24)
        combobox_widget.grid(row=0, column=1, padx=5)

        # Set default if provided
        if default_value is not None:
            try:
                # Find index of default value in values list
                default_index = values.index(default_value)
                combobox_widget.current(default_index)
            except (ValueError, IndexError):
                # Default not in list or invalid index - skip
                pass

        return combobox_widget

    def create_widget_for_field(
        self,
        parent,
        field_name: str,
        field_info: FieldInfo,
        transformation_name: str = None,
    ):
        """
        Create appropriate widget based on Pydantic field type.

        Args:
            parent: Parent tkinter widget
            field_name: Name of the field
            field_info: Pydantic FieldInfo object
            transformation_name: Optional transformation name for validator enum lookup

        Returns:
            Appropriate widget (Entry, Combobox, etc.)
        """
        from pydantic_core import PydanticUndefined

        annotation = field_info.annotation

        # Get default value if it exists (for pre-populating widgets)
        default_value = None
        if hasattr(field_info, 'default') and field_info.default != PydanticUndefined:
            default_value = field_info.default

        # Check for Literal (enum values) first
        literal_values = self._get_literal_values(annotation)
        if literal_values:
            label_text = (
                f'{field_name} ({("opt" if self._is_optional(field_info) else "req")})'
            )
            return self._create_label_combobox(
                parent, label_text, list(literal_values), default_value=default_value
            )

        # Check for validator-based enums (fields with @field_validator)
        if (
            transformation_name
            and (transformation_name, field_name) in self.validator_enums
        ):
            enum_values = self.validator_enums[(transformation_name, field_name)]
            label_text = (
                f'{field_name} ({("opt" if self._is_optional(field_info) else "req")})'
            )
            return self._create_label_combobox(
                parent, label_text, enum_values, default_value=default_value
            )

        # Get the actual Python type
        python_type = self._get_python_type(annotation)

        # Create label text
        label_text = self._make_label_text(field_name, field_info, python_type)

        # Boolean -> Combobox with True/False
        if python_type == bool:
            return self._create_label_combobox(
                parent, label_text, [True, False], default_value=default_value
            )

        # Everything else -> Entry box
        # (list, dict, str, int, float all use Entry and are parsed later)
        # Pre-populate with default if it's a simple type (not None, not list, not dict)
        entry_default = None
        if default_value is not None and python_type in (str, int, float):
            entry_default = default_value

        return self._create_label_entry(parent, label_text, default_value=entry_default)

    def create_widgets_from_model(
        self,
        parent,
        model_class: Type[BaseModel],
        exclude_fields: List[str] = None,
        transformation_name: str = None,
    ) -> Dict[str, Any]:
        """
        Create all widgets for a Pydantic model.

        Args:
            parent: Parent tkinter widget
            model_class: Pydantic model class
            exclude_fields: List of field names to skip (e.g., ['Name'])
            transformation_name: Optional transformation name for validator enum lookup

        Returns:
            Dictionary mapping field names to widgets
        """
        if exclude_fields is None:
            exclude_fields = []

        widgets = {}

        for field_name, field_info in model_class.model_fields.items():
            if field_name not in exclude_fields:
                widget = self.create_widget_for_field(
                    parent, field_name, field_info, transformation_name
                )
                widgets[field_name] = widget

        return widgets
