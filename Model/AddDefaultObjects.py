# Model/AddDefaultObjects.py
from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime

from Persistance import session

# For type hints only; import actual models inside functions if needed.
if TYPE_CHECKING:
    from .Student import Student
    from .Project import Project
    from .ProjectCategory import ProjectCategory
    from .Objective import Objective
    from .Unit import Unit
    from .Hour import Hour
    from .Checkin import Checkin
    from .ClassroomLocation import ClassroomLocation


class AddDefaultObjects:
    def __init__(self, add_project_categories: bool):
        """Select which default objects to create."""
        if add_project_categories:
            self.add_project_categories()

    def add_project_categories(self) -> None:
        # Import at runtime to avoid circular imports and ensure availability
        from .ProjectCategory import ProjectCategory

        # Define default categories and their descriptions
        categories: dict[str, str] = {
            "Career": "Career related projects",
            "Guided": "projects that have a clear set of instructions designed to teach a specific skill",
            "Knowledge": "Projects that are predominantly book work",
            "Extension": "projects that use skills gained in guided and knowledge projects, they typically do not have a set follow-me list of instructions, but rather have a list of end goals",
            "Capstone": "Projects that are predominantly book work",
            "Add-On": "Projects that are special add ons",
            "Group": "Projects that are done together on a scheduled day",
        }

        # Insert only the categories that don't already exist (idempotent)
        created_any = False
        for name, description in categories.items():
            # Use the mapped column name; many models map _name as the column
            exists = session.query(ProjectCategory).filter_by(_name=name).first()
            if not exists:
                session.add(ProjectCategory(name, description))
                created_any = True

        if created_any:
            session.commit()