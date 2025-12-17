# Osteopathy Education Scheduler

A Python-based scheduler for osteopathy education that manages lecturers, subjects, rooms, and student groups across a semester.
click on (base) danuta.paraficz@FFHS-Y6F4YKGH7H ~ % /Users/danuta.paraficz/PyProjects/planner_osteo/dist/PlannerAllInOne exec file in your finder, this will open terminal editor
## Features

- **Priority-based Scheduling**: Prioritizes the top 5 lecturers and respects their availability calendars
- **Pattern-Based Availability**: NEW! Reduces 150+ manual entries to ~10 pattern definitions (see [PATTERN_AVAILABILITY_GUIDE.md](PATTERN_AVAILABILITY_GUIDE.md))
- **Interactive CLI Wizard**: User-friendly input builder with pattern toggle interface
- **Flexible Room Assignment**: Auto-generates 10 theory rooms + 1 practical room (no manual room input needed)
- **Spread Subjects**: Distributes certain subjects evenly across the semester for better learning retention
- **Practical Subject Mixing**: Mixes practical subjects across the semester to ensure variety
- **Conflict Resolution**: Automatically prevents scheduling conflicts for lecturers, rooms, and student groups
- **Comprehensive Visualizations**: Input data plots, room/group/lecturer calendars, weekly overviews, utilization heatmaps
- **Detailed Statistics**: Provides comprehensive scheduling statistics and utilization reports
- **Standalone Apps**: PyInstaller macOS binaries for non-technical users

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

## Quick Start

### All-in-One App (Recommended)
```bash
python3 app_cli.py
# or double-click: start_all_in_one.command
```

Menu options:
1. **Edit input (wizard)** - Interactive pattern builder for lecturer availability
2. **Validate input** - Check data integrity
3. **Run scheduler** - Generate optimized schedule
4. **Visualize input data** - See subjects, lecturers, constraints
5. **Visualize schedule** - Room/group/lecturer calendars + weekly overviews

### Command Line Usage

**Edit input data:**
```bash
python3 user_input_cli.py
# or: ./start_wizard.command
```

**Run scheduler only:**
```bash
python3 main.py
```

**Visualize:**
```bash
python3 visualize_input_data.py  # Input plots
python3 visualize_schedule.py     # Schedule calendars
```

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

## Key New Features

### Pattern-Based Availability (🆕)
Dramatically simplifies lecturer availability input:
- **Old way**: 150+ manual entries per lecturer
- **New way**: ~10 pattern definitions

See [PATTERN_AVAILABILITY_GUIDE.md](PATTERN_AVAILABILITY_GUIDE.md) for complete guide.

**Example:**
```json
"availability": {
  "patterns": [{"weeks": "1-15", "days": {"Mon": ["morning", "afternoon"], "Wed": ["morning"]}}],
  "exceptions": [{"week": 7, "day": "Mon", "remove": ["afternoon"]}],
  "blackouts": [{"from_week": 13, "to_week": 13, "days": []}]
}
```

Interactive CLI with toggle interface:
```
  slot> all
    Day       Morning Afternoon
    Mon         ✓         ✓
    Tue         ✓         ✓
```

## Project Structure

```
planner_osteo/
├── README.md                       # This file
├── PATTERN_AVAILABILITY_GUIDE.md   # NEW: Complete pattern guide
├── IMPLEMENTATION_SUMMARY.md       # Technical documentation
├── main.py                         # Scheduler entry point
├── app_cli.py                      # All-in-one menu app
├── user_input_cli.py              # Interactive wizard with pattern builder
├── models.py                       # Data models
├── scheduler.py                    # Scheduling algorithm
├── data_loader.py                  # JSON loader with pattern expansion
├── validate_input.py               # Input validation
├── visualize_input_data.py         # Input visualizations
├── visualize_schedule.py           # Schedule visualizations
├── test_pattern_availability.py    # Pattern tests
├── demo_pattern_availability.py    # Demo and conversion tool
├── input_data.json                 # Input data
├── schedule_output.txt            # Generated schedule
├── images/                         # Visualization outputs
│   ├── input/                     # Input data plots
│   └── schedule/                  # Schedule calendars
└── dist/                          # Standalone macOS apps
    ├── PlannerAllInOne
    └── PlannerInputWizard
```

## Requirements

- Python 3.6 or higher
- No external dependencies

## License

This project is part of the osteopathy education planning system.
