"""
JSON Import for GUI v2

Loads BIDS Stats Model JSON and populates GUI widgets.
"""

import json
from tkinter import filedialog, messagebox

import ttkbootstrap as tb


def load_json_to_gui(input_widgets, node_widgets, edge_widgets):
    """
    Load a JSON file and populate the GUI.

    Args:
        input_widgets: CreateInputWidgets instance
        node_widgets: AddNode instance
        edge_widgets: AddEdge instance

    Returns:
        bool: True if successful, False otherwise
    """
    # Open file dialog
    filepath = filedialog.askopenfilename(
        title='Select BIDS Stats Model JSON',
        filetypes=[('JSON files', '*.json'), ('All files', '*.*')],
    )

    if not filepath:
        return False  # User cancelled

    try:
        # Load JSON
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Validate first
        from stats_spec_architect.validation.enhanced_validator import (
            EnhancedBIDSValidator,
        )

        validator = EnhancedBIDSValidator()
        result = validator.validate_data(data)

        if not result.valid:
            # Show validation errors
            error_msg = (
                f'⚠️  JSON file has {len(result.errors)} validation error(s).\n\n'
                'Do you still want to load it?\n\n'
                'First 5 errors:\n'
            )
            for i, error in enumerate(result.errors[:5], 1):
                error_msg += f'{i}. {error}\n'

            response = messagebox.askyesno('Validation Errors', error_msg)
            if not response:
                return False

        # Clear existing GUI data
        if not _confirm_clear_gui():
            return False

        _clear_gui(input_widgets, node_widgets, edge_widgets)

        # Populate GUI
        _populate_input_widgets(data, input_widgets)
        _populate_node_widgets(data, node_widgets)
        _populate_edge_widgets(data, edge_widgets, node_widgets)

        # Success - no additional popup (confirmation was enough)
        return True

    except json.JSONDecodeError as e:
        messagebox.showerror('Invalid JSON', f'Could not parse JSON file:\n\n{str(e)}')
        return False
    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        messagebox.showerror(
            'Load Error',
            f'Error loading JSON:\n\n{str(e)}\n\nDetails:\n{error_details[:500]}',
        )
        return False


def _confirm_clear_gui():
    """Ask user to confirm clearing existing GUI data."""
    response = messagebox.askyesno(
        'Clear Existing Data?',
        'Loading a JSON file will clear all current GUI data.\n\n'
        'Do you want to continue?',
    )
    return response


def _clear_gui(input_widgets, node_widgets, edge_widgets):
    """Clear all GUI data."""
    # Clear input widgets
    if hasattr(input_widgets, 'widget_output'):
        for key, widget in input_widgets.widget_output.items():
            if key == 'Input':
                # Clear nested Input dict
                for sub_key, sub_widget in widget.items():
                    if hasattr(sub_widget, 'delete'):
                        sub_widget.delete(0, 'end')
            else:
                # Clear checkboxes
                if hasattr(widget, 'is_selected'):
                    for checkvalue in widget.is_selected.values():
                        checkvalue.set(0)
                # Clear entry/combobox
                elif hasattr(widget, 'delete'):
                    widget.delete(0, 'end')
                elif hasattr(widget, 'set'):
                    widget.set('')

    # Clear nodes (destroy frames without confirmation dialogs)
    for node_number in list(node_widgets.node_frames.keys()):
        if node_number in node_widgets.node_frames:
            child_frame = node_widgets.node_frames[node_number]
            grid_info = child_frame.grid_info()
            if grid_info:
                # Destroy header and child
                child_row = grid_info['row']
                header_row = child_row - 1
                for widget in node_widgets.node_specific_cf.grid_slaves(row=header_row):
                    widget.destroy()
                child_frame.destroy()

    # Reset node data
    node_widgets.node_output.clear()
    node_widgets.node_frames.clear()
    node_widgets.node_header_labels.clear()
    node_widgets.contrast_frames.clear()
    node_widgets.dummy_contrast_frames.clear()
    node_widgets.contrast_counter.clear()
    node_widgets.number_of_nodes = 0

    # Clear edges (destroy frames without confirmation dialogs)
    for edge_number in list(edge_widgets.edge_frames.keys()):
        if edge_number in edge_widgets.edge_frames:
            child_frame = edge_widgets.edge_frames[edge_number]
            grid_info = child_frame.grid_info()
            if grid_info:
                # Destroy header and child
                child_row = grid_info['row']
                header_row = child_row - 1
                for widget in edge_widgets.edge_specific_cf.grid_slaves(row=header_row):
                    widget.destroy()
                child_frame.destroy()

    # Reset edge data
    edge_widgets.edge_output.clear()
    edge_widgets.edge_frames.clear()
    edge_widgets.edge_header_labels.clear()
    edge_widgets.number_of_edges = 0


def _populate_input_widgets(data, input_widgets):
    """Populate top-level input widgets from JSON data."""
    # Populate Name
    if 'Name' in data:
        _set_widget_value(
            input_widgets.widget_output.get('Name (req, str)'), data['Name']
        )

    # Populate BIDSModelVersion
    if 'BIDSModelVersion' in data:
        _set_widget_value(
            input_widgets.widget_output.get('BIDSModelVersion (req, str)'),
            data['BIDSModelVersion'],
        )

    # Populate Description
    if 'Description' in data:
        _set_widget_value(
            input_widgets.widget_output.get('Description (opt, str)'),
            data['Description'],
        )

    # Populate Input fields
    if 'Input' in data and isinstance(data['Input'], dict):
        input_dict = input_widgets.widget_output.get('Input', {})
        for field in ['subject', 'run', 'task', 'session']:
            if field in data['Input']:
                key = f'{field} (opt, list of strings)'
                widget = input_dict.get(key)
                if widget:
                    # Convert list to comma-separated string
                    value = data['Input'][field]
                    if isinstance(value, list):
                        value = ', '.join(str(v) for v in value)
                    _set_widget_value(widget, value)


def _populate_node_widgets(data, node_widgets):
    """Populate node widgets from JSON data."""
    if 'Nodes' not in data or not isinstance(data['Nodes'], list):
        return

    for node_data in data['Nodes']:
        # Add a new node
        node_widgets.make_node_subframe()
        node_number = node_widgets.number_of_nodes

        # Populate node fields
        _populate_single_node(node_data, node_widgets, node_number)


def _populate_single_node(node_data, node_widgets, node_number):
    """Populate a single node's widgets."""
    node_key = f'node_{node_number}'
    node_output = node_widgets.node_output.get(node_key, {})

    # Populate Level
    if 'Level' in node_data:
        _set_widget_value(node_output.get('Level (req)'), node_data['Level'])

    # Populate Name
    if 'Name' in node_data:
        _set_widget_value(node_output.get('Name (req, str)'), node_data['Name'])

    # Populate GroupBy (checkboxes)
    if 'GroupBy' in node_data and isinstance(node_data['GroupBy'], list):
        groupby_widget = node_output.get('GroupBy (req, str)')
        if groupby_widget and hasattr(groupby_widget, 'is_selected'):
            for value in node_data['GroupBy']:
                if value in groupby_widget.is_selected:
                    groupby_widget.is_selected[value].set(1)

    # Populate Model
    if 'Model' in node_data:
        _populate_model(node_data['Model'], node_output.get('Model', {}))

    # Populate Transformations
    if 'Transformations' in node_data:
        _populate_transformations(
            node_data['Transformations'], node_output.get('transformations')
        )

    # Populate Contrasts
    if 'Contrasts' in node_data and isinstance(node_data['Contrasts'], list):
        for contrast_data in node_data['Contrasts']:
            _add_and_populate_contrast(contrast_data, node_widgets, node_number)

    # Populate DummyContrasts
    if 'DummyContrasts' in node_data:
        _add_and_populate_dummy_contrast(
            node_data['DummyContrasts'], node_widgets, node_number
        )


def _populate_model(model_data, model_widgets):
    """Populate Model widgets."""
    if not isinstance(model_widgets, dict):
        return

    # Map JSON keys to widget keys (based on node_widgets.py key format)
    field_mapping = {
        'Type': 'Type',  # Special case - no (req) suffix
        'X': 'X (req, list of strings)',
        'Formula': 'Formula (opt, str)',
        'Software': 'Software (opt, dict)',
    }

    for json_key, widget_key in field_mapping.items():
        if json_key in model_data:
            widget = model_widgets.get(widget_key)
            if widget:
                value = model_data[json_key]
                # Convert lists to comma-separated strings
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                elif isinstance(value, dict):
                    value = json.dumps(value)
                _set_widget_value(widget, value)


def _populate_transformations(trans_data, trans_widget):
    """Populate transformation widgets."""
    if not trans_widget or not isinstance(trans_data, dict):
        return

    # Set Transformer
    if 'Transformer' in trans_data:
        transformer_widget = trans_widget.widget_output.get('Transformer (req)')
        if transformer_widget:
            _set_widget_value(transformer_widget, trans_data['Transformer'])

    # Add and populate Instructions
    if 'Instructions' in trans_data and isinstance(trans_data['Instructions'], list):
        for instruction_data in trans_data['Instructions']:
            _add_and_populate_transformation(instruction_data, trans_widget)


def _add_and_populate_transformation(instruction_data, trans_widget):
    """Add a transformation tab and populate it."""
    # Add transformation tab
    trans_widget.add_transformation_tab()

    # Get the tab index (just added, so it's number - 1)
    tab_index = trans_widget.number - 1

    # Get transformation name
    transform_name = instruction_data.get('Name')
    if not transform_name:
        return

    # Get the widgets for this instruction
    instruction_widgets = trans_widget.widget_output.get(
        f'Instructions_{tab_index}', {}
    )

    # Set the transformation type dropdown
    # We need to find the combobox in the tab and set it
    # Then trigger the selection to create the fields
    notebook = trans_widget.transformations_notebook
    tab_frame = notebook.nametowidget(notebook.tabs()[tab_index])

    # Find the transformation selector combobox
    for child in tab_frame.winfo_children():
        if isinstance(child, tb.Frame):
            for widget in child.winfo_children():
                if isinstance(widget, tb.Combobox):
                    # Set the value
                    widget.set(transform_name)
                    # Trigger the event to create fields
                    widget.event_generate('<<ComboboxSelected>>')

                    # Wait for fields to be created
                    tab_frame.update_idletasks()

                    # Now populate the fields
                    tab_frame.after(
                        50,
                        lambda: _populate_transformation_fields(
                            instruction_data, trans_widget, tab_index
                        ),
                    )
                    return


def _populate_transformation_fields(instruction_data, trans_widget, tab_index):
    """Populate transformation field widgets after they're created."""
    instruction_widgets = trans_widget.widget_output.get(
        f'Instructions_{tab_index}', {}
    )

    for field_name, value in instruction_data.items():
        if field_name == 'Name':
            continue  # Already set

        # Find the widget
        widget = instruction_widgets.get(field_name)
        if widget:
            # Convert lists/dicts to appropriate format
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value)
            elif isinstance(value, dict):
                value = json.dumps(value)
            _set_widget_value(widget, value)


def _add_and_populate_contrast(contrast_data, node_widgets, node_number):
    """Add a contrast and populate it."""
    # Get the contrast frame for this node
    contrast_frame = node_widgets.contrast_frames.get(node_number)
    if not contrast_frame:
        return

    # Create the contrast widgets
    node_widgets.create_contrast_widgets(contrast_frame, node_number)

    # Get the most recently added contrast (last one in the list)
    node_key = f'node_{node_number}'
    contrasts = node_widgets.node_output.get(node_key, {}).get('Contrasts', [])
    if not contrasts:
        return

    contrast_widgets = contrasts[-1]

    # Populate the contrast fields
    field_mapping = {
        'Name': 'Name (req, str)',
        'ConditionList': 'ConditionList (req, list of strings)',
        'Weights': 'Weights (req, list of numbers)',
        'Test': 'Test (req)',
    }

    for json_key, widget_key in field_mapping.items():
        if json_key in contrast_data:
            widget = contrast_widgets.get(widget_key)
            if widget:
                value = contrast_data[json_key]
                # Convert lists to comma-separated strings
                if isinstance(value, list):
                    # Handle nested lists (2D arrays for F-tests)
                    if value and isinstance(value[0], list):
                        # 2D array - format as JSON
                        value = json.dumps(value)
                    else:
                        # 1D array
                        value = ', '.join(str(v) for v in value)
                _set_widget_value(widget, value)


def _add_and_populate_dummy_contrast(dummy_data, node_widgets, node_number):
    """Add dummy contrast and populate it."""
    # Get the dummy contrast frame for this node
    dummy_frame = node_widgets.dummy_contrast_frames.get(node_number)
    if not dummy_frame:
        return

    # Create the dummy contrast widgets
    node_widgets.create_dummy_contrast_widgets(dummy_frame, node_number)

    # Get the dummy contrast widgets
    node_key = f'node_{node_number}'
    dummy_widgets = node_widgets.node_output.get(node_key, {}).get('DummyContrasts', {})
    if not dummy_widgets:
        return

    # Populate the fields
    field_mapping = {
        'Contrasts': 'Contrasts (opt, list of strings)',
        'Test': 'Test (req)',
    }

    for json_key, widget_key in field_mapping.items():
        if json_key in dummy_data:
            widget = dummy_widgets.get(widget_key)
            if widget:
                value = dummy_data[json_key]
                # Convert lists to comma-separated strings
                if isinstance(value, list):
                    value = ', '.join(str(v) for v in value)
                _set_widget_value(widget, value)


def _populate_edge_widgets(data, edge_widgets, node_widgets):
    """Populate edge widgets from JSON data."""
    if 'Edges' not in data or not isinstance(data['Edges'], list):
        return

    for edge_data in data['Edges']:
        # Add a new edge
        edge_widgets.make_edge_subframe()
        edge_number = edge_widgets.number_of_edges

        # Populate edge fields
        edge_output = edge_widgets.edge_output[-1]  # Just added

        # Populate Source
        if 'Source' in edge_data:
            _set_widget_value(edge_output.get('Source (req, str)'), edge_data['Source'])

        # Populate Destination
        if 'Destination' in edge_data:
            _set_widget_value(
                edge_output.get('Destination (req, str)'), edge_data['Destination']
            )

        # Populate Filter
        if 'Filter' in edge_data:
            filter_value = edge_data['Filter']
            if isinstance(filter_value, dict):
                filter_value = json.dumps(filter_value)
            _set_widget_value(edge_output.get('Filter (opt, dict)'), filter_value)


def _set_widget_value(widget, value):
    """Set a widget's value (works for Entry and Combobox)."""
    if widget is None:
        return

    if hasattr(widget, 'delete') and hasattr(widget, 'insert'):
        # Entry widget
        widget.delete(0, 'end')
        widget.insert(0, str(value))

        # Update button text if this entry has an associated edit button (like Model.X)
        if hasattr(widget, '_edit_button'):
            button = widget._edit_button
            if value:
                preview = (
                    str(value)[:40] + '...' if len(str(value)) > 40 else str(value)
                )
                button.configure(text=preview)
            else:
                button.configure(text='Click to edit variables...')
    elif hasattr(widget, 'set'):
        # Combobox widget
        widget.set(str(value))
