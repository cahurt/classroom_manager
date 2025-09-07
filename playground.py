# Python
import ttkbootstrap as tb
from ttkbootstrap.dialogs import Messagebox
from datetime import datetime, date, time, timedelta
import tkinter as tk

# Project modules
import Persistance
from Model.Student import Student
from Model.Project import Project
from Model.Checkin import Checkin
from Model.Hour import Hour
import HourManager  # used for countdown formatting (format_countdown_for_display)


class StartupDialog(tb.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Start Options")
        self.transient(master)
        self.grab_set()
        self.resizable(False, False)

        self.var_sub_day = tk.BooleanVar(value=False)
        self.var_assembly = tk.BooleanVar(value=False)

        frm = tb.Frame(self, padding=20)
        frm.pack(fill="both", expand=True)

        tb.Label(frm, text="Choose schedule options", bootstyle="inverse").pack(anchor="w", pady=(0, 8))
        tb.Checkbutton(frm, text="Sub Day", variable=self.var_sub_day, bootstyle="round-toggle").pack(anchor="w", pady=4)
        tb.Checkbutton(frm, text="Assembly Schedule", variable=self.var_assembly, bootstyle="round-toggle").pack(anchor="w", pady=4)

        btns = tb.Frame(frm)
        btns.pack(fill="x", pady=(12, 0))
        tb.Button(btns, text="Start", bootstyle="success", command=self._ok).pack(side="right", padx=6)
        tb.Button(btns, text="Cancel", bootstyle="secondary", command=self._cancel).pack(side="right")

        self.result = None
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.wait_visibility()
        self.focus_set()
        self.wait_window(self)

    def _ok(self):
        self.result = {
            "sub_day": self.var_sub_day.get(),
            "assembly": self.var_assembly.get(),
        }
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


class CheckinKioskApp:
    def __init__(self):
        # DB/session
        Persistance.Base.metadata.create_all(Persistance.engine)
        self.session = Persistance.Session()

        # Window (same style as ProjectManager)
        self.root = tb.Window(themename="superhero")
        self.root.title("Foundations of Manufacturing - Check-in")
        self.root.geometry("1280x1024")

        # Time control
        self._use_test_time = False
        self._test_now = None  # set via self.set_test_time

        # State from startup dialog
        self.is_sub_day = False
        self.is_assembly = False

        # UI state
        self.current_hour_obj = None
        self.current_student = None

        # Panels
        self.hour_display = None
        self.project_information = None
        self.student_entry = None
        self.student_var = tk.StringVar(value="")
        self.student_name_label = None
        self.countdown_label = None
        self.hour_name_label = None

        # Load options then build UI
        self._start_dialog()
        if self.is_sub_day is None:
            # user canceled
            self.root.destroy()
            return

        self._build_layout()
        self._refresh_hour()
        self._update_countdown()
        self.root.after(1000, self._tick)

    # -------- Time helpers --------
    def now(self) -> datetime:
        """
        Return the current time, using test time if set, otherwise real time.
        """
        if self._use_test_time and isinstance(self._test_now, datetime):
            return self._test_now
        return datetime.now()

    def set_test_time(self, dt: datetime | None):
        """
        Set or clear test time. Pass None to switch back to real time.
        """
        if dt is None:
            self._use_test_time = False
            self._test_now = None
        else:
            self._use_test_time = True
            self._test_now = dt

    def advance_test_time(self, delta: timedelta):
        """
        Advance test time by delta (only if test time is active).
        """
        if self._use_test_time and self._test_now:
            self._test_now += delta

    # -------- Startup dialog --------
    def _start_dialog(self):
        self.root.withdraw()
        dlg = StartupDialog(self.root)
        if not dlg.result:
            self.is_sub_day = None
            return
        self.is_sub_day = bool(dlg.result["sub_day"])
        self.is_assembly = bool(dlg.result["assembly"])
        self.root.deiconify()

    # -------- UI layout --------
    def _build_layout(self):
        # Main grid: left 2/3 for hour + projects; right 1/3 for keypad + entry
        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        left = tb.Frame(self.root, padding=10)
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(0, weight=0)  # hour_display
        left.rowconfigure(1, weight=1)  # project_information
        left.columnconfigure(0, weight=1)

        right = tb.Frame(self.root, padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(0, weight=0)  # entry
        right.rowconfigure(1, weight=1)  # keypad
        right.columnconfigure(0, weight=1)

        # Hour Display (top-left)
        self.hour_display = tb.Labelframe(left, text="Current Period", padding=10, bootstyle="info")
        self.hour_display.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        self.hour_display.columnconfigure(0, weight=1)
        self.hour_name_label = tb.Label(self.hour_display, text="—", font=("Segoe UI", 16, "bold"))
        self.hour_name_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
        self.countdown_label = tb.Label(self.hour_display, text="--:--", font=("Consolas", 20), bootstyle="inverse")
        self.countdown_label.grid(row=0, column=1, sticky="e")

        # Project Information (bottom-left)
        self.project_information = tb.Labelframe(left, text="Projects", padding=10, bootstyle="primary")
        self.project_information.grid(row=1, column=0, sticky="nsew")
        self.project_information.columnconfigure(0, weight=1)
        self._clear_project_info()

        # Right side: entry + keypad
        self._build_student_entry(right)
        self._build_keypad(right)

    def _build_student_entry(self, parent):
        entry_frame = tb.Labelframe(parent, text="Student ID Entry", padding=10, bootstyle="secondary")
        entry_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        entry_frame.columnconfigure(0, weight=1)

        self.student_entry = tb.Entry(entry_frame, textvariable=self.student_var, justify="right", font=("Consolas", 16))
        self.student_entry.grid(row=0, column=0, sticky="ew")
        self.student_entry.bind("<Return>", lambda e: self._on_student_entered())
        self.student_entry.focus_set()

        # Optional quick controls when testing time
        ctrl = tb.Frame(entry_frame)
        ctrl.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        tb.Button(ctrl, text="Use Real Time", bootstyle="secondary-outline", command=lambda: self.set_test_time(None)).pack(side="left")
        tb.Button(ctrl, text="+1 min (test)", bootstyle="warning-outline", command=lambda: self._bump_time_for_test(minutes=1)).pack(side="left", padx=6)

    def _build_keypad(self, parent):
        pad = tb.Labelframe(parent, text="Number Pad", padding=10, bootstyle="dark")
        pad.grid(row=1, column=0, sticky="nsew")
        for r in range(4):
            pad.rowconfigure(r, weight=1)
        for c in range(3):
            pad.columnconfigure(c, weight=1)

        def mkbtn(txt, r, c, cmd=None, style="secondary"):
            b = tb.Button(pad, text=txt, bootstyle=style, command=cmd)
            b.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)
            return b

        # Digits
        digits = [
            ("1", 0, 0), ("2", 0, 1), ("3", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("7", 2, 0), ("8", 2, 1), ("9", 2, 2),
            ("C", 3, 0), ("0", 3, 1), ("⌫", 3, 2),
        ]
        for d, r, c in digits:
            if d.isdigit():
                mkbtn(d, r, c, cmd=lambda x=d: self._push_digit(x))
            elif d == "C":
                mkbtn("Clear", r, c, cmd=self._clear_entry, style="danger")
            else:
                mkbtn("Back", r, c, cmd=self._backspace, style="warning")

        # Enter button below (spans all columns)
        enter_btn = tb.Button(pad, text="Enter", bootstyle="success", command=self._on_student_entered)
        enter_btn.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=4, pady=(8, 0))

    # -------- UI events / handlers --------
    def _push_digit(self, d: str):
        self.student_var.set(self.student_var.get() + d)

    def _clear_entry(self):
        self.student_var.set("")

    def _backspace(self):
        s = self.student_var.get()
        if s:
            self.student_var.set(s[:-1])

    def _on_student_entered(self):
        code = self.student_var.get().strip()
        if not code.isdigit():
            Messagebox.show_warning("Please enter digits only.", "Invalid Entry", parent=self.root)
            return

        student = self._find_student_by_code(code)
        if not student:
            Messagebox.show_info(f"No student found for ID {code}.", "Not Found", parent=self.root)
            self.current_student = None
            self._clear_project_info()
            return

        self.current_student = student
        self._populate_projects_for_student(student)

    # -------- DB lookups --------
    def _find_student_by_code(self, code: str):
        """
        Find a student by a numeric code. Tries several common fields safely.
        """
        try:
            # Pull all or filter if the field is known.
            students = self.session.query(Student).all()
        except Exception:
            return None

        for s in students:
            candidates = []
            # Try a set of possible attributes
            for attr in ("student_ID", "studentID", "tt_sid", "ttsid", "id", "sid", "_student_ID"):
                if hasattr(s, attr):
                    val = getattr(s, attr)
                    if val is not None:
                        candidates.append(str(val))
            # Deduplicate
            if code in set(candidates):
                return s
        return None

    def _get_open_projects_ordered(self):
        """
        Prefer using Project.get_all_ordered_by_name if available, otherwise fallback to a simple query.
        Filters to 'open' projects if open/close dates exist.
        """
        projects = []
        # Try provided method first
        try:
            if hasattr(Project, "get_all_ordered_by_name"):
                maybe = Project.get_all_ordered_by_name()
                projects = list(maybe) if maybe is not None else []
        except Exception:
            projects = []

        if not projects:
            # Fallback: pull all and sort by display or internal name
            try:
                projects = self.session.query(Project).all()
            except Exception:
                projects = []

            # Filter to 'open' if open/close date fields exist
            now_dt = self.now()
            filtered = []
            for p in projects:
                open_ok = True
                od = getattr(p, "_open_date", None) or getattr(p, "open_date", None)
                cd = getattr(p, "_close_date", None) or getattr(p, "close_date", None)
                if od and isinstance(od, (date, datetime)):
                    od_dt = datetime.combine(od, time.min) if isinstance(od, date) and not isinstance(od, datetime) else od
                    if now_dt < od_dt:
                        open_ok = False
                if cd and isinstance(cd, (date, datetime)):
                    cd_dt = datetime.combine(cd, time.max) if isinstance(cd, date) and not isinstance(cd, datetime) else cd
                    if now_dt > cd_dt:
                        open_ok = False
                if open_ok:
                    filtered.append(p)
            projects = filtered

            # Sort
            def keyproj(x):
                return (getattr(x, "_display_name", None)
                        or getattr(x, "display_name", None)
                        or getattr(x, "_name", None)
                        or getattr(x, "name", None)
                        or "").lower()
            projects.sort(key=keyproj)
        return projects

    # -------- Hour / countdown --------
    def _refresh_hour(self):
        self.current_hour_obj = self._find_current_hour()
        if self.current_hour_obj:
            hname = (getattr(self.current_hour_obj, "display_name", None)
                     or getattr(self.current_hour_obj, "_display_name", None)
                     or getattr(self.current_hour_obj, "name", None)
                     or getattr(self.current_hour_obj, "_name", None)
                     or "Current Hour")
            self.hour_name_label.configure(text=str(hname))
        else:
            self.hour_name_label.configure(text="No Active Hour")

    def _find_current_hour(self):
        """
        Determine the current Hour object based on now() and selected schedule.
        Tries to use start/end fields; also checks for assembly-specific fields.
        """
        try:
            hours = self.session.query(Hour).all()
        except Exception:
            return None

        now_dt = self.now()
        today = now_dt.date()

        def resolve_time(h, start_names, end_names):
            st = et = None
            for n in start_names:
                if hasattr(h, n):
                    st = getattr(h, n)
                    break
            for n in end_names:
                if hasattr(h, n):
                    et = getattr(h, n)
                    break
            # Convert to datetimes for today if they are times
            if isinstance(st, time):
                st = datetime.combine(today, st)
            if isinstance(et, time):
                et = datetime.combine(today, et)
            return st, et

        # Choose which fields to check based on "Assembly Schedule"
        if self.is_assembly:
            start_candidates = ("assembly_start_time", "assembly_start", "_assembly_start_time")
            end_candidates = ("assembly_end_time", "assembly_end", "_assembly_end_time")
        else:
            start_candidates = ("start_time", "_start_time", "normal_start_time")
            end_candidates = ("end_time", "_end_time", "normal_end_time")

        # Fallback if above missing and sub-day selected (try sub-day fields if they exist)
        sub_start_candidates = ("sub_start_time", "_sub_start_time")
        sub_end_candidates = ("sub_end_time", "_sub_end_time")

        # Scan all hours and return the one containing now
        selected = None
        for h in hours:
            st, et = resolve_time(h, start_candidates, end_candidates)
            if (st is None or et is None) and self.is_sub_day:
                st, et = resolve_time(h, sub_start_candidates, sub_end_candidates)
            if st and et and st <= now_dt <= et:
                selected = h
                break
        return selected

    def _update_countdown(self):
        """
        Update the countdown display using HourManager's formatting logic if available.
        """
        now_dt = self.now()
        # Determine end time of current hour
        if self.current_hour_obj:
            # Pick proper end
            if self.is_assembly and hasattr(self.current_hour_obj, "assembly_end_time"):
                end_val = getattr(self.current_hour_obj, "assembly_end_time")
            elif self.is_sub_day and hasattr(self.current_hour_obj, "sub_end_time"):
                end_val = getattr(self.current_hour_obj, "sub_end_time")
            else:
                end_val = (getattr(self.current_hour_obj, "end_time", None)
                           or getattr(self.current_hour_obj, "_end_time", None)
                           or getattr(self.current_hour_obj, "normal_end_time", None))
        else:
            end_val = None

        if isinstance(end_val, time):
            end_dt = datetime.combine(now_dt.date(), end_val)
        elif isinstance(end_val, datetime):
            end_dt = end_val
        else:
            end_dt = None

        if end_dt:
            remaining = max(0, int((end_dt - now_dt).total_seconds()))
            try:
                disp = HourManager.format_countdown_for_display(remaining)
            except Exception:
                # Simple fallback MM:SS
                m, s = divmod(remaining, 60)
                disp = f"{m:02d}:{s:02d}"
        else:
            disp = "--:--"

        self.countdown_label.configure(text=disp)

    def _tick(self):
        """
        Periodic update loop for hour change and countdown.
        """
        prev_hour = self.current_hour_obj
        self._refresh_hour()
        # If the hour switched, you could beep or notify here if desired.
        self._update_countdown()

        # If using test time, you may want to auto-advance during testing (disabled by default).
        # Example: self.advance_test_time(timedelta(seconds=1))
        self.root.after(1000, self._tick)

    def _bump_time_for_test(self, minutes=1):
        # Enable test time if not enabled
        if not self._use_test_time:
            self.set_test_time(self.now())
        self.advance_test_time(timedelta(minutes=minutes))
        self._refresh_hour()
        self._update_countdown()

    # -------- Project grid and check-in --------
    def _clear_project_info(self):
        for w in self.project_information.winfo_children():
            w.destroy()
        # Put a placeholder label and keep a spot where the student name can appear
        self.student_name_label = tb.Label(self.project_information, text="Enter a student ID to see projects.", bootstyle="secondary")
        self.student_name_label.grid(row=0, column=0, sticky="w")

    def _populate_projects_for_student(self, student):
        # Clear existing
        for w in self.project_information.winfo_children():
            w.destroy()

        # Student name at top
        sname = (getattr(student, "display_name", None)
                 or getattr(student, "_display_name", None)
                 or getattr(student, "name", None)
                 or getattr(student, "_name", None)
                 or getattr(student, "first_last_name", None)
                 or "Selected Student")
        self.student_name_label = tb.Label(self.project_information, text=f"Student: {sname}", font=("Segoe UI", 12, "bold"))
        self.student_name_label.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 8))

        projects = self._get_open_projects_ordered()
        if not projects:
            tb.Label(self.project_information, text="No open projects.", bootstyle="warning").grid(row=1, column=0, sticky="w")
            return

        # Grid of buttons
        cols = 4
        for idx, proj in enumerate(projects, start=0):
            r = 1 + idx // cols
            c = idx % cols
            pname = (getattr(proj, "display_name", None)
                     or getattr(proj, "_display_name", None)
                     or getattr(proj, "name", None)
                     or getattr(proj, "_name", None)
                     or f"Project {idx+1}")
            btn = tb.Button(self.project_information, text=str(pname), bootstyle="primary", command=lambda p=proj: self._on_project_clicked(p))
            btn.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
            self.project_information.columnconfigure(c, weight=1)

    def _on_project_clicked(self, project):
        if not self.current_student:
            Messagebox.show_warning("Please enter a valid student ID first.", "No Student", parent=self.root)
            return

        # Create Checkin
        try:
            chk = Checkin()
            # Set relationships/properties robustly
            self._safe_set(chk, "checkin_student", self.current_student)
            self._safe_set(chk, "checkin_project", project)
            self._safe_set(chk, "checkin_datetime", self.now())
            self._safe_set(chk, "last_edited", self.now())
            # If hour available, set it too
            if self.current_hour_obj is not None:
                self._safe_set(chk, "checkin_hour", self.current_hour_obj)

            self.session.add(chk)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            Messagebox.show_error(f"Failed to create check-in.\n{e}", "Error", parent=self.root)
            return

        # Clear project info and student entry after successful check-in
        self._clear_project_info()
        self.current_student = None
        self.student_var.set("")
        Messagebox.show_info("Check-in recorded.", "Success", parent=self.root)

    @staticmethod
    def _safe_set(obj, attr_name, value):
        """
        Try property first (setter), otherwise set attribute if present.
        """
        try:
            setattr(obj, attr_name, value)
        except Exception:
            # try backing field if any common names exist
            for alt in (f"_{attr_name}",):
                if hasattr(obj, alt):
                    try:
                        setattr(obj, alt, value)
                        return
                    except Exception:
                        pass
            raise

    # -------- Run --------
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CheckinKioskApp()
    # Example: to test with fixed time
    # app.set_test_time(datetime.now().replace(hour=9, minute=5, second=0, microsecond=0))
    if app.is_sub_day is not None:
        app.run()