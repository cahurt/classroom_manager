from datetime import datetime
from typing import List, Optional
from sqlalchemy import Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.exc import SQLAlchemyError
from Persistance import Base, session


class Unit(Base):
    __tablename__ = 'units'

    unit_ID: Mapped[int] = mapped_column(primary_key=True)
    unit_sequence: Mapped[int] = mapped_column(Integer, unique=True)
    unit_name: Mapped[str] = mapped_column(String(255))
    unit_description: Mapped[str] = mapped_column(Text)
    unit_opening_date: Mapped[datetime] = mapped_column(DateTime)
    unit_end_date: Mapped[datetime] = mapped_column(DateTime)
    unit_closing_date: Mapped[datetime] = mapped_column(DateTime)

    def __init__(self, unit_name: str, unit_sequence: int,
                 unit_opening_date: datetime, unit_closing_date: datetime,
                 unit_end_date: datetime, unit_description: str):
        self.unit_name = unit_name
        self.unit_sequence = unit_sequence
        self.unit_opening_date = unit_opening_date
        self.unit_closing_date = unit_closing_date
        self.unit_end_date = unit_end_date
        self.unit_description = unit_description

        if not self._validate_dates():
            raise ValueError("Invalid date sequence - unit cannot close or end before it opens: opens:f'{self.unit_opening_date}', closes: '{self.unit_closing_date}', ends: '{self.unit_end_date}'")

    def _validate_dates(self) -> bool:
        return (self.unit_opening_date < self.unit_end_date <= self.unit_closing_date)


    def add_new_unit(self, session) -> None:
        #"""Add unit to database#"""
        try:
            # to generate a nicer error message we do a little pre-checking
            existing_unit = session.query(Unit).filter_by(unit_sequence=self.unit_sequence).first()
            if existing_unit:
                raise ValueError(f"Unit with sequence number {self.unit_sequence} already exists")
            if not self._validate_dates():
                raise ValueError("Invalid date sequence - unit cannot close or end before it opens.")
            session.add(self)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise

    def update_unit(self, session) -> None:
        ###"""Update unit in database#"""
        try:
            session.merge(self)
            session.commit()
        except SQLAlchemyError as e:
            print(e)
            session.rollback()
            raise

    def delete_unit(self, session) -> None:
        #"""Delete unit from database#"""
        try:
            session.delete(self)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            raise

    @classmethod
    def create_from_dict(cls, data_dict: dict) -> 'Unit':
        # """Create a Unit instance from a dictionary of attributes#"""
        required_fields = ['unit_name', 'unit_sequence', 'unit_opening_date',
                           'unit_closing_date', 'unit_end_date', 'unit_description']

        if not all(field in data_dict for field in required_fields):
            raise ValueError("Missing required fields")

        return cls(**data_dict)

    @classmethod
    def get_all_units_by_sequence(cls) -> List['Unit']:
        # """Retrieve all units ordered by sequence#"""
        return session.query(cls).order_by(cls.unit_sequence).all()

    @classmethod
    def get_unit_by_sequence(cls, sequence) -> 'Unit':
        # """Retrieve unit from database by sequence number#"""
        return session.query(cls).filter_by(unit_sequence=sequence).first()

    @classmethod
    def get_unit_by_ID(cls, ID) -> 'Unit':
        # """Retrieve unit from database by sequence number#"""
        return session.query(cls).filter_by(unit_ID=ID).first()
