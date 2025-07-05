# tabs/BaseTab.py
import ttkbootstrap as tb
from tkinter import messagebox


class BaseTab(tb.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

    def show_error(self, message):
        messagebox.showerror("Error", message)

    def show_success(self, message):
        messagebox.showinfo("Success", message)

    def confirm_delete(self, message="Are you sure you want to delete this item?"):
        return messagebox.askyesno("Confirm Delete", message)
