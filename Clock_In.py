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


# 2) Make the dialog non-blocking in __init__, avoid wait_visibility here
class StartupDialog(tb.Toplevel):
    def __init__(self, master):
        super().__init__(master)

        # Basic window settings
        self.withdraw()               # start hidden to avoid flicker
        self.transient(master)        # keep on top of parent
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

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
        #self.protocol("WM_DELETE_WINDOW", self._cancel)
        #self.wait_visibility()
        #self.focus_set()
        #self.wait_window(self)

        # Finalize showing the dialog once idle (event loop is running)
        self.after_idle(self._show_modal)

    def _show_modal(self):
        # Map and focus the dialog without using wait_visibility
        try:
            self.deiconify()
            self.lift()
            self.grab_set()           # modal behavior
            self.focus_force()
            self.update_idletasks()
        except Exception as ex:
            print(f"[StartupDialog] show failed: {ex}")

    def _on_cancel(self):
        # release grab automatically when the window is destroyed
        self.destroy()

    def _ok(self):
        self.result = {
            "sub_day": self.var_sub_day.get(),
            "assembly": self.var_assembly.get(),
        }
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


# 1) Defer dialog creation until after mainloop starts
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
        self._use_test_time = True
        self._test_now = datetime(2025,9,8,11,22)  # set via self.set_test_time

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

        # Instead of: self._start_dialog()
        # Defer to when the event loop is running
        self.root.after(0, self._start_dialog)

    def _start_dialog(self):
        dlg = StartupDialog(self.root)
        # If you need to block app flow until the dialog is closed,
        # this is safe now because we're already in the event loop.
        self.root.wait_window(dlg)
        # Continue with the rest of your startup after dialog closes...
        # e.g., self._init_main_ui()

        if not dlg.result:
            self.is_sub_day = None
            self.root.destroy()
            return

        self.is_sub_day = bool(dlg.result["sub_day"])
        self.is_assembly = bool(dlg.result["assembly"])

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
    #def _start_dialog(self):
    #    self.root.withdraw()
    #    dlg = StartupDialog(self.root)
    #    if not dlg.result:
    #        self.is_sub_day = None
    #        return
    #    self.is_sub_day = bool(dlg.result["sub_day"])
    #    self.is_assembly = bool(dlg.result["assembly"])
    #    self.root.deiconify()

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
        Find a student by a numeric code. Tries 3 possible IDs for flexibility
        """
        try:
            student = Student.get_by_id(code)
            if student is None:
                student = Student.get_by_glenpool_id(code)
                if student is None:
                    student = Student.get_by_reg_id(code)
        except Exception:
            return None

        return student


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
            self._clear_project_info()

    def _find_current_hour(self):
        """
        Determine the current Hour object based on now() and selected schedule.
        Tries to use start/end fields; also checks for assembly-specific fields.
        """
        now_dt = self.now()
        today = now_dt.date()

        try:
            hour = Hour.get_by_time(now_dt.time())
        except Exception:
            return None

        if hour is None:
            hour = Hour.get_next_by_time(now_dt.time())


        return hour

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
            else:
                end_val = (getattr(self.current_hour_obj, "end_time", None))
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
        if self.current_student is None:
            self._update_current_checkins()

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
        self.advance_test_time(timedelta(seconds=1))
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
        self._update_current_checkins()

# python
    def _update_current_checkins(self):
        self._refresh_hour()
        if self.current_hour_obj:
            checkins = Checkin.get_checkins_by_hour_today(self.current_hour_obj)

            # Normalize to a list so we can iterate safely
            if checkins is None:
                checkins = []
            elif isinstance(checkins, Checkin):
                checkins = [checkins]
            else:
                # Convert generic iterables (e.g., SQLAlchemy results) to a concrete list
                try:
                    checkins = list(checkins)
                except TypeError:
                    checkins = [checkins]

            current_row = 2
            current_col = 0
            for checkin in checkins:
                display_text = f'{checkin.checkin_student.first_name} {checkin.checkin_student.last_name} - {checkin.checkin_project.display_name}'
                self.student_with_checkin_label = tb.Label(self.project_information, text=display_text, font=("Segoe UI", 10, "bold"), style="success")
                self.student_with_checkin_label.grid(row=current_row, column=current_col, sticky="w", pady=(0, 8))
                current_col += 1
                if current_col >= 1:
                    current_row += 1
                    current_col = 0

            current_row +=2
            current_col = 0
            students_without_checkins = Student.get_students_without_checkin_today(self.current_hour_obj)
            for student in students_without_checkins:
                display_text = f'{student.first_name} {student.last_name}'
                self.student_without_checkin_label = tb.Label(self.project_information, text=display_text, font=("Segoe UI", 8, "bold"), style="danger")
                self.student_without_checkin_label.grid(row=current_row, column=current_col, sticky="w", pady=(0, 8))
                current_col += 1
                if current_col >= 1:
                    current_row += 1
                    current_col = 0

    def _populate_projects_for_student(self, student):
        # Clear existing
        for w in self.project_information.winfo_children():
            w.destroy()

        # Student name at top
        student_first_name = (getattr(student, "first_name", None)
                 or "Selected Student")
        student_last_name = (getattr(student, "last_name", None)
                              or "Selected Student")
        self.student_name_label = tb.Label(self.project_information, text=f"Student: {student_first_name} {student_last_name}", font=("Segoe UI", 12, "bold"))
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
        existing_checkin = Checkin.get_checkins_by_hour_and_student_today(self.current_hour_obj, self.current_student)
        has_existing_checkin = False
        if existing_checkin is not None:
            has_existing_checkin = True
        # Create Checkin
        try:
            print(f"Creating check-in for {self.current_student} on {project}, {self.current_hour_obj.hourID}")
            if not has_existing_checkin:
                chk = Checkin(self.now(), self.current_hour_obj, self.current_student, project)
            else:
                chk = existing_checkin
                chk.datetime = self.now()
                #chk.last_edited = self.now()
                chk.checkin_hour = self.current_hour_obj
                chk.checkin_project = project
                chk.checkin_student = self.current_student

                #Messagebox.show_info("Check-in updated.", "Success", parent=self.root)
            chk.save()


        except Exception as e:
            self.session.rollback()
            Messagebox.show_error(f"Failed to create check-in.\n{e}", "Error", parent=self.root)
            return

        # Clear project info and student entry after successful check-in
        self._clear_project_info()
        self.current_student = None
        self.student_var.set("")
        #Messagebox.show_info("Check-in recorded.", "Success", parent=self.root)

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

# python
import threading
import faulthandler
import tkinter as tk

def _verify_main_thread_and_root(app):
    cur = threading.current_thread()
    main = threading.main_thread()
    print(f"[Verify] current_thread={cur.name} ident={cur.ident}")
    print(f"[Verify] main_thread={main.name} ident={main.ident}")
    if cur is not main:
        raise RuntimeError("GUI must be created and run on the main thread.")

    root = getattr(app, "root", None)
    if root is None:
        raise RuntimeError("Application has no 'root' attribute.")

    if not isinstance(root, (tk.Tk, tk.Toplevel)):
        pass
       # print(f"[Verify] Unexpected root type: {type(root)!r}")

    try:
        root.update_idletasks()
        state = root.state() if hasattr(root, "state") else "?"
        print(f"[Verify] winfo_exists={root.winfo_exists()} viewable={root.winfo_viewable()} state={state}")
        print(f"[Verify] geometry={root.winfo_geometry()} title={root.title()!r}")
    except Exception as ex:
        pass
        #print(f"[Verify] Root inspection failed: {ex}")

    def _report_after():
        t = threading.current_thread()
       # print(f"[Verify] Tk after() running on thread={t.name} ident={t.ident}")

    try:
        root.after(10, _report_after)
    except Exception as ex:
        pass
       # print(f"[Verify] Scheduling after() failed: {ex}")

    return root


def run_app(app):
    root = _verify_main_thread_and_root(app)

    # Ensure it’s visible and front-most before entering mainloop
    for action in (
        lambda: root.overrideredirect(False),
        lambda: root.attributes("-alpha", 1.0),
        lambda: root.state("normal"),
        lambda: root.deiconify(),
    ):
        try:
            action()
        except Exception:
            pass

    # Optional: let the app set title/geometry
    if hasattr(app, "setup_window") and callable(app.setup_window):
        try:
            app.setup_window()
        except Exception as ex:
            pass
           # print(f"[Run] setup_window() raised: {ex}")

    try:
        root.lift()
        root.attributes("-topmost", True)
        root.after(200, lambda: root.attributes("-topmost", False))
        root.focus_force()
    except Exception:
        pass

    # Help surface exceptions from Tk callbacks
    def _tk_error_handler(exc, val, tb):
        import traceback, sys
        #print("Tk callback exception:", file=sys.stderr)
        traceback.print_exception(exc, val, tb)

    try:
        root.report_callback_exception = _tk_error_handler
    except Exception:
        pass

    print("[Run] Entering mainloop()")
    root.mainloop()
    print("[Run] mainloop() returned")


def _dump_threads(reason):
    import sys, traceback
    #print(f"[Watchdog] {reason}")
    for tid, frame in sys._current_frames().items():
        thr = next((t for t in threading.enumerate() if t.ident == tid), None)
        #print(f"\n[Watchdog] Thread {thr.name if thr else '?'} ({tid}):")
        #traceback.print_stack(frame)


if __name__ == "__main__":
    import sys
    import traceback

    faulthandler.enable()
    print("Starting Clock_In.py...")

    # Watchdog if app creation blocks
    create_timer = threading.Timer(5.0, lambda: _dump_threads("Possible hang while creating app"))
    create_timer.daemon = True
    create_timer.start()

    try:
        #print("[Entry] Creating app...")
        app = CheckinKioskApp()
        #print("[Entry] App created.")
    except Exception:
        #print("[Entry] App creation failed:")
        traceback.print_exc()
        sys.exit(1)
    finally:
        create_timer.cancel()

    # Watchdog if run_app() never starts or blocks before mainloop
    run_timer = threading.Timer(5.0, lambda: _dump_threads("Possible hang before entering mainloop"))
    run_timer.daemon = True
    run_timer.start()

    try:
        #print("[Entry] Calling run_app(app)...")
        run_app(app)
        #print("[Entry] run_app() returned (window closed).")
    except Exception:
        #print("[Entry] run_app() raised:")
        #traceback.print_exc()
        sys.exit(1)
    finally:
        run_timer.cancel()