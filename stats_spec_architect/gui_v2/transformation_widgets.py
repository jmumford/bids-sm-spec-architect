"""
Transformation Widgets - Pydantic-based transformation interface

This module provides the transformation widget component that auto-generates
widgets from Pydantic transformation models.
"""

import collections
from functools import partial
from tkinter import messagebox, ttk

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from stats_spec_architect.gui_v2.model_discovery import discover_transformation_models
from stats_spec_architect.gui_v2.widget_factory import WidgetFactory
from stats_spec_architect.validation.transformation_models import (
    get_available_transformations,
)


class AddTransformationWidgets:
    """
    Widget manager for transformations using Pydantic models.

    This replaces the JSON schema-based transformation widget generator
    with a Pydantic model-based approach.
    """

    def __init__(self, parent_frame):
        """
        Initialize transformation widget manager.

        Args:
            parent_frame: Parent tkinter frame to attach widgets to
        """
        self.number = 0
        self.master = tb.Frame(parent_frame)
        self.master.pack(fill=X, expand=NO, pady=5)

        # Auto-discover all transformation models from transformation_models module
        # No hardcoded imports needed - new transformations are automatically detected!
        self.transformation_models = discover_transformation_models()

        # Widget factory - auto-detects validator enums from models
        self.widget_factory = WidgetFactory(
            transformation_models=self.transformation_models
        )

        self.create_widgets()

    def create_widgets(self):
        """Create the main transformation UI structure."""
        self.frame = tb.Frame(self.master)
        self.frame.pack(fill=X, expand=NO, pady=5)

        self.add_button = tb.Button(
            self.frame, text='Add Transformation', command=self.add_transformation_tab
        )
        self.add_button.pack(side=LEFT, padx=5, fill=X, expand=NO)

        self.widget_output = collections.defaultdict(dict)

    def add_transformation_tab(self):
        """Add a new transformation tab to the notebook."""
        if self.number == 0:
            # First transformation - create Transformer selector and notebook
            self.widget_output['Transformer (req)'] = (
                self._create_transformer_selector()
            )

            # Initialize tab frames
            self.transformations_notebook = ttk.Notebook(self.master)
            self.transformations_notebook.pack(side=LEFT, pady=5, padx=300)

        # Create a new tab
        notebook_frame = tb.Frame(self.transformations_notebook, width=1000, height=300)
        notebook_frame.pack(fill=BOTH, expand=1)

        # Create dropdown with transformation names
        transformation_values = get_available_transformations()
        transformation_combo = self._create_transformation_selector(
            notebook_frame, transformation_values
        )

        # Bind selection event to populate fields
        transformation_combo.bind(
            '<<ComboboxSelected>>',
            partial(
                self._on_transformation_selected,
                transformation_combo=transformation_combo,
                container_frame=notebook_frame,
                tab_index=self.number,
            ),
        )

        # Add tab to notebook
        self.transformations_notebook.add(
            notebook_frame, text=f'Transformation {self.number + 1}'
        )

        # Auto-select the newly added tab
        self.transformations_notebook.select(self.number)

        self.number += 1

    def _create_transformer_selector(self):
        """Create the Transformer version selector."""
        widget_pair_frame = tb.Frame(self.master)
        widget_pair_frame.pack(fill=X, expand=NO, pady=5)

        label = tb.Label(master=widget_pair_frame, text='Transformer (req)', width=25)
        label.pack(side=LEFT, padx=5)

        # Get Transformer values dynamically from bsmschema TransformerID Literal
        transformer_values = self._get_transformer_values()

        combo = tb.Combobox(
            master=widget_pair_frame, values=transformer_values, width=24
        )
        combo.pack(side=LEFT, padx=5)
        if transformer_values:
            combo.current(0)  # Default to first option

        return combo

    def _get_transformer_values(self):
        """Get valid Transformer values from bsmschema TransformerID Literal."""
        try:
            from typing import get_args

            from bsmschema.models import TransformerID

            # TransformerID is a Literal - extract its values
            values = get_args(TransformerID)
            return list(values) if values else ['pybids-transforms-v1']
        except Exception:
            # Fallback if extraction fails
            return ['pybids-transforms-v1']

    def _create_transformation_selector(self, parent, transformation_values):
        """Create the transformation type selector."""
        selector_frame = tb.Frame(parent)
        selector_frame.pack(fill=X, expand=NO, pady=5)

        label = tb.Label(master=selector_frame, text='Name', width=25)
        label.pack(side=LEFT, padx=5)

        combo = tb.Combobox(
            master=selector_frame, values=transformation_values, width=24
        )
        combo.pack(side=LEFT, padx=5)

        # Add initial tooltip
        from stats_spec_architect.gui_v2.widget_factory import ToolTip

        self.transformation_tooltip = ToolTip(
            combo,
            'Select a transformation type - hover after selection to see description',
        )

        return combo

    def _on_transformation_selected(
        self, event, transformation_combo=None, container_frame=None, tab_index=None
    ):
        """
        Handle transformation selection - populate appropriate widgets.

        Args:
            event: Tkinter event
            transformation_combo: Combobox widget with transformation name
            container_frame: Frame to add widgets to
            tab_index: Index for storing widget references
        """
        # Delete existing widgets if already created for a different transformation
        row_children = container_frame.winfo_children()
        num_children = len(row_children)
        if num_children > 1:  # Keep the selector, delete the rest
            for child in row_children[1:]:
                child.destroy()

        # Get selected transformation
        transform_name = transformation_combo.get()

        # Update combobox tooltip with transformation description
        model_class = self.transformation_models.get(transform_name)
        if model_class and model_class.__doc__:
            # Update the tooltip text dynamically
            if hasattr(transformation_combo, '_tooltip'):
                # Remove old tooltip bindings
                transformation_combo.unbind('<Enter>')
                transformation_combo.unbind('<Leave>')

            # Add new tooltip with transformation description
            from stats_spec_architect.gui_v2.widget_factory import ToolTip

            transformation_combo._tooltip = ToolTip(
                transformation_combo, f'{transform_name}: {model_class.__doc__.strip()}'
            )

        # Create widgets for this transformation
        widgets = self._create_transformation_widgets(container_frame, transform_name)

        # Store widget references
        self.widget_output[f'Instructions_{tab_index}'] = widgets

        # Add delete button after transformation widgets
        self._add_delete_button(container_frame, tab_index)

    def _create_transformation_widgets(self, parent_frame, transform_name):
        """
        Create widgets for a specific transformation using Pydantic model.

        Args:
            parent_frame: Frame to add widgets to
            transform_name: Name of transformation

        Returns:
            Dictionary with 'Name' and widget references
        """
        # Get the Pydantic model for this transformation
        model_class = self.transformation_models.get(transform_name)
        if not model_class:
            print(f'Warning: No model found for transformation {transform_name}')
            return {'Name': transform_name}

        # Create a container for the widgets
        widgets_container = tb.Frame(parent_frame)
        widgets_container.pack(fill=BOTH, expand=YES, padx=10, pady=10)

        # Generate widgets from Pydantic model (exclude 'Name' since we already have it)
        field_widgets = self.widget_factory.create_widgets_from_model(
            widgets_container,
            model_class,
            exclude_fields=['Name'],
            transformation_name=transform_name,
        )

        # Build output dictionary with Name + all field widgets
        output = {'Name': transform_name}
        output.update(field_widgets)

        return output

    def _add_delete_button(self, parent_frame, tab_index):
        """Add a delete button to a transformation tab."""
        delete_frame = tb.Frame(parent_frame)
        delete_frame.pack(side='top', anchor='e', padx=10, pady=10)

        delete_button = tb.Button(
            delete_frame,
            text=f'Delete Transformation {tab_index + 1}',
            command=partial(self.delete_transformation, tab_index),
            bootstyle='warning',
        )
        delete_button.pack()

    def delete_transformation(self, tab_index):
        """
        Delete a transformation and renumber all subsequent transformations.

        Args:
            tab_index: Index of the transformation to delete (0-based)
        """
        # Confirm deletion
        result = messagebox.askyesno(
            'Delete Transformation',
            f'Are you sure you want to delete Transformation {tab_index + 1}?\n\n'
            'All transformations after this will be renumbered.',
        )

        if not result:
            return

        # Rebuild widget_output with renumbered Instructions
        # We need to rebuild to preserve insertion order in the dict
        new_widget_output = collections.defaultdict(dict)

        # Copy non-Instructions items first
        for key, value in self.widget_output.items():
            if not key.startswith('Instructions_'):
                new_widget_output[key] = value

        # Renumber and add Instructions items
        instruction_counter = 0
        for i in range(self.number):
            if i == tab_index:
                # Skip the deleted transformation
                continue
            old_key = f'Instructions_{i}'
            if old_key in self.widget_output:
                new_key = f'Instructions_{instruction_counter}'
                new_widget_output[new_key] = self.widget_output[old_key]
                instruction_counter += 1

        # Replace the old widget_output
        self.widget_output = new_widget_output

        # Remove the tab from the notebook
        self.transformations_notebook.forget(tab_index)

        # Update all remaining tab titles
        for i in range(self.transformations_notebook.index('end')):
            self.transformations_notebook.tab(i, text=f'Transformation {i + 1}')

        # Update delete button labels in remaining tabs
        self._update_delete_button_labels()

        # Decrement counter
        self.number -= 1

        # If no transformations left, remove the notebook and Transformer selector
        if self.number == 0:
            self.transformations_notebook.destroy()
            # Remove Transformer selector
            if 'Transformer (req)' in self.widget_output:
                widget = self.widget_output['Transformer (req)']
                if hasattr(widget, 'master'):
                    widget.master.destroy()
                del self.widget_output['Transformer (req)']

    def _update_delete_button_labels(self):
        """Update all delete button labels after renumbering."""
        for i in range(self.transformations_notebook.index('end')):
            # Get the tab frame
            tab_frame = self.transformations_notebook.nametowidget(
                self.transformations_notebook.tabs()[i]
            )
            # Find the delete button and update its text
            for child in tab_frame.winfo_children():
                if isinstance(child, tb.Frame):
                    for button in child.winfo_children():
                        if isinstance(button, tb.Button) and button.cget(
                            'text'
                        ).startswith('Delete'):
                            button.configure(text=f'Delete Transformation {i + 1}')
                            # Update command to use correct index
                            button.configure(
                                command=partial(self.delete_transformation, i)
                            )
