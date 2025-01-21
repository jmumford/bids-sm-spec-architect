import collections
import json
import re
from tkinter import messagebox


def check_str(widget_label, val):
    # just make sure there aren't any commas
    success = True
    val_save = None
    if len(val) > 0:
        if "," in val:
            messagebox.showwarning(
                f"Problem with entry in {widget_label}",
                f"Problem with entry in {widget_label}",
                "\n Entry should be single string without commas",
            )
            success = False
        else:
            val_save = val
    return val_save


def check_list_of_strings(widget_label, val):
    val_save = None
    if len(val) > 0:
        if "," in val:
            val_save = re.split(",", val)
            val_save = [
                (re.sub(r"\[|\]|\'|\"|\s", "", val)) for val in val_save if len(val) > 0
            ]
        else:
            val_save = [val]
    return val_save


def check_list_of_numbers(widget_label, val):
    val_save = None
    if len(val) > 0:
        if "," in val:
            val_save = re.split(",", val)
            val_save = [
                (re.sub(r"\[|\]|\'|\"|\s", "", val)) for val in val_save if len(val) > 0
            ]
        else:
            val_save = [val]
    try:
        val_save = [float(val) for val in val_save]
    except:
        val_save = None
        messagebox.showwarning(
            f"Entry {widget_label}", f"{widget_label} must be a list of numbers"
        )
    return val_save


def process_entrybox(label, widget_data):
    label_info = re.split("[(),]", label)
    label_info = [val.strip() for val in label_info if len(val) > 0]
    # will be str, list of strings, list of numbers or dict
    if ("str" in label_info) or ("string" in label_info):
        widget_data_get = widget_data.get()
        val_save = check_str(label, widget_data_get)
        if ("req" in label_info) and (val_save == None):
            messagebox.showwarning(
                f"Entry {label}", f"{label} is required for the model spec"
            )
    if "list of strings" in label_info:
        widget_data_get = widget_data.get()
        val_save = check_list_of_strings(label, widget_data_get)
        if ("req" in label_info) and (val_save == None):
            messagebox.showwarning(
                f"Entry {label}", f"{label} is required for the model spec"
            )
    if "list of numbers" in label_info:
        widget_data_get = widget_data.get()
        val_save = check_list_of_numbers(label, widget_data_get)
    if "dict" in label_info:
        val_save = None
    return label_info[0], val_save


def process_combobox(label, widget_data):
    label_info = re.split("[(),]", label)
    label_info = [val.strip() for val in label_info if len(val) > 0]
    widget_data_get = widget_data.get()
    if ("req" in label_info) and (len(widget_data_get) == 0):
        messagebox.showwarning(
            f"Entry {label}", f"{label} is required for the model spec"
        )
    elif len(widget_data_get) == 0:
        val_save = None
    else:
        val_save = widget_data_get
    return label_info[0], val_save


def process_widget(label, widget_data):
    import tkinter

    # Will either be a combobox, entry or string
    if isinstance(widget_data, tkinter.ttk.Combobox):
        spec_key, val_save = process_combobox(label, widget_data)
    elif isinstance(widget_data, tkinter.ttk.Entry):
        spec_key, val_save = process_entrybox(label, widget_data)
    elif isinstance(widget_data, str):
        spec_key = label
        val_save = widget_data
    else:
        print("Jeanette, you need to write code for whatever this is")
        print(type(widget_data))
        spec_key = "oops"
        val_save = "fix this"
    return spec_key, val_save


def process_transformation_object(widget_data):
    transformations_out = collections.defaultdict(dict)
    for trans_label, trans_widget in widget_data.items():
        if "Instructions" not in trans_label:
            spec_key, val_save = process_widget(trans_label, trans_widget)
            if val_save is not None:
                transformations_out[spec_key] = val_save
        elif "Instructions" in trans_label:
            instruction_widget_out = {}
            if "Instructions" not in transformations_out:
                transformations_out["Instructions"] = []
            for instruction_label, instruction_widget in trans_widget.items():
                instruction_spec_key, instruction_val_save = process_widget(
                    instruction_label, instruction_widget
                )
                if instruction_val_save is not None:
                    instruction_widget_out[instruction_spec_key] = instruction_val_save
            transformations_out["Instructions"].append(instruction_widget_out)
        else:
            print("oh no, there is something I missed in transformations objects")
    return transformations_out


def process_checkbox_row_object(label, widget_data):
    label_info = re.split("[(),]", label)
    label_info = [val.strip() for val in label_info if len(val) > 0]
    selections = widget_data.get_list_of_checked_values()
    if (len(selections) == 0) and ("req" in label_info):
        messagebox.showwarning(
            f"Checkboxes for {label}", f"{label} requires you check at least 1 box"
        )
        val_save = None
    else:
        val_save = selections
    return label_info[0], val_save


def process_list(label, widget_data):
    label_info = re.split("[(),]", label)
    output = []
    for list_val in widget_data:
        if isinstance(list_val, dict):
            out_loop = {}
            for spec_sub_label, sub_widget in list_val.items():
                out_key, val_save = process_widget(spec_sub_label, sub_widget)
                out_loop[out_key] = val_save
            output.append(out_loop)
    return label_info[0], output


def format_data_inputs_nodes_edges(node_inputs_edge_object):
    """
    Processes each of nodes, inputs and edges
    """
    import tkinter

    from stats_spec_architect.nodes_transformations_setup import (
        AddTransformationWidgets,
    )
    from stats_spec_architect.nodes_transformations_setup_try_tabs import (
        AddTransformationWidgets,
    )
    from stats_spec_architect.utils import CreateCheckbuttonRow

    model_spec = collections.defaultdict(dict)
    # The entries should either be tkinter objects or dictionaries
    #  (containing tkinter objects).  This will process each
    # top_level_data.widget_output.items():
    for label, widget_data in node_inputs_edge_object.items():
        # This will grab entry and combobox widgets (not sure why both)
        if isinstance(widget_data, tkinter.ttk.Entry):
            spec_key, val_save = process_widget(label, widget_data)
            if val_save is not None:
                model_spec[spec_key] = val_save
        elif isinstance(widget_data, dict):
            for sub_label, sub_widget_data in widget_data.items():
                spec_key, val_save = process_widget(sub_label, sub_widget_data)
                if val_save is not None:
                    model_spec[label][spec_key] = val_save
        elif isinstance(widget_data, AddTransformationWidgets):
            transformation_widgets = process_transformation_object(
                widget_data.widget_output
            )
            if bool(transformation_widgets):
                model_spec["Transformations"] = transformation_widgets
        elif isinstance(widget_data, CreateCheckbuttonRow):
            spec_key, val_save = process_checkbox_row_object(label, widget_data)
            if val_save is not None:
                model_spec[spec_key] = val_save
        elif isinstance(widget_data, list):
            # This is a bit "dangerous" since I'm assuming the list
            # is filled with dictionaries.
            spec_key, val_save = process_list(label, widget_data)
            model_spec[spec_key] = val_save
        else:
            print("Jeanette you missed something")
            print(f"Label is {label} and type is {type(widget_data)}")
    return model_spec


def make_json(top_level_data, node_widgets, edge_widgets):
    model_spec = format_data_inputs_nodes_edges(top_level_data.widget_output)
    nodes = []
    for node_name, node_widget_data in node_widgets.node_output.items():
        current_node_json = format_data_inputs_nodes_edges(node_widget_data)
        nodes.append(current_node_json)
    model_spec["Nodes"] = nodes
    edges = []
    for edge_widget_output in edge_widgets.edge_output:
        single_edge = format_data_inputs_nodes_edges(edge_widget_output)
        edges.append(single_edge)
    model_spec["Edges"] = edges
    json_formatted_str = json.dumps(model_spec, indent=4)
    print(json_formatted_str)
    return json_formatted_str
