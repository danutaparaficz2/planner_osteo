# Using input_data.json

The scheduler now uses `input_data.json` as the sole data source. This file contains all the information needed to generate a schedule.

## JSON Structure

### Subjects
```json
{
  "id": "S1",
  "name": "Anatomy",
  "blocks_required": 20,
  "room_type": "theory",  // "theory" or "practical"
  "spread": true          // true = distribute evenly across semester
}
```

### Lecturers
```json
{
  "id": "L1",
  "name": "Dr. Smith",
  "subject_id": "S1",
  "priority": 1,          // 1-5 are top priority
  "availability": [       // [week, day, timeslot] where week is 0-based
    [0, 1, "morning"],    // Week 0 (1st week), Monday, Morning
    [0, 1, "afternoon"],
    [1, 2, "morning"]     // Week 1 (2nd week), Tuesday, Morning
  ]
}
```
- **Priority 1-5**: Top priority lecturers - scheduler uses their availability calendar
- **Priority 6+**: Lower priority lecturers - assumed always available (empty availability array)
- **Week**: 0-based (0 = week 1, 1 = week 2, etc.)
- **Day**: 1-5 (Monday=1, Tuesday=2, Wednesday=3, Thursday=4, Friday=5)
- **Timeslot**: "morning" or "afternoon"

### Rooms
```json
{
  "id": "R1",
  "name": "Theory Room 1",
  "room_type": "theory",  // "theory" or "practical"
  "capacity": 30
}
```

### Student Groups
```json
{
  "id": "G1",
  "name": "Group 1 - Year 1",
  "subject_ids": ["S1", "S2", "S6", "S9", "A"]
}
```

### Configuration
```json
{
  "weeks": 15,
  "days_per_week": 5,
  "timeslots_per_day": 2,
  "timeslots": ["morning", "afternoon"]
}
```

## Running the Scheduler

Simply run:
```bash
python main.py
```

The scheduler will:
1. Load data from `input_data.json`
2. Create a schedule prioritizing top 5 lecturers
3. Save the output to `schedule_output.txt`

## Easiest Way: Interactive Input Wizard (Recommended)

Use the built-in interactive CLI to create or edit `input_data.json` without touching JSON manually:

```bash
python user_input_cli.py
```

What you can do:
- Add/edit/delete Subjects, Lecturers, Rooms, and Student Groups
- Edit configuration (weeks, days per week, timeslots per day)
- For priority lecturers (1-5), add availability slots interactively
- Validate inputs and save with automatic backup of the previous file

Tips:
- Press Enter to keep the shown default value
- IDs must be unique within their category (e.g., subjects)
- Room types: `theory` or `practical`
- Timeslots: `morning` or `afternoon`

## Validate Your Input

Run validation to catch mistakes (missing IDs, wrong references, out-of-range availability, etc.):

```bash
python validate_input.py
```

You will get a pass/fail report with specific issues, if any. The scheduler expects a valid file.

## macOS App (Optional)

You can build a standalone macOS app for the input wizard (no coding required for users):

```bash
chmod +x build_macos_apps.sh
./build_macos_apps.sh
```

Artifacts will appear in `dist/`:
- `PlannerInputWizard` (double-clickable binary). When launched from Finder, it opens in Terminal and runs the interactive wizard.

How to share:
- Zip the entire project folder (including `dist/PlannerInputWizard`) and share.
- Ask users to put `PlannerInputWizard` inside this project folder and double-click it. It reads/writes `input_data.json` next to itself.

Note: Gatekeeper may require right-click → Open on first run.

## Modifying the Input Data

To customize the schedule:

1. **Add/modify subjects**: Edit the `subjects` array
2. **Add/modify lecturers**: Edit the `lecturers` array
   - For top priority lecturers (1-5), specify their availability calendar
   - For lower priority lecturers, use empty availability array `[]`
3. **Add/modify rooms**: Edit the `rooms` array
4. **Add/modify groups**: Edit the `student_groups` array
5. **Change semester length**: Modify `configuration.weeks`

Alternatively, use the interactive wizard:

```bash
python user_input_cli.py
```

## Example: Adding a New Lecturer

```json
{
  "id": "L21",
  "name": "Dr. New",
  "subject_id": "S1",
  "priority": 21,
  "availability": []
}
```

## Example: Making a Lecturer High Priority

Change priority to 1-5 and add availability:
```json
{
  "id": "L6",
  "name": "Dr. Miller",
  "subject_id": "S6",
  "priority": 3,
  "availability": [
    [0, 1, "morning"],
    [0, 2, "afternoon"],
    [1, 1, "morning"]
  ]
}
```

## Visualization

After running the scheduler, generate visualizations:

### Input Data Visualization
```bash
python visualize_input_data.py
```
Creates plots showing subjects, lecturers, rooms, and constraints.

### Schedule Visualization
```bash
python visualize_schedule.py
```
Creates calendar views showing:
- Individual room schedules
- Individual student group schedules
- Weekly overviews
- Utilization heatmaps
