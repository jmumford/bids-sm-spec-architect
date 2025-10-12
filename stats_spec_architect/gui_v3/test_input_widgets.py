#!/usr/bin/env python
"""
Test script for the Input widgets.

Run this to test the input widget system in isolation:
    python -m stats_spec_architect.gui_v3.test_input_widgets
"""

import json
from tkinter import messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from stats_spec_architect.gui_v3.input_widgets import CreateInputWidgets


def show_output(input_widget):
    """Display the widget output (for testing)."""
    output = {}

    # Get top-level fields
    for label, widget in input_widget.widget_output.items():
        if label == 'Input':
            # Handle Input section separately
            continue

        value = widget.get()
        if value:  # Only include non-empty values
            field_name = label.split(' (')[0]
            output[field_name] = value

    # Get Input section
    if 'Input' in input_widget.widget_output:
        input_dict = {}
        for label, widget in input_widget.widget_output['Input'].items():
            value = widget.get()
            if value:  # Only include non-empty values
                field_name = label.split(' (')[0]
                # Parse as list (comma-separated)
                if ',' in value:
                    input_dict[field_name] = [v.strip() for v in value.split(',')]
                else:
                    input_dict[field_name] = [value.strip()]

        if input_dict:
            output['Input'] = input_dict

    # Show in popup
    json_str = json.dumps(output, indent=2)
    print('\n' + '=' * 60)
    print('Input Widget Output:')
    print('=' * 60)
    print(json_str)
    print('=' * 60 + '\n')

    messagebox.showinfo(
        'Input Widget Output', f'Output:\n\n{json_str}\n\nAlso printed to console.'
    )


def main():
    """Run the test GUI."""
    # Create main window
    window = tb.Window(themename='superhero')
    window.title('Input Widgets Test')
    window.geometry('800x400')

    # Add title
    title = tb.Label(
        window,
        text='🧪 Input Widgets Test (Pydantic-based)',
        font=('Helvetica', 20, 'bold'),
        bootstyle='inverse-primary',
    )
    title.pack(pady=20)

    # Add instructions
    instructions = tb.Label(
        window,
        text='1. Fill in the fields\n'
        '2. Hover over fields to see descriptions\n'
        '3. Click "Show Output" to see the JSON\n'
        '4. For lists, use comma-separated values (e.g., "faces, houses")',
        font=('Helvetica', 12),
        justify=LEFT,
    )
    instructions.pack(pady=10)

    # Create a frame for the input widgets
    input_frame = tb.Frame(window, padding=20)
    input_frame.pack(fill=BOTH, expand=YES)

    # Create the input widgets
    input_widget = CreateInputWidgets(input_frame)

    # Add buttons
    button_frame = tb.Frame(window)
    button_frame.pack(pady=20)

    show_button = tb.Button(
        button_frame,
        text='Show Output',
        command=lambda: show_output(input_widget),
        bootstyle='success',
        width=20,
    )
    show_button.pack(side=LEFT, padx=10)

    quit_button = tb.Button(
        button_frame, text='Quit', command=window.quit, bootstyle='danger', width=20
    )
    quit_button.pack(side=LEFT, padx=10)

    # Info label
    info = tb.Label(
        window,
        text='Note: This tests the top-level BIDS Stats Model fields.\n'
        'Tooltips show descriptions from the BIDS specification.',
        font=('Helvetica', 10),
        bootstyle='secondary',
    )
    info.pack(pady=10)

    window.mainloop()


if __name__ == '__main__':
    main()
