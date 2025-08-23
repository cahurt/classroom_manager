# Python
import tkinter as tk

import ttkbootstrap as tb
import Persistance
from GUI_components.HourTab import HourTab
from GUI_components.ClassroomLocationsTab import ClassroomLocationsTab
from GUI_components.ObjectiveTab import ObjectiveTab
from GUI_components.UnitTab import UnitTab
from Model.AddDefaultObjects import AddDefaultObjects
from GUI_components.ProjectTab import ProjectTab
from Model.Hour import Hour
from sqlalchemy.orm import Session
import datetime
import time

USE_TEST_TIME = True  # Set to False to use real time
TEST_TIME = datetime.datetime.now().replace(hour=9, minute=35, second=45, microsecond=0)


class HourManager:
    def __init__(self, ...):
        self.is_assembly_day = False
        self.has_substitute = False
        Persistance.Base.metadata.create_all(Persistance.engine)
        self.root = tb.Window(themename="superhero")
        self.show_settings_dialog()
        self.setup_window()

        # Anchor test time to real time so it advances when testing
        self._use_test_time = USE_TEST_TIME
        if self._use_test_time:
            self._test_anchor_real = datetime.datetime.now()
            self._test_anchor_mock = TEST_TIME

        self.timer_label = None
        self.current_hour_label = None
        self.next_hour_label = None

        # Flashing state
        self.is_visible = True
        self.FLASH_INTERVAL = 300  # milliseconds
        self.NORMAL_COLOR = "white"
        self.WARNING_COLOR = "red"

        # Flash control state
        self._flash_job_id = None          # after() handle so we can cancel
        self._flashes_left = 0             # remaining toggles
        self._flash_active = False         # currently flashing?
        self._flash_latch_hour = None      # prevents re-triggering within the same hour

        self.setup_timer()

    def setup_window(self):
        self.root.title("Foundations of Manufacturing 2025-2026")
        self.root.geometry('1280x1024')

    def show_settings_dialog(self):
        dialog = tb.Toplevel(self.root)
        dialog.title("Daily Settings")
        dialog.geometry("300x150")

        assembly_var = tk.BooleanVar(master=self.root)
        substitute_var = tk.BooleanVar(master=self.root)

        tb.Checkbutton(dialog, text="Assembly Day", variable=assembly_var).pack(pady=10)
        tb.Checkbutton(dialog, text="Substitute Teacher", variable=substitute_var).pack(pady=10)

        def save_settings():
            self.is_assembly_day = assembly_var.get()
            self.has_substitute = substitute_var.get()
            dialog.destroy()

        tb.Button(dialog, text="OK", command=save_settings).pack(pady=20)

        dialog.transient(self.root)
        dialog.grab_set()
        self.root.wait_window(dialog)

    def setup_timer(self):
        self.current_hour_label = tb.Label(self.root, text="", font=("Helvetica", 24))
        self.current_hour_label.pack(pady=10)

        self.next_hour_label = tb.Label(self.root, text="", font=("Helvetica", 20))
        self.next_hour_label.pack(pady=5)

        self.timer_label = tb.Label(self.root, text="", font=("Helvetica", 24))
        self.timer_label.pack(pady=10)

        self.update_timer()

    def _now(self) -> datetime.datetime:
        """Return current time (mocked when test mode is on)."""
        if self._use_test_time:
            elapsed = datetime.datetime.now() - self._test_anchor_real
            return self._test_anchor_mock + elapsed
        return datetime.datetime.now()

    # --- Flash control helpers -------------------------------------------------
    def start_flash(self, times: int = 10) -> None:
        """Start a bounded flash sequence (exactly `times` on/off toggles)."""
        # Cancel any previous scheduled toggle
        if self._flash_job_id is not None:
            try:
                self.root.after_cancel(self._flash_job_id)
            except Exception:
                pass
            self._flash_job_id = None

        # Each toggle flips color; times is the number of flips (on/off pairs are 2 toggles)
        self._flashes_left = max(0, times)
        self._flash_active = self._flashes_left > 0

        # Ensure we start from NORMAL_COLOR so the first toggle is WARNING
        try:
            self.timer_label.config(fg=self.NORMAL_COLOR)
        except Exception:
            pass

        if self._flash_active:
            self._schedule_next_flash_toggle()

    def _schedule_next_flash_toggle(self) -> None:
        if self._flashes_left <= 0:
            self._stop_flash()
            return

        # Toggle color
        try:
            current = self.timer_label.cget("fg")
            next_color = self.WARNING_COLOR if current == self.NORMAL_COLOR else self.NORMAL_COLOR
            self.timer_label.config(fg=next_color)
        except Exception:
            # Fail-safe: stop flashing if widget is unavailable
            self._stop_flash()
            return

        self._flashes_left -= 1

        # Schedule next toggle
        try:
            self._flash_job_id = self.root.after(self.FLASH_INTERVAL, self._schedule_next_flash_toggle)
        except Exception:
            self._stop_flash()

    def _stop_flash(self) -> None:
        """Stop flashing and restore normal color."""
        if self._flash_job_id is not None:
            try:
                self.root.after_cancel(self._flash_job_id)
            except Exception:
                pass
            self._flash_job_id = None

        try:
            self.timer_label.config(fg=self.NORMAL_COLOR)
        except Exception:
            pass

        self._flashes_left = 0
        self._flash_active = False

    # --- Existing timer update -------------------------------------------------
    def update_timer(self):
        now = self._now()

        # Default update interval (ms). May be reduced when flashing.
        next_interval_ms = 1000

        with Session(Persistance.engine) as session:
            # Pick the correct columns based on assembly day
            start_col = Hour._assembly_start_time if self.is_assembly_day else Hour._start_time
            end_col = Hour._assembly_end_time if self.is_assembly_day else Hour._end_time

            # Current hour (if any)
            current_hour = (
                session.query(Hour)
                .filter(start_col <= now.time(), end_col > now.time())
                .order_by(start_col)
                .first()
            )

            # Next hour (wrap to first if none later today)
            next_hour = (
                session.query(Hour)
                .filter(start_col > now.time())
                .order_by(start_col)
                .first()
            )
            if not next_hour:
                next_hour = session.query(Hour).order_by(start_col).first()

            # If no hours are configured at all
            if not current_hour and not next_hour:
                self.current_hour_label.config(text="Current Hour: --")
                self.next_hour_label.config(text="Next Hour: --")
                self.timer_label.config(text="Time remaining: --:--:--")
                self.timer_label.config(foreground=self.NORMAL_COLOR)
                self.root.after(next_interval_ms, self.update_timer)
                return

            # Update Current Hour label and compute the target time for the countdown
            if current_hour:
                self.current_hour_label.config(text=f"Current Hour: {current_hour.name}")
                end_time = current_hour.assembly_end_time if self.is_assembly_day else current_hour.end_time
                next_time = datetime.datetime.combine(now.date(), end_time)
            else:
                self.current_hour_label.config(text="Current Hour: --")
                # No active hour; countdown to the next hour's start
                start_time = next_hour.assembly_start_time if self.is_assembly_day else next_hour.start_time
                next_time = datetime.datetime.combine(now.date(), start_time)
                # If we wrapped to the first hour but its start_time is earlier than now,
                # the event is tomorrow.
                if start_time <= now.time():
                    next_time += datetime.timedelta(days=1)

            # Update Next Hour label (if any)
            if next_hour:
                self.next_hour_label.config(text=f"Next Hour: {next_hour.name}")
            else:
                self.next_hour_label.config(text="Next Hour: --")

        # Update countdown
        time_diff = next_time - now
        total_seconds = max(0, int(time_diff.total_seconds()))
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        self.timer_label.config(text=f"Time remaining: {hours:02d}:{minutes:02d}:{seconds:02d}")

        # Latch key to ensure we trigger flashing at most once per hour
        hour_key = (now.year, now.month, now.day, now.hour)

        # Choose your trigger condition. Example:
        # Start flashing in the last 10 seconds of the hour, once per hour.
        seconds_into_hour = now.minute * 60 + now.second
        seconds_left_in_hour = 3600 - seconds_into_hour
        should_start_flash = seconds_left_in_hour <= 10

        if should_start_flash and self._flash_latch_hour != hour_key and not self._flash_active:
            self._flash_latch_hour = hour_key
            # Exactly 10 toggles
            self.start_flash(times=10)

        # If you have another trigger condition elsewhere, ensure it uses:
        #   if not self._flash_active and self._flash_latch_hour != hour_key:
        #       self._flash_latch_hour = hour_key
        #       self.start_flash(times=10)

        # Flash during the last 5 minutes of an active hour
        # if current_hour and hours == 0 and minutes < 5:
        #     # Toggle color to create a flash effect and speed up the update tempo.
        #     self.timer_label.config(foreground=self.WARNING_COLOR if self.is_visible else self.NORMAL_COLOR)
        #     self.is_visible = not self.is_visible
        #     next_interval_ms = min(next_interval_ms, self.FLASH_INTERVAL)
        # else:
        #     # Reset to normal display outside flashing window
        #     self.timer_label.config(foreground=self.NORMAL_COLOR)
        #     self.is_visible = True

        self.root.after(next_interval_ms, self.update_timer)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = HourManager()
    app.run()