"""
Data models for the osteopathy education scheduler.
"""
from dataclasses import dataclass, field
from typing import List, Set, Optional
from enum import Enum


class TimeSlot(Enum):
    """Half-day time slots"""
    MORNING = "morning"
    AFTERNOON = "afternoon"


class RoomType(Enum):
    """Types of rooms available"""
    THEORY = "theory"
    PRACTICAL = "practical"


@dataclass
class StudentGroup:
    """Represents a student group"""
    id: str
    name: str
    subject_ids: List[str] = field(default_factory=list)
    
    def __repr__(self):
        return f"StudentGroup({self.id}: {self.name})"


@dataclass
class Room:
    """Represents a classroom or practical room"""
    id: str
    name: str
    room_type: RoomType
    capacity: int
    room_number: Optional[str] = None
    
    def __repr__(self):
        num = f" #{self.room_number}" if self.room_number else ""
        return f"Room({self.id}: {self.name}{num}, {self.room_type.value})"


@dataclass
class Lecturer:
    """Represents a lecturer"""
    id: str
    name: str
    subject_id: str
    priority: int  # Lower number = higher priority (1-5 are top priority)
    availability: Set[tuple] = field(default_factory=set)  # Set of (week, day, timeslot) tuples
    
    def is_available(self, week: int, day: int, timeslot: TimeSlot) -> bool:
        """Check if lecturer is available at given time"""
        return (week, day, timeslot) in self.availability
    
    def __repr__(self):
        return f"Lecturer({self.id}: {self.name}, Subject: {self.subject_id}, Priority: {self.priority})"


@dataclass
class Subject:
    """Represents a subject/course"""
    id: str
    name: str
    blocks_required: int  # Number of half-day blocks needed
    room_type: RoomType
    spread: bool = False  # Whether to spread blocks evenly across semester
    
    def __repr__(self):
        return f"Subject({self.id}: {self.name}, Blocks: {self.blocks_required}, Spread: {self.spread})"


@dataclass
class ScheduledBlock:
    """Represents a scheduled teaching block"""
    subject_id: str
    lecturer_id: str
    student_group_id: str
    room_id: str
    week: int
    day: int  # 1-5 (Monday-Friday)
    timeslot: TimeSlot
    room_number: Optional[str] = None
    
    def __repr__(self):
        return (f"ScheduledBlock(Week {self.week}, Day {self.day}, {self.timeslot.value}: "
                f"Subject={self.subject_id}, Lecturer={self.lecturer_id}, "
                f"Group={self.student_group_id}, Room={self.room_id})")
    
    def conflicts_with(self, other: 'ScheduledBlock') -> bool:
        """Check if this block conflicts with another block"""
        if self.week != other.week or self.day != other.day or self.timeslot != other.timeslot:
            return False
        
        # Conflict if same lecturer, room, or student group
        return (self.lecturer_id == other.lecturer_id or 
                self.room_id == other.room_id or 
                self.student_group_id == other.student_group_id)


@dataclass
class Schedule:
    """Represents the complete schedule"""
    blocks: List[ScheduledBlock] = field(default_factory=list)
    weeks: int = 15  # Semester length in weeks
    days_per_week: int = 5  # Monday-Friday
    
    def add_block(self, block: ScheduledBlock) -> bool:
        """Add a block to the schedule if no conflicts exist"""
        for existing_block in self.blocks:
            if block.conflicts_with(existing_block):
                return False
        self.blocks.append(block)
        return True
    
    def get_blocks_for_subject(self, subject_id: str) -> List[ScheduledBlock]:
        """Get all blocks scheduled for a subject"""
        return [b for b in self.blocks if b.subject_id == subject_id]
    
    def is_slot_available(self, week: int, day: int, timeslot: TimeSlot, 
                         lecturer_id: str, room_id: str, student_group_id: str) -> bool:
        """Check if a time slot is available for given lecturer, room, and group"""
        for block in self.blocks:
            if block.week == week and block.day == day and block.timeslot == timeslot:
                if (block.lecturer_id == lecturer_id or 
                    block.room_id == room_id or 
                    block.student_group_id == student_group_id):
                    return False
        return True
    
    def __repr__(self):
        return f"Schedule({len(self.blocks)} blocks scheduled)"
