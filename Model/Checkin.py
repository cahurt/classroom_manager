from datetime import datetime
from typing import List, Optional
import Persistance
from sqlalchemy import Integer, DateTime, String, Boolean, Text, ForeignKey, select

from Model import Student
from Persistance import session
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .Hour import Hour
    from .Student import Student
    from .Project import Project
from Model.Hour import Hour
from Model.Student import Student
from Model.Project import Project


class Checkin(Persistance.Base):
    __tablename__ = "checkins"
    MAX_STRING_LENGTH = 255

    checkinID: Mapped[int] = mapped_column(primary_key=True)
    _checkin_datetime: Mapped[datetime] = mapped_column('datetime', DateTime, nullable=False)
    _checkin_last_edited: Mapped[datetime] = mapped_column('last_edited', DateTime, nullable=False)

    # one-to-one relationships 
    _checkin_hourID: Mapped[int] = mapped_column(ForeignKey("hours.hourID"), nullable=False)
    _checkin_hour: Mapped["Hour"] = relationship(back_populates="checkins_in_hour")

    _checkin_studentID: Mapped[int] = mapped_column(ForeignKey("students.studentID"), nullable=False)
    _checkin_Student: Mapped["Student"] = relationship(back_populates="student_checkins")

    _checkin_projectID: Mapped[int] = mapped_column(ForeignKey("projects.projectID"), nullable=False)
    _checkin_project: Mapped["Student"] = relationship(back_populates="project_checkins")

    def __init__(self, checkin_datetime: datetime, checkin_hour: "Hour", checkin_student: "Student",
                 checkin_project: "Student"):
        self._checkin_datetime = checkin_datetime
        self._checkin_last_edited = datetime.now()
        self._checkin_hour = checkin_hour
        self._checkin_Student = checkin_student
        self._checkin_project = checkin_project

    @property
    def checkin_datetime(self) -> datetime:
        return self._checkin_datetime

    @checkin_datetime.setter
    def datetime(self, value: datetime) -> None:
        self._checkin_datetime = value
        self._checkin_last_edited = datetime.now()

    @property
    def last_edited(self) -> datetime:
        return self._checkin_last_edited

    @property
    def checkin_hour(self) -> "Hour":
        return self._checkin_hour

    @checkin_hour.setter
    def checkin_hour(self, value: "Hour") -> None:
        self._checkin_hour = value
        self._checkin_last_edited = datetime.now()

    @property
    def checkin_student(self) -> "Student":
        return self._checkin_Student

    @checkin_student.setter
    def checkin_student(self, value: "Student") -> None:
        self._checkin_Student = value
        self._checkin_last_edited = datetime.now()

    @property
    def checkin_project(self) -> "Student":
        return self._checkin_project

    @checkin_project.setter
    def checkin_project(self, value: "Student") -> None:
        self._checkin_project = value
        self._checkin_last_edited = datetime.now()

    def save(self) -> None:
        """Save or update the checkin in the database."""
        session.add(self)
        session.commit()

    def update(self) -> None:
        """Update the existing checkin in the database."""
        self._checkin_last_edited = datetime.now()
        session.commit()

    @classmethod
    def get_by_id(cls, checkin_id: int) -> Optional['Checkin']:
        """Retrieve a checkin by its ID."""
        return session.query(cls).filter_by(checkinID=checkin_id).first()

    @classmethod
    def get_all(cls) -> List['Checkin']:
        """Retrieve all checkins."""
        return session.query(cls).all()
