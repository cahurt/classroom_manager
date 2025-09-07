# Model/Objective.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped

from Persistance import Base, session

if TYPE_CHECKING:
    from .Student import Student
    from .Project import Project
    from .Unit import Unit




class Objective(Base):
    """Represents a learning objective with specific properties."""

    __tablename__ = 'objectives'

    # Constants for validation
    MAX_STRING_LENGTH = 255
    MIN_HOURS = 0
    MAX_HOURS = 1000

    # Database columns
    objective_ID: Mapped[int] = mapped_column('objective_ID', primary_key=True)
    _name: Mapped[str] = mapped_column('objective_name', String(MAX_STRING_LENGTH), nullable=False)
    _description: Mapped[str] = mapped_column('objective_description', Text)
    _hours_required: Mapped[int] = mapped_column('hours_required', Integer, default=0, nullable=False)
    _hours_allocated: Mapped[int] = mapped_column('hours_allocated', Integer, default=0)

    #relationships
    _projects: Mapped[List[Project]] = relationship(back_populates="_objective")

    def __init__(self, name: str, description: str = "", hours_required: float = 0, hours_allocated: float = 0,
                 ignore_validation=False):
        """Initialize a new objective.

        Args:
            name: The name of the objective
            description: Detailed description of the objective
            hours_required: Required hours for the objective
            hours_allocated: Allocated hours for the objective
        """
        self.name = name
        self.description = description
        self.hours_required = hours_required
        self.hours_allocated = hours_allocated

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or len(value) > self.MAX_STRING_LENGTH:
            raise ValueError(f"Name must be between 1 and {self.MAX_STRING_LENGTH} characters")
        self._name = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value or ""

    @property
    def hours_required(self) -> float:
        return self._hours_required

    @hours_required.setter
    def hours_required(self, value: float) -> None:
        if not self.MIN_HOURS <= value <= self.MAX_HOURS:
            raise ValueError(f"Hours required must be between {self.MIN_HOURS} and {self.MAX_HOURS}")
        self._hours_required = value

    @property
    def hours_allocated(self) -> float:
        return self._hours_allocated

    @hours_allocated.setter
    def hours_allocated(self, value: float) -> None:
        if not self.MIN_HOURS <= value <= self.MAX_HOURS:
            raise ValueError(f"Hours allocated must be between {self.MIN_HOURS} and {self.MAX_HOURS}")
        self._hours_allocated = value

    def save(self) -> None:
        """Save or update the objective in the database."""
        session.add(self)
        session.commit()

    def delete(self) -> None:
        """Delete the objective from the database."""
        session.delete(self)
        session.commit()


    @property
    def projects(self) -> List['Project']:
        return self._projects


    @projects.setter
    def projects(self, value: List['Project']) -> None:
        self._projects = value



    @classmethod
    def get_by_id(cls, objective_ID: int) -> Optional['Objective']:
        """Retrieve an objective by its ID."""
        return session.query(cls).filter_by(objective_ID=objective_ID).first()

    @classmethod
    def get_all(cls) -> List['Objective']:
        """Retrieve all objectives."""
        return session.query(cls).order_by(cls._name).all()

    @classmethod
    def get_all_order_by_name(cls) -> List['Objective']:
        """Retrieve all objectives ordered by name."""
        return session.query(cls).order_by(cls._name).all()
