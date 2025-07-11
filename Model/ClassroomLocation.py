from typing import List, Optional
from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.attributes import Mapped
from Persistance import Base, session


class ClassroomLocation(Base):
    """Represents a physical location within a classroom with specific display properties."""

    __tablename__ = 'classroom_locations'

    # Constants for validation
    MAX_STRING_LENGTH = 255
    MIN_LABEL_SIZE = 0
    MAX_LABEL_SIZE = 100

    # Database columns
    classroom_location_ID: Mapped[int] = mapped_column('classroom_location_ID', primary_key=True)
    _name: Mapped[str] = mapped_column('classroom_location_name', String(MAX_STRING_LENGTH))
    _label: Mapped[str] = mapped_column('classroom_location_label', String(MAX_STRING_LENGTH))
    _label_size: Mapped[int] = mapped_column('classroom_location_label_size', Integer)
    _label_color: Mapped[str] = mapped_column('classroom_location_label_color', String(MAX_STRING_LENGTH))
    _description: Mapped[str] = mapped_column('classroom_location_description', Text)

    def __init__(self, name: str, label: str = "", label_size: int = 12,
                 label_color: str = "#000000", description: str = "", ignore_validation=False):
        """Initialize a new classroom location.
        
        Args:
            name: The name of the location
            label: Display label for the location
            label_size: Size of the label text
            label_color: Color code for the label
            description: Detailed description of the location
        """
        self.name = name
        self.label = label
        self.label_size = label_size
        self.label_color = label_color
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
    def label(self) -> str:
        return self._label

    @label.setter
    def label(self, value: str) -> None:
        if len(value) > self.MAX_STRING_LENGTH:
            raise ValueError(f"Label cannot exceed {self.MAX_STRING_LENGTH} characters")
        self._label = value

    @property
    def label_size(self) -> int:
        return self._label_size

    @label_size.setter
    def label_size(self, value: int) -> None:
        if not self.MIN_LABEL_SIZE <= value <= self.MAX_LABEL_SIZE:
            raise ValueError(f"Label size must be between {self.MIN_LABEL_SIZE} and {self.MAX_LABEL_SIZE}")
        self._label_size = value

    @property
    def label_color(self) -> str:
        return self._label_color

    @label_color.setter
    def label_color(self, value: str) -> None:
        # Basic hex color validation
        if not (value.startswith('#') and len(value) in [4, 7]):
            raise ValueError("Label color must be a valid hex color code (e.g., #FFF or #FFFFFF)")
        self._label_color = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str) -> None:
        self._description = value or ""

    def save(self) -> None:
        """Save or update the classroom location in the database."""
        session.add(self)
        session.commit()

    def delete(self) -> None:
        """Delete the classroom location from the database."""
        session.delete(self)
        session.commit()

    @classmethod
    def get_by_id(cls, location_ID: int) -> Optional['ClassroomLocation']:
        """Retrieve a classroom location by its ID."""
        return session.query(cls).filter_by(classroom_location_ID=location_ID).first()

    @classmethod
    def get_all(cls) -> List['ClassroomLocation']:
        """Retrieve all classroom locations."""
        return session.query(cls).order_by(cls._name).all()

    @classmethod
    def get_all_order_by_name(cls) -> List['ClassroomLocation']:
        """Retrieve all classroom locations ordered by name."""
        return session.query(cls).order_by(cls._name).all()
