# Model/Project.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, select, func, cast, Date, and_

from sqlalchemy.orm import relationship, Mapped, mapped_column

from Persistance import Base, session

if TYPE_CHECKING:
    from .Student import Student
    from .ProjectCategory import ProjectCategory
    from .Objective import Objective
    from .Unit import Unit
    from .Hour import Hour
    from  .Checkin import Checkin




class Project(Base):
    MAX_STRING_LENGTH = 255

    __tablename__ = 'projects'

    # Unique attributes
    project_ID: Mapped[int] = mapped_column(primary_key=True)
    _name: Mapped[str] = mapped_column('project_name', String(255), nullable=False)
    _display_name: Mapped[str] = mapped_column('project_display_name', String(60), nullable=False)
    _open_date: Mapped[datetime] = mapped_column('project_open_date', DateTime, nullable=False)
    _close_date: Mapped[datetime] = mapped_column('project_close_date',DateTime, nullable=False)
    _description: Mapped[str] = mapped_column('project_description', Text, nullable=False)
    _days_allowed: Mapped[int] = mapped_column('project_days_allowed', Integer, nullable=False)
    _seats: Mapped[int] = mapped_column('project_seats',Integer,nullable=False)
    _minimum_group_size: Mapped[int] = mapped_column('project_minimum_group_size', Integer, nullable=False)
    _maximum_group_size: Mapped[int] = mapped_column('project_maximum_group_size', Integer, nullable=False)
    _sub_eligible : Mapped[bool] = mapped_column('project__sub_eligible', Boolean, default=False)
    _scheduled_date: Mapped[datetime] = mapped_column('project_scheduled_date', DateTime, nullable=True)


    # One to One relationships
    _unit_ID: Mapped[int] = mapped_column('project_unit_ID', ForeignKey("units.unit_ID"))
    _unit: Mapped[Unit] = relationship(back_populates="_projects_in_unit")

    _objective_ID: Mapped[int] = mapped_column('project_objective_ID', ForeignKey("objectives.objective_ID"))
    _objective: Mapped[Objective] = relationship(back_populates="_projects")

    _category_ID: Mapped[int] = mapped_column('project_category_ID',ForeignKey("project_categories.project_category_ID"))
    _project_category: Mapped[ProjectCategory] = relationship(back_populates="_projects_in_category")

    # One to Many relationships
    _project_checkins: Mapped[List["Checkin"]] = relationship(back_populates="_checkin_project")


    # Many to One relationships
    #project_consumable_checkouts: Mapped[List["ConsumableCheckout"]] = relationship(back_populates="consumable_checkout_project")
    #consumables_planned: Mapped[List["ConsumableAllocation"]] = relationship(back_populates="consumable_allocated_for_project")


   #projectReservations: Mapped[List["Reservation"]] = relationship(back_populates="reservationProject")
    #materialsRequired: Mapped[List["Material"]] = relationship(back_populates="MaterialProject")

    # Many to Many relationships
    #projectToolsRequired: Mapped[List["Tool"]] = relationship(secondary="tool_project_association", back_populates="projectsThatUseThisTool")
    #projectToolAssociations: Mapped[List["ToolProjectAssociation"]] = relationship(back_populates="project")
    #projectMaterialsRequired: Mapped[List["Material"]] = relationship(secondary="material_project_association", back_populates="projectsThatUseThisMaterial")
    #projectMaterialAssociations: Mapped[List["MaterialProjectAssociation"]] = relationship(back_populates="project")

    def __init__(self,name: str, display_name: str, description: str, open_date: datetime, close_date: datetime,
                 days_allowed: int, seats: int, minimum_group_size: int,
                 maximum_group_size: int, sub_eligible: bool = False, ignore_validation=False,
                 unit: Optional[Unit] = None, objective: Optional[Objective] = None,  category: Optional[ProjectCategory] = None):

        self.name = name
        self._display_name = display_name
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
        self.category = category

    @property
    def open_date(self) -> datetime:
        return self._open_date

    @open_date.setter
    def open_date(self, value: datetime) -> None:
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                try:
                    value = datetime.strptime(value, '%m/%d/%y')
                except ValueError:
                    raise ValueError(f'Date string must be in YYYY-MM-DD or MM/DD/YY format - {value}')
        if not isinstance(value, datetime):
            raise ValueError(f'Open date must be a datetime object - {value}')
        self._open_date = value

    @property
    def display_name(self) -> str:
        return self._display_name

    @display_name.setter
    def display_name(self, value: str) -> None:
        if not value or len(value) > 60:
            raise ValueError("Display name must be between 1 and 60 characters")
        self._display_name = value

    @property
    def close_date(self) -> datetime:
        return self._close_date

    @close_date.setter
    def close_date(self, value: datetime) -> None:
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                try:
                    value = datetime.strptime(value, '%m/%d/%y')
                except ValueError:
                    raise ValueError(f'Date string must be in YYYY-MM-DD or MM/DD/YY format - {value}')
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

    @property
    def scheduled_date(self) -> datetime:
        return self._scheduled_date

    @scheduled_date.setter
    def scheduled_date(self, value: datetime) -> None:
        if isinstance(value, str):
            try:
                value = datetime.strptime(value, '%Y-%m-%d')
            except ValueError:
                try:
                    value = datetime.strptime(value, '%m/%d/%y')
                except ValueError:
                    raise ValueError(f'Date string must be in YYYY-MM-DD or MM/DD/YY format - {value}')
        if not isinstance(value, datetime):
            raise ValueError("Scheduled date must be a datetime object")
        self._scheduled_date = value


    @property
    def unit_id(self) -> int:
        return self._unit_ID

    @unit_id.setter
    def unit_id(self, value: int) -> None:
        self._unit_ID = value

    @property
    def objective_id(self) -> int:
        return self._objective_ID

    @objective_id.setter
    def objective_id(self, value: int) -> None:
        self._objective_ID = value

    @property
    def category_id(self) -> int:
        return self._category_ID

    @category_id.setter
    def category_id(self, value: int) -> None:
        self._category_ID = value

    @property
    def project_category(self) -> ProjectCategory:
        return self._project_category

    @project_category.setter
    def project_category(self, value: ProjectCategory) -> None:
        self._project_category = value

    @property
    def project_checkins(self) -> List["Checkin"]:
        return self._project_checkins

    @project_checkins.setter
    def project_checkins(self, value: List["Checkin"]) -> None:
        self._project_checkins = value

    #*********************************************************************
    #           Persistance methods
    #*******************************************************************
    def save(self) -> None:
        """Save or update the project in the database."""
        try:
            session.add(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

    def delete(self) -> None:
        """Delete the project from the database."""
        try:
            session.delete(self)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

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

    @classmethod
    def get_available_projects(
            cls,
            student: Student,
            hour: Hour,
            now: datetime | None = None,
    ) -> List[Project]:
        """
        Return projects that are:
          - Open (now between open and close dates, inclusive)
          - Not over the student's allowed days for that project
            (student's checkins for the project <= project._days_allowed)
          - Not full for the given hour today
            (today's checkins for that project+hour < project._seats)
        """
        if now is None:
            now = datetime.now()
        today: date = now.date()

        # Defensive checks for required identifiers
        student_id = getattr(student, "studentID", None)
        hour_id = getattr(hour, "hourID", None)
        if student_id is None:
            raise ValueError("Student must have a valid primary key (studentID).")
        if hour_id is None:
            raise ValueError("Hour must have a valid primary key (hourID).")

        # Correlated subquery: total checkins by this student for each project
        student_checkins_for_project = (
            select(func.count(Checkin.checkinID))
            .where(
                Checkin._checkin_projectID == Project.project_ID,
                Checkin._checkin_studentID == student_id,
            )
            .correlate(Project)
            .scalar_subquery()
        )

        # Correlated subquery: today's checkins for this project and hour
        todays_hour_checkins_for_project = (
            select(func.count(Checkin.checkinID))
            .where(
                Checkin._checkin_projectID == Project.project_ID,
                Checkin._checkin_hourID == hour_id,
                cast(Checkin._checkin_datetime, Date) == today,
            )
            .correlate(Project)
            .scalar_subquery()
        )

        q = (
            session.query(Project)
            .filter(
                and_(
                    Project._open_date <= now,
                    Project._close_date >= now,
                    student_checkins_for_project <= Project._days_allowed,
                    todays_hour_checkins_for_project < Project._seats,
                )
            )
            .order_by(Project._display_name)
        )

        return q.all()


