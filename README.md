# Osteopathy Education Scheduler

A Python-based scheduler for osteopathy education that manages lecturers, subjects, rooms, and student groups across a semester.

## Features

- **Priority-based Scheduling**: Prioritizes the top 5 lecturers and respects their availability calendars
- **Flexible Room Assignment**: Automatically assigns theory rooms (9 available) and manages a single practical room
- **Spread Subjects**: Distributes certain subjects evenly across the semester for better learning retention
- **Practical Subject Mixing**: Mixes practical subjects (A, B, C, D) across the semester to ensure variety
- **Conflict Resolution**: Automatically prevents scheduling conflicts for lecturers, rooms, and student groups
- **Detailed Statistics**: Provides comprehensive scheduling statistics and utilization reports

## Problem Specification

The scheduler handles:
- Up to 5 student groups with subject assignments
- 20 lecturers (each teaches one subject)
- 15 subjects with varying block requirements
- 10 rooms (9 theory rooms + 1 practical room)
- Each block is a half-day (morning or afternoon)
- Semester spans 15 weeks

## Installation

No external dependencies required. Uses Python 3 standard library only.

```bash
# Clone the repository
git clone https://github.com/danutaparaficz2/planner_osteo.git
cd planner_osteo

# Run the scheduler
python3 main.py
```

## Usage

### Running the Scheduler

```bash
python3 main.py
```

This will:
1. Generate sample data (lecturers, subjects, rooms, groups)
2. Create an optimized schedule
3. Display scheduling statistics
4. Save detailed schedule to `schedule_output.txt`

### Output

The scheduler produces:
- **Console output**: Summary statistics and scheduling progress
- **schedule_output.txt**: Detailed week-by-week schedule with all assignments

### Example Output

```
SCHEDULING STATISTICS
Blocks scheduled per subject:
  Anatomy (S1): 40/20 blocks
    Average gap: 0.4 weeks (spread subject)
  Physiology (S2): 30/15 blocks
    Average gap: 0.5 weeks (spread subject)
  ...

Blocks per lecturer:
  Dr. Smith (Priority 1): 40 blocks
  Dr. Johnson (Priority 2): 30 blocks
  ...

Room utilization:
  Theory Room 1 (theory): 130 blocks (86.7% utilization)
  Practical Room (practical): 66 blocks (44.0% utilization)
  ...
```

## Architecture

### Core Components

- **models.py**: Data models for all entities (Lecturer, Subject, Room, StudentGroup, Schedule, etc.)
- **scheduler.py**: Main scheduling algorithm with priority-based allocation
- **sample_data.py**: Sample data generator for testing
- **main.py**: Entry point and execution script

### Scheduling Algorithm

1. **Priority Phase**: Schedule top 5 priority lecturers first, respecting their availability calendars
2. **Spread Distribution**: For subjects marked as "spread", distribute blocks evenly across the semester
3. **Practical Mixing**: Mix practical subjects (A, B, C, D) across the semester using the single practical room
4. **Remaining Subjects**: Schedule any remaining subjects in available slots
5. **Conflict Prevention**: Ensure no lecturer, room, or student group double-booking

## Customization

### Modifying Sample Data

Edit `sample_data.py` to customize:
- Number and priority of lecturers
- Subject definitions and block requirements
- Room configurations
- Student group assignments
- Lecturer availability patterns

### Adjusting Scheduler Behavior

Edit `scheduler.py` to modify:
- Spreading algorithm (adjust gap calculations)
- Practical subject mixing strategy
- Priority weighting
- Room assignment logic

## Project Structure

```
planner_osteo/
├── README.md           # This file
├── main.py            # Entry point
├── models.py          # Data models
├── scheduler.py       # Scheduling algorithm
├── sample_data.py     # Sample data generator
└── schedule_output.txt # Generated schedule (created on run)
```

## Requirements

- Python 3.6 or higher
- No external dependencies

## License

This project is part of the osteopathy education planning system.