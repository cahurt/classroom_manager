# Model/Checkin.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, timedelta



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
    #checkin_student: Mapped[Student] = relationship(back_populates="student_checkins")

    _checkin_projectID: Mapped[int] = mapped_column(ForeignKey("projects.project_ID"), nullable=False)
    _checkin_project: Mapped[Project] = relationship(back_populates="_project_checkins")

    def __init__(self, checkin_datetime: datetime, checkin_hour: Hour, checkin_student: Student,
                 checkin_project: Student):
        self._checkin_datetime = checkin_datetime
        self._checkin_last_edited = datetime.now()
        self._checkin_hour = checkin_hour
        #shouldn't need to do this, but can't think of another way to get it out the door #TODO: track down why the hourID is not setting automatically
        self._checkin_hourID = checkin_hour.hourID
        self._checkin_Student = checkin_student
        #shouldn't need to do this, but can't think of another way to get it out the door #TODO: track down why the StudentID is not setting automatically
        self._checkin_studentID = checkin_student.studentID
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

    @last_edited.setter
    def last_edited(self, value: datetime) -> None:
        self._checkin_last_edited = value

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
    def get_checkins_by_hour_student_today(cls, hour: 'Hour', student: 'Student') -> List['Checkin']:
        """Retrieve all checkins for today for a specific hour and student.

        Args:
            hour (Hour): The hour to filter checkins by
            student (Student): The student to filter checkins by

        Returns:
            List[Checkin]: List of checkins for the specified hour and student today
        """
        today = datetime.now().date()
        return session.query(cls).filter(
            cls._checkin_hourID == hour.hourID,
            cls._checkin_studentID == student.studentID,
            cls._checkin_datetime >= today,
            cls._checkin_datetime < today + datetime.timedelta(days=1)
        ).all()
