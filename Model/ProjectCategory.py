from typing import List, Optional
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.attributes import Mapped
from Persistance import Base, session


class ProjectCategory(Base):
    """Represents a learning objective with specific properties."""

    __tablename__ = 'project_categories'

    # Constants for validation
    MAX_STRING_LENGTH = 255

    # Database columns
    objective_ID: Mapped[int] = mapped_column('objective_ID', primary_key=True)
    _name: Mapped[str] = mapped_column('project_category_name', String(MAX_STRING_LENGTH), nullable=False)
    _description: Mapped[str] = mapped_column('project_category_description', Text)

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
    def get_by_id(cls, objective_ID: int) -> Optional['ProjectCategory']:
        """Retrieve a project category by its ID."""
        return session.query(cls).filter_by(objective_ID=objective_ID).first()

    @classmethod
    def get_all_order_by_name(cls) -> List['ProjectCategory']:
        """Retrieve all project categories ordered by name."""
        return session.query(cls).order_by(cls._name).all()
