# Quick Start Guide

This guide will help you get started with the Osteopathy Scheduler quickly.

## Running the Example

The easiest way to see the scheduler in action is to run the provided example:

```bash
python example_usage.py
```

This will:
1. Create 15 subjects, 15 lecturers, 10 rooms, and 5 student groups
2. Set up availability calendars for the top 5 lecturers
3. Run the scheduler for a 3-month semester
4. Display a complete schedule with all scheduled blocks

## Understanding the Output

The scheduler output includes:

### Schedule Summary
- Total blocks scheduled
- Number of subjects, lecturers, rooms, and student groups involved

### Blocks by Subject
Shows how many blocks were scheduled for each subject vs. how many were required.

### Detailed Schedule
Day-by-day breakdown showing:
- Date and day of week
- Time slot (morning or afternoon)
- Subject being taught
- Lecturer teaching
- Student group attending
- Room assigned
- Block number (e.g., Block 3/10 means the 3rd block out of 10 required)

## Creating Your Own Schedule

Here's a minimal example to create your own schedule:

```python
from datetime import date, timedelta
from scheduler import Lecturer, Subject, Room, StudentGroup, Scheduler, TimeSlot

# 1. Create your data
lecturer = Lecturer(id=1, name="Dr. Smith", subject_id=1, importance=10)
subject = Subject(id=1, name="Anatomy", required_blocks=5)
room = Room(id=1, name="Room A", capacity=30)
group = StudentGroup(id=1, name="Group A", size=25)

# 2. Set lecturer availability
start_date = date(2024, 9, 1)
for day_offset in range(10):  # 10 days
    day = start_date + timedelta(days=day_offset)
    lecturer.add_availability(day, TimeSlot.MORNING)
    lecturer.add_availability(day, TimeSlot.AFTERNOON)

# 3. Create and run scheduler
scheduler = Scheduler(
    lecturers=[lecturer],
    subjects=[subject],
    rooms=[room],
    student_groups=[group],
    semester_start=date(2024, 9, 1),
    semester_end=date(2024, 9, 30)
)

schedule = scheduler.schedule_subjects()

# 4. View the schedule
scheduler.print_schedule()
```

## Key Concepts

### Importance Ranking
Lecturers have an importance value (higher = more important). The scheduler automatically selects the 5 most important lecturers.

### Availability Calendars
Each lecturer has an availability calendar showing which days and time slots they are available. The scheduler only schedules sessions when the lecturer is available.

### Half-Day Blocks
All sessions are half-day blocks (either morning or afternoon). Each subject requires a specific number of blocks.

### Automatic Room Assignment
The scheduler automatically assigns any available theory room. All rooms have sufficient capacity.

### Conflict Prevention
The scheduler ensures no double-booking:
- Each room can only be used once per time slot
- Each lecturer can only teach once per time slot
- Each student group can only attend one session per time slot

## Running Tests

To verify everything is working correctly:

```bash
python test_scheduler.py
```

All tests should pass with green checkmarks (✓).

## Tips

1. **Set realistic availability**: Make sure lecturers have enough available time slots to schedule all their required blocks.

2. **Balance workload**: Distribute availability across multiple days to avoid scheduling too many blocks on the same day.

3. **Monitor warnings**: The scheduler will warn you if it cannot schedule all required blocks for a subject.

4. **Start simple**: Begin with a small schedule (fewer lecturers, subjects, and blocks) and gradually increase complexity.

## Troubleshooting

**Problem**: Not all blocks are being scheduled

**Solution**: Check that:
- Lecturers have enough availability
- There are enough rooms
- The semester is long enough for all required blocks
- Student groups aren't over-scheduled

**Problem**: ValueError about multiple lecturers per subject

**Solution**: Ensure each subject has exactly one lecturer assigned to it.

## Next Steps

- Customize the example in `example_usage.py` with your own data
- Adjust availability patterns to match real lecturer schedules
- Modify the number of blocks per subject based on your curriculum
- Export the schedule to a file or database for further use
