class CommonUtils:
    @staticmethod
    def generate_csv_template(headers):
        file_path = filedialog.asksaveasfilename(
            defaultextension='.csv',
            filetypes=[("CSV Files", "*.csv")]
        )
        if file_path:
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(headers)

    @staticmethod
    def toggle_form_visibility(show_frame, hide_buttons):
        for button in hide_buttons:
            button.pack_forget()
        show_frame.pack(padx=5, pady=15)

    @staticmethod
    def validate_form_fields(label_to_validate, fields):
        for field_name, field_value, field_type in fields:
            if not field_value.strip():
                label_to_validate.config(text=f"{field_name} is required")
                return False
            if field_type == "number" and not field_value.strip().isdigit():
                label_to_validate.config(text=f"{field_name} must be a number")
                return False
            label_to_validate.config(text="")
            return True

