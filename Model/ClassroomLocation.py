from typing import List

from sqlalchemy import String, Integer, ForeignKey, Boolean, Text
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.attributes import Mapped
from Persistance import Base, session

class ClassroomLocation(Base):
    __tablename__ = 'classroom_locations'

    # Unique attributes
    classroom_location_ID: Mapped[int] = mapped_column(primary_key=True)
    classroom_location_name: Mapped[str] = mapped_column(String(255))
    classroom_location_label: Mapped[str] = mapped_column(String(255))
    classroom_location_label_size: Mapped[int] = mapped_column(Integer)
    classroom_location_label_color: Mapped[str] = mapped_column(String(255))
    classroom_location_description: Mapped[str] = mapped_column(Text)

    # One to Many relationships

    # Many to One relationships
    #consumables: Mapped[List["Consumable"]] = relationship(back_populates="consumable_location")
    # Many to Many relationships

    def __init__(self, classroom_location_name):
        self.classroom_location_name = classroom_location_name

    def add_classroom_location(self):
        # Create a new project
        session.add(self)
        session.commit()

    def update_classroom_location(self):
        session.commit()
