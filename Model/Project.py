import datetime
from typing import List
import Persistance
from sqlalchemy import Integer, DateTime, String, Boolean, Text, ForeignKey
from Persistance import session
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Unit import Unit
    from .Objective import Objective



class Project(Persistance.Base):
    MAX_STRING_LENGTH = 255

    __tablename__ = 'projects'

    # Unique attributes
    project_ID: Mapped[int] = mapped_column(primary_key=True)
    _name: Mapped[str] = mapped_column('project_name', String(255), nullable=False)
    _open_date: Mapped[datetime] = mapped_column('project_open_date', DateTime, nullable=False)
    _close_date: Mapped[datetime] = mapped_column('project_close_date',DateTime, nullable=False)
    _description: Mapped[str] = mapped_column('project_description', Text, nullable=False)
    _days_allowed: Mapped[int] = mapped_column('project_days_allowed', Integer, nullable=False)
    _seats: Mapped[int] = mapped_column('project_seats',Integer,nullable=False)
    _minimum_group_size: Mapped[int] = mapped_column('project_minimum_group_size', Integer, nullable=False)
    _maximum_group_size: Mapped[int] = mapped_column('project_maximum_group_size', Integer, nullable=False)
    _sub_eligible : Mapped[bool] = mapped_column('project__sub_eligible', Boolean, default=False)

    # One to Many relationships
    _unit_ID: Mapped[int] = mapped_column('project_unit_ID', ForeignKey("units.unit_ID"))
    _unit: Mapped["Unit"] = relationship("Model.Unit.Unit", back_populates="_projects_in_unit")

    _objective_ID: Mapped[int] = mapped_column('project_objective_ID', ForeignKey("objectives.objective_ID"))
    _objective: Mapped["Objective"] = relationship("Model.Objective.Objective", back_populates="_projects")


    # Many to One relationships
    #project_consumable_checkouts: Mapped[List["ConsumableCheckout"]] = relationship(back_populates="consumable_checkout_project")
    #consumables_planned: Mapped[List["ConsumableAllocation"]] = relationship(back_populates="consumable_allocated_for_project")

    #projectCheckins: Mapped[List["Checkin"]] = relationship(back_populates="checkinProject")
   #projectReservations: Mapped[List["Reservation"]] = relationship(back_populates="reservationProject")
    #materialsRequired: Mapped[List["Material"]] = relationship(back_populates="MaterialProject")

    # Many to Many relationships
    #projectToolsRequired: Mapped[List["Tool"]] = relationship(secondary="tool_project_association", back_populates="projectsThatUseThisTool")
    #projectToolAssociations: Mapped[List["ToolProjectAssociation"]] = relationship(back_populates="project")
    #projectMaterialsRequired: Mapped[List["Material"]] = relationship(secondary="material_project_association", back_populates="projectsThatUseThisMaterial")
    #projectMaterialAssociations: Mapped[List["MaterialProjectAssociation"]] = relationship(back_populates="project")

    def __init__(self,name: str, description: str, open_date: datetime, close_date: datetime,
                 days_allowed: int, seats: int, minimum_group_size: int,
                 maximum_group_size: int, sub_eligible: bool = False, ignore_validation=False,
                 unit: Optional["Unit"] = None, objective: Optional["Objective"] = None):

        self.name = name
        self.open_date = open_date
        self.close_date = close_date
        self.description = description
        self.days_allowed = days_allowed
        self.seats = seats
        self.minimum_group_size = minimum_group_size
        self.maximum_group_size = maximum_group_size
        self.sub_eligible = sub_eligible
        self.unit = unit
        self.objective = objective

    @property
    def open_date(self) -> datetime:
        return self._open_date

    @open_date.setter
    def open_date(self, value: datetime) -> None:
        print(value)
        if not isinstance(value, datetime):
            raise ValueError("Open date must be a datetime object")
        self._open_date = value

    @property
    def close_date(self) -> datetime:
        return self._close_date

    @close_date.setter
    def close_date(self, value: datetime) -> None:
        if not isinstance(value, datetime):
            raise ValueError("Close date must be a datetime object")
        self._close_date = value


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
        if not value:
            raise ValueError("Description cannot be empty")
        self._description = value

    @property
    def days_allowed(self) -> int:
        return self._days_allowed

    @days_allowed.setter
    def days_allowed(self, value: int) -> None:
        if value < 1:
            raise ValueError("Days allowed must be at least 1")
        self._days_allowed = value

    @property
    def seats(self) -> int:
        return self._seats

    @seats.setter
    def seats(self, value: int) -> None:
        if value < 1:
            raise ValueError("Seats must be at least 1")
        self._seats = value

    @property
    def minimum_group_size(self) -> int:
        return self._minimum_group_size

    @minimum_group_size.setter
    def minimum_group_size(self, value: int) -> None:
        if value < 1:
            raise ValueError("Minimum group size must be at least 1")
        self._minimum_group_size = value

    @property
    def maximum_group_size(self) -> int:
        return self._maximum_group_size

    @maximum_group_size.setter
    def maximum_group_size(self, value: int) -> None:
        if value < self._minimum_group_size:
            raise ValueError("Maximum group size must be greater than or equal to minimum group size")
        self._maximum_group_size = value

    @property
    def sub_eligible(self) -> bool:
        return self._sub_eligible

    @sub_eligible.setter
    def sub_eligible(self, value: bool) -> None:
        self._sub_eligible = value

    @property
    def unit(self) -> Optional["Unit"]:
        return self._unit

    @unit.setter
    def unit(self, value: Optional["Unit"]) -> None:
        self._unit = value

    @property
    def objective(self) -> Optional["Objective"]:
        return self._objective

    @objective.setter
    def objective(self, value: Optional["Objective"]) -> None:
        self._objective = value

    @classmethod
    def get_all_ordered_by_name(cls) -> List["Project"]:
        """Retrieve all projects ordered by name."""
        return session.query(cls).order_by(cls._name).all()

    @classmethod
    def get_by_id(cls, project_ID: int) -> Optional["Project"]:
        """Retrieve a project by its ID.

        Args:
            project_ID: The ID of the project to retrieve

        Returns:
            The Project instance if found, None otherwise
        """
        return session.query(cls).filter_by(project_ID=project_ID).first()

