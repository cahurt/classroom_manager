import csv
from datetime import datetime
from tkinter import filedialog

import ttkbootstrap as tb
from Model import Unit
from GUI_components.BaseTab import BaseTab
from GUI_components.BaseForm import BaseForm
from GUI_components.BaseTreeView import BaseTreeView



class UnitTab(BaseTab):
    # Class constants
    FIELD_DEFINITIONS = [
        ('Name', 'unit_name', str),
        ('Sequence', 'sequence', int),
        ('Opening Date', 'opening_date', datetime),
        ('End Date', 'end_date', datetime),
        ('Closing Date', 'closing_date', datetime),
        ('Description', 'description', None)
    ]

    TREE_COLUMNS = ['unit_name', 'sequence', 'opening_date',
                    'end_date', 'closing_date', 'description']

    CSV_TEMPLATE_HEADERS = ['unit_name', 'sequence', 'opening_date',
                            'end_date', 'closing_date', 'description']

    DATE_FORMAT = '%Y-%m-%d'
    DISPLAY_DATE_FORMAT = '%m/%d/%Y'

    def __init__(self, notebook):
        super().__init__(notebook)
        self.setup_variables()
        self.setup_ui()

    def setup_variables(self):
        self.new_unit_vars = self._create_unit_variables()
        self.edit_unit_vars = self._create_unit_variables()

    def _create_unit_variables(self):
        return {
            'name': tb.StringVar(value=""),
            'sequence': tb.StringVar(value=""),
            'opening_date': tb.StringVar(value=""),
            'closing_date': tb.StringVar(value=""),
            'end_date': tb.StringVar(value=""),
            'description': tb.StringVar(value="")
        }

    def setup_ui(self):
        self._create_header()
        self._create_treeview()
        self._create_forms()
        self._setup_buttons()

    def _create_header(self):
        self.header_label = tb.Label(self, text="Units", font=("Helvetica", 18))
        self.header_label.grid(pady=20)

    def _create_treeview(self):
        self.units_tree = BaseTreeView(self, self.TREE_COLUMNS)
        self.units_tree.grid(padx=5, pady=15)
        self.units_tree.bind('<Double-1>', lambda e: self.show_edit_unit())
        self.reload_units()

    def _create_forms(self):
        self.main_button_panel = BaseForm(self)
        self.main_button_panel.grid(pady=20)

        self.new_unit_form = BaseForm(self)
        self.new_unit_form.show_standard_fields(self.FIELD_DEFINITIONS, 4)

        self.edit_unit_form = BaseForm(self)
        self.edit_unit_form.show_standard_fields(self.FIELD_DEFINITIONS, 4)

    def create_new_unit(self):
        unit_values = self.new_unit_form.validate_and_collect_form_values(self.main_button_panel)
        if unit_values:
            try:
                self._save_new_unit(unit_values)
                self.reload_units()
            except Exception as e:
                self.show_error(f"Failed to create unit: {str(e)}")

    def _save_new_unit(self, values):
        new_unit = Unit.Unit(
            values.get('unit_name'),
            values.get('sequence'),
            values.get('opening_date'),
            values.get('closing_date'),
            values.get('end_date'),
            values.get('description')
        )
        new_unit.add_new_unit()
        print("Unit created:", values)

    def upload_unit_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            try:
                self._process_csv_file(file_path)
                self.show_success("Units imported successfully")
            except Exception as e:
                self.show_error(f"Failed to process CSV: {str(e)}")
            finally:
                self.reload_units()

    def _process_csv_file(self, file_path):
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            first_row = next(csv_reader)

            if first_row != self.CSV_TEMPLATE_HEADERS:
                self._process_unit_row(first_row)

            for row in csv_reader:
                self._process_unit_row(row)

    def _process_unit_row(self, row):
        try:
            Unit.Unit(
                row[0],
                int(row[1]),
                datetime.strptime(row[2], self.DATE_FORMAT),
                datetime.strptime(row[4], self.DATE_FORMAT),
                datetime.strptime(row[3], self.DATE_FORMAT),
                row[5]
            ).add_new_unit()
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid data in CSV row: {str(e)}")



#**********************************************************************************
#                       UNIT TAB
#**********************************************************************************
def get_all_units(self):
    return Persistance.session.query(Unit.Unit).order_by(Unit.Unit.unit_sequence).all()


def reload_units(self):
    self.units_tree.delete(*self.units_tree.get_children())
    # Load units from database
    self.units = self.get_all_units()
    for unit in self.units:
        self.units_tree.insert(parent='', index='end', values=(
            unit.unit_sequence,
            unit.unit_name,
            unit.unit_opening_date.strftime('%Y-%m-%d'),
            unit.unit_end_date.strftime('%Y-%m-%d'),
            unit.unit_closing_date.strftime('%Y-%m-%d')
        ))
    self.units_tree.grid(pady=10, padx=10)

unit_tab = tb.Frame(main_notebook)
objective_tab = tb.Frame(main_notebook)
consumable_tab = tb.Frame(main_notebook)
classroom_location_tab = tb.Frame(main_notebook)

units_label = Label(unit_tab, text="Units", font=("Helvetica", 18))
units_label.pack(pady=20)

# Create Treeview
units_tree = tb.Treeview(unit_tab, bootstyle="primary")
units_tree['columns'] = ('Sequence', 'Name', 'Opening Date', 'End Date', 'Closing Date')

# Format columns
units_tree.column("#0", width=0, stretch=NO)
units_tree.column("Sequence", anchor=CENTER, width=80)
units_tree.column("Name", anchor=W, width=200)
units_tree.column("Opening Date", anchor=CENTER, width=120)
units_tree.column("End Date", anchor=CENTER, width=120)
units_tree.column("Closing Date", anchor=CENTER, width=120)

# Create headings
units_tree.heading("#0", text="", anchor=W)
units_tree.heading("Sequence", text="Sequence", anchor=CENTER)
units_tree.heading("Name", text="Name", anchor=W)
units_tree.heading("Opening Date", text="Opening Date", anchor=CENTER)
units_tree.heading("End Date", text="End Date", anchor=CENTER)
units_tree.heading("Closing Date", text="Closing Date", anchor=CENTER)

def reload_units():
    units_tree.delete(*units_tree.get_children())
    # Load units from database
    units = Persistance.session.query(Unit.Unit).order_by(Unit.Unit.unit_sequence).all()
    for unit in units:
      units_tree.insert(parent='', index='end', values=(
            unit.unit_sequence,
           unit.unit_name,
           unit.unit_opening_date.strftime('%Y-%m-%d'),
           unit.unit_end_date.strftime('%Y-%m-%d'),
           unit.unit_closing_date.strftime('%Y-%m-%d')
        )
            )
units_tree.pack(pady=10, padx=10)
reload_units()


def generate_csv_template():


    file_path = filedialog.asksaveasfilename(
        defaultextension='.csv',
        filetypes=[("CSV Files", "*.csv")]
    )
    if file_path:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['unit_name', 'sequence', 'opening_date', 'end_date', 'closing_date', 'description'])


def show_new_unit():

    add_unit_button.pack_forget()
    upload_units_button.pack_forget()
    template_button.pack_forget()
    new_unit_frame.pack(padx=5, pady=15)


add_unit_button = tb.Button(unit_tab, text="Add Unit", bootstyle="danger", command=show_new_unit)
add_unit_button.pack(pady=20)


def upload_csv():
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
                    ).add_new_unit()
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
                    ).add_new_unit()
                except (ValueError, IndexError) as e:
                    messagebox.showerror("Error", f"Invalid data in CSV: {str(e)}")
                    reload_units()
                    return

            reload_units()
            messagebox.showinfo("Success", "Units imported successfully")
            reload_units()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV file: {str(e)}")
        reload_units()


upload_units_button = tb.Button(unit_tab, text="upload CSV", bootstyle="default outline", command=upload_csv)
upload_units_button.pack(pady=20)

template_button = tb.Button(unit_tab, text="Download Template", bootstyle="info outline", command=generate_csv_template)
template_button.pack(pady=20)

# variables for creating a new unit
new_unit_name = tb.StringVar(value="")
new_unit_sequence = tb.StringVar(value="")
new_unit_opening_date = tb.StringVar(value="")
new_unit_closing_date = tb.StringVar(value="")
new_unit_end_date = tb.StringVar(value="")
new_unit_description = tb.StringVar(value="")

# new unit GUI items
new_unit_frame = tb.Frame(unit_tab)
validation_label = tb.Label(new_unit_frame, text="", bootstyle="danger")
validation_label.grid(row=5, column=0, columnspan=5, pady=5)
new_unit_name_label = tb.Label(new_unit_frame, text="unit name", width=15)
new_unit_name_label.grid(row=0, column=0, padx=10, pady=10)
new_unit_name_entry = tb.Entry(new_unit_frame, textvariable=new_unit_name, width=50)
new_unit_name_entry.grid(row=0, column=1, padx=10, pady=10)
new_unit_sequence_label = tb.Label(new_unit_frame, text="sequence", width=10)
new_unit_sequence_label.grid(row=0, column=3, padx=10, pady=10)
new_unit_sequence_entry = tb.Entry(new_unit_frame, textvariable=new_unit_sequence, width=20)
new_unit_sequence_entry.grid(row=0, column=4, padx=10, pady=10)
new_unit_sequence_opening_date_label = tb.Label(new_unit_frame, text="opening date", width=15)
new_unit_sequence_opening_date_label.grid(row=1, column=0, padx=10, pady=10)
new_unit_opening_date_entry = tb.DateEntry(new_unit_frame, width=15)
new_unit_opening_date_entry.grid(row=1, column=1, padx=10, pady=10)
new_unit_sequence_end_date_label = tb.Label(new_unit_frame, text="End date", width=15)
new_unit_sequence_end_date_label.grid(row=1, column=3, padx=10, pady=10)
new_unit_end_date_entry = tb.DateEntry(new_unit_frame, width=15)
new_unit_end_date_entry.grid(row=1, column=4, padx=10, pady=10)
new_unit_closing_date_label = tb.Label(new_unit_frame, text="Closing date", width=15)
new_unit_closing_date_label.grid(row=2, column=0, padx=10, pady=10)
new_unit_closing_date_entry = tb.DateEntry(new_unit_frame, width=15)
new_unit_closing_date_entry.grid(row=2, column=1, padx=10, pady=10)
new_unit_description_label = tb.Label(new_unit_frame, text="Description", width=15)
new_unit_description_label.grid(row=3, column=0, padx=10, pady=10)
new_unit_description_text = tb.Text(new_unit_frame, width=50, height=4)
new_unit_description_text.grid(row=3, column=1, columnspan=4, padx=10, pady=10)


def validate_unit_fields():
    if not new_unit_name.get().strip():
        validation_label.config(text="Unit name is required")
        return False
    if not new_unit_sequence.get().strip() or not new_unit_sequence.get().strip().isdigit():
        validation_label.config(text="Sequence is required and must be a number")
        return False
    if not new_unit_opening_date_entry.entry.get().strip():
        validation_label.config(text="Opening date is required")
        return False
    if not new_unit_closing_date_entry.entry.get().strip():
        validation_label.config(text="Closing date is required")
        return False
    if not new_unit_end_date_entry.entry.get().strip():
        validation_label.config(text="End date is required")
        return False
    if not new_unit_description_text.get("1.0", END).strip():
        validation_label.config(text="Description is required")
        return False
    validation_label.config(text="")
    return True

def create_new_unit():

    if validate_unit_fields():
        Unit.Unit(
            new_unit_name.get(),
            new_unit_sequence.get(),
            datetime.strptime(new_unit_opening_date_entry.entry.get(), '%m/%d/%Y'),
            datetime.strptime(new_unit_closing_date_entry.entry.get(), '%m/%d/%Y'),
            datetime.strptime(new_unit_end_date_entry.entry.get(), '%m/%d/%Y'),
            new_unit_description_text.get("1.0", END)
        ).add_new_unit()
        reload_units()
        new_unit_frame.pack_forget()
        add_unit_button.pack(pady=20)
        upload_units_button.pack(pady=20)


def cancel_new_unit():
    #reload_units()
    print("cancel")
    new_unit_frame.pack_forget()
    add_unit_button.pack(pady=20)
    upload_units_button.pack(pady=20)
    template_button.pack(pady=20)


new_unit_submit = tb.Button(new_unit_frame, text="Create", bootstyle="success", command=create_new_unit)
new_unit_submit.grid(row=4, column=0, columnspan=5, pady=20)

new_unit_cancel = tb.Button(new_unit_frame, text="Cancel", bootstyle="danger", command=cancel_new_unit)
new_unit_cancel.grid(row=4, column=1, columnspan=5, pady=20)


# edit unit GUI items
# variables for editing a unit
edit_unit_name = tb.StringVar(value="")
edit_unit_sequence = tb.StringVar(value="")
edit_unit_opening_date = tb.StringVar(value="")
edit_unit_closing_date = tb.StringVar(value="")
edit_unit_end_date = tb.StringVar(value="")
edit_unit_description = tb.StringVar(value="")

# edit unit GUI items
edit_unit_frame = tb.Frame(unit_tab)
edit_validation_label = tb.Label(edit_unit_frame, text="", bootstyle="danger")
edit_validation_label.grid(row=5, column=0, columnspan=5, pady=5)
edit_unit_name_label = tb.Label(edit_unit_frame, text="unit name", width=15)
edit_unit_name_label.grid(row=0, column=0, padx=10, pady=10)
edit_unit_name_entry = tb.Entry(edit_unit_frame, textvariable=edit_unit_name, width=50)
edit_unit_name_entry.grid(row=0, column=1, padx=10, pady=10)
edit_unit_sequence_label = tb.Label(edit_unit_frame, text="sequence", width=10)
edit_unit_sequence_label.grid(row=0, column=3, padx=10, pady=10)
edit_unit_sequence_entry = tb.Entry(edit_unit_frame, textvariable=edit_unit_sequence, width=20)
edit_unit_sequence_entry.grid(row=0, column=4, padx=10, pady=10)
edit_unit_sequence_opening_date_label = tb.Label(edit_unit_frame, text="opening date", width=15)
edit_unit_sequence_opening_date_label.grid(row=1, column=0, padx=10, pady=10)
edit_unit_opening_date_entry = tb.DateEntry(edit_unit_frame, width=15)
edit_unit_opening_date_entry.grid(row=1, column=1, padx=10, pady=10)
edit_unit_sequence_end_date_label = tb.Label(edit_unit_frame, text="End date", width=15)
edit_unit_sequence_end_date_label.grid(row=1, column=3, padx=10, pady=10)
edit_unit_end_date_entry = tb.DateEntry(edit_unit_frame, width=15)
edit_unit_end_date_entry.grid(row=1, column=4, padx=10, pady=10)
edit_unit_closing_date_label = tb.Label(edit_unit_frame, text="Closing date", width=15)
edit_unit_closing_date_label.grid(row=2, column=0, padx=10, pady=10)
edit_unit_closing_date_entry = tb.DateEntry(edit_unit_frame, width=15)
edit_unit_closing_date_entry.grid(row=2, column=1, padx=10, pady=10)
edit_unit_description_label = tb.Label(edit_unit_frame, text="Description", width=15)
edit_unit_description_label.grid(row=3, column=0, padx=10, pady=10)
edit_unit_description_text = tb.Text(edit_unit_frame, width=50, height=4)
edit_unit_description_text.grid(row=3, column=1, columnspan=4, padx=10, pady=10)


def validate_edit_unit_fields():
    if not edit_unit_name.get().strip():
        edit_validation_label.config(text="Unit name is required")
        return False
    if not edit_unit_sequence.get().strip() or not edit_unit_sequence.get().strip().isdigit():
        edit_validation_label.config(text="Sequence is required and must be a number")
        return False
    if not edit_unit_opening_date_entry.entry.get().strip():
        edit_validation_label.config(text="Opening date is required")
        return False
    if not edit_unit_closing_date_entry.entry.get().strip():
        edit_validation_label.config(text="Closing date is required")
        return False
    if not edit_unit_end_date_entry.entry.get().strip():
        edit_validation_label.config(text="End date is required")
        return False
    if not edit_unit_description_text.get("1.0", END).strip():
        edit_validation_label.config(text="Description is required")
        return False
    edit_validation_label.config(text="")
    return True


def submit_edit_unit():
    if validate_edit_unit_fields():
        selected = units_tree.selection()[0]
        unit = Persistance.session.query(Unit.Unit).filter_by(
            unit_sequence=units_tree.item(selected)['values'][0]).first()
        unit.unit_name = edit_unit_name.get()
        unit.unit_sequence = edit_unit_sequence.get()
        unit.unit_opening_date = datetime.strptime(edit_unit_opening_date_entry.entry.get(), '%m/%d/%Y')
        unit.unit_closing_date = datetime.strptime(edit_unit_closing_date_entry.entry.get(), '%m/%d/%Y')
        unit.unit_end_date = datetime.strptime(edit_unit_end_date_entry.entry.get(), '%m/%d/%Y')
        unit.unit_description = edit_unit_description_text.get("1.0", END)
        unit.update_unit()
        reload_units()
        edit_unit_frame.pack_forget()
        add_unit_button.pack(pady=20)
        upload_units_button.pack(pady=20)

def delete_unit():

    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this unit?"):
        selected = units_tree.selection()[0]
        unit = Persistance.session.query(Unit.Unit).filter_by(
        unit_sequence=units_tree.item(selected)['values'][0]).first()
        unit._delete_selected_unit()
        reload_units()
        edit_unit_frame.pack_forget()
        add_unit_button.pack(pady=20)
        upload_units_button.pack(pady=20)
        template_button.pack(pady=20)


def cancel_edit_unit():
    edit_unit_frame.pack_forget()
    add_unit_button.pack(pady=20)
    upload_units_button.pack(pady=20)
    template_button.pack(pady=20)


def show_edit_unit(event):
    selected = units_tree.selection()[0]
    unit = Persistance.session.query(Unit.Unit).filter_by(unit_sequence=units_tree.item(selected)['values'][0]).first()
    edit_unit_name.set(unit.unit_name)
    edit_unit_sequence.set(str(unit.unit_sequence))
    edit_unit_opening_date_entry.entry.delete(0, END)
    edit_unit_opening_date_entry.entry.insert(0, unit.unit_opening_date.strftime('%m/%d/%Y'))
    edit_unit_closing_date_entry.entry.delete(0, END)
    edit_unit_closing_date_entry.entry.insert(0, unit.unit_closing_date.strftime('%m/%d/%Y'))
    edit_unit_end_date_entry.entry.delete(0, END)
    edit_unit_end_date_entry.entry.insert(0, unit.unit_end_date.strftime('%m/%d/%Y'))
    edit_unit_description_text.delete("1.0", END)
    edit_unit_description_text.insert("1.0", unit.unit_description)
    add_unit_button.pack_forget()
    upload_units_button.pack_forget()
    edit_unit_frame.pack(padx=5, pady=15)


edit_unit_submit = tb.Button(edit_unit_frame, text="Update", bootstyle="success", command=submit_edit_unit)
edit_unit_submit.grid(row=4, column=0, columnspan=2, pady=20)

edit_unit_delete = tb.Button(edit_unit_frame, text="Delete", bootstyle="danger", command=delete_unit)
edit_unit_delete.grid(row=4, column=2, columnspan=1, pady=20)

edit_unit_cancel = tb.Button(edit_unit_frame, text="Cancel", bootstyle="warning", command=cancel_edit_unit)
edit_unit_cancel.grid(row=4, column=3, columnspan=2, pady=20)

units_tree.bind("<Double-1>", show_edit_unit)


#**********************************************************************************
#                       Objectives Tab
#**********************************************************************************

objectives_label = Label(objective_tab, text="Objectives", font=("Helvetica", 18))
objectives_label.pack(pady=20)

# Create Objectives Treeview
objectives_tree = tb.Treeview(objective_tab, bootstyle="primary")
objectives_tree['columns'] = ('Name', 'Description')

# Format columns
objectives_tree.column("#0", width=0, stretch=NO)
objectives_tree.column("Name", anchor=W, width=200)
objectives_tree.column("Description", anchor=W, width=400)

# Create headings
objectives_tree.heading("#0", text="", anchor=W)
objectives_tree.heading("Name", text="Name", anchor=W)
objectives_tree.heading("Description", text="Description", anchor=W)


def reload_objectives():
    objectives_tree.delete(*objectives_tree.get_children())
    # Load objectives from database
    objectives = Persistance.session.query(Objective.Objective).all()
    for objective in objectives:
        objectives_tree.insert(parent='', index='end', values=(
            objective.objective_name,
            objective.objective_description
        ))


objectives_tree.pack(pady=10, padx=10)
reload_objectives()

# Add buttons
add_objective_button = tb.Button(objective_tab, text="Add Objective", bootstyle="danger")
add_objective_button.pack(pady=20)


def generate_objectives_csv_template():
    file_path = filedialog.asksaveasfilename(
        defaultextension='.csv',
        filetypes=[("CSV Files", "*.csv")]
    )
    if file_path:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['objective_name', 'description'])


def upload_objectives_csv():
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
            if first_row == ['objective_name', 'description']:
                # Skip the header row
                pass
            else:
                # If not header, process first row as data
                try:
                    Objective.Objective(
                        first_row[0],
                        first_row[1]
                    ).add_objective()
                except (ValueError, IndexError) as e:
                    messagebox.showerror("Error", f"Invalid data in CSV: {str(e)}")
                    return

            for row in csv_reader:
                try:
                    Objective.Objective(
                        row[0],
                        row[1]
                    ).add_objective()
                except (ValueError, IndexError) as e:
                    messagebox.showerror("Error", f"Invalid data in CSV: {str(e)}")
                    reload_objectives()
                    return

            reload_objectives()
            messagebox.showinfo("Success", "Objectives imported successfully")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV file: {str(e)}")
        reload_objectives()


upload_objectives_button = tb.Button(objective_tab, text="Upload CSV", bootstyle="default outline",
                                     command=upload_objectives_csv)
upload_objectives_button.pack(pady=20)

template_objectives_button = tb.Button(objective_tab, text="Download Template", bootstyle="info outline",
                                       command=generate_objectives_csv_template)
template_objectives_button.pack(pady=20)

# Form variables
new_objective_name = tb.StringVar(value="")
new_objective_description = tb.StringVar(value="")

# New objective form frame
new_objective_frame = tb.Frame(objective_tab)
new_objective_validation_label = tb.Label(new_objective_frame, text="", bootstyle="danger")
new_objective_validation_label.grid(row=2, column=0, columnspan=2, pady=5)

new_objective_name_label = tb.Label(new_objective_frame, text="Name", width=15)
new_objective_name_label.grid(row=0, column=0, padx=10, pady=10)
new_objective_name_entry = tb.Entry(new_objective_frame, textvariable=new_objective_name, width=50)
new_objective_name_entry.grid(row=0, column=1, padx=10, pady=10)

new_objective_description_label = tb.Label(new_objective_frame, text="Description", width=15)
new_objective_description_label.grid(row=1, column=0, padx=10, pady=10)
new_objective_description_text = tb.Text(new_objective_frame, width=50, height=4)
new_objective_description_text.grid(row=1, column=1, padx=10, pady=10)


def show_new_objective():
    add_objective_button.pack_forget()
    upload_objectives_button.pack_forget()
    template_objectives_button.pack_forget()
    new_objective_frame.pack(padx=5, pady=15)


add_objective_button.configure(command=show_new_objective)


def validate_objective_fields():
    if not new_objective_name.get().strip():
        new_objective_validation_label.config(text="Name is required")
        return False
    if not new_objective_description_text.get("1.0", END).strip():
        new_objective_validation_label.config(text="Description is required")
        return False
    new_objective_validation_label.config(text="")
    return True


def create_new_objective():
    if validate_objective_fields():
        objective = Objective.Objective(
            new_objective_name.get(),
            new_objective_description_text.get("1.0", END)
        )
        objective.add_objective()
        reload_objectives()
        new_objective_frame.pack_forget()
        add_objective_button.pack(pady=20)
        upload_objectives_button.pack(pady=20)
        template_objectives_button.pack(pady=20)


def cancel_new_objective():
    new_objective_frame.pack_forget()
    add_objective_button.pack(pady=20)
    upload_objectives_button.pack(pady=20)
    template_objectives_button.pack(pady=20)


new_objective_submit = tb.Button(new_objective_frame, text="Create", bootstyle="success", command=create_new_objective)
new_objective_submit.grid(row=3, column=0, columnspan=1, pady=20)

new_objective_cancel = tb.Button(new_objective_frame, text="Cancel", bootstyle="danger", command=cancel_new_objective)
new_objective_cancel.grid(row=3, column=1, columnspan=1, pady=20)

# Edit objective variables
edit_objective_name = tb.StringVar(value="")

# Edit objective form frame
edit_objective_frame = tb.Frame(objective_tab)
edit_objective_validation_label = tb.Label(edit_objective_frame, text="", bootstyle="danger")
edit_objective_validation_label.grid(row=2, column=0, columnspan=2, pady=5)

edit_objective_name_label = tb.Label(edit_objective_frame, text="Name", width=15)
edit_objective_name_label.grid(row=0, column=0, padx=10, pady=10)
edit_objective_name_entry = tb.Entry(edit_objective_frame, textvariable=edit_objective_name, width=50)
edit_objective_name_entry.grid(row=0, column=1, padx=10, pady=10)

edit_objective_description_label = tb.Label(edit_objective_frame, text="Description", width=15)
edit_objective_description_label.grid(row=1, column=0, padx=10, pady=10)
edit_objective_description_text = tb.Text(edit_objective_frame, width=50, height=4)
edit_objective_description_text.grid(row=1, column=1, padx=10, pady=10)


def validate_edit_objective_fields():
    if not edit_objective_name.get().strip():
        edit_objective_validation_label.config(text="Name is required")
        return False
    if not edit_objective_description_text.get("1.0", END).strip():
        edit_objective_validation_label.config(text="Description is required")
        return False
    edit_objective_validation_label.config(text="")
    return True


def submit_edit_objective():
    if validate_edit_objective_fields():
        selected = objectives_tree.selection()[0]
        objective = Persistance.session.query(Objective.Objective).filter_by(
            objective_name=objectives_tree.item(selected)['values'][0]).first()
        objective.objective_name = edit_objective_name.get()
        objective.objective_description = edit_objective_description_text.get("1.0", END)
        objective.update_objective()
        reload_objectives()
        edit_objective_frame.pack_forget()
        add_objective_button.pack(pady=20)
        upload_objectives_button.pack(pady=20)
        template_objectives_button.pack(pady=20)


def delete_objective():
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this objective?"):
        selected = objectives_tree.selection()[0]
        objective = Persistance.session.query(Objective.Objective).filter_by(
            objective_name=objectives_tree.item(selected)['values'][0]).first()
        objective.delete_objective()
        reload_objectives()
        edit_objective_frame.pack_forget()
        add_objective_button.pack(pady=20)
        upload_objectives_button.pack(pady=20)
        template_objectives_button.pack(pady=20)


def cancel_edit_objective():
    edit_objective_frame.pack_forget()
    add_objective_button.pack(pady=20)
    upload_objectives_button.pack(pady=20)
    template_objectives_button.pack(pady=20)


def show_edit_objective(event):
    selected = objectives_tree.selection()[0]
    objective = Persistance.session.query(Objective.Objective).filter_by(
        objective_name=objectives_tree.item(selected)['values'][0]).first()
    edit_objective_name.set(objective.objective_name)
    edit_objective_description_text.delete("1.0", END)
    edit_objective_description_text.insert("1.0", objective.objective_description)
    add_objective_button.pack_forget()
    upload_objectives_button.pack_forget()
    template_objectives_button.pack_forget()
    edit_objective_frame.pack(padx=5, pady=15)


edit_objective_submit = tb.Button(edit_objective_frame, text="Update", bootstyle="success",
                                  command=submit_edit_objective)
edit_objective_submit.grid(row=3, column=0, columnspan=1, pady=20)

edit_objective_delete = tb.Button(edit_objective_frame, text="Delete", bootstyle="danger", command=delete_objective)
edit_objective_delete.grid(row=3, column=1, columnspan=1, pady=20)

edit_objective_cancel = tb.Button(edit_objective_frame, text="Cancel", bootstyle="warning",
                                  command=cancel_edit_objective)
edit_objective_cancel.grid(row=3, column=2, columnspan=1, pady=20)

objectives_tree.bind("<Double-1>", show_edit_objective)


#**********************************************************************************
#                       CONSUMABLE TAB
#**********************************************************************************

consumables_label = Label(consumable_tab, text="Consumables", font=("Helvetica", 18))
consumables_label.pack(pady=20)

# Create Consumables Treeview
consumables_tree = tb.Treeview(consumable_tab, bootstyle="primary")
consumables_tree['columns'] = ('Name', 'Quantity', 'Location')

# Format columns
consumables_tree.column("#0", width=0, stretch=NO)
consumables_tree.column("Name", anchor=W, width=200)
consumables_tree.column("Quantity", anchor=CENTER, width=100)
consumables_tree.column("Location", anchor=W, width=200)

# Create headings
consumables_tree.heading("#0", text="", anchor=W)
consumables_tree.heading("Name", text="Name", anchor=W)
consumables_tree.heading("Quantity", text="Quantity", anchor=CENTER)
consumables_tree.heading("Location", text="Location", anchor=W)


def reload_consumables():
    consumables_tree.delete(*consumables_tree.get_children())
    # Load consumables from database
    consumables = Persistance.session.query(Consumable.Consumable).all()
    for consumable in consumables:
        consumables_tree.insert(parent='', index='end', values=(
            consumable.consumable_name,
            consumable.consumable_quantity_available,
            consumable.consumable_location.classroom_location_name if consumable.consumable_location else "No Location"
        ))


consumables_tree.pack(pady=10, padx=10)
reload_consumables()

# Add buttons
add_consumable_button = tb.Button(consumable_tab, text="Add Consumable", bootstyle="danger")
add_consumable_button.pack(pady=20)


def generate_consumables_csv_template():
    file_path = filedialog.asksaveasfilename(
        defaultextension='.csv',
        filetypes=[("CSV Files", "*.csv")]
    )
    if file_path:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['consumable_name', 'quantity', 'location'])


def upload_consumables_csv():
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
            if first_row == ['consumable_name', 'quantity', 'location']:
                # Skip the header row
                pass
            else:
                # If not header, process first row as data
                try:
                    location = Persistance.session.query(ClassroomLocation.ClassroomLocation).filter_by(
                        classroom_location_name=first_row[2]).first()
                    try:
                        quantity = int(first_row[1])
                    except ValueError:
                        messagebox.showerror("Error", "Quantity must be an integer")
                        return
                    Consumable.Consumable(
                        first_row[0],
                        quantity,
                        location
                    ).add_consumable()
                except (ValueError, IndexError) as e:
                    messagebox.showerror("Error", f"Invalid data in CSV: {str(e)}")
                    return

            for row in csv_reader:
                try:
                    location = Persistance.session.query(ClassroomLocation.ClassroomLocation).filter_by(
                        classroom_location_name=row[2]).first()
                    try:
                        quantity = int(row[1])
                    except ValueError:
                        messagebox.showerror("Error", "Quantity must be an integer")
                        reload_consumables()
                        return
                    Consumable.Consumable(
                        row[0],
                        quantity,
                        location
                    ).add_consumable()
                except (ValueError, IndexError) as e:
                    messagebox.showerror("Error", f"Invalid data in CSV: {str(e)}")
                    reload_consumables()
                    return

            reload_consumables()
            messagebox.showinfo("Success", "Consumables imported successfully")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV file: {str(e)}")
        reload_consumables()


upload_consumables_button = tb.Button(consumable_tab, text="Upload CSV", bootstyle="default outline",
                                      command=upload_consumables_csv)
upload_consumables_button.pack(pady=20)

template_consumables_button = tb.Button(consumable_tab, text="Download Template", bootstyle="info outline",
                                        command=generate_consumables_csv_template)
template_consumables_button.pack(pady=20)

# Form variables
new_consumable_name = tb.StringVar(value="")
new_consumable_quantity = tb.StringVar(value="")
new_consumable_location = tb.StringVar(value="")

# New consumable form frame
new_consumable_frame = tb.Frame(consumable_tab)
new_consumable_validation_label = tb.Label(new_consumable_frame, text="", bootstyle="danger")
new_consumable_validation_label.grid(row=3, column=0, columnspan=2, pady=5)

new_consumable_name_label = tb.Label(new_consumable_frame, text="Name", width=15)
new_consumable_name_label.grid(row=0, column=0, padx=10, pady=10)
new_consumable_name_entry = tb.Entry(new_consumable_frame, textvariable=new_consumable_name, width=50)
new_consumable_name_entry.grid(row=0, column=1, padx=10, pady=10)

new_consumable_quantity_label = tb.Label(new_consumable_frame, text="Quantity", width=15)
new_consumable_quantity_label.grid(row=1, column=0, padx=10, pady=10)
new_consumable_quantity_entry = tb.Entry(new_consumable_frame, textvariable=new_consumable_quantity, width=50)
new_consumable_quantity_entry.grid(row=1, column=1, padx=10, pady=10)

new_consumable_location_label = tb.Label(new_consumable_frame, text="Location", width=15)
new_consumable_location_label.grid(row=2, column=0, padx=10, pady=10)
new_consumable_location_entry = tb.Entry(new_consumable_frame, textvariable=new_consumable_location, width=50)
new_consumable_location_entry.grid(row=2, column=1, padx=10, pady=10)


def show_new_consumable():
    add_consumable_button.pack_forget()
    upload_consumables_button.pack_forget()
    template_consumables_button.pack_forget()
    new_consumable_frame.pack(padx=5, pady=15)


add_consumable_button.configure(command=show_new_consumable)


def validate_consumable_fields():
    if not new_consumable_name.get().strip():
        new_consumable_validation_label.config(text="Name is required")
        return False
    if not new_consumable_quantity.get().strip() or not new_consumable_quantity.get().strip().isdigit():
        new_consumable_validation_label.config(text="Quantity is required and must be a number")
        return False
    if not new_consumable_location.get().strip():
        new_consumable_validation_label.config(text="Location is required")
        return False
    new_consumable_validation_label.config(text="")
    return True


def create_new_consumable():
    if validate_consumable_fields():
        location = Persistance.session.query(ClassroomLocation.ClassroomLocation).filter_by(
            classroom_location_name=new_consumable_location.get()).first()
        if not location:
            new_consumable_validation_label.config(text="Invalid location")
            return
        consumable = Consumable.Consumable(
            new_consumable_name.get(),
            int(new_consumable_quantity.get()),
            location
        )
        consumable.add_consumable()
        reload_consumables()
        new_consumable_frame.pack_forget()
        add_consumable_button.pack(pady=20)
        upload_consumables_button.pack(pady=20)
        template_consumables_button.pack(pady=20)


def cancel_new_consumable():
    new_consumable_frame.pack_forget()
    add_consumable_button.pack(pady=20)
    upload_consumables_button.pack(pady=20)
    template_consumables_button.pack(pady=20)


new_consumable_submit = tb.Button(new_consumable_frame, text="Create", bootstyle="success",
                                  command=create_new_consumable)
new_consumable_submit.grid(row=4, column=0, columnspan=1, pady=20)

new_consumable_cancel = tb.Button(new_consumable_frame, text="Cancel", bootstyle="danger",
                                  command=cancel_new_consumable)
new_consumable_cancel.grid(row=4, column=1, columnspan=1, pady=20)

# Edit consumable variables
edit_consumable_name = tb.StringVar(value="")
edit_consumable_quantity = tb.StringVar(value="")
edit_consumable_location = tb.StringVar(value="")

# Edit consumable form frame
edit_consumable_frame = tb.Frame(consumable_tab)
edit_consumable_validation_label = tb.Label(edit_consumable_frame, text="", bootstyle="danger")
edit_consumable_validation_label.grid(row=3, column=0, columnspan=2, pady=5)

edit_consumable_name_label = tb.Label(edit_consumable_frame, text="Name", width=15)
edit_consumable_name_label.grid(row=0, column=0, padx=10, pady=10)
edit_consumable_name_entry = tb.Entry(edit_consumable_frame, textvariable=edit_consumable_name, width=50)
edit_consumable_name_entry.grid(row=0, column=1, padx=10, pady=10)

edit_consumable_quantity_label = tb.Label(edit_consumable_frame, text="Quantity", width=15)
edit_consumable_quantity_label.grid(row=1, column=0, padx=10, pady=10)
edit_consumable_quantity_entry = tb.Entry(edit_consumable_frame, textvariable=edit_consumable_quantity, width=50)
edit_consumable_quantity_entry.grid(row=1, column=1, padx=10, pady=10)

edit_consumable_location_label = tb.Label(edit_consumable_frame, text="Location", width=15)
edit_consumable_location_label.grid(row=2, column=0, padx=10, pady=10)
edit_consumable_location_entry = tb.Entry(edit_consumable_frame, textvariable=edit_consumable_location, width=50)
edit_consumable_location_entry.grid(row=2, column=1, padx=10, pady=10)


def validate_edit_consumable_fields():
    if not edit_consumable_name.get().strip():
        edit_consumable_validation_label.config(text="Name is required")
        return False
    if not edit_consumable_quantity.get().strip() or not edit_consumable_quantity.get().strip().isdigit():
        edit_consumable_validation_label.config(text="Quantity is required and must be a number")
        return False
    if not edit_consumable_location.get().strip():
        edit_consumable_validation_label.config(text="Location is required")
        return False
    edit_consumable_validation_label.config(text="")
    return True


def submit_edit_consumable():
    if validate_edit_consumable_fields():
        selected = consumables_tree.selection()[0]
        consumable = Persistance.session.query(Consumable.Consumable).filter_by(
            consumable_name=consumables_tree.item(selected)['values'][0]).first()
        location = Persistance.session.query(ClassroomLocation.ClassroomLocation).filter_by(
            classroom_location_name=edit_consumable_location.get()).first()
        if not location:
            edit_consumable_validation_label.config(text="Invalid location")
            return
        consumable.consumable_name = edit_consumable_name.get()
        consumable.consumable_quantity_available = int(edit_consumable_quantity.get())
        consumable.consumable_location = location
        consumable.update_consumable()
        reload_consumables()
        edit_consumable_frame.pack_forget()
        add_consumable_button.pack(pady=20)
        upload_consumables_button.pack(pady=20)
        template_consumables_button.pack(pady=20)


def delete_consumable():
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this consumable?"):
        selected = consumables_tree.selection()[0]
        consumable = Persistance.session.query(Consumable.Consumable).filter_by(
            consumable_name=consumables_tree.item(selected)['values'][0]).first()
        Persistance.session.delete(consumable)
        Persistance.session.commit()
        reload_consumables()
        edit_consumable_frame.pack_forget()
        add_consumable_button.pack(pady=20)
        upload_consumables_button.pack(pady=20)
        template_consumables_button.pack(pady=20)


def cancel_edit_consumable():
    edit_consumable_frame.pack_forget()
    add_consumable_button.pack(pady=20)
    upload_consumables_button.pack(pady=20)
    template_consumables_button.pack(pady=20)


def show_edit_consumable(event):
    selected = consumables_tree.selection()[0]
    consumable = Persistance.session.query(Consumable.Consumable).filter_by(
        consumable_name=consumables_tree.item(selected)['values'][0]).first()
    edit_consumable_name.set(consumable.consumable_name)
    edit_consumable_quantity.set(str(consumable.consumable_quantity_available))
    edit_consumable_location.set(
        consumable.consumable_location.classroom_location_name if consumable.consumable_location else "")
    add_consumable_button.pack_forget()
    upload_consumables_button.pack_forget()
    template_consumables_button.pack_forget()
    edit_consumable_frame.pack(padx=5, pady=15)


edit_consumable_submit = tb.Button(edit_consumable_frame, text="Update", bootstyle="success",
                                   command=submit_edit_consumable)
edit_consumable_submit.grid(row=4, column=0, columnspan=1, pady=20)

edit_consumable_delete = tb.Button(edit_consumable_frame, text="Delete", bootstyle="danger",
                                   command=delete_consumable)
edit_consumable_delete.grid(row=4, column=1, columnspan=1, pady=20)

edit_consumable_cancel = tb.Button(edit_consumable_frame, text="Cancel", bootstyle="warning",
                                   command=cancel_edit_consumable)
edit_consumable_cancel.grid(row=4, column=2, columnspan=1, pady=20)

consumables_tree.bind("<Double-1>", show_edit_consumable)


# **********************************************************************************
#                       CLASSROOM LOCATIONS TAB
# **********************************************************************************


# Add our frames to the notebook
main_notebook.add(unit_tab, text="Units")
main_notebook.add(objective_tab, text="Objectives")
main_notebook.add(consumable_tab, text="Consumables")
main_notebook.add(classroom_location_tab, text="Classroom Locations")

# Classroom Locations Tab
locations_label = Label(classroom_location_tab, text="Classroom Locations", font=("Helvetica", 18))
locations_label.pack(pady=20)

# Create Locations Treeview
locations_tree = tb.Treeview(classroom_location_tab, bootstyle="primary")
locations_tree['columns'] = ('Name',)

# Format columns
locations_tree.column("#0", width=0, stretch=NO)
locations_tree.column("Name", anchor=W, width=200)

# Create headings
locations_tree.heading("#0", text="", anchor=W)
locations_tree.heading("Name", text="Name", anchor=W)


def reload_locations():
    locations_tree.delete(*locations_tree.get_children())
    locations = Persistance.session.query(ClassroomLocation.ClassroomLocation).all()
    for location in locations:
        locations_tree.insert(parent='', index='end', values=(location.classroom_location_name,))


locations_tree.pack(pady=10, padx=10)
reload_locations()


def generate_locations_csv_template():
    file_path = filedialog.asksaveasfilename(
        defaultextension='.csv',
        filetypes=[("CSV Files", "*.csv")]
    )
    if file_path:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['location_name'])


def upload_locations_csv():
    file_path = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")]
    )
    if not file_path:
        return

    try:
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            first_row = next(csv_reader)

            if first_row == ['location_name']:
                pass
            else:
                try:
                    ClassroomLocation.ClassroomLocation(first_row[0]).add_classroom_location()
                except (ValueError, IndexError) as e:
                    messagebox.showerror("Error", f"Invalid data in CSV: {str(e)}")
                    return

            for row in csv_reader:
                try:
                    ClassroomLocation.ClassroomLocation(row[0]).add_classroom_location()
                except (ValueError, IndexError) as e:
                    messagebox.showerror("Error", f"Invalid data in CSV: {str(e)}")
                    reload_locations()
                    return

            reload_locations()
            messagebox.showinfo("Success", "Locations imported successfully")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to read CSV file: {str(e)}")
        reload_locations()


# Add Location button and frame
new_location_name = tb.StringVar(value="")

new_location_frame = tb.Frame(classroom_location_tab)
new_location_validation_label = tb.Label(new_location_frame, text="", bootstyle="danger")
new_location_validation_label.grid(row=1, column=0, columnspan=2, pady=5)

new_location_name_label = tb.Label(new_location_frame, text="Location Name", width=15)
new_location_name_label.grid(row=0, column=0, padx=10, pady=10)
new_location_name_entry = tb.Entry(new_location_frame, textvariable=new_location_name, width=50)
new_location_name_entry.grid(row=0, column=1, padx=10, pady=10)


def validate_location_fields():
    if not new_location_name.get().strip():
        new_location_validation_label.config(text="Location name is required")
        return False
    new_location_validation_label.config(text="")
    return True


def show_new_location():
    add_location_button.pack_forget()
    upload_locations_button.pack_forget()
    template_locations_button.pack_forget()
    new_location_frame.pack(padx=5, pady=15)


def create_new_location():
    if validate_location_fields():
        location = ClassroomLocation.ClassroomLocation(new_location_name.get())
        location.add_classroom_location()
        reload_locations()
        new_location_frame.pack_forget()
        add_location_button.pack(pady=20)
        upload_locations_button.pack(pady=20)
        template_locations_button.pack(pady=20)


def cancel_new_location():
    new_location_frame.pack_forget()
    add_location_button.pack(pady=20)
    upload_locations_button.pack(pady=20)
    template_locations_button.pack(pady=20)


new_location_submit = tb.Button(new_location_frame, text="Create", bootstyle="success", command=create_new_location)
new_location_submit.grid(row=2, column=0, columnspan=1, pady=20)

new_location_cancel = tb.Button(new_location_frame, text="Cancel", bootstyle="danger", command=cancel_new_location)
new_location_cancel.grid(row=2, column=1, columnspan=1, pady=20)

# Edit Location frame
edit_location_name = tb.StringVar(value="")

edit_location_frame = tb.Frame(classroom_location_tab)
edit_location_validation_label = tb.Label(edit_location_frame, text="", bootstyle="danger")
edit_location_validation_label.grid(row=1, column=0, columnspan=2, pady=5)

edit_location_name_label = tb.Label(edit_location_frame, text="Location Name", width=15)
edit_location_name_label.grid(row=0, column=0, padx=10, pady=10)
edit_location_name_entry = tb.Entry(edit_location_frame, textvariable=edit_location_name, width=50)
edit_location_name_entry.grid(row=0, column=1, padx=10, pady=10)


def validate_edit_location_fields():
    if not edit_location_name.get().strip():
        edit_location_validation_label.config(text="Location name is required")
        return False
    edit_location_validation_label.config(text="")
    return True


def show_edit_location(event):
    selected = locations_tree.selection()[0]
    location = Persistance.session.query(ClassroomLocation.ClassroomLocation).filter_by(
        classroom_location_name=locations_tree.item(selected)['values'][0]).first()
    edit_location_name.set(location.classroom_location_name)
    add_location_button.pack_forget()
    upload_locations_button.pack_forget()
    template_locations_button.pack_forget()
    edit_location_frame.pack(padx=5, pady=15)


def submit_edit_location():
    if validate_edit_location_fields():
        selected = locations_tree.selection()[0]
        location = Persistance.session.query(ClassroomLocation.ClassroomLocation).filter_by(
            classroom_location_name=locations_tree.item(selected)['values'][0]).first()
        location.classroom_location_name = edit_location_name.get()
        location.update_classroom_location()
        reload_locations()
        edit_location_frame.pack_forget()
        add_location_button.pack(pady=20)
        upload_locations_button.pack(pady=20)
        template_locations_button.pack(pady=20)


def delete_location():
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this location?"):
        selected = locations_tree.selection()[0]
        location = Persistance.session.query(ClassroomLocation.ClassroomLocation).filter_by(
            classroom_location_name=locations_tree.item(selected)['values'][0]).first()
        Persistance.session.delete(location)
        Persistance.session.commit()
        reload_locations()
        edit_location_frame.pack_forget()
        add_location_button.pack(pady=20)
        upload_locations_button.pack(pady=20)
        template_locations_button.pack(pady=20)


def cancel_edit_location():
    edit_location_frame.pack_forget()
    add_location_button.pack(pady=20)
    upload_locations_button.pack(pady=20)
    template_locations_button.pack(pady=20)


edit_location_submit = tb.Button(edit_location_frame, text="Update", bootstyle="success", command=submit_edit_location)
edit_location_submit.grid(row=2, column=0, columnspan=1, pady=20)

edit_location_delete = tb.Button(edit_location_frame, text="Delete", bootstyle="danger", command=delete_location)
edit_location_delete.grid(row=2, column=1, columnspan=1, pady=20)

edit_location_cancel = tb.Button(edit_location_frame, text="Cancel", bootstyle="warning", command=cancel_edit_location)
edit_location_cancel.grid(row=2, column=2, columnspan=1, pady=20)

locations_tree.bind("<Double-1>", show_edit_location)

add_location_button = tb.Button(classroom_location_tab, text="Add Location", bootstyle="danger",
                                command=show_new_location)
add_location_button.pack(pady=20)

upload_locations_button = tb.Button(classroom_location_tab, text="Upload CSV", bootstyle="default outline",
                                    command=upload_locations_csv)
upload_locations_button.pack(pady=20)

template_locations_button = tb.Button(classroom_location_tab, text="Download Template", bootstyle="info outline",
                                      command=generate_locations_csv_template)
template_locations_button.pack(pady=20)

root.mainloop()

self.units = Persistance.session.query(Unit.Unit).order_by(Unit.Unit.unit_sequence).all()
for unit in self.units:
    self.units_tree.insert(parent='', index='end', values=(
        unit.unit_sequence,
        unit.unit_name,
        unit.unit_opening_date.strftime('%Y-%m-%d'),
        unit.unit_end_date.strftime('%Y-%m-%d'),
        unit.unit_closing_date.strftime('%Y-%m-%d')
    )
                           )