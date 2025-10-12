"""
GUI v2 Utilities

Reusable GUI components for the Pydantic-based GUI.
Copied from v1 to make gui_v3 independent.
"""

import tkinter as tk
from pathlib import Path

import ttkbootstrap as tb
from ttkbootstrap.constants import BOTH, EW, INVERSE, LEFT, NO, NSEW, PRIMARY, X
from ttkbootstrap.style import Bootstyle

# Path to assets (icons for collapsing frame)
IMG_PATH = Path(__file__).parent.parent / 'assets'

# Standard label width
label_width = 25


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
        btn.pack(side='right')

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


class CreateCheckbuttonRow:
    """Creates a row of checkboxes with a label."""

    def __init__(self, label, checkbutton_names, frame_name):
        self.form_field_container = tb.Frame(frame_name)
        self.form_field_container.pack(fill=X, expand=NO, pady=55)
        self.make_checkbutton_row(label, checkbutton_names)

    def make_checkbutton_row(self, label, checkbutton_names):
        """Create the checkbox row widgets."""
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
        """Get list of checked checkbox values."""
        selections = []
        for checkbutton_name, checkvalue in self.is_selected.items():
            selection = checkvalue.get()
            if selection:
                selections.append(checkbutton_name)
        return selections
