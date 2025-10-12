"""
Node Widgets - Pydantic-based node interface

Dynamically generates node widgets from bsmschema Node, Model, Contrast models.
"""

import collections
from functools import partial
from tkinter import messagebox

import ttkbootstrap as tb
from bsmschema.models import Contrast, DummyContrasts, Model, Node
from ttkbootstrap.constants import *

from stats_spec_architect.gui_v2.bsmschema_introspector import BSMSchemaIntrospector
from stats_spec_architect.gui_v2.transformation_widgets import AddTransformationWidgets
from stats_spec_architect.gui_v2.widget_factory import ToolTip, WidgetFactory


class AddNode:
    """
    Widget manager for nodes using Pydantic models.

    Fully dynamic - auto-generates widgets from bsmschema Node, Model, Contrast models.
    """

    def __init__(self, master):
        self.number = 0
        self.master = master
        self.node_output = collections.defaultdict(dict)
        self.contrast_counter = collections.defaultdict(dict)

        # Create widget factory
        self.widget_factory = WidgetFactory()

        # Extract docstrings from bsmschema models
        self.node_docs = BSMSchemaIntrospector.get_field_docstrings(Node)
        self.model_docs = BSMSchemaIntrospector.get_field_docstrings(Model)
        self.contrast_docs = BSMSchemaIntrospector.get_field_docstrings(Contrast)
        self.dummy_docs = BSMSchemaIntrospector.get_field_docstrings(DummyContrasts)

        # Add Node button
        add_button_frame = tb.Frame(self.master)
        add_button_frame.pack(fill=X, expand=NO, pady=5)
        add_button = tb.Button(
            add_button_frame, text='Add Node', command=self.make_node_subframe
        )
        add_button.pack(side=LEFT, padx=5, fill=X, expand=NO)

        self.number_of_nodes = 0

        # Store frame references for deletion and contrast/dummy contrast creation
        self.node_frames = {}  # Stores the child content frames
        self.node_header_labels = {}  # Stores the header label widgets
        self.contrast_frames = {}  # Stores the contrast frames for each node
        self.dummy_contrast_frames = {}  # Stores the dummy contrast frames

        # Import CollapsingFrame
        from stats_spec_architect.gui_v2.utils import CollapsingFrame

        self.node_specific_cf = CollapsingFrame(self.master, padding=10)
        self.node_specific_cf.pack(fill=BOTH)

    def make_node_subframe(self):
        """Create a new node in a collapsing frame."""
        self.number_of_nodes = self.number_of_nodes + 1
        self.contrast_counter[f'node_{self.number_of_nodes}_num_contrasts'] = 0
        self.contrast_counter[f'node_{self.number_of_nodes}_num_dummy_contrasts'] = 0

        # Make a collapsible frame for this node
        frame_win_node_specific_cf = tb.Frame(self.node_specific_cf, padding=10)

        # Store frame reference for potential deletion
        self.node_frames[self.number_of_nodes] = frame_win_node_specific_cf

        self.create_node_widgets(self.number_of_nodes, frame_win_node_specific_cf)
        self.node_specific_cf.add(
            child=frame_win_node_specific_cf,
            title=f'Node {self.number_of_nodes}',
            bootstyle=SECONDARY,
        )

        # Store reference to the header label for later updates
        # The header label is in the frame's grid row - 1
        grid_info = frame_win_node_specific_cf.grid_info()
        if grid_info:
            child_row = grid_info['row']
            header_row = child_row - 1
            # Find the header label in the header frame
            for widget in self.node_specific_cf.grid_slaves(row=header_row):
                for child in widget.winfo_children():
                    if isinstance(child, tb.Label):
                        self.node_header_labels[self.number_of_nodes] = child
                        break

        # Auto-scroll to make the new node visible
        self._scroll_to_node(frame_win_node_specific_cf)

    def _open_text_editor(self, entry_widget, title):
        """
        Open a popup text editor for editing long text values.

        Args:
            entry_widget: The Entry widget to edit
            title: Title for the popup window
        """
        import tkinter as tk

        # Create popup window with superhero theme
        popup = tb.Toplevel(title=title)
        popup.geometry('600x400')

        # Instructions
        instructions = tb.Label(
            popup,
            text='Enter variables as comma-separated list or one per line',
            font=('Helvetica', 10),
            bootstyle='inverse-secondary',
        )
        instructions.pack(pady=10, fill='x')

        # Text widget with scrollbar
        text_frame = tb.Frame(popup)
        text_frame.pack(fill='both', expand=True, padx=10, pady=5)

        scrollbar = tb.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')

        text_widget = tk.Text(
            text_frame, wrap='word', yscrollcommand=scrollbar.set, font=('Courier', 11)
        )
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=text_widget.yview)

        # Get current value from entry
        current_value = entry_widget.get()
        # Convert comma-separated to one-per-line for easier editing
        if current_value:
            lines = [v.strip() for v in current_value.split(',')]
            text_widget.insert('1.0', '\n'.join(lines))

        # Focus on text widget
        text_widget.focus_set()

        # Define button actions
        def save_and_close():
            # Get text from editor
            content = text_widget.get('1.0', 'end-1c')
            # Convert back to comma-separated
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            result = ', '.join(lines)
            # Update entry widget
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, result)

            # Update button text to show what's in there
            if hasattr(entry_widget, '_edit_button'):
                button = entry_widget._edit_button
                if result:
                    # Show first few variables
                    preview = result[:40] + '...' if len(result) > 40 else result
                    button.configure(text=preview)
                else:
                    button.configure(text='Click to edit variables...')

            popup.destroy()

        def cancel():
            popup.destroy()

        # Buttons at bottom
        button_frame = tb.Frame(popup)
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)

        save_button = tb.Button(
            button_frame,
            text='Save',
            command=save_and_close,
            bootstyle='primary',
            width=15,
        )
        save_button.pack(side='left', padx=5)

        cancel_button = tb.Button(
            button_frame,
            text='Cancel',
            command=cancel,
            bootstyle='warning',
            width=15,
        )
        cancel_button.pack(side='right', padx=5)

        # Make modal
        popup.transient()
        popup.grab_set()

    def _scroll_to_node(self, frame):
        """Scroll to make a node frame visible."""

        # Schedule scroll after layout is complete
        def do_scroll():
            # Walk up the widget hierarchy to find the canvas
            widget = frame
            canvas = None
            while widget:
                parent = widget.master if hasattr(widget, 'master') else None
                if parent and hasattr(parent, 'canvas'):
                    canvas = parent.canvas
                    break
                widget = parent

            if canvas:
                # Update layout
                canvas.update_idletasks()
                # Get scroll region
                bbox = canvas.bbox('all')
                if bbox:
                    # Calculate position as fraction of total height
                    frame_y = frame.winfo_rooty() - canvas.winfo_rooty()
                    total_height = bbox[3]
                    if total_height > 0:
                        # Scroll to show the frame near the top
                        fraction = max(0, min(1, frame_y / total_height))
                        canvas.yview_moveto(fraction)

        # Delay scroll to ensure layout is complete
        frame.after(100, do_scroll)

    def create_node_widgets(self, node_number, frame):
        """
        Create widgets for a node dynamically from bsmschema Node model.

        Args:
            node_number: Sequential node number
            frame: Frame to add widgets to
        """
        # Auto-generate node-level fields from Node model
        # Exclude: Transformations (handled separately), Model (handled separately),
        #          Contrasts (handled with button), DummyContrasts (handled with button)
        exclude_fields = [
            'Transformations',
            'Model',
            'Contrasts',
            'DummyContrasts',
            'Description',
        ]

        for field_name, field_info in Node.model_fields.items():
            if field_name in exclude_fields:
                continue

            # Create widget based on field type
            if field_name == 'GroupBy':
                # Special handling - checkboxes for GroupBy
                widget = self._create_groupby_checkboxes(frame, field_info)
            else:
                # Standard field (Level, Name) - use widget factory
                widget = self._create_node_field(frame, field_name, field_info)

            # Store widget
            req_opt = 'req' if field_info.is_required() else 'opt'
            if field_name == 'Level':
                key = f'{field_name} ({req_opt})'
            else:
                key = f'{field_name} ({req_opt}, str)'
            self.node_output[f'node_{node_number}'][key] = widget

        # Add Transformations section
        self.node_output[f'node_{node_number}']['transformations'] = (
            AddTransformationWidgets(frame)
        )

        # Add Model section
        self.create_model_widgets(frame, node_number)

        # Add Contrast button and DummyContrast button
        self._create_contrast_buttons(frame, node_number)

        # Add Delete Node button at bottom
        self._create_delete_button(frame, node_number)

    def _create_node_field(self, frame, field_name: str, field_info):
        """Create a standard node field (Level or Name)."""
        import typing
        from typing import get_args, get_origin

        container = tb.Frame(frame)
        container.pack(fill=X, expand=NO, pady=5)

        # Check if it's a simple Literal enum (e.g., Level with NodeLevel)
        origin = get_origin(field_info.annotation)

        # Only treat as dropdown if origin is EXACTLY typing.Literal
        # (not Union, not list, etc. even if they have __args__)
        if origin is typing.Literal:
            # Get Literal values
            try:
                if hasattr(field_info.annotation, '__args__'):
                    values = list(field_info.annotation.__args__)
                else:
                    values = list(get_args(field_info.annotation))

                # Create dropdown
                req_opt = 'req' if field_info.is_required() else 'opt'
                label_text = f'{field_name} ({req_opt})'

                label = tb.Label(master=container, text=label_text, width=25)
                label.pack(side=LEFT, padx=5)

                combo = tb.Combobox(master=container, values=values, width=24)
                combo.pack(side=LEFT, padx=5)

                # Add tooltip
                tooltip = self.node_docs.get(field_name, '')
                if tooltip:
                    ToolTip(combo, tooltip)

                return combo
            except:
                pass

        # Standard text entry (Name field)
        req_opt = 'req' if field_info.is_required() else 'opt'
        label_text = f'{field_name} ({req_opt}, str)'

        label = tb.Label(master=container, text=label_text, width=25)
        label.pack(side=LEFT, padx=5)

        entry = tb.Entry(master=container, width=25)
        entry.pack(side=LEFT, padx=5)

        # Add tooltip
        tooltip = self.node_docs.get(field_name, '')
        if tooltip:
            ToolTip(entry, tooltip)

        return entry

    def _create_groupby_checkboxes(self, frame, field_info):
        """
        Create GroupBy checkboxes.

        Note: The GroupBy field accepts any metadata field, but we provide
        checkboxes for the most common: run, session, subject, contrast.
        """
        # Import the checkbox row widget
        from stats_spec_architect.gui_v2.utils import CreateCheckbuttonRow

        # Standard GroupBy options (from BIDS spec - these are reserved strings)
        groupby_options = ['run', 'session', 'subject', 'contrast']

        widget = CreateCheckbuttonRow('GroupBy (req)', groupby_options, frame)

        # Add tooltip to the frame
        tooltip = self.node_docs.get('GroupBy', 'Group by these variables')
        if tooltip and hasattr(widget, 'form_field_container'):
            ToolTip(widget.form_field_container, tooltip)

        return widget

    def create_model_widgets(self, frame, node_number):
        """
        Create Model section widgets dynamically from bsmschema Model.

        Args:
            frame: Parent frame
            node_number: Node number
        """
        self.node_output[f'node_{node_number}']['Model'] = {}

        # Create Model section container
        model_frames_holder = tb.Frame(frame)
        model_frames_holder.pack(fill=X, expand=NO, pady=5)

        # Model section label
        model_label = tb.Label(master=model_frames_holder, text='Model', width=25)
        model_label.pack(side=LEFT, padx=5)

        # Add tooltip for Model section
        if Model.__doc__:
            ToolTip(model_label, Model.__doc__.strip())

        # Create two rows: required fields on top, optional on bottom
        top_row_frame = tb.Frame(model_frames_holder)
        top_row_frame.pack(fill=X, expand=NO, pady=5)
        bottom_row_frame = tb.Frame(model_frames_holder)
        bottom_row_frame.pack(fill=X, expand=NO, pady=5)

        # Auto-generate widgets for Model fields
        # Exclude Description (inherited from _BSMBase, not needed here)
        exclude_fields = [
            'Description',
            'HRF',
            'Options',
        ]  # HRF/Options complex, handle later

        for field_name, field_info in Model.model_fields.items():
            if field_name in exclude_fields:
                continue

            # Determine which row based on required/optional
            row = top_row_frame if field_info.is_required() else bottom_row_frame

            # Create widget using widget factory
            widget = self._create_model_field(row, field_name, field_info)

            # Store widget
            req_opt = 'req' if field_info.is_required() else 'opt'

            # Determine type string for key
            if field_name == 'Type':
                key = 'Type'
            elif field_name == 'X':
                key = 'X (req, list of strings)'
            elif field_name == 'Software':
                key = f'{field_name} (opt, str)'  # Actually dict, but simplified
            else:
                key = f'{field_name} ({req_opt}, str)'

            self.node_output[f'node_{node_number}']['Model'][key] = widget

    def _create_model_field(self, parent_row, field_name: str, field_info):
        """Create a Model field widget."""
        import typing
        from typing import get_args, get_origin

        field_frame = tb.Frame(parent_row)
        field_frame.pack(side=LEFT, expand=NO, pady=5)

        # Check if it's a simple Literal enum (Type field with ModelType)
        origin = get_origin(field_info.annotation)

        # Only create dropdown if origin is EXACTLY typing.Literal
        if origin is typing.Literal:
            # It's a Literal - create dropdown
            try:
                if hasattr(field_info.annotation, '__args__'):
                    values = list(field_info.annotation.__args__)
                else:
                    values = list(get_args(field_info.annotation))

                req_opt = 'req' if field_info.is_required() else 'opt'
                label_text = f'{field_name} ({req_opt})'

                label = tb.Label(master=field_frame, text=label_text, width=20)
                label.grid(row=0, column=0, padx=5)

                combo = tb.Combobox(master=field_frame, values=values, width=18)
                combo.grid(row=1, column=0, padx=5)

                # Add tooltip
                tooltip = self.model_docs.get(field_name, '')
                if tooltip:
                    ToolTip(combo, tooltip)

                return combo
            except:
                pass

        # Standard entry field
        req_opt = 'req' if field_info.is_required() else 'opt'

        # Determine type string
        type_str = 'str'
        if 'list' in str(field_info.annotation).lower():
            type_str = 'list of strings'

        label_text = f'{field_name} ({req_opt}, {type_str})'

        label = tb.Label(master=field_frame, text=label_text, width=20)
        label.grid(row=0, column=0, padx=5)

        # For X field, use popup editor button instead of tiny entry
        if field_name == 'X':
            # Create hidden entry to store the value
            entry = tb.Entry(master=field_frame, width=0)
            entry.grid(row=1, column=0, padx=0)
            entry.grid_remove()  # Hide it

            # Create edit button that shows current value
            edit_button = tb.Button(
                field_frame,
                text='Click to edit variables...',
                command=partial(self._open_text_editor, entry, 'Model X Variables'),
                bootstyle='info-outline',
                width=30,
            )
            edit_button.grid(row=1, column=0, padx=5)

            # Store button reference so we can update its text
            entry._edit_button = edit_button
        else:
            # Standard entry field for other Model fields
            entry = tb.Entry(master=field_frame, width=18)
            entry.grid(row=1, column=0, padx=5)

        # Add tooltip
        tooltip = self.model_docs.get(field_name, '')
        if tooltip:
            ToolTip(entry, tooltip)

        return entry

    def _create_contrast_buttons(self, frame, node_number):
        """Create buttons for adding Contrasts and DummyContrasts."""
        # Add Contrast button
        contrast_frame = tb.Frame(frame, padding=10)
        contrast_frame.pack(fill=X, expand=NO, pady=5)
        contrast_button = tb.Button(
            contrast_frame,
            text='Add Contrast',
            command=partial(self.create_contrast_widgets, contrast_frame, node_number),
        )
        contrast_button.pack(side=LEFT, padx=5, fill=X, expand=NO)

        # Store contrast frame for later use (e.g., during JSON import)
        self.contrast_frames[node_number] = contrast_frame

        # Add Dummy Contrast button
        dummy_contrast_frame = tb.Frame(frame, padding=10)
        dummy_contrast_frame.pack(fill=X, expand=NO, pady=5)
        dummy_button = tb.Button(
            dummy_contrast_frame,
            text='Add Dummy Contrast',
            command=partial(
                self.create_dummy_contrast_widgets, dummy_contrast_frame, node_number
            ),
        )
        dummy_button.pack(side=LEFT, padx=5, fill=X, expand=NO)

        # Store dummy contrast frame for later use
        self.dummy_contrast_frames[node_number] = dummy_contrast_frame

    def _create_delete_button(self, frame, node_number):
        """Create delete button for this node."""
        delete_frame = tb.Frame(frame, padding=10)
        delete_frame.pack(fill=X, expand=NO, pady=10)

        delete_button = tb.Button(
            delete_frame,
            text=f'Delete Node {node_number}',
            command=partial(self.delete_node, node_number),
            bootstyle='warning',
        )
        delete_button.pack(side=RIGHT, padx=5)

    def delete_node(self, node_number):
        """
        Delete a node and renumber all subsequent nodes.

        Args:
            node_number: Number of the node to delete
        """
        # Confirm deletion
        result = messagebox.askyesno(
            'Delete Node',
            f'Are you sure you want to delete Node {node_number}?\n\n'
            'All data in this node will be lost.\n'
            'All nodes after this will be renumbered.',
        )

        if not result:
            return

        # Rebuild node_output with renumbered nodes
        new_node_output = collections.defaultdict(dict)
        node_counter = 1
        for i in range(1, self.number_of_nodes + 1):
            if i == node_number:
                # Skip the deleted node
                continue
            old_key = f'node_{i}'
            if old_key in self.node_output:
                new_key = f'node_{node_counter}'
                new_node_output[new_key] = self.node_output[old_key]
                node_counter += 1

        self.node_output = new_node_output

        # Rebuild contrast_counter with renumbered nodes
        new_contrast_counter = collections.defaultdict(int)
        node_counter = 1
        for i in range(1, self.number_of_nodes + 1):
            if i == node_number:
                continue
            old_contrast_key = f'node_{i}_num_contrasts'
            old_dummy_key = f'node_{i}_num_dummy_contrasts'

            if old_contrast_key in self.contrast_counter:
                new_contrast_key = f'node_{node_counter}_num_contrasts'
                new_contrast_counter[new_contrast_key] = self.contrast_counter[
                    old_contrast_key
                ]

            if old_dummy_key in self.contrast_counter:
                new_dummy_key = f'node_{node_counter}_num_dummy_contrasts'
                new_contrast_counter[new_dummy_key] = self.contrast_counter[
                    old_dummy_key
                ]

            node_counter += 1

        self.contrast_counter = new_contrast_counter

        # Remove UI frames (both header and content) for deleted node
        if node_number in self.node_frames:
            child_frame = self.node_frames[node_number]

            # Get the row of the child frame
            grid_info = child_frame.grid_info()
            if grid_info:
                child_row = grid_info['row']
                header_row = child_row - 1

                # Find and destroy the header frame
                for widget in self.node_specific_cf.grid_slaves(row=header_row):
                    widget.destroy()

                # Destroy the child frame
                child_frame.destroy()

        # Rebuild node_frames dict with renumbered keys
        new_node_frames = {}
        new_node_header_labels = {}
        new_contrast_frames = {}
        new_dummy_contrast_frames = {}
        node_counter = 1
        for i in range(1, self.number_of_nodes + 1):
            if i == node_number:
                continue
            if i in self.node_frames:
                new_node_frames[node_counter] = self.node_frames[i]
                if i in self.node_header_labels:
                    new_node_header_labels[node_counter] = self.node_header_labels[i]
                if i in self.contrast_frames:
                    new_contrast_frames[node_counter] = self.contrast_frames[i]
                if i in self.dummy_contrast_frames:
                    new_dummy_contrast_frames[node_counter] = (
                        self.dummy_contrast_frames[i]
                    )
                node_counter += 1

        self.node_frames = new_node_frames
        self.node_header_labels = new_node_header_labels
        self.contrast_frames = new_contrast_frames
        self.dummy_contrast_frames = new_dummy_contrast_frames

        # Update CollapsingFrame titles using stored label references
        self._update_node_titles()

        # Update delete button labels and commands
        self._update_delete_button_labels()

        # Decrement counter
        self.number_of_nodes -= 1

    def _update_node_titles(self):
        """Update all node titles in the CollapsingFrame after renumbering."""
        # Use stored label references to update titles
        for new_num in range(1, len(self.node_header_labels) + 1):
            if new_num in self.node_header_labels:
                label = self.node_header_labels[new_num]
                label.configure(text=f'Node {new_num}')
                print(f'Updated node title to: Node {new_num}')

    def _update_delete_button_labels(self):
        """Update all delete button labels after renumbering."""
        for i in range(1, len(self.node_frames) + 1):
            if i in self.node_frames:
                node_frame = self.node_frames[i]
                # Find the delete button and update its text and command
                for child in node_frame.winfo_children():
                    if isinstance(child, tb.Frame):
                        for button in child.winfo_children():
                            if isinstance(button, tb.Button) and button.cget(
                                'text'
                            ).startswith('Delete'):
                                button.configure(text=f'Delete Node {i}')
                                button.configure(command=partial(self.delete_node, i))

    def create_contrast_widgets(self, frame, node_number):
        """
        Create widgets for a new Contrast dynamically from bsmschema Contrast model.

        Args:
            frame: Parent frame
            node_number: Node number
        """
        self.contrast_counter[f'node_{self.number_of_nodes}_num_contrasts'] += 1
        if self.contrast_counter[f'node_{self.number_of_nodes}_num_contrasts'] == 1:
            self.node_output[f'node_{node_number}']['Contrasts'] = []

        current_contrast = {}
        row_holder = tb.Frame(frame)
        row_holder.pack(fill=X, expand=NO, pady=5)

        # Contrast label
        contrast_num = self.contrast_counter[
            f'node_{self.number_of_nodes}_num_contrasts'
        ]
        label = tb.Label(master=row_holder, text=f'Contrast {contrast_num}:', width=15)
        label.pack(side=LEFT, padx=5)

        # Auto-generate widgets from Contrast model
        for field_name, field_info in Contrast.model_fields.items():
            if field_name == 'Description':  # Skip inherited field
                continue

            widget = self._create_contrast_field(row_holder, field_name, field_info)

            # Store widget with compatible key
            req_opt = 'req' if field_info.is_required() else 'opt'

            if field_name == 'Test':
                key = f'{field_name} ({req_opt})'
            elif field_name in ['ConditionList', 'Weights']:
                type_str = (
                    'list of strings'
                    if field_name == 'ConditionList'
                    else 'list of numbers'
                )
                key = f'{field_name} ({req_opt}, {type_str})'
            else:
                key = f'{field_name} ({req_opt}, str)'

            current_contrast[key] = widget

        self.node_output[f'node_{node_number}']['Contrasts'].append(current_contrast)

    def _create_contrast_field(self, parent, field_name: str, field_info):
        """Create a Contrast field widget."""
        import typing
        from typing import get_args, get_origin

        field_frame = tb.Frame(parent)
        field_frame.pack(side=LEFT, expand=NO, pady=5)

        # Check if it's a simple Literal enum (Test field with StatisticalTest)
        origin = get_origin(field_info.annotation)

        # Only create dropdown if origin is EXACTLY typing.Literal
        if origin is typing.Literal:
            # It's a Literal - create dropdown
            try:
                if hasattr(field_info.annotation, '__args__'):
                    values = list(field_info.annotation.__args__)
                else:
                    values = list(get_args(field_info.annotation))

                req_opt = 'req' if field_info.is_required() else 'opt'
                label_text = f'{field_name} ({req_opt})'

                label = tb.Label(master=field_frame, text=label_text, width=18)
                label.grid(row=0, column=0, padx=5)

                combo = tb.Combobox(master=field_frame, values=values, width=16)
                combo.grid(row=1, column=0, padx=5)

                # Add tooltip
                tooltip = self.contrast_docs.get(field_name, '')
                if tooltip:
                    ToolTip(combo, tooltip)

                return combo
            except:
                pass

        # Standard entry field
        req_opt = 'req' if field_info.is_required() else 'opt'

        # Determine type string
        type_str = 'str'
        if 'ConditionList' in field_name:
            type_str = 'list of strings'
        elif 'Weights' in field_name:
            type_str = 'list of numbers'

        label_text = f'{field_name} ({req_opt}, {type_str})'

        label = tb.Label(master=field_frame, text=label_text, width=18)
        label.grid(row=0, column=0, padx=5)

        entry = tb.Entry(master=field_frame, width=16)
        entry.grid(row=1, column=0, padx=5)

        # Add tooltip
        tooltip = self.contrast_docs.get(field_name, '')
        if tooltip:
            ToolTip(entry, tooltip)

        return entry

    def create_dummy_contrast_widgets(self, frame, node_number):
        """
        Create DummyContrasts widgets dynamically from bsmschema DummyContrasts model.

        Args:
            frame: Parent frame
            node_number: Node number
        """
        self.contrast_counter[f'node_{self.number_of_nodes}_num_dummy_contrasts'] += 1
        if (
            self.contrast_counter[f'node_{self.number_of_nodes}_num_dummy_contrasts']
            > 1
        ):
            messagebox.showwarning(
                'Dummy contrast warning', 'You only need 1 dummy contrast entry'
            )
        else:
            self.node_output[f'node_{node_number}']['DummyContrasts'] = {}
            row_holder = tb.Frame(frame)
            row_holder.pack(fill=X, expand=NO, pady=5)

            # Label
            label = tb.Label(master=row_holder, text='Dummy Contrasts:', width=15)
            label.pack(side=LEFT, padx=5)

            # Auto-generate from DummyContrasts model
            for field_name, field_info in DummyContrasts.model_fields.items():
                if field_name == 'Description':  # Skip inherited
                    continue

                widget = self._create_dummy_contrast_field(
                    row_holder, field_name, field_info
                )

                # Store widget
                req_opt = 'req' if field_info.is_required() else 'opt'
                if field_name == 'Test':
                    key = f'{field_name} ({req_opt})'
                else:
                    key = f'{field_name} ({req_opt}, list of strings)'

                self.node_output[f'node_{node_number}']['DummyContrasts'][key] = widget

    def _create_dummy_contrast_field(self, parent, field_name: str, field_info):
        """Create a DummyContrasts field widget."""
        import typing
        from typing import get_args, get_origin

        field_frame = tb.Frame(parent)
        field_frame.pack(side=LEFT, expand=NO, pady=5)

        # Check if it's a simple Literal enum (Test field)
        origin = get_origin(field_info.annotation)

        # Only create dropdown if origin is EXACTLY typing.Literal
        if origin is typing.Literal:
            try:
                if hasattr(field_info.annotation, '__args__'):
                    values = list(field_info.annotation.__args__)
                else:
                    values = list(get_args(field_info.annotation))

                req_opt = 'req' if field_info.is_required() else 'opt'
                label_text = f'{field_name} ({req_opt})'

                label = tb.Label(master=field_frame, text=label_text, width=18)
                label.grid(row=0, column=0, padx=5)

                combo = tb.Combobox(master=field_frame, values=values, width=16)
                combo.grid(row=1, column=0, padx=5)

                # Add tooltip
                tooltip = self.dummy_docs.get(field_name, '')
                if tooltip:
                    ToolTip(combo, tooltip)

                return combo
            except:
                pass

        # Standard entry field
        req_opt = 'req' if field_info.is_required() else 'opt'
        label_text = f'{field_name} ({req_opt}, list of strings)'

        label = tb.Label(master=field_frame, text=label_text, width=18)
        label.grid(row=0, column=0, padx=5)

        entry = tb.Entry(master=field_frame, width=16)
        entry.grid(row=1, column=0, padx=5)

        # Add tooltip
        tooltip = self.dummy_docs.get(field_name, '')
        if tooltip:
            ToolTip(entry, tooltip)

        return entry
