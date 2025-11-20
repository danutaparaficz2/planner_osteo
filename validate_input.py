#!/usr/bin/env python3
"""
Validation utilities for input_data.json.
Checks referential integrity and value ranges.
"""
import json
from typing import Any, Dict, List, Tuple

ALLOWED_TIMESLOTS = {"morning", "afternoon"}
ALLOWED_ROOM_TYPES = {"theory", "practical"}


def load_json(path: str = "input_data.json") -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def validate_data(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    errors: List[str] = []

    # Basic presence (rooms key is optional now as they're auto-generated)
    for key in ["subjects", "lecturers", "student_groups", "configuration"]:
        if key not in data:
            errors.append(f"Missing top-level key: {key}")
            return False, errors

    # Collect ids
    subject_ids = set()
    room_ids = set()
    lecturer_ids = set()
    group_ids = set()

    # Subjects
    for s in data["subjects"]:
        sid = s.get("id")
        if not sid:
            errors.append("Subject with missing id")
            continue
        if sid in subject_ids:
            errors.append(f"Duplicate subject id: {sid}")
        subject_ids.add(sid)
        if s.get("room_type") not in ALLOWED_ROOM_TYPES:
            errors.append(f"Subject {sid} invalid room_type: {s.get('room_type')}")
        if not isinstance(s.get("blocks_required"), int) or s.get("blocks_required", 0) <= 0:
            errors.append(f"Subject {sid} blocks_required must be positive int")

    # Rooms - all rooms (10 theory + 1 practical) are auto-generated, no rooms in JSON needed
    if "rooms" in data and data["rooms"]:
        errors.append("Rooms are auto-generated (10 theory + 1 practical), remove 'rooms' from JSON")

    # Groups
    for g in data["student_groups"]:
        gid = g.get("id")
        if not gid:
            errors.append("Group with missing id")
            continue
        if gid in group_ids:
            errors.append(f"Duplicate group id: {gid}")
        group_ids.add(gid)
        for sid in g.get("subject_ids", []):
            if sid not in subject_ids:
                errors.append(f"Group {gid} references unknown subject id: {sid}")

    # Lecturers
    for l in data["lecturers"]:
        lid = l.get("id")
        if not lid:
            errors.append("Lecturer with missing id")
            continue
        if lid in lecturer_ids:
            errors.append(f"Duplicate lecturer id: {lid}")
        lecturer_ids.add(lid)
        subj = l.get("subject_id")
        if subj not in subject_ids:
            errors.append(f"Lecturer {lid} references unknown subject id: {subj}")
        prio = l.get("priority")
        if not isinstance(prio, int) or prio <= 0:
            errors.append(f"Lecturer {lid} priority must be positive int")
        # availability
        for idx, slot in enumerate(l.get("availability", [])):
            if not (isinstance(slot, list) and len(slot) == 3):
                errors.append(f"Lecturer {lid} availability[{idx}] must be [week, day, timeslot]")
                continue
            w, d, t = slot
            if not isinstance(w, int) or w < 0:
                errors.append(f"Lecturer {lid} availability[{idx}] invalid week: {w}")
            if not isinstance(d, int) or d < 1:
                errors.append(f"Lecturer {lid} availability[{idx}] invalid day: {d}")
            if t not in ALLOWED_TIMESLOTS:
                errors.append(f"Lecturer {lid} availability[{idx}] invalid timeslot: {t}")

    # Configuration
    cfg = data["configuration"]
    weeks = cfg.get("weeks")
    days = cfg.get("days_per_week")
    tpd = cfg.get("timeslots_per_day")
    if not isinstance(weeks, int) or weeks <= 0:
        errors.append("configuration.weeks must be positive int")
    if not isinstance(days, int) or days <= 0 or days > 7:
        errors.append("configuration.days_per_week must be 1..7")
    if not isinstance(tpd, int) or tpd <= 0:
        errors.append("configuration.timeslots_per_day must be positive int")
    # timeslots array
    tsl = cfg.get("timeslots", [])
    if not isinstance(tsl, list) or any(t not in ALLOWED_TIMESLOTS for t in tsl):
        errors.append("configuration.timeslots must be list of allowed timeslots")

    # Check that availabilities are within week/day bounds
    if errors:
        ok = False
    else:
        ok = True
        for l in data["lecturers"]:
            for idx, (w, d, t) in enumerate(l.get("availability", [])):
                if w >= weeks:
                    errors.append(f"Lecturer {l['id']} availability[{idx}] week {w} >= configured weeks {weeks}")
                    ok = False
                if d < 1 or d > days:
                    errors.append(f"Lecturer {l['id']} availability[{idx}] day {d} out of 1..{days}")
                    ok = False

    return ok, errors


def print_report(ok: bool, report: List[str]) -> None:
    line = "=" * 60
    print("\n" + line)
    print("INPUT VALIDATION REPORT")
    print(line)
    if ok:
        print("✓ All checks passed.")
    else:
        print("✗ Issues found:")
        for e in report:
            print("  -", e)
    print(line + "\n")


def main():
    data = load_json()
    ok, report = validate_data(data)
    print_report(ok, report)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
