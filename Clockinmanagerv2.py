import sys
import tkinter as tk
from tkinter import ttk

from click import wrap_text

from Model import Project

# Try to enable ttkbootstrap theming if available (optional)
try:
    import ttkbootstrap as tb
    HAS_TTKBOOTSTRAP = True
except Exception:
    tb = None
    HAS_TTKBOOTSTRAP = False

# python
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select

try:
    # Project model import
    from Model.Hour import Hour as HourModel
    from Model.Student import Student
except Exception:
    HourModel = None  # type: ignore
from Persistance import session

# -----------------------------------------------------------------------------
# Test time controls (changeable at the top of the program)
# -----------------------------------------------------------------------------
# Set to True to enable test time. When False, the system clock is used.
USE_TEST_TIME: bool = True

# If set, acts as a frozen "now"
_TEST_FIXED: Optional[datetime] = None

# If set (with _TEST_REAL_EPOCH), acts as an advancing simulated clock:
# now = _TEST_SIM_EPOCH + (real_now - _TEST_REAL_EPOCH)
_TEST_SIM_EPOCH: Optional[datetime] = None
_TEST_REAL_EPOCH: Optional[datetime] = None


def _normalize_dt(dt: datetime) -> datetime:
    """Normalize timezone-aware datetimes to naive local to keep consistency."""
    if isinstance(dt, datetime) and dt.tzinfo is not None:
        return dt.astimezone().replace(tzinfo=None)
    return dt


def set_fixed_test_time(dt: datetime) -> None:
    """
    Enable a fixed test time (does not advance).
    """
    global USE_TEST_TIME, _TEST_FIXED, _TEST_SIM_EPOCH, _TEST_REAL_EPOCH
    dt = _normalize_dt(dt)
    USE_TEST_TIME = True
    _TEST_FIXED = dt
    _TEST_SIM_EPOCH = None
    _TEST_REAL_EPOCH = None


def set_advancing_test_time(dt: datetime) -> None:
    """
    Enable an advancing test time that moves forward with real time.
    """
    global USE_TEST_TIME, _TEST_SIM_EPOCH, _TEST_REAL_EPOCH, _TEST_FIXED
    dt = _normalize_dt(dt)
    USE_TEST_TIME = True
    _TEST_SIM_EPOCH = dt
    _TEST_REAL_EPOCH = datetime.now()
    _TEST_FIXED = None


def clear_test_time() -> None:
    """
    Disable test time and revert to the system clock.
    """
    global USE_TEST_TIME, _TEST_FIXED, _TEST_SIM_EPOCH, _TEST_REAL_EPOCH
    USE_TEST_TIME = False
    _TEST_FIXED = None
    _TEST_SIM_EPOCH = None
    _TEST_REAL_EPOCH = None


def advance_test_time(delta: timedelta) -> None:
    """
    Manually advance the simulated time by 'delta' when using a frozen time
    or an advancing simulated time.
    """
    global _TEST_SIM_EPOCH, _TEST_FIXED
    if _TEST_FIXED is not None:
        _TEST_FIXED += delta
    elif _TEST_SIM_EPOCH is not None:
        _TEST_SIM_EPOCH += delta


def _seconds_since_midnight(t) -> int:
    return t.hour * 3600 + t.minute * 60 + t.second


def _time_in_range(now_s: int, start_s: int, end_s: int) -> bool:
    """
    True if now is within [start, end) on a 24h clock.
    Handles windows that cross midnight (end < start).
    """
    if start_s <= end_s:
        return start_s <= now_s < end_s
    # crosses midnight
    return now_s >= start_s or now_s < end_s

class CheckinApp:
    def __init__(self, master: tk.Misc):
        self.master = master
        self.master.title("Two-Pane App (Hour Display + Form | Entry + Keypad)")

        # Top-level paned window: left (display + form), right (entry + keypad)
        self.outer_paned = ttk.Panedwindow(self.master, orient=tk.HORIZONTAL)
        self.outer_paned.pack(fill=tk.BOTH, expand=True)

        # Left pane (larger): hour_display at top + bottom form
        self.left_frame = ttk.Frame(self.outer_paned, padding=10)
        self._build_display_pane(self.left_frame)
        self.outer_paned.add(self.left_frame, weight=3)

        # Right pane: entry + keypad
        self.right_frame = ttk.Frame(self.outer_paned, padding=10)
        self._build_keypad_pane(self.right_frame)
        self.outer_paned.add(self.right_frame, weight=2)

        # Give a nicer initial split after layout
        self.master.after(100, self._set_initial_sashes)

    def _set_initial_sashes(self):
        # Put the split so the left pane is larger
        try:
            total = self.master.winfo_width()
            self.outer_paned.sashpos(0, max(320, int(total * 0.6)))
        except Exception:
            pass
        try:
            self.left_paned.sashpos(0, 80)
        except Exception:
            pass

    # LEFT PANE: hour_display label at top, bottom form
    def _build_display_pane(self, parent: ttk.Frame):
        parent.rowconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)

        self.left_paned = ttk.Panedwindow(parent, orient=tk.VERTICAL)
        self.left_paned.grid(row=0, column=0, sticky="nsew")

        # Top: hour_display label
        top_frame = ttk.Frame(self.left_paned, padding=(0, 10, 0, 10))
        self.hour_display = tk.StringVar(value="hour_display")
        hour_label = ttk.Label(top_frame, textvariable=self.hour_display, anchor="center", font=("", 20, "bold"))
        hour_label.pack(fill=tk.X, expand=False)
        self.left_paned.add(top_frame, weight=1)

        # Bottom: form area (buttons, labels, fields)
        form_frame = ttk.Frame(self.left_paned, padding=5)
        self._build_form(form_frame)
        self.left_paned.add(form_frame, weight=3)

    def _build_form(self, parent: ttk.Frame):
        parent.columnconfigure(1, weight=1)

        submit_btn = ttk.Button(parent, text="Submit", command=self._on_submit)
        cancel_btn = ttk.Button(parent, text="Cancel", command=self._on_cancel)

        btns = ttk.Frame(parent)
        btns.grid(row=2, column=0, columnspan=2, sticky="e", pady=(8, 0))
        submit_btn.grid(in_=btns, row=0, column=0, padx=(0, 6))
        cancel_btn.grid(in_=btns, row=0, column=1)

    # RIGHT PANE: entry + keypad (moved here)
    def _build_keypad_pane(self, parent: ttk.Frame):
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
                if char.isdigit():
                    self.entry_var.set(self.entry_var.get() + char)
            self.entry.icursor(tk.END)
            self.entry.focus_set()

        row_idx = 1
        for row in keypad_layout:
            for col_idx, char in enumerate(row):
                btn = ttk.Button(parent, text=char, command=lambda c=char: on_keypad(c))
                btn.grid(row=row_idx, column=col_idx, sticky="nsew", padx=4, pady=4)
            row_idx += 1

        for r in range(1, row_idx):
            parent.rowconfigure(r, weight=1)

        enter_btn = ttk.Button(parent, text="Enter", command=self._on_enter)
        enter_btn.grid(row=row_idx, column=0, columnspan=3, sticky="nsew", padx=4, pady=(8, 0))
        parent.rowconfigure(row_idx, weight=0)

        # Bind Return/Enter key from keyboard
        self.master.bind("<Return>", lambda _e: self._on_enter())

    def _build_student_clockin_form(self):
        pass


    def _on_enter(self):

        # For demo: reflect the entry to hour_display
        student_id_value = self.entry_var.get()

        id_val = ttk.Label(self.left_frame)
        id_val.configure(text=student_id_value)
        id_val.grid(row=0, column=1, sticky="ew", pady=4)

        """
            When Enter is pressed, try to identify a student using entry_var:
              1) Match studentID (int)
              2) Match glenpool_id (int)
              3) Match rfid (string)
            Update id_val accordingly.
            """
        text = ""
        if hasattr(self, "entry_var"):
            try:
                text = self.entry_var.get().strip()
                print(f'{text} was entered', file=sys.stdout)
            except Exception:
                text = ""

        # Choose a SQLAlchemy session: prefer self.session if present, else shared Persistance session


        student = None

        # 1) Try studentID (int)
        sid = None
        try:
            sid = int(text)
        except (TypeError, ValueError):
            sid = None

        if sid is not None:
            student = (
                session.query(Student)
                .filter(Student.studentID == sid)
                .first()
            )
            print(f'{sid} was found as TT SID', file=sys.stdout)

        # 2) Try glenpool_id (int) if still not found and input was numeric
        if student is None and sid is not None:
            student = (
                session.query(Student)
                .filter(Student._student_glenpool_ID == sid)
                .first()
            )
            print(f'{sid} was found as Glenpool ID', file=sys.stdout)

        # 3) Try rfid (string) if still not found
        if student is None and text:
            student = (
                session.query(Student)
                .filter(Student._studentRFID == text)
                .first()
            )
            print(f'{text} was found as RFID', file=sys.stdout)

        # Prepare display text
        if student is not None:

            display = f"{student.first_name} {student.last_name}".strip()
            print(f'{display} was found', file=sys.stdout)
            projects = Project.get_all_ordered_by_name()
            current_row = 2
            current_col = 1
            for project in projects:
                # Add newline every 80 chars for readability
                wrap_length = 30
                button_text = '\n'.join(project.name[i:i + wrap_length] for i in range(0, len(project.name), wrap_length))
                print(f'{button_text} was added', file=sys.stdout)

                btn = ttk.Button(self.left_frame, text=button_text)

                btn.grid(row=current_row, column=current_col, sticky="ew", pady=10, padx=10)
                current_col += 1
                if current_col > 4:
                    current_row += 1
                    current_col = 1
        else:
            display = "No Student Found, please tryagain"
            print(f'{display}', file=sys.stdout)

        id_val.configure(text=display)


        # Optionally clear the entry box for the next scan/entry
        if hasattr(self, "entry_var") and hasattr(self.entry_var, "set"):
            self.entry_var.set("")

    def _on_submit(self):
        print("Submit clicked", file=sys.stdout)

    def _on_cancel(self):
        print("Cancel clicked", file=sys.stdout)

    def _set_hour_display_text(self, text: str) -> None:
        """
        Set the hour_display to the provided text.
        Supports tkinter Variable via .set() or a widget via .config(text=...).
        """
        hour_display = getattr(self, "hour_display", None)

        # Try tkinter Variable
        try:
            if hour_display is not None and hasattr(hour_display, "set"):
                hour_display.set(text)
                return
        except Exception:
            pass

        # Try widget with config(text=...)
        try:
            if hour_display is not None and hasattr(hour_display, "config"):
                hour_display.config(text=text)
                return
        except Exception:
            pass

        # Common fallback label attribute
        try:
            lbl = getattr(self, "hour_display_label", None)
            if lbl is not None and hasattr(lbl, "config"):
                lbl.config(text=text)
        except Exception:
            pass

    def _get_current_hour_record(self) -> Optional[object]:
        """
        Return the Hour model row that matches the current time by start/end time.
        If multiple match, picks the most recently started hour relative to now.
        """
        if HourModel is None or session is None:
            #print(f"No HourModel {HourModel.hourID} or session {session} provided", file=sys.stderr)
            return None



        if USE_TEST_TIME:
            if _TEST_FIXED is not None:
                now = _TEST_FIXED
            elif _TEST_SIM_EPOCH is not None and _TEST_REAL_EPOCH is not None:
                delta = datetime.now() - _TEST_REAL_EPOCH
                now = _TEST_SIM_EPOCH + delta
            else:
                now = datetime.now()
        else:
            now = datetime.now()
        now_s = _seconds_since_midnight(now.time())


        # Fetch all hours; if you have many, consider filtering by active date range.
        rows = session.execute(select(HourModel)).scalars().all()

        best = None
        best_delta = None

        for h in rows:
            # Be tolerant to either public or private attribute naming
            start_t = getattr(h, "start_time", getattr(h, "_start_time", None))
            end_t = getattr(h, "end_time", getattr(h, "_end_time", None))
            if not start_t or not end_t:
                continue

            start_s = _seconds_since_midnight(start_t)
            end_s = _seconds_since_midnight(end_t)

            if not _time_in_range(now_s, start_s, end_s):
                continue

            # Choose the most recent start relative to now (mod 24h)
            delta = (now_s - start_s) % 86400
            if best is None or delta < best_delta:
                best = h
                best_delta = delta

        return best

    def update_hour_display(self) -> None:
        """
        Set hour_display to the name of the current Hour based on current time.
        """


        current = self._get_current_hour_record()

        name = ""
        if current is not None:
            name = getattr(current, "name", getattr(current, "_name", "")) or ""
            self._set_hour_display_text(name)

    def start_hour_display_auto_update(self, interval_ms: int = 60_000) -> None:
        """
        Optional: call this once to keep hour_display updated every interval_ms.
        This method is idempotent; calling it multiple times won't schedule duplicates.
        """
        # Prevent duplicate schedulers
        if getattr(self, "_hour_auto_update_running", False):
            return
        self._hour_auto_update_running = True

        root = getattr(self, "root", None) or getattr(self, "master", None)
        if root is None:
            # No GUI loop available; still do a one-time refresh
            self.update_hour_display()
            return

        def _tick():
            try:
                self.update_hour_display()
            finally:
                try:
                    root.after(interval_ms, _tick)
                except Exception:
                    # If root is gone, stop scheduling
                    self._hour_auto_update_running = False

        # Immediate first refresh, then schedule
        self.update_hour_display()
        _tick()



def main():
    # Set up test time to Sep 6 12pm
    test_datetime = datetime(2025, 9, 6, 12, 0, 0)
    set_advancing_test_time(test_datetime)

    if HAS_TTKBOOTSTRAP:
        root = tb.Window(themename="flatly")
    else:
        root = tk.Tk()
    app = CheckinApp(root)
    root.geometry("900x520")
    root.minsize(640, 400)
    app.start_hour_display_auto_update(interval_ms=60000)  # schedules immediate refresh + periodic updates
    root.mainloop()


if __name__ == "__main__":
    main()
# python