import csv
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from datetime import datetime

import Persistance
from Model import Hour
from GUI_components.BaseTreeView import BaseTreeView
from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTab import BaseTab


class HourTab(BaseTab):
    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    # (display label, field label, display type)
    HOUR_FIELDS = [
        ('Name', 'name', 'string(10,50)', []),
        ('Start Time', 'start_time', 'time', []),
        ('End Time', 'end_time', 'time', []),
        ('Assembly Start Time', 'assembly_start_time', 'time', []),
        ('Assembly End Time', 'assembly_end_time', 'time', []),
        ('Start Date', 'start_date', 'date', []),
        ('End Date', 'end_date', 'date', [])

    ]

    TREE_COLUMNS = [('ID', 'hourID', 0),
                    ('Name', 'name', 250),
                    ('Start Time', 'start_time', 50),
                    ('End Time', 'end_time', 50),
                    ('Start Date', 'start_date', 50),
                    ('End Date', 'end_date', 50)
                    ]

    CSV_HEADERS = ['name', 'description', 'hours_required']

    def __init__(self, notebook):
        super().__init__(notebook)
        self._setup_variables()
        self._setup_ui()

    def _setup_variables(self):
        pass

    # *************************************************************

    #    ----- All of this is basic UI setup, no logic code shall go here
    #    ------ I have spoken

    # **************************************************************

    def _setup_ui(self):
        # """Setup UI components#"""
        self.create_header("Hours")

        self._create_treeviews()
        self._create_forms()

    def _create_treeviews(self):
        # """Create and configure treeviews"""
        self.hours_tree = self._create_base_treeview(
            self.TREE_COLUMNS,
            double_click_handler=self._load_edit_state
        )
        self._reload_hours_tree()

    def _create_forms(self):
        # setup form buttons,
        # text, style, row, col, colspan, command
        self.edit_buttons = [
            ("Update", "success", 5, 0, 2, self._submit_edited_hour),
            ("Delete", "danger", 5, 2, 1, self._delete_selected_hour),
            ("Cancel", "warning", 5, 3, 2, self._load_base_state)
        ]

        self.main_buttons = [
            ("Upload CSV", "default outline", 5, 0, 2, self.upload_hour_csv),
            ("Download Template", "info outline", 5, 2, 1,
             lambda: self.generate_csv_template(self.CSV_HEADERS, 'hour_template')),
            ("Add Hour", "danger", 5, 4, 2, self._load_new_hour_state)
        ]

        self.new_buttons = [
            ("Create", "success", 5, 0, 2, self._create_new_hour_from_form),
            ("Cancel", "warning", 5, 3, 2, self._load_base_state)
        ]

        # """Create form panels#"""
        self.main_button_panel = BaseForm(self, self.HOUR_FIELDS)
        self.main_button_panel.grid(pady=20)
        self.main_button_panel.create_buttons(self.main_buttons)

        self.new_hour_form = BaseForm(self, self.HOUR_FIELDS)
        self.new_hour_form.show_standard_fields(4)
        self.new_hour_form.create_buttons(self.new_buttons)

        self.edit_hour_form = BaseForm(self, self.HOUR_FIELDS)
        self.edit_hour_form.show_standard_fields(4)
        self.edit_hour_form.create_buttons(self.edit_buttons)

    def _load_new_hour_state(self):
        self.hide_forms()
        self.new_hour_form.clear_form()
        self.new_hour_form.grid()

    def _load_base_state(self):
        self.hide_forms()
        self.new_hour_form.clear_form()
        self.edit_hour_form.clear_form()
        self.main_button_panel.grid()

    def _load_edit_state(self):
        # validation should be redundant here as it should only be called as an action
        try:
            if not self.hours_tree.validate_item_is_selected():
                return
        except Exception as e:
            pass

        field_values = self.hours_tree._create_dictionary_from_selected_tree_item_and_values(
            self.TREE_COLUMNS)
        self.edit_hour_form.populate_fields(field_values)
        self.hide_forms()
        self.edit_hour_form.grid()

    def upload_hour_csv(self):
        # """Handle Hour CSV file upload - done in base tab"""
        self.upload_csv(self.CSV_HEADERS, "Classroom Locations imported successfully")
        self._reload_hours_tree()

    # ************************************************************

    #    ----- Hour-specific Processing, no UI elements here, just all back-end stuff
    #    ------ I have spoken

    # **************************************************************

    def _reload_hours_tree(self):
        # this should be the only place where we have a query object for this tree or anything dealing with it
        self.hours_tree.reload_tree(Hour.get_all_order_by_start_time(),
                                         self.TREE_COLUMNS)

    def _create_hour_from_dictionary(self, dictionary) -> Hour:
        hour = None
        # try to get an existing hour

        if 'hour_ID' in dictionary:

            hour = Hour.get_by_id(dictionary['hour_ID'])

        # if none exists: make a new one
        if not hour:
            hour = Hour(
                name=dictionary['name'],
                start_time = dictionary['start_time'],
                end_time = dictionary['end_time'],
                start_date = dictionary['start_date'],
                end_date = dictionary['end_date']
            )
            if 'hour_ID' in dictionary:
                hour.hour_ID = dictionary['hour_ID']

        # if one does, we set values directly
        else:

            hour.name = dictionary['name']
            hour.start_time = dictionary['start_time']
            hour.end_time = dictionary['end_time']
            hour.start_date = dictionary['start_date']
            hour.end_date = dictionary['end_date']

        return hour

    def _process_row(self, dictionary_from_row: dict):
        try:
            hour = self._create_hour_from_dictionary(dictionary_from_row)

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data in CSV: {str(e)}")

        return hour

    def _save_CSV_row(self, hour: Hour):
        """ we use a separate function to save so that we can process the CSV as a whole"""
        hour.save()

    def _create_new_hour_from_form(self):
        # """Create new hour from form data#"""
    #    try:
            values = self.new_hour_form.validate_and_collect_form_values()
            if values:
                self.hour = self._create_hour_from_dictionary(values)
                self.hour.save()
                self._reload_hours_tree()
                self._load_base_state()
      #  except Exception as e:
       #     self.show_error(f"Failed to update hour: {str(e)}")

    def _submit_edited_hour(self):
        # """Submit edited hour data#"""

        # try:
        form_values = self.edit_hour_form.validate_and_collect_form_values()
        existing_hour = self.get_selected_hour()
        form_values['hour_ID'] = existing_hour.hour_ID
        edited_hour = self._create_hour_from_dictionary(form_values)

        if edited_hour and existing_hour:
            edited_hour.save()
            self._reload_hours_tree()
            self._load_base_state()
        else:
            self.show_error("Hour not found in database")

    # except Exception as e:
    # self.show_error(f"Failed to update hour: {str(e)}")

    def _delete_selected_hour(self):
        # """Delete selected hour#"""

        if self.confirm_delete(f"Are you sure you want to delete selected hour'?"):
            try:
                hour = self.get_selected_hour()
                if hour:
                    hour.delete()
                    self._reload_hours_tree()
                    self._load_base_state()

            except Exception as e:
                self.show_error(f"Failed to delete hour: {str(e)}")

    def get_selected_hour(self) -> Hour:
        if not self.hours_tree.validate_item_is_selected():
            return None

        try:
            selected = self.hours_tree.selection()[0]
            values = self.hours_tree.item(selected)['values']
            hour = Hour.get_by_id(values[0])
            if hour:
                return hour
            else:
                self.show_error("Hour not found in database")
                return None
        except Exception as e:
            self.show_error(f"Failed to select hour: {str(e)}")
