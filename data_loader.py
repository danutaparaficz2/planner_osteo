"""
Data loader utility to load scheduling data from JSON file.

Enhanced to support a new, more concise lecturer availability schema:

Old (still supported for backward compatibility):
  "availability": [ [week, day, "morning"|"afternoon"], ... ]

New (patterns + overrides):
  "availability": {
      "patterns": [
          {
              "weeks": "1-15",          # ranges and comma lists e.g. "1-5,7,9-10"
              "days": {
                  "Mon": ["morning","afternoon"],
                  "Tue": ["morning"],
                  "Wed": [],
                  "Thu": ["afternoon"],
                  "Fri": ["morning"]
              }
          },
          {
              "weeks": "9-12",           # later patterns extend/override (add slots)
              "days": { "Wed": ["morning"] }
          }
      ],
      "exceptions": [                    # fine-grained adds/removes
          {"week": 7, "day": "Tue", "remove": ["afternoon"]},
          {"week": 10, "day": "Fri", "add": ["afternoon"]}
      ],
      "blackouts": [                     # bulk removals (vacations, conferences)
          {"from_week": 13, "to_week": 13, "days": ["Thu","Fri"]}
      ]
  }

Resolution order:
  1. Apply patterns sequentially (later patterns can extend availability).
  2. Apply exceptions (removes then adds).
  3. Apply blackouts (removes both slots for listed days unless slot-specific given later).

This produces the same internal representation: a set of (week, day_int, TimeSlot) tuples.
"""
import json
from typing import Tuple, List, Set, Dict
from models import Lecturer, Subject, Room, StudentGroup, TimeSlot, RoomType

DAY_NAME_TO_INT = {
    'Mon': 1, 'Monday': 1,
    'Tue': 2, 'Tuesday': 2,
    'Wed': 3, 'Wednesday': 3,
    'Thu': 4, 'Thursday': 4,
    'Fri': 5, 'Friday': 5,
}


def _parse_weeks_expr(expr: str, max_week: int) -> Set[int]:
    """Parse a weeks expression like '1-5,7,9-10' into a set of ints.

    Any week outside 1..max_week is ignored.
    Empty or invalid returns empty set.
    """
    weeks: Set[int] = set()
    if not expr:
        return weeks
    parts = [p.strip() for p in expr.split(',') if p.strip()]
    for part in parts:
        if '-' in part:
            a, b = part.split('-', 1)
            try:
                start = int(a)
                end = int(b)
            except ValueError:
                continue
            if start > end:
                start, end = end, start
            for w in range(start, end + 1):
                if 1 <= w <= max_week:
                    weeks.add(w)
        else:
            try:
                w = int(part)
            except ValueError:
                continue
            if 1 <= w <= max_week:
                weeks.add(w)
    return weeks


def _expand_availability(raw_availability, semester_weeks: int) -> Set[tuple]:
    """Expand lecturer availability from either old list form or new pattern schema.

    Returns a set of (week, day_int, TimeSlot) tuples.
    """
    availability: Set[tuple] = set()

    # Old format: list of triples
    if isinstance(raw_availability, list):
        for item in raw_availability:
            if not isinstance(item, (list, tuple)) or len(item) != 3:
                continue
            week, day, slot = item
            if not isinstance(week, int) or not isinstance(day, int):
                continue
            if week < 1 or week > semester_weeks or day < 1 or day > 5:
                continue
            timeslot_enum = TimeSlot.MORNING if slot == 'morning' else TimeSlot.AFTERNOON
            availability.add((week, day, timeslot_enum))
        return availability

    # New format: dict with patterns / exceptions / blackouts
    if not isinstance(raw_availability, dict):
        return availability  # empty / unknown format => no availability

    patterns = raw_availability.get('patterns', []) or []
    for pattern in patterns:
        if not isinstance(pattern, dict):
            continue
        week_expr = pattern.get('weeks', f'1-{semester_weeks}')
        weeks_set = _parse_weeks_expr(week_expr, semester_weeks)
        days_map: Dict[str, List[str]] = pattern.get('days', {}) or {}
        for day_name, slots in days_map.items():
            day_int = DAY_NAME_TO_INT.get(day_name.strip(), None)
            if not day_int:
                continue
            if not isinstance(slots, list):
                continue
            for slot in slots:
                ts = TimeSlot.MORNING if slot == 'morning' else TimeSlot.AFTERNOON
                for w in weeks_set:
                    availability.add((w, day_int, ts))

    # Exceptions: remove then add
    exceptions = raw_availability.get('exceptions', []) or []
    for exc in exceptions:
        if not isinstance(exc, dict):
            continue
        week = exc.get('week')
        day_name = exc.get('day')
        day_int = DAY_NAME_TO_INT.get(day_name, None)
        if not isinstance(week, int) or not day_int:
            continue
        # Removals
        for slot in exc.get('remove', []) or []:
            ts = TimeSlot.MORNING if slot == 'morning' else TimeSlot.AFTERNOON
            availability.discard((week, day_int, ts))
        # Additions
        for slot in exc.get('add', []) or []:
            ts = TimeSlot.MORNING if slot == 'morning' else TimeSlot.AFTERNOON
            if 1 <= week <= semester_weeks:
                availability.add((week, day_int, ts))

    # Blackouts: remove both slots for listed days in week range
    blackouts = raw_availability.get('blackouts', []) or []
    for blk in blackouts:
        if not isinstance(blk, dict):
            continue
        from_w = blk.get('from_week')
        to_w = blk.get('to_week')
        if isinstance(from_w, int) and isinstance(to_w, int):
            if from_w > to_w:
                from_w, to_w = to_w, from_w
            days_list = blk.get('days', []) or []
            day_ints = [DAY_NAME_TO_INT.get(d, None) for d in days_list]
            day_ints = [d for d in day_ints if d]
            if not day_ints:
                # If no days specified, assume all 5 days
                day_ints = [1, 2, 3, 4, 5]
            for w in range(from_w, to_w + 1):
                if 1 <= w <= semester_weeks:
                    for d in day_ints:
                        availability.discard((w, d, TimeSlot.MORNING))
                        availability.discard((w, d, TimeSlot.AFTERNOON))
        # date_range support could be added here if calendar dates are introduced

    return availability


def load_from_json(filename: str = 'input_data.json') -> Tuple[List[Lecturer], List[Subject], List[Room], List[StudentGroup], int]:
    """
    Load all scheduling data from JSON file.
    
    Args:
        filename: Path to the JSON input file
        
    Returns:
        Tuple of (lecturers, subjects, rooms, student_groups, semester_weeks)
    """
    with open(filename, 'r') as f:
        data = json.load(f)
    
    # Load subjects
    subjects = []
    for s in data['subjects']:
        subjects.append(Subject(
            id=s['id'],
            name=s['name'],
            blocks_required=s['blocks_required'],
            room_type=RoomType.THEORY if s['room_type'] == 'theory' else RoomType.PRACTICAL,
            spread=s['spread']
        ))
    
    # Load lecturers (supporting both old and new availability schema)
    lecturers = []
    for l in data['lecturers']:
        raw_avail = l.get('availability', [])
        availability = _expand_availability(raw_avail, data['configuration']['weeks'])
        
        lecturers.append(Lecturer(
            id=l['id'],
            name=l['name'],
            subject_id=l['subject_id'],
            priority=l['priority'],
            availability=availability
        ))
    
    # Create 10 default theory rooms with 50 capacity (always sufficient for any group)
    rooms = []
    for i in range(1, 11):
        rooms.append(Room(
            id=f'T{i}',
            name=f'Theory Room {i}',
            room_type=RoomType.THEORY,
            capacity=50,
            room_number=str(i)
        ))
    
    # Create 1 default practical room with 50 capacity (always sufficient)
    rooms.append(Room(
        id='P1',
        name='Practical Room',
        room_type=RoomType.PRACTICAL,
        capacity=50,
        room_number='101'
    ))
    
    # Load student groups
    student_groups = []
    for g in data['student_groups']:
        student_groups.append(StudentGroup(
            id=g['id'],
            name=g['name'],
            subject_ids=g['subject_ids']
        ))
    
    # Get configuration
    semester_weeks = data['configuration']['weeks']
    
    return lecturers, subjects, rooms, student_groups, semester_weeks


def print_data_summary(lecturers: List[Lecturer], subjects: List[Subject], 
                      rooms: List[Room], student_groups: List[StudentGroup]):
    """Print a summary of the loaded data"""
    print("=" * 80)
    print("DATA SUMMARY")
    print("=" * 80)
    
    print(f"\nTotal Lecturers: {len(lecturers)}")
    priority_lecturers = [l for l in lecturers if l.priority <= 5]
    print(f"Priority Lecturers (1-5): {len(priority_lecturers)}")
    
    print(f"\nTotal Subjects: {len(subjects)}")
    theory_subjects = [s for s in subjects if s.room_type == RoomType.THEORY]
    practical_subjects = [s for s in subjects if s.room_type == RoomType.PRACTICAL]
    spread_subjects = [s for s in subjects if s.spread]
    print(f"  Theory: {len(theory_subjects)}")
    print(f"  Practical: {len(practical_subjects)}")
    print(f"  Spread subjects: {len(spread_subjects)}")
    
    total_blocks = sum(s.blocks_required for s in subjects)
    print(f"\nTotal blocks needed across all subjects: {total_blocks}")
    
    print(f"\nTotal Rooms: {len(rooms)}")
    print(f"  Theory rooms: {len([r for r in rooms if r.room_type == RoomType.THEORY])}")
    print(f"  Practical rooms: {len([r for r in rooms if r.room_type == RoomType.PRACTICAL])}")
    
    print(f"\nTotal Student Groups: {len(student_groups)}")
    for group in student_groups:
        print(f"  {group.name}: {len(group.subject_ids)} subjects")
    
    print("\nTop 5 Priority Lecturers:")
    for lecturer in sorted(priority_lecturers, key=lambda x: x.priority)[:5]:
        subject = next((s for s in subjects if s.id == lecturer.subject_id), None)
        availability_count = len(lecturer.availability) if lecturer.availability else 0
        print(f"  Priority {lecturer.priority}: {lecturer.name} - {subject.name if subject else 'Unknown'} ({availability_count} available slots)")
    
    print("=" * 80)
