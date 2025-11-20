"""
Sample data generator for the osteopathy scheduler.
Creates realistic test data based on the problem requirements.
"""
from models import Lecturer, Subject, Room, StudentGroup, TimeSlot, RoomType
from typing import List, Set, Tuple
import random


def generate_lecturer_availability(weeks: int, availability_percentage: float = 0.7) -> Set[Tuple[int, int, TimeSlot]]:
    """
    Generate availability calendar for a lecturer.
    Returns a set of (week, day, timeslot) tuples where lecturer is available.
    """
    availability = set()
    
    for week in range(weeks):
        for day in range(1, 6):  # Monday-Friday
            for timeslot in [TimeSlot.MORNING, TimeSlot.AFTERNOON]:
                # Randomly make lecturer available based on percentage
                if random.random() < availability_percentage:
                    availability.add((week, day, timeslot))
    
    return availability


def create_sample_data() -> tuple:
    """
    Create sample data for the scheduler based on problem requirements:
    - 5 student groups
    - 20 lecturers
    - 15 subjects
    - 10 rooms (9 theory + 1 practical)
    """
    
    # Create 15 subjects (11 theory + 4 practical A,B,C,D)
    subjects = [
        # Theory subjects with varying block requirements
        Subject(id="S1", name="Anatomy", blocks_required=20, room_type=RoomType.THEORY, spread=True),
        Subject(id="S2", name="Physiology", blocks_required=15, room_type=RoomType.THEORY, spread=True),
        Subject(id="S3", name="Pathology", blocks_required=18, room_type=RoomType.THEORY, spread=True),
        Subject(id="S4", name="Biomechanics", blocks_required=12, room_type=RoomType.THEORY, spread=True),
        Subject(id="S5", name="Neurology", blocks_required=14, room_type=RoomType.THEORY, spread=True),
        Subject(id="S6", name="Pharmacology", blocks_required=10, room_type=RoomType.THEORY, spread=False),
        Subject(id="S7", name="Radiology", blocks_required=8, room_type=RoomType.THEORY, spread=False),
        Subject(id="S8", name="Clinical Skills", blocks_required=16, room_type=RoomType.THEORY, spread=True),
        Subject(id="S9", name="Ethics", blocks_required=6, room_type=RoomType.THEORY, spread=False),
        Subject(id="S10", name="Research Methods", blocks_required=8, room_type=RoomType.THEORY, spread=False),
        Subject(id="S11", name="Case Studies", blocks_required=10, room_type=RoomType.THEORY, spread=False),
        
        # Practical subjects A, B, C, D
        Subject(id="A", name="Practical A - Palpation", blocks_required=12, room_type=RoomType.PRACTICAL, spread=False),
        Subject(id="B", name="Practical B - Manipulation", blocks_required=12, room_type=RoomType.PRACTICAL, spread=False),
        Subject(id="C", name="Practical C - Assessment", blocks_required=10, room_type=RoomType.PRACTICAL, spread=False),
        Subject(id="D", name="Practical D - Treatment", blocks_required=10, room_type=RoomType.PRACTICAL, spread=False),
    ]
    
    # Create 20 lecturers (each teaches one subject)
    # Priority 1-5 are the most important lecturers with full availability calendars
    lecturers = []
    
    # Top 5 priority lecturers with availability calendars
    lecturers.append(Lecturer(
        id="L1", name="Dr. Smith", subject_id="S1", priority=1,
        availability=generate_lecturer_availability(15, 0.8)
    ))
    lecturers.append(Lecturer(
        id="L2", name="Dr. Johnson", subject_id="S2", priority=2,
        availability=generate_lecturer_availability(15, 0.75)
    ))
    lecturers.append(Lecturer(
        id="L3", name="Dr. Williams", subject_id="S3", priority=3,
        availability=generate_lecturer_availability(15, 0.7)
    ))
    lecturers.append(Lecturer(
        id="L4", name="Dr. Brown", subject_id="S4", priority=4,
        availability=generate_lecturer_availability(15, 0.75)
    ))
    lecturers.append(Lecturer(
        id="L5", name="Dr. Davis", subject_id="S5", priority=5,
        availability=generate_lecturer_availability(15, 0.8)
    ))
    
    # Remaining 15 lecturers (lower priority, assumed always available)
    lecturers.append(Lecturer(id="L6", name="Dr. Miller", subject_id="S6", priority=6, availability=set()))
    lecturers.append(Lecturer(id="L7", name="Dr. Wilson", subject_id="S7", priority=7, availability=set()))
    lecturers.append(Lecturer(id="L8", name="Dr. Moore", subject_id="S8", priority=8, availability=set()))
    lecturers.append(Lecturer(id="L9", name="Dr. Taylor", subject_id="S9", priority=9, availability=set()))
    lecturers.append(Lecturer(id="L10", name="Dr. Anderson", subject_id="S10", priority=10, availability=set()))
    lecturers.append(Lecturer(id="L11", name="Dr. Thomas", subject_id="S11", priority=11, availability=set()))
    lecturers.append(Lecturer(id="L12", name="Dr. Jackson", subject_id="A", priority=12, availability=set()))
    lecturers.append(Lecturer(id="L13", name="Dr. White", subject_id="B", priority=13, availability=set()))
    lecturers.append(Lecturer(id="L14", name="Dr. Harris", subject_id="C", priority=14, availability=set()))
    lecturers.append(Lecturer(id="L15", name="Dr. Martin", subject_id="D", priority=15, availability=set()))
    
    # Add duplicate subjects for some lecturers if needed (to reach 20 lecturers)
    lecturers.append(Lecturer(id="L16", name="Dr. Thompson", subject_id="S1", priority=16, availability=set()))
    lecturers.append(Lecturer(id="L17", name="Dr. Garcia", subject_id="S2", priority=17, availability=set()))
    lecturers.append(Lecturer(id="L18", name="Dr. Martinez", subject_id="S3", priority=18, availability=set()))
    lecturers.append(Lecturer(id="L19", name="Dr. Robinson", subject_id="S4", priority=19, availability=set()))
    lecturers.append(Lecturer(id="L20", name="Dr. Clark", subject_id="S5", priority=20, availability=set()))
    
    # Create 10 rooms (9 theory + 1 practical)
    rooms = [
        Room(id="R1", name="Theory Room 1", room_type=RoomType.THEORY, capacity=30),
        Room(id="R2", name="Theory Room 2", room_type=RoomType.THEORY, capacity=30),
        Room(id="R3", name="Theory Room 3", room_type=RoomType.THEORY, capacity=30),
        Room(id="R4", name="Theory Room 4", room_type=RoomType.THEORY, capacity=30),
        Room(id="R5", name="Theory Room 5", room_type=RoomType.THEORY, capacity=30),
        Room(id="R6", name="Theory Room 6", room_type=RoomType.THEORY, capacity=30),
        Room(id="R7", name="Theory Room 7", room_type=RoomType.THEORY, capacity=30),
        Room(id="R8", name="Theory Room 8", room_type=RoomType.THEORY, capacity=30),
        Room(id="R9", name="Theory Room 9", room_type=RoomType.THEORY, capacity=30),
        Room(id="RP1", name="Practical Room", room_type=RoomType.PRACTICAL, capacity=20),
    ]
    
    # Create 5 student groups with subject assignments
    student_groups = [
        StudentGroup(
            id="G1", 
            name="Group 1 - Year 1",
            subject_ids=["S1", "S2", "S6", "S9", "A"]  # Mixed theory and practical
        ),
        StudentGroup(
            id="G2",
            name="Group 2 - Year 2", 
            subject_ids=["S3", "S4", "S7", "S10", "B"]
        ),
        StudentGroup(
            id="G3",
            name="Group 3 - Year 3",
            subject_ids=["S5", "S8", "S11", "C"]
        ),
        StudentGroup(
            id="G4",
            name="Group 4 - Advanced",
            subject_ids=["S1", "S3", "S5", "D"]
        ),
        StudentGroup(
            id="G5",
            name="Group 5 - Foundation",
            subject_ids=["S2", "S4", "S6", "S8", "A", "C"]
        ),
    ]
    
    return lecturers, subjects, rooms, student_groups


def print_data_summary(lecturers, subjects, rooms, student_groups):
    """Print a summary of the generated data"""
    print("=" * 80)
    print("SAMPLE DATA SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal Lecturers: {len(lecturers)}")
    print(f"Priority Lecturers (1-5): {len([l for l in lecturers if l.priority <= 5])}")
    
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
    for lecturer in sorted(lecturers, key=lambda x: x.priority)[:5]:
        subject = next((s for s in subjects if s.id == lecturer.subject_id), None)
        availability_count = len(lecturer.availability) if lecturer.availability else 0
        print(f"  Priority {lecturer.priority}: {lecturer.name} - {subject.name if subject else 'Unknown'} ({availability_count} available slots)")
    
    print("=" * 80)
