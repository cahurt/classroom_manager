import csv
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from datetime import datetime

import Persistance
from Model import Project, Unit
from GUI_components.BaseTreeView import BaseTreeView
from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTab import BaseTab



class ProjectTab(BaseTab):
    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    # (display label, field label, display type)
    PROJECT_FIELDS = [
        ('Name', 'name', 'string(10,50)'),
        ('Description', 'description', 'text(15,5,1000)'),
        ('Opening Date', 'open_date', 'date'),
        ('Closing Date', 'close_date', 'date'),
        ('Days Allowed', 'days_allowed', 'int(10,0,20)'),
        ('Seats', 'seats', 'int(10,0,20)'),
        ('Min Group Size', 'minimum_group_size', 'int(10,0,20)'),
        ('Max Group Size', 'maximum_group_size', 'int(10,0,20)'),
        ('Sub Eligible', 'sub_eligible', 'bool'),
        ('Unit', 'unit', 'unit_dropdown'),
        ('Objective', 'objective', 'objective_dropdown')
    ]

    TREE_COLUMNS = [('ID', 'project_ID', 0),
                    ('Name', 'name', 250),
                    ('Description', 'description', 100),
                    ('Opening Date', 'open_date', 50),
                    ('Closing Date', 'close_date', 50)
                    ]

    CSV_HEADERS = ['name', 'description', 'open_date', 'close_date', 'days_allowed', 'seats',
                   'minimum_group_size', 'maximum_group_size', 'sub_eligible']


    def __init__(self, notebook):
        super().__init__(notebook)
        self._setup_variables()
        self._setup_ui()
        self._setup_variables()

    def _setup_variables(self):
        self.units = Unit.get_all_order_by_sequence()

    # *************************************************************

    #    ----- All of this is basic UI setup, no logic code shall go here
    #    ------ I have spoken

    # **************************************************************

    def _setup_ui(self):
        # """Setup UI components#"""
        self.create_header("Projects")

        self._create_treeviews()
        self._create_forms()

    def _create_treeviews(self):
        # """Create and configure treeviews"""
        self.projects_tree = self._create_base_treeview(
            self.TREE_COLUMNS,
            double_click_handler=self._load_edit_state
        )
        self._reload_projects_tree()

    def _create_forms(self):
        # setup form buttons,
        # text, style, row, col, colspan, command
        self.edit_buttons = [
            ("Update", "success", 8, 0, 2, self._submit_edited_project),
            ("Delete", "danger", 8, 2, 1, self._delete_selected_project),
            ("Cancel", "warning", 8, 3, 2, self._load_base_state)
        ]

        self.main_buttons = [
            ("Upload CSV", "default outline", 5, 0, 2, self.upload_project_csv),
            ("Download Template", "info outline", 5, 2, 1,
             lambda: self.generate_csv_template(self.CSV_HEADERS, 'project_template')),
            ("Add Project", "danger", 5, 4, 2, self._load_new_project_state)
        ]

        self.new_buttons = [
            ("Create", "success", 8, 0, 2, self._create_new_project_from_form),
            ("Cancel", "warning", 8, 3, 2, self._load_base_state)
        ]

        # """Create form panels#"""
        self.main_button_panel = BaseForm(self, self.PROJECT_FIELDS)
        self.main_button_panel.grid(pady=20)
        self.main_button_panel.create_buttons(self.main_buttons)

        self.new_project_form = BaseForm(self, self.PROJECT_FIELDS)
        self.new_project_form.show_standard_fields(4)
        self.new_project_form.create_buttons(self.new_buttons)

        self.edit_project_form = BaseForm(self, self.PROJECT_FIELDS)
        self.edit_project_form.show_standard_fields(4)
        self.edit_project_form.create_buttons(self.edit_buttons)

    def _load_new_project_state(self):
        self.hide_forms()
        self.new_project_form.clear_form()
        self.new_project_form.grid()

    def _load_base_state(self):
        self.hide_forms()
        self.new_project_form.clear_form()
        self.edit_project_form.clear_form()
        self.main_button_panel.grid()

    def _load_edit_state(self):
        # validation should be redundant here as it should only be called as an action
        try:
            if not self.projects_tree.validate_item_is_selected():
                return
        except Exception as e:
            pass

        field_values = self.projects_tree._create_dictionary_from_selected_tree_item_and_values(
            self.TREE_COLUMNS)
        self.edit_project_form.populate_fields(field_values)
        self.hide_forms()
        self.edit_project_form.grid()

    def upload_project_csv(self):
        # """Handle Project CSV file upload - done in base tab"""
        self.upload_csv(self.CSV_HEADERS, "Classroom Locations imported successfully")
        self._reload_projects_tree()

    # ************************************************************

    #    ----- Project-specific Processing, no UI elements here, just all back-end stuff
    #    ------ I have spoken

    # **************************************************************

    def _reload_projects_tree(self):
        # this should be the only place where we have a query object for this tree or anything dealing with it
        self.projects_tree.reload_tree(Project.get_all_ordered_by_name(),
                                         self.TREE_COLUMNS)

    def _create_project_from_dictionary(self, dictionary) -> Project:
        project = None
        print(f' here is what we are getting from the creaate/edit form: {dictionary}')
        # try to get an existing project

        if 'project_ID' in dictionary:
            project = Project.get_by_id(dictionary['project_ID'])

        # if none exists: make a new one
        if not project:
            print("no project found in dict function, making a new one")
            project = Project(
                name=dictionary['name'],
                description=dictionary['description'],
                open_date=dictionary['open_date'],
                close_date=dictionary['close_date'],
                days_allowed=int(dictionary['days_allowed']),
                seats=int(dictionary['seats']),
                minimum_group_size=int(dictionary['minimum_group_size']),
                maximum_group_size=int(dictionary['maximum_group_size']),
                sub_eligible=dictionary['sub_eligible'] == 'True',
                unit=dictionary['unit'],
                objective=dictionary['objective'],
                ignore_validation=True
            )
            if 'project_ID' in dictionary:
                print(f"set project ID from dict function as {dictionary['project_ID']}")
                project.project_ID = dictionary['project_ID']

        # if one does, we set values directly
        else:

            project.name = dictionary['name']
            project.description = dictionary['description']
            project.open_date = dictionary['open_date']
            project.close_date = dictionary['close_date']
            project.days_allowed = int(dictionary['days_allowed'])
            project.seats = int(dictionary['seats'])
            project.minimum_group_size = int(dictionary['minimum_group_size'])
            project.maximum_group_size = int(dictionary['maximum_group_size'])
            project.sub_eligible = dictionary['sub_eligible'] == 'True'
            project.unit = dictionary['unit']

        return project

    def _process_row(self, dictionary_from_row: dict):
        try:
            project = self._create_project_from_dictionary(dictionary_from_row)

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data in CSV: {str(e)}")

        return project

    def _save_CSV_row(self, project: Project):
        """ we use a separate function to save so that we can process the CSV as a whole"""
        project.save()

    def _create_new_project_from_form(self):
        # """Create new project from form data#"""
        #try:
            values = self.new_project_form.validate_and_collect_form_values()
            if values:
                self.project = self._create_project_from_dictionary(values)
                self.project.save()
                self._reload_projects_tree()
                self._load_base_state()
        #except Exception as e:
            #self.show_error(f"Failed to update project: {str(e)}")

    def _submit_edited_project(self):
        # """Submit edited project data#"""

        # try:
        form_values = self.edit_project_form.validate_and_collect_form_values()
        existing_project = self.get_selected_project()
        form_values['project_ID'] = existing_project.project_ID
        edited_project = self._create_project_from_dictionary(form_values)

        if edited_project and existing_project:
            edited_project.save()
            self._reload_projects_tree()
            self._load_base_state()
        else:
            self.show_error("Project not found in database")

    # except Exception as e:
    # self.show_error(f"Failed to update project: {str(e)}")

    def _delete_selected_project(self):
        # """Delete selected project#"""

        if self.confirm_delete(f"Are you sure you want to delete selected project'?"):
            try:
                project = self.get_selected_project()
                if project:
                    project.delete()
                    self._reload_projects_tree()
                    self._load_base_state()

            except Exception as e:
                self.show_error(f"Failed to delete project: {str(e)}")

    def get_selected_project(self) -> Project:
        if not self.projects_tree.validate_item_is_selected():
            return None

        try:
            selected = self.projects_tree.selection()[0]
            values = self.projects_tree.item(selected)['values']
            project = Project.get_by_id(values[0])
            if project:
                return project
            else:
                self.show_error("Project not found in database")
                return None
        except Exception as e:
            self.show_error(f"Failed to select project: {str(e)}")
