import ttkbootstrap as tb
from stats_spec_architect.utils import (
    CollapsingFrame,
    create_label,
    create_label_entry,
    make_button,
)
from ttkbootstrap.constants import *

label_width = 25


class AddEdgeWidgets:
    def __init__(self, master):
        self.widgets = []
        self.master = master
        self.edge_output = []
        make_button(self.master, "Add Edge", self.make_edge_subframe)
        self.number_of_edges = 0
        self.edge_specific_cf = CollapsingFrame(self.master, padding=10)
        self.edge_specific_cf.pack(fill=BOTH)

    def make_edge_subframe(self):
        self.number_of_edges += 1
        edge_output_dict = {}
        edge_frame = tb.Frame(self.master)
        edge_frame.pack(fill=X, expand=NO, pady=5)
        create_label(f"Edge {self.number_of_edges}", edge_frame, frame_pack="left")
        entry_widget_names = [
            "Source (req, str)",
            "Destination (req, str)",
            "Filter (opt, dict)",
        ]
        for entry_widget_name in entry_widget_names:
            edge_output_dict[entry_widget_name] = create_label_entry(
                edge_frame,
                entry_widget_name,
                frame_pack="left",
                entry_width=25,
                label_left=False,
            )
        self.edge_output.append(edge_output_dict)
