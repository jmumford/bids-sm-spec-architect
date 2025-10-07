import collections

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from stats_spec_architect.utils import create_label_combobox, create_label_entry


class CreateInputWidgets:
    """
    Populates frame with Input Setting widgets
    """

    def __init__(self, master):
        self.master = master
        self.create_top_level_widgets()

    def create_top_level_widgets(self):
        self.widget_output = collections.defaultdict(dict)

        self.widget_output['Name (req, str)'] = create_label_entry(
            self.master, 'Name (req, str)', frame_pack='top', label_left=True
        )
        self.widget_output['BIDSModelVersion (req, str)'] = create_label_combobox(
            self.master,
            'BIDS Model Version (req)',
            ['1.0.0'],
            frame_pack='top',
            label_left=True,
            default=0,
        )
        self.widget_output['Description (opt, str)'] = create_label_entry(
            self.master, 'Description (opt, str)', frame_pack='top', label_left=True
        )

        inputs_frame = tb.Frame(self.master)
        inputs_frame.pack(fill=X, expand=NO, pady=5)
        self.widget_output['Input'] = {}
        input_section_label = tb.Label(master=inputs_frame, text='Input', width=25)
        input_section_label.pack(side=LEFT, expand=NO, pady=5)
        fields = ['subject', 'run', 'task', 'session']
        for field in fields:
            self.widget_output['Input'][f'{field} (opt, list of strings)'] = (
                create_label_entry(
                    inputs_frame,
                    f'{field} (opt, list of strings)',
                    frame_pack='left',
                    label_left=False,
                )
            )


class CreateInputWidgetsPydantic:
    """
    Populates frame with Input Setting widgets
    """

    def __init__(self, master):
        self.master = master
        self.create_top_level_widgets()

    def create_top_level_widgets(self):
        self.widget_output = collections.defaultdict(dict)

        self.widget_output['Name (req, str)'] = create_label_entry(
            self.master, 'Name (req, str)', frame_pack='top', label_left=True
        )
        self.widget_output['BIDSModelVersion (req, str)'] = create_label_combobox(
            self.master,
            'BIDS Model Version (req)',
            ['1.0.0'],
            frame_pack='top',
            label_left=True,
            default=0,
        )
        self.widget_output['Description (opt, str)'] = create_label_entry(
            self.master, 'Description (opt, str)', frame_pack='top', label_left=True
        )

        inputs_frame = tb.Frame(self.master)
        inputs_frame.pack(fill=X, expand=NO, pady=5)
        self.widget_output['Input'] = {}
        input_section_label = tb.Label(master=inputs_frame, text='Input', width=25)
        input_section_label.pack(side=LEFT, expand=NO, pady=5)
        fields = ['subject', 'run', 'task', 'session']
        for field in fields:
            self.widget_output['Input'][f'{field} (opt, list of strings)'] = (
                create_label_entry(
                    inputs_frame,
                    f'{field} (opt, list of strings)',
                    frame_pack='left',
                    label_left=False,
                )
            )