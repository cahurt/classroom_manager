import datetime
from typing import List
import Persistance
from sqlalchemy import Integer, DateTime, String, Boolean, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from typing import Optional
import Consumable
import ConsumableCheckout
import Unit
import Objective


class Project(Persistance.Base):
    __tablename__ = 'projects'

    # Unique attributes
    project_ID: Mapped[int] = mapped_column(primary_key=True)
    project_open_date: Mapped[datetime] = mapped_column(DateTime)
    project_close_date: Mapped[datetime] = mapped_column(DateTime)
    project_name: Mapped[str] = mapped_column(String(255))
    project_description: Mapped[str] = mapped_column(Text)
    project_days_allowed: Mapped[int] = mapped_column(Integer)
    project_seats: Mapped[int] = mapped_column(Integer)
    project_minimum_group_size: Mapped[int] = mapped_column(Integer)
    project_maximum_group_size: Mapped[int] = mapped_column(Integer)

    project_sub_eligible : Mapped[bool] = mapped_column(Boolean)

    # One to Many relationships
    project_unit_ID: Mapped[int] = mapped_column(ForeignKey("units.unit_ID"))
    project_unit: Mapped["Unit"] = relationship(back_populates="projects_in_unit")

    project_objective_ID: Mapped[int] = mapped_column(ForeignKey("objectives.objective_ID"))
    project_objective: Mapped["Objective"] = relationship(back_populates="objective_projects")


    # Many to One relationships
    project_consumable_checkouts: Mapped[List["ConsumableCheckout"]] = relationship(back_populates="consumable_checkout_project")
    consumables_planned: Mapped[List["ConsumableAllocation"]] = relationship(back_populates="consumable_allocated_for_project")

    #projectCheckins: Mapped[List["Checkin"]] = relationship(back_populates="checkinProject")
   #projectReservations: Mapped[List["Reservation"]] = relationship(back_populates="reservationProject")
    #materialsRequired: Mapped[List["Material"]] = relationship(back_populates="MaterialProject")

    # Many to Many relationships
    #projectToolsRequired: Mapped[List["Tool"]] = relationship(secondary="tool_project_association", back_populates="projectsThatUseThisTool")
    #projectToolAssociations: Mapped[List["ToolProjectAssociation"]] = relationship(back_populates="project")
    #projectMaterialsRequired: Mapped[List["Material"]] = relationship(secondary="material_project_association", back_populates="projectsThatUseThisMaterial")
    #projectMaterialAssociations: Mapped[List["MaterialProjectAssociation"]] = relationship(back_populates="project")


    def __init__(self, projectOpenDate, projectCloseDate, projectName, projectUnit, projectDaysAllowed, projectConcurrentAllowed, projectSubEligible):
        self.projectOpenDate = projectOpenDate
        self.projectCloseDate = projectCloseDate
        self.projectName = projectName
        self.projectUnit = projectUnit
        self.projectDaysAllowed = projectDaysAllowed
        self.projectConcurrentAllowed = projectConcurrentAllowed
        self.projectSubEligible = projectSubEligible

    def getNumberOfToolsRequired(self):
        return len(self.projectToolsRequired)

    def getNumberOfCheckinsforDateAndHour(self, dateRequestedForCheckins, hourRequestedForCheckins):
        checkinsInHour = 0

        for checkin in self.projectCheckins:
            if checkin.checkinHour == hourRequestedForCheckins:
                checkinsInHour += 1

        return checkinsInHour


    def addProject(self):
        # Create a new project
        session.add(self)
        session.commit()

    def updateProject(self):
        session.commit()

def listAllProjects():
    projects = Persistance.session.query(Project).all()
    return projects

def listOpenProjects():
    projects = Persistance.session.query(Project).filter(Project.projectOpenDate <= datetime.now()).all()
    for project in projects:
        var1 = 1
        # print(f"Project: {project.projectName}, {project.projectOpenDate}")
    return projects

# sub classes used for things like tracking what is needed or other things that are directly tied to the project and probablyu should not be in thier own object

