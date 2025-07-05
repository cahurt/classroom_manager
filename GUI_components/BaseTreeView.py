# GUI_components/BaseTreeView.py
import ttkbootstrap as tb
from tkinter import NO, W, CENTER


class BaseTreeView(tb.Treeview):
    def __init__(self, parent, columns, column_widths=None):
        super().__init__(parent, bootstyle="primary")
        self.setup_columns(columns, column_widths)

    def setup_columns(self, columns, column_widths=None):
        self['columns'] = columns

        # Hide first column
        self.column("#0", width=0, stretch=NO)
        self.heading("#0", text="", anchor=W)

        # Setup other columns
        for i, col in enumerate(columns):
            width = column_widths[i] if column_widths else 200
            anchor = CENTER if 'date' in col.lower() else W
            self.column(col, anchor=anchor, width=width)
            self.heading(col, text=col, anchor=anchor)

    def reload_tree(self, object, coumsToGet):
        self.delete(*self.get_children())
        # Load units from database
