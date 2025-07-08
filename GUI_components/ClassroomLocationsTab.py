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

    TREE_COLUMNS = [('ID', 'classroom_location_ID', 0),
                    ('Name', 'classroom_location_name', 50),
                    ('Description', 'classroom_location_description',100),
                    ('Label', 'classroom_location_label',100),
                    ('Color','classroom_location_label_color',50)]

    CSV_HEADERS = ['classroom_location_name', 'classroom_location_description', 'classroom_location_label','classroom_location_label_size',
                   'classroom_location_label_color']


def __init__(self, notebook):
    super().__init__(notebook)
    self._setup_variables()
    self._setup_ui()


def _setup_variables(self):
    pass


def _setup_ui(self):
    # """Setup UI components#"""
    self.create_header("ClassroomLocations")
    self._create_treeviews()
    self._create_forms()


def _create_treeviews(self):
    # """Create and configure treeviews"""
    self.classroom_locations_tree = self._create_base_treeview(
        self.TREE_COLUMNS,
        double_click_handler=self._load_edit_state
    )
    self._reload_classroom_locations_tree()


def _create_forms(self):
    # setup form buttons,
    # text, style, row, col, colspan, command
    self.edit_buttons = [
        ("Update", "success", 5, 0, 2, self._submit_edited_classroom_location),
        ("Delete", "danger", 5, 2, 1, self._delete_selected_classroom_location),
        ("Cancel", "warning", 5, 3, 2, self._load_base_state)
    ]

    self.main_buttons = [
        ("Upload CSV", "default outline", 5, 0, 2, self.upload_classroom_location_csv),
        ("Download Template", "info outline", 5, 2, 1,
         lambda: self.generate_csv_template(self.CSV_HEADERS, 'classroom_location_template')),
        ("Add ClassroomLocation", "danger", 5, 4, 2, self._load_new_classroom_location_state)
    ]

    self.new_buttons = [
        ("Create", "success", 5, 0, 2, self._create_new_classroom_location_from_form),
        ("Cancel", "warning", 5, 3, 2, self._load_base_state)
    ]

    # """Create form panels#"""
    self.main_button_panel = BaseForm(self, self.CLASSROOM_LOCATION_DISPLAY_FIELDS)
    self.main_button_panel.grid(pady=20)
    self.create_buttons(self.main_button_panel, self.main_buttons)

    self.new_classroom_location_form = BaseForm(self, self.CLASSROOM_LOCATION_DISPLAY_FIELDS)
    self.new_classroom_location_form.show_standard_fields(4)
    self.create_buttons(self.new_classroom_location_form, self.new_buttons)

    self.edit_classroom_location_form = BaseForm(self, self.CLASSROOM_LOCATION_DISPLAY_FIELDS)
    self.edit_classroom_location_form.show_standard_fields(4)
    self.create_buttons(self.edit_classroom_location_form, self.edit_buttons)


def _load_new_classroom_location_state(self):
    self.hide_forms()
    self.new_classroom_location_form.clear_form()
    self.new_classroom_location_form.grid()


def _load_base_state(self):
    self.hide_forms()
    self.new_classroom_location_form.clear_form()
    self.edit_classroom_location_form.clear_form()
    self.main_button_panel.grid()


def _load_edit_state(self):
    # validation should be redundant here as it should only be called as an action
    try:
        if not self.classroom_locations_tree.validate_item_is_selected():
            return
    except Exception as e:
        pass

    field_values = self.classroom_locations_tree._create_dictionary_from_selected_tree_item_and_values(self.TREE_COLUMNS)
    self.edit_classroom_location_form.populate_fields(field_values)
    self.hide_forms()
    self.edit_classroom_location_form.grid()


def upload_classroom_location_csv(self):
    # """Handle ClassroomLocation CSV file upload - done in base tab"""
    self.upload_csv(self.CSV_HEADERS, "ClassroomLocations imported successfully")
    self._reload_classroom_locations_tree()


def _process_row(self, row):
    # all in this world this method does is call the specific create from dictionary method for the class and then persist
    # at this point there should have been like 7 different error checks on the types, and the class method will catch anything else
    # so we are not going to do anything beyond a basic try/catch validation

    try:
        classroom_location = ClassroomLocation.ClassroomLocation.create_from_dict(row)

        classroom_location.add_new_classroom_location(session)
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid data in CSV: {str(e)}")


def _reload_classroom_locations_tree(self):
    # this should be the only place where we have a query object for this tree or anything dealing with it
    self.classroom_locations_tree.reload_tree(ClassroomLocation.ClassroomLocation.get_all_classroom_locations_by_sequence(), self.TREE_COLUMNS)


def _submit_edited_classroom_location(self):
    # """Submit edited classroom_location data#"""

    try:
        classroom_location = self.get_selected_classroom_location()

        if classroom_location:
            self._modify_classroom_location_from_form()
            self._reload_classroom_locations_tree()
            self._load_base_state()
        else:
            self.show_error("ClassroomLocation not found in database")
    except Exception as e:
        self.show_error(f"Failed to update classroom_location: {str(e)}")


def _modify_classroom_location_from_form(self):
    # """Update classroom_location with form values#"""
    form_values = self.edit_classroom_location_form.validate_and_collect_form_values()
    try:
        classroom_location = ClassroomLocation.ClassroomLocation.create_from_dict(form_values)
        classroom_location.classroom_location_ID = self.classroom_locations_tree.item(self.classroom_locations_tree.selection()[0])['values'][0]
        classroom_location.update_classroom_location(session)
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid data, the classroom_location was not updated: {str(e)}")


def _create_new_classroom_location_from_form(self):
    # """Create new classroom_location from form data#"""
    try:
        values = self.new_classroom_location_form.validate_and_collect_form_values()
        if values:
            ClassroomLocation.ClassroomLocation.create_from_dict(values).add_new_classroom_location(session)
            self._reload_classroom_locations_tree()
            self._load_base_state()
    except Exception as e:
        self.show_error(f"Failed to update classroom_location: {str(e)}")


def _delete_selected_classroom_location(self):
    # """Delete selected classroom_location#"""

    if self.confirm_delete(f"Are you sure you want to delete selected classroom_location'?"):
        try:
            classroom_location = self.get_selected_classroom_location()
            if classroom_location:
                classroom_location.delete_classroom_location(session)
                self._reload_classroom_locations_tree()
                self._load_base_state()

        except Exception as e:
            self.show_error(f"Failed to delete classroom_location: {str(e)}")


def get_selected_classroom_location(self) -> ClassroomLocation:
    if not self.classroom_locations_tree.validate_item_is_selected():
        return None

    try:
        selected = self.classroom_locations_tree.selection()[0]
        values = self.classroom_locations_tree.item(selected)['values']
        classroom_location = ClassroomLocation.ClassroomLocation.get_classroom_location_by_ID(values[0])
        if classroom_location:
            return classroom_location
        else:
            self.show_error("ClassroomLocation not found in database")
            return None
    except Exception as e:
        self.show_error(f"Failed to delete classroom_location: {str(e)}")
