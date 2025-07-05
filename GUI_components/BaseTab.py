# GUI_components/BaseTab.py
import ttkbootstrap as tb
from tkinter import messagebox, filedialog
import csv

class BaseTab(tb.Frame):
    def __init__(self, notebook):
        super().__init__(notebook)
        self.notebook = notebook

    #probably depricated
    def toggle_form_visibility(self, form_to_show, buttons_to_hide):
        #"""Common method to toggle form visibility#"""
        form_to_show.grid(padx=5, pady=15)
        for button in buttons_to_hide:
            button.grid_forget()


    def swap_form_visibility(self, form_to_hide, form_to_show):
        form_to_hide.grid_forget()
        form_to_show.grid(padx=5, pady=15)

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