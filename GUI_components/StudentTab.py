import csv
from tkinter import filedialog, messagebox
import ttkbootstrap as tb
from datetime import datetime

import Persistance
from Model import Student, Unit
from GUI_components.BaseTreeView import BaseTreeView
from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTab import BaseTab



class StudentTab(BaseTab):
    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    # (display label, field label, display type)
    STUDENT_FIELDS = [
        ('StudentID', 'studentID', 'int(10,0,20)'),
        ('Glenpool ID', 'glenpool_id', 'int(10,0,20)'),
        ('RFID', 'rfid', 'string(10,50)'),
        ('First Name', 'first_name', 'string(10,50)'),
        ('Last Name', 'last_name', 'string(10,50)'),
        ('User Name', 'user_name', 'string(10,50)'),
        ('Hour', 'hour_ID', 'hour_dropdown')
    ]

    TREE_COLUMNS = [('ID', 'studentID', 100),
                    ('Glenpool ID', 'glenpool_id', 100),
                    ('First Name', 'first_name', 150),
                    ('Last Name', 'last_name', 150),
                    ('Hour', 'hour_id', 50),
                    ('User Name', 'user_name', 50),
                    ('RFID', 'rfid', 50)
                    ]

    CSV_HEADERS = ['studentID', 'glenpool_id', 'first_name', 'last_name', 'hour_ID', 'user_name', 'rfid']


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
        self.create_header("Students")

        self._create_treeviews()
        self._create_forms()

    def _create_treeviews(self):
        # """Create and configure treeviews"""
        self.students_tree = self._create_base_treeview(
            self.TREE_COLUMNS,
            double_click_handler=self._load_edit_state
        )
        self._reload_students_tree()

    def _create_forms(self):
        # setup form buttons,
        # text, style, row, col, colspan, command
        self.edit_buttons = [
            ("Update", "success", 8, 0, 2, self._submit_edited_student),
            ("Delete", "danger", 8, 2, 1, self._delete_selected_student),
            ("Cancel", "warning", 8, 3, 2, self._load_base_state)
        ]

        self.main_buttons = [
            ("Upload CSV", "default outline", 5, 0, 2, self.upload_student_csv),
            ("Download Template", "info outline", 5, 2, 1,
             lambda: self.generate_csv_template(self.CSV_HEADERS, 'student_template')),
            ("Add Student", "danger", 5, 4, 2, self._load_new_student_state)
        ]

        self.new_buttons = [
            ("Create", "success", 8, 0, 2, self._create_new_student_from_form),
            ("Cancel", "warning", 8, 3, 2, self._load_base_state)
        ]

        # """Create form panels#"""
        self.main_button_panel = BaseForm(self, self.STUDENT_FIELDS)
        self.main_button_panel.grid(pady=20)
        self.main_button_panel.create_buttons(self.main_buttons)

        self.new_student_form = BaseForm(self, self.STUDENT_FIELDS)
        self.new_student_form.show_standard_fields(4)
        self.new_student_form.create_buttons(self.new_buttons)

        self.edit_student_form = BaseForm(self, self.STUDENT_FIELDS)
        self.edit_student_form.show_standard_fields(4)
        self.edit_student_form.create_buttons(self.edit_buttons)

    def _load_new_student_state(self):
        self.hide_forms()
        self.new_student_form.clear_form()
        self.new_student_form.grid()

    def _load_base_state(self):
        self.hide_forms()
        self.new_student_form.clear_form()
        self.edit_student_form.clear_form()
        self.main_button_panel.grid()

    def _load_edit_state(self):
        # validation should be redundant here as it should only be called as an action
        try:
            if not self.students_tree.validate_item_is_selected():
                return
        except Exception as e:
            pass

        field_values = self.students_tree._create_dictionary_from_selected_tree_item_and_values(
            self.TREE_COLUMNS)
        self.edit_student_form.populate_fields(field_values)
        self.hide_forms()
        self.edit_student_form.grid()

    def upload_student_csv(self):
        # """Handle Student CSV file upload - done in base tab"""
        self.upload_csv(self.CSV_HEADERS, "Classroom Locations imported successfully")
        self._reload_students_tree()

    # ************************************************************

    #    ----- Student-specific Processing, no UI elements here, just all back-end stuff
    #    ------ I have spoken

    # **************************************************************

    def _reload_students_tree(self):
        # this should be the only place where we have a query object for this tree or anything dealing with it
        self.students_tree.reload_tree(Student.get_all_ordered_by_last_name(),
                                         self.TREE_COLUMNS)

    def _create_student_from_dictionary(self, dictionary) -> Student:
        """Create or update a Student from a form/CSV dictionary.
        - Tolerates missing 'rfid'
        - Accepts 'hour' or 'hour_ID'
        - Looks up existing student using 'original_studentID' (from edit flow) or 'studentID'
        """

        def to_int(value, default=None):
            try:
                if value is None:
                    return default
                s = str(value).strip()
                if s == '':
                    return default
                return int(s)
            except (TypeError, ValueError):
                return default

        print(f" here is what we are getting from the creaate/edit form: {dictionary}")

        # Determine which student to update (edit flow) or create (new)
        original_sid = dictionary.get('original_studentID')
        sid_lookup = to_int(original_sid) if original_sid is not None else to_int(dictionary.get('studentID'))

        student = Student.get_by_id(sid_lookup) if sid_lookup is not None else None

        # Normalize incoming values
        sid = to_int(dictionary.get('studentID'))
        glenpool_id = to_int(dictionary.get('glenpool_id'))
        rfid = (dictionary.get('rfid'))
        first_name = (dictionary.get('first_name') or '').strip()
        last_name = (dictionary.get('last_name') or '').strip()
        user_name = (dictionary.get('user_name') or '').strip()
        hour_value = dictionary.get('hour', dictionary.get('hour_ID'))

        if not student:
            # Creating a new student
            student = Student(
                studentID=sid,
                glenpool_id=glenpool_id,
                rfid=rfid,
                first_name=first_name,
                last_name=last_name,
                user_name=user_name,
                hour = hour_value
            )
        else:
            # Updating existing student
            if sid is not None:
                student.studentID = sid
            if glenpool_id is not None:
                # Keep property name consistent with the rest of the code
                student.glenpool_id = glenpool_id
            student.rfid = rfid
            student.first_name = first_name
            student.last_name = last_name
            student.user_name = user_name

        # Assign hour using whichever representation we have
        if hour_value is not None:
            # Try to set via the 'hour' property (likely expects a Hour object),
            # fall back to hour_ID if that fails.
            try:
                student.hour = hour_value
            except Exception:
                try:
                    student.hour_ID = to_int(hour_value)
                except Exception:
                    pass

        return student

    def _submit_edited_student(self):
        # """Submit edited student data#"""
        form_values = self.edit_student_form.validate_and_collect_form_values()
        existing_student = self.get_selected_student()
        if not existing_student:
            self.show_error("Student not found in database")
            return

        # Carry the original studentID so we update the correct record even if the ID was changed in the form
        form_values['original_studentID'] = getattr(existing_student, 'studentID', None)

        edited_student = self._create_student_from_dictionary(form_values)
        if edited_student:
            edited_student.save()
            self._reload_students_tree()
            self._load_base_state()
        else:
            self.show_error("Failed to update student: invalid form values")

    def _process_row(self, dictionary_from_row: dict):
        try:
            student = self._create_student_from_dictionary(dictionary_from_row)

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data in CSV: {str(e)}")

        return student

    def _save_CSV_row(self, student: Student):
        """ we use a separate function to save so that we can process the CSV as a whole"""
        student.save()

    def _create_new_student_from_form(self):
        # """Create new student from form data#"""
        #try:
            values = self.new_student_form.validate_and_collect_form_values()
            if values:
                self.student = self._create_student_from_dictionary(values)
                self.student.save()
                self._reload_students_tree()
                self._load_base_state()
        #except Exception as e:
            #self.show_error(f"Failed to update student: {str(e)}")

    def _delete_selected_student(self):
        # """Delete selected student#"""

        if self.confirm_delete(f"Are you sure you want to delete selected student'?"):
            try:
                student = self.get_selected_student()
                if student:
                    student.delete()
                    self._reload_students_tree()
                    self._load_base_state()

            except Exception as e:
                self.show_error(f"Failed to delete student: {str(e)}")

    def get_selected_student(self) -> Student:
        if not self.students_tree.validate_item_is_selected():
            return None

        try:
            selected = self.students_tree.selection()[0]
            values = self.students_tree.item(selected)['values']
            student = Student.get_by_id(values[0])
            if student:
                return student
            else:
                self.show_error("Student not found in database")
                return None
        except Exception as e:
            self.show_error(f"Failed to select student: {str(e)}")