"""
Transformation Widgets - Pydantic-based transformation interface

This module provides the transformation widget component that auto-generates
widgets from Pydantic transformation models.
"""

import collections
from functools import partial
from tkinter import messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from stats_spec_architect.gui_v3.model_discovery import discover_transformation_models
from stats_spec_architect.gui_v3.widget_factory import WidgetFactory
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

        # Use Menubutton (button with dropdown menu) for solid button appearance
        transformation_values = get_available_transformations()

        self.add_button = tb.Menubutton(
            self.frame,
            text='➕ Add Transformation',
            bootstyle='primary',
        )
        self.add_button.pack(side=LEFT, padx=5)

        # Create menu with transformation options
        menu = tb.Menu(self.add_button)
        self.add_button['menu'] = menu

        # Add each transformation as a menu item
        for transform_name in transformation_values:
            menu.add_command(
                label=transform_name,
                command=partial(self.add_transformation_with_type, transform_name),
            )

        self.widget_output = collections.defaultdict(dict)

    def add_transformation_with_type(self, transform_name):
        """Add a new transformation with type pre-selected."""
        if self.number == 0:
            # First transformation - create Transformer selector and accordion container
            self.widget_output['Transformer'] = self._create_transformer_selector()

            # Initialize accordion container (vertical list of collapsible sections)
            self.transformations_container = tb.Frame(self.master)
            self.transformations_container.pack(fill=X, expand=NO, pady=5)

        # Store current index
        tab_index = self.number

        # Create a new collapsible section
        transformation_frame = self._create_transformation_section(
            tab_index, initial_title=f'{tab_index + 1}. {transform_name}'
        )

        # Create dropdown with transformation names (pre-filled)
        transformation_values = get_available_transformations()
        transformation_combo = self._create_transformation_selector(
            transformation_frame, transformation_values
        )

        # Set the value to the selected transformation
        transformation_combo.set(transform_name)

        # Create the fields immediately
        widgets = self._create_transformation_widgets(
            transformation_frame, transform_name
        )
        self.widget_output[f'Instructions_{tab_index}'] = widgets

        # Add delete button
        self._add_delete_button(transformation_frame, tab_index)

        # Update tooltip for the combobox
        model_class = self.transformation_models.get(transform_name)
        if model_class and model_class.__doc__:
            from stats_spec_architect.gui_v3.widget_factory import ToolTip

            transformation_combo._tooltip = ToolTip(
                transformation_combo, f'{transform_name}: {model_class.__doc__.strip()}'
            )

        # Bind selection event for future changes
        transformation_combo.bind(
            '<<ComboboxSelected>>',
            partial(
                self._on_transformation_selected,
                transformation_combo=transformation_combo,
                container_frame=transformation_frame,
                tab_index=tab_index,
            ),
        )

        self.number += 1

    def _create_transformation_section(self, index, initial_title=None):
        """Create a collapsible section for a transformation."""
        from stats_spec_architect.gui_v3.utils import CollapsingFrame

        # Create collapsing frame if not exists
        if not hasattr(self, 'transformation_cf'):
            self.transformation_cf = CollapsingFrame(
                self.transformations_container, padding=5
            )
            self.transformation_cf.pack(fill=X, expand=NO)

        # Create frame for this transformation's content
        trans_frame = tb.Frame(self.transformation_cf, padding=10)

        # Determine title
        title = (
            initial_title if initial_title else f'{index + 1}. Select transformation...'
        )

        # Add to collapsing frame with title
        self.transformation_cf.add(
            child=trans_frame,
            title=title,
            bootstyle='info',
        )

        # Store frame reference
        if not hasattr(self, 'transformation_frames'):
            self.transformation_frames = {}
        self.transformation_frames[index] = trans_frame

        return trans_frame

    def _update_transformation_title(self, index, transform_name):
        """Update the header title for a transformation section."""
        if not hasattr(self, 'transformation_cf'):
            return

        # Find the header label for this transformation
        trans_frame = self.transformation_frames.get(index)
        if trans_frame:
            grid_info = trans_frame.grid_info()
            if grid_info:
                child_row = grid_info['row']
                header_row = child_row - 1

                # Find and update the header label
                for widget in self.transformation_cf.grid_slaves(row=header_row):
                    for child in widget.winfo_children():
                        if isinstance(child, tb.Label):
                            child.configure(text=f'{index + 1}. {transform_name}')
                            break

    def _create_transformer_selector(self):
        """Create the Transformer version selector."""
        from bsmschema.models import Transformations

        widget_pair_frame = tb.Frame(self.master)
        widget_pair_frame.pack(fill=X, expand=NO, pady=5)

        # Build label from Pydantic Transformations model (not hardcoded!)
        transformer_field = Transformations.model_fields.get('Transformer')
        req_opt = 'req' if transformer_field.is_required() else 'opt'
        label_text = f'Transformer ({req_opt})'

        label = tb.Label(master=widget_pair_frame, text=label_text, width=25)
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
        from stats_spec_architect.gui_v3.widget_factory import ToolTip

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

        # Update the collapsible section title
        self._update_transformation_title(tab_index, transform_name)

        # Update combobox tooltip with transformation description
        model_class = self.transformation_models.get(transform_name)
        if model_class and model_class.__doc__:
            # Update the tooltip text dynamically
            if hasattr(transformation_combo, '_tooltip'):
                # Remove old tooltip bindings
                transformation_combo.unbind('<Enter>')
                transformation_combo.unbind('<Leave>')

            # Add new tooltip with transformation description
            from stats_spec_architect.gui_v3.widget_factory import ToolTip

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

        # Remove the transformation frame from accordion
        if tab_index in self.transformation_frames:
            trans_frame = self.transformation_frames[tab_index]

            # Get grid info and destroy both header and content
            grid_info = trans_frame.grid_info()
            if grid_info:
                child_row = grid_info['row']
                header_row = child_row - 1

                # Destroy header and child
                for widget in self.transformation_cf.grid_slaves(row=header_row):
                    widget.destroy()
                trans_frame.destroy()

        # Rebuild transformation_frames dict with renumbered keys
        new_transformation_frames = {}
        trans_counter = 0
        for i in range(self.number):
            if i == tab_index:
                continue
            if i in self.transformation_frames:
                new_transformation_frames[trans_counter] = self.transformation_frames[i]
                trans_counter += 1

        self.transformation_frames = new_transformation_frames

        # Update all remaining section titles
        self._update_all_transformation_titles()

        # Update delete button labels
        self._update_delete_button_labels()

        # Decrement counter
        self.number -= 1

        # If no transformations left, remove the container and Transformer selector
        if self.number == 0:
            if hasattr(self, 'transformations_container'):
                self.transformations_container.destroy()
                delattr(self, 'transformations_container')
            if hasattr(self, 'transformation_cf'):
                delattr(self, 'transformation_cf')
            if hasattr(self, 'transformation_frames'):
                delattr(self, 'transformation_frames')
            # Remove Transformer selector
            if 'Transformer' in self.widget_output:
                widget = self.widget_output['Transformer']
                if hasattr(widget, 'master'):
                    widget.master.destroy()
                del self.widget_output['Transformer']

    def _update_all_transformation_titles(self):
        """Update all transformation section titles after renumbering."""
        for i in range(len(self.transformation_frames)):
            if i in self.transformation_frames:
                trans_frame = self.transformation_frames[i]

                # Get the Name from widget_output to update title
                instruction_key = f'Instructions_{i}'
                if instruction_key in self.widget_output:
                    instruction_data = self.widget_output[instruction_key]
                    transform_name = instruction_data.get(
                        'Name', 'Select transformation...'
                    )
                else:
                    transform_name = 'Select transformation...'

                # Update header
                grid_info = trans_frame.grid_info()
                if grid_info:
                    child_row = grid_info['row']
                    header_row = child_row - 1
                    for widget in self.transformation_cf.grid_slaves(row=header_row):
                        for child in widget.winfo_children():
                            if isinstance(child, tb.Label):
                                child.configure(text=f'{i + 1}. {transform_name}')
                                break

    def _update_delete_button_labels(self):
        """Update all delete button labels after renumbering."""
        for i in range(len(self.transformation_frames)):
            if i in self.transformation_frames:
                trans_frame = self.transformation_frames[i]
                # Find the delete button and update its text
                for child in trans_frame.winfo_children():
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
