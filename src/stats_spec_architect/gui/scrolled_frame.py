"""
Vertical-only Scrolled Frame

A simplified scrolled frame that only scrolls vertically (no horizontal scroll).
"""

import tkinter as tk
from tkinter import ttk


class VerticalScrolledFrame:
    """
    A vertically scrolled Frame (no horizontal scrolling).

    Can be treated like any other Frame - needs a master and layout.
    """

    def __init__(self, master, **kwargs):
        """
        Initialize the vertical scrolled frame.

        Args:
            master: Parent widget
            **kwargs: Passed to the outer Frame (except 'width' and 'height' for Canvas)
        """
        width = kwargs.pop('width', None)
        height = kwargs.pop('height', None)
        self.outer = tk.Frame(master, **kwargs)

        # Vertical scrollbar only
        self.vsb = ttk.Scrollbar(self.outer, orient=tk.VERTICAL)
        self.vsb.grid(row=0, column=1, sticky='ns')

        # Canvas
        self.canvas = tk.Canvas(
            self.outer, highlightthickness=0, width=width, height=height
        )
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.outer.rowconfigure(0, weight=1)
        self.outer.columnconfigure(0, weight=1)

        # Connect scrollbar to canvas (vertical only)
        self.canvas['yscrollcommand'] = self.vsb.set
        self.vsb['command'] = self.canvas.yview

        # Inner frame (where content goes)
        self.inner = tk.Frame(self.canvas)
        self.canvas.create_window(4, 4, window=self.inner, anchor='nw')
        self.inner.bind('<Configure>', self._on_frame_configure)

        # Mouse scroll support - bind only to canvas and inner frame (not all widgets)
        self._setup_mousewheel()

        self.outer_attr = set(dir(tk.Widget))

    def __getattr__(self, item):
        """Delegate attribute access to outer frame if not found."""
        if item in self.outer_attr:
            return getattr(self.outer, item)
        else:
            return getattr(self.inner, item)

    def _on_frame_configure(self, event=None):
        """Update scroll region when frame size changes."""
        x1, y1, x2, y2 = self.canvas.bbox('all')
        height = self.canvas.winfo_height()
        self.canvas.config(scrollregion=(0, 0, x2, max(y2, height)))

    def _setup_mousewheel(self):
        """Set up mousewheel scrolling for all platforms."""
        import platform

        system = platform.system()

        # Use bind_all for maximum coverage, but check if cursor is over dropdown
        if system == 'Darwin':  # macOS
            self.canvas.bind_all('<MouseWheel>', self._on_mousewheel_mac)
        elif system == 'Windows':
            self.canvas.bind_all('<MouseWheel>', self._on_mousewheel_windows)
        else:  # Linux
            self.canvas.bind_all('<Button-4>', self._on_mousewheel_linux_up)
            self.canvas.bind_all('<Button-5>', self._on_mousewheel_linux_down)

    def _on_mousewheel_mac(self, event):
        """Handle mouse wheel scrolling on macOS."""
        # Don't scroll if cursor is over a dropdown list
        if self._is_over_dropdown(event):
            return
        # macOS trackpad/mouse - delta values are typically larger
        self.canvas.yview_scroll(int(-1 * event.delta), 'units')

    def _on_mousewheel_windows(self, event):
        """Handle mouse wheel scrolling on Windows."""
        if self._is_over_dropdown(event):
            return
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def _on_mousewheel_linux_up(self, event):
        """Handle mouse wheel scrolling up on Linux."""
        if self._is_over_dropdown(event):
            return
        self.canvas.yview_scroll(-1, 'units')

    def _on_mousewheel_linux_down(self, event):
        """Handle mouse wheel scrolling down on Linux."""
        if self._is_over_dropdown(event):
            return
        self.canvas.yview_scroll(1, 'units')

    def _is_over_dropdown(self, event):
        """Check if cursor is over a dropdown menu."""
        try:
            # Get widget under the pointer
            x, y = self.canvas.winfo_pointerxy()
            widget_under_cursor = self.canvas.winfo_containing(x, y)

            # If winfo_containing returns None, cursor is over a popup/dropdown!
            if widget_under_cursor is None:
                return True

            # Check widget class
            widget_class = widget_under_cursor.winfo_class()
            if widget_class == 'Listbox':
                return True

            # Check if in different toplevel (dropdown popup)
            try:
                cursor_toplevel = widget_under_cursor.winfo_toplevel()
                canvas_toplevel = self.canvas.winfo_toplevel()
                if cursor_toplevel != canvas_toplevel:
                    return True
            except:
                pass

            # Also check event.widget as fallback
            widget = event.widget
            if widget.winfo_class() == 'Listbox':
                return True

        except:
            # Any exception likely means cursor is over something outside our control
            return True

        return False
