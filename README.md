# Osteopathy Planner

A Python-based scheduler for osteopathy courses that manages lecturers, subjects, rooms, and student groups.

## Features

- Manages up to **5 student groups**, **20 lecturers**, **15 subjects**, and **10 rooms**
- Each lecturer teaches only one subject
- Each subject can have up to **50 blocks** (half-day sessions)
- Selects the **5 most important lecturers** based on importance ranking
- Uses lecturer **availability calendars** to schedule sessions
- Distributes subjects across the semester
- Schedules all required blocks in available half-day slots (morning or afternoon)
- Automatically assigns available theory rooms

## Installation

This is a standalone Python module. No external dependencies are required (uses only Python standard library).

```bash
git clone https://github.com/danutaparaficz2/planner_osteo.git
cd planner_osteo
```

## Usage

### Basic Example

```python
from datetime import date, timedelta
from scheduler import Lecturer, Subject, Room, StudentGroup, Scheduler, TimeSlot

# Create lecturers
lecturers = [
    Lecturer(1, "Dr. Smith", subject_id=1, importance=10),
    Lecturer(2, "Dr. Johnson", subject_id=2, importance=9),
    # ... more lecturers
]

# Create subjects
subjects = [
    Subject(1, "Anatomy Fundamentals", required_blocks=10),
    Subject(2, "Osteopathic Principles", required_blocks=12),
    # ... more subjects
]

# Create rooms
rooms = [
    Room(1, "Room A", capacity=30),
    Room(2, "Room B", capacity=30),
    # ... more rooms
]

# Create student groups
student_groups = [
    StudentGroup(1, "Group A", size=25),
    StudentGroup(2, "Group B", size=28),
    # ... more groups
]

# Set lecturer availability
for lecturer in lecturers:
    # Add availability for specific dates and time slots
    lecturer.add_availability(date(2024, 9, 1), TimeSlot.MORNING)
    lecturer.add_availability(date(2024, 9, 1), TimeSlot.AFTERNOON)
    # ... add more availability

# Create scheduler
scheduler = Scheduler(
    lecturers=lecturers,
    subjects=subjects,
    rooms=rooms,
    student_groups=student_groups,
    semester_start=date(2024, 9, 1),
    semester_end=date(2024, 11, 30)
)

# Run scheduler for top 5 lecturers
schedule = scheduler.schedule_subjects()

# Print the schedule
scheduler.print_schedule()
```

### Running the Example

A complete working example is provided in `example_usage.py`:

```bash
python example_usage.py
```

This will:
1. Create sample data (lecturers, subjects, rooms, student groups)
2. Set up availability calendars for the top 5 lecturers
3. Run the scheduler
4. Display a detailed schedule with all scheduled blocks

## Data Models

### Lecturer
- `id`: Unique identifier
- `name`: Lecturer name
- `subject_id`: The subject they teach (one subject per lecturer)
- `importance`: Importance ranking (higher = more important)
- `availability`: Dictionary mapping dates to available time slots

### Subject
- `id`: Unique identifier
- `name`: Subject name
- `required_blocks`: Number of half-day blocks needed (max 50)

### Room
- `id`: Unique identifier
- `name`: Room name
- `capacity`: Room capacity (all rooms have sufficient capacity)

### StudentGroup
- `id`: Unique identifier
- `name`: Group name
- `size`: Number of students

### TimeSlot
- `MORNING`: Morning session
- `AFTERNOON`: Afternoon session

### ScheduledBlock
- `subject_id`: Subject being taught
- `lecturer_id`: Lecturer teaching
- `room_id`: Room assigned
- `student_group_id`: Student group attending
- `day`: Date of the session
- `time_slot`: Morning or afternoon
- `block_number`: Block number within the subject (1 to required_blocks)

## Algorithm

The scheduler works as follows:

1. **Select Top 5 Lecturers**: Identifies the 5 most important lecturers based on their importance ranking
2. **Iterate Through Semester**: Goes through each day in the semester
3. **Check Lecturer Availability**: For each lecturer and time slot, checks if they are available
4. **Check Student Group Availability**: Ensures the student group is not already scheduled
5. **Find Available Room**: Assigns any free theory room
6. **Create Schedule**: Creates a scheduled block if all conditions are met
7. **Repeat**: Continues until all required blocks are scheduled or no more slots are available

## Constraints

- Maximum 5 student groups
- Maximum 20 lecturers
- Maximum 15 subjects
- Maximum 10 rooms
- Maximum 50 blocks per subject
- Each lecturer teaches exactly one subject
- Half-day blocks (morning or afternoon only)
- No double-booking of rooms, lecturers, or student groups

## Output

The scheduler provides:

- **Schedule Summary**: Total blocks scheduled, subjects, lecturers, rooms, and student groups involved
- **Blocks by Subject**: How many blocks were scheduled for each subject vs. required
- **Detailed Schedule**: Day-by-day breakdown with date, time slot, subject, lecturer, group, room, and block number

## License

MIT