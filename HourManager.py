import datetime
import tkinter as tk
from tkinter import ttk

import ttkbootstrap as tb
from sqlalchemy.orm import sessionmaker

import Persistance
from Model.Hour import Hour as HourModel

# Test time configuration
USE_TEST_TIME = True
TEST_TIME = datetime.datetime(2025, 8, 22, 9, 40)  # 10:30 AM on August 22, 2025
TEST_TIME_ELAPSED = 0  # Track elapsed seconds in test mode


class DayOptionsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Today's Options")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.assembly_var = tk.BooleanVar(value=False)
        self.sub_var = tk.BooleanVar(value=False)
        self.result = None

        # UI
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Select options for today:").pack(anchor="w", pady=(0, 8))
        ttk.Checkbutton(frame, text="Assembly day", variable=self.assembly_var).pack(anchor="w")
        ttk.Checkbutton(frame, text="Sub day", variable=self.sub_var).pack(anchor="w", pady=(4, 0))

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", pady=(12, 0))
        ttk.Button(btn_frame, text="OK", command=self._on_ok).pack(side="right", padx=(8, 0))
        ttk.Button(btn_frame, text="Cancel", command=self._on_cancel).pack(side="right")

        self._center_over(parent)

    def _center_over(self, parent):
        self.update_idletasks()
        pw = parent.winfo_width()
        ph = parent.winfo_height()
        px = parent.winfo_rootx()
        py = parent.winfo_rooty()
        w = self.winfo_width()
        h = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _on_ok(self):
        self.result = (self.assembly_var.get(), self.sub_var.get())
        self.destroy()

    def _on_cancel(self):
        # Defaults if canceled
        self.result = (False, False)
        self.destroy()


class HourManager:
    def __init__(self):
        # DB setup
        Persistance.Base.metadata.create_all(Persistance.engine)
        self.SessionLocal = sessionmaker(bind=Persistance.engine)

        # UI setup
        self.root = tb.Window(themename="superhero")
        self.setup_window()

        # Ask for today's options before building rest of UI
        self.assembly_day, self.sub_day = self._prompt_day_options()

        # Main UI: status + big timer
        self.status_label = tb.Label(
            self.root,
            text="",
            font=("Helvetica", 16),
            bootstyle="secondary"
        )
        self.status_label.pack(pady=(20, 4))

        self.timer_label = tb.Label(
            self.root,
            text="--:--",
            font=("Helvetica", 72, "bold"),
            bootstyle="inverse-primary"
        )
        self.timer_label.pack(pady=10)

        # Load hours once; they rarely change during a session
        self.hours = self._load_hours()

        # Start updates
        self.update_timer()

    def setup_window(self):
        self.root.title("Foundations of Manufacturing 2025-2026")
        self.root.geometry("600x300")

    def _prompt_day_options(self):
        # Build a tiny invisible center reference to position dialog nicely
        self.root.update_idletasks()
        dialog = DayOptionsDialog(self.root)
        self.root.wait_window(dialog)
        assembly_day, sub_day = dialog.result
        # Optional: reflect options in title for clarity
        title_suffix = []
        if assembly_day:
            title_suffix.append("Assembly")
        if sub_day:
            title_suffix.append("Sub")
        if title_suffix:
            self.root.title(f"{self.root.title()} - {' & '.join(title_suffix)} Day")
        return assembly_day, sub_day

    def _load_hours(self):
        session = self.SessionLocal()
        try:
            hours = session.query(HourModel).all()
            return hours
        finally:
            session.close()

    def _to_time(self, value):
        # Accept datetime.time or string like "8:55", "1:17", "1:17 PM"
        if isinstance(value, datetime.time):
            return value
        if isinstance(value, str):
            s = value.strip().lower()
            # Try with explicit AM/PM
            try:
                if "am" in s or "pm" in s:
                    return datetime.datetime.strptime(s.replace(".", ""), "%I:%M %p").time()
            except Exception:
                pass
            # Try 24-hour format
            try:
                return datetime.datetime.strptime(s, "%H:%M").time()
            except Exception:
                pass
            # Heuristic: school afternoon hours 1..6 => PM
            try:
                parts = s.split(":")
                h = int(parts[0])
                m = int(parts[1])
                if 1 <= h <= 6:
                    h += 12
                return datetime.time(hour=h, minute=m)
            except Exception:
                return None
        return None

    def _to_date(self, value):
        # Normalize to a pure date for consistent comparisons
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        if isinstance(value, str):
            for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d"):
                try:
                    return datetime.datetime.strptime(value.strip(), fmt).date()
                except Exception:
                    continue
        return None

    def _today_intervals(self, today):
        # Build list of (start_dt, end_dt, hour_name) for today based on options.
        intervals = []
        use_assembly = self.assembly_day

        for h in self.hours:
            # Date gating
            start_date = self._to_date(getattr(h, "start_date", None))
            end_date = self._to_date(getattr(h, "end_date", None))
            if start_date and today < start_date:
                continue
            if end_date and today > end_date:
                continue

            # Times
            if use_assembly:
                st = self._to_time(getattr(h, "assembly_start_time", None)) or self._to_time(getattr(h, "start_time", None))
                et = self._to_time(getattr(h, "assembly_end_time", None)) or self._to_time(getattr(h, "end_time", None))
            else:
                st = self._to_time(getattr(h, "start_time", None))
                et = self._to_time(getattr(h, "end_time", None))

            if not st or not et:
                continue

            start_dt = datetime.datetime.combine(today, st)
            end_dt = datetime.datetime.combine(today, et)
            if end_dt <= start_dt:
                # Guard against invalid or overnight ranges; skip invalid entries
                continue

            hour_name = getattr(h, "name", "Hour")
            intervals.append((start_dt, end_dt, hour_name))

        intervals.sort(key=lambda t: t[0])
        return intervals

    def update_timer(self):
        if USE_TEST_TIME:
            global TEST_TIME_ELAPSED
            now = TEST_TIME + datetime.timedelta(seconds=TEST_TIME_ELAPSED)
            TEST_TIME_ELAPSED += 1
        else:
            now = datetime.datetime.now()
        today = now.date()
        intervals = self._today_intervals(today)

        label_text = ""
        remaining = None

        # Determine if we are in an active hour
        current = next(((s, e, n) for (s, e, n) in intervals if s <= now <= e), None)
        if current:
            s, e, name = current
            remaining = e - now
            label_text = f"In {name} — time remaining"
        else:
            # Next upcoming hour today
            upcoming = next(((s, e, n) for (s, e, n) in intervals if s > now), None)
            if upcoming:
                s, e, name = upcoming
                remaining = s - now
                label_text = f"Until {name} starts"
            else:
                # No more hours today; find the first hour tomorrow (if within date range)
                tomorrow = today + datetime.timedelta(days=1)
                tomorrow_intervals = self._today_intervals(tomorrow)
                if tomorrow_intervals:
                    s, e, name = tomorrow_intervals[0]
                    remaining = s - now
                    label_text = f"No more today — until {name} starts"
                else:
                    # Nothing scheduled
                    self.status_label.config(text="No scheduled hours in range.")
                    self.timer_label.config(text="--:--")
                    self.root.after(1000, self.update_timer)
                    return

        # Format remaining as MM:SS or H:MM:SS if long
        total_seconds = max(0, int(remaining.total_seconds()))
        hours, rem = divmod(total_seconds, 3600)
        minutes, seconds = divmod(rem, 60)

        if hours > 0:
            time_str = f"{hours:d}:{minutes:02d}:{seconds:02d}"
        else:
            time_str = f"{minutes:02d}:{seconds:02d}"

        # Reflect options in status
        badges = []
        if self.assembly_day:
            badges.append("Assembly")
        if self.sub_day:
            badges.append("Sub")
        badge_str = f" [{' & '.join(badges)}]" if badges else ""

        self.status_label.config(text=f"{label_text}{badge_str}")

        # Change color to red if 5 minutes or less remaining during an hour
        if current and total_seconds <= 300:  # 5 minutes = 300 seconds
            self.timer_label.config(text=time_str, bootstyle="danger")
        else:
            self.timer_label.config(text=time_str, bootstyle="inverse-primary")

        # Schedule next tick
        self.root.after(1000, self.update_timer)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = HourManager()
    app.run()