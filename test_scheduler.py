"""
Tests for the Osteopathy Scheduler

This module contains basic tests to verify the scheduler functionality.
"""

from datetime import date, timedelta
from scheduler import (
    Lecturer, Subject, Room, StudentGroup, Scheduler, TimeSlot
)


def test_lecturer_creation():
    """Test creating a lecturer"""
    lecturer = Lecturer(1, "Dr. Test", 1, 10)
    assert lecturer.id == 1
    assert lecturer.name == "Dr. Test"
    assert lecturer.subject_id == 1
    assert lecturer.importance == 10
    print("✓ Lecturer creation test passed")


def test_subject_creation():
    """Test creating a subject"""
    subject = Subject(1, "Test Subject", 10)
    assert subject.id == 1
    assert subject.name == "Test Subject"
    assert subject.required_blocks == 10
    print("✓ Subject creation test passed")


def test_subject_max_blocks():
    """Test subject max blocks constraint"""
    try:
        Subject(1, "Too Many Blocks", 51)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "maximum is 50" in str(e)
    print("✓ Subject max blocks constraint test passed")


def test_room_creation():
    """Test creating a room"""
    room = Room(1, "Room A", 30)
    assert room.id == 1
    assert room.name == "Room A"
    assert room.capacity == 30
    print("✓ Room creation test passed")


def test_student_group_creation():
    """Test creating a student group"""
    group = StudentGroup(1, "Group A", 25)
    assert group.id == 1
    assert group.name == "Group A"
    assert group.size == 25
    print("✓ Student group creation test passed")


def test_lecturer_availability():
    """Test lecturer availability management"""
    lecturer = Lecturer(1, "Dr. Test", 1, 10)
    test_date = date(2024, 9, 1)
    
    # Initially not available
    assert not lecturer.is_available(test_date, TimeSlot.MORNING)
    
    # Add availability
    lecturer.add_availability(test_date, TimeSlot.MORNING)
    assert lecturer.is_available(test_date, TimeSlot.MORNING)
    assert not lecturer.is_available(test_date, TimeSlot.AFTERNOON)
    
    # Add afternoon availability
    lecturer.add_availability(test_date, TimeSlot.AFTERNOON)
    assert lecturer.is_available(test_date, TimeSlot.AFTERNOON)
    print("✓ Lecturer availability test passed")


def test_scheduler_constraints():
    """Test scheduler constraint validation"""
    subjects = [Subject(i, f"Subject {i}", 10) for i in range(1, 16)]
    rooms = [Room(i, f"Room {i}", 30) for i in range(1, 11)]
    groups = [StudentGroup(i, f"Group {i}", 25) for i in range(1, 6)]
    
    # Test max lecturers constraint
    try:
        lecturers = [Lecturer(i, f"Dr. {i}", i % 15 + 1, 10) for i in range(1, 22)]
        Scheduler(lecturers, subjects, rooms, groups, date(2024, 9, 1), date(2024, 11, 30))
        assert False, "Should have raised ValueError for too many lecturers"
    except ValueError as e:
        assert "Maximum 20 lecturers" in str(e)
    
    # Test max subjects constraint
    try:
        lecturers = [Lecturer(i, f"Dr. {i}", i, 10) for i in range(1, 11)]
        too_many_subjects = [Subject(i, f"Subject {i}", 10) for i in range(1, 17)]
        Scheduler(lecturers, too_many_subjects, rooms, groups, date(2024, 9, 1), date(2024, 11, 30))
        assert False, "Should have raised ValueError for too many subjects"
    except ValueError as e:
        assert "Maximum 15 subjects" in str(e)
    
    # Test max rooms constraint
    try:
        lecturers = [Lecturer(i, f"Dr. {i}", i, 10) for i in range(1, 11)]
        too_many_rooms = [Room(i, f"Room {i}", 30) for i in range(1, 12)]
        Scheduler(lecturers, subjects, too_many_rooms, groups, date(2024, 9, 1), date(2024, 11, 30))
        assert False, "Should have raised ValueError for too many rooms"
    except ValueError as e:
        assert "Maximum 10 rooms" in str(e)
    
    # Test max groups constraint
    try:
        lecturers = [Lecturer(i, f"Dr. {i}", i, 10) for i in range(1, 11)]
        too_many_groups = [StudentGroup(i, f"Group {i}", 25) for i in range(1, 7)]
        Scheduler(lecturers, subjects, rooms, too_many_groups, date(2024, 9, 1), date(2024, 11, 30))
        assert False, "Should have raised ValueError for too many groups"
    except ValueError as e:
        assert "Maximum 5 student groups" in str(e)
    
    print("✓ Scheduler constraints test passed")


def test_top_lecturers_selection():
    """Test selection of top 5 lecturers"""
    lecturers = [
        Lecturer(1, "Dr. A", 1, 10),
        Lecturer(2, "Dr. B", 2, 5),
        Lecturer(3, "Dr. C", 3, 8),
        Lecturer(4, "Dr. D", 4, 3),
        Lecturer(5, "Dr. E", 5, 9),
        Lecturer(6, "Dr. F", 6, 1),
        Lecturer(7, "Dr. G", 7, 7),
    ]
    
    subjects = [Subject(i, f"Subject {i}", 10) for i in range(1, 8)]
    rooms = [Room(i, f"Room {i}", 30) for i in range(1, 6)]
    groups = [StudentGroup(i, f"Group {i}", 25) for i in range(1, 3)]
    
    scheduler = Scheduler(
        lecturers, subjects, rooms, groups,
        date(2024, 9, 1), date(2024, 11, 30)
    )
    
    top_5 = scheduler.get_top_lecturers(5)
    
    assert len(top_5) == 5
    assert top_5[0].name == "Dr. A"  # importance 10
    assert top_5[1].name == "Dr. E"  # importance 9
    assert top_5[2].name == "Dr. C"  # importance 8
    assert top_5[3].name == "Dr. G"  # importance 7
    assert top_5[4].name == "Dr. B"  # importance 5
    
    print("✓ Top lecturers selection test passed")


def test_simple_scheduling():
    """Test basic scheduling functionality"""
    # Create minimal setup
    lecturers = [
        Lecturer(1, "Dr. A", 1, 10),
        Lecturer(2, "Dr. B", 2, 5),
    ]
    
    subjects = [
        Subject(1, "Subject 1", 2),
        Subject(2, "Subject 2", 3),
    ]
    
    rooms = [Room(1, "Room A", 30)]
    groups = [StudentGroup(1, "Group A", 25)]
    
    start_date = date(2024, 9, 2)  # Monday
    end_date = date(2024, 9, 6)    # Friday
    
    # Add availability for lecturers
    for day_offset in range(5):
        day = start_date + timedelta(days=day_offset)
        lecturers[0].add_availability(day, TimeSlot.MORNING)
        lecturers[0].add_availability(day, TimeSlot.AFTERNOON)
        lecturers[1].add_availability(day, TimeSlot.MORNING)
    
    scheduler = Scheduler(lecturers, subjects, rooms, groups, start_date, end_date)
    schedule = scheduler.schedule_subjects()
    
    # Should schedule some blocks
    assert len(schedule) > 0
    
    # Should schedule subject 1 (top lecturer)
    subject_1_blocks = [b for b in schedule if b.subject_id == 1]
    assert len(subject_1_blocks) == 2  # All required blocks
    
    print("✓ Simple scheduling test passed")


def test_room_availability():
    """Test that rooms are not double-booked"""
    lecturers = [
        Lecturer(1, "Dr. A", 1, 10),
        Lecturer(2, "Dr. B", 2, 9),
    ]
    
    subjects = [
        Subject(1, "Subject 1", 2),
        Subject(2, "Subject 2", 2),
    ]
    
    rooms = [Room(1, "Room A", 30)]
    groups = [
        StudentGroup(1, "Group A", 25),
        StudentGroup(2, "Group B", 25),
    ]
    
    start_date = date(2024, 9, 2)
    end_date = date(2024, 9, 3)
    
    # Both lecturers available same time
    for lecturer in lecturers:
        lecturer.add_availability(start_date, TimeSlot.MORNING)
        lecturer.add_availability(start_date, TimeSlot.AFTERNOON)
    
    scheduler = Scheduler(lecturers, subjects, rooms, groups, start_date, end_date)
    schedule = scheduler.schedule_subjects()
    
    # Check no room double-booking
    time_slots_used = set()
    for block in schedule:
        key = (block.day, block.time_slot, block.room_id)
        assert key not in time_slots_used, "Room double-booked!"
        time_slots_used.add(key)
    
    print("✓ Room availability test passed")


def test_student_group_availability():
    """Test that student groups are not double-booked"""
    lecturers = [
        Lecturer(1, "Dr. A", 1, 10),
        Lecturer(2, "Dr. B", 2, 9),
    ]
    
    subjects = [
        Subject(1, "Subject 1", 2),
        Subject(2, "Subject 2", 2),
    ]
    
    rooms = [
        Room(1, "Room A", 30),
        Room(2, "Room B", 30),
    ]
    groups = [StudentGroup(1, "Group A", 25)]
    
    start_date = date(2024, 9, 2)
    end_date = date(2024, 9, 3)
    
    # Both lecturers available same time
    for lecturer in lecturers:
        lecturer.add_availability(start_date, TimeSlot.MORNING)
        lecturer.add_availability(start_date, TimeSlot.AFTERNOON)
    
    scheduler = Scheduler(lecturers, subjects, rooms, groups, start_date, end_date)
    schedule = scheduler.schedule_subjects()
    
    # Check no student group double-booking
    time_slots_used = set()
    for block in schedule:
        key = (block.day, block.time_slot, block.student_group_id)
        assert key not in time_slots_used, "Student group double-booked!"
        time_slots_used.add(key)
    
    print("✓ Student group availability test passed")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("RUNNING TESTS")
    print("="*60 + "\n")
    
    test_lecturer_creation()
    test_subject_creation()
    test_subject_max_blocks()
    test_room_creation()
    test_student_group_creation()
    test_lecturer_availability()
    test_scheduler_constraints()
    test_top_lecturers_selection()
    test_simple_scheduling()
    test_room_availability()
    test_student_group_availability()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
