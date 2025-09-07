import csv
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from datetime import datetime

import Persistance
from Model.Objective import Objective
from GUI_components.BaseTreeView import BaseTreeView
from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTab import BaseTab


class ObjectiveTab(BaseTab):
    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    # (display label, field label, display type)
    OBJECTIVE_FIELDS = [
        ('Name', 'name', 'string(10,50)', []),
        ('Description', 'description', 'text(15,5,1000)', []),
        ('Hours Req', 'hours_required', 'int(10,0,50)', [])

    ]

    TREE_COLUMNS = [('ID', 'objective_ID', 0),
                    ('Name', 'name', 250),
                    ('Description', 'description', 100),
                    ('Hours Req', 'hours_required', 50)
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
        self.create_header("Objectives")

        self._create_treeviews()
        self._create_forms()


    def _create_treeviews(self):
        # """Create and configure treeviews"""
        self.objectives_tree = self._create_base_treeview(
            self.TREE_COLUMNS,
            double_click_handler=self._load_edit_state
        )
        self._reload_objectives_tree()


    def _create_forms(self):
        # setup form buttons,
        # text, style, row, col, colspan, command
        self.edit_buttons = [
            ("Update", "success", 5, 0, 2, self._submit_edited_objective),
            ("Delete", "danger", 5, 2, 1, self._delete_selected_objective),
            ("Cancel", "warning", 5, 3, 2, self._load_base_state)
        ]

        self.main_buttons = [
            ("Upload CSV", "default outline", 5, 0, 2, self.upload_objective_csv),
            ("Download Template", "info outline", 5, 2, 1,
             lambda: self.generate_csv_template(self.CSV_HEADERS, 'objective_template')),
            ("Add Objective", "danger", 5, 4, 2, self._load_new_objective_state)
        ]

        self.new_buttons = [
            ("Create", "success", 5, 0, 2, self._create_new_objective_from_form),
            ("Cancel", "warning", 5, 3, 2, self._load_base_state)
        ]

        # """Create form panels#"""
        self.main_button_panel = BaseForm(self, self.OBJECTIVE_FIELDS)
        self.main_button_panel.grid(pady=20)
        self.main_button_panel.create_buttons(self.main_buttons)

        self.new_objective_form = BaseForm(self, self.OBJECTIVE_FIELDS)
        self.new_objective_form.show_standard_fields(4)
        self.new_objective_form.create_buttons(self.new_buttons)

        self.edit_objective_form = BaseForm(self, self.OBJECTIVE_FIELDS)
        self.edit_objective_form.show_standard_fields(4)
        self.edit_objective_form.create_buttons(self.edit_buttons)


    def _load_new_objective_state(self):
        self.hide_forms()
        self.new_objective_form.clear_form()
        self.new_objective_form.grid()

    def _load_base_state(self):
        self.hide_forms()
        self.new_objective_form.clear_form()
        self.edit_objective_form.clear_form()
        self.main_button_panel.grid()

    def _load_edit_state(self):
        # validation should be redundant here as it should only be called as an action
        try:
            if not self.objectives_tree.validate_item_is_selected():
                return
        except Exception as e:
            pass

        field_values = self.objectives_tree._create_dictionary_from_selected_tree_item_and_values(
            self.TREE_COLUMNS)
        self.edit_objective_form.populate_fields(field_values)
        self.hide_forms()
        self.edit_objective_form.grid()

    def upload_objective_csv(self):
        # """Handle Objective CSV file upload - done in base tab"""
        self.upload_csv(self.CSV_HEADERS, "Classroom Locations imported successfully")
        self._reload_objectives_tree()

    # ************************************************************

    #    ----- Objective-specific Processing, no UI elements here, just all back-end stuff
    #    ------ I have spoken

    # **************************************************************

    def _reload_objectives_tree(self):
        # this should be the only place where we have a query object for this tree or anything dealing with it
        self.objectives_tree.reload_tree(Objective.get_all_order_by_name(),
                                                  self.TREE_COLUMNS)

    def _create_objective_from_dictionary(self, dictionary) -> Objective:
        objective = None
        # try to get an existing objective

        if 'objective_ID' in dictionary:
            objective = Objective.get_by_id(dictionary['objective_ID'])

        # if none exists: make a new one
        if not objective:
            objective = Objective(
                name=dictionary['name'],
                description=dictionary['description'],
                hours_required=int(dictionary['hours_required']),
                ignore_validation=True
            )
            if 'objective_ID' in dictionary:
                objective.objective_ID = dictionary['objective_ID']

        # if one does, we set values directly
        else:

            objective.name = dictionary['name']
            objective.description = dictionary['description']
            objective.hours_required = int(dictionary['hours_required'])


        return objective

    def _process_row(self, dictionary_from_row: dict):
        try:
            objective = self._create_objective_from_dictionary(dictionary_from_row)

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data in CSV: {str(e)}")

        return objective

    def _save_CSV_row(self, objective: Objective):
        """ we use a separate function to save so that we can process the CSV as a whole"""
        objective.save()

    def _create_new_objective_from_form(self):
        # """Create new objective from form data#"""
        try:
            values = self.new_objective_form.validate_and_collect_form_values()
            if values:
                self.objective = self._create_objective_from_dictionary(values)
                self.objective.save()
                self._reload_objectives_tree()
                self._load_base_state()
        except Exception as e:
            self.show_error(f"Failed to update objective: {str(e)}")

    def _submit_edited_objective(self):
        # """Submit edited objective data#"""

        #try:
            form_values = self.edit_objective_form.validate_and_collect_form_values()
            existing_objective = self.get_selected_objective()
            form_values['objective_ID'] = existing_objective.objective_ID
            edited_objective = self._create_objective_from_dictionary(form_values)

            if edited_objective and existing_objective:
                edited_objective.save()
                self._reload_objectives_tree()
                self._load_base_state()
            else:
                self.show_error("Objective not found in database")
        #except Exception as e:
            #self.show_error(f"Failed to update objective: {str(e)}")

    def _delete_selected_objective(self):
        # """Delete selected objective#"""

        if self.confirm_delete(f"Are you sure you want to delete selected objective'?"):
            try:
                objective = self.get_selected_objective()
                if objective:
                    objective.delete()
                    self._reload_objectives_tree()
                    self._load_base_state()

            except Exception as e:
                self.show_error(f"Failed to delete objective: {str(e)}")

    def get_selected_objective(self) -> Objective:
        if not self.objectives_tree.validate_item_is_selected():
            return None

        try:
            selected = self.objectives_tree.selection()[0]
            values = self.objectives_tree.item(selected)['values']
            objective = Objective.get_by_id(values[0])
            if objective:
                return objective
            else:
                self.show_error("Objective not found in database")
                return None
        except Exception as e:
            self.show_error(f"Failed to select objective: {str(e)}")
