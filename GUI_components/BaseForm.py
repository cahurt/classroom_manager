# GUI_components/BaseForm.py
from datetime import datetime
from tkinter import colorchooser

import ttkbootstrap as tb

from Model import Unit, Objective


class BaseForm(tb.Frame):
    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'
    DEFAULT_COLOR = "#000000"

    def __init__(self, parent, display_labels):
        super().__init__(parent)
        self.validation_label = tb.Label(self, text="", bootstyle="danger")
        self.validation_label.grid(pady=5)
        self.entry_dictionary = {}  # this is a dictionary of the field name, (which SHOULD be the class variable name... if it's not then you dun messed up and this method cannot help you) and the entry widget
        self.display_labels = display_labels  # this is a list of tuples we use to parse out what to display, the rules are in the form builder method

    def show_validation_error(self, message):
        self.validation_label.config(text=message)

    def clear_validation_error(self):
        self.validation_label.config(text="")

    def create_buttons(self, button_data):
        for text, style, row, col, colspan, command in button_data:
            btn = tb.Button(self, text=text, bootstyle=style, command=command)
            btn.grid(row=row, column=col, columnspan=colspan, pady=20)

    def clear_form(self):
        for field_label, widget in self.entry_dictionary.items():
            if isinstance(widget, tb.DateEntry):
                widget.entry.delete(0, 'end')
            elif isinstance(widget, tb.Text):
                widget.delete("1.0", "end")
            elif isinstance(widget, tb.Button):
                widget.color = "#000000"
            elif isinstance(widget, tb.Combobox):
                widget.set('')
            else:
                widget.delete(0, 'end')

    def _choose_color(self, button, var):
        # Open color chooser dialog
        color = colorchooser.askcolor(color=button.color, title="Choose Color")
        if color[1]:  # color[1] contains the hex value
            button.color = color[1]
            var.set(color[1])
            button.configure(bootstyle=f"light")

    def show_standard_fields(self, per_row=2):
        # updated the show_standard_fields method with the followiong rules: use the third element in the display_fields tuple -
        # entires that start with 'string' are tb.Entry fields. The first number in the parentheses is the widthe of the field, the second is the max characters allowed
        # enties that start with 'text' are tb.Text enties with the first number in the parentheses being the width, the second being the height, and the last the max number of characters allowed
        # entires that start with 'int' are whole numbers with the first number in the parentheses being the width of the field the second being the lowest allowed, the last being the highest allowed
        # entries that start with 'color; are color pickers
        # entires that start with 'file' are file uploads
        # entries that start with 'dropdown' are drop down menus that use the 4th value in the tuple as the array to pick from

        self.row_count = 0
        self.column_count = 0

        for label, field, entry_type, *extra in self.display_labels:
            if self.column_count % per_row == 0:
                self.row_count += 1
                self.column_count = 0

            field_label = tb.Label(self, text=label)
            field_label.grid(row=self.row_count, column=self.column_count, padx=10, pady=5)
            self.column_count += 1

            if entry_type.startswith('string'):
                width, max_chars = eval(entry_type.replace('string', ''))
                field_entry = tb.Entry(self, textvariable=field, width=width)
                field_entry.config(validate='key',
                                   validatecommand=(self.register(lambda s: len(s) <= max_chars), '%P'))

                # Add new handler for unit_dropdown type
            elif entry_type == 'unit_dropdown':
                units = Unit.get_all_order_by_sequence()
                # Create list of tuples with (unit_ID, name) for the combobox
                unit_choices = [(str(unit.unit_ID), unit.name) for unit in units] if not extra else extra[0]
                # Create a Combobox with just the names
                field_entry = tb.Combobox(self, values=[name for _, name in unit_choices])
                # Store the unit_choices for later lookup
                field_entry.unit_choices = unit_choices

            elif entry_type == 'objective_dropdown':
                objectives = Objective.get_all()
                # Create list of tuples with (objective_ID, name) for the combobox
                objective_choices = [(str(objective.objective_ID), objective.name) for objective in objectives] if not extra else extra[0]
                # Create a Combobox with just the names
                field_entry = tb.Combobox(self, values=[name for _, name in objective_choices])
                # Store the objective_choices for later lookup
                field_entry.objective_choices = objective_choices

            elif entry_type.startswith('text'):
                width, height, max_chars = eval(entry_type.replace('text', ''))
                field_entry = tb.Text(self, width=width, height=height)
                field_entry.bind('<KeyPress>', lambda e, w=field_entry, m=max_chars:
                None if len(w.get('1.0', 'end-1c')) >= m and e.keysym not in ('BackSpace', 'Delete') else True)

            elif entry_type.startswith('int'):
                width, min_val, max_val = eval(entry_type.replace('int', ''))
                field_entry = tb.Entry(self, textvariable=field, width=width)

                # field_entry.config(validate='key', validatecommand=(self.register(
                #    lambda s: s.isdigit() and (not s or min_val <= int(s) <= max_val)), '%P'))

            elif entry_type.startswith('color'):
                field_entry = tb.Button(self, text="Choose Color...")
                color_var = tb.StringVar(value="#000000")  # Default color
                field_entry.configure(command=lambda b=field_entry, v=color_var: self._choose_color(b, v))
                field_entry.color = color_var.get()
                field_entry.configure(bootstyle=f"light")

            elif entry_type.startswith('file'):
                field_entry = tb.Button(self, text="Choose File...")

            elif entry_type.startswith('dropdown'):
                options = extra[0] if extra else []
                field_entry = tb.Combobox(self, values=options)

            elif entry_type.startswith('date'):
                options = extra[0] if extra else []
                field_entry = tb.DateEntry(self, self.DISPLAY_DATE_FORMAT)

            # if all else fails we just give it a standard non-validated entry field
            else:
                field_entry = tb.Entry(self, textvariable=field, width=50)

            # Store the entry and its type in entry_list
            self.entry_dictionary[field] = field_entry
            # make it visible
            field_entry.grid(row=self.row_count, column=self.column_count, padx=10, pady=5)
            self.column_count += 1


    def validate_form(self):
        self.clear_validation_error()

        for label, field, entry_type, *extra in self.display_labels:

            if isinstance(self.entry_dictionary.get(field), tb.DateEntry):
                if not self.entry_dictionary.get(field).entry.get().strip():
                    self.show_validation_error(f"Field {label} is required")
                    return False
                try:
                    datetime.strptime(self.entry_dictionary.get(field).entry.get(), '%m/%d/%Y')
                except ValueError:
                    self.show_validation_error(f"Field {label} must be in the format MM/DD/YYYY")
                    return False
                else:
                    self.clear_validation_error()
            elif isinstance(self.entry_dictionary.get(field), tb.Text):
                if not self.entry_dictionary.get(field).get("1.0", "end-1c").strip():
                    self.show_validation_error(f"Field {label} is required")
                    return False
            elif isinstance(self.entry_dictionary.get(field), tb.Button):
                pass
            else:
                value = self.entry_dictionary.get(field).get().strip()
                if not value:
                    self.show_validation_error(f"Field {label} is required")
                    return False
                if entry_type.startswith('int') and not value.isdigit():
                    self.show_validation_error(f"Field {label} must be a number")
                    return False

        self.clear_validation_error()
        return True


    def populate_fields(self, field_values):
        for field in field_values:
            if field not in self.entry_dictionary:
                pass
            else:
                widget = self.entry_dictionary[field]
                if isinstance(widget, tb.DateEntry):
                    widget.entry.delete(0, 'end')
                    widget.entry.insert(0, field_values.get(field))
                elif hasattr(widget, 'unit_choices'):
                    # Handle unit dropdown population
                    unit = field_values.get(field)
                    if unit and hasattr(unit, 'name'):
                        widget.set(unit.name)
                elif isinstance(widget, tb.Text):
                    widget.delete("1.0", "end")
                    widget.insert("1.0", field_values.get(field))
                elif isinstance(widget, tb.Button):
                    widget.color = self.DEFAULT_COLOR
                    pass
                else:
                    widget.delete(0, 'end')
                    widget.insert(0, field_values.get(field))


    def get_all_entries(self):
        self.value_list = {}
        for field_label, entry_widget in self.entry_dictionary.items():

            # Handle different widget types
            if isinstance(entry_widget, tb.DateEntry):
                value = entry_widget.entry.get()  # Use .entry.get() for DateEntry
                self.value_list[field_label] = datetime.strptime(value, '%m/%d/%Y')
            elif isinstance(entry_widget, tb.Text):
                value = entry_widget.get("1.0", "end-1c")  # Special handling for Text widgets
                self.value_list[field_label] = value
            elif hasattr(entry_widget, 'color'):  # Check if it's a color picker button
                self.value_list[field_label] = entry_widget.color  # Get the color value directly from the button
            elif hasattr(entry_widget, 'unit_choices'):
                selected_name = entry_widget.get()
                # Find the corresponding unit_ID for the selected name
                unit_id = None
                for id_str, name in entry_widget.unit_choices:
                    if name == selected_name:
                        unit_id = int(id_str)
                        break
                self.value_list[field_label] = Unit.get_by_id(unit_id) if unit_id else None

            elif hasattr(entry_widget, 'objective_choices'):
                selected_name = entry_widget.get()
                # Find the corresponding objective_ID for the selected name
                objective_id = None
                for id_str, name in entry_widget.objective_choices:
                    if name == selected_name:
                        objective_id = int(id_str)
                        break
                self.value_list[field_label] = Objective.get_by_id(objective_id) if objective_id else None

        else:
            value = entry_widget.get()  # Regular Entry widgets
            self.value_list[field_label] = value

        return self.value_list


    def validate_and_collect_form_values(self) -> dict or None:
        # validates the form using the base class validator and return a dictionary of fields and values
        if self.validate_form():
            self.value_list = self.get_all_entries()
            return self.value_list
        else:
            return None
