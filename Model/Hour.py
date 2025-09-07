# Model/Hour.py
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, time

from sqlalchemy import Column, Integer, DateTime, ForeignKey, Float, String, Time
from sqlalchemy.orm import relationship, mapped_column, Mapped

from Persistance import Base, session

if TYPE_CHECKING:
    from .Student import Student
    from .Project import Project


class Hour(Base):
    """Represents a time period (hour) in the classroom schedule."""

    __tablename__ = 'hours'

    # Constants
    MAX_NAME_LENGTH = 255
    DEFAULT_NEXT_DAY_START = datetime(2025, 8, 14, 7, 46, 55)

    # Database columns
    hourID: Mapped[int] = mapped_column(primary_key=True)
    _name: Mapped[str] = mapped_column(String(MAX_NAME_LENGTH))
    _start_time: Mapped[time] = mapped_column(Time)
    _end_time: Mapped[time] = mapped_column(Time)
    _assembly_start_time: Mapped[time] = mapped_column(Time)
    _assembly_end_time: Mapped[time] = mapped_column(Time)
    _start_date: Mapped[datetime] = mapped_column(DateTime)
    _end_date: Mapped[datetime] = mapped_column(DateTime)

    # Relationships
    students_in_hour: Mapped[List["Student"]] = relationship(back_populates="_student_hour")

    #students: Mapped[List["Student"]] = relationship(back_populates="student_hour")
    #teams: Mapped[List["Team"]] = relationship(back_populates="team_hour")
    #checkins: Mapped[List["Checkin"]] = relationship(back_populates="checkin_hour")
    #bathroom_visits: Mapped[List["BathroomVisit"]] = relationship(back_populates="bathroom_visit_hour")

    def __init__(self, name: str, start_time: time, end_time: time,
                 start_date: datetime, end_date: datetime,
                 assembly_start_time: time = None, assembly_end_time: time = None):
        """Initialize a new Hour instance with validation."""
        """if not name or len(name) > self.MAX_NAME_LENGTH:
            raise ValueError(f"Name must be between 1 and {self.MAX_NAME_LENGTH} characters")
        if end_time <= start_time:
            raise ValueError("End time must be after start time")
        if end_date <= start_date:
            raise ValueError(f"End date ({end_date}) must be after start date ({start_date})")
        if assembly_start_time and assembly_end_time and assembly_end_time <= assembly_start_time:
            raise ValueError("Assembly end time must be after assembly start time")"""

        self._name = name
        self._start_time = start_time
        self._end_time = end_time
        self._start_date = start_date
        self._end_date = end_date
        self._assembly_start_time = assembly_start_time
        self._assembly_end_time = assembly_end_time

    @property
    def name(self) -> str:
        """Get the hour name."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Set the hour name."""
        if not value or len(value) > self.MAX_NAME_LENGTH:
            raise ValueError(f"Name must be between 1 and {self.MAX_NAME_LENGTH} characters")
        self._name = value

    @property
    def start_time(self) -> time:
        """Get the start time."""
        return self._start_time


    @start_time.setter
    def start_time(self, value: time) -> None:
        """Set the start time."""
        if value >= self._end_time:
            raise ValueError("Start time must be before end time")
        self._start_time = value

    @property
    def end_time(self) -> time:
        """Get the end time."""
        return self._end_time

    @end_time.setter
    def end_time(self, value: time) -> None:
        """Set the end time."""
        if value <= self._start_time:
            raise ValueError("End time must be after start time")
        self._end_time = value

    @property
    def start_date(self) -> datetime:
        """Get the start date."""
        return self._start_date

    @start_date.setter
    def start_date(self, value: datetime) -> None:
        """Set the start date."""
        if value >= self._end_date:
            raise ValueError("Start date must be before end date")
        self._start_date = value

    @property
    def end_date(self) -> datetime:
        """Get the end date."""
        return self._end_date

    @end_date.setter
    def end_date(self, value: datetime) -> None:
        """Set the end date."""
        if value <= self._start_date:
            raise ValueError(f"End date ({value}) must be after start date ({self._start_date})")
        self._end_date = value

    @property
    def assembly_start_time(self) -> time:
        """Get the assembly start time."""
        return self._assembly_start_time

    @assembly_start_time.setter
    def assembly_start_time(self, value: time) -> None:
        """Set the assembly start time."""
        if value and self._assembly_end_time and value >= self._assembly_end_time:
            raise ValueError("Assembly start time must be before assembly end time")
        self._assembly_start_time = value

    @property
    def assembly_end_time(self) -> time:
        """Get the assembly end time."""
        return self._assembly_end_time

    @assembly_end_time.setter
    def assembly_end_time(self, value: time) -> None:
        """Set the assembly end time."""
        if value and self._assembly_start_time and value <= self._assembly_start_time:
            raise ValueError("Assembly end time must be after assembly start time")
        self._assembly_end_time = value

    def save(self):
        """Add or update the hour in the database."""
        if not self.hourID:
            session.add(self)
        session.commit()

    @staticmethod
    def add(self):
        """Add a new hour to the database."""
        session.add(self)
        session.commit()

    @staticmethod
    def update(self):
        """Update an existing hour in the database."""
        session.commit()

    @staticmethod
    def get_by_name(hour_name: str) :
        """Retrieve an hour by its name."""
        return session.query(Hour).filter_by(name=hour_name).first()

    @staticmethod
    def get_by_id(hour_ID: int) -> Optional['Hour']:
        """Retrieve an hour by its ID.

        Args:
            hour_ID (int): The ID of the hour to retrieve.

        Returns:
            Optional[Hour]: The hour with the specified ID, or None if not found.
        """
        if not isinstance(hour_ID, int) or hour_ID < 1:
            raise ValueError("Hour ID must be a positive integer")
        return session.query(Hour).filter_by(hourID=hour_ID).first()

    @staticmethod
    def get_by_time(requested_time: time) :
        """Retrieve the current hour based on the requested time."""
        return session.query(Hour).filter(
            Hour._start_time <= requested_time,
            Hour._end_time >= requested_time
        ).first()

    @staticmethod
    def get_next_by_time(requested_time: time) :
        """Retrieve the next hour based on the requested time."""
        next_hour = session.query(Hour).filter(Hour._start_time > requested_time).first()
        if next_hour is not None:
            return next_hour
        return session.query(Hour).filter(
            Hour._start_time > Hour.DEFAULT_NEXT_DAY_START
        ).first()

    @staticmethod
    def get_all_order_by_start_time():
        """Retrieve all hours ordered by start time."""
        return session.query(Hour).order_by(Hour._start_time).all()
