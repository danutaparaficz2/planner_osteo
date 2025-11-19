"""
Osteopathy Planner Package

A scheduler for osteopathy courses managing lecturers, subjects, rooms, and student groups.
"""

from .scheduler import (
    Lecturer,
    Subject,
    Room,
    StudentGroup,
    TimeSlot,
    ScheduledBlock,
    Scheduler,
)

__version__ = "1.0.0"
__all__ = [
    "Lecturer",
    "Subject",
    "Room",
    "StudentGroup",
    "TimeSlot",
    "ScheduledBlock",
    "Scheduler",
]
