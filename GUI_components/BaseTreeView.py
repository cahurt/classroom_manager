# GUI_components/BaseTreeView.py
import ttkbootstrap as tb
from tkinter import NO, W, CENTER, messagebox




class BaseTreeView(tb.Treeview):
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    def __init__(self, parent, columns):
        column_names = [name for _, name, *_ in columns]
        super().__init__(parent, bootstyle="primary", columns=column_names)
        self.setup_columns(columns)


        # Initialize with column names
        super().__init__(parent, bootstyle="primary", columns=column_names)

        self.setup_columns(columns)

    def setup_columns(self, columns):
        # Hide first column
        self.column("#0", width=0, stretch=NO)
        self.heading("#0", text="", anchor=W)

        # Setup other columns
        self.col_count = 0
        for label, name, *column_width in columns:
            width = column_width[0] if column_width else 200
            anchor = CENTER if 'date' in name.lower() else W
            self.column(name, anchor=anchor, width=width, stretch=NO)
            self.heading(name, text=label, anchor=anchor)
            self.col_count += 1

    def reload_tree(self, query_result, expected_fields):
        # this will take a query object and the tree fields that should be part of the creation process
        self.delete(*self.get_children())
        for item in query_result:
            self.insert('', 'end',
                        values=self.format_tree_values(item,expected_fields))

    def get_selected_item_values(self):
        """Get values from selected tree item"""
        if not self.selection():
            return None
        selected = self.selection()[0]
        return self.item(selected)['values']

    def _create_dictionary_from_selected_tree_item_and_values(self, fields):
        # """Create dictionary of field values from selected unit#"""
        # this is a bit sketch b/c it has absolutely NO error checking, but it's
        # relying on the same source used to build the tree view... so it should work?

        if not self.selection():
            return

        selected = self.selection()[0]
        values = self.item(selected)['values']
        #print(values)
        dictionary_to_return = {}

        # Iterate through fields list and map values to their field names
        for i, (label, field_name, width) in enumerate(fields):
            dictionary_to_return[field_name] = values[i]

        return dictionary_to_return

    def format_tree_values(self, object_passed,expected_fields):
        #"""Format unit values for display"""
        values = []
        for label, field, width in expected_fields:
            value = getattr(object_passed, field)
            if 'date' in field and value:
                value = value.strftime(self.DISPLAY_DATE_FORMAT)
            values.append(value)
        return tuple(values)
        #return values_passed

    def validate_item_is_selected(self):
        #"""Validate unit selection for editing#"""
        if not self.selection():
            #BaseTab.show_error("Please select an item to edit")
            print("Please select an item to edit")
            return False
        return True

