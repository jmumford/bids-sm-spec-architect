"""
Edge Widgets - Pydantic-based edge interface

Dynamically generates edge widgets from bsmschema Edge model.
"""

from functools import partial
from tkinter import messagebox

import ttkbootstrap as tb
from bsmschema.models import Edge
from ttkbootstrap.constants import BOTH, LEFT, NO, SECONDARY, X

from stats_spec_architect.gui_v3.bsmschema_introspector import BSMSchemaIntrospector
from stats_spec_architect.gui_v3.widget_factory import ToolTip


class AddEdge:
    """
    Widget manager for edges using Pydantic Edge model.

    Dynamically generates edge configuration from bsmschema.models.Edge.
    """

    def __init__(self, master_frame, node_widget_manager):
        """
        Initialize edge widget manager.

        Args:
            master_frame: Parent tkinter frame
            node_widget_manager: Reference to node widget manager to get node names
        """
        self.master = master_frame
        self.node_widget_manager = node_widget_manager
        self.number_of_edges = 0

        # Store edge data
        self.edge_output = []

        # Store frame references for deletion
        self.edge_frames = {}
        self.edge_header_labels = {}

        # Get field docstrings from Edge model
        self.edge_docs = BSMSchemaIntrospector.get_field_docstrings(Edge)

        # Create UI
        self._create_ui()

    def _create_ui(self):
        """Create the main edge UI structure."""
        # Add Edge button
        add_button_frame = tb.Frame(self.master)
        add_button_frame.pack(fill=X, expand=NO, pady=5)

        add_button = tb.Button(
            add_button_frame, text='Add Edge', command=self.make_edge_subframe
        )
        add_button.pack(side=LEFT, padx=5, fill=X, expand=NO)

        # Import CollapsingFrame
        from stats_spec_architect.gui_v3.utils import CollapsingFrame

        self.edge_specific_cf = CollapsingFrame(self.master, padding=10)
        self.edge_specific_cf.pack(fill=BOTH)

    def make_edge_subframe(self):
        """Create a new edge in a collapsing frame."""
        self.number_of_edges += 1

        # Make a collapsible frame for this edge
        frame_win_edge_specific_cf = tb.Frame(self.edge_specific_cf, padding=10)

        # Store frame reference for potential deletion
        self.edge_frames[self.number_of_edges] = frame_win_edge_specific_cf

        # Create edge widgets
        self.create_edge_widgets(self.number_of_edges, frame_win_edge_specific_cf)

        # Add to collapsing frame
        self.edge_specific_cf.add(
            child=frame_win_edge_specific_cf,
            title=f'Edge {self.number_of_edges}',
            bootstyle=SECONDARY,
        )

        # Store reference to the header label for later updates
        grid_info = frame_win_edge_specific_cf.grid_info()
        if grid_info:
            child_row = grid_info['row']
            header_row = child_row - 1
            # Find the header label in the header frame
            for widget in self.edge_specific_cf.grid_slaves(row=header_row):
                for child in widget.winfo_children():
                    if isinstance(child, tb.Label):
                        self.edge_header_labels[self.number_of_edges] = child
                        break

        # Auto-scroll to make the new edge visible
        self._scroll_to_edge(frame_win_edge_specific_cf)

    def _scroll_to_edge(self, frame):
        """Scroll to make an edge frame visible."""

        # Schedule scroll after layout is complete
        def do_scroll():
            # Walk up to find the canvas from the Edges section
            widget = self.edge_specific_cf
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
                # Scroll to bottom to show the newly added edge
                canvas.yview_moveto(1.0)

        # Delay scroll to ensure layout is complete
        frame.after(100, do_scroll)

    def create_edge_widgets(self, edge_number, frame):
        """
        Create widgets for an edge dynamically from bsmschema Edge model.

        Args:
            edge_number: Number of this edge (for labeling)
            frame: Parent frame to add widgets to
        """
        # Add delete button at top
        self._create_delete_button(frame, edge_number)

        # Create dict to store this edge's widgets
        edge_data = {}

        # Get node names for dropdowns
        node_names = self._get_node_names()

        # Dynamically create widgets from Edge model fields
        for field_name, field_info in Edge.model_fields.items():
            if field_name == 'Description':  # Skip inherited Description field
                continue

            # Create appropriate widget based on field
            if field_name in ['Source', 'Destination']:
                widget = self._create_node_dropdown(
                    frame, field_name, node_names, field_info
                )
            elif field_name == 'Filter':
                widget = self._create_filter_entry(frame, field_name, field_info)
            else:
                # Fallback for any other fields
                widget = self._create_text_entry(frame, field_name, field_info)

            # Store widget with simple field name as key
            edge_data[field_name] = widget

        # Store edge data
        self.edge_output.append(edge_data)

    def _get_node_names(self):
        """Get list of node names from node widget manager."""
        node_names = []
        if hasattr(self.node_widget_manager, 'node_output'):
            for node_key in self.node_widget_manager.node_output.keys():
                # Extract node name from the stored data
                node_data = self.node_widget_manager.node_output[node_key]
                # Use new simple key format
                if 'Name' in node_data:
                    name_widget = node_data['Name']
                    name = name_widget.get() if hasattr(name_widget, 'get') else ''
                    if name:
                        node_names.append(name)
        return node_names

    def _create_node_dropdown(self, parent, field_name, node_names, field_info):
        """Create a dropdown for Source or Destination."""
        widget_pair_frame = tb.Frame(parent)
        widget_pair_frame.pack(fill=X, expand=NO, pady=5)

        # Label (dynamically determined)
        req_opt = 'req' if field_info.is_required() else 'opt'
        type_str = self._get_type_string(field_info)
        label_text = f'{field_name} ({req_opt}, {type_str})'
        label = tb.Label(master=widget_pair_frame, text=label_text, width=25)
        label.pack(side=LEFT, padx=5)

        # Dropdown
        combo = tb.Combobox(master=widget_pair_frame, values=node_names, width=24)
        combo.pack(side=LEFT, padx=5)

        # Add tooltip with description from Edge model
        tooltip = self.edge_docs.get(field_name, '')
        if tooltip:
            ToolTip(combo, tooltip)

        return combo

    def _create_filter_entry(self, parent, field_name, field_info):
        """Create a text entry for Filter field (JSON dict input)."""
        widget_pair_frame = tb.Frame(parent)
        widget_pair_frame.pack(fill=X, expand=NO, pady=5)

        # Label (dynamically determined)
        req_opt = 'req' if field_info.is_required() else 'opt'
        type_str = self._get_type_string(field_info)
        label_text = f'{field_name} ({req_opt}, {type_str})'
        label = tb.Label(master=widget_pair_frame, text=label_text, width=25)
        label.pack(side=LEFT, padx=5)

        # Entry
        entry = tb.Entry(master=widget_pair_frame, width=24)
        entry.pack(side=LEFT, padx=5)

        # Add tooltip with description and hint
        tooltip = self.edge_docs.get(field_name, '')
        if tooltip:
            tooltip += '\n\nFormat: {"entity": ["value1", "value2"]}'
        else:
            tooltip = 'Format: {"entity": ["value1", "value2"]}'
        ToolTip(entry, tooltip)

        return entry

    def _create_text_entry(self, parent, field_name, field_info):
        """Create a generic text entry field."""
        widget_pair_frame = tb.Frame(parent)
        widget_pair_frame.pack(fill=X, expand=NO, pady=5)

        # Label (dynamically determined)
        req_opt = 'req' if field_info.is_required() else 'opt'
        type_str = self._get_type_string(field_info)
        label_text = f'{field_name} ({req_opt}, {type_str})'
        label = tb.Label(master=widget_pair_frame, text=label_text, width=25)
        label.pack(side=LEFT, padx=5)

        # Entry
        entry = tb.Entry(master=widget_pair_frame, width=24)
        entry.pack(side=LEFT, padx=5)

        # Add tooltip with description
        tooltip = self.edge_docs.get(field_name, '')
        if tooltip:
            ToolTip(entry, tooltip)

        return entry

    def _get_type_string(self, field_info):
        """
        Extract a human-readable type string from field_info.

        Args:
            field_info: Pydantic FieldInfo object

        Returns:
            String representation of type (e.g., 'str', 'dict', 'list')
        """
        annotation = field_info.annotation

        # Handle Optional types
        from typing import get_args, get_origin

        origin = get_origin(annotation)
        if origin is type(None) or (
            hasattr(annotation, '__args__') and type(None) in get_args(annotation)
        ):
            # It's Optional - unwrap it
            args = get_args(annotation)
            if args:
                annotation = args[0] if args[0] is not type(None) else args[1]
                origin = get_origin(annotation)

        # Check if it's dict
        if origin is dict or annotation.__name__ == 'Filter':
            return 'dict'

        # Check if it's list
        if origin is list:
            return 'list'

        # Check for string types
        if 'str' in str(annotation).lower() or annotation.__name__ in [
            'str',
            'StrictStr',
        ]:
            return 'str'

        # Default
        return 'str'

    def _create_delete_button(self, frame, edge_number):
        """Create delete button for this edge."""
        delete_frame = tb.Frame(frame, padding=10)
        delete_frame.pack(fill=X, expand=NO, pady=10)

        delete_button = tb.Button(
            delete_frame,
            text=f'Delete Edge {edge_number}',
            command=partial(self.delete_edge, edge_number),
            bootstyle='warning',
        )
        delete_button.pack(side='right', padx=5)

    def delete_edge(self, edge_number):
        """
        Delete an edge and renumber all subsequent edges.

        Args:
            edge_number: Number of the edge to delete (1-based)
        """
        # Confirm deletion
        result = messagebox.askyesno(
            'Delete Edge',
            f'Are you sure you want to delete Edge {edge_number}?\n\n'
            'All data in this edge will be lost.\n'
            'All edges after this will be renumbered.',
        )

        if not result:
            return

        # Remove edge data (convert to 0-based index)
        edge_index = edge_number - 1
        if 0 <= edge_index < len(self.edge_output):
            del self.edge_output[edge_index]

        # Remove UI frames (both header and content) for deleted edge
        if edge_number in self.edge_frames:
            child_frame = self.edge_frames[edge_number]

            # Get the row of the child frame
            grid_info = child_frame.grid_info()
            if grid_info:
                child_row = grid_info['row']
                header_row = child_row - 1

                # Find and destroy the header frame
                for widget in self.edge_specific_cf.grid_slaves(row=header_row):
                    widget.destroy()

                # Destroy the child frame
                child_frame.destroy()

        # Rebuild edge_frames dict with renumbered keys
        new_edge_frames = {}
        new_edge_header_labels = {}
        edge_counter = 1
        for i in range(1, self.number_of_edges + 1):
            if i == edge_number:
                continue
            if i in self.edge_frames:
                new_edge_frames[edge_counter] = self.edge_frames[i]
                if i in self.edge_header_labels:
                    new_edge_header_labels[edge_counter] = self.edge_header_labels[i]
                edge_counter += 1

        self.edge_frames = new_edge_frames
        self.edge_header_labels = new_edge_header_labels

        # Update edge titles using stored label references
        self._update_edge_titles()

        # Update delete button labels and commands
        self._update_delete_button_labels()

        # Decrement counter
        self.number_of_edges -= 1

    def _update_edge_titles(self):
        """Update all edge titles in the CollapsingFrame after renumbering."""
        # Use stored label references to update titles
        for new_num in range(1, len(self.edge_header_labels) + 1):
            if new_num in self.edge_header_labels:
                label = self.edge_header_labels[new_num]
                label.configure(text=f'Edge {new_num}')
                print(f'Updated edge title to: Edge {new_num}')

    def _update_delete_button_labels(self):
        """Update all delete button labels after renumbering."""
        for i in range(1, len(self.edge_frames) + 1):
            if i in self.edge_frames:
                edge_frame = self.edge_frames[i]
                # Find the delete button and update its text and command
                for child in edge_frame.winfo_children():
                    if isinstance(child, tb.Frame):
                        for button in child.winfo_children():
                            if isinstance(button, tb.Button) and button.cget(
                                'text'
                            ).startswith('Delete'):
                                button.configure(text=f'Delete Edge {i}')
                                button.configure(command=partial(self.delete_edge, i))
