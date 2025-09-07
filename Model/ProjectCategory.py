# Model/ProjectCategory.py
from __future__ import annotations
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship, mapped_column, Mapped

from Persistance import Base, session

if TYPE_CHECKING:
    from .Project import Project



class ProjectCategory(Base):
    """Represents a learning objective with specific properties."""

    __tablename__ = 'project_categories'

    # Constants for validation
    MAX_STRING_LENGTH = 255

    # Database columns
    project_category_ID: Mapped[int] = mapped_column('project_category_ID', primary_key=True)
    _name: Mapped[str] = mapped_column('project_category_name', String(MAX_STRING_LENGTH), nullable=False)
    _description: Mapped[str] = mapped_column('project_category_description', Text)

    _projects_in_category: Mapped[List[Project]] = relationship(back_populates="_project_category")

    def __init__(self, name: str, description: str = ""):
        """Initialize a new objective.
        Args:
            name: The name of the objective
            description: Detailed description of the objective
        """
        self.name = name
        self.description = description

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

    def save(self) -> None:
        """Save or update the project category in the database."""
        session.add(self)
        session.commit()

    def delete(self) -> None:
        """Delete the project category from the database."""
        session.delete(self)
        session.commit()

    

    @classmethod
    def get_by_id(cls, category_id: int) -> Optional['ProjectCategory']:
        """Retrieve a project category by its ID.
        Args:
            category_id: The ID of the project category to retrieve
        Returns:
            The ProjectCategory if found, None otherwise
        """
        return session.query(cls).filter(cls.project_category_ID == category_id).first()


    @classmethod


    def get_all_order_by_name(cls) -> List['ProjectCategory']:
            """Retrieve all project categories ordered by name."""
            return session.query(cls).order_by(cls._name).all()
