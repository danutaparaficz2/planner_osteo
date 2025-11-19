# Usage Guide - Osteopathy Education Scheduler

## Quick Start

```bash
# Run the scheduler with default sample data
python3 main.py

# Run tests
python3 test_scheduler.py

# Verify all requirements
python3 verify_requirements.py
```

## Understanding the Output

### Console Output

When you run `main.py`, you'll see:

1. **Data Summary**: Overview of lecturers, subjects, rooms, and groups
2. **Scheduling Progress**: Which lecturers and subjects are being scheduled
3. **Statistics**: Blocks per subject, blocks per lecturer, room utilization

### Generated Files

- **schedule_output.txt**: Detailed week-by-week schedule showing:
  - Each week (1-15)
  - Each day (Monday-Friday)
  - Each time slot (morning/afternoon)
  - Subject, lecturer, student group, and room assignments

## Key Features Demonstrated

### 1. Priority Lecturer Scheduling

The top 5 lecturers (Priority 1-5) are scheduled first using their availability calendars:
- Dr. Smith (Priority 1) - Anatomy
- Dr. Johnson (Priority 2) - Physiology
- Dr. Williams (Priority 3) - Pathology
- Dr. Brown (Priority 4) - Biomechanics
- Dr. Davis (Priority 5) - Neurology

### 2. Spread Subjects

Subjects marked as "spread" are distributed evenly across the semester:
- Anatomy (S1)
- Physiology (S2)
- Pathology (S3)
- Biomechanics (S4)
- Neurology (S5)
- Clinical Skills (S8)

Example: If a subject needs 20 blocks over 15 weeks, they're spaced approximately 0.75 weeks apart.

### 3. Practical Subjects

Four practical subjects (A, B, C, D) are mixed across the semester:
- Subject A: Practical A - Palpation
- Subject B: Practical B - Manipulation
- Subject C: Practical C - Assessment
- Subject D: Practical D - Treatment

All use the single practical room, with blocks mixed to provide variety.

### 4. Room Assignment

- **Theory Rooms**: 9 rooms available, automatically assigned to theory subjects
- **Practical Room**: 1 room shared by all practical subjects

## Customizing the Scheduler

### Modifying Data

Edit `sample_data.py` to customize:

```python
# Change lecturer availability
availability=generate_lecturer_availability(15, 0.8)  # 80% available

# Add/modify subjects
Subject(id="NEW", name="New Subject", blocks_required=10, 
        room_type=RoomType.THEORY, spread=True)

# Adjust semester length
scheduler = OsteopathyScheduler(..., semester_weeks=20)
```

### Adjusting Spread Algorithm

In `scheduler.py`, modify the `_schedule_spread_blocks` method:

```python
# Change the ideal gap calculation
ideal_gap = total_slots // (blocks_needed + 1)  # Adjust formula
```

## Common Use Cases

### 1. Generate a New Schedule with Different Seed

```python
import random
random.seed(123)  # Different seed = different schedule
```

### 2. Export Schedule to Different Format

Modify the `print_schedule` method in `scheduler.py` to output CSV, JSON, etc.

### 3. Analyze Room Utilization

```python
scheduler.print_statistics()  # Shows room utilization percentages
```

## Validation

The scheduler automatically:
- Prevents double-booking of lecturers
- Prevents double-booking of rooms
- Prevents double-booking of student groups
- Respects lecturer availability (for priority lecturers)
- Ensures practical subjects use practical rooms
- Ensures theory subjects use theory rooms

## Tips

1. **Increasing Schedule Density**: Add more subjects or increase blocks_required
2. **Reducing Conflicts**: Increase semester_weeks or add more rooms
3. **Testing Changes**: Run `test_scheduler.py` after modifications
4. **Debugging**: Add print statements in scheduler.py to trace decisions

## Example Schedule Snippet

```
WEEK 1
--------------------------------------------------------------------------------

  Monday:
    MORNING:
      - Subject: Neurology (S5)
        Lecturer: Dr. Davis
        Group: Group 4 - Advanced
        Room: Theory Room 1 (theory)

      - Subject: Practical A - Palpation (A)
        Lecturer: Dr. Jackson
        Group: Group 1 - Year 1
        Room: Practical Room (practical)
```

## Troubleshooting

### Not All Blocks Scheduled

- Check lecturer availability (may be too restrictive)
- Increase semester length
- Add more rooms

### Poor Spread Distribution

- Adjust the ideal_gap calculation
- Ensure spread=True is set on subjects
- Increase semester length

### Practical Room Conflicts

- The single practical room limits scheduling
- Consider reducing practical subject block requirements
- Or spread blocks over more weeks
