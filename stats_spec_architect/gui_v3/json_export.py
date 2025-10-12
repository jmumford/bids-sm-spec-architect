"""
JSON Export for GUI v3

Converts GUI widget state to BIDS Stats Model JSON and validates it.
"""

import json
import re
from tkinter import messagebox
from typing import get_args, get_origin

from bsmschema.models import Contrast, DummyContrasts, Model

from stats_spec_architect.gui_v3.widget_helpers import extract_field_name_from_key


# Fields that should be parsed as lists (based on Pydantic models)
def _should_parse_as_list(field_name: str, context: str = None) -> bool:
    """Determine if a field should be parsed as a list based on Pydantic model."""
    from typing import Union

    # Map context to Pydantic model
    model_map = {
        'Model': Model,
        'Contrast': Contrast,
        'DummyContrasts': DummyContrasts,
    }

    # Check Pydantic model if context provided
    if context and context in model_map:
        model_class = model_map[context]
        if field_name in model_class.model_fields:
            field_info = model_class.model_fields[field_name]
            annotation = field_info.annotation

            # Unwrap Optional if present
            origin = get_origin(annotation)
            if origin is type(None) or str(annotation).startswith('Optional'):
                args = get_args(annotation)
                if args:
                    annotation = args[0]
                    origin = get_origin(annotation)

            # Check if it's directly a list
            if origin is list:
                return True

            # Check if it's a Union containing list types
            # (e.g., Union[List[...], List[List[...]]] for Weights)
            if origin is Union:
                union_args = get_args(annotation)
                for arg in union_args:
                    if get_origin(arg) is list:
                        return True

            return False

    # Fallback: known list fields by name
    list_fields = {
        'X',  # Model.X
        'ConditionList',  # Contrast.ConditionList
        'Weights',  # Contrast.Weights
        'Contrasts',  # DummyContrasts.Contrasts
    }
    return field_name in list_fields


def export_to_json(input_widgets, node_widgets, edge_widgets, validate=True):
    """
    Export GUI state to BIDS Stats Model JSON.

    Args:
        input_widgets: CreateInputWidgets instance
        node_widgets: AddNode instance
        edge_widgets: AddEdge instance
        validate: Whether to validate with enhanced_validator (default: True)

    Returns:
        tuple: (json_string, validation_result) or (None, validation_result) if errors
    """
    try:
        # Build the model dictionary
        model = {}

        # Extract top-level fields
        model.update(_extract_input_data(input_widgets))

        # Extract nodes
        nodes = _extract_nodes_data(node_widgets)
        if nodes:
            model['Nodes'] = nodes
        else:
            # Always include Nodes as empty list
            model['Nodes'] = []

        # Extract edges
        edges = _extract_edges_data(edge_widgets)
        if edges:
            model['Edges'] = edges
        else:
            # Always include Edges as empty list to avoid validator issues
            model['Edges'] = []

        # Validate if requested
        if validate:
            from stats_spec_architect.validation.enhanced_validator import (
                EnhancedBIDSValidator,
            )

            validator = EnhancedBIDSValidator()
            result = validator.validate_data(model)

            if not result.valid:
                # Show validation errors
                _show_validation_errors(result)
                return None, result
            else:
                # Valid! Return JSON
                json_string = json.dumps(model, indent=2)
                return json_string, result
        else:
            # No validation - just return JSON
            json_string = json.dumps(model, indent=2)
            return json_string, None

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        messagebox.showerror(
            'JSON Export Error',
            f'Error generating JSON:\n\n{str(e)}\n\nDetails:\n{error_details[:500]}',
        )
        return None, None


def _extract_input_data(input_widgets):
    """Extract data from input widgets."""
    data = {}

    # Safety check
    if (
        not hasattr(input_widgets, 'widget_output')
        or input_widgets.widget_output is None
    ):
        return data

    # Iterate through widget_output
    for key, widget in input_widgets.widget_output.items():
        if key == 'Input':
            # Input is a nested dict with sub-fields
            if widget is not None and isinstance(widget, dict):
                input_dict = {}
                for sub_key, sub_widget in widget.items():
                    field_name, value = _process_widget(sub_key, sub_widget)
                    if value is not None:
                        input_dict[field_name] = value
                if input_dict:
                    data['Input'] = input_dict
        else:
            # Regular top-level field
            field_name, value = _process_widget(key, widget)
            if value is not None:
                data[field_name] = value

    return data


def _extract_nodes_data(node_widgets):
    """Extract data from node widgets."""
    nodes = []

    # Iterate through each node
    for node_key in sorted(node_widgets.node_output.keys()):
        node_data = node_widgets.node_output[node_key]
        node_dict = {}

        for key, widget in node_data.items():
            if key == 'transformations':
                # Handle transformations
                trans_dict = _extract_transformations(widget)
                if trans_dict:
                    node_dict['Transformations'] = trans_dict
            elif key == 'Model':
                # Model is a dict with widget keys
                if widget is not None and isinstance(widget, dict):
                    model_dict = {}
                    for model_key, model_widget in widget.items():
                        field_name, value = _process_widget(
                            model_key, model_widget, context='Model'
                        )
                        if value is not None:
                            model_dict[field_name] = value
                    if model_dict:
                        node_dict['Model'] = model_dict
            elif key == 'Contrasts':
                # Contrasts is a list of dicts
                if widget is not None and isinstance(widget, list):
                    contrasts_list = []
                    for contrast_dict_raw in widget:
                        contrast_dict = {}
                        for contrast_key, contrast_widget in contrast_dict_raw.items():
                            field_name, value = _process_widget(
                                contrast_key, contrast_widget, context='Contrast'
                            )
                            if value is not None:
                                contrast_dict[field_name] = value
                        if contrast_dict:
                            contrasts_list.append(contrast_dict)
                    if contrasts_list:
                        node_dict['Contrasts'] = contrasts_list
            elif key == 'DummyContrasts':
                # DummyContrasts is a dict with widget keys
                if widget is not None and isinstance(widget, dict):
                    dummy_dict = {}
                    for dummy_key, dummy_widget in widget.items():
                        field_name, value = _process_widget(
                            dummy_key, dummy_widget, context='DummyContrasts'
                        )
                        if value is not None:
                            dummy_dict[field_name] = value
                    if dummy_dict:
                        node_dict['DummyContrasts'] = dummy_dict
            else:
                # Regular node field (Level, Name, GroupBy)
                field_name, value = _process_widget(key, widget)
                if value is not None:
                    node_dict[field_name] = value

        if node_dict:
            nodes.append(node_dict)

    return nodes


def _extract_transformations(transformation_widget):
    """Extract transformations from AddTransformationWidgets."""
    trans_dict = {}

    # Get Transformer (using new simple key format)
    if 'Transformer' in transformation_widget.widget_output:
        transformer = transformation_widget.widget_output['Transformer'].get()
        if transformer:
            trans_dict['Transformer'] = transformer

    # Get Instructions
    instructions = []
    for key in sorted(transformation_widget.widget_output.keys()):
        if key.startswith('Instructions_'):
            instruction_widgets = transformation_widget.widget_output[key]
            instruction_dict = {}

            # Get the transformation name to look up its model
            transform_name = instruction_widgets.get('Name')

            for inst_key, inst_widget in instruction_widgets.items():
                if inst_key == 'Name':
                    # Name is a string, not a widget
                    instruction_dict['Name'] = inst_widget
                else:
                    # For other fields, we need to check the model type
                    value = _process_transformation_field(
                        inst_key, inst_widget, transform_name
                    )
                    if value is not None:
                        instruction_dict[inst_key] = value

            if instruction_dict:
                instructions.append(instruction_dict)

    if instructions:
        trans_dict['Instructions'] = instructions

    return trans_dict if trans_dict else None


def _process_transformation_field(field_name, widget, transform_name):
    """
    Process a transformation field with proper type detection.

    Args:
        field_name: Name of the field (e.g., "Input", "Output")
        widget: The widget containing the value
        transform_name: Name of the transformation (e.g., "Convolve")

    Returns:
        Processed value with correct type
    """
    # Get the value from the widget
    if hasattr(widget, 'get'):
        raw_value = widget.get()
    else:
        return widget

    if not raw_value or (isinstance(raw_value, str) and raw_value.strip() == ''):
        return None

    # Look up the field type from the transformation model
    try:
        from stats_spec_architect.gui_v3.model_discovery import (
            discover_transformation_models,
        )

        models = discover_transformation_models()
        model_class = models.get(transform_name)

        if model_class and field_name in model_class.model_fields:
            field_info = model_class.model_fields[field_name]
            annotation = field_info.annotation

            # Check if it's a list type
            from typing import get_args, get_origin

            origin = get_origin(annotation)

            # Handle Optional types
            if origin is type(None) or str(annotation).startswith('Optional'):
                args = get_args(annotation)
                if args:
                    annotation = args[0]
                    origin = get_origin(annotation)

            # If it's a list, parse as list
            if origin is list:
                # Check what kind of list
                args = get_args(annotation)
                if args and (args[0] == str or 'str' in str(args[0]).lower()):
                    return _parse_list_of_strings(raw_value)
                elif args and (
                    args[0] in (int, float)
                    or 'int' in str(args[0]).lower()
                    or 'float' in str(args[0]).lower()
                ):
                    return _parse_list_of_numbers(raw_value)
                else:
                    return _parse_list_of_strings(raw_value)

            # If it's a dict, parse as dict
            if origin is dict:
                return _parse_dict(raw_value)

    except Exception:
        # If we can't determine the type, fall back to simple parsing
        pass

    # Default: return as string
    return raw_value


def _extract_edges_data(edge_widgets):
    """Extract data from edge widgets."""
    edges = []

    for edge_data in edge_widgets.edge_output:
        edge_dict = {}

        for key, widget in edge_data.items():
            field_name, value = _process_widget(key, widget)
            if value is not None:
                edge_dict[field_name] = value

        if edge_dict:
            edges.append(edge_dict)

    return edges


def _process_widget(label, widget, context=None):
    """
    Process a widget to extract its value.

    Args:
        label: Widget key/label (e.g., "Name" or legacy "Name (req, str)")
        widget: Tkinter widget or value
        context: Optional context ('Model', 'Contrast', 'DummyContrasts') for type inference

    Returns:
        tuple: (field_name, processed_value)
    """
    # Extract field name from key (supports both new and legacy formats)
    field_name = extract_field_name_from_key(label)

    if not field_name:
        return None, None

    # Check if it's a checkbox row (CreateCheckbuttonRow)
    if hasattr(widget, 'get_list_of_checked_values'):
        checked_values = widget.get_list_of_checked_values()
        return field_name, checked_values if checked_values else None

    # Check if it's a widget with .get() method
    if hasattr(widget, 'get'):
        raw_value = widget.get()
    else:
        # It might be a nested structure (like transformations)
        return field_name, widget

    # If empty, return None
    if not raw_value or (isinstance(raw_value, str) and raw_value.strip() == ''):
        return field_name, None

    # Check if this field should be a list (using Pydantic model)
    if _should_parse_as_list(field_name, context):
        # Try to determine if it's numbers or strings
        if field_name == 'Weights':
            return field_name, _parse_list_of_numbers(raw_value)
        else:
            return field_name, _parse_list_of_strings(raw_value)

    # Legacy format type hints (for backwards compatibility)
    if '(' in label and ')' in label:
        # Legacy format: "Name (req, list of strings)"
        label_parts = re.split(r'[(),]', label)
        label_parts = [part.strip() for part in label_parts if part.strip()]
        type_hints = [part.lower() for part in label_parts[1:]]

        # Handle different types
        if 'list of strings' in ' '.join(type_hints):
            return field_name, _parse_list_of_strings(raw_value)
        elif 'list of numbers' in ' '.join(type_hints):
            return field_name, _parse_list_of_numbers(raw_value)
        elif 'dict' in type_hints:
            return field_name, _parse_dict(raw_value)
        elif 'list' in type_hints:
            return field_name, _parse_list_of_strings(raw_value)

    # Default: string or simple type
    return field_name, raw_value


def _parse_list_of_strings(value):
    """Parse a comma-separated string into a list of strings."""
    if not value:
        return None

    # Split by comma
    if ',' in value:
        items = [item.strip() for item in value.split(',')]
        # Remove empty strings and clean up
        items = [re.sub(r'[\[\]\'\"]', '', item) for item in items if item.strip()]
        return items
    else:
        # Single value - make it a list
        return [value.strip()]


def _parse_list_of_numbers(value):
    """Parse a comma-separated string into a list of numbers."""
    if not value:
        return None

    # Split by comma
    if ',' in value:
        items = [item.strip() for item in value.split(',')]
    else:
        items = [value.strip()]

    # Convert to numbers
    try:
        # Clean up brackets/quotes
        items = [re.sub(r'[\[\]\'\"]', '', item) for item in items if item.strip()]
        # Try to convert to float
        numbers = [float(item) for item in items]
        # Convert to int if they're whole numbers
        numbers = [int(n) if n == int(n) else n for n in numbers]
        return numbers
    except ValueError:
        messagebox.showwarning(
            'Invalid Number', f'Could not parse numbers from: {value}'
        )
        return None


def _parse_dict(value):
    """Parse a JSON string into a dictionary."""
    if not value:
        return None

    try:
        # Try to parse as JSON
        import json

        return json.loads(value)
    except json.JSONDecodeError:
        messagebox.showwarning(
            'Invalid JSON',
            f'Could not parse JSON from: {value}\n\nExpected format: {{"key": ["value1", "value2"]}}',
        )
        return None


def _show_validation_errors(validation_result):
    """Display validation errors in a message box."""
    error_msg = '❌ Validation Failed\n\n'
    error_msg += f'Found {len(validation_result.errors)} error(s):\n\n'

    for i, error in enumerate(validation_result.errors[:10], 1):  # Show first 10
        error_msg += f'{i}. {error}\n'

    if len(validation_result.errors) > 10:
        error_msg += f'\n... and {len(validation_result.errors) - 10} more errors.'

    messagebox.showerror('Validation Errors', error_msg)


def show_json_in_window(json_string):
    """Display JSON in a popup window."""
    import platform
    import tkinter as tk

    import ttkbootstrap as tb

    # Create popup window
    popup = tk.Toplevel()
    popup.title('BIDS Stats Model JSON')
    popup.geometry('800x600')

    # Add text widget with scrollbar
    frame = tk.Frame(popup)
    frame.pack(fill='both', expand=True, padx=10, pady=10)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side='right', fill='y')

    text_widget = tk.Text(frame, wrap='none', yscrollcommand=scrollbar.set)
    text_widget.pack(side='left', fill='both', expand=True)
    scrollbar.config(command=text_widget.yview)

    # Insert JSON
    text_widget.insert('1.0', json_string)
    text_widget.config(state='disabled')  # Make read-only

    # Set up mouse wheel scrolling for the text widget (platform-specific)
    def scroll_text(event):
        """Handle mouse wheel scrolling in text widget."""
        system = platform.system()
        if system == 'Darwin':  # macOS
            text_widget.yview_scroll(int(-1 * event.delta), 'units')
        elif system == 'Windows':
            text_widget.yview_scroll(int(-1 * (event.delta / 120)), 'units')
        return 'break'  # Prevent event from propagating

    def scroll_text_linux_up(event):
        text_widget.yview_scroll(-1, 'units')
        return 'break'

    def scroll_text_linux_down(event):
        text_widget.yview_scroll(1, 'units')
        return 'break'

    # Bind mouse wheel to text widget only
    system = platform.system()
    if system == 'Darwin':
        text_widget.bind('<MouseWheel>', scroll_text)
    elif system == 'Windows':
        text_widget.bind('<MouseWheel>', scroll_text)
    else:
        text_widget.bind('<Button-4>', scroll_text_linux_up)
        text_widget.bind('<Button-5>', scroll_text_linux_down)

    # Add copy button
    def copy_to_clipboard():
        popup.clipboard_clear()
        popup.clipboard_append(json_string)
        messagebox.showinfo('Copied', 'JSON copied to clipboard!')

    copy_button = tb.Button(
        popup, text='Copy to Clipboard', command=copy_to_clipboard, bootstyle='primary'
    )
    copy_button.pack(pady=5)
