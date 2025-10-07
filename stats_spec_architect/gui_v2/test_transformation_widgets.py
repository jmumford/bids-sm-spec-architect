#!/usr/bin/env python
"""
Test script for the new Pydantic-based transformation widgets.

Run this to test the transformation widget system in isolation:
    python -m stats_spec_architect.gui_v2.test_transformation_widgets
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from stats_spec_architect.gui_v2.transformation_widgets import AddTransformationWidgets


def show_output(transformation_widget):
    """Display the widget output (for testing)."""
    import json
    from tkinter import messagebox

    output = {}

    # Get Transformer version
    if 'Transformer (req)' in transformation_widget.widget_output:
        output['Transformer'] = transformation_widget.widget_output[
            'Transformer (req)'
        ].get()

    # Get all instructions
    instructions = []
    for key, value in transformation_widget.widget_output.items():
        if key.startswith('Instructions_'):
            instruction = {}
            for field_name, widget in value.items():
                if field_name == 'Name':
                    instruction['Name'] = widget
                else:
                    # Get widget value
                    widget_value = widget.get()
                    if widget_value:  # Only include non-empty values
                        instruction[field_name.split(' (')[0]] = widget_value
            if instruction:
                instructions.append(instruction)

    output['Instructions'] = instructions

    # Show in popup
    json_str = json.dumps(output, indent=2)
    print('\n' + '=' * 60)
    print('Transformation Widget Output:')
    print('=' * 60)
    print(json_str)
    print('=' * 60 + '\n')

    messagebox.showinfo(
        'Transformation Output', f'Output:\n\n{json_str}\n\nAlso printed to console.'
    )


def main():
    """Run the test GUI."""
    # Create main window
    window = tb.Window(themename='superhero')
    window.title('Transformation Widgets Test')
    window.geometry('1200x800')

    # Add title
    title = tb.Label(
        window,
        text='🧪 Transformation Widgets Test (Pydantic-based)',
        font=('Helvetica', 20, 'bold'),
        bootstyle='inverse-primary',
    )
    title.pack(pady=20)

    # Add instructions
    instructions = tb.Label(
        window,
        text='1. Click "Add Transformation"\n'
        '2. Select a transformation from dropdown\n'
        '3. Fill in the fields\n'
        '4. Click "Show Output" to see the JSON',
        font=('Helvetica', 12),
        justify=LEFT,
    )
    instructions.pack(pady=10)

    # Create a frame for the transformation widgets
    transform_frame = tb.Frame(window, padding=20)
    transform_frame.pack(fill=BOTH, expand=YES)

    # Create the transformation widget
    transformation_widget = AddTransformationWidgets(transform_frame)

    # Add a button to show output
    button_frame = tb.Frame(window)
    button_frame.pack(pady=20)

    show_button = tb.Button(
        button_frame,
        text='Show Output',
        command=lambda: show_output(transformation_widget),
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
        text='Note: This is testing the new Pydantic-based widget generation.\n'
        'Widgets are auto-generated from transformation_models.py',
        font=('Helvetica', 10),
        bootstyle='secondary',
    )
    info.pack(pady=10)

    window.mainloop()


if __name__ == '__main__':
    main()
