from functools import partial

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from stats_spec_architect.DoubleScrolledFrame import DoubleScrolledFrame
from stats_spec_architect.edges_setup import AddEdgeWidgets
from stats_spec_architect.input_setup import CreateInputWidgets
from stats_spec_architect.make_json import make_json
from stats_spec_architect.nodes_transformations_setup_try_tabs import AddNode
from stats_spec_architect.utils import CollapsingFrame, json_to_file, make_button


def main():
    # GUI window
    main_window = tb.Window(themename="superhero", minsize=(300, 1))
    main_window.title("BidsSM maker")
    main_window.geometry("1400x950")

    # Turn it into a scrolled frame
    scrolling_window = DoubleScrolledFrame(main_window)
    scrolling_window.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    # Set up so all added frames (added to cf) will be collapsing frames
    cf = CollapsingFrame(scrolling_window)
    cf.pack(fill=BOTH)
    label_width = 30
    s = tb.Style()
    s.configure(".", font=("Helvetica", 18))

    # Inputs Section
    top_level_frame = tb.Frame(cf, padding=10)
    top_level_data = CreateInputWidgets(top_level_frame)
    cf.add(child=top_level_frame, title="Top level data")

    # Nodes
    nodes_frame = tb.Frame(cf, padding=10)
    node_widgets = AddNode(nodes_frame)
    cf.add(child=nodes_frame, title="Nodes")

    # Edges
    edges_frame = tb.Frame(cf, padding=10)
    edge_widgets = AddEdgeWidgets(edges_frame)
    cf.add(child=edges_frame, title="Edges")

    # Button to display json
    make_button(
        main_window,
        "Show Model Spec!",
        partial(make_json, top_level_data, node_widgets, edge_widgets),
    )

    # Button to save json to file
    make_button(
        main_window,
        "Save as file",
        partial(json_to_file, top_level_data, node_widgets, edge_widgets),
    )

    main_window.mainloop()


if __name__ == "__main__":
    main()
