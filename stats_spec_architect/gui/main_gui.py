"""
Main GUI Window - Pydantic-based BIDS Stats Model Architect

Integrates all components (Input, Nodes, Edges) into a single GUI using
dynamic Pydantic-based widget generation.
"""

from functools import partial

import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, YES

from stats_spec_architect.gui.edge_widgets import AddEdge
from stats_spec_architect.gui.input_widgets import CreateInputWidgets
from stats_spec_architect.gui.node_widgets import AddNode
from stats_spec_architect.gui.scrolled_frame import VerticalScrolledFrame
from stats_spec_architect.gui.utils import CollapsingFrame


def launch_main_gui(layout=None):
    """
    Launch the main GUI (Pydantic-based, dynamic widget generation).

    Args:
        layout: Optional BIDSLayout object (for future integration)
    """
    if layout:
        print(f'Layout loaded: {layout.get_subjects()}')

    # Create main window with superhero theme
    main_window = tb.Window(themename='superhero')
    main_window.title('BIDS Stats Model Architect')
    main_window.geometry('1400x950')
    main_window.minsize(1400, 600)  # Prevent width from collapsing
    main_window.protocol('WM_DELETE_WINDOW', main_window.quit)

    # Create vertical-only scrolled frame (no horizontal scrolling)
    scrolling_window = VerticalScrolledFrame(main_window)
    scrolling_window.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    # Set up collapsing frame container
    cf = CollapsingFrame(scrolling_window)
    cf.pack(fill=BOTH)

    # Set font style
    s = tb.Style()
    s.configure('.', font=('Helvetica', 18))

    # ========== Top Level Data Section ==========
    top_level_frame = tb.Frame(cf, padding=10)
    input_widgets = CreateInputWidgets(top_level_frame)
    cf.add(child=top_level_frame, title='Input (Name, Version, Description)')

    # ========== Nodes Section ==========
    nodes_frame = tb.Frame(cf, padding=10)
    node_widgets = AddNode(nodes_frame)
    cf.add(child=nodes_frame, title='Nodes')

    # ========== Edges Section ==========
    edges_frame = tb.Frame(cf, padding=10)
    edge_widgets = AddEdge(edges_frame, node_widgets)
    cf.add(child=edges_frame, title='Edges')

    # ========== Action Buttons ==========
    button_frame = tb.Frame(main_window, padding=10)
    button_frame.pack(fill='x', padx=10, pady=10)

    # Show JSON button
    show_json_button = tb.Button(
        button_frame,
        text='Show Model Spec (JSON)',
        command=partial(_show_json, input_widgets, node_widgets, edge_widgets),
        bootstyle='primary',
    )
    show_json_button.pack(side='left', padx=5)

    # Save JSON button
    save_json_button = tb.Button(
        button_frame,
        text='Save to File',
        command=partial(_save_json, input_widgets, node_widgets, edge_widgets),
        bootstyle='primary',
    )
    save_json_button.pack(side='left', padx=5)

    # Load JSON button
    load_json_button = tb.Button(
        button_frame,
        text='Load from File',
        command=partial(_load_json, input_widgets, node_widgets, edge_widgets),
        bootstyle='primary',
    )
    load_json_button.pack(side='left', padx=5)

    # Validate button
    validate_button = tb.Button(
        button_frame,
        text='Validate',
        command=partial(_validate_model, input_widgets, node_widgets, edge_widgets),
        bootstyle='primary',
    )
    validate_button.pack(side='left', padx=5)

    main_window.mainloop()


def _show_json(input_widgets, node_widgets, edge_widgets):
    """Display the generated JSON in a popup window."""
    from stats_spec_architect.gui.json_export import (
        export_to_json,
        show_json_in_window,
    )

    # Export and validate
    json_string, validation_result = export_to_json(
        input_widgets, node_widgets, edge_widgets, validate=True
    )

    if json_string:
        # Valid! Show the JSON
        show_json_in_window(json_string)


def _save_json(input_widgets, node_widgets, edge_widgets):
    """Save the JSON to a file."""
    from tkinter import filedialog, messagebox

    from stats_spec_architect.gui.json_export import export_to_json

    # Export and validate
    json_string, validation_result = export_to_json(
        input_widgets, node_widgets, edge_widgets, validate=True
    )

    if json_string:
        # Valid! Ask where to save
        # Get default filename from Name field if available
        default_name = 'model_spec.json'
        if (
            hasattr(input_widgets, 'widget_output')
            and 'Name (req, str)' in input_widgets.widget_output
        ):
            name_widget = input_widgets.widget_output['Name (req, str)']
            if hasattr(name_widget, 'get'):
                name = name_widget.get()
                if name:
                    default_name = f'{name}.json'

        # File dialog
        filepath = filedialog.asksaveasfilename(
            defaultextension='.json',
            filetypes=[('JSON files', '*.json'), ('All files', '*.*')],
            initialfile=default_name,
        )

        if filepath:
            try:
                with open(filepath, 'w') as f:
                    f.write(json_string)
                messagebox.showinfo('Success', f'Model saved to:\n{filepath}')
            except Exception as e:
                messagebox.showerror('Save Error', f'Error saving file:\n\n{str(e)}')


def _load_json(input_widgets, node_widgets, edge_widgets):
    """Load JSON from a file into the GUI."""
    from stats_spec_architect.gui.json_import import load_json_to_gui

    load_json_to_gui(input_widgets, node_widgets, edge_widgets)


def _validate_model(input_widgets, node_widgets, edge_widgets):
    """Validate the current model using enhanced_validator."""
    from tkinter import messagebox

    from stats_spec_architect.gui.json_export import export_to_json

    # Export and validate
    json_string, validation_result = export_to_json(
        input_widgets, node_widgets, edge_widgets, validate=True
    )

    if json_string:
        # Valid!
        messagebox.showinfo(
            'Validation Success',
            '✅ Model is valid!\n\nNo errors found.',
        )
    # If invalid, errors are already shown by export_to_json


# Standalone test function
def main():
    """Launch the GUI for testing (without BIDSLayout)."""
    # Launch main GUI directly (tb.Window is a root window)
    launch_main_gui(layout=None)


if __name__ == '__main__':
    main()
