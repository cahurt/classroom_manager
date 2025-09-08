# Model/Student.py
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from datetime import datetime, date, time, timedelta

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from Persistance import Base, session

if TYPE_CHECKING:
    from .Project import Project
    from .Objective import Objective
    from .Hour import Hour
    from .Checkin import Checkin
    from .ClassroomLocation import ClassroomLocation



class Student(Base):
    __tablename__ = "students"
    MAX_STRING_LENGTH = 255

    studentID: Mapped[int] = mapped_column(primary_key=True)
    _student_glenpool_ID:Mapped[int] = mapped_column('student_glenpool_id',Integer,nullable=False)
    _studentRFID: Mapped[str] = mapped_column('student_rfid',String(MAX_STRING_LENGTH),nullable=False)
    _student_first_name: Mapped[str] = mapped_column('student_first_name',String(MAX_STRING_LENGTH),nullable=False)
    _student_last_name: Mapped[str] = mapped_column('student_last_name',String(MAX_STRING_LENGTH),nullable=False)
    _student_user_name: Mapped[str] = mapped_column('student_user_name',String(MAX_STRING_LENGTH),nullable=False)
    
    
    #one-to-one relationships 
    _student_hourID: Mapped[int] = mapped_column(ForeignKey("hours.hourID"),nullable=False)
    _student_hour: Mapped[Hour] = relationship(back_populates="_students_in_hour")

    _student_checkins: Mapped[list[Checkin]] = relationship(back_populates="_checkin_student", cascade="all, delete-orphan")

    # @studentTeamID: Mapped[int] = mapped_column(ForeignKey("teams.teamID"))
    # studentTeam: Mapped["Team"] = relationship(back_populates="studentsInTeam")
    # studentBathroomVisits: Mapped[List["BathroomVisit"]] = relationship(back_populates="bathroomVisitStudent")
    # studentReservations: Mapped[List["Reservation"]] = relationship(back_populates="reservationStudent")

    def __init__(self, studentID, glenpool_id: int, rfid: str, first_name: str, last_name: str, user_name: str, hour: Hour):
        """Initialize a new Student instance.

        Args:
            glenpool_id (int): Student's Glenpool ID
            rfid (str): Student's RFID
            first_name (str): Student's first name
            last_name (str): Student's last name
            user_name (str): Student's username
            hour_id (int): Student's hour ID
        """
        self.studentID = studentID
        self._student_glenpool_ID = glenpool_id
        self._studentRFID = rfid
        self._student_first_name = first_name
        self._student_last_name = last_name
        self._student_user_name = user_name
        self._student_hour = hour




    @property
    def glenpool_id(self) -> int:
        """Get student's Glenpool ID."""
        return self._student_glenpool_ID

    @glenpool_id.setter
    def glenpool_id(self, value: int) -> None:
        """Set student's Glenpool ID."""
        self._student_glenpool_ID = value

    @property
    def rfid(self) -> str:
        """Get student's RFID."""
        return self._studentRFID

    @rfid.setter
    def rfid(self, value: str) -> None:
        """Set student's RFID."""
        self._studentRFID = value

    @property
    def first_name(self) -> str:
        """Get student's first name."""
        return self._student_first_name

    @first_name.setter
    def first_name(self, value: str) -> None:
        """Set student's first name."""
        self._student_first_name = value

    @property
    def last_name(self) -> str:
        """Get student's last name."""
        return self._student_last_name

    @last_name.setter
    def last_name(self, value: str) -> None:
        """Set student's last name."""
        self._student_last_name = value

    @property
    def user_name(self) -> str:
        """Get student's username."""
        return self._student_user_name

    @user_name.setter
    def user_name(self, value: str) -> None:
        """Set student's username."""
        self._student_user_name = value

    @property
    def hour_id(self) -> int:
        """Get student's hour ID."""
        return self._student_hourID

    @hour_id.setter
    def hour_id(self, value: int) -> None:
        """Set student's hour ID."""
        self._student_hourID = value

    @property
    def id(self) -> int:
        """Get student's ID."""
        return self.studentID

    @id.setter
    def id(self, value: int) -> None:
        """Set student's ID."""
        self.studentID = value

    @property
    def hour(self) -> Hour:
        """Get student's assigned hour."""
        return self._student_hour

    @hour.setter
    def hour(self, value: Hour) -> None:
        """Set student's assigned hour."""
        self._student_hour = value

    @property
    def checkins(self) -> List[Checkin]:
        """Get student's checkins."""
        return self._student_checkins

    @checkins.setter
    def checkins(self, value: List[Checkin]) -> None:
        """Set student's checkins."""
        self._student_checkins = value

    def save(self):
        """Save this student instance to the database."""
        session.add(self)
        session.commit()

    def update(self):
        """Update this student's information in the database."""
        session.merge(self)
        session.commit()


    @classmethod
    def get_students_by_hour(cls, hour_id: int):
        """Get a query for students in a specific hour.

        Args:
            hour_id (int): The hour ID to filter students by

        Returns:
            Query: SQLAlchemy query object for students in the specified hour
        """
        return session.query(cls).filter(cls._student_hourID == hour_id)

    @classmethod
    def get_all_ordered_by_last_name(cls):
        """Get all students ordered by last name.

        Returns:
            Query: SQLAlchemy query object for all students ordered by last name
        """
        return session.query(cls).order_by(cls._student_last_name).all()

    @classmethod
    def get_by_id(cls, student_id: int):
        """Get a student by their ID.

        Args:
            student_id (int): The ID of the student to retrieve

        Returns:
            Student: The student with the specified ID, or None if not found
        """
        return session.query(cls).filter(cls.studentID == student_id).first()

    @classmethod
    def get_by_glenpool_id(cls, glenpool_id: int):
        """Get a student by their Glenpool ID.

        Args:
            glenpool_id (int): The Glenpool ID of the student to retrieve

        Returns:
            Student: The student with the specified Glenpool ID, or None if not found
        """
        return session.query(cls).filter(cls._student_glenpool_ID == glenpool_id).first()

    @classmethod
    def get_by_rfid(cls, rfid: str):
        """Get a student by their RFID.

        Args:
            rfid (str): The RFID of the student to retrieve

        Returns:
            Student: The student with the specified RFID, or None if not found
        """
        return session.query(cls).filter(cls._studentRFID == rfid).first()

    @classmethod
    def get_students_without_checkin_today(cls, hour: "Hour") -> List["Student"]:
        """Get all students in a specific hour who don't have a checkin for today.

        Args:
            hour (Hour): The hour to check students from

        Returns:
            List[Student]: List of students without a checkin today
        """

        # Ensure Checkin is defined in this scope (avoids NameError and circular imports)
        from .Checkin import Checkin

        today = date.today()
        start_of_day = datetime.combine(today, time.min)
        end_of_day = datetime.combine(today, time.max)

        students_with_checkins = (
            session.query(cls)
            .join(cls._student_checkins)
            .filter(
                cls._student_hourID == hour.hourID,
                Checkin._checkin_datetime >= start_of_day,
                Checkin._checkin_datetime <= end_of_day
            )
        )

        students_without_checkins = (
            session.query(cls)
            .filter(
                cls._student_hourID == hour.hourID,
                ~cls.studentID.in_(students_with_checkins.with_entities(cls.studentID))
            )
            .all()
        )

        return students_without_checkins
