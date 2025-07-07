import csv
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from datetime import datetime

from Persistance import session
from Model import Unit
from GUI_components.BaseTreeView import BaseTreeView
from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTab import BaseTab


class UnitTab(BaseTab):
    UNIT_DISPLAY_FIELDS = [
        ('Name', 'unit_name', 'string(50,255)', []),
        ('Sequence', 'unit_sequence', 'int(10,0,30)', []),
        ('Opening Date', 'unit_opening_date', 'date', []),
        ('End Date', 'unit_end_date', 'date', []),
        ('Closing Date', 'unit_closing_date', 'date', []),
        ('Description', 'unit_description', 'text(15,5, 1000)', [])
    ]

    TREE_COLUMNS = [('ID', 'unit_ID', 0),
                    ('Name', 'unit_name', 200),
                    ('Sequence', 'unit_sequence', 50),
                    ('Opening Date', 'unit_opening_date', 125),
                    ('End Date', 'unit_end_date', 125),
                    ('Closing Date', 'unit_closing_date', 125),
                    ('Description', 'unit_description', 150)

                    ]

    CSV_HEADERS = ['unit_name', 'unit_sequence', 'unit_opening_date', 'unit_end_date', 'unit_closing_date', 'unit_description']

    def __init__(self, notebook):
        super().__init__(notebook)
        self._setup_variables()
        self._setup_ui()

    def _setup_variables(self):

        pass

    def _setup_ui(self):
        # """Setup UI components#"""
        self.create_header("Units")
        self._create_treeviews()
        self._create_forms()

    def _create_treeviews(self):
        # """Create and configure treeviews"""
        self.units_tree = self._create_base_treeview(
            self.TREE_COLUMNS,
            double_click_handler=self._load_edit_state
        )
        self._reload_units_tree()

    def _create_forms(self):

        # setup form buttons,
        # text, style, row, col, colspan, command
        self.edit_buttons = [
            ("Update", "success", 5, 0, 2, self._submit_edited_unit),
            ("Delete", "danger", 5, 2, 1, self._delete_selected_unit),
            ("Cancel", "warning", 5, 3, 2, self._load_base_state)
        ]

        self.main_buttons = [
            ("Upload CSV", "default outline", 5, 0, 2, self.upload_unit_csv),
            ("Download Template", "info outline", 5, 2, 1,
             lambda: self.generate_csv_template(self.CSV_HEADERS, 'unit_template')),
            ("Add Unit", "danger", 5, 4, 2, self._load_new_unit_state)
        ]

        self.new_buttons = [
            ("Create", "success", 5, 0, 2, self._create_new_unit_from_form),
            ("Cancel", "warning", 5, 3, 2, self._load_base_state)
        ]

        # """Create form panels#"""
        self.main_button_panel = BaseForm(self, self.UNIT_DISPLAY_FIELDS)
        self.main_button_panel.grid(pady=20)
        self.create_buttons(self.main_button_panel, self.main_buttons)

        self.new_unit_form = BaseForm(self, self.UNIT_DISPLAY_FIELDS)
        self.new_unit_form.show_standard_fields(4)
        self.create_buttons(self.new_unit_form, self.new_buttons)

        self.edit_unit_form = BaseForm(self, self.UNIT_DISPLAY_FIELDS)
        self.edit_unit_form.show_standard_fields(4)
        self.create_buttons(self.edit_unit_form, self.edit_buttons)

    def _load_new_unit_state(self):
        self.hide_forms()
        self.new_unit_form.clear_form()
        self.new_unit_form.grid()

    def _load_base_state(self):

        self.hide_forms()
        self.new_unit_form.clear_form()
        self.edit_unit_form.clear_form()
        self.main_button_panel.grid()

    def _load_edit_state(self):

        #validation should be redundant here as it should only be called as an action
        try:
            if not self.units_tree.validate_item_is_selected():
                return
        except Exception as e:
            pass

        field_values = self.units_tree._create_dictionary_from_selected_tree_item_and_values(self.TREE_COLUMNS)
        self.edit_unit_form.populate_fields(field_values)
        self.hide_forms()
        self.edit_unit_form.grid()

    def upload_unit_csv(self):
        # """Handle Unit CSV file upload - done in base tab"""
        self.upload_csv(self.CSV_HEADERS,"Units imported successfully")
        self._reload_units_tree()

    def _process_row(self, row):
        # all in this world this method does is call the specific create from dictionary method for the class and then persist
        # at this point there should have been like 7 different error checks on the types, and the class method will catch anything else
        # so we are not going to do anything beyond a basic try/catch validation

        try:
            unit = Unit.Unit.create_from_dict(row)

            unit.add_new_unit(session)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data in CSV: {str(e)}")

    def _reload_units_tree(self):
        # this should be the only place where we have a query object for this tree or anything dealing with it
        self.units_tree.reload_tree(Unit.Unit.get_all_units_by_sequence(), self.TREE_COLUMNS)

    def _submit_edited_unit(self):
        # """Submit edited unit data#"""

        try:
            unit = self.get_selected_unit()

            if unit:
                self._modify_unit_from_form()
                self._reload_units_tree()
                self._load_base_state()
            else:
                self.show_error("Unit not found in database")
        except Exception as e:
            self.show_error(f"Failed to update unit: {str(e)}")

    def _modify_unit_from_form(self):
        # """Update unit with form values#"""
        form_values = self.edit_unit_form.validate_and_collect_form_values()
        try:
            unit = Unit.Unit.create_from_dict(form_values)
            unit.unit_ID = self.units_tree.item(self.units_tree.selection()[0])['values'][0]
            unit.update_unit(session)
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data, the unit was not updated: {str(e)}")

    def _create_new_unit_from_form(self):
        # """Create new unit from form data#"""
        try:
            values = self.new_unit_form.validate_and_collect_form_values()
            if values:
                Unit.Unit.create_from_dict(values).add_new_unit(session)
                self._reload_units_tree()
                self._load_base_state()
        except Exception as e:
            self.show_error(f"Failed to update unit: {str(e)}")

    def _delete_selected_unit(self):
        # """Delete selected unit#"""

        if self.confirm_delete(f"Are you sure you want to delete selected unit'?"):
            try:
                unit = self.get_selected_unit()
                if unit:
                    unit.delete_unit(session)
                    self._reload_units_tree()
                    self._load_base_state()

            except Exception as e:
                self.show_error(f"Failed to delete unit: {str(e)}")

    def get_selected_unit(self) -> Unit:

        if not self.units_tree.validate_item_is_selected():
            return None

        try:
            selected = self.units_tree.selection()[0]
            values = self.units_tree.item(selected)['values']
            unit = Unit.Unit.get_unit_by_ID(values[0])
            if unit:
                return unit
            else:
                self.show_error("Unit not found in database")
                return None
        except Exception as e:
            self.show_error(f"Failed to delete unit: {str(e)}")
