# python
# --- Test time support (module-level) ---
from datetime import datetime, timedelta
from typing import Optional

# Toggle and storage
_TEST_TIME_ENABLED: bool = False
# When advancing with real time:
_TEST_SIM_EPOCH: Optional[datetime] = None   # simulated start datetime
_TEST_REAL_EPOCH: Optional[datetime] = None  # real clock when test started
# When frozen:
_TEST_FIXED: Optional[datetime] = None       # fixed datetime to return when enabled

def set_test_time(dt: datetime, enable: bool = True, advance_with_real_time: bool = True) -> None:
    """
    Configure a test time to use instead of the real clock.

    dt: baseline simulated datetime.
    enable: immediately enable the override.
    advance_with_real_time: if True, the simulated clock advances in sync with real time
                            starting from 'dt'. If False, the time is frozen at 'dt'.
    """
    global _TEST_TIME_ENABLED, _TEST_SIM_EPOCH, _TEST_REAL_EPOCH, _TEST_FIXED

    # Normalize to naive local datetime to match typical usage in this module
    if isinstance(dt, datetime) and dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)

    _TEST_TIME_ENABLED = bool(enable)

    if advance_with_real_time:
        _TEST_SIM_EPOCH = dt
        _TEST_REAL_EPOCH = datetime.now()
        _TEST_FIXED = None
    else:
        _TEST_FIXED = dt
        _TEST_SIM_EPOCH = None
        _TEST_REAL_EPOCH = None

def use_test_time(enabled: bool) -> None:
    """
    Toggle whether the configured test time should be used.
    """
    global _TEST_TIME_ENABLED
    _TEST_TIME_ENABLED = bool(enabled)

def clear_test_time() -> None:
    """
    Disable test time and clear any configured baseline.
    """
    global _TEST_TIME_ENABLED, _TEST_SIM_EPOCH, _TEST_REAL_EPOCH, _TEST_FIXED
    _TEST_TIME_ENABLED = False
    _TEST_SIM_EPOCH = None
    _TEST_REAL_EPOCH = None
    _TEST_FIXED = None

def advance_test_time(delta: timedelta) -> None:
    """
    Manually advance the simulated time by 'delta' when using a frozen time.
    If advancing mode is active, this nudges the baseline forward by 'delta'.
    """
    global _TEST_SIM_EPOCH, _TEST_FIXED
    if _TEST_FIXED is not None:
        _TEST_FIXED += delta
    elif _TEST_SIM_EPOCH is not None:
        _TEST_SIM_EPOCH += delta

def get_now() -> datetime:
    """
    Return the effective 'now' for this module:
    - If test time is enabled and a fixed time is set, return the fixed time.
    - If test time is enabled and an advancing baseline is set, return baseline + elapsed real time.
    - Otherwise, return the real current time.
    """
    if _TEST_TIME_ENABLED:
        if _TEST_FIXED is not None:
            return _TEST_FIXED
        if _TEST_SIM_EPOCH is not None and _TEST_REAL_EPOCH is not None:
            return _TEST_SIM_EPOCH + (datetime.now() - _TEST_REAL_EPOCH)
    return datetime.now()

# Replace uses of datetime.now() in this module with get_now() so the override is respected.
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *

# Import your model's Hour class
# Assumes Hour.get_by_time(requested_time: time) -> Hour | None
from Model.Hour import Hour


class KeypadApp(tb.Window):
    def __init__(self, themename="flatly"):
        super().__init__(themename=themename)
        self.title("Daily Clock-in: Foundations of Manifacturing @ Glenpool")
        self.geometry("900x520")

        # Paned layout: left info pane, right keypad pane
        paned = ttk.Panedwindow(self, orient="horizontal")
        paned.pack(fill="both", expand=True)

        self.left_pane = tb.Labelframe(paned, text="Information", padding=10)
        self.right_pane = tb.Labelframe(paned, text="Input", padding=10)
        paned.add(self.left_pane, weight=3)
        paned.add(self.right_pane, weight=2)

        # set up testing:
        set_test_time(datetime(2025, 9, 8, 12, 0, 0), enable=True, advance_with_real_time=True)

        self._build_left_info_pane()
        self._build_right_keypad_pane()

        # Show current hour and keep it updated
        self.refresh_current_hour()


    def _build_left_info_pane(self):
        # Grid config
        self.left_pane.rowconfigure(1, weight=1)  # text area grows
        self.left_pane.columnconfigure(0, weight=1)

        # Hour name at the top
        self.hour_label = tb.Label(
            self.left_pane,
            text="",
            font=("Segoe UI", 18, "bold"),
            bootstyle=PRIMARY,
            anchor="w",
        )
        self.hour_label.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Scrollable text area (kept empty as requested)
        self.info_text = tk.Text(self.left_pane, wrap="word", height=10)
        self.info_text.grid(row=1, column=0, sticky="nsew", padx=(0, 6))

        scroll = tb.Scrollbar(self.left_pane, orient="vertical", command=self.info_text.yview)
        scroll.grid(row=1, column=1, sticky="ns")
        self.info_text.configure(yscrollcommand=scroll.set)

        # Ensure no default text remains
        self.info_text.delete("1.0", "end")

    def refresh_current_hour(self):
        """
        Looks up the current Hour based on the system time and displays its name.
        Clears any text content in the left pane text area.
        """
        try:
            now_time = get_now().time()
            hour = Hour.get_by_time(now_time)
        except Exception:
            hour = None

        # Resolve a display name robustly
        display_name = "No current hour"
        if hour is not None:
            # Try common patterns: hour.name or hour.unit.name
            name = getattr(hour, "name", None)
            if not name:
                unit = getattr(hour, "unit", None)
                name = getattr(unit, "name", None) if unit is not None else None
            if not name:
                # Fallbacks for underscore attributes or repr
                name = getattr(hour, "_name", None)
            display_name = str(name) if name else "Unnamed Hour"


        self.hour_label.configure(text=f' clock in for: {display_name} hour')

        # Clear any text content in the pane
        try:
            self.info_text.delete("1.0", "end")
        except Exception:
            pass

        # Refresh every 30 seconds
        self.after(30_000, self.refresh_current_hour)

    def _build_right_keypad_pane(self):
        self.right_pane.columnconfigure(0, weight=1)

        # Always-visible entry at the top
        self.entry_var = tk.StringVar()
        self.entry = tb.Entry(self.right_pane, textvariable=self.entry_var, font=("Segoe UI", 18))
        self.entry.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.entry.focus_set()

        # Keypad
        pad = tb.Frame(self.right_pane)
        pad.grid(row=1, column=0, sticky="nsew")
        for c in range(3):
            pad.columnconfigure(c, weight=1)

        buttons = [
            ["7", "8", "9"],
            ["4", "5", "6"],
            ["1", "2", "3"],
            [".", "0", "⌫"],
        ]

        def insert_text(ch: str):
            self.entry.focus_set()
            if ch == "⌫":
                idx = self.entry.index(tk.INSERT)
                if idx > 0:
                    self.entry.delete(idx - 1)
                return
            self.entry.insert(tk.INSERT, ch)

        for r, row_vals in enumerate(buttons):
            for c, label in enumerate(row_vals):
                tb.Button(
                    pad,
                    text=label,
                    bootstyle=SECONDARY,
                    command=lambda ch=label: insert_text(ch),
                    width=6
                ).grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

        # Control buttons
        controls = tb.Frame(self.right_pane)
        controls.grid(row=2, column=0, sticky="ew", pady=(8, 0))
        controls.columnconfigure(0, weight=1)
        controls.columnconfigure(1, weight=1)

        tb.Button(
            controls, text="Clear", bootstyle=WARNING, command=lambda: self.entry_var.set("")
        ).grid(row=0, column=0, padx=4, sticky="ew")

        tb.Button(
            controls, text="Enter", bootstyle=SUCCESS, command=self._commit_value
        ).grid(row=0, column=1, padx=4, sticky="ew")

        # Keyboard binding for Enter key
        self.bind("<Return>", lambda e: self._commit_value())

    def _commit_value(self):
        value = self.entry_var.get()
        # You can add any action here; we don't write to the left pane text as requested.
        self.entry_var.set("")


if __name__ == "__main__":
    app = KeypadApp(themename="flatly")

    app.mainloop()