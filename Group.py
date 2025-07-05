from typing import List
import Persistance
from Persistance import *
from sqlalchemy import Integer, DateTime, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional
import Project

class Group(Base):
    __tablename__ = 'groups'

    # Unique attributes
    group_ID: Mapped[int] = mapped_column(primary_key=True)
    group_name: Mapped[str] = mapped_column(String(255))

    # One to Many relationships

    # Many to One relationships
    group_projects: Mapped[List["Project"]] = relationship(back_populates="project_group")
    group_consumable_checkouts: Mapped[List["ConsumableCheckout"]] = relationship(back_populates="consumable_checkout_to_group")
    # Many to Many relationships

    def __init__(self, groupName):
        self.groupName = groupName

    def add_group(self):
        # Create a new project
        session.add(self)
        session.commit()

    def update_group(self):
        session.commit()
