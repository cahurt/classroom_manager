from Model import ClassroomLocation
from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTab import BaseTab


class ClassroomLocationsTab(BaseTab):
    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    # (display label, field label, display type)
    CLASSROOM_LOCATION_FIELDS = [
        ('Name', 'name', 'string(10,50)', []),
        ('Description', 'description', 'text(15,5,1000)', []),
        ('Label', 'label', 'string(10,255)', []),
        ('Label Size', 'label_size', 'int(10,0,5)', []),
        ('Label Color', 'label_color', 'color', []),
    ]

    TREE_COLUMNS = [('ID', 'classroom_location_ID', 0),
                    ('Label Size', 'label_size', 0),
                    ('Name', 'name', 50),
                    ('Description', 'description', 100),
                    ('Label', 'label', 100),
                    ('Color', 'label_color', 50)]

    CSV_HEADERS = ['name', 'description', 'label', 'label_size', 'label_color']


    def __init__(self, notebook):
        super().__init__(notebook)
        print("setting up classroom locations tab")
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
        self.create_header("Classroom Locations")

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
        self.main_button_panel = BaseForm(self, self.CLASSROOM_LOCATION_FIELDS)
        self.main_button_panel.grid(pady=20)
        self.main_button_panel.create_buttons(self.main_buttons)

        self.new_classroom_location_form = BaseForm(self, self.CLASSROOM_LOCATION_FIELDS)
        self.new_classroom_location_form.show_standard_fields(4)
        self.new_classroom_location_form.create_buttons(self.new_buttons)

        self.edit_classroom_location_form = BaseForm(self, self.CLASSROOM_LOCATION_FIELDS)
        self.edit_classroom_location_form.show_standard_fields(4)
        self.edit_classroom_location_form.create_buttons(self.edit_buttons)


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

        field_values = self.classroom_locations_tree._create_dictionary_from_selected_tree_item_and_values(
            self.TREE_COLUMNS)
        self.edit_classroom_location_form.populate_fields(field_values)
        self.hide_forms()
        self.edit_classroom_location_form.grid()

    def upload_classroom_location_csv(self):
        # """Handle ClassroomLocation CSV file upload - done in base tab"""
        self.upload_csv(self.CSV_HEADERS, "Classroom Locations imported successfully")
        self._reload_classroom_locations_tree()

    # ************************************************************

    #    ----- ClassroomLocation-specific Processing, no UI elements here, just all back-end stuff
    #    ------ I have spoken

    # **************************************************************

    def _reload_classroom_locations_tree(self):
        # this should be the only place where we have a query object for this tree or anything dealing with it
        self.classroom_locations_tree.reload_tree(ClassroomLocation.get_all_order_by_name(),
                                                  self.TREE_COLUMNS)

    def _create_classroom_location_from_dictionary(self, dictionary) -> ClassroomLocation:
        classroom_location = None
        print(dictionary)
        # try to get an existing classroom_location

        if 'classroom_location_ID' in dictionary:
            classroom_location = ClassroomLocation.get_by_id(dictionary['classroom_location_ID'])

        # if none exists: make a new one
        if not classroom_location:
            print("no classroom_location found in dict function, making a new one")
            classroom_location = ClassroomLocation(
                name=dictionary['name'],
                label=dictionary['label'],
                label_size=int(dictionary['label_size']),
                label_color=dictionary['label_color'],
                description=dictionary['description'],
                ignore_validation=True
            )
            if 'classroom_location_ID' in dictionary:
                print(f"set classroom_location ID from dict function as {dictionary['classroom_location_ID']}")
                classroom_location.classroom_location_ID = dictionary['classroom_location_ID']

        # if one does, we set values directly
        else:

            classroom_location.name = dictionary['name']
            classroom_location.label = dictionary['label']
            classroom_location.label_size = int(dictionary['label_size'])
            classroom_location.label_color = dictionary['label_color']
            classroom_location.description = dictionary['description']

        return classroom_location

    def _process_row(self, dictionary_from_row: dict):
        try:
            classroom_location = self._create_classroom_location_from_dictionary(dictionary_from_row)

        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data in CSV: {str(e)}")

        return classroom_location

    def _save_CSV_row(self, classroom_location: ClassroomLocation):
        """ we use a separate function to save so that we can process the CSV as a whole"""
        classroom_location.save()

    def _create_new_classroom_location_from_form(self):
        # """Create new classroom_location from form data#"""
        try:
            values = self.new_classroom_location_form.validate_and_collect_form_values()
            if values:
                self.classroom_location = self._create_classroom_location_from_dictionary(values)
                self.classroom_location.save()
                self._reload_classroom_locations_tree()
                self._load_base_state()
        except Exception as e:
            self.show_error(f"Failed to update classroom_location: {str(e)}")

    def _submit_edited_classroom_location(self):
        # """Submit edited classroom_location data#"""

        #try:
            form_values = self.edit_classroom_location_form.validate_and_collect_form_values()
            existing_classroom_location = self.get_selected_classroom_location()
            form_values['classroom_location_ID'] = existing_classroom_location.classroom_location_ID
            edited_classroom_location = self._create_classroom_location_from_dictionary(form_values)

            if edited_classroom_location and existing_classroom_location:
                edited_classroom_location.save()
                self._reload_classroom_locations_tree()
                self._load_base_state()
            else:
                self.show_error("ClassroomLocation not found in database")
        #except Exception as e:
            #self.show_error(f"Failed to update classroom_location: {str(e)}")

    def _delete_selected_classroom_location(self):
        # """Delete selected classroom_location#"""

        if self.confirm_delete(f"Are you sure you want to delete selected classroom_location'?"):
            try:
                classroom_location = self.get_selected_classroom_location()
                if classroom_location:
                    classroom_location.delete()
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
            classroom_location = ClassroomLocation.ClassroomLocation.get_by_id(values[0])
            if classroom_location:
                return classroom_location
            else:
                self.show_error("ClassroomLocation not found in database")
                return None
        except Exception as e:
            self.show_error(f"Failed to select classroom_location: {str(e)}")
