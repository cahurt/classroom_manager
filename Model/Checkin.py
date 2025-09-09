# Model/Checkin.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timedelta, time

from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from Persistance import Base, session

if TYPE_CHECKING:
    from .Student import Student
    from .Hour import Hour
    from .Project import Project
    from .ClassroomLocation import ClassroomLocation


class Checkin(Base):
    __tablename__ = "checkins"
    MAX_STRING_LENGTH = 255

    checkinID: Mapped[int] = mapped_column(primary_key=True)
    _checkin_datetime: Mapped[datetime] = mapped_column('datetime', DateTime, nullable=False)
    _checkin_last_edited: Mapped[datetime] = mapped_column('last_edited', DateTime, nullable=False)



    # one-to-one relationships 
    _checkin_hourID: Mapped[int] = mapped_column(ForeignKey("hours.hourID"), nullable=False)
    checkin_hour: Mapped[Hour] = relationship(back_populates="checkins_in_hour")

    _checkin_studentID: Mapped[int] = mapped_column(ForeignKey("students.studentID"), nullable=False)
    _checkin_student: Mapped[Student] = relationship(back_populates="_student_checkins")

    _checkin_projectID: Mapped[int] = mapped_column(ForeignKey("projects.project_ID"), nullable=False)
    _checkin_project: Mapped[Project] = relationship(back_populates="_project_checkins")

    def __init__(self, checkin_datetime: datetime, checkin_hour: Hour, checkin_student: Student,
                 checkin_project: Student):
        self._checkin_datetime = checkin_datetime
        self._checkin_last_edited = datetime.now()
        self._checkin_hour = checkin_hour
        #shouldn't need to do this, but can't think of another way to get it out the door #TODO: track down why the hourID is not setting automatically
        self._checkin_hourID = checkin_hour.hourID
        self._checkin_student = checkin_student
        #shouldn't need to do this, but can't think of another way to get it out the door #TODO: track down why the StudentID is not setting automatically
        self._checkin_studentID = checkin_student.studentID
        self._checkin_project = checkin_project

    @property
    def datetime(self) -> datetime:
        return self._checkin_datetime

    @datetime.setter
    def datetime(self, value: datetime) -> None:
        self._checkin_datetime = value
        self._checkin_last_edited = datetime.now()

    @property
    def last_edited(self) -> datetime:
        return self._checkin_last_edited

    @last_edited.setter
    def last_edited(self, value: datetime) -> None:
        self._checkin_last_edited = value


    @property
    def hourID(self) -> int:
        return self._checkin_hourID

    @hourID.setter
    def hourID(self, value: int) -> None:
        self._checkin_hourID = value
        self._checkin_last_edited = datetime.now()

    @property
    def studentID(self) -> int:
        return self._checkin_studentID

    @studentID.setter
    def studentID(self, value: int) -> None:
        self._checkin_studentID = value
        self._checkin_last_edited = datetime.now()

    @property
    def projectID(self) -> int:
        return self._checkin_projectID

    @projectID.setter
    def projectID(self, value: int) -> None:
        self._checkin_projectID = value
        self._checkin_last_edited = datetime.now()

    @property
    def checkin_hour(self) -> "Hour":
        return self._checkin_hour

    @checkin_hour.setter
    def checkin_hour(self, value: "Hour") -> None:
        self._checkin_hour = value
        self._checkin_last_edited = datetime.now()

    @property
    def checkin_student(self) -> "Student":
        return self._checkin_student

    @checkin_student.setter
    def checkin_student(self, value: "Student") -> None:
        self._checkin_student = value
        self._checkin_last_edited = datetime.now()

    @property
    def checkin_project(self) -> "Project":
        return self._checkin_project

    @checkin_project.setter
    def checkin_project(self, value: "Project") -> None:
        self._checkin_project = value
        self._checkin_last_edited = datetime.now()

    def save(self) -> None:
        """Save this Checkin. Updates if it exists, otherwise adds it."""
        from datetime import datetime
        from sqlalchemy import inspect as sa_inspect

        try:
            mapper = sa_inspect(self.__class__)
            pk_cols = mapper.primary_key
            pk_values = tuple(getattr(self, col.key, None) for col in pk_cols)
            has_pk = all(v is not None for v in pk_values)

            exists = False
            if has_pk:
                identity = pk_values[0] if len(pk_values) == 1 else pk_values
                exists = session.get(self.__class__, identity) is not None

            if exists:
                # Mark as edited for updates
                self._checkin_last_edited = datetime.now()

            # Use merge to handle both insert and update safely (avoids cross-session issues)
            session.merge(self)
            session.commit()
        except Exception:
            session.rollback()
            raise

    def update(self) -> None:
        """Backward-compatible alias for save()."""
        self.save()

    @classmethod
    def get_by_id(cls, checkin_id: int) -> Optional['Checkin']:
        """Retrieve a checkin by its ID."""
        return session.query(cls).filter_by(checkinID=checkin_id).first()

    @classmethod
    def get_all(cls) -> List['Checkin']:
        """Retrieve all checkins."""
        return session.query(cls).all()

    @classmethod
    def get_checkins_by_hour_and_student_today(cls, hour: "Hour", student: "Student") -> Optional['Checkin']:
        """
        Retrieve the most recent checkin for today for a specific hour and student.
        Returns None if none exists.
        """
        # Build start-of-day and next-day bounds as datetimes to compare with a DateTime column
        today = datetime.now().date()
        start_of_day = datetime.combine(today, time.min)
        next_day = start_of_day + timedelta(days=1)

        return (
            session.query(cls)
            .filter(
                cls._checkin_hourID == hour.hourID,
                cls._checkin_studentID == student.studentID,
                cls._checkin_datetime >= start_of_day,
                cls._checkin_datetime < next_day,
            )
            .order_by(cls._checkin_datetime.desc())
            .first()
        )

    @classmethod
    def get_checkins_by_hour_today(cls, hour: "Hour") -> Optional['Checkin']:
        """
        Retrieve the most recent checkin for today for a specific hour and student.
        Returns None if none exists.
        """
        # Build start-of-day and next-day bounds as datetimes to compare with a DateTime column
        today = datetime.now().date()
        start_of_day = datetime.combine(today, time.min)
        next_day = start_of_day + timedelta(days=1)

        return (
            session.query(cls)
            .filter(
                cls._checkin_hourID == hour.hourID,
                cls._checkin_datetime >= start_of_day,
                cls._checkin_datetime < next_day,
            )
            .order_by(cls._checkin_datetime.desc())
            .first()
        )

