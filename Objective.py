from typing import List
import Persistance
from Persistance import *
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional

class Objective(Base):
    __tablename__ = 'objectives'

    # Unique attributes
    objective_ID: Mapped[int] = mapped_column(primary_key=True)
    objective_name: Mapped[str] = mapped_column(String(255))
    objective_description: Mapped[str] = mapped_column(Text)

    # One to Many relationships

    # Many to One relationships
    objective_projects: Mapped[List["Project"]] = relationship(back_populates="project_objective")
    # Many to Many relationships

    def __init__(self, objective_name, objective_description):
        self.objective_name = objective_name
        self.objective_description = objective_description

    def add_objective(self):
        # Create a new project
        session.add(self)
        session.commit()

    def update_objective(self):
        session.commit()

    def delete_objective(self):
        session.delete(self)
        session.commit()