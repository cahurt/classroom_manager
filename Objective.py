from typing import List
import persistance
from persistance import *
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional

class Objective(Base):
    __tablename__ = 'objectives'

    # Unique attributes
    objectiveID: Mapped[int] = mapped_column(primary_key=True)
    objectiveName: Mapped[str] = mapped_column(String(255))

    # One to Many relationships

    # Many to One relationships

    # Many to Many relationships

    def __init__(self, objectiveName):
        self.objectiveName = objectiveName

    def addObjective(self):
        # Create a new project
        session.add(self)
        session.commit()

    def updateObjective(self):
        session.commit()
