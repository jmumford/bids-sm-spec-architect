"""
Input Widgets - Top-level BIDS Stats Model fields

Dynamically generates widgets for BIDSStatsModel top-level fields using
the WidgetFactory and bsmschema Pydantic models.
"""

import ttkbootstrap as tb
from bsmschema.models import BIDSStatsModel
from ttkbootstrap.constants import *

from stats_spec_architect.gui.bsmschema_introspector import BSMSchemaIntrospector
from stats_spec_architect.gui.widget_factory import ToolTip, WidgetFactory


class CreateInputWidgets:
    """
    Populates frame with Input Setting widgets.

    Fully dynamic - auto-generates widgets from BIDSStatsModel Pydantic definition.
    """

    def __init__(self, master):
        self.master = master
        self.widget_output = {}

        # Create widget factory
        self.widget_factory = WidgetFactory()

        # Extract field docstrings from bsmschema for tooltips
        self.field_docs = BSMSchemaIntrospector.get_field_docstrings(BIDSStatsModel)

        self.create_top_level_widgets()

    def create_top_level_widgets(self):
        """Create widgets for top-level BIDSStatsModel fields dynamically."""

        # Exclude Nodes and Edges (they have their own GUI sections)
        exclude_fields = ['Nodes', 'Edges']

        # Auto-generate widgets for all other top-level fields
        for field_name, field_info in BIDSStatsModel.model_fields.items():
            if field_name in exclude_fields:
                continue

            if field_name == 'Input':
                # Special handling for Input section (dict with sub-fields)
                self._create_input_section()
            else:
                # Standard fields (Name, BIDSModelVersion, Description)
                widget = self._create_standard_field(field_name, field_info)

                # Store with simple field name as key
                self.widget_output[field_name] = widget

    def _create_standard_field(self, field_name: str, field_info):
        """
        Create a standard input field using the widget factory.

        Args:
            field_name: Name of the field
            field_info: Pydantic FieldInfo from BIDSStatsModel

        Returns:
            Widget (Entry or Combobox)
        """
        # Create container frame
        frame = tb.Frame(self.master)
        frame.pack(fill=X, expand=NO, pady=5)

        # Special case for BIDSModelVersion - should be a dropdown
        if field_name == 'BIDSModelVersion':
            # Build label from Pydantic field_info
            req_opt = 'req' if field_info.is_required() else 'opt'
            label_text = f'BIDS Model Version ({req_opt})'
            label = tb.Label(master=frame, text=label_text, width=25)
            label.pack(side=LEFT, padx=5)

            combo = tb.Combobox(master=frame, values=['1.0.0'], width=24)
            combo.pack(side=LEFT, padx=5)
            combo.current(0)

            # Add tooltip
            tooltip = self.field_docs.get(field_name, '')
            if tooltip:
                ToolTip(combo, tooltip)

            return combo

        # For other fields (Name, Description) use standard entry
        req_opt = 'req' if field_info.is_required() else 'opt'
        label_text = f'{field_name} ({req_opt}, str)'

        label = tb.Label(master=frame, text=label_text, width=25)
        label.pack(side=LEFT, padx=5)

        entry = tb.Entry(master=frame, width=25)
        entry.pack(side=LEFT, padx=5)

        # Add tooltip from bsmschema
        tooltip = self.field_docs.get(field_name, '')
        if tooltip:
            ToolTip(entry, tooltip)

        return entry

    def _create_input_section(self):
        """Create Input section with task, subject, run, session fields."""
        inputs_frame = tb.Frame(self.master)
        inputs_frame.pack(fill=X, expand=NO, pady=5)

        # Section label
        input_section_label = tb.Label(master=inputs_frame, text='Input', width=25)
        input_section_label.pack(side=LEFT, expand=NO, pady=5)

        # Add tooltip from bsmschema (with fallback)
        tooltip = self.field_docs.get(
            'Input',
            'Dictionary specification of input images - filter by BIDS entities',
        )
        ToolTip(input_section_label, tooltip)

        # Create widgets for each input field
        self.widget_output['Input'] = {}
        fields = ['subject', 'run', 'task', 'session']

        for field in fields:
            # Store with simple field name as key
            self.widget_output['Input'][field] = self._create_input_field(
                inputs_frame, field
            )

    def _create_input_field(self, parent_frame, field_name: str):
        """
        Create an individual input field (task, subject, run, or session).

        Args:
            parent_frame: Parent frame
            field_name: Name of the field (task, subject, run, or session)

        Returns:
            Entry widget
        """
        field_frame = tb.Frame(parent_frame)
        field_frame.pack(side=LEFT, expand=NO, pady=5)

        # Configure grid column to center content
        field_frame.columnconfigure(0, weight=1)

        label = tb.Label(
            master=field_frame, text=f'{field_name} (opt, list of strings)', width=20
        )
        label.grid(row=0, column=0, padx=5, sticky='ew')

        entry = tb.Entry(master=field_frame, width=15)
        entry.grid(row=1, column=0, padx=5)

        # Add tooltip - dynamic if we had the docs, but these are entity filters
        tooltip_text = f'List of {field_name} values to include (e.g., ["01", "02"] or leave empty for all)'
        ToolTip(entry, tooltip_text)

        return entry
