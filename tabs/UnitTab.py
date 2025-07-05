#**********************************************************************************
#                       UNIT TAB
#**********************************************************************************
import ttkbootstrap as tb
from tabs.BaseTab import BaseTab
import csv
from tkinter import filedialog
from Unit import Unit
from utils.csv_handler import generate_csv_template
from datetime import datetime
from tkinter import messagebox, END, W, CENTER, NO
from tkinter.ttk import Treeview
import Persistance


class UnitsTab(BaseTab):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.create_header()
        self.create_treeview()
        self.setup_treeview_columns()
        self.create_new_unit_form()
        self.create_edit_unit_form()
        self.setup_buttons()


    def create_header(self):
        self.objectives_label = tb.Label(self, text="Objectives", font=("Helvetica", 18))
        self.objectives_label.pack(pady=20)

    def create_treeview(self):
        self.units_tree = tb.Treeview(self, bootstyle="primary")
        self.units_tree['columns'] = ('Sequence', 'Name', 'Opening Date', 'End Date', 'Closing Date')
        self.setup_treeview_columns()
        self.reload_units()

    def setup_treeview_columns(self):
        # Format columns
        self.units_tree.column("#0", width=0, stretch=NO)
        self.units_tree.column("Sequence", anchor=CENTER, width=80)
        self.units_tree.column("Name", anchor=W, width=200)
        self.units_tree.column("Opening Date", anchor=CENTER, width=120)
        self.units_tree.column("End Date", anchor=CENTER, width=120)
        self.units_tree.column("Closing Date", anchor=CENTER, width=120)
        self.units_tree.bind("<Double-1>", self.show_edit_unit)
        self.units_tree.pack(pady=10, padx=10)

        # Create headings
        self.units_tree.heading("#0", text="", anchor=W)
        self.units_tree.heading("Sequence", text="Sequence", anchor=CENTER)
        self.units_tree.heading("Name", text="Name", anchor=W)
        self.units_tree.heading("Opening Date", text="Opening Date", anchor=CENTER)
        self.units_tree.heading("End Date", text="End Date", anchor=CENTER)
        self.units_tree.heading("Closing Date", text="Closing Date", anchor=CENTER)


    def create_new_unit_form(self):

        # variables for creating a new unit
        self.new_unit_name = tb.StringVar(value="")
        self.new_unit_sequence = tb.StringVar(value="")
        self.new_unit_opening_date = tb.StringVar(value="")
        self.new_unit_closing_date = tb.StringVar(value="")
        self.new_unit_end_date = tb.StringVar(value="")
        self.new_unit_description = tb.StringVar(value="")

        # new unit GUI items
        self.new_unit_frame = tb.Frame(self.unit_tab)
        self.validation_label = tb.Label(self.new_unit_frame, text="", bootstyle="danger")
        self.validation_label.grid(row=5, column=0, columnspan=5, pady=5)
        self.new_unit_name_label = tb.Label(self.new_unit_frame, text="unit name", width=15)
        self.new_unit_name_label.grid(row=0, column=0, padx=10, pady=10)
        self.new_unit_name_entry = tb.Entry(self.new_unit_frame, textvariable=self.new_unit_name, width=50)
        self.new_unit_name_entry.grid(row=0, column=1, padx=10, pady=10)
        self.new_unit_sequence_label = tb.Label(self.new_unit_frame, text="sequence", width=10)
        self.new_unit_sequence_label.grid(row=0, column=3, padx=10, pady=10)
        self.new_unit_sequence_entry = tb.Entry(self.new_unit_frame, textvariable=self.new_unit_sequence, width=20)
        self.new_unit_sequence_entry.grid(row=0, column=4, padx=10, pady=10)
        self.new_unit_sequence_opening_date_label = tb.Label(self.new_unit_frame, text="opening date", width=15)
        self.new_unit_sequence_opening_date_label.grid(row=1, column=0, padx=10, pady=10)
        self.new_unit_opening_date_entry = tb.DateEntry(self.new_unit_frame, width=15)
        self.new_unit_opening_date_entry.grid(row=1, column=1, padx=10, pady=10)
        self.new_unit_sequence_end_date_label = tb.Label(self.new_unit_frame, text="End date", width=15)
        self.new_unit_sequence_end_date_label.grid(row=1, column=3, padx=10, pady=10)
        self.new_unit_end_date_entry = tb.DateEntry(self.new_unit_frame, width=15)
        self.new_unit_end_date_entry.grid(row=1, column=4, padx=10, pady=10)
        self.new_unit_closing_date_label = tb.Label(self.new_unit_frame, text="Closing date", width=15)
        self.new_unit_closing_date_label.grid(row=2, column=0, padx=10, pady=10)
        self.new_unit_closing_date_entry = tb.DateEntry(self.new_unit_frame, width=15)
        self.new_unit_closing_date_entry.grid(row=2, column=1, padx=10, pady=10)
        self.new_unit_description_label = tb.Label(self.new_unit_frame, text="Description", width=15)
        self.new_unit_description_label.grid(row=3, column=0, padx=10, pady=10)
        self.new_unit_description_text = tb.Text(self.new_unit_frame, width=50, height=4)
        self.new_unit_description_text.grid(row=3, column=1, columnspan=4, padx=10, pady=10)

    def create_edit_unit_form(self):
        # edit unit GUI items
        # variables for editing a unit
        self.edit_unit_name = tb.StringVar(value="")
        self.edit_unit_sequence = tb.StringVar(value="")
        edit_unit_opening_date = tb.StringVar(value="")
        edit_unit_closing_date = tb.StringVar(value="")
        edit_unit_end_date = tb.StringVar(value="")
        edit_unit_description = tb.StringVar(value="")

        # edit unit GUI items
        self.edit_unit_frame = tb.Frame(self.unit_tab)
        self.edit_validation_label = tb.Label(self.edit_unit_frame, text="", bootstyle="danger")
        self. edit_validation_label.grid(row=5, column=0, columnspan=5, pady=5)
        self. edit_unit_name_label = tb.Label(self.edit_unit_frame, text="unit name", width=15)
        self. edit_unit_name_label.grid(row=0, column=0, padx=10, pady=10)
        self. edit_unit_name_entry = tb.Entry(self.edit_unit_frame, textvariable=self.edit_unit_name, width=50)
        self. edit_unit_name_entry.grid(row=0, column=1, padx=10, pady=10)
        self. edit_unit_sequence_label = tb.Label(self.edit_unit_frame, text="sequence", width=10)
        self. edit_unit_sequence_label.grid(row=0, column=3, padx=10, pady=10)
        self.edit_unit_sequence_entry = tb.Entry(self.edit_unit_frame, textvariable=self.edit_unit_sequence, width=20)
        self.edit_unit_sequence_entry.grid(row=0, column=4, padx=10, pady=10)
        self.edit_unit_sequence_opening_date_label = tb.Label(self.edit_unit_frame, text="opening date", width=15)
        self.edit_unit_sequence_opening_date_label.grid(row=1, column=0, padx=10, pady=10)
        self.edit_unit_opening_date_entry = tb.DateEntry(self.edit_unit_frame, width=15)
        self.edit_unit_opening_date_entry.grid(row=1, column=1, padx=10, pady=10)
        self.edit_unit_sequence_end_date_label = tb.Label(self.edit_unit_frame, text="End date", width=15)
        self.edit_unit_sequence_end_date_label.grid(row=1, column=3, padx=10, pady=10)
        self.edit_unit_end_date_entry = tb.DateEntry(self.edit_unit_frame, width=15)
        self.edit_unit_end_date_entry.grid(row=1, column=4, padx=10, pady=10)
        self.edit_unit_closing_date_label = tb.Label(self.edit_unit_frame, text="Closing date", width=15)
        self.edit_unit_closing_date_label.grid(row=2, column=0, padx=10, pady=10)
        self.edit_unit_closing_date_entry = tb.DateEntry(self.edit_unit_frame, width=15)
        self.edit_unit_closing_date_entry.grid(row=2, column=1, padx=10, pady=10)
        self.edit_unit_description_label = tb.Label(self.edit_unit_frame, text="Description", width=15)
        self.edit_unit_description_label.grid(row=3, column=0, padx=10, pady=10)
        self. edit_unit_description_text = tb.Text(self.edit_unit_frame, width=50, height=4)
        self.edit_unit_description_text.grid(row=3, column=1, columnspan=4, padx=10, pady=10)

    def setup_buttons(self):
        self.upload_units_button = tb.Button(self.unit_tab, text="upload CSV", bootstyle="default outline", command=self.upload_unit_csv)
        self.upload_units_button.pack(pady=20)

        self.template_button = tb.Button(self.unit_tab, text="Download Template", bootstyle="info outline",command=generate_csv_template(['unit_name', 'sequence', 'opening_date', 'end_date', 'closing_date', 'description'],'unit_template.csv'))
        self.template_button.pack(pady=20)

        self.add_unit_button = tb.Button(self.unit_tab, text="Add Unit", bootstyle="danger", command=self.show_new_unit)
        self.add_unit_button.pack(pady=20)

        self.new_unit_submit = tb.Button(self.new_unit_frame, text="Create", bootstyle="success", command=self.create_new_unit)
        self.new_unit_submit.grid(row=4, column=0, columnspan=5, pady=20)

        self.new_unit_cancel = tb.Button(self.new_unit_frame, text="Cancel", bootstyle="danger", command=self.cancel_new_unit)
        self.new_unit_cancel.grid(row=4, column=1, columnspan=5, pady=20)

        self.edit_unit_submit = tb.Button(self.edit_unit_frame, text="Update", bootstyle="success", command=self.submit_edit_unit)
        self.edit_unit_submit.grid(row=4, column=0, columnspan=2, pady=20)

        self.edit_unit_delete = tb.Button(self.edit_unit_frame, text="Delete", bootstyle="danger", command=self.delete_unit)
        self.edit_unit_delete.grid(row=4, column=2, columnspan=1, pady=20)

        self.edit_unit_cancel = tb.Button(self.edit_unit_frame, text="Cancel", bootstyle="warning", command=self.cancel_edit_unit)
        self.edit_unit_cancel.grid(row=4, column=3, columnspan=2, pady=20)

    def reload_units(self):
        self.units_tree.delete(*self.units_tree.get_children())
        # Load units from database
        units = Persistance.session.query(Unit.Unit).order_by(Unit.Unit.unit_sequence).all()
        for unit in units:
          self.units_tree.insert(parent='', index='end', values=(
               unit.unit_sequence,
               unit.unit_name,
               unit.unit_opening_date.strftime('%Y-%m-%d'),
               unit.unit_end_date.strftime('%Y-%m-%d'),
               unit.unit_closing_date.strftime('%Y-%m-%d')
               )
            )



    def show_new_unit(self):

        self.add_unit_button.pack_forget()
        self.upload_units_button.pack_forget()
        self.template_button.pack_forget()
        self.new_unit_frame.pack(padx=5, pady=15)


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

        if self.validate_unit_fields():
            Unit.Unit(
                self.new_unit_name.get(),
                self.new_unit_sequence.get(),
                datetime.strptime(self.new_unit_opening_date_entry.entry.get(), '%m/%d/%Y'),
                datetime.strptime(self.new_unit_closing_date_entry.entry.get(), '%m/%d/%Y'),
                datetime.strptime(self.new_unit_end_date_entry.entry.get(), '%m/%d/%Y'),
                self.new_unit_description_text.get("1.0", END)
            ).add_unit()
            self.reload_units()
            self.new_unit_frame.pack_forget()
            self.add_unit_button.pack(pady=20)
            self.upload_units_button.pack(pady=20)


    def cancel_new_unit(self):
        #reload_units()
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
        unit = Persistance.session.query(Unit.Unit).filter_by(unit_sequence=event.units_tree.item(selected)['values'][0]).first()
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





