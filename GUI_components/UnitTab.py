# GUI_components/tabs/UnitTab.py
import csv
from tkinter import filedialog, messagebox
from Model import Unit
from GUI_components.BaseTab import BaseTab
from GUI_components.BaseTreeView import BaseTreeView
import ttkbootstrap as tb
from datetime import datetime
from tkinter import*
from GUI_components.BaseForm import BaseForm
import Persistance


class UnitTab(BaseTab):
    def __init__(self, notebook):
        super().__init__(notebook)
        self.setup_variables()
        self.setup_ui()
        #self.load_data()

    def setup_variables(self):
        #"""Initialize all StringVar variables#"""
        self.new_unit_vars = {
            'name': tb.StringVar(value=""),
            'sequence': tb.StringVar(value=""),
            'opening_date': tb.StringVar(value=""),
            'closing_date': tb.StringVar(value=""),
            'end_date': tb.StringVar(value=""),
            'description': tb.StringVar(value="")
        }

        self.edit_unit_vars = {
            'name': tb.StringVar(value=""),
            'sequence': tb.StringVar(value=""),
            'opening_date': tb.StringVar(value=""),
            'closing_date': tb.StringVar(value=""),
            'end_date': tb.StringVar(value=""),
            'description': tb.StringVar(value="")
        }

        # map to give the label, field name, and validator/entry type
        self.display_unit_fields = [
                                         ('Name','unit_name',str),
                                         ('Sequence','sequence',int),
                                         ('Opening Date','opening_date',datetime),
                                         ('End Date','end_date',datetime),
                                         ('Closing Date','closing_date',datetime),
                                         ('Description', 'description',None)
                                         ]

        self.display_unit_tree_fields =['unit_name', 'sequence', 'opening_date', 'end_date', 'closing_date', 'description']

    def setup_ui(self):
        self.create_header()
        self.create_treeview()
        self.create_forms()
        self.setup_buttons()

    def create_header(self):
        self.objectives_label = tb.Label(self, text="Units", font=("Helvetica", 18))
        self.objectives_label.grid(pady=20)

    def create_treeview(self):
        self.units_tree = BaseTreeView(self, self.display_unit_tree_fields)
        self.units_tree.grid(padx=5, pady=15)
        self.reload_units()

    def create_forms(self):

        # new unit GUI items
        self.main_button_panel = BaseForm(self)
        self.main_button_panel.grid(pady=20)

        self.new_unit_form = BaseForm(self)
        self.new_unit_form.show_standard_fields(self.display_unit_fields, 4)

        self.edit_unit_form = BaseForm(self)
        self.edit_unit_form.show_standard_fields(self.display_unit_fields, 4)

    def setup_buttons(self):
        self.upload_units_button = tb.Button(self.main_button_panel, text="upload CSV", bootstyle="default outline", command=self.upload_unit_csv)
        self.upload_units_button.grid(pady=20)

        self.template_button = tb.Button(self.main_button_panel, text="Download Template", bootstyle="info outline", command=lambda: self.generate_csv_template(['unit_name', 'sequence', 'opening_date', 'end_date', 'closing_date', 'description'], 'unit_template.csv'))
        self.template_button.grid(pady=20)

        self.add_unit_button = tb.Button(self.main_button_panel, text="Add Unit", bootstyle="danger", command=lambda: self.swap_form_visibility(self.main_button_panel, self.new_unit_form))
        self.add_unit_button.grid(pady=20)

        self.new_unit_submit = tb.Button(self.new_unit_form, text="Create", bootstyle="success", command=lambda: self.new_unit_form.submit_form(self.create_new_unit()))
        self.new_unit_submit.grid(row=4, column=0, columnspan=5, pady=20)

        self.new_unit_cancel = tb.Button(self.new_unit_form, text="Cancel", bootstyle="danger", command=lambda: self.swap_form_visibility(self.new_unit_form, self.main_button_panel))
        self.new_unit_cancel.grid(row=4, column=1, columnspan=5, pady=20)

        self.edit_unit_submit = tb.Button(self.new_unit_form, text="Update", bootstyle="success", command=self.submit_edit_unit)
        self.edit_unit_submit.grid(row=4, column=0, columnspan=2, pady=20)

        self.edit_unit_delete = tb.Button(self.edit_unit_form, text="Delete", bootstyle="danger", command=self.delete_unit)
        self.edit_unit_delete.grid(row=4, column=2, columnspan=1, pady=20)

        self.edit_unit_cancel = tb.Button(self.edit_unit_form, text="Cancel", bootstyle="warning", command=lambda: self.swap_form_visibility(self.edit_unit_form, self.main_button_panel))
        self.edit_unit_cancel.grid(row=4, column=3, columnspan=2, pady=20)

    def upload_unit_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file)
                first_row = next(csv_reader)

                # Check if first row is header
                if first_row == ['unit_name', 'sequence', 'opening_date', 'end_date', 'closing_date', 'description']:
                    # Skip the header row
                    pass
                else:
                    # If not header, process first row as data
                    try:
                        Unit.Unit(
                            first_row[0],
                            int(first_row[1]),
                            datetime.strptime(first_row[2], '%Y-%m-%d'),
                            datetime.strptime(first_row[4], '%Y-%m-%d'),
                            datetime.strptime(first_row[3], '%Y-%m-%d'),
                            first_row[5]
                        ).add_unit()
                    except (ValueError, IndexError) as e:
                        messagebox.showerror("Error", f"Invalid data in CSV: {str(e)}")
                        return

                for row in csv_reader:
                    try:
                        Unit.Unit(
                            row[0],
                            int(row[1]),
                            datetime.strptime(row[2], '%Y-%m-%d'),
                            datetime.strptime(row[4], '%Y-%m-%d'),
                            datetime.strptime(row[3], '%Y-%m-%d'),
                            row[5]
                        ).add_unit()
                    except (ValueError, IndexError) as e:
                        messagebox.showerror("Error", f"Invalid data in CSV: {str(e)}")
                        self.reload_units()
                        return

                self.reload_units()
                messagebox.showinfo("Success", "Units imported successfully")
                self.reload_units()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to read CSV file: {str(e)}")
            self.reload_units()

    def validate_unit_fields(self):
        if not self.new_unit_name.get().strip():
            self.validation_label.config(text="Unit name is required")
            return False
        if not self.new_unit_sequence.get().strip() or not self.new_unit_sequence.get().strip().isdigit():
            self.validation_label.config(text="Sequence is required and must be a number")
            return False
        if not self.new_unit_opening_date_entry.entry.get().strip():
            self.validation_label.config(text="Opening date is required")
            return False
        if not self.new_unit_closing_date_entry.entry.get().strip():
            self.validation_label.config(text="Closing date is required")
            return False
        if not self.new_unit_end_date_entry.entry.get().strip():
            self.validation_label.config(text="End date is required")
            return False
        if not self.new_unit_description_text.get("1.0", END).strip():
            self.validation_label.config(text="Description is required")
            return False
        self.validation_label.config(text="")
        return True

    def create_new_unit(self):

         self.new_unit_values = self.new_unit_form.submit_form(self.main_button_panel)
         if self.new_unit_values is not None:
             print(self.new_unit_values)
             Unit.Unit(
                self.new_unit_values.get('unit_name'),
                int(self.new_unit_values.get('sequence')),
                self.new_unit_values.get('opening_date'),
                self.new_unit_values.get('closing_date'),
                self.new_unit_values.get('end_date'),
                self.new_unit_values.get('description')
                ).add_unit()
         self.reload_units()

    def cancel_new_unit(self):
        # reload_units()
        print("cancel")
        self.new_unit_frame.pack_forget()
        self.add_unit_button.pack(pady=20)
        self.upload_units_button.pack(pady=20)
        self.template_button.pack(pady=20)

    def validate_edit_unit_fields(self):
        if not self.edit_unit_name.get().strip():
            self.edit_validation_label.config(text="Unit name is required")
            return False
        if not self.edit_unit_sequence.get().strip() or not self.edit_unit_sequence.get().strip().isdigit():
            self.edit_validation_label.config(text="Sequence is required and must be a number")
            return False
        if not self.edit_unit_opening_date_entry.entry.get().strip():
            self.edit_validation_label.config(text="Opening date is required")
            return False
        if not self.edit_unit_closing_date_entry.entry.get().strip():
            self.edit_validation_label.config(text="Closing date is required")
            return False
        if not self.edit_unit_end_date_entry.entry.get().strip():
            self.edit_validation_label.config(text="End date is required")
            return False
        if not self.edit_unit_description_text.get("1.0", END).strip():
            self.edit_validation_label.config(text="Description is required")
            return False
        self.edit_validation_label.config(text="")
        return True

    def submit_edit_unit(self):
        if self.validate_edit_unit_fields():
            selected = self.units_tree.selection()[0]
            unit = Persistance.session.query(Unit.Unit).filter_by(
                unit_sequence=self.units_tree.item(selected)['values'][0]).first()
            unit.unit_name = self.edit_unit_name.get()
            unit.unit_sequence = self.edit_unit_sequence.get()
            unit.unit_opening_date = datetime.strptime(self.edit_unit_opening_date_entry.entry.get(), '%m/%d/%Y')
            unit.unit_closing_date = datetime.strptime(self.edit_unit_closing_date_entry.entry.get(), '%m/%d/%Y')
            unit.unit_end_date = datetime.strptime(self.edit_unit_end_date_entry.entry.get(), '%m/%d/%Y')
            unit.unit_description = self.edit_unit_description_text.get("1.0", END)
            unit.update_unit()
            self.reload_units()
            self.edit_unit_frame.pack_forget()
            self.add_unit_button.pack(pady=20)
            self.upload_units_button.pack(pady=20)

    def delete_unit(self):

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this unit?"):
            selected = self.units_tree.selection()[0]
            unit = Persistance.session.query(Unit.Unit).filter_by(
                unit_sequence=self.units_tree.item(selected)['values'][0]).first()
            unit.delete_unit()
            self.reload_units()
            self.edit_unit_frame.pack_forget()
            self.add_unit_button.pack(pady=20)
            self.upload_units_button.pack(pady=20)
            self.template_button.pack(pady=20)

    def cancel_edit_unit(self):
        self.edit_unit_frame.pack_forget()
        self.add_unit_button.pack(pady=20)
        self.upload_units_button.pack(pady=20)
        self.template_button.pack(pady=20)

    def show_edit_unit(event):
        selected = event.units_tree.selection()[0]
        unit = Persistance.session.query(Unit.Unit).filter_by(
            unit_sequence=event.units_tree.item(selected)['values'][0]).first()
        event.edit_unit_name.set(unit.unit_name)
        event.edit_unit_sequence.set(str(unit.unit_sequence))
        event.edit_unit_opening_date_entry.entry.delete(0, END)
        event.edit_unit_opening_date_entry.entry.insert(0, unit.unit_opening_date.strftime('%m/%d/%Y'))
        event.edit_unit_closing_date_entry.entry.delete(0, END)
        event.edit_unit_closing_date_entry.entry.insert(0, unit.unit_closing_date.strftime('%m/%d/%Y'))
        event.edit_unit_end_date_entry.entry.delete(0, END)
        event.edit_unit_end_date_entry.entry.insert(0, unit.unit_end_date.strftime('%m/%d/%Y'))
        event.edit_unit_description_text.delete("1.0", END)
        event.edit_unit_description_text.insert("1.0", unit.unit_description)
        event.add_unit_button.pack_forget()
        event.upload_units_button.pack_forget()
        event.edit_unit_frame.pack(padx=5, pady=15)

    def reload_units(self):
        self.units_tree.delete(*self.units_tree.get_children())
        # Load units from database

