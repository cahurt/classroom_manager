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

from typing import Optional
from sqlalchemy import select
from Persistance import session
from Model.Student import Student


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

        self.clock_in_form = None  # New: container replacing info_text
        # Keep a backward-compatible alias if other parts still reference info_text
        self.info_text = None


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

        # Scrollable text area 
        self.info_text = tk.Text(self.left_pane, wrap="word", height=10)
        self.info_text.grid(row=1, column=0, sticky="nsew", padx=(0, 6))

        scroll = tb.Scrollbar(self.left_pane, orient="vertical", command=self.info_text.yview)
        scroll.grid(row=1, column=1, sticky="ns")
        self.info_text.configure(yscrollcommand=scroll.set)

        # Ensure no default text remains
        self.info_text.delete("1.0", "end")
        self._set_info_display_text("boom")
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

        tb.Button(controls, text="Enter", bootstyle=SUCCESS, command=self.handle_right_pane_enter).grid(row=0, column=1, padx=4, sticky="ew")

        # Keyboard binding for Enter key
        self.bind("<Return>", lambda e: self._commit_value())

    def _commit_value(self):
        value = self.entry_var.get()
        # You can add any action here; we don't write to the left pane text as requested.
        self.handle_right_pane_enter()


    def handle_right_pane_enter(self) -> None:
        """
        Handler for the 'Enter' action in the right pane.
        - Clears the information display field.
        - Evaluates the text in the number entry field.
        - Searches for a matching Student by priority: StudentID -> glenpool_id -> rfid.
        - If not found, shows 'no student found' for 10 seconds, then clears again.
        """
        print('Enter Pressed')
        # 1) Clear the information display field first (not the hour display pane)
        self._clear_info_display()

        # 2) Get number entry text from the right pane
        raw = self._get_number_entry_text().strip()

        # 3) Try to resolve a student
        student = self._find_student_by_input(raw)

        if student is None:
            self._show_temporary_info_message("no student found", 10_000)
            return

        # 4) Display whatever student info you need in the info display field
        # Adjust these fields to match your model's attributes
        first = getattr(student, "first_name", "")
        last = getattr(student, "last_name", "")
        sid = getattr(student, "studentID", "")
        self._set_info_display_text(f"{first} {last} (ID: {sid})")

    # ------- helpers: UI -------
    def _get_number_entry_text(self) -> str:
        """
        Return the text from the number entry field in the right pane.
        Tries a few common attribute names used for the widget.
        """
        candidate_attrs = (
            "number_entry",
            "number_entry_field",
            "right_number_entry",
            "student_number_entry",
        )
        for name in candidate_attrs:
            widget = getattr(self, name, None)
            if widget is not None and hasattr(widget, "get"):
                try:
                    return widget.get()
                except Exception:
                    pass
        return ""

    def _clear_info_display(self) -> None:
        """
        Clear the information display field (not the hour display pane).
        Tries to work with both Text-like and Label-like widgets.
        """
        self._set_info_display_text("")

    def _set_info_display_text(self, text: str) -> None:
        """
        Set the information display field's text. Works with common widget types.
        """
        candidate_attrs = (
            "info_display",
            "information_display_field",
            "right_info_display",
            "info_label",
        )
        for name in candidate_attrs:
            widget = getattr(self, name, None)
            if widget is None:
                continue

            # Text-like widget
            if hasattr(widget, "delete") and hasattr(widget, "insert"):
                try:
                    if hasattr(widget, "config"):
                        widget.config(state="normal")
                    widget.delete("1.0", "end")
                    if text:
                        widget.insert("end", text)
                    if hasattr(widget, "config"):
                        widget.config(state="disabled")
                    return
                except Exception:
                    pass

            # Label-like widget
            if hasattr(widget, "configure"):
                try:
                    widget.configure(text=text)
                    return
                except Exception:
                    pass

            # Variable-backed widget (StringVar)
            if hasattr(widget, "set"):
                try:
                    widget.set(text)
                    return
                except Exception:
                    pass

    def _show_temporary_info_message(self, text: str, duration_ms: int) -> None:
        """
        Show a temporary message in the information display field, then clear it.
        """
        print('showing message')
        self._set_info_display_text(text)
        if hasattr(self, "after"):
            # Schedule clear on the UI loop (Tkinter-style)
            self.after(duration_ms, self._clear_info_display)
        else:
            # Fallback: clear in a background thread after a delay
            import threading, time
            def _delayed_clear():
                time.sleep(duration_ms / 1000.0)
                try:
                    self._clear_info_display()
                except Exception:
                    pass
            threading.Thread(target=_delayed_clear, daemon=True).start()

    # ------- helpers: data lookup -------
    def _find_student_by_input(self, raw: str) -> Optional[Student]:
        """
        Resolve input to a Student using priority:
        1) StudentID (primary key)
        2) glenpool_id
        3) rfid
        Returns the Student or None.
        """
        if not raw:
            return None

        # Try integer conversions where appropriate
        try:
            numeric = int(raw)
        except ValueError:
            numeric = None

        # 1) StudentID (primary key lookup)
        if numeric is not None:
            try:
                s = session.get(Student, numeric)
                if s is not None:
                    return s
            except Exception:
                pass

        # Fetch all students once for subsequent comparisons
        try:
            students = session.execute(select(Student)).scalars().all()
        except Exception:
            students = list(session.query(Student))  # type: ignore[attr-defined]

        # 2) glenpool_id (via public property)
        if numeric is not None:
            for s in students:
                try:
                    if getattr(s, "glenpool_id", None) == numeric:
                        return s
                except Exception:
                    pass

        # 3) rfid (string comparison; supports numeric or string RFIDs)
        for s in students:
            try:
                rfid_val = getattr(s, "rfid", None)
                if rfid_val is None:
                    # Try a couple of common alternate attribute names if needed
                    rfid_val = getattr(s, "student_rfid", None)
                if rfid_val is None:
                    continue
                if str(rfid_val).strip() == raw:
                    return s
            except Exception:
                pass

        return None

    # New: ensure clock_in_form exists and replace the old info_text widget in-place
    def _ensure_clock_in_form(self):
        # If already created, nothing to do
        if getattr(self, "clock_in_form", None) is not None:
            return

        parent = None
        target_manager = None
        grid_opts = {}
        pack_opts = {}

        old = getattr(self, "info_text", None)

        # Helpers to normalize geometry manager values
        def _norm_pad(v):
            # Accept int, tuple/list of ints, or strings like "6" or "0 6"
            if v in (None, "", 0):
                return 0
            if isinstance(v, (list, tuple)):
                vals = []
                for item in v:
                    try:
                        vals.append(int(item))
                    except Exception:
                        try:
                            vals.append(int(float(item)))
                        except Exception:
                            vals.append(0)
                return tuple(vals) if len(vals) != 1 else vals[0]
            if isinstance(v, str):
                parts = v.replace(",", " ").split()
                if not parts:
                    return 0
                if len(parts) == 1:
                    try:
                        return int(parts[0])
                    except Exception:
                        try:
                            return int(float(parts[0]))
                    except Exception:
                        return 0
            vals = []
            for p in parts[:2]:
                try:
                    vals.append(int(p))
                except Exception:
                    try:
                        vals.append(int(float(p)))
                    except Exception:
                        vals.append(0)
                return tuple(vals)
            try:
                return int(v)
            except Exception:
                try:
                    return int(float(v))
                except Exception:
                    return 0

        def _norm_bool(v, default=False):
            if v is None or v == "":
                return default
            if isinstance(v, bool):
                return v
            if isinstance(v, (int, float)):
                return bool(int(v))
            s = str(v).strip().lower()
            if s in ("0", "false", "no", "off"):
                return False
            if s in ("1", "true", "yes", "on"):
                return True
            return default

        if old is not None:
            try:
                parent = old.nametowidget(old.winfo_parent())
            except Exception:
                parent = getattr(self, "left_pane", None) or getattr(self, "right_pane", None)
            try:
                mgr = old.winfo_manager()
            except Exception:
                mgr = ""
            target_manager = mgr

            if mgr == "grid":
                try:
                    gi = old.grid_info()
                except Exception:
                    gi = {}
                grid_opts = {
                    "row": int(gi.get("row", 0)),
                    "column": int(gi.get("column", 0)),
                    "rowspan": int(gi.get("rowspan", 1)),
                    "columnspan": int(gi.get("columnspan", 1)),
                    "sticky": gi.get("sticky", "nsew"),
                    "padx": _norm_pad(gi.get("padx", 0) or 0),
                    "pady": _norm_pad(gi.get("pady", 0) or 0),
                }
                try:
                    old.grid_forget()
                except Exception:
                    try:
                        old.destroy()
                    except Exception:
                        pass
            elif mgr == "pack":
                try:
                    pi = old.pack_info()
                except Exception:
                    pi = {}
                pack_opts = {
                    "side": pi.get("side", "top"),
                    "fill": pi.get("fill", "both"),
                    "expand": _norm_bool(pi.get("expand", True)),
                    "padx": _norm_pad(pi.get("padx", 0) or 0),
                    "pady": _norm_pad(pi.get("pady", 0) or 0),
                }
                try:
                    old.pack_forget()
                except Exception:
                    try:
                        old.destroy()
                    except Exception:
                        pass
            else:
                # Unknown manager; just destroy and fall back to left_pane
                try:
                    old.destroy()
                except Exception:
                    pass
                parent = getattr(self, "left_pane", None)
        else:
            # No previous info_text; default to left_pane
            parent = getattr(self, "left_pane", None)

        if parent is None:
            # As a last resort, attach to the main app window/pane if available
            parent = getattr(self, "left_pane", None) or getattr(self, "right_pane", None)

        # Create the new flexible form container
        container_parent = parent if parent is not None else self
        try:
            # Use the ttkbootstrap module directly
            self.clock_in_form = tb.Frame(container_parent)
        except Exception:
            # Fallback to the tkinter module directly
            self.clock_in_form = tk.Frame(container_parent)

        # Place it where the old info_text was
        if target_manager == "grid" and grid_opts:
            self.clock_in_form.grid(**grid_opts)
        elif target_manager == "pack" and pack_opts:
            self.clock_in_form.pack(**pack_opts)
        else:
            # Default placement
            try:
                # Prefer grid if the parent already uses it
                if hasattr(container_parent, "grid_slaves") and container_parent.grid_slaves():
                    self.clock_in_form.grid(row=0, column=0, sticky="nsew")
                    try:
                        container_parent.grid_rowconfigure(0, weight=1)
                        container_parent.grid_columnconfigure(0, weight=1)
                    except Exception:
                        pass
                else:
                    self.clock_in_form.pack(fill="both", expand=True)
            except Exception:
                self.clock_in_form.pack(fill="both", expand=True)

        # Keep alias to avoid attribute errors in existing code paths
        self.info_text = self.clock_in_form

        # Start with an empty form
        self._clear_info_display()


def _set_info_display_text(self, text: str) -> None:
    """
    Render simple text into the clock_in_form as a Label.
    This keeps existing callers working while the UI has moved to a form container.
    """
    self._ensure_clock_in_form()
    self._clear_info_display()
    try:
        # Use ttkbootstrap module directly
        label = tb.Label(self.clock_in_form, text=text, anchor="w", justify="left", wraplength=600)
    except Exception:
        # Fallback to tkinter module directly
        label = tk.Label(self.clock_in_form, text=text, anchor="w", justify="left", wraplength=600)

    # Use grid if the form is on a grid parent; otherwise pack
    try:
        if self.clock_in_form.winfo_manager() == "grid" or (
            hasattr(self.clock_in_form.master, "grid_slaves") and self.clock_in_form.master.grid_slaves()
        ):
            label.grid(row=0, column=0, sticky="nw", padx=8, pady=8)
        else:
            label.pack(anchor="nw", padx=8, pady=8)
    except Exception:
        label.pack(anchor="nw", padx=8, pady=8)

    def _show_temporary_info_message(self, text: str, duration_ms: int) -> None:
        """
        Show a temporary message inside the clock_in_form, then clear it.
        """
        self._set_info_display_text(text)

        # Prefer scheduling on a widget's event loop
        after_target = None
        for candidate_name in ("clock_in_form", "left_pane", "right_pane", "entry"):
            candidate = getattr(self, candidate_name, None)
            if candidate is not None and hasattr(candidate, "after"):
                after_target = candidate
                break

        if after_target is not None:
            after_target.after(duration_ms, self._clear_info_display)
        else:
            # Fallback (not ideal for UI frameworks)
            import threading, time
            def _delayed_clear():
                time.sleep(duration_ms / 1000.0)
                try:
                    self._clear_info_display()
                except Exception:
                    pass
            threading.Thread(target=_delayed_clear, daemon=True).start()

    # Optional helpers to populate the new form with interactive controls

    def show_clock_in_buttons(self, buttons):
        """
        Populate the clock_in_form with a row/column grid of buttons.
        buttons: list of dicts or tuples describing buttons.
          Accepted forms:
            - {"text": "...", "command": callable, "style": "..."}
            - ("...", callable) or ("...", callable, {"style": "..."})
        """
        self._ensure_clock_in_form()
        self._clear_info_display()

        # Normalize to list of (text, command, style)
        normalized = []
        for item in buttons:
            if isinstance(item, dict):
                normalized.append((
                    item.get("text", ""),
                    item.get("command"),
                    item.get("style")
                ))
            elif isinstance(item, (tuple, list)):
                if len(item) == 2:
                    normalized.append((item[0], item[1], None))
                elif len(item) == 3 and isinstance(item[2], dict):
                    normalized.append((item[0], item[1], item[2].get("style")))
                else:
                    # Fallback: best-effort
                    text = item[0] if len(item) > 0 else ""
                    cmd = item[1] if len(item) > 1 else None
                    style = item[2] if len(item) > 2 else None
                    normalized.append((text, cmd, style))
            else:
                continue

        # Layout buttons in a responsive grid
        cols = 3 if len(normalized) >= 3 else max(1, len(normalized))
        for i in range(cols):
            try:
                self.clock_in_form.grid_columnconfigure(i, weight=1)
            except Exception:
                pass

        r, c = 0, 0
        for text, cmd, style in normalized:
            try:
                btn = self.tb.Button(self.clock_in_form, text=text, command=cmd, bootstyle=style or "")
            except Exception:
                btn = self.tk.Button(self.clock_in_form, text=text, command=cmd)
            try:
                btn.grid(row=r, column=c, sticky="ew", padx=8, pady=8)
            except Exception:
                btn.pack(fill="x", padx=8, pady=8)
            c += 1
            if c >= cols:
                c = 0
                r += 1

    def add_clock_in_widget(self, widget_factory):
        """
        Add an arbitrary widget to the clock_in_form.
        widget_factory: callable taking parent -> widget
        Example:
            self.add_clock_in_widget(lambda parent: self.tb.Label(parent, text="Hello"))
        """
        self._ensure_clock_in_form()
        try:
            widget = widget_factory(self.clock_in_form)
        except Exception:
            return None

        # Place below existing content
        try:
            if self.clock_in_form.winfo_manager() == "grid":
                # Determine next available grid row
                current_rows = [int(ch.grid_info().get("row", 0)) for ch in self.clock_in_form.winfo_children() if ch.winfo_manager() == "grid"]
                next_row = (max(current_rows) + 1) if current_rows else 0
                try:
                    self.clock_in_form.grid_rowconfigure(next_row, weight=0)
                except Exception:
                    pass
                widget.grid(row=next_row, column=0, sticky="w", padx=8, pady=4)
            else:
                widget.pack(anchor="w", padx=8, pady=4)
        except Exception:
            try:
                widget.pack(anchor="w", padx=8, pady=4)
            except Exception:
                pass
        return widget


if __name__ == "__main__":
    app = KeypadApp(themename="flatly")

    app.mainloop()