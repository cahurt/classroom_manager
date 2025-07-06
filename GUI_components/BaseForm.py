# GUI_components/BaseForm.py
from datetime import datetime

import ttkbootstrap as tb

class BaseForm(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.validation_label = tb.Label(self, text="", bootstyle="danger")
        self.validation_label.grid(pady=5)
        self.entry_list = {}

    def show_validation_error(self, message):
        self.validation_label.config(text=message)

    def clear_validation_error(self):
        self.validation_label.config(text="")

    def clear_form(self):
        for field_label, entry_tuple in self.entry_list.items():
            entry_type, widget = entry_tuple
            if isinstance(widget, tb.DateEntry):
                widget.entry.delete(0, 'end')
            elif isinstance(widget, tb.Text):
                widget.delete("1.0", "end")
            else:
                widget.delete(0, 'end')

    def show_standard_fields(self, display_fields, per_row=2):
        self.row_count = 0
        self.column_count = 0

        for label, field, entry_type in display_fields:
            if self.column_count % per_row == 0:
                self.row_count += 1
                self.column_count = 0

            field_label = tb.Label(self, text=label)
            field_label.grid(row=self.row_count, column=self.column_count, padx=10, pady=5)
            self.column_count += 1


            if entry_type == str:
                field_entry = tb.Entry(self, textvariable=field, width=50)
                field_entry.grid(row=self.row_count, column=self.column_count, padx=10, pady=5)
                self.entry_list[field] = (entry_type, field_entry)
                self.column_count += 1

            elif entry_type == int:
                field_entry = tb.Entry(self, textvariable=field, width=50)
                field_entry.grid(row=self.row_count, column=self.column_count, padx=10, pady=5)
                self.entry_list[field] = (entry_type, field_entry)
                self.column_count += 1

            elif entry_type == datetime:
                field_entry = tb.DateEntry(self, width=15)
                field_entry.grid(row=self.row_count, column=self.column_count, padx=10, pady=5)
                self.entry_list[field] = (entry_type, field_entry)
                self.column_count += 1

            elif entry_type == None:
                field_entry = tb.Text(self, width=15, height=4)
                field_entry.grid(row=self.row_count, column=self.column_count, padx=10, pady=5)
                self.entry_list[field] = (entry_type, field_entry)
                self.column_count += 1

    def validate_form(self):

        self.clear_validation_error()

        for field_label, entry_tuple in self.entry_list.items():
            entry_type, entry_widget = entry_tuple
            if entry_type == str:
                if not entry_widget.get().strip():
                    self.show_validation_error(f"Field {field_label} is required")
                    return False
            elif entry_type == int:
                if not entry_widget.get().strip() or not entry_widget.get().strip().isdigit():
                    self.show_validation_error(f"Field {field_label} is required and must be a number")
                    return False
            elif entry_type == datetime:
                if not entry_widget.entry.get().strip():
                    self.show_validation_error(f"Field {field_label} is required")
                    return False
                try:
                    datetime.strptime(entry_widget.entry.get(), '%m/%d/%Y')
                except ValueError:
                    self.show_validation_error(f"Field {field_label} must be in the format MM/DD/YYYY")
                    return False
                else:
                    self.clear_validation_error()
            else:
                if not entry_widget.get("1.0", "end-1c").strip():
                    self.show_validation_error(f"Field {field_label} is required")
                    return False

        self.clear_validation_error()
        return True

    def populate_fields(self, field_values):

        for field in field_values:
            entry_type, widget = self.entry_list[field]
            if isinstance(widget, tb.DateEntry):
                widget.entry.delete(0, 'end')
                widget.entry.insert(0, field_values.get(field))
            elif isinstance(widget, tb.Text):
                widget.delete("1.0", "end")
                widget.insert("1.0", field_values.get(field))
            else:
                widget.delete(0, 'end')
                widget.insert(0, field_values.get(field))

    


    def get_all_entries(self):

        self.value_list = {}
        for field_label, entry_tuple in self.entry_list.items():
            #print(f"Entry name: {field_label}")
            #print(f"Entry type: {entry_tuple[0]}")

            entry_widget = entry_tuple[1]

            # Handle different widget types
            if isinstance(entry_widget, tb.DateEntry):
                value = entry_widget.entry.get()  # Use .entry.get() for DateEntry
                self.value_list[field_label] = datetime.strptime(value, '%m/%d/%Y')
            elif isinstance(entry_widget, tb.Text):
                value = entry_widget.get("1.0", "end-1c")  # Special handling for Text widgets
                self.value_list[field_label] = value
            else:
                value = entry_widget.get()  # Regular Entry widgets
                self.value_list[field_label] = value

        return self.value_list

    def submit_form(self, form_to_show_next):
        if self.validate_form():
            self.grid_forget()
            form_to_show_next.grid(pady=20)
            self.value_list = self.get_all_entries()
            return self.value_list
        else:
            return None



