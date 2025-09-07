# Model/Unit.py
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Text

from Persistance import Base, session

if TYPE_CHECKING:
    from .Objective import Objective
    from .Project import Project




class Unit(Base):
    """Represents a teaching unit with sequence, dates and description."""

    __tablename__ = 'units'

    # Constants for validation
    MAX_STRING_LENGTH = 255
    MIN_SEQUENCE = 0
    MAX_SEQUENCE = 30

    # Database columns
    unit_ID: Mapped[int] = mapped_column('unit_ID', primary_key=True)
    _sequence: Mapped[int] = mapped_column('unit_sequence', Integer, unique=True)
    _name: Mapped[str] = mapped_column('unit_name', String(MAX_STRING_LENGTH))
    _description: Mapped[str] = mapped_column('unit_description', Text)
    _opening_date: Mapped[datetime] = mapped_column('unit_opening_date', DateTime)
    _end_date: Mapped[datetime] = mapped_column('unit_end_date', DateTime)
    _closing_date: Mapped[datetime] = mapped_column('unit_closing_date', DateTime)

    # Relationships
    _projects_in_unit: Mapped[List["Project"]] = relationship(back_populates="_unit")

    def __init__(self, name: str, sequence: int,
                 opening_date: datetime, closing_date: datetime,
                 end_date: datetime, description: str = "", ignore_validation=False) -> None:
        """Initialize a new unit.
        
        Args:
            name: The name of the unit
            sequence: The sequence number of the unit
            opening_date: Date when unit opens
            closing_date: Date when unit closes
            end_date: Date when unit ends
            description: Detailed description of the unit
        """
        """Initialize a new unit."""
        # First set the basic attributes
        self.name = name
        self.sequence = sequence
        self.description = description

        # Set dates directly first
        self._opening_date = opening_date
        self._closing_date = closing_date
        self._end_date = end_date

        # Now validate all dates
        if not self.are_dates_valid() and not ignore_validation:
            raise ValueError(
                "Invalid date sequence: opening_date must be before end_date, which must be before or equal to closing_date")

        if not self.validate_unique_sequence() and not ignore_validation:
            raise ValueError(f"Unit: {self.name} with sequence number {self.sequence} already exists from init")


    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or len(value) > self.MAX_STRING_LENGTH:
            raise ValueError(f"Name must be between 1 and {self.MAX_STRING_LENGTH} characters")
        self._name = value

    @property
    def sequence(self) -> int:
        return self._sequence

    @sequence.setter
    def sequence(self, value: int) -> None:
        sequence_value = int(value)
        if not self.MIN_SEQUENCE <= sequence_value <= self.MAX_SEQUENCE:
            raise ValueError(f"Sequence must be between {self.MIN_SEQUENCE} and {self.MAX_SEQUENCE}")
        self._sequence = sequence_value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value or ""

    @property
    def opening_date(self) -> datetime:
        return self._opening_date

    @opening_date.setter
    def opening_date(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise ValueError("Opening date must be a datetime object")
        self._opening_date = value

    @property
    def end_date(self) -> datetime:
        return self._end_date

    @end_date.setter
    def end_date(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise ValueError("End date must be a datetime object")
        self._end_date = value

    @property
    def closing_date(self) -> datetime:
        return self._closing_date

    @closing_date.setter
    def closing_date(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise ValueError("Closing date must be a datetime object")
        self._closing_date = value

    @property
    def projects_in_unit(self) -> List["Project"]:
        return self._projects_in_unit

    @projects_in_unit.setter
    def projects_in_unit(self, value: List["Project"]) -> None:
        self._projects_in_unit = value

    def are_dates_valid(self) -> bool:
        """Validate that dates are in correct sequence."""
        return (self.opening_date < self.end_date <= self.closing_date)

    def validate_unique_sequence(self) -> bool:
        """Validate that the unit sequence is unique."""
        existing_unit = session.query(Unit).filter_by(_sequence=self.sequence).first()

        if existing_unit is not None and existing_unit.unit_ID != self.unit_ID:
            return False

        return True

    def save(self) -> None:
        """Save or update the unit in the database."""
        try:
            if not self.validate_unique_sequence():
                raise ValueError(f"Unit with sequence number {self.sequence} already exists from save")
            if not self.are_dates_valid():
                raise ValueError("End date must be after opening date and before or equal to closing date")

            if not self.exists(self.unit_ID):
                print("Unit does not exist, adding")
                session.add(self)

            session.commit()

        except Exception as e:
            session.rollback()
            raise

    def delete(self) -> None:
        """Delete the unit from the database."""
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise

    @classmethod
    def exists(self, unit_ID: int) -> bool:
        """Check if a unit with the given ID exists in the database."""
        return session.query(Unit).filter_by(unit_ID=unit_ID).first() is not None

    @classmethod
    def get_by_id(cls, unit_ID: int) -> Optional['Unit']:
        """Retrieve a unit by its ID."""
        return session.query(cls).filter_by(unit_ID=unit_ID).first()

    @classmethod
    def get_by_sequence(cls, sequence: int) -> Optional['Unit']:
        """Retrieve a unit by its sequence number."""
        return session.query(cls).filter_by(_sequence=sequence).first()

    @classmethod
    def get_all_order_by_sequence(cls) -> List['Unit']:
        """Retrieve all units ordered by sequence."""
        return session.query(cls).order_by(cls._sequence).all()
