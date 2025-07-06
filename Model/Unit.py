from datetime import datetime
from typing import List
from Persistance import session, Base
from sqlalchemy import Integer, DateTime, String, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import desc
#from Model import Project

class Unit(Base):
    __tablename__ = 'units'

    # Unique attributes
    unit_ID: Mapped[int] = mapped_column(primary_key=True)
    unit_sequence: Mapped[int] = mapped_column(Integer) #display order for units
    unit_name: Mapped[str] = mapped_column(String(255))
    unit_description: Mapped[str] = mapped_column(Text)
    unit_opening_date: Mapped[datetime] = mapped_column(DateTime) #date when projects become available by default (can be overidden at the project level)
    unit_end_date: Mapped[datetime] = mapped_column(DateTime) #for display purposes, does not have any effect on flow
    unit_closing_date: Mapped[datetime] = mapped_column(DateTime) #date when projects become unavailable by default (can be overidden at the project level)

    #One to Many relationships
    #projects_in_unit: Mapped[List["Project"]] = relationship(back_populates="project_unit")

    def __init__(self, unit_name, unit_sequence, unit_opening_date, unit_closing_date, unit_end_date, unit_desciption):
        print("made a new unit")
        self.unit_name = unit_name
        self.unit_sequence = unit_sequence
        self.unit_opening_date = unit_opening_date
        self.unit_closing_date = unit_closing_date
        self.unit_end_date = unit_end_date
        self.unit_description = unit_desciption


    def add_unit(self):
        # Create a new unit
        session.add(self)
        session.commit()

    def update_unit(self):
        session.commit()

    def delete_unit(self):
        session.delete(self)
        session.commit()

    def list_all_units_by_sequence(self):
        self.units = session.query(Unit).all().order_by(Unit.unit_sequence)
        return self.units

def list_all_units_by_sequence():
    print("list_all_units_by_sequence")
    units = session.query(Unit).all().order_by(Unit.unit_sequence)
    print(units)
    return units

def getCurrentUnit():
    return session.query(Unit).filter(Unit.unitOpeningDate < datetime.now(), Unit.unitClosingDate >= datetime.now()).order_by(desc(Unit.unitOpeningDate)).first()

def getOpenUnits():
    return session.query(Unit).filter(Unit.unitOpeningDate < datetime.now(), Unit.unitClosingDate >= datetime.now()).order_by(desc(Unit.unitOpeningDate)).all()

