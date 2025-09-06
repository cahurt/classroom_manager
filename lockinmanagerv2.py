import sys
import tkinter as tk
from tkinter import ttk

# Try to enable ttkbootstrap theming if available (optional)
try:
    import ttkbootstrap as tb
    HAS_TTKBOOTSTRAP = True
except Exception:
    tb = None
    HAS_TTKBOOTSTRAP = False


class CheckinApp:
    def __init__(self, master: tk.Misc):
        self.master = master
        self.master.title("Two-Pane App (Entry + Keypad | Hour Display + Form)")

        # Top-level paned window: left (entry + keypad), right (display + form)
        self.outer_paned = ttk.Panedwindow(self.master, orient=tk.HORIZONTAL)
        self.outer_paned.pack(fill=tk.BOTH, expand=True)

        # Left pane
        self.left_frame = ttk.Frame(self.outer_paned, padding=10)
        self._build_left_pane(self.left_frame)
        self.outer_paned.add(self.left_frame, weight=1)

        # Right pane (itself split into two vertical panes)
        self.right_frame = ttk.Frame(self.outer_paned, padding=10)
        self._build_right_pane(self.right_frame)
        self.outer_paned.add(self.right_frame, weight=3)

        # Give a nicer initial split after layout
        self.master.after(100, self._set_initial_sashes)

    def _set_initial_sashes(self):
        # Set initial horizontal split (left ~ 280px)
        try:
            self.outer_paned.sashpos(0, 280)
        except Exception:
            pass
        # Set initial vertical split inside right pane (top around 80px)
        try:
            self.right_paned.sashpos(0, 80)
        except Exception:
            pass

    def _build_left_pane(self, parent: ttk.Frame):
        parent.columnconfigure((0, 1, 2), weight=1)

        # Always-visible text entry at the top
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(parent, textvariable=self.entry_var, font=("", 16))
        self.entry.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 10))
        self.entry.focus_set()

        # On-screen number pad (no decimal button)
        keypad_layout = [
            ("7", "8", "9"),
            ("4", "5", "6"),
            ("1", "2", "3"),
            ("C", "0", "⌫"),
        ]

        def on_keypad(char: str):
            if char == "C":
                self.entry_var.set("")
            elif char == "⌫":
                self.entry_var.set(self.entry_var.get()[:-1])
            else:
                # Only digits, no decimal point
                if char.isdigit():
                    self.entry_var.set(self.entry_var.get() + char)
            self.entry.icursor(tk.END)
            self.entry.focus_set()

        row_idx = 1
        for row in keypad_layout:
            col_idx = 0
            for char in row:
                btn = ttk.Button(parent, text=char, command=lambda c=char: on_keypad(c))
                btn.grid(row=row_idx, column=col_idx, sticky="nsew", padx=4, pady=4)
                col_idx += 1
            row_idx += 1

        # Make keypad cells expand nicely
        for r in range(1, row_idx):
            parent.rowconfigure(r, weight=1)

        # Enter button (optional convenience)
        enter_btn = ttk.Button(parent, text="Enter", command=self._on_enter)
        enter_btn.grid(row=row_idx, column=0, columnspan=3, sticky="nsew", padx=4, pady=(8, 0))
        parent.rowconfigure(row_idx, weight=0)

        # Bind Return/Enter key from keyboard
        self.master.bind("<Return>", lambda _e: self._on_enter())

    def _build_right_pane(self, parent: ttk.Frame):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        self.right_paned = ttk.Panedwindow(parent, orient=tk.VERTICAL)
        self.right_paned.grid(row=0, column=0, sticky="nsew")

        # Top: hour_display label
        top_frame = ttk.Frame(self.right_paned, padding=(0, 10, 0, 10))
        self.hour_display = tk.StringVar(value="hour_display")
        hour_label = ttk.Label(top_frame, textvariable=self.hour_display, anchor="center", font=("", 20, "bold"))
        hour_label.pack(fill=tk.X, expand=False)
        self.right_paned.add(top_frame, weight=1)

        # Bottom: form area (buttons, labels, fields)
        form_frame = ttk.Frame(self.right_paned, padding=5)
        self._build_form(form_frame)
        self.right_paned.add(form_frame, weight=3)

    def _build_form(self, parent: ttk.Frame):
        # Example fields — replace/extend as needed
        parent.columnconfigure(1, weight=1)

        name_lbl = ttk.Label(parent, text="Name:")
        name_ent = ttk.Entry(parent)

        notes_lbl = ttk.Label(parent, text="Notes:")
        notes_ent = ttk.Entry(parent)

        submit_btn = ttk.Button(parent, text="Submit", command=self._on_submit)
        cancel_btn = ttk.Button(parent, text="Cancel", command=self._on_cancel)

        # Layout
        name_lbl.grid(row=0, column=0, sticky="e", padx=(0, 8), pady=4)
        name_ent.grid(row=0, column=1, sticky="ew", padx=(0, 0), pady=4)

        notes_lbl.grid(row=1, column=0, sticky="e", padx=(0, 8), pady=4)
        notes_ent.grid(row=1, column=1, sticky="ew", padx=(0, 0), pady=4)

        btns = ttk.Frame(parent)
        btns.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8, 0))
        btns.columnconfigure((0, 1), weight=0)

        submit_btn.grid(in_=btns, row=0, column=0, padx=(0, 6))
        cancel_btn.grid(in_=btns, row=0, column=1)

    def _on_enter(self):
        # For demo: reflect the entry to hour_display
        value = self.entry_var.get()
        self.hour_display.set(value if value else "hour_display")

    def _on_submit(self):
        # Placeholder for form submission
        print("Submit clicked", file=sys.stdout)

    def _on_cancel(self):
        # Placeholder for cancel action
        print("Cancel clicked", file=sys.stdout)


def main():
    if HAS_TTKBOOTSTRAP:
        # Use ttkbootstrap Window so ttk widgets get themed
        root = tb.Window(themename="flatly")
    else:
        root = tk.Tk()
    app = CheckinApp(root)
    root.geometry("900x520")
    root.minsize(640, 400)
    root.mainloop()


if __name__ == "__main__":
    main()