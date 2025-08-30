# Python
from __future__ import annotations

import sys
import threading
from dataclasses import dataclass
from datetime import datetime, date, time, timedelta
from typing import Callable, Iterable, List, Optional, Tuple, Union

# UI imports
try:
    import ttkbootstrap as tb
    from ttkbootstrap.constants import CENTER, E, W, NSEW
except Exception as exc:
    raise RuntimeError(
        "This program requires ttkbootstrap to run. Please ensure it is installed in your virtualenv."
    ) from exc

import tkinter as tk
from tkinter import messagebox

# --- Add near the top of the file (after imports) ---
class Phases:
    MORNING_BRIEFING = "daily_briefing"
    IN_HOUR = "in_hour"
    BETWEEN_HOURS = "between_hours"
    CLEANUP = "cleanup"

ALL_PHASES = (
    Phases.MORNING_BRIEFING,
    Phases.IN_HOUR,
    Phases.BETWEEN_HOURS,
    Phases.CLEANUP,
)


def _normalize_phase_cleanup(state):
    """
    Ensure cleanup is represented as a proper phase while preserving
    the existing cleanup_active boolean for backward compatibility.
    """
    if getattr(state, "cleanup_active", False):
        state.phase = Phases.CLEANUP
        if not getattr(state, "label", None):
            state.label = "Cleanup"
    return state


# Add this near the top-level of HourManager.py (before HourManagerApp)
def format_countdown_for_display(
    target_or_delta: Union[datetime, timedelta, int, float],
    now_dt: Optional[datetime] = None,
    phase_name: Optional[str] = None,
    ) -> str:
    """
    Format a countdown value. Strictly shows seconds only during Cleanup or Daily Briefing.
    - target_or_delta: future datetime, timedelta, or seconds (int/float).
    """
    current = now_dt or datetime.now()

    # Compute remaining seconds
    if isinstance(target_or_delta, datetime):
        remaining_seconds = int((target_or_delta - current).total_seconds())
    elif isinstance(target_or_delta, timedelta):
        remaining_seconds = int(target_or_delta.total_seconds())
    else:
        remaining_seconds = int(target_or_delta)

    if remaining_seconds < 0:
        remaining_seconds = 0
    #print(phase_name, remaining_seconds)
    # Strict phase check (no substring matches)
    normalized_phase = " ".join((phase_name or "").strip().lower().split())
    allowed_aliases = {
        "cleanup",
        "clean-up",
        "between_hours",
        "daily_briefing",

    }
    show_sec = normalized_phase in allowed_aliases

    if show_sec:
        # H:MM:SS (omit hours when zero)
        h, rem = divmod(remaining_seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
    else:
        # Hide seconds: round up to the next minute
        minutes_total = (remaining_seconds + 59) // 60
        h, m = divmod(minutes_total, 60)
        return f"{h}:{m:02d}" if h else f"{m:02d}"


# If you previously added a wrapper named format_countdown, keep it:
def format_countdown(*args, **kwargs) -> str:
    return format_countdown_for_display(*args, **kwargs)


# Sound (Windows-friendly); will noop gracefully on non-Windows
try:
    import winsound

    def beep_once():
        try:
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            try:
                winsound.Beep(880, 250)
            except Exception:
                pass
except Exception:
    def beep_once():
        # Cross-platform soft fallback; won't error if sound not supported
        try:
            print("\a", end="")
        except Exception:
            pass

# Try to inherit theme from ProjectManager if available, otherwise fallback
def _resolve_theme() -> str:
    potential_attrs = ("DEFAULT_THEME", "PROJECT_THEME", "APP_THEME", "THEME")
    try:
        import ProjectManager as _pm  # type: ignore
        for attr in potential_attrs:
            if hasattr(_pm, attr):
                theme = getattr(_pm, attr)
                if isinstance(theme, str) and theme:
                    return theme
    except Exception:
        pass
    # Reasonable defaults similar to typical ProjectManager styles
    return "flatly"


# A method to use the real current time or a test time.
# - Call set_test_time(datetime) to enable test time.

# - Call clear_test_time() to use the real current time again.
_test_time_lock = threading.Lock()
_test_time: Optional[datetime] = None

# Epoch-based simulated time: when test time is set, we store both the simulated
# start instant and the real-world instant. get_now() then advances automatically.
# These globals should be at module scope.
_TEST_EPOCH_SIM = None  # type: typing.Optional[datetime]
_TEST_EPOCH_REAL = None  # type: typing.Optional[datetime]

def get_now() -> datetime:
    """Return current time. In test mode, return simulated time that advances."""
    global _TEST_EPOCH_SIM, _TEST_EPOCH_REAL
    if _TEST_EPOCH_SIM is not None and _TEST_EPOCH_REAL is not None:
        # Advance simulated time by how much real time has elapsed since enabling test mode.
        return _TEST_EPOCH_SIM + (datetime.now() - _TEST_EPOCH_REAL)
    return datetime.now()

def set_test_time(dt: datetime) -> None:
    """
    Enable test time override that advances with real time.
    dt: baseline simulated datetime to start from.
    """
    global _TEST_EPOCH_SIM, _TEST_EPOCH_REAL
    # Normalize timezone-aware datetimes to naive local to keep consistency with the rest of the app
    if isinstance(dt, datetime) and dt.tzinfo is not None:
        dt = dt.astimezone().replace(tzinfo=None)

    _TEST_EPOCH_SIM = dt
    _TEST_EPOCH_REAL = datetime.now()

def clear_test_time() -> None:
    """Disable test time override and return to real time."""
    global _TEST_EPOCH_SIM, _TEST_EPOCH_REAL
    _TEST_EPOCH_SIM = None
    _TEST_EPOCH_REAL = None

def advance_test_seconds(seconds: float) -> None:
    """
    Jump the simulated time forward (or backward with negative values).
    If test mode is not active, it will start from current real time.
    """
    global _TEST_EPOCH_SIM, _TEST_EPOCH_REAL
    if _TEST_EPOCH_SIM is None or _TEST_EPOCH_REAL is None:
        # Start test mode from now if not already active
        set_test_time(datetime.now())
    _TEST_EPOCH_SIM = _TEST_EPOCH_SIM + timedelta(seconds=seconds)


def now() -> datetime:
    """Centralized 'current time' function honoring test-time override."""
    with _test_time_lock:
        return _test_time if _test_time is not None else datetime.now()


# --------- Database access for Model.Hour ---------
@dataclass
class HourRecord:
    """Normalized hour record for the UI engine."""
    name: str
    start: time
    end: time


def _parse_time_like(value) -> Optional[time]:
    """Accepts datetime.time, 'HH:MM', 'HH:MM:SS', or None; returns datetime.time or None."""
    if value is None:
        return None
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        return value.time()
    if isinstance(value, str):
        s = value.strip()
        for fmt in ("%H:%M:%S", "%H:%M"):
            try:
                return datetime.strptime(s, fmt).time()
            except ValueError:
                continue
    return None


def _first_attr(obj, candidates: Iterable[str]):
    for name in candidates:
        if hasattr(obj, name):
            return getattr(obj, name)
    raise AttributeError(f"Expected one of attributes {candidates} on {type(obj).__name__}")


def _maybe_attr(obj, candidates: Iterable[str]):
    for name in candidates:
        if hasattr(obj, name):
            return getattr(obj, name)
    return None


def load_hours_from_db(use_assembly: bool) -> List[HourRecord]:
    """
    Loads Model.Hour objects from the database and normalizes them into HourRecord list.
    It attempts to be forgiving about attribute naming.
    """
    # Try to construct a session using common patterns in this project
    session = None
    try:
        # Preferred helper
        from Persistance import get_session  # type: ignore
        session = get_session()
    except Exception:
        try:
            # Common SQLAlchemy naming
            from Persistance import SessionLocal  # type: ignore
            session = SessionLocal()
        except Exception:
            try:
                # Another possible name
                from Persistance import Session  # type: ignore
                session = Session()
            except Exception as exc:
                raise RuntimeError("Could not establish a DB session from Persistance.") from exc

    try:
        from Model.Hour import Hour  # type: ignore
    except Exception as exc:
        raise RuntimeError("Model.Hour could not be imported. Check your project structure.") from exc

    try:
        # Basic all() query
        hours = session.query(Hour).all()  # type: ignore[attr-defined]
    except Exception as exc:
        raise RuntimeError("Failed to query Model.Hour objects. Check your ORM setup.") from exc
    finally:
        try:
            session.close()
        except Exception:
            pass

    normalized: List[HourRecord] = []
    # Candidate attribute names for standard and assembly schedules
    name_candidates = ("name", "title", "hour_name")
    std_start_candidates = ("start_time", "start", "startTime", "standard_start_time")
    std_end_candidates = ("end_time", "end", "endTime", "standard_end_time")
    asm_start_candidates = ("assembly_start_time", "assembly_start", "assemblyStart", "assemblyStartTime")
    asm_end_candidates = ("assembly_end_time", "assembly_end", "assemblyEnd", "assemblyEndTime")

    for h in hours:
        # Name
        try:
            raw_name = _first_attr(h, name_candidates)
        except AttributeError:
            raw_name = str(h)
        name_str = str(raw_name)

        # Times
        if use_assembly:
            start_raw = _maybe_attr(h, asm_start_candidates)
            end_raw = _maybe_attr(h, asm_end_candidates)
            # If assembly fields are missing, fall back to standard
            if start_raw is None or end_raw is None:
                start_raw = _maybe_attr(h, std_start_candidates)
                end_raw = _maybe_attr(h, std_end_candidates)
        else:
            start_raw = _maybe_attr(h, std_start_candidates)
            end_raw = _maybe_attr(h, std_end_candidates)

        start_t = _parse_time_like(start_raw)
        end_t = _parse_time_like(end_raw)

        if not start_t or not end_t:
            # Skip malformed rows
            continue

        normalized.append(HourRecord(name=name_str, start=start_t, end=end_t))

    # Sort by start time
    normalized.sort(key=lambda r: r.start)
    return normalized


# --------- Time engine ---------
@dataclass
class CurrentState:
    phase: str  # "daily_briefing", "in_hour", "between_hours", "cleanup
    label: str
    remaining: int  # seconds
    cleanup_active: bool
    hour_index: Optional[int]  # current hour index when in hour-phase


def _dt_on(day: date, t: time) -> datetime:
    return datetime.combine(day, t)


def compute_state(
    clock: datetime,
    hours: List[HourRecord],
    daily_briefing_min: int,
    cleanup_min: int,
) -> CurrentState:
    if not hours:
        return CurrentState(
            phase="between_hours",
            label="No hours found",
            remaining=0,
            cleanup_active=False,
            hour_index=None,
        )

    today = clock.date()
    # Build today's schedule
    spans: List[Tuple[datetime, datetime, str]] = []  # (start_dt, end_dt, name)
    for h in hours:
        start_dt = _dt_on(today, h.start)
        end_dt = _dt_on(today, h.end)
        # Support overnight wrap if needed (end before start)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)
        spans.append((start_dt, end_dt, h.name))

    # Find current or next span
    current_idx: Optional[int] = None
    for idx, (a, b, _) in enumerate(spans):
        if a <= clock < b:
            current_idx = idx
            break

    if current_idx is not None:
        a, b, nm = spans[current_idx]
        # Daily briefing phase for the first X minutes of the hour
        mb_end = a + timedelta(minutes=max(0, daily_briefing_min))
        if clock < mb_end:
            remaining = int((mb_end - clock).total_seconds())
            phase = "daily_briefing"
            label = "Daily Briefing"
            cleanup_active = False
        # Otherwise normal in-hour countdown
        else:
            remaining = int((b - clock).total_seconds())
            phase = "in_hour"
            label = nm
            cleanup_active = remaining <= max(0, cleanup_min) * 60
    else:
        # Between hours: countdown until the next hour's start
        # If after last span, next is next day's first span
        next_span_idx = None
        min_dt = None
        for idx, (a, _, _) in enumerate(spans):
            if clock < a and (min_dt is None or a < min_dt):
                min_dt = a
                next_span_idx = idx
        if next_span_idx is None:
            # Next day's first span
            a, _, nm = spans[0]
            a_next = a + timedelta(days=1)
            remaining = int((a_next - clock).total_seconds())
            phase = "between_hours"
            label = f"Next: {nm}"
            cleanup_active = False
        else:
            a, _, nm = spans[next_span_idx]
            remaining = int((a - clock).total_seconds())
            phase = "between_hours"
            label = f"Next: {nm}"
            cleanup_active = False

    # --- Inside compute_state(), right before returning the state ---
    state = CurrentState(
        phase=phase,
        label=label,
        remaining=remaining,
        cleanup_active=cleanup_active,
        hour_index=current_idx,
    )

    # Normalize: represent cleanup as a proper phase for consistent parsing
    state = _normalize_phase_cleanup(state)
    return state


def format_hms(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# --------- UI ---------
class StartupDialog(tb.Toplevel):
    def __init__(self, master, *, theme: str):
        super().__init__(master)
        self.title("Hour Manager - Start")
        self.resizable(False, False)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

        self.result = None  # tuple: (is_sub_day, use_assembly, daily_briefing_min, cleanup_min)

        frm = tb.Frame(self, padding=20)
        frm.grid(row=0, column=0, sticky=NSEW)

        self.var_sub = tk.BooleanVar(value=False)
        self.var_assembly = tk.BooleanVar(value=False)
        self.var_mb = tk.StringVar(value="5")
        self.var_cleanup = tk.StringVar(value="5")

        # Validation for numeric-only entries
        vcmd = (self.register(self._validate_int), "%P")

        row = 0
        tb.Checkbutton(frm, text="Sub Day", variable=self.var_sub, bootstyle="round-toggle").grid(
            row=row, column=0, columnspan=2, sticky=W, pady=(0, 10)
        )
        row += 1
        tb.Checkbutton(
            frm, text="Assembly Schedule", variable=self.var_assembly, bootstyle="round-toggle"
        ).grid(row=row, column=0, columnspan=2, sticky=W, pady=(0, 10))
        row += 1

        tb.Label(frm, text="Daily Briefing Time (minutes):").grid(row=row, column=0, sticky=E, padx=(0, 8))
        tb.Entry(frm, textvariable=self.var_mb, validate="key", validatecommand=vcmd, width=10).grid(
            row=row, column=1, sticky=W
        )
        row += 1

        tb.Label(frm, text="Cleanup Time (minutes):").grid(row=row, column=0, sticky=E, padx=(0, 8), pady=(10, 0))
        tb.Entry(frm, textvariable=self.var_cleanup, validate="key", validatecommand=vcmd, width=10).grid(
            row=row, column=1, sticky=W, pady=(10, 0)
        )
        row += 1

        btns = tb.Frame(frm)
        btns.grid(row=row, column=0, columnspan=2, pady=(16, 0))
        tb.Button(btns, text="Start", bootstyle="success", command=self._on_ok).grid(row=0, column=0, padx=(0, 8))
        tb.Button(btns, text="Cancel", command=self._on_cancel).grid(row=0, column=1)

        self.columnconfigure(0, weight=1)
        frm.columnconfigure(0, weight=0)
        frm.columnconfigure(1, weight=1)

        # Center dialog on parent
        self.update_idletasks()
        self._center_on_parent(master)

    def _center_on_parent(self, parent):
        try:
            px = parent.winfo_rootx()
            py = parent.winfo_rooty()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
        except Exception:
            px = py = 100
            pw = ph = 400
        sw = self.winfo_width()
        sh = self.winfo_height()
        x = px + (pw - sw) // 2
        y = py + (ph - sh) // 2
        self.geometry(f"+{x}+{y}")

    def _validate_int(self, proposed: str) -> bool:
        if proposed == "":
            return True
        return proposed.isdigit()

    def _on_ok(self):
        mb = self.var_mb.get().strip() or "0"
        cu = self.var_cleanup.get().strip() or "0"
        try:
            mb_i = int(mb)
            cu_i = int(cu)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter whole numbers for times.")
            return
        self.result = (bool(self.var_sub.get()), bool(self.var_assembly.get()), mb_i, cu_i)
        self.grab_release()
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.grab_release()
        self.destroy()


class HourManagerApp(tb.Window):
    def __init__(self):
        theme = _resolve_theme()
        super().__init__(themename=theme)
        self.title("Hour Manager")
        self.geometry("520x260")
        self.minsize(420, 220)

        # State
        self.is_sub_day: bool = False
        self.use_assembly: bool = False
        self.daily_briefing_min: int = 5
        self.cleanup_min: int = 5
        self.hours: List[HourRecord] = []

        # Cleanup alert tracking
        self._alerted_for_hour_idx: Optional[int] = None

        # UI
        container = tb.Frame(self, padding=16)
        container.pack(fill="both", expand=True)

        # Label for current period
        self.lbl_period = tb.Label(
            container, text="—", anchor=CENTER, font=("-size", 20, "-weight", "bold")
        )
        self.lbl_period.pack(fill="x", pady=(8, 8))

        # Big countdown
        self.lbl_timer = tb.Label(
            container, text="00:00", anchor=CENTER, font=("-size", 48, "-weight", "bold")
        )
        self.lbl_timer.pack(fill="x", pady=(0, 8))

        # Subtle status line
        self.lbl_status = tb.Label(container, text="", anchor=CENTER, font=("-size", 10))
        self.lbl_status.pack(fill="x")

        # Start with the dialog
        self.after(50, self._show_startup_dialog)

        # Keyboard shortcuts for testing time override (optional)
        self.bind("<F6>", self._toggle_test_time_now)
        self.bind("<F7>", self._advance_5_min)
        self.bind("<F8>", self._clear_test_time)

    # ---- Test time helpers via shortcuts (optional) ----
    def _toggle_test_time_now(self, _evt=None):
        if _test_time is None:
            set_test_time(get_now())
            messagebox.showinfo("Test Time", "Test time enabled (frozen to current). Press F8 to clear or F7 to advance.")
        else:
            clear_test_time()
            messagebox.showinfo("Test Time", "Test time disabled. Using real clock.")

    def _advance_5_min(self, _evt=None):
        if _test_time is None:
            messagebox.showinfo("Test Time", "Enable test time first with F6.")
            return
        with _test_time_lock:
            assert _test_time is not None
            set_test_time(_test_time + timedelta(minutes=5))

    def _clear_test_time(self, _evt=None):
        clear_test_time()
        messagebox.showinfo("Test Time", "Test time cleared. Using real clock.")

    # ---- Startup and main loop ----
    def _show_startup_dialog(self):
        dlg = StartupDialog(self, theme=self.style.theme.name)
        self.wait_window(dlg)
        if dlg.result is None:
            self.destroy()
            return

        self.is_sub_day, self.use_assembly, self.daily_briefing_min, self.cleanup_min = dlg.result

        # Load hours
        try:
            self.hours = load_hours_from_db(self.use_assembly)
        except Exception as exc:
            messagebox.showwarning(
                "Hour Load Error",
                f"Could not load hours from the database.\n\n{exc}\n\nContinuing with an empty schedule.",
            )
            self.hours = []

        self._alerted_for_hour_idx = None
        self._tick()  # start update loop

    def _tick(self):
        clk = get_now()
        state = compute_state(clk, self.hours, self.daily_briefing_min, self.cleanup_min)

        # Label prefix for Sub Day
        prefix = "[Sub Day] " if self.is_sub_day else ""

        # Update labels
        self.lbl_period.config(text=prefix + state.label)

        # Timer formatting and color
        #self.lbl_timer.config(text=format_hms(state.remaining))
        self.lbl_timer.config(text=format_countdown_for_display(state.remaining, phase_name=state.phase))
        if state.phase == "cleanup" and state.cleanup_active:
            self.lbl_timer.configure(bootstyle="danger")
            # Play the sound exactly once per hour when threshold is crossed
            if state.hour_index is not None and self._alerted_for_hour_idx != state.hour_index:
                self._alerted_for_hour_idx = state.hour_index
                beep_once()
        else:
            # Reset style when not in cleanup
            self.lbl_timer.configure(bootstyle="secondary")

        # Status line: real or test time
        tm_src = "TEST" if _test_time is not None else "REAL"
        #self.lbl_status.config(text=f"Time source: {tm_src}  •  Now: {clk.strftime('%I:%M:%S %p').lstrip('0')}")
        self.lbl_status.config(text=f"Now: {clk.strftime('%I:%M %p').lstrip('0')}")

        # When we transition into a new hour, reset cleanup alert so it can fire again later
        if state.phase != "cleanup":
           # print(f"Resetting cleanup alert for hour {state.phase}")
            self._alerted_for_hour_idx = None

        # Schedule next tick
        self.after(250, self._tick)


def main():
    app = HourManagerApp()
    app.mainloop()


if __name__ == "__main__":
    # Optional: allow a quick test time injection from CLI
    # Example: python HourManager.py 2025-09-01T08:00:00
    if len(sys.argv) > 1:
        try:
            set_test_time(datetime.fromisoformat(sys.argv[1]))
        except Exception:
            pass
    else:
        set_test_time(datetime.combine(date.today(), time(10, 30, 45))) # TODO: remove testing value
        pass # No test time now

    main()