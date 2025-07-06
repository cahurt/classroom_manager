import csv
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from datetime import datetime

import Persistance
from Model import Unit
from GUI_components.BaseTreeView import BaseTreeView
from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTab import BaseTab


class UnitTab(BaseTab):
    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    UNIT_FIELDS = [
        ('Name', 'unit_name', str),
        ('Sequence', 'sequence', int),
        ('Opening Date', 'opening_date', datetime),
        ('End Date', 'end_date', datetime),
        ('Closing Date', 'closing_date', datetime),
        ('Description', 'description', None)
    ]

    TREE_COLUMNS = ['unit_name', 'sequence', 'opening_date', 'end_date', 'closing_date', 'description']
    CSV_HEADERS = ['unit_name', 'sequence', 'opening_date', 'end_date', 'closing_date', 'description']

    def __init__(self, notebook):
        super().__init__(notebook)
        self._setup_variables()
        self._setup_ui()

    def _setup_variables(self):
        #"""Initialize form variables#"""
        self.new_unit_vars = self._create_unit_variables()
        self.edit_unit_vars = self._create_unit_variables()

    def _create_unit_variables(self):
        #"""Create StringVar variables for unit forms#"""
        return {field: tb.StringVar(value="") for field in
                ['name', 'sequence', 'opening_date', 'closing_date', 'end_date', 'description']}

    def _setup_ui(self):
        #"""Setup UI components#"""
        self._create_header()
        self._create_treeview()
        self._create_forms()
        self._setup_buttons()

    def _create_header(self):
        #"""Create header label#"""
        self.units_label = tb.Label(self, text="Units", font=("Helvetica", 18))
        self.units_label.grid(pady=20)

    def _create_treeview(self):
        #"""Create and configure treeview#"""
        self.units_tree = BaseTreeView(self, self.TREE_COLUMNS)
        self.units_tree.grid(padx=5, pady=15)
        self.units_tree.bind('<Double-1>', lambda e: self.show_edit_unit())
        self._reload_units()

    def _create_forms(self):
        #"""Create form panels#"""
        self.main_button_panel = BaseForm(self)
        self.main_button_panel.grid(pady=20)

        self.new_unit_form = BaseForm(self)
        self.new_unit_form.show_standard_fields(self.UNIT_FIELDS, 4)

        self.edit_unit_form = BaseForm(self)
        self.edit_unit_form.show_standard_fields(self.UNIT_FIELDS, 4)

    def _setup_buttons(self):
        #"""Setup form buttons#"""
        self._create_main_buttons()
        self._create_new_unit_buttons()
        self._create_edit_unit_buttons()

    def _create_main_buttons(self):
        #"""Create main panel buttons#"""
        buttons = [
            ("Upload CSV", "default outline", self.upload_unit_csv),
            ("Download Template", "info outline",
             lambda: self.generate_csv_template(self.CSV_HEADERS, 'unit_template.csv')),
            ("Add Unit", "danger", self.load_new_unit_state)
        ]

        for text, style, command in buttons:
            btn = tb.Button(self.main_button_panel, text=text, bootstyle=style, command=command)
            btn.grid(pady=20)

    def load_new_unit_state(self):
        self.swap_form_visibility(self.main_button_panel, self.new_unit_form)
        self.new_unit_form.clear_form()

    def _create_new_unit_buttons(self):
        #"""Create new unit form buttons#"""
        submit_btn = tb.Button(self.new_unit_form, text="Create", bootstyle="success",
                               command=lambda: self.new_unit_form.submit_form(self.create_new_unit()))
        submit_btn.grid(row=4, column=0, columnspan=5, pady=20)

        cancel_btn = tb.Button(self.new_unit_form, text="Cancel", bootstyle="danger",
                               command=lambda: self.swap_form_visibility(self.new_unit_form, self.main_button_panel))
        cancel_btn.grid(row=4, column=1, columnspan=5, pady=20)

    def _create_edit_unit_buttons(self):
        #"""Create edit unit form buttons#"""
        buttons = [
            ("Update", "success", 0, 2, self.submit_edit_unit),
            ("Delete", "danger", 2, 1, self.delete_unit),
            ("Cancel", "warning", 3, 2,
             lambda: self.swap_form_visibility(self.edit_unit_form, self.main_button_panel))
        ]

        for text, style, col, colspan, command in buttons:
            btn = tb.Button(self.edit_unit_form, text=text, bootstyle=style, command=command)
            btn.grid(row=4, column=col, columnspan=colspan, pady=20)

    def upload_unit_csv(self):
        #"""Handle CSV file upload#"""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            self._process_csv_file(file_path)
            self.show_success("Units imported successfully")
        except Exception as e:
            self.show_error(f"Failed to read CSV file: {str(e)}")
        finally:
            self._reload_units()

    def _process_csv_file(self, file_path):
        #"""Process uploaded CSV file#"""
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            first_row = next(csv_reader)

            if first_row != self.CSV_HEADERS:
                self._process_unit_row(first_row)

            for row in csv_reader:
                self._process_unit_row(row)

    def _process_unit_row(self, row):
        #"""Process single CSV row into Unit object#"""
        try:
            unit = Unit.Unit(
                row[0],
                int(row[1]),
                datetime.strptime(row[2], self.DATE_FORMAT),
                datetime.strptime(row[4], self.DATE_FORMAT),
                datetime.strptime(row[3], self.DATE_FORMAT),
                row[5]
            )
            unit.add_unit()
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data in CSV: {str(e)}")

    def create_new_unit(self):
        #"""Create new unit from form data#"""
        values = self.new_unit_form.submit_form(self.main_button_panel)
        if values:
            Unit.Unit(
                values.get('unit_name'),
                values.get('sequence'),
                values.get('opening_date'),
                values.get('closing_date'),
                values.get('end_date'),
                values.get('description')
            ).add_unit()
            self._reload_units()

    def show_edit_unit(self):
        #"""Display edit form for selected unit#"""
        if not self.units_tree.selection():
            return

        selected = self.units_tree.selection()[0]
        values = self.units_tree.item(selected)['values']

        self.hide_forms()
        self.edit_unit_form.grid()

        field_values = self._create_field_values_dict(values)
        self.edit_unit_form.populate_fields(field_values)

    def _create_field_values_dict(self, values):
        #"""Create dictionary of field values from selected unit#"""
        return {
            'unit_name': values[0],
            'sequence': values[1],
            'opening_date': values[2],
            'end_date': values[3],
            'closing_date': values[4],
            'description': values[5]
        }

    def hide_forms(self):
        # """Hide all form components#"""
        self.main_button_panel.grid_remove()
        self.new_unit_form.grid_remove()
        self.edit_unit_form.grid_remove()

    def submit_edit_unit(self):
        #"""Submit edited unit data#"""
        if not self._validate_edit_unit():
            return

        selected = self.units_tree.selection()[0]
        values = self.units_tree.item(selected)['values']

        try:
            unit = self._get_unit_by_sequence(values[1])
            if unit:
                self._update_unit(unit)
                self._reload_units()
                self.swap_form_visibility(self.edit_unit_form, self.main_button_panel)
            else:
                self.show_error("Unit not found in database")
        except Exception as e:
            self.show_error(f"Failed to update unit: {str(e)}")

    def _validate_edit_unit(self):
        #"""Validate unit selection for editing#"""
        if not self.units_tree.selection():
            self.show_error("Please select a unit to edit")
            return False
        return True

    def _get_unit_by_sequence(self, sequence):
        #"""Retrieve unit from database by sequence number#"""
        return Persistance.session.query(Unit.Unit).filter_by(unit_sequence=sequence).first()

    def _update_unit(self, unit):
        #"""Update unit with form values#"""
        form_values = self.edit_unit_form.get_all_entries()
        unit.unit_name = form_values.get('unit_name')
        unit.unit_sequence = form_values.get('sequence')
        unit.unit_opening_date = form_values.get('opening_date')
        unit.unit_closing_date = form_values.get('closing_date')
        unit.unit_end_date = form_values.get('end_date')
        unit.unit_description = form_values.get('description')
        unit.update_unit()

    def delete_unit(self):
        #"""Delete selected unit#"""
        if not self._validate_edit_unit():
            return

        selected = self.units_tree.selection()[0]
        values = self.units_tree.item(selected)['values']

        if self.confirm_delete(f"Are you sure you want to delete unit '{values[0]}'?"):
            try:
                unit = self._get_unit_by_sequence(values[1])
                if unit:
                    unit.delete_unit()
                    self._reload_units()
                    self.swap_form_visibility(self.edit_unit_form, self.main_button_panel)
                else:
                    self.show_error("Unit not found in database")
            except Exception as e:
                self.show_error(f"Failed to delete unit: {str(e)}")

    def _reload_units(self):
        #"""Refresh units display in treeview#"""
        self.units_tree.delete(*self.units_tree.get_children())
        units = Persistance.session.query(Unit.Unit).order_by(Unit.Unit.unit_sequence).all()

        for unit in units:
            self.units_tree.insert('', 'end', values=self._format_unit_values(unit))

    def _format_unit_values(self, unit):
        #"""Format unit values for display#"""
        return (
            unit.unit_name,
            unit.unit_sequence,
            unit.unit_opening_date.strftime(self.DISPLAY_DATE_FORMAT),
            unit.unit_end_date.strftime(self.DISPLAY_DATE_FORMAT),
            unit.unit_closing_date.strftime(self.DISPLAY_DATE_FORMAT),
            unit.unit_description
        )
