#!/usr/bin/env python3
"""
Tests for the osteopathy education scheduler.
Validates that the scheduler meets all requirements.
"""
import random
from sample_data import create_sample_data
from scheduler import OsteopathyScheduler
from models import RoomType


def test_scheduler_basic():
    """Test basic scheduler functionality"""
    print("Test: Basic scheduler functionality")
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Create data
    lecturers, subjects, rooms, student_groups = create_sample_data()
    
    # Create scheduler
    scheduler = OsteopathyScheduler(
        lecturers=lecturers,
        subjects=subjects,
        rooms=rooms,
        student_groups=student_groups,
        semester_weeks=15
    )
    
    # Create schedule
    schedule = scheduler.create_schedule()
    
    # Verify blocks were scheduled
    assert len(schedule.blocks) > 0, "No blocks were scheduled"
    print(f"  ✓ Scheduled {len(schedule.blocks)} blocks")
    
    return True


def test_priority_lecturers():
    """Test that top 5 priority lecturers are scheduled"""
    print("Test: Priority lecturers are scheduled")
    
    random.seed(42)
    lecturers, subjects, rooms, student_groups = create_sample_data()
    
    scheduler = OsteopathyScheduler(
        lecturers=lecturers,
        subjects=subjects,
        rooms=rooms,
        student_groups=student_groups,
        semester_weeks=15
    )
    
    schedule = scheduler.create_schedule()
    
    # Check that priority lecturers (1-5) have blocks scheduled
    priority_lecturer_ids = [l.id for l in lecturers if l.priority <= 5]
    scheduled_lecturer_ids = set(block.lecturer_id for block in schedule.blocks)
    
    priority_scheduled = [lid for lid in priority_lecturer_ids if lid in scheduled_lecturer_ids]
    
    assert len(priority_scheduled) == 5, f"Expected 5 priority lecturers, got {len(priority_scheduled)}"
    print(f"  ✓ All 5 priority lecturers scheduled")
    
    return True


def test_practical_subjects():
    """Test that practical subjects A, B, C, D are scheduled"""
    print("Test: Practical subjects A, B, C, D are scheduled")
    
    random.seed(42)
    lecturers, subjects, rooms, student_groups = create_sample_data()
    
    scheduler = OsteopathyScheduler(
        lecturers=lecturers,
        subjects=subjects,
        rooms=rooms,
        student_groups=student_groups,
        semester_weeks=15
    )
    
    schedule = scheduler.create_schedule()
    
    # Check practical subjects are scheduled
    practical_subjects = ['A', 'B', 'C', 'D']
    scheduled_subjects = set(block.subject_id for block in schedule.blocks)
    
    for subj_id in practical_subjects:
        assert subj_id in scheduled_subjects, f"Practical subject {subj_id} not scheduled"
    
    print(f"  ✓ All practical subjects A, B, C, D scheduled")
    
    # Verify practical subjects use practical room
    practical_blocks = [b for b in schedule.blocks if b.subject_id in practical_subjects]
    practical_room_ids = [r.id for r in rooms if r.room_type == RoomType.PRACTICAL]
    
    for block in practical_blocks:
        assert block.room_id in practical_room_ids, f"Practical block using non-practical room"
    
    print(f"  ✓ Practical subjects use practical room")
    
    return True


def test_spread_subjects():
    """Test that spread subjects are distributed across semester"""
    print("Test: Spread subjects are distributed")
    
    random.seed(42)
    lecturers, subjects, rooms, student_groups = create_sample_data()
    
    scheduler = OsteopathyScheduler(
        lecturers=lecturers,
        subjects=subjects,
        rooms=rooms,
        student_groups=student_groups,
        semester_weeks=15
    )
    
    schedule = scheduler.create_schedule()
    
    # Find spread subjects
    spread_subject_ids = [s.id for s in subjects if s.spread]
    
    for subj_id in spread_subject_ids:
        blocks = [b for b in schedule.blocks if b.subject_id == subj_id]
        
        if len(blocks) > 1:
            # Check that blocks are not all in the same week
            weeks = [b.week for b in blocks]
            unique_weeks = set(weeks)
            
            # For spread subjects, we expect blocks in multiple weeks
            assert len(unique_weeks) > 1, f"Spread subject {subj_id} not spread across weeks"
    
    print(f"  ✓ Spread subjects distributed across multiple weeks")
    
    return True


def test_no_conflicts():
    """Test that there are no scheduling conflicts"""
    print("Test: No scheduling conflicts")
    
    random.seed(42)
    lecturers, subjects, rooms, student_groups = create_sample_data()
    
    scheduler = OsteopathyScheduler(
        lecturers=lecturers,
        subjects=subjects,
        rooms=rooms,
        student_groups=student_groups,
        semester_weeks=15
    )
    
    schedule = scheduler.create_schedule()
    
    # Check for conflicts
    for i, block1 in enumerate(schedule.blocks):
        for block2 in schedule.blocks[i+1:]:
            # If same time slot, check for conflicts
            if (block1.week == block2.week and 
                block1.day == block2.day and 
                block1.timeslot == block2.timeslot):
                
                # No lecturer, room, or group should be double-booked
                assert block1.lecturer_id != block2.lecturer_id, \
                    f"Lecturer conflict: {block1.lecturer_id}"
                assert block1.room_id != block2.room_id, \
                    f"Room conflict: {block1.room_id}"
                assert block1.student_group_id != block2.student_group_id, \
                    f"Student group conflict: {block1.student_group_id}"
    
    print(f"  ✓ No scheduling conflicts detected")
    
    return True


def test_theory_rooms():
    """Test that theory subjects use theory rooms"""
    print("Test: Theory subjects use theory rooms")
    
    random.seed(42)
    lecturers, subjects, rooms, student_groups = create_sample_data()
    
    scheduler = OsteopathyScheduler(
        lecturers=lecturers,
        subjects=subjects,
        rooms=rooms,
        student_groups=student_groups,
        semester_weeks=15
    )
    
    schedule = scheduler.create_schedule()
    
    # Find theory subjects
    theory_subject_ids = [s.id for s in subjects if s.room_type == RoomType.THEORY]
    theory_room_ids = [r.id for r in rooms if r.room_type == RoomType.THEORY]
    
    # Check that theory subjects use theory rooms
    theory_blocks = [b for b in schedule.blocks if b.subject_id in theory_subject_ids]
    
    for block in theory_blocks:
        assert block.room_id in theory_room_ids, \
            f"Theory block using non-theory room: {block.room_id}"
    
    print(f"  ✓ Theory subjects use theory rooms")
    
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 80)
    print("RUNNING SCHEDULER TESTS")
    print("=" * 80)
    print()
    
    tests = [
        test_scheduler_basic,
        test_priority_lecturers,
        test_practical_subjects,
        test_spread_subjects,
        test_no_conflicts,
        test_theory_rooms,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
                print(f"  ✗ Test failed")
        except AssertionError as e:
            failed += 1
            print(f"  ✗ Test failed: {e}")
        except Exception as e:
            failed += 1
            print(f"  ✗ Test error: {e}")
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
