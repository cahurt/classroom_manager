from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.attributes import Mapped
from Persistance import Base, session
import ClassroomLocation

class Consumable(Base):
    __tablename__ = 'consumables'

    # Unique attributes
    consumable_ID: Mapped[int] = mapped_column(primary_key=True)
    consumable_name: Mapped[str] = mapped_column(String(255))
    consumable_quantity_available: Mapped[int] = mapped_column(Integer)


    # One to Many relationships
    consumable_location_ID: Mapped[int] = mapped_column(ForeignKey("classroom_locations.classroom_location_ID"))
    consumable_location: Mapped["ClassroomLocation"] = relationship(back_populates="consumables")

    # Many to One relationships

    # Many to Many relationships

    def __init__(self, consumable_name, consumable_quantity_available, consumable_location):
        self.consumable_name = consumable_name
        self.consumable_quantity_available = consumable_quantity_available
        self.consumable_location = consumable_location

    def add_consumable(self):
        # Create a new consumable
        session.add(self)
        session.commit()

    def update_consumable(self):
        session.commit()
