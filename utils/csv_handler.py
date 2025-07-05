import csv
from tkinter import filedialog

def generate_csv_template(headers, default_filename):
    file_path = filedialog.asksaveasfilename(
        defaultextension='.csv',
        filetypes=[("CSV Files", "*.csv")],
        initialfile=default_filename
    )
    if file_path:
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
