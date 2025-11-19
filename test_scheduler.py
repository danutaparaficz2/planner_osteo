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


def test_lecturer_preferred_days():
    """Test lecturer preferred day management"""
    lecturer = Lecturer(1, "Dr. Test", 1, 10)
    
    # Initially no preferred days
    assert len(lecturer.preferred_days) == 0
    
    # All days should be acceptable when no preferences set
    assert lecturer.is_preferred_day(date(2024, 9, 2))  # Monday
    assert lecturer.is_preferred_day(date(2024, 9, 6))  # Friday
    
    # Add Monday as preferred day
    lecturer.add_preferred_day(0)  # Monday
    assert 0 in lecturer.preferred_days
    
    # Check preferred day detection
    assert lecturer.is_preferred_day(date(2024, 9, 2))  # Monday
    assert not lecturer.is_preferred_day(date(2024, 9, 3))  # Tuesday
    
    # Add Wednesday
    lecturer.add_preferred_day(2)  # Wednesday
    assert lecturer.is_preferred_day(date(2024, 9, 4))  # Wednesday
    
    print("✓ Lecturer preferred days test passed")


def test_day_stability_assignment():
    """Test that lecturers are assigned stable days of the week"""
    lecturers = [
        Lecturer(1, "Dr. A", 1, 10),
        Lecturer(2, "Dr. B", 2, 8),
        Lecturer(3, "Dr. C", 3, 6),
    ]
    
    subjects = [Subject(i, f"Subject {i}", 5) for i in range(1, 4)]
    rooms = [Room(i, f"Room {i}", 30) for i in range(1, 3)]
    groups = [StudentGroup(1, "Group A", 25)]
    
    start_date = date(2024, 9, 2)  # Monday
    end_date = date(2024, 9, 27)   # Friday (4 weeks)
    
    # Add availability for all weekdays
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Weekdays only
            for lecturer in lecturers:
                lecturer.add_availability(current, TimeSlot.MORNING)
                lecturer.add_availability(current, TimeSlot.AFTERNOON)
        current += timedelta(days=1)
    
    scheduler = Scheduler(lecturers, subjects, rooms, groups, start_date, end_date)
    
    # Assign preferred days
    scheduler.assign_preferred_days_to_lecturers()
    
    # All lecturers should have preferred days assigned
    for lecturer in lecturers:
        assert len(lecturer.preferred_days) > 0
        assert len(lecturer.preferred_days) <= 2
    
    print("✓ Day stability assignment test passed")


def test_schedule_respects_preferred_days():
    """Test that scheduling respects lecturer preferred days"""
    lecturers = [
        Lecturer(1, "Dr. A", 1, 10),
        Lecturer(2, "Dr. B", 2, 8),
    ]
    
    subjects = [
        Subject(1, "Subject 1", 6),
        Subject(2, "Subject 2", 6),
    ]
    
    rooms = [Room(1, "Room A", 30)]
    groups = [StudentGroup(1, "Group A", 25)]
    
    start_date = date(2024, 9, 2)  # Monday
    end_date = date(2024, 9, 27)   # Friday (4 weeks)
    
    # Add availability for all weekdays
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Weekdays only
            for lecturer in lecturers:
                lecturer.add_availability(current, TimeSlot.MORNING)
                lecturer.add_availability(current, TimeSlot.AFTERNOON)
        current += timedelta(days=1)
    
    scheduler = Scheduler(lecturers, subjects, rooms, groups, start_date, end_date)
    schedule = scheduler.schedule_subjects()
    
    # Check that each lecturer's blocks are mostly on their preferred days
    for lecturer in lecturers:
        lecturer_blocks = [b for b in schedule if b.lecturer_id == lecturer.id]
        if len(lecturer_blocks) > 0:
            # Count blocks on preferred days
            preferred_day_blocks = sum(
                1 for b in lecturer_blocks if lecturer.is_preferred_day(b.day)
            )
            
            # At least 70% of blocks should be on preferred days
            ratio = preferred_day_blocks / len(lecturer_blocks)
            assert ratio >= 0.7, (
                f"Lecturer {lecturer.name} has only {ratio:.0%} blocks on preferred days "
                f"({preferred_day_blocks}/{len(lecturer_blocks)})"
            )
    
    print("✓ Schedule respects preferred days test passed")


def test_all_lecturers_scheduled():
    """Test that all lecturers (not just top 5) get scheduled"""
    lecturers = [
        Lecturer(1, "Dr. A", 1, 10),  # Top 5
        Lecturer(2, "Dr. B", 2, 9),
        Lecturer(3, "Dr. C", 3, 8),
        Lecturer(4, "Dr. D", 4, 7),
        Lecturer(5, "Dr. E", 5, 6),
        Lecturer(6, "Dr. F", 6, 5),   # Not in top 5
        Lecturer(7, "Dr. G", 7, 4),
        Lecturer(8, "Dr. H", 8, 3),
    ]
    
    subjects = [Subject(i, f"Subject {i}", 3) for i in range(1, 9)]
    rooms = [Room(i, f"Room {i}", 30) for i in range(1, 5)]
    groups = [StudentGroup(i, f"Group {i}", 25) for i in range(1, 3)]
    
    start_date = date(2024, 9, 2)  # Monday
    end_date = date(2024, 10, 31)  # Long semester
    
    # Add availability for all weekdays
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:  # Weekdays only
            for lecturer in lecturers:
                lecturer.add_availability(current, TimeSlot.MORNING)
                lecturer.add_availability(current, TimeSlot.AFTERNOON)
        current += timedelta(days=1)
    
    scheduler = Scheduler(lecturers, subjects, rooms, groups, start_date, end_date)
    schedule = scheduler.schedule_subjects()
    
    # Check that more than 5 lecturers were scheduled
    scheduled_lecturer_ids = set(b.lecturer_id for b in schedule)
    assert len(scheduled_lecturer_ids) > 5, (
        f"Expected more than 5 lecturers scheduled, got {len(scheduled_lecturer_ids)}"
    )
    
    # Check that lower importance lecturers were also scheduled
    assert 6 in scheduled_lecturer_ids or 7 in scheduled_lecturer_ids, (
        "Lower importance lecturers were not scheduled"
    )
    
    print("✓ All lecturers scheduled test passed")


def test_top_lecturers_priority():
    """Test that top lecturers are scheduled before lower importance lecturers"""
    lecturers = [
        Lecturer(1, "Dr. A", 1, 10),  # Top
        Lecturer(2, "Dr. B", 2, 5),   # Lower
    ]
    
    subjects = [
        Subject(1, "Subject 1", 20),  # Many blocks needed
        Subject(2, "Subject 2", 20),
    ]
    
    rooms = [Room(1, "Room A", 30)]
    groups = [StudentGroup(1, "Group A", 25)]
    
    start_date = date(2024, 9, 2)
    end_date = date(2024, 9, 20)  # Limited time
    
    # Add limited availability
    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            for lecturer in lecturers:
                lecturer.add_availability(current, TimeSlot.MORNING)
        current += timedelta(days=1)
    
    scheduler = Scheduler(lecturers, subjects, rooms, groups, start_date, end_date)
    schedule = scheduler.schedule_subjects()
    
    # Count blocks for each lecturer
    lecturer_a_blocks = len([b for b in schedule if b.lecturer_id == 1])
    lecturer_b_blocks = len([b for b in schedule if b.lecturer_id == 2])
    
    # Top lecturer should get more or equal blocks scheduled
    assert lecturer_a_blocks >= lecturer_b_blocks, (
        f"Top lecturer should have priority: "
        f"Dr. A={lecturer_a_blocks}, Dr. B={lecturer_b_blocks}"
    )
    
    print("✓ Top lecturers priority test passed")


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
    test_lecturer_preferred_days()
    test_day_stability_assignment()
    test_schedule_respects_preferred_days()
    test_all_lecturers_scheduled()
    test_top_lecturers_priority()
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
