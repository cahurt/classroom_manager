import csv
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from datetime import datetime

import Persistance
from Model import Objective
from GUI_components.BaseTreeView import BaseTreeView
from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTab import BaseTab


class ObjectiveTab(BaseTab):
    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    OBJECTIVE_FIELDS = [
        ('Name', 'objective_name', 'string(10, 255)', []),
        ('Description', 'objective_description', 'text(15,5,1000)', [])
    ]

    TREE_COLUMNS = [('Name', 'objective_name'), ('Description','objective_description')]
    CSV_HEADERS = ['objective_name', 'objective_description']

    def __init__(self, notebook):
        super().__init__(notebook)
        self._setup_variables()
        self._setup_ui()

    def _setup_variables(self):
        #"""Initialize form variables#"""
        self.new_objective_vars = self._create_objective_variables()
        self.edit_objective_vars = self._create_objective_variables()

    def _create_objective_variables(self):
        #"""Create StringVar variables for objective forms#"""
        return {field: tb.StringVar(value="") for field in self.CSV_HEADERS}

    def _setup_ui(self):
        #"""Setup UI components#"""
        self._create_header()
        self._create_treeview()
        self._create_forms()
        self._setup_buttons()

    def _create_header(self):
        #"""Create header label#"""
        self.objectives_label = tb.Label(self, text="Objectives", font=("Helvetica", 18))
        self.objectives_label.grid(pady=20)

    def _create_treeview(self):
        #"""Create and configure treeview#"""
        self.objectives_tree = BaseTreeView(self, self.TREE_COLUMNS)
        self.objectives_tree.grid(padx=5, pady=15)
        self.objectives_tree.bind('<Double-1>', lambda e: self.show_edit_objective())
        self._reload_objectives()

    def _create_forms(self):
        #"""Create form panels#"""
        self.main_button_panel = BaseForm(self)
        self.main_button_panel.grid(pady=20)

        self.new_objective_form = BaseForm(self)
        self.new_objective_form.show_standard_fields(self.OBJECTIVE_FIELDS, 4)

        self.edit_objective_form = BaseForm(self)
        self.edit_objective_form.show_standard_fields(self.OBJECTIVE_FIELDS, 4)

    def _setup_buttons(self):
        #"""Setup form buttons#"""
        self._create_main_buttons()
        self._create_new_objective_buttons()
        self._create_edit_objective_buttons()

    def _create_main_buttons(self):
        #"""Create main panel buttons#"""
        buttons = [
            ("Upload CSV", "default outline", self.upload_objective_csv),
            ("Download Template", "info outline",
             lambda: self.generate_csv_template(self.CSV_HEADERS, 'objective_template.csv')),
            ("Add Objective", "danger", self.load_new_objective_state)
        ]

        for text, style, command in buttons:
            btn = tb.Button(self.main_button_panel, text=text, bootstyle=style, command=command)
            btn.grid(pady=20)

    def load_new_objective_state(self):
        self.swap_form_visibility(self.main_button_panel, self.new_objective_form)
        self.new_objective_form.clear_form()

    def _create_new_objective_buttons(self):
        #"""Create new objective form buttons#"""
        submit_btn = tb.Button(self.new_objective_form, text="Create", bootstyle="success",
                               command=lambda: self.new_objective_form.validate_and_collect_form_values(self.create_new_objective()))
        submit_btn.grid(row=4, column=0, columnspan=5, pady=20)

        cancel_btn = tb.Button(self.new_objective_form, text="Cancel", bootstyle="danger",
                               command=lambda: self.swap_form_visibility(self.new_objective_form, self.main_button_panel))
        cancel_btn.grid(row=4, column=1, columnspan=5, pady=20)

    def _create_edit_objective_buttons(self):
        #"""Create edit objective form buttons#"""
        buttons = [
            ("Update", "success", 0, 2, self.submit_edit_objective),
            ("Delete", "danger", 2, 1, self.delete_objective),
            ("Cancel", "warning", 3, 2,
             lambda: self.swap_form_visibility(self.edit_objective_form, self.main_button_panel))
        ]

        for text, style, col, colspan, command in buttons:
            btn = tb.Button(self.edit_objective_form, text=text, bootstyle=style, command=command)
            btn.grid(row=4, column=col, columnspan=colspan, pady=20)

    def upload_objective_csv(self):
        #"""Handle CSV file upload#"""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            self._process_csv_file(file_path)
            self.show_success("Objectives imported successfully")
        except Exception as e:
            self.show_error(f"Failed to read CSV file: {str(e)}")
        finally:
            self._reload_objectives()

    def _process_csv_file(self, file_path):
        #"""Process uploaded CSV file#"""
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            first_row = next(csv_reader)

            if first_row != self.CSV_HEADERS:
                self._process_objective_row(first_row)

            for row in csv_reader:
                self._process_objective_row(row)

    def _process_objective_row(self, row):
        #"""Process single CSV row into Objective object#"""
        try:
            objective = Objective.Objective(
                row[0],
                row[1]
             )
            objective.add_objective()
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data in CSV: {str(e)}")

    def create_new_objective(self):
        #"""Create new objective from form data#"""
        values = self.new_objective_form.validate_and_collect_form_values(self.main_button_panel)
        if values:
            Objective.Objective(
                values.get('objective_name'),
                values.get('objective_description'),
               ).add_objective()
            self._reload_objectives()

    def show_edit_objective(self):
        #"""Display edit form for selected objective#"""
        if not self.objectives_tree.selection():
            return

        selected = self.objectives_tree.selection()[0]
        values = self.objectives_tree.item(selected)['values']

        self.hide_forms()
        self.edit_objective_form.grid()

        field_values = self._create_field_values_dict(values)
        self.edit_objective_form.populate_fields(field_values)

    def _create_field_values_dict(self, values):
        #"""Create dictionary of field values from selected objective#"""
        return {
            'objective_name': values[0],
            'objective_description': values[1]
        }

    def hide_forms(self):
        # """Hide all form components#"""
        self.main_button_panel.grid_remove()
        self.new_objective_form.grid_remove()
        self.edit_objective_form.grid_remove()

    def submit_edit_objective(self):
        #"""Submit edited objective data#"""
        if not self._validate_edit_objective():
            return

        selected = self.objectives_tree.selection()[0]
        values = self.objectives_tree.item(selected)['values']

        try:
            objective = self._get_objective_by_name(values[0])
            if objective:
                self._update_objective(objective)
                self._reload_objectives()
                self.swap_form_visibility(self.edit_objective_form, self.main_button_panel)
            else:
                self.show_error("Objective not found in database")
        except Exception as e:
            self.show_error(f"Failed to update objective: {str(e)}")

    def _validate_edit_objective(self):
        #"""Validate objective selection for editing#"""
        if not self.objectives_tree.selection():
            self.show_error("Please select a objective to edit")
            return False
        return True

    def _get_objective_by_name(self, name):
        #"""Retrieve objective from database by name#"""
        return Persistance.session.query(Objective.Objective).filter_by(objective_name=name).first()

    def _update_objective(self, objective):
        #"""Update objective with form values#"""
        form_values = self.edit_objective_form.get_all_entries()
        objective.objective_name = form_values.get('objective_name')
        objective.objective_description = form_values.get('objective_description')
        objective.update_objective()

    def delete_objective(self):
        #"""Delete selected objective#"""
        if not self._validate_edit_objective():
            return

        selected = self.objectives_tree.selection()[0]
        values = self.objectives_tree.item(selected)['values']

        if self.confirm_delete(f"Are you sure you want to delete objective '{values[0]}'?"):
            try:
                objective = self._get_objective_by_name(values[0])
                if objective:
                    objective.delete_objective()
                    self._reload_objectives()
                    self.swap_form_visibility(self.edit_objective_form, self.main_button_panel)
                else:
                    self.show_error("Objective not found in database")
            except Exception as e:
                self.show_error(f"Failed to delete objective: {str(e)}")

    def _reload_objectives(self):
        #"""Refresh objectives display in treeview#"""
        self.objectives_tree.delete(*self.objectives_tree.get_children())
        objectives = Persistance.session.query(Objective.Objective).order_by(Objective.Objective.objective_name).all()

        for objective in objectives:
            self.objectives_tree.insert('', 'end', values=self._format_objective_values(objective))

    def _format_objective_values(self, objective):
        #"""Format objective values for display#"""
        return (
            objective.objective_name,
            objective.objective_description
            )
