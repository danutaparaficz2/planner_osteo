# Pattern-Based Availability Guide

## Overview

The new pattern-based availability system dramatically simplifies lecturer availability input, reducing 150+ manual entries to just a few pattern definitions.

## Quick Comparison

### Old Format (Manual)
```json
"availability": [
  [1, 1, "morning"], [1, 1, "afternoon"],
  [1, 2, "morning"], [1, 2, "afternoon"],
  [1, 3, "morning"], [1, 3, "afternoon"],
  ... 144 more entries ...
]
```
**Problem**: Must manually enter every single week/day/slot combination.

### New Format (Pattern)
```json
"availability": {
  "patterns": [
    {
      "weeks": "1-15",
      "days": {
        "Mon": ["morning", "afternoon"],
        "Tue": ["morning", "afternoon"],
        "Wed": ["morning", "afternoon"],
        "Thu": ["morning", "afternoon"],
        "Fri": ["morning", "afternoon"]
      }
    }
  ],
  "exceptions": [],
  "blackouts": []
}
```
**Benefit**: One pattern definition replaces 150 manual entries!

## Schema Structure

### Patterns
Define recurring availability across week ranges:
```json
"patterns": [
  {
    "weeks": "1-8",      // Week range expression
    "days": {
      "Mon": ["morning", "afternoon"],
      "Tue": ["morning"],
      "Wed": [],         // Not available Wednesday
      "Thu": ["afternoon"],
      "Fri": ["morning"]
    }
  },
  {
    "weeks": "9-15",     // Mid-semester change
    "days": {
      "Mon": ["morning"],
      "Wed": ["morning", "afternoon"],
      "Fri": ["afternoon"]
    }
  }
]
```

**Week expressions support**:
- Single weeks: `"5"`, `"10"`
- Ranges: `"1-8"`, `"9-15"`
- Comma-separated: `"1-5,7,9-12"`

### Exceptions
Override specific week/day/slot combinations:
```json
"exceptions": [
  {"week": 7, "day": "Tue", "remove": ["afternoon"]},  // Not available
  {"week": 10, "day": "Fri", "add": ["afternoon"]}     // Extra availability
]
```

### Blackouts
Block out entire week ranges (vacations, conferences):
```json
"blackouts": [
  {"from_week": 7, "to_week": 7, "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]},
  {"from_week": 13, "to_week": 14, "days": []}  // Empty = all days
]
```

## Using the CLI Pattern Builder

### Launch the Wizard
```bash
python user_input_cli.py
# or
./start_wizard.command
```

### Add New Lecturer with Pattern
1. Choose: `4) Lecturers`
2. Choose: `1) Add lecturer`
3. Enter details (ID, name, subject, priority)
4. When asked about availability, choose **pattern builder** (recommended)
5. Interactive session:
   - **Week expression**: Enter range like `1-15`
   - **Toggle slots**: Commands like `mon m`, `tue a`, `wed both`, `all`, `show`, `done`
   - **Add exceptions**: Specific week/day overrides
   - **Add blackouts**: Vacation periods

### Edit Existing Lecturer
1. Choose: `4) Lecturers`
2. Choose: `2) Edit lecturer`
3. Select lecturer by ID
4. Choose to edit availability
5. Select **pattern builder** mode

### Convert All Lecturers (Batch)
1. Choose: `4) Lecturers`
2. Choose: `6) Convert availability format`
3. Automatically converts all list-based to pattern-based

### Build Pattern for Multiple Lecturers
1. Choose: `4) Lecturers`
2. Choose: `5) Build availability (patterns)`
3. Creates a pattern and applies to all priority lecturers

## Interactive Toggle Interface

```
Toggle slots. Commands: 'mon m', 'tue a', 'wed both', 'all', 'done', 'show'.
  slot> all
    Day       Morning Afternoon
    Mon         ✓         ✓
    Tue         ✓         ✓
    Wed         ✓         ✓
    Thu         ✓         ✓
    Fri         ✓         ✓
  slot> wed both
    Day       Morning Afternoon
    Mon         ✓         ✓
    Tue         ✓         ✓
    Wed         ·         ·
    Thu         ✓         ✓
    Fri         ✓         ✓
  slot> fri a
    Day       Morning Afternoon
    Mon         ✓         ✓
    Tue         ✓         ✓
    Wed         ·         ·
    Thu         ✓         ✓
    Fri         ✓         ·
  slot> done
```

**Commands**:
- `mon m` - Toggle Monday morning
- `tue a` - Toggle Tuesday afternoon
- `wed both` - Toggle both Wednesday slots
- `all` - Toggle all slots on
- `show` - Display current selection
- `done` - Finish pattern definition

## Common Use Cases

### Full-Time Lecturer
**Scenario**: Available all week, every week
```json
{
  "patterns": [{
    "weeks": "1-15",
    "days": {
      "Mon": ["morning", "afternoon"],
      "Tue": ["morning", "afternoon"],
      "Wed": ["morning", "afternoon"],
      "Thu": ["morning", "afternoon"],
      "Fri": ["morning", "afternoon"]
    }
  }]
}
```

### Part-Time Lecturer
**Scenario**: Only Mon/Wed/Fri mornings
```json
{
  "patterns": [{
    "weeks": "1-15",
    "days": {
      "Mon": ["morning"],
      "Wed": ["morning"],
      "Fri": ["morning"]
    }
  }]
}
```

### Mid-Semester Schedule Change
**Scenario**: Different availability first/second half
```json
{
  "patterns": [
    {
      "weeks": "1-8",
      "days": {
        "Mon": ["morning", "afternoon"],
        "Tue": ["morning"],
        "Thu": ["afternoon"]
      }
    },
    {
      "weeks": "9-15",
      "days": {
        "Wed": ["morning", "afternoon"],
        "Fri": ["morning"]
      }
    }
  ]
}
```

### Vacation Week
**Scenario**: Regular schedule except one week vacation
```json
{
  "patterns": [{
    "weeks": "1-15",
    "days": {
      "Mon": ["morning", "afternoon"],
      "Tue": ["morning", "afternoon"],
      "Wed": ["morning", "afternoon"],
      "Thu": ["morning", "afternoon"],
      "Fri": ["morning"]
    }
  }],
  "blackouts": [
    {"from_week": 7, "to_week": 7, "days": []}
  ]
}
```

### Conference + Exception
**Scenario**: Conference Thu/Fri week 5, but available extra Friday afternoon week 10
```json
{
  "patterns": [{
    "weeks": "1-15",
    "days": {
      "Mon": ["morning", "afternoon"],
      "Tue": ["morning", "afternoon"],
      "Wed": ["morning", "afternoon"],
      "Thu": ["morning", "afternoon"],
      "Fri": ["morning"]
    }
  }],
  "exceptions": [
    {"week": 10, "day": "Fri", "add": ["afternoon"]}
  ],
  "blackouts": [
    {"from_week": 5, "to_week": 5, "days": ["Thu", "Fri"]}
  ]
}
```

## Resolution Algorithm

When the scheduler loads availability:

1. **Start with empty set**
2. **Apply patterns sequentially** (later patterns extend availability)
3. **Process exceptions**:
   - Apply all `remove` operations first
   - Apply all `add` operations second
4. **Apply blackouts** (remove both morning/afternoon for specified days)

Result: Clean set of `(week, day, timeslot)` tuples used by scheduler.

## Backward Compatibility

The old list format still works:
```json
"availability": [[1, 1, "morning"], [1, 2, "afternoon"], ...]
```

**No migration required** - both formats are supported side-by-side in the same JSON file.

## Testing Your Patterns

### View Expanded Slots
```bash
python test_pattern_availability.py
```

### Validate Before Scheduling
```bash
python validate_input.py
# or use app menu option 2
```

### Run Demo
```bash
python demo_pattern_availability.py
```

## Benefits Summary

✅ **10x less typing**: 150+ entries → ~10 pattern definitions  
✅ **Easier to understand**: "Mon/Wed mornings" vs. 30 individual entries  
✅ **Mid-semester changes**: Add patterns instead of editing 75+ slots  
✅ **Vacation handling**: Blackout ranges instead of removing 10 individual slots  
✅ **Error reduction**: Toggle interface prevents typos  
✅ **Backward compatible**: Old format still works  
✅ **No scheduler changes**: Same internal representation

## Troubleshooting

**Q: Pattern not working as expected?**  
A: Run `python test_pattern_availability.py` to see exact slot expansion.

**Q: Need to see old format?**  
A: Check `input_data.json.bak` backup files.

**Q: Want to revert?**  
A: Use "Convert availability format" to batch convert back, or manually edit JSON.

**Q: Validation fails?**  
A: Run `python validate_input.py` for detailed error messages.

## Next Steps

1. Try the demo: `python demo_pattern_availability.py`
2. Launch wizard: `python user_input_cli.py`
3. Add a test lecturer with pattern builder
4. Validate: Option 2 in app menu
5. Run scheduler: Option 3 in app menu

For questions or issues, check `IMPLEMENTATION_SUMMARY.md` or `README.md`.
