"""
Osteopathy Scheduler

This module implements a scheduler for osteopathy courses that:
- Manages up to 5 student groups, 20 lecturers, 15 subjects, and 10 rooms
- Each lecturer teaches only one subject
- Each subject has up to 50 blocks (half-day sessions: morning or afternoon)
- Prioritizes top 5 most important lecturers, then schedules remaining lecturers
- Ensures each lecturer has stable/consistent days of the week
- Uses lecturer availability calendars
- Distributes subjects across the semester
- Assigns theory rooms
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from enum import Enum
from datetime import date, datetime, timedelta


class TimeSlot(Enum):
    """Half-day time slots"""
    MORNING = "morning"
    AFTERNOON = "afternoon"


@dataclass
class Lecturer:
    """Represents a lecturer"""
    id: int
    name: str
    subject_id: int  # Each lecturer teaches only one subject
    importance: int  # Higher number = more important
    availability: Dict[date, Set[TimeSlot]] = field(default_factory=dict)
    preferred_days: Set[int] = field(default_factory=set)  # Set of weekday numbers (0=Monday, 6=Sunday)
    
    def is_available(self, day: date, time_slot: TimeSlot) -> bool:
        """Check if lecturer is available on a specific day and time slot"""
        if day not in self.availability:
            return False
        return time_slot in self.availability[day]
    
    def add_availability(self, day: date, time_slot: TimeSlot):
        """Add availability for a specific day and time slot"""
        if day not in self.availability:
            self.availability[day] = set()
        self.availability[day].add(time_slot)
    
    def add_preferred_day(self, weekday: int):
        """
        Add a preferred day of the week for this lecturer
        
        Args:
            weekday: Day of week (0=Monday, 1=Tuesday, ..., 6=Sunday)
        """
        if not 0 <= weekday <= 6:
            raise ValueError(f"Weekday must be 0-6, got {weekday}")
        self.preferred_days.add(weekday)
    
    def is_preferred_day(self, day: date) -> bool:
        """Check if a date falls on one of the lecturer's preferred days"""
        if not self.preferred_days:
            return True  # If no preferences set, all days are acceptable
        return day.weekday() in self.preferred_days


@dataclass
class Subject:
    """Represents a subject/course"""
    id: int
    name: str
    required_blocks: int  # Number of half-day blocks needed (up to 50)
    
    def __post_init__(self):
        if self.required_blocks > 50:
            raise ValueError(f"Subject {self.name} has {self.required_blocks} blocks, maximum is 50")


@dataclass
class Room:
    """Represents a theory room"""
    id: int
    name: str
    capacity: int  # All rooms have sufficient capacity
    

@dataclass
class StudentGroup:
    """Represents a student group"""
    id: int
    name: str
    size: int


@dataclass
class ScheduledBlock:
    """Represents a scheduled block"""
    subject_id: int
    lecturer_id: int
    room_id: int
    student_group_id: int
    day: date
    time_slot: TimeSlot
    block_number: int  # Which block of the subject this is (1 to required_blocks)


class Scheduler:
    """
    Main scheduler class that schedules subjects for all lecturers.
    Prioritizes top 5 most important lecturers, then schedules remaining lecturers.
    Ensures each lecturer has stable/consistent days of the week.
    """
    
    def __init__(
        self,
        lecturers: List[Lecturer],
        subjects: List[Subject],
        rooms: List[Room],
        student_groups: List[StudentGroup],
        semester_start: date,
        semester_end: date
    ):
        """
        Initialize the scheduler
        
        Args:
            lecturers: List of up to 20 lecturers
            subjects: List of up to 15 subjects
            rooms: List of up to 10 theory rooms
            student_groups: List of up to 5 student groups
            semester_start: Start date of the semester
            semester_end: End date of the semester
        """
        if len(lecturers) > 20:
            raise ValueError(f"Maximum 20 lecturers allowed, got {len(lecturers)}")
        if len(subjects) > 15:
            raise ValueError(f"Maximum 15 subjects allowed, got {len(subjects)}")
        if len(rooms) > 10:
            raise ValueError(f"Maximum 10 rooms allowed, got {len(rooms)}")
        if len(student_groups) > 5:
            raise ValueError(f"Maximum 5 student groups allowed, got {len(student_groups)}")
        
        self.lecturers = lecturers
        self.subjects = {s.id: s for s in subjects}
        self.rooms = rooms
        self.student_groups = student_groups
        self.semester_start = semester_start
        self.semester_end = semester_end
        self.schedule: List[ScheduledBlock] = []
        
        # Create lecturer lookup by subject
        self.lecturers_by_subject: Dict[int, Lecturer] = {}
        for lecturer in lecturers:
            if lecturer.subject_id in self.lecturers_by_subject:
                raise ValueError(
                    f"Multiple lecturers assigned to subject {lecturer.subject_id}. "
                    f"Each subject should have only one lecturer."
                )
            self.lecturers_by_subject[lecturer.subject_id] = lecturer
    
    def get_top_lecturers(self, count: int = 5) -> List[Lecturer]:
        """
        Get the top N most important lecturers
        
        Args:
            count: Number of top lecturers to select (default 5)
            
        Returns:
            List of top lecturers sorted by importance (descending)
        """
        sorted_lecturers = sorted(self.lecturers, key=lambda l: l.importance, reverse=True)
        return sorted_lecturers[:min(count, len(sorted_lecturers))]
    
    def get_available_days(self) -> List[date]:
        """
        Get all days in the semester
        
        Returns:
            List of dates from semester start to end
        """
        days = []
        current_day = self.semester_start
        while current_day <= self.semester_end:
            days.append(current_day)
            current_day += timedelta(days=1)
        return days
    
    def is_room_available(self, room_id: int, day: date, time_slot: TimeSlot) -> bool:
        """
        Check if a room is available at a specific time
        
        Args:
            room_id: Room ID to check
            day: Date to check
            time_slot: Time slot to check
            
        Returns:
            True if room is available, False otherwise
        """
        for block in self.schedule:
            if (block.room_id == room_id and 
                block.day == day and 
                block.time_slot == time_slot):
                return False
        return True
    
    def is_student_group_available(
        self, 
        student_group_id: int, 
        day: date, 
        time_slot: TimeSlot
    ) -> bool:
        """
        Check if a student group is available at a specific time
        
        Args:
            student_group_id: Student group ID to check
            day: Date to check
            time_slot: Time slot to check
            
        Returns:
            True if student group is available, False otherwise
        """
        for block in self.schedule:
            if (block.student_group_id == student_group_id and 
                block.day == day and 
                block.time_slot == time_slot):
                return False
        return True
    
    def find_available_room(self, day: date, time_slot: TimeSlot) -> Optional[int]:
        """
        Find an available theory room for a specific time
        
        Args:
            day: Date to check
            time_slot: Time slot to check
            
        Returns:
            Room ID if available, None otherwise
        """
        for room in self.rooms:
            if self.is_room_available(room.id, day, time_slot):
                return room.id
        return None
    
    def assign_preferred_days_to_lecturers(self):
        """
        Assign preferred days of the week to lecturers to ensure day stability.
        
        Top lecturers get first choice of days. Each lecturer is assigned 1-2
        consistent days per week based on their availability.
        """
        # Sort lecturers by importance
        sorted_lecturers = sorted(self.lecturers, key=lambda l: l.importance, reverse=True)
        
        # Track which weekdays are already heavily used
        weekday_usage = {i: 0 for i in range(7)}
        
        for lecturer in sorted_lecturers:
            # Analyze which weekdays the lecturer is most available
            weekday_availability = {i: 0 for i in range(7)}
            
            for day, time_slots in lecturer.availability.items():
                weekday = day.weekday()
                weekday_availability[weekday] += len(time_slots)
            
            # Sort weekdays by lecturer's availability and current usage
            available_weekdays = [
                (wd, count) for wd, count in weekday_availability.items() if count > 0
            ]
            
            if not available_weekdays:
                continue
            
            # Sort by availability (descending) and usage (ascending)
            available_weekdays.sort(key=lambda x: (x[1], -weekday_usage[x[0]]), reverse=True)
            
            # Assign top 1-2 weekdays as preferred days
            num_preferred = min(2, len(available_weekdays))
            for i in range(num_preferred):
                weekday = available_weekdays[i][0]
                lecturer.add_preferred_day(weekday)
                weekday_usage[weekday] += 1
    
    def schedule_subjects(self) -> List[ScheduledBlock]:
        """
        Schedule subjects for all lecturers, prioritizing top lecturers.
        Ensures each lecturer has stable days of the week.
        
        Returns:
            List of scheduled blocks
        """
        self.schedule = []
        
        # Assign preferred days to all lecturers for day stability
        self.assign_preferred_days_to_lecturers()
        
        # Get top 5 lecturers first
        top_lecturers = self.get_top_lecturers(5)
        
        # Get remaining lecturers
        top_lecturer_ids = {l.id for l in top_lecturers}
        remaining_lecturers = [l for l in self.lecturers if l.id not in top_lecturer_ids]
        remaining_lecturers.sort(key=lambda l: l.importance, reverse=True)
        
        # Schedule in order: top lecturers first, then remaining by importance
        all_lecturers_ordered = top_lecturers + remaining_lecturers
        
        if not all_lecturers_ordered:
            return self.schedule
        
        # Get all available days in semester
        semester_days = self.get_available_days()
        
        # Schedule each lecturer's subject
        for lecturer in all_lecturers_ordered:
            subject = self.subjects.get(lecturer.subject_id)
            if not subject:
                continue
            
            blocks_scheduled = 0
            
            # First pass: try to schedule on preferred days only
            for day in semester_days:
                if blocks_scheduled >= subject.required_blocks:
                    break
                
                # Skip if not a preferred day
                if not lecturer.is_preferred_day(day):
                    continue
                
                # Try both time slots for this day
                for time_slot in [TimeSlot.MORNING, TimeSlot.AFTERNOON]:
                    if blocks_scheduled >= subject.required_blocks:
                        break
                    
                    # Check if lecturer is available
                    if not lecturer.is_available(day, time_slot):
                        continue
                    
                    # Try to schedule for each student group
                    for student_group in self.student_groups:
                        if blocks_scheduled >= subject.required_blocks:
                            break
                        
                        # Check if student group is available
                        if not self.is_student_group_available(
                            student_group.id, day, time_slot
                        ):
                            continue
                        
                        # Find available room
                        room_id = self.find_available_room(day, time_slot)
                        if room_id is None:
                            continue
                        
                        # Create scheduled block
                        scheduled_block = ScheduledBlock(
                            subject_id=subject.id,
                            lecturer_id=lecturer.id,
                            room_id=room_id,
                            student_group_id=student_group.id,
                            day=day,
                            time_slot=time_slot,
                            block_number=blocks_scheduled + 1
                        )
                        
                        self.schedule.append(scheduled_block)
                        blocks_scheduled += 1
            
            # Second pass: if not all blocks scheduled, try any available day
            if blocks_scheduled < subject.required_blocks:
                for day in semester_days:
                    if blocks_scheduled >= subject.required_blocks:
                        break
                    
                    # Skip preferred days (already tried)
                    if lecturer.is_preferred_day(day):
                        continue
                    
                    # Try both time slots for this day
                    for time_slot in [TimeSlot.MORNING, TimeSlot.AFTERNOON]:
                        if blocks_scheduled >= subject.required_blocks:
                            break
                        
                        # Check if lecturer is available
                        if not lecturer.is_available(day, time_slot):
                            continue
                        
                        # Try to schedule for each student group
                        for student_group in self.student_groups:
                            if blocks_scheduled >= subject.required_blocks:
                                break
                            
                            # Check if student group is available
                            if not self.is_student_group_available(
                                student_group.id, day, time_slot
                            ):
                                continue
                            
                            # Find available room
                            room_id = self.find_available_room(day, time_slot)
                            if room_id is None:
                                continue
                            
                            # Create scheduled block
                            scheduled_block = ScheduledBlock(
                                subject_id=subject.id,
                                lecturer_id=lecturer.id,
                                room_id=room_id,
                                student_group_id=student_group.id,
                                day=day,
                                time_slot=time_slot,
                                block_number=blocks_scheduled + 1
                            )
                            
                            self.schedule.append(scheduled_block)
                            blocks_scheduled += 1
            
            # Log if not all blocks were scheduled
            if blocks_scheduled < subject.required_blocks:
                print(
                    f"Warning: Only scheduled {blocks_scheduled} of {subject.required_blocks} "
                    f"blocks for subject {subject.name} (lecturer: {lecturer.name})"
                )
        
        return self.schedule
    
    def get_schedule_summary(self) -> Dict:
        """
        Get a summary of the schedule
        
        Returns:
            Dictionary with schedule statistics
        """
        summary = {
            "total_blocks_scheduled": len(self.schedule),
            "subjects_scheduled": len(set(block.subject_id for block in self.schedule)),
            "lecturers_used": len(set(block.lecturer_id for block in self.schedule)),
            "rooms_used": len(set(block.room_id for block in self.schedule)),
            "student_groups_involved": len(set(block.student_group_id for block in self.schedule)),
            "blocks_by_subject": {}
        }
        
        # Count blocks per subject
        for block in self.schedule:
            subject_id = block.subject_id
            if subject_id not in summary["blocks_by_subject"]:
                subject = self.subjects[subject_id]
                summary["blocks_by_subject"][subject_id] = {
                    "subject_name": subject.name,
                    "blocks_scheduled": 0,
                    "blocks_required": subject.required_blocks
                }
            summary["blocks_by_subject"][subject_id]["blocks_scheduled"] += 1
        
        return summary
    
    def print_schedule(self):
        """Print the schedule in a readable format"""
        if not self.schedule:
            print("No blocks scheduled.")
            return
        
        print("\n" + "="*80)
        print("SCHEDULE SUMMARY")
        print("="*80)
        
        summary = self.get_schedule_summary()
        print(f"\nTotal blocks scheduled: {summary['total_blocks_scheduled']}")
        print(f"Subjects scheduled: {summary['subjects_scheduled']}")
        print(f"Lecturers used: {summary['lecturers_used']}")
        print(f"Rooms used: {summary['rooms_used']}")
        print(f"Student groups involved: {summary['student_groups_involved']}")
        
        print("\n" + "-"*80)
        print("BLOCKS BY SUBJECT")
        print("-"*80)
        
        for subject_id, info in summary["blocks_by_subject"].items():
            print(
                f"{info['subject_name']}: "
                f"{info['blocks_scheduled']}/{info['blocks_required']} blocks scheduled"
            )
        
        print("\n" + "-"*80)
        print("DETAILED SCHEDULE")
        print("-"*80)
        
        # Sort schedule by date and time slot
        sorted_schedule = sorted(
            self.schedule, 
            key=lambda b: (b.day, b.time_slot.value, b.subject_id)
        )
        
        current_day = None
        for block in sorted_schedule:
            # Print date header if it's a new day
            if block.day != current_day:
                current_day = block.day
                print(f"\n{block.day.strftime('%Y-%m-%d (%A)')}")
            
            subject = self.subjects[block.subject_id]
            lecturer = next(l for l in self.lecturers if l.id == block.lecturer_id)
            room = next(r for r in self.rooms if r.id == block.room_id)
            student_group = next(sg for sg in self.student_groups if sg.id == block.student_group_id)
            
            print(
                f"  {block.time_slot.value.upper():10} | "
                f"Subject: {subject.name:20} | "
                f"Lecturer: {lecturer.name:15} | "
                f"Group: {student_group.name:10} | "
                f"Room: {room.name:10} | "
                f"Block {block.block_number}/{subject.required_blocks}"
            )
        
        print("\n" + "="*80 + "\n")
