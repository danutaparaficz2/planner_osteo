"""
Data loader utility to load scheduling data from JSON file.
"""
import json
from typing import Tuple, List
from models import Lecturer, Subject, Room, StudentGroup, TimeSlot, RoomType


def load_from_json(filename: str = 'input_data.json') -> Tuple[List[Lecturer], List[Subject], List[Room], List[StudentGroup], int]:
    """
    Load all scheduling data from JSON file.
    
    Args:
        filename: Path to the JSON input file
        
    Returns:
        Tuple of (lecturers, subjects, rooms, student_groups, semester_weeks)
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    
    # Load subjects
    subjects = []
    for s in data['subjects']:
        subjects.append(Subject(
            id=s['id'],
            name=s['name'],
            blocks_required=s['blocks_required'],
            room_type=RoomType.THEORY if s['room_type'] == 'theory' else RoomType.PRACTICAL,
            spread=s['spread']
        ))
    
    # Load lecturers
    lecturers = []
    for l in data['lecturers']:
        # Convert availability from list to set of tuples
        availability = set()
        for avail in l['availability']:
            week, day, timeslot = avail
            timeslot_enum = TimeSlot.MORNING if timeslot == 'morning' else TimeSlot.AFTERNOON
            availability.add((week, day, timeslot_enum))
        
        lecturers.append(Lecturer(
            id=l['id'],
            name=l['name'],
            subject_id=l['subject_id'],
            priority=l['priority'],
            availability=availability
        ))
    
    # Load rooms
    rooms = []
    for r in data['rooms']:
        rooms.append(Room(
            id=r['id'],
            name=r['name'],
            room_type=RoomType.THEORY if r['room_type'] == 'theory' else RoomType.PRACTICAL,
            capacity=r['capacity']
        ))
    
    # Load student groups
    student_groups = []
    for g in data['student_groups']:
        student_groups.append(StudentGroup(
            id=g['id'],
            name=g['name'],
            subject_ids=g['subject_ids']
        ))
    
    # Get configuration
    semester_weeks = data['configuration']['weeks']
    
    return lecturers, subjects, rooms, student_groups, semester_weeks


def print_data_summary(lecturers: List[Lecturer], subjects: List[Subject], 
                      rooms: List[Room], student_groups: List[StudentGroup]):
    """Print a summary of the loaded data"""
    print("=" * 80)
    print("DATA SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal Lecturers: {len(lecturers)}")
    priority_lecturers = [l for l in lecturers if l.priority <= 5]
    print(f"Priority Lecturers (1-5): {len(priority_lecturers)}")
    
    print(f"\nTotal Subjects: {len(subjects)}")
    theory_subjects = [s for s in subjects if s.room_type == RoomType.THEORY]
    practical_subjects = [s for s in subjects if s.room_type == RoomType.PRACTICAL]
    spread_subjects = [s for s in subjects if s.spread]
    print(f"  Theory: {len(theory_subjects)}")
    print(f"  Practical: {len(practical_subjects)}")
    print(f"  Spread subjects: {len(spread_subjects)}")
    
    total_blocks = sum(s.blocks_required for s in subjects)
    print(f"\nTotal blocks needed across all subjects: {total_blocks}")
    
    print(f"\nTotal Rooms: {len(rooms)}")
    print(f"  Theory rooms: {len([r for r in rooms if r.room_type == RoomType.THEORY])}")
    print(f"  Practical rooms: {len([r for r in rooms if r.room_type == RoomType.PRACTICAL])}")
    
    print(f"\nTotal Student Groups: {len(student_groups)}")
    for group in student_groups:
        print(f"  {group.name}: {len(group.subject_ids)} subjects")
    
    print("\nTop 5 Priority Lecturers:")
    for lecturer in sorted(priority_lecturers, key=lambda x: x.priority)[:5]:
        subject = next((s for s in subjects if s.id == lecturer.subject_id), None)
        availability_count = len(lecturer.availability) if lecturer.availability else 0
        print(f"  Priority {lecturer.priority}: {lecturer.name} - {subject.name if subject else 'Unknown'} ({availability_count} available slots)")
    
    print("=" * 80)
