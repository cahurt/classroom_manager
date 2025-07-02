from typing import List
import persistance
from persistance import *
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional

class Unit(Base):
    __tablename__ = 'units'

    # Unique attributes
    unitID: Mapped[int] = mapped_column(primary_key=True)
    unitName: Mapped[str] = mapped_column(String(255))

    # One to Many relationships

    # Many to One relationships

    # Many to Many relationships

    def __init__(self, unitName):
        self.unitName = unitName

    def addUnit(self):
        # Create a new project
        session.add(self)
        session.commit()

    def updateUnit(self):
        session.commit()
