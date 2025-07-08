# GUI_components/BaseTab.py
import ttkbootstrap as tb
from tkinter import messagebox, filedialog
import csv

from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTreeView import BaseTreeView


class BaseTab(tb.Frame):
    
    # Class constants
    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'


    def __init__(self, notebook):
        super().__init__(notebook)
        self.notebook = notebook

    def create_header(self, header_text):
        # """Create header label#"""
        self.units_label = tb.Label(self, text=header_text, font=("Helvetica", 18))
        self.units_label.grid(pady=20)

    def _create_base_treeview(self, tree_columns, double_click_handler=None):
        """Create and configure base treeview"""
        tree = BaseTreeView(self, tree_columns)
        tree.grid(padx=5, pady=15)
        if double_click_handler:
            tree.bind('<Double-1>', lambda e: double_click_handler())
        return tree

    def _create_base_forms(self, display_fields, button_configs):
        """Create standard forms with configurable buttons"""
        forms = {}

        # Create main panel
        forms['main'] = BaseForm(self, display_fields)
        forms['main'].grid(pady=20)

        # Create new item form
        forms['new'] = BaseForm(self, display_fields)
        forms['new'].show_standard_fields(4)

        # Create edit form
        forms['edit'] = BaseForm(self, display_fields)
        forms['edit'].show_standard_fields(4)

        # Add buttons to each form
        for form_name, buttons in button_configs.items():
            if form_name in forms:
                self.create_buttons(forms[form_name], buttons)

        return forms

    def hide_forms(self):
        """Hide all form components"""
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, BaseForm):
                attr.grid_remove()

    def generate_csv_template(self, headers, filename="template"):
        #"""Common method for CSV template generation#"""
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"{filename}.csv"
        )
        if file_path:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)

    def show_error(self, message):
        #"""Common error dialog#"""
        messagebox.showerror("Error", message)

    def show_success(self, message):
        #"""Common success dialog#"""
        messagebox.showinfo("Success", message)

    def confirm_delete(self, message="Are you sure you want to delete this item?"):
        #"""Common delete confirmation dialog#"""
        return messagebox.askyesno("Confirm Delete", message)

    def upload_csv(self, header_row, success_message="Items imported successfully"):
        #"""Generic CSV file upload handler"""
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        try:
            self._process_csv_file(file_path, header_row)
            self.show_success(success_message)
        except Exception as e:
            self.show_error(f"Failed to read CSV file: {str(e)}")

    def _process_csv_file(self, file_path, header_row):
        #"""Generic CSV file processor"""
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            first_row = next(csv_reader)
            CSV_generated_objects = []
            csv_rows = 0

            if first_row != header_row:
                self.dictionary_to_convert = self._generate_dictionary_from_csv_row(first_row, header_row)
                CSV_generated_objects.append(self._process_row(self.dictionary_to_convert))
                csv_rows += 1

            for row in csv_reader:
                self.dictionary_to_convert = self._generate_dictionary_from_csv_row(row, header_row)
                CSV_generated_objects.append(self._process_row(self.dictionary_to_convert))
                csv_rows += 1

            if csv_rows == len(CSV_generated_objects):
                for item in CSV_generated_objects:
                    self._save_CSV_row(item)
            else:
                raise ValueError(f"CSV not processed sue to previous error")


    def _generate_dictionary_from_csv_row(self, csv_row, header_row):
        #"""Generate dictionary from CSV row using header row as keys"""
        if len(csv_row) != len(header_row):
            raise ValueError(f"CSV row length ({len(csv_row)}) does not match header length ({len(header_row)})")

        try:
            return {header: value for header, value in zip(header_row, csv_row)}
        except Exception as e:
            raise ValueError(f"Error creating dictionary from CSV row: {str(e)}")

    def _process_row(self, row):
        #"""Abstract method to be implemented by child classes"""
        raise NotImplementedError("Subclasses must implement _process_row")

    def _save_CSV_row(self, row):
        #"""Abstract method to be implemented by child classes"""
        raise NotImplementedError("Subclasses must implement _process_row")



