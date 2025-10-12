"""Test script for Edge widgets."""

import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, YES

from stats_spec_architect.gui_v3.edge_widgets import AddEdge
from stats_spec_architect.gui_v3.node_widgets import AddNode


def main():
    """Launch test window for edge widgets."""
    # Create main window
    root = tb.Window(themename='darkly')
    root.title('Edge Widgets Test (gui_v3)')
    root.geometry('1400x900')

    # Create a canvas with scrollbar
    canvas = tb.Canvas(root)
    scrollbar = tb.Scrollbar(root, orient='vertical', command=canvas.yview)
    scrollable_frame = tb.Frame(canvas)

    scrollable_frame.bind(
        '<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all'))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side='left', fill=BOTH, expand=YES)
    scrollbar.pack(side='right', fill='y')

    # Add some nodes first (edges need node names)
    node_section = tb.Labelframe(
        scrollable_frame, text='Nodes (for testing)', padding=10
    )
    node_section.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    node_widgets = AddNode(node_section)

    # Add edge section
    edge_section = tb.Labelframe(scrollable_frame, text='Edges', padding=10)
    edge_section.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    edge_widgets = AddEdge(edge_section, node_widgets)

    # Instructions
    instructions = tb.Label(
        scrollable_frame,
        text='Test Instructions:\n'
        '1. Add 2-3 nodes and give them names (e.g., "run_level", "subject_level")\n'
        '2. Add edges and select node names from dropdowns\n'
        '3. Try deleting edges - they should renumber\n'
        '4. Filter is optional (format: {"entity": ["value1", "value2"]})',
        justify='left',
        padding=10,
    )
    instructions.pack(fill='x', padx=10, pady=10)

    root.mainloop()


if __name__ == '__main__':
    main()
