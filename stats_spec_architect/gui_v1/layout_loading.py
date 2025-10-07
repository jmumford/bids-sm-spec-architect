import tkinter as tk
import tkinter.messagebox as messagebox
from tkinter import filedialog

import ttkbootstrap as tb
from bids import BIDSLayout


class LayoutLoadWindow(tb.Window):
    def __init__(self, on_data_loaded, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_data_loaded = on_data_loaded
        self.title('Initial Setup')
        self.geometry('350x200')
        # ensures program is terminated if window is closed
        self.protocol('WM_DELETE_WINDOW', self.quit)
        # Add a label
        label = tk.Label(self, text='Choose how to load your BIDs data layout:')
        label.pack(pady=20)

        # Create buttons with ttkbootstrap styling
        self.load_bids_button = tb.Button(
            self,
            text='Load Layout from BIDs Directory Root',
            command=self.load_from_bids,
        )
        self.load_bids_button.pack(pady=5)

        self.load_db_button = tb.Button(
            self, text='Load Layout From Database Path', command=self.load_from_db
        )
        self.load_db_button.pack(pady=5)

        self.skip_button = tb.Button(self, text='Skip', command=self.skip)
        self.skip_button.pack(pady=5)

    def load_from_bids(self):
        # Ask user to choose a directory (BIDs directory)
        directory = filedialog.askdirectory(title='Select BIDs Directory Root')
        if directory:  # If the user selects a directory
            try:
                layout = BIDSLayout(directory, validate=True)
                self.withdraw()
                self.on_data_loaded(layout)
            except Exception as e:
                messagebox.showerror('Error', f'Error loading BIDs data: {e}')
        else:
            messagebox.showwarning('No Directory', 'No directory selected.')

    def load_from_db(self):
        # Ask user to choose a database path
        database_path = filedialog.askdirectory(title='Select Layout Database File')
        if database_path:  # If the user selects a database file
            try:
                layout = BIDSLayout(database_path=database_path)
                self.withdra()
                self.on_data_loaded(layout)
            except Exception as e:
                messagebox.showerror(
                    'Error', f'Error loading layout from database: {e}'
                )
        else:
            messagebox.showwarning('No File', 'No database file selected.')

    def skip(self):
        # Skip loading data and move to main GUI
        self.withdraw()
        self.on_data_loaded(None)
