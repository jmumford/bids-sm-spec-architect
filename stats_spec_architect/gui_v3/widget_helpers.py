"""
Widget Helper Functions

Centralized utilities for creating GUI widgets with consistent styling
and behavior. Reduces code duplication across widget modules.
"""

from typing import Optional

import ttkbootstrap as tb
from pydantic.fields import FieldInfo
from ttkbootstrap.constants import *

from stats_spec_architect.gui_v3.widget_factory import ToolTip


def create_field_label(
    parent, field_name: str, field_info: Optional[FieldInfo] = None, width: int = 25
) -> tb.Label:
    """
    Create a standardized field label with (req) or (opt) indicator.

    Args:
        parent: Parent frame
        field_name: Name of the field (e.g., 'Name', 'GroupBy')
        field_info: Optional Pydantic FieldInfo to extract requirement status
        width: Label width (default: 25)

    Returns:
        tb.Label widget

    Example:
        label = create_field_label(frame, 'GroupBy', Node.model_fields['GroupBy'])
        # Creates label: "GroupBy (req)"
    """
    if field_info is not None:
        req_opt = 'req' if field_info.is_required() else 'opt'
        label_text = f'{field_name} ({req_opt})'
    else:
        label_text = field_name

    label = tb.Label(master=parent, text=label_text, width=width)
    return label


def create_labeled_entry(
    parent,
    field_name: str,
    field_info: Optional[FieldInfo] = None,
    tooltip: Optional[str] = None,
    default_value: Optional[str] = None,
    width: int = 25,
    entry_width: int = 25,
) -> tuple[tb.Frame, tb.Entry]:
    """
    Create a labeled entry field (label + entry in a frame).

    Args:
        parent: Parent frame
        field_name: Name of the field
        field_info: Optional Pydantic FieldInfo for requirement status
        tooltip: Optional tooltip text
        default_value: Optional default value to populate
        width: Label width
        entry_width: Entry width

    Returns:
        tuple: (container_frame, entry_widget)
    """
    frame = tb.Frame(parent)
    frame.pack(fill=X, expand=NO, pady=5)

    label = create_field_label(frame, field_name, field_info, width)
    label.pack(side=LEFT, padx=5)

    entry = tb.Entry(master=frame, width=entry_width)
    entry.pack(side=LEFT, padx=5)

    if default_value:
        entry.insert(0, str(default_value))

    if tooltip:
        ToolTip(entry, tooltip)

    return frame, entry


def create_labeled_combobox(
    parent,
    field_name: str,
    values: list,
    field_info: Optional[FieldInfo] = None,
    tooltip: Optional[str] = None,
    default_value: Optional[str] = None,
    width: int = 25,
    combo_width: int = 24,
) -> tuple[tb.Frame, tb.Combobox]:
    """
    Create a labeled combobox (label + dropdown in a frame).

    Args:
        parent: Parent frame
        field_name: Name of the field
        values: List of values for the dropdown
        field_info: Optional Pydantic FieldInfo for requirement status
        tooltip: Optional tooltip text
        default_value: Optional default value to pre-select
        width: Label width
        combo_width: Combobox width

    Returns:
        tuple: (container_frame, combobox_widget)
    """
    frame = tb.Frame(parent)
    frame.pack(fill=X, expand=NO, pady=5)

    label = create_field_label(frame, field_name, field_info, width)
    label.pack(side=LEFT, padx=5)

    combo = tb.Combobox(master=frame, values=values, width=combo_width)
    combo.pack(side=LEFT, padx=5)

    # Set default value
    if default_value and default_value in values:
        combo.set(default_value)
    elif values:
        combo.current(0)  # Select first value by default

    if tooltip:
        ToolTip(combo, tooltip)

    return frame, combo


def extract_field_name_from_key(key: str) -> str:
    """
    Extract the field name from a widget key.

    Legacy function for backwards compatibility with old key format.
    Will be deprecated once full refactor is complete.

    Args:
        key: Widget key (e.g., "Name (req, str)" or "Name")

    Returns:
        Field name (e.g., "Name")

    Example:
        >>> extract_field_name_from_key("GroupBy (req, str)")
        "GroupBy"
        >>> extract_field_name_from_key("Name")
        "Name"
    """
    # Check if it's the new format (no parentheses)
    if '(' not in key:
        return key

    # Old format - parse out the field name
    import re

    label_parts = re.split(r'[(),]', key)
    label_parts = [part.strip() for part in label_parts if part.strip()]
    return label_parts[0] if label_parts else key
