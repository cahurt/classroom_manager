# object used to track checked out consumables
import datetime

from sqlalchemy import String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm.attributes import Mapped
from Persistance import Base, session
from Model import Project
from Model import Consumable
from Model import Group


class ConsumableCheckout(Base):
    __tablename__ = 'consumable_checkout'

    # Unique attributes
    consumable_checkout_ID: Mapped[int] = mapped_column(primary_key=True)
    consumable_quantity_used: Mapped[int] = mapped_column(Integer)
    consumable_checkout_date: Mapped[datetime] = mapped_column(DateTime)

    # One to one relationships

    # One to Many relationships
    consumable_checkout_project_ID: Mapped[int] = mapped_column(ForeignKey("projects.project_ID"))
    consumable_checkout_project: Mapped["Project"] = relationship(back_populates="project_consumable_checkouts")

    consumable_checkout_consumable_ID: Mapped[int] = mapped_column(ForeignKey("consumables.consumable_ID"))
    consumable_checkout_consumable: Mapped["Consumable"] = relationship(back_populates="consumable_checkouts")

    consumable_checkout_to_group_ID: Mapped[int] = mapped_column(ForeignKey("groups.group_ID"))
    consumable_checkout_to_group: Mapped["Group"] = relationship(back_populates="group_consumable_checkouts")

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
