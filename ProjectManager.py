from tkinter import *
import ttkbootstrap as tb
import Objective
import Persistance
import Unit
import Group

#THIS SHOULD PRETTY MUCH ALWAYS BE COMMENTED OUT!!!
Persistance.Base.metadata.create_all(Persistance.engine)
print("Database created")

def show_new_unit():
    add_unit_button.pack_forget()
    new_unit_frame.pack(padx=5, pady=15)



root = tb.Window(themename="superhero")
root.title("Foundations of Manufacturing 2025-2026")
#root.iconbitmap('images/codemy.ico')
root.geometry('1280x1024')

main_notebook = tb.Notebook(root, bootstyle="dark")
main_notebook.pack(pady=20)

unit_tab = tb.Frame(main_notebook)
tab2 = tb.Frame(main_notebook)

units_label = Label(unit_tab, text="Units", font=("Helvetica", 18))
units_label.pack(pady=20)

my_text = Text(unit_tab, width=70, height=10)
my_text.pack(pady=10, padx=10)

add_unit_button = tb.Button(unit_tab, text="Add Unit", bootstyle="danger outline", command=show_new_unit)
add_unit_button.pack(pady=20)

# variables for crating a new unit
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


new_unit_submit = tb.Button(new_unit_frame, text="Create", bootstyle="success", command=lambda: Unit.Unit(
    new_unit_name.get(),
    new_unit_sequence.get(),
    new_unit_opening_date_entry.entry.get(),
    new_unit_closing_date_entry.entry.get(),
    new_unit_end_date_entry.entry.get(),
    new_unit_description_text.get("1.0", END)
).add_unit() if validate_unit_fields() else None)

new_unit_submit.grid(row=4, column=0, columnspan=5, pady=20)

my_label2 = Label(tab2, text="Objectives", font=("Helvetica", 18))
my_label2.pack(pady=20)

# Add our frames to the notebook
main_notebook.add(unit_tab, text="Units")
main_notebook.add(tab2, text="Objectives")

root.mainloop()

