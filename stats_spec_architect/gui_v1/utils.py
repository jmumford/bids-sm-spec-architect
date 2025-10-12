import collections
import tkinter as tk
from functools import partial
from pathlib import Path
from tkinter import filedialog

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.style import Bootstyle

from stats_spec_architect.gui_v1.make_json import make_json

label_width = 25


IMG_PATH = Path(__file__).parent.parent / 'assets'


# Used to make each frame collapsable
class CollapsingFrame(tb.Frame):
    """A collapsible frame widget that opens and closes with a click."""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.columnconfigure(0, weight=1)
        self.cumulative_rows = 0

        # widget images
        self.images = [
            tb.PhotoImage(file=IMG_PATH / 'icons8_double_up_24px.png'),
            tb.PhotoImage(file=IMG_PATH / 'icons8_double_right_24px.png'),
        ]

    def add(self, child, title='', bootstyle=PRIMARY, **kwargs):
        """Add a child to the collapsible frame
        Parameters:
            child (Frame):
                The child frame to add to the widget.
            title (str):
                The title appearing on the collapsible section header.
            bootstyle (str):
                The style to apply to the collapsible section header.
            **kwargs (Dict):
                Other optional keyword arguments.
        """
        if child.winfo_class() != 'TFrame':
            return

        style_color = Bootstyle.ttkstyle_widget_color(bootstyle)
        frm = tb.Frame(self, bootstyle=style_color)
        frm.grid(row=self.cumulative_rows, column=0, sticky=EW)

        # header title
        header = tb.Label(
            master=frm,
            text=title,
            font=('Helvetica', 22),
            bootstyle=(style_color, INVERSE),
        )
        if kwargs.get('textvariable'):
            header.configure(textvariable=kwargs.get('textvariable'))
        header.pack(side=LEFT, fill=BOTH, padx=10)

        # header toggle button
        def _func(c=child):
            return self._toggle_open_close(c)

        btn = tb.Button(
            master=frm, image=self.images[0], bootstyle=style_color, command=_func
        )
        btn.pack(side=RIGHT)

        # assign toggle button to child so that it can be toggled
        child.btn = btn
        child.grid(row=self.cumulative_rows + 1, column=0, sticky=NSEW)

        # increment the row assignment
        self.cumulative_rows += 2

    def _toggle_open_close(self, child):
        """Open or close the section and change the toggle button
        image accordingly.
        Parameters:
            child (Frame):
                The child element to add or remove from grid manager.
        """
        # Check if widget still exists (in case it was deleted)
        try:
            if child.winfo_exists() and child.winfo_viewable():
                child.grid_remove()
                child.btn.configure(image=self.images[1])
            elif child.winfo_exists():
                child.grid()
                child.btn.configure(image=self.images[0])
        except tk.TclError:
            # Widget has been destroyed, ignore
            pass


def _label_add_grid(parent_frame, label, row, column, label_width=None):
    """
    Makes label widget and adds it to row/column of grid within given frame.
    Primarily used in create_label_entry and create_label_combobox
    """
    label_widget = tb.Label(master=parent_frame, text=label, width=label_width)
    label_widget.grid(row=row, column=column, padx=5)


def _entry_add_grid(parent_frame, row, column, width=25):
    """
    Makes entry widget and adds it to row/column of grid within given frame
    Primarily used in create_label_entry
    """
    entry_widget = tb.Entry(master=parent_frame, width=width)
    entry_widget.grid(row=row, column=column, padx=5)
    return entry_widget


def _combobox_add_grid(parent_frame, combobox_values, row, column):
    """
    Makes combobox widget and adds it to row/column of grid within given frame
    Primarily used in create_label_combobox
    """
    entry_combo = tb.Combobox(master=parent_frame, values=combobox_values, width=24)
    entry_combo.grid(row=row, column=column, padx=5)
    return entry_combo


def create_label_entry(
    parent_frame, label, frame_pack='top', entry_width=25, label_left=True
):
    """
    creates a label widget with an entry widget
    label_left=True adds label to the left of entry
    label_left=False adds label above the entry
    """
    if frame_pack == 'top':
        frame_pack_kwargs = {'fill': X, 'expand': NO, 'pady': 5}
    elif frame_pack == 'left':
        frame_pack_kwargs = {'side': LEFT, 'expand': NO, 'pady': 5}

    widget_pair_frame = tb.Frame(parent_frame)
    widget_pair_frame.pack(**frame_pack_kwargs)
    row_label = 0
    column_label = 0
    if label_left:
        row_entry = 0
        column_entry = 1
        _label_add_grid(
            widget_pair_frame, label, row_label, column_label, label_width=25
        )
        entry_widget = _entry_add_grid(
            widget_pair_frame, row_entry, column_entry, width=entry_width
        )
    else:
        row_entry = 1
        column_entry = 0
        _label_add_grid(widget_pair_frame, label, row_label, column_label)
        entry_widget = _entry_add_grid(
            widget_pair_frame, row_entry, column_entry, width=entry_width
        )
    return entry_widget


def create_label_combobox(
    parent_frame, label, combobox_values, frame_pack, label_left=True, default=None
):
    """
    creates a label widget with a combobox widget
    label_left=True adds label to the left of combobox
    label_left=False adds label above the combobox
    :param int default: Index of value in combobox_values to default to.
    """
    if frame_pack == 'top':
        frame_pack_kwargs = {'fill': X, 'expand': NO, 'pady': 5}
    elif frame_pack == 'left':
        frame_pack_kwargs = {'side': LEFT, 'expand': NO, 'pady': 5}
    widget_pair_frame = tb.Frame(parent_frame)
    widget_pair_frame.pack(**frame_pack_kwargs)
    row_label = 0
    column_label = 0
    if label_left:
        row_combobox = 0
        column_combobox = 1
        _label_add_grid(
            widget_pair_frame, label, row_label, column_label, label_width=25
        )
        combobox_widget = _combobox_add_grid(
            widget_pair_frame, combobox_values, row_combobox, column_combobox
        )
    else:
        row_combobox = 1
        column_combobox = 0
        _label_add_grid(widget_pair_frame, label, row_label, column_label)
        combobox_widget = _combobox_add_grid(
            widget_pair_frame, combobox_values, row_combobox, column_combobox
        )
    if default is not None:
        combobox_widget.current(default)
    return combobox_widget


def make_button(master_frame, label, command):
    frame = tb.Frame(master_frame)
    frame.pack(fill=X, expand=NO, pady=5)
    cloneButton = tb.Button(frame, text=label, command=command)
    cloneButton.pack(side=LEFT, padx=5, fill=X, expand=NO)


def create_label(label, frame_name, frame_pack='top'):
    if frame_pack == 'top':
        frame_pack_kwargs = {'fill': X, 'expand': NO, 'pady': 5}
    elif frame_pack == 'left':
        frame_pack_kwargs = {'side': LEFT, 'expand': NO, 'pady': 5}
    form_field_container = tb.Frame(frame_name)
    form_field_container.pack(**frame_pack_kwargs)

    form_field_label = tb.Label(
        master=form_field_container, text=label, width=label_width
    )
    form_field_label.pack(side=LEFT, padx=5)


class CreateCheckbuttonRow:
    def __init__(self, label, checkbutton_names, frame_name):
        self.form_field_container = tb.Frame(frame_name)
        self.form_field_container.pack(fill=X, expand=NO, pady=55)
        self.make_checkbutton_row(label, checkbutton_names)

    def make_checkbutton_row(self, label, checkbutton_names):
        form_field_label = tb.Label(
            master=self.form_field_container, text=label, width=label_width
        )
        form_field_label.pack(side=LEFT, padx=5)
        checkbutton_dict = {}
        self.is_selected = {}
        for checkbutton_name in checkbutton_names:
            self.is_selected[checkbutton_name] = tk.IntVar()
            checkbutton_dict[checkbutton_name] = tb.Checkbutton(
                master=self.form_field_container,
                bootstyle='primary',
                text=checkbutton_name,
                variable=self.is_selected[checkbutton_name],
                onvalue=1,
                offvalue=0,
            )
            checkbutton_dict[checkbutton_name].pack(
                side=LEFT, padx=5, fill=X, expand=NO
            )

    def get_list_of_checked_values(self):
        selections = []
        for checkbutton_name, checkvalue in self.is_selected.items():
            selection = checkvalue.get()
            if selection:
                selections.append(checkbutton_name)
        return selections


def json_to_file(top_level_data, node_widgets, edge_widgets):
    to_save = make_json(top_level_data, node_widgets, edge_widgets)
    name = top_level_data.widget_output['Name (req, str)'].get()
    save_file(to_save, f'{name}.json')


def save_file(to_save, filename):
    file = filedialog.asksaveasfile(initialfile=filename)
    file.write(to_save)
    file.close()


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#### OLD (I don't think I use anything below this)


# Functions that create label/entry type widget pairs
# The label is to the left of the entry widget


# Entry widget with label to left of it
def create_form_entry_not_used(label, frame_name):
    form_field_container = tb.Frame(frame_name)
    form_field_container.pack(fill=X, expand=NO, pady=5)

    form_field_label = tb.Label(
        master=form_field_container, text=label, width=label_width
    )
    form_field_label.pack(side=LEFT, padx=5)

    form_input = tb.Entry(master=form_field_container)
    form_input.pack(side=LEFT, padx=5, fill=X, expand=NO)

    # add_regex_validation(form_input, r'^[a-zA-Z0-9_]*$')
    return form_input


# Combo box with label to left of it
def create_combobox_not_used(label, combobox_values, frame_name):
    form_field_container = tb.Frame(frame_name)
    form_field_container.pack(fill=X, expand=NO, pady=5)

    form_field_label = tb.Label(
        master=form_field_container, text=label, width=label_width
    )
    form_field_label.pack(side=LEFT, padx=5)  # I definitely need the left here.
    # form_field_label.pack(padx=5)

    form_combo = tb.Combobox(master=form_field_container, values=combobox_values)
    form_combo.pack(side=LEFT, padx=5, fill=X, expand=NO)
    return form_combo


#  Creates a rows of checkbox widgets with a label next to it
def create_checkbutton_row_with_select_all_not_used(
    label, checkbutton_names, frame_name
):
    form_field_container = tb.Frame(frame_name)
    form_field_container.pack(fill=X, expand=NO, pady=5)

    form_field_label = tb.Label(
        master=form_field_container, text=label, width=label_width
    )
    form_field_label.pack(side=LEFT, padx=5)

    form_checkbutton = []
    checkbutton_dict = {}
    for checkbutton_name in checkbutton_names:
        is_selected = tk.IntVar()
        if checkbutton_name != 'Select all':
            checkbutton_dict[checkbutton_name] = tb.Checkbutton(
                master=form_field_container,
                bootstyle='primary',
                text=checkbutton_name,
                variable=is_selected,
                onvalue=1,
                offvalue=0,
            )
        #                                    command=checker)
        if checkbutton_name == 'Select all':
            checkbutton_dict[checkbutton_name] = tb.Checkbutton(
                master=form_field_container,
                bootstyle='primary',
                text=checkbutton_name,
                variable=is_selected,
                onvalue=1,
                offvalue=0,
                command=partial(check_all_checkbuttons, checkbutton_dict),
            )
        checkbutton_dict[checkbutton_name].pack(side=LEFT, padx=5, fill=X, expand=NO)
        # form_checkbutton[checkbutton_name] = is_selected
        form_checkbutton.append()
    return form_checkbutton


# Checks input values (this will be replace later, it isn't currently used)
# It is weird that this is called when the checkbuttons are checked.
# I must need something to save out the checkbuttons that were selected?
def checker_not_used(event=None):
    model_spec = collections.defaultdict(dict)
    model_spec['Name'] = analysis_name.get()
    model_spec['BIDSModelVersion'] = bids_version.get()
    model_spec['Description'] = description.get()
    checker_process_form_entry(subjects, model_spec, 'Input', 'subject')
    model_spec['Input']['task'] = checker_process_dictionary(task_out)
    model_spec['Input']['run'] = checker_process_dictionary(run_out)
    model_spec['Input']['session'] = checker_process_dictionary(session_out)
    print(json.dumps(model_spec, indent=2))


# Used in create_checkbutton_row.  Perhaps I should make that a Class object?
def check_all_checkbuttons_not_used(check_button_set):
    for check_name, is_selected in check_button_set.items():
        if check_name != 'Select all':
            if check_button_set['Select all'].instate(['selected']) == True:
                if check_button_set[check_name].instate(['selected']) == False:
                    check_button_set[check_name].invoke()
            if check_button_set['Select all'].instate(['selected']) == False:
                if check_button_set[check_name].instate(['selected']) == True:
                    check_button_set[check_name].invoke()
