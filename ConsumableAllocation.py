
from Persistance import Base
from sqlalchemy import Integer, DateTime, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

class ConsumableAllocation(Base):
    __tablename__ = 'consumable_allocation'

    # Unique attributes
    consumable_allocation_ID: Mapped[int] = mapped_column(primary_key=True)
    consumable_allocation_quantity: Mapped[int] = mapped_column(Integer)

    consumable_allocated_for_project_ID: Mapped[int] = mapped_column(ForeignKey("project_project_ID"))
    consumable_allocated_for_project: Mapped["Project"] = relationship(back_populates="consumables_planned")
    consumable_allocated_consumable_ID: Mapped[int] = mapped_column(ForeignKey("consumables_consumable_ID"))
    consumable_allocated_consumable: Mapped["Consumable"] = relationship(back_populates="used_in_projects")
