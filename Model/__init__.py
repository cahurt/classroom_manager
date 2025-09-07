## Model/__init__.py
from __future__ import annotations
from typing import TYPE_CHECKING
from .Objective import Objective
from .Checkin import Checkin
from .Student import Student
from .Hour import Hour
from .Project import Project

from .ProjectCategory import ProjectCategory
from .ClassroomLocation import ClassroomLocation
from .Unit import Unit



__all__ = [
    "Student",
    "Project",
    "ProjectCategory",
    "Objective",
    "Unit",
    "Hour",
    "Checkin",
    "ClassroomLocation",
]

# Avoid importing models at runtime to prevent circular imports.
if TYPE_CHECKING:
    from .Checkin import Checkin
    from .Student import Student
    from .Project import Project
    from .ProjectCategory import ProjectCategory
    from .Objective import Objective
    from .Unit import Unit
    from .Hour import Hour
    from .ClassroomLocation import ClassroomLocation
