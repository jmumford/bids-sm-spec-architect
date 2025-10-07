import collections
import importlib.resources
from functools import partial
from tkinter import messagebox

import ttkbootstrap as tb
from ttkbootstrap.constants import *

from stats_spec_architect.utils import (
    CollapsingFrame,
    CreateCheckbuttonRow,
    create_label,
    create_label_combobox,
    create_label_entry,
    make_button,
)

label_width = 25


class AddNode:
    def __init__(self, master):
        import collections

        self.number = 0  # I don't think this is used
        self.master = master
        self.node_output = collections.defaultdict(dict)
        self.contrast_counter = collections.defaultdict(dict)
        make_button(self.master, 'Add Node', self.make_node_subframe)
        self.number_of_nodes = 0
        self.node_specific_cf = CollapsingFrame(self.master, padding=10)
        self.node_specific_cf.pack(fill=BOTH)

    def make_node_subframe(self):
        self.number_of_nodes = self.number_of_nodes + 1
        self.contrast_counter[f'node_{self.number_of_nodes}_num_contrasts'] = 0
        self.contrast_counter[f'node_{self.number_of_nodes}_num_dummy_contrasts'] = 0
        # Make a secondary collapsable frame
        frame_win_node_specific_cf = tb.Frame(self.node_specific_cf, padding=10)
        self.create_node_widgets(self.number_of_nodes, frame_win_node_specific_cf)
        self.node_specific_cf.add(
            child=frame_win_node_specific_cf,
            title=f'Node {self.number_of_nodes}',
            bootstyle=SECONDARY,
        )

    def create_node_widgets(self, node_number, frame):
        self.node_output[f'node_{node_number}']['Level (req)'] = create_label_combobox(
            frame,
            'Level (req)',
            ['Run', 'Session', 'Subject', 'Dataset'],
            frame_pack='top',
            label_left=True,
        )
        self.node_output[f'node_{node_number}']['Name (req, str)'] = create_label_entry(
            frame, 'Name (req, str)', frame_pack='top', label_left=True
        )
        self.node_output[f'node_{node_number}']['GroupBy (req)'] = CreateCheckbuttonRow(
            'GroupBy (req)', ['run', 'session', 'subject', 'contrast'], frame
        )
        self.node_output[f'node_{node_number}']['transformations'] = (
            AddTransformationWidgets(frame)
        )
        self.create_model_widgets(frame, node_number)
        # button for adding contrasts
        contrast_frame = tb.Frame(frame, padding=10)
        contrast_frame.pack(fill=X, expand=NO, pady=5)
        make_button(
            contrast_frame,
            'Add Contrast',
            partial(self.create_contrast_widgets, contrast_frame, node_number),
        )
        # button for adding dummy contrasts
        dummy_contrast_frame = tb.Frame(frame, padding=10)
        dummy_contrast_frame.pack(fill=X, expand=NO, pady=5)
        make_button(
            dummy_contrast_frame,
            'Add Dummy Contrast',
            partial(
                self.create_dummy_contrast_widgets, dummy_contrast_frame, node_number
            ),
        )

    def create_model_widgets(self, frame, node_number):
        self.node_output[f'node_{node_number}']['Model'] = {}
        model_frames_holder = tb.Frame(frame)
        model_frames_holder.pack(fill=X, expand=NO, pady=5)
        create_label('Model', model_frames_holder, frame_pack='left')
        model_widgets = {
            'Type': {'label': 'Type (req)', 'combobox_values': ['glm', 'meta']},
            'X (req, list of strings)': {'label': 'X (req, list of strings)'},
            'Formula (opt, str)': {'label': 'Formula (opt, str)'},
            'HRF (opt, str)': {'label': 'HRF (opt, str)'},
            'Options (opt, str)': {'label': 'Options (opt, str)'},
            'Software (opt, str)': {'label': 'Software (opt, str)'},
        }
        top_row_model_frames = tb.Frame(model_frames_holder)
        top_row_model_frames.pack(fill=X, expand=NO, pady=5)
        bottom_row_model_frames = tb.Frame(model_frames_holder)
        bottom_row_model_frames.pack(fill=X, expand=NO, pady=5)
        # I repeat this strategy below. Maybe I should build a function for this
        for widget_name, widget_info in model_widgets.items():
            if 'req' in widget_info['label']:
                row = top_row_model_frames
            else:
                row = bottom_row_model_frames
            if 'combobox_values' in widget_info.keys():
                self.node_output[f'node_{node_number}']['Model'][widget_name] = (
                    create_label_combobox(
                        row,
                        widget_info['label'],
                        widget_info['combobox_values'],
                        frame_pack='left',
                        label_left=False,
                    )
                )
            else:
                self.node_output[f'node_{node_number}']['Model'][widget_name] = (
                    create_label_entry(
                        row, widget_info['label'], frame_pack='left', label_left=False
                    )
                )

    def create_contrast_widgets(self, frame, node_number):
        self.contrast_counter[f'node_{self.number_of_nodes}_num_contrasts'] += 1
        if self.contrast_counter[f'node_{self.number_of_nodes}_num_contrasts'] == 1:
            self.node_output[f'node_{node_number}']['Contrasts'] = []
        current_contrast = {}
        row_of_contrast_frames_holder = tb.Frame(frame)
        row_of_contrast_frames_holder.pack(fill=X, expand=NO, pady=5)
        create_label(
            f'Contrast {self.contrast_counter[f'node_{self.number_of_nodes}_num_contrasts']}:',
            row_of_contrast_frames_holder,
            frame_pack='left',
        )
        contrast_widgets = {
            'Name (req, str)': {'label': 'Name (req, str)'},
            'ConditionList (req, list of strings)': {
                'label': 'ConditionList (req, list of strings)'
            },
            'Weights (req, list of numbers)': {
                'label': 'Weights (req, list of numbers)'
            },
            'Test (req)': {
                'label': 'Test (req)',
                'combobox_values': ['pass', 't', 'F'],
            },
        }
        for widget_name, widget_info in contrast_widgets.items():
            if 'combobox_values' in widget_info.keys():
                current_contrast[widget_name] = create_label_combobox(
                    row_of_contrast_frames_holder,
                    widget_info['label'],
                    widget_info['combobox_values'],
                    frame_pack='left',
                    label_left=False,
                )
            else:
                current_contrast[widget_name] = create_label_entry(
                    row_of_contrast_frames_holder,
                    widget_info['label'],
                    frame_pack='left',
                    label_left=False,
                )
        self.node_output[f'node_{node_number}']['Contrasts'].append(current_contrast)

    def create_dummy_contrast_widgets(self, frame, node_number):
        self.contrast_counter[f'node_{self.number_of_nodes}_num_dummy_contrasts'] += 1
        if (
            self.contrast_counter[f'node_{self.number_of_nodes}_num_dummy_contrasts']
            > 1
        ):
            messagebox.showwarning(
                'Dummy contrast warning', 'You only need 1 dummy contrast entry'
            )
        else:
            self.node_output[f'node_{node_number}']['DummyContrasts'] = {}
            row_of_contrast_frames_holder = tb.Frame(frame)
            row_of_contrast_frames_holder.pack(fill=X, expand=NO, pady=5)
            create_label(
                'Dummy Contrasts:', row_of_contrast_frames_holder, frame_pack='left'
            )
            contrast_widgets = {
                'Contrasts (opt, list of strings)': {
                    'label': 'Contrasts (opt, list of strings)'
                },
                'Test (req)': {
                    'label': 'Test (req)',
                    'combobox_values': ['pass', 't', 'F'],
                },
            }
            output_key = 'DummyContrasts'
            for widget_name, widget_info in contrast_widgets.items():
                if 'combobox_values' in widget_info.keys():
                    self.node_output[f'node_{node_number}'][output_key][widget_name] = (
                        create_label_combobox(
                            row_of_contrast_frames_holder,
                            widget_info['label'],
                            widget_info['combobox_values'],
                            frame_pack='left',
                            label_left=False,
                        )
                    )
                else:
                    self.node_output[f'node_{node_number}'][output_key][widget_name] = (
                        create_label_entry(
                            row_of_contrast_frames_holder,
                            widget_info['label'],
                            frame_pack='left',
                            label_left=False,
                        )
                    )


class AddTransformationWidgets:
    def __init__(self, collapsable_frame):
        import ttkbootstrap as tb

        self.number = 0
        # I need to make a separate frame that can by dynamic while fixing the model
        # frame that is below the transformations frame
        self.master = tb.Frame(collapsable_frame)
        self.master.pack(fill=X, expand=NO, pady=5)
        self.create_widgets()
        self.transformation_widget_dictionary = (
            self.make_transformation_widget_dictionary()
        )

    def create_widgets(self):
        self.frame = tb.Frame(self.master)
        self.frame.pack(fill=X, expand=NO, pady=5)
        self.cloneButton = tb.Button(
            self.frame, text='Add Transformation', command=self.clone
        )
        self.cloneButton.pack(side=LEFT, padx=5, fill=X, expand=NO)
        self.widget_output = collections.defaultdict(dict)

    def clone(self):
        if self.number == 0:
            self.widget_output['Transformer (req)'] = create_label_combobox(
                self.master,
                'Transformer (req)',
                ['pybids-transforms-v1'],
                frame_pack='top',
                label_left=True,
            )
        # This frame is within the parent frame (likely a collapsable frame)
        row_of_frames_holder = tb.Frame(self.master)
        row_of_frames_holder.pack(fill=X, expand=NO, pady=5)

        # Label the row with the transformation number
        form_field_label = tb.Label(
            master=row_of_frames_holder,
            text=f'Transformation {self.number + 1}:',
            width=label_width,
        )
        form_field_label.pack(side=LEFT, expand=NO, pady=5, padx=5)

        # Create dropdown with transformation names
        transformation_values = list(self.transformation_widget_dictionary.keys())
        transformation_combo = create_label_combobox(
            row_of_frames_holder,
            'Name',
            transformation_values,
            frame_pack='left',
            label_left=False,
        )
        transformation_combo.bind(
            '<<ComboboxSelected>>',
            partial(
                self.populate_transformation_fields,
                transformation=transformation_combo,
                row_holder=row_of_frames_holder,
                widget_output_handle=self.number,
            ),
        )
        self.number += 1

    def populate_transformation_fields(
        self, e, transformation=None, row_holder=None, widget_output_handle=None
    ):
        # Delete widgets if they were already created for a different transformation choice
        row_children = row_holder.winfo_children()
        num_children = len(row_children)
        if num_children > 2:
            for child_num, child in enumerate(row_children):
                if child_num > 1:
                    child.destroy()
        # add appropriate widgets for the selected transformation
        output = self.make_xform(transformation.get(), row_holder)
        self.widget_output[f'Instructions_{widget_output_handle}'] = output

    def make_xform(self, transform_name, row_holder):
        """
        Adds each label/entry widget pair for each transformation property
        """
        output_dict = {'Name': transform_name}
        for widget_info in self.transformation_widget_dictionary[transform_name]:
            if 'combobox_values' in widget_info.keys():
                output_dict[widget_info['label']] = create_label_combobox(
                    row_holder,
                    widget_info['label'],
                    widget_info['combobox_values'],
                    frame_pack='top',
                    label_left=False,
                )
            else:
                output_dict[widget_info['label']] = create_label_entry(
                    row_holder, widget_info['label'], frame_pack='top', label_left=False
                )
        return output_dict

    # Functions for creating widget dictionary
    def label_maker(self, property_name, optional=True, type=None):
        fill_opt_req = 'opt'
        if optional == False:
            fill_opt_req = 'req'
        if type:
            label = f'{property_name} ({fill_opt_req}, {type})'
        else:
            label = f'{property_name} ({fill_opt_req})'
        return label

    def make_type_widget(
        self, transform_property, transform_property_options, property_optional
    ):
        input_type = transform_property_options['type']
        if input_type == 'object':
            input_type = 'dictionary'
        type_label = self.label_maker(
            transform_property, optional=property_optional, type=input_type
        )
        if input_type == 'string' or input_type == 'dictionary':
            widget_dict = {'label': type_label, 'widget': 'Entry'}
        elif input_type == 'boolean':
            widget_dict = {
                'label': type_label,
                'widget': 'Combobox',
                'combobox_values': [True, False],
            }
        else:
            print('"type" can only be a string, boolean or dictionary')
        return widget_dict

    def make_type_items_widget(
        self, transform_property, transform_property_options, property_optional
    ):
        """
        I'm assuming ['type', 'item'] is always an array of something.
        """
        item_type = transform_property_options['items']['type']
        input_type = f'list of {item_type}s'
        type_label = self.label_maker(
            transform_property, optional=property_optional, type=input_type
        )
        widget_dict = {'label': type_label, 'widget': 'Entry'}
        return widget_dict

    def make_oneof_anyof(
        self, transform_property, transform_property_options, property_optional
    ):
        """
        Assuming these are always lists of strings
        """
        input_type = 'list of strings'
        type_label = self.label_maker(
            transform_property, optional=property_optional, type=input_type
        )
        widget_dict = {'label': type_label, 'widget': 'Entry'}
        return widget_dict

    def make_type_enum(
        self, transform_property, transform_property_options, property_optional
    ):
        """
        Assuming these are always lists of strings
        """
        input_type = None
        type_label = self.label_maker(
            transform_property, optional=property_optional, type=input_type
        )
        widget_dict = {
            'label': type_label,
            'widget': 'Combobox',
            'combobox_values': transform_property_options['enum'],
        }
        return widget_dict

    def make_widget(
        self, transform_property, transform_property_options, property_optional
    ):
        option_category = list(transform_property_options.keys())
        widget_data = None
        if option_category == ['type']:
            widget_data = self.make_type_widget(
                transform_property, transform_property_options, property_optional
            )
        if option_category == ['type', 'items']:
            widget_data = self.make_type_items_widget(
                transform_property, transform_property_options, property_optional
            )
        if (option_category == ['oneOf']) | (option_category == ['anyOf']):
            widget_data = self.make_oneof_anyof(
                transform_property, transform_property_options, property_optional
            )
        if option_category == ['type', 'enum']:
            widget_data = self.make_type_enum(
                transform_property, transform_property_options, property_optional
            )
        if not widget_data:
            print('shoot, something was missed')
        return widget_data

    # This is a horrible idea, I'll need to fix it later
    def get_xform_schema(self):
        import jsonref

        json_path = (
            importlib.resources.files('stats_spec_architect')
            / 'assets'
            / 'pybids_xform_schema_JM.json'
        )
        with open(json_path) as f:
            xform_schema = jsonref.load(f)
        return xform_schema

    def make_transformation_widget_dictionary(self):
        xform_schema = self.get_xform_schema()
        transform_widgets = {}
        for transform, transform_data in xform_schema['definitions'][
            'transformations'
        ].items():
            transform_widgets[transform] = []
            for transform_property, transform_property_options in transform_data[
                'properties'
            ].items():
                if transform_property not in ['_comment', 'Name']:
                    property_optional = (
                        transform_property not in transform_data['required']
                    )
                    transform_widgets[transform].append(
                        self.make_widget(
                            transform_property,
                            transform_property_options,
                            property_optional,
                        )
                    )
        return transform_widgets
