import csv
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from datetime import datetime

import Persistance
from Model import ClassroomLocation
from GUI_components.BaseTreeView import BaseTreeView
from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTab import BaseTab


class ClassroomLocationTab(BaseTab):
    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    #(display label, field label, display type)
    CLASSROOM_LOCATION_FIELDS = [
        ('Name', 'classroom_location_name', 'string(10,50)', []),
        ('Description', 'classroom_location_description', 'text(15,5,1000)', []),
        ('Label', 'classroom_location_label', 'string(10,255)', []),
        ('Label Size', 'classroom_location_label_size', 'int(10,0,5)', []),
        ('Label Color', 'classroom_location_label_color', 'color', []),
        ]

    TREE_COLUMNS = [('Name', 'classroom_location_name'),
                    ('Description', 'classroom_location_description'),
                    ('Label', 'classroom_location_label'),
                    ('Color','classroom_location_label_color')]

    CSV_HEADERS = ['classroom_location_name', 'classroom_location_description', 'classroom_location_label','classroom_location_label_size',
                   'classroom_location_label_color']

    def __init__(self, notebook):
        super().__init__(notebook)
        self._setup_variables()
        self._setup_ui()

    def _setup_variables(self):
        #"""Initialize form variables#"""
        self.new_classroom_location_vars = self._create_classroom_location_variables()
        self.edit_classroom_location_vars = self._create_classroom_location_variables()

    def _create_classroom_location_variables(self):
        #"""Create StringVar variables for classroom_location forms#"""
        return {field: tb.StringVar(value="") for field in self.CSV_HEADERS}

    def _setup_ui(self):
        #"""Setup UI components#"""
        self._create_header()
        self._create_treeview()
        self._create_forms()
        self._setup_buttons()

    def _create_header(self):
        #"""Create header label#"""
        self.classroom_locations_label = tb.Label(self, text="ClassroomLocations", font=("Helvetica", 18))
        self.classroom_locations_label.grid(pady=20)

    def _create_treeview(self):
        #"""Create and configure treeview#"""
        self.classroom_locations_tree = BaseTreeView(self, self.TREE_COLUMNS)
        self.classroom_locations_tree.grid(padx=5, pady=15)
        self.classroom_locations_tree.bind('<Double-1>', lambda e: self.show_edit_classroom_location())
        self._reload_classroom_locations()

    def _create_forms(self):
        #"""Create form panels#"""
        self.main_button_panel = BaseForm(self)
        self.main_button_panel.grid(pady=20)

        self.new_classroom_location_form = BaseForm(self)
        self.new_classroom_location_form.show_standard_fields(self.CLASSROOM_LOCATION_FIELDS, 4)

        self.edit_classroom_location_form = BaseForm(self)
        self.edit_classroom_location_form.show_standard_fields(self.CLASSROOM_LOCATION_FIELDS, 4)

    def _setup_buttons(self):
        #"""Setup form buttons#"""
        self._create_main_buttons()
        self._create_new_classroom_location_buttons()
        self._create_edit_classroom_location_buttons()

    def _create_main_buttons(self):
        #"""Create main panel buttons#"""
        buttons = [
            ("Upload CSV", "default outline", self.upload_classroom_location_csv),
            ("Download Template", "info outline",
             lambda: self.generate_csv_template(self.CSV_HEADERS, 'classroom_location_template.csv')),
            ("Add ClassroomLocation", "danger", self.load_new_classroom_location_state)
        ]

        for text, style, command in buttons:
            btn = tb.Button(self.main_button_panel, text=text, bootstyle=style, command=command)
            btn.grid(pady=20)

    def load_new_classroom_location_state(self):
        self.swap_form_visibility(self.main_button_panel, self.new_classroom_location_form)
        self.new_classroom_location_form.clear_form()

    def _create_new_classroom_location_buttons(self):
        #"""Create new classroom_location form buttons#"""
        submit_btn = tb.Button(self.new_classroom_location_form, text="Create", bootstyle="success",
                               command=lambda: self.new_classroom_location_form.validate_and_collect_form_values(self.create_new_classroom_location()))
        submit_btn.grid(row=4, column=0, columnspan=5, pady=20)

        cancel_btn = tb.Button(self.new_classroom_location_form, text="Cancel", bootstyle="danger",
                               command=lambda: self.swap_form_visibility(self.new_classroom_location_form, self.main_button_panel))
        cancel_btn.grid(row=4, column=1, columnspan=5, pady=20)

    def _create_edit_classroom_location_buttons(self):
        #"""Create edit classroom_location form buttons#"""
        buttons = [
            ("Update", "success", 0, 2, self.submit_edit_classroom_location),
            ("Delete", "danger", 2, 1, self.delete_classroom_location),
            ("Cancel", "warning", 3, 2,
             lambda: self.swap_form_visibility(self.edit_classroom_location_form, self.main_button_panel))
        ]

        for text, style, col, colspan, command in buttons:
            btn = tb.Button(self.edit_classroom_location_form, text=text, bootstyle=style, command=command)
            btn.grid(row=4, column=col, columnspan=colspan, pady=20)

    def upload_classroom_location_csv(self):
        #"""Handle CSV file upload#"""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            self._process_csv_file(file_path)
            self.show_success("ClassroomLocations imported successfully")
        except Exception as e:
            self.show_error(f"Failed to read CSV file: {str(e)}")
        finally:
            self._reload_classroom_locations()

    def _process_csv_file(self, file_path):
        #"""Process uploaded CSV file#"""
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            first_row = next(csv_reader)

            if first_row != self.CSV_HEADERS:
                self._process_classroom_location_row(first_row)

            for row in csv_reader:
                self._process_classroom_location_row(row)

    def _process_classroom_location_row(self, row):
        #"""Process single CSV row into ClassroomLocation object#"""
        try:
            classroom_location = ClassroomLocation.ClassroomLocation(
                row[0],
                row[1]
             )
            classroom_location.add_classroom_location()
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data in CSV: {str(e)}")

    def create_new_classroom_location(self):
        #"""Create new classroom_location from form data#"""
        values = self.new_classroom_location_form.validate_and_collect_form_values(self.main_button_panel)
        if values:
            ClassroomLocation.ClassroomLocation(
                values.get('classroom_location_name'),
                values.get('classroom_location_description'),
               ).add_classroom_location()
            self._reload_classroom_locations()

    def show_edit_classroom_location(self):
        #"""Display edit form for selected classroom_location#"""
        if not self.classroom_locations_tree.selection():
            return

        selected = self.classroom_locations_tree.selection()[0]
        values = self.classroom_locations_tree.item(selected)['values']

        self.hide_forms()
        self.edit_classroom_location_form.grid()

        field_values = self._create_field_values_dict(values)
        self.edit_classroom_location_form.populate_fields(field_values)

    def _create_field_values_dict(self, values):
        #"""Create dictionary of field values from selected classroom_location#"""
        return {
            'classroom_location_name': values[0],
            'classroom_location_description': values[1]
        }

    def hide_forms(self):
        # """Hide all form components#"""
        self.main_button_panel.grid_remove()
        self.new_classroom_location_form.grid_remove()
        self.edit_classroom_location_form.grid_remove()

    def submit_edit_classroom_location(self):
        #"""Submit edited classroom_location data#"""
        if not self._validate_edit_classroom_location():
            return

        selected = self.classroom_locations_tree.selection()[0]
        values = self.classroom_locations_tree.item(selected)['values']

        try:
            classroom_location = self._get_classroom_location_by_name(values[0])
            if classroom_location:
                self._update_classroom_location(classroom_location)
                self._reload_classroom_locations()
                self.swap_form_visibility(self.edit_classroom_location_form, self.main_button_panel)
            else:
                self.show_error("ClassroomLocation not found in database")
        except Exception as e:
            self.show_error(f"Failed to update classroom_location: {str(e)}")

    def _validate_edit_classroom_location(self):
        #"""Validate classroom_location selection for editing#"""
        if not self.classroom_locations_tree.selection():
            self.show_error("Please select a classroom_location to edit")
            return False
        return True

    def _get_classroom_location_by_name(self, name):
        #"""Retrieve classroom_location from database by name#"""
        return Persistance.session.query(ClassroomLocation.ClassroomLocation).filter_by(classroom_location_name=name).first()

    def _update_classroom_location(self, classroom_location):
        #"""Update classroom_location with form values#"""
        form_values = self.edit_classroom_location_form.get_all_entries()
        classroom_location.classroom_location_name = form_values.get('classroom_location_name')
        classroom_location.classroom_location_description = form_values.get('classroom_location_description')
        classroom_location.update_classroom_location()

    def delete_classroom_location(self):
        #"""Delete selected classroom_location#"""
        if not self._validate_edit_classroom_location():
            return

        selected = self.classroom_locations_tree.selection()[0]
        values = self.classroom_locations_tree.item(selected)['values']

        if self.confirm_delete(f"Are you sure you want to delete classroom_location '{values[0]}'?"):
            try:
                classroom_location = self._get_classroom_location_by_name(values[0])
                if classroom_location:
                    classroom_location.delete_classroom_location()
                    self._reload_classroom_locations()
                    self.swap_form_visibility(self.edit_classroom_location_form, self.main_button_panel)
                else:
                    self.show_error("ClassroomLocation not found in database")
            except Exception as e:
                self.show_error(f"Failed to delete classroom_location: {str(e)}")

    def _reload_classroom_locations(self):
        #"""Refresh classroom_locations display in treeview#"""
        self.classroom_locations_tree.delete(*self.classroom_locations_tree.get_children())
        classroom_locations = Persistance.session.query(ClassroomLocation.ClassroomLocation).order_by(ClassroomLocation.ClassroomLocation.classroom_location_name).all()

        for classroom_location in classroom_locations:
            self.classroom_locations_tree.insert('', 'end', values=self._format_classroom_location_values(classroom_location))

    def _format_classroom_location_values(self, classroom_location):
        #"""Format classroom_location values for display#"""
        return (
            classroom_location.classroom_location_name,
            classroom_location.classroom_location_description
            )
