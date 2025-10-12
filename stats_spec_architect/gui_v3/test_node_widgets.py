#!/usr/bin/env python
"""
Test script for Node widgets.

Run this to test the node widget system in isolation:
    python -m stats_spec_architect.gui_v3.test_node_widgets
"""

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from stats_spec_architect.gui_v3.node_widgets import AddNode


def main():
    """Run the test GUI."""
    # Create main window
    window = tb.Window(themename='superhero')
    window.title('Node Widgets Test')
    window.geometry('1400x900')

    # Add title
    title = tb.Label(
        window,
        text='🧪 Node Widgets Test (Pydantic-based)',
        font=('Helvetica', 20, 'bold'),
        bootstyle='inverse-primary',
    )
    title.pack(pady=20)

    # Add instructions
    instructions = tb.Label(
        window,
        text='1. Click "Add Node"\n'
        '2. Fill in node fields (Level, Name, GroupBy)\n'
        '3. Add transformations (optional)\n'
        '4. Fill in Model section\n'
        '5. Add Contrasts (optional)\n'
        '6. Hover over fields to see descriptions from BIDS spec',
        font=('Helvetica', 12),
        justify=LEFT,
    )
    instructions.pack(pady=10)

    # Create a scrollable frame for nodes
    from stats_spec_architect.gui_v3.scrolled_frame import VerticalScrolledFrame

    scrolling_window = VerticalScrolledFrame(window)
    scrolling_window.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    # Create the node widgets
    node_widget = AddNode(scrolling_window)

    # Add quit button
    button_frame = tb.Frame(window)
    button_frame.pack(pady=20)

    quit_button = tb.Button(
        button_frame, text='Quit', command=window.quit, bootstyle='danger', width=20
    )
    quit_button.pack(side=LEFT, padx=10)

    # Info label
    info = tb.Label(
        window,
        text='Note: This tests node widgets with dynamic Pydantic generation.\n'
        'All fields, dropdowns, and tooltips come from bsmschema models.',
        font=('Helvetica', 10),
        bootstyle='secondary',
    )
    info.pack(pady=10)

    window.mainloop()


if __name__ == '__main__':
    main()
