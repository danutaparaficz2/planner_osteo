#!/usr/bin/env python3
"""
Interactive CLI wizard to create and edit input_data.json for the scheduler.
- No external dependencies
- Validates inputs as you type
- Safe editing with preview and backup
"""
import json
import os
import shutil
import sys
from typing import Any, Dict, List

def _set_working_dir_for_bundle():
    """Ensure reads/writes happen next to the script/app bundle.
    When frozen (PyInstaller), use the folder of the executable. Otherwise use file dir.
    """
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(base_dir)
    except Exception:
        pass


_set_working_dir_for_bundle()

INPUT_FILE = "input_data.json"

TYPESLOTS = ["morning", "afternoon"]
ROOM_TYPES = ["theory", "practical"]


def load_data(path: str = INPUT_FILE) -> Dict[str, Any]:
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    # default skeleton
    return {
        "subjects": [],
        "lecturers": [],
        "rooms": [],
        "student_groups": [],
        "configuration": {
            "weeks": 15,
            "days_per_week": 5,
            "timeslots_per_day": 2,
            "timeslots": TYPESLOTS,
        },
    }


def save_data(data: Dict[str, Any], path: str = INPUT_FILE) -> None:
    # backup existing
    if os.path.exists(path):
        shutil.copyfile(path, path + ".bak")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved to {path} (backup at {path}.bak if existed)")


def prompt(msg: str, default: Any = None, validator=None) -> Any:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"{msg}{suffix}: ").strip()
        if raw == "" and default is not None:
            return default
        val = raw
        if validator:
            ok, err, conv = validator(val)
            if not ok:
                print(f"  ✗ {err}")
                continue
            return conv
        return val


def yes_no(msg: str, default: bool = True) -> bool:
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        raw = input(f"{msg}{suffix}: ").strip().lower()
        if raw == "" and default is not None:
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  Please answer y/n")


def v_nonempty(s: str):
    return (len(s) > 0, "Value cannot be empty", s)


def v_int(min_v=None, max_v=None):
    def _v(s: str):
        try:
            v = int(s)
        except ValueError:
            return False, "Must be an integer", None
        if min_v is not None and v < min_v:
            return False, f"Must be >= {min_v}", None
        if max_v is not None and v > max_v:
            return False, f"Must be <= {max_v}", None
        return True, "", v
    return _v


def v_choice(choices: List[str]):
    def _v(s: str):
        if s not in choices:
            return False, f"Must be one of: {', '.join(choices)}", None
        return True, "", s
    return _v


def list_menu(items: List[str], title: str) -> int:
    print(f"\n{title}")
    print("-" * len(title))
    for i, it in enumerate(items, 1):
        print(f"  {i}. {it}")
    print("  0. Back")
    choice = prompt("Choose", validator=v_int(0, len(items)))
    return choice


# ---- Subjects ----

def subjects_menu(data: Dict[str, Any]):
    while True:
        items = [f"{s['id']}: {s['name']} ({s['room_type']}, blocks={s['blocks_required']}, spread={s.get('spread', False)})" for s in data["subjects"]]
        ch = list_menu(["Add subject", "Edit subject", "Delete subject", "List subjects"] , "Subjects")
        if ch == 0:
            return
        if ch == 1:
            add_subject(data)
        elif ch == 2:
            edit_subject(data)
        elif ch == 3:
            delete_subject(data)
        elif ch == 4:
            for line in items:
                print("  -", line)


def add_subject(data: Dict[str, Any]):
    print("\nAdd Subject")
    sid = prompt("ID (e.g., S1/A/B)", validator=v_nonempty)
    # ensure unique
    if any(s["id"] == sid for s in data["subjects"]):
        print("  ✗ ID already exists")
        return
    name = prompt("Name", validator=v_nonempty)
    blocks = prompt("Blocks required", validator=v_int(1))
    rtype = prompt("Room type", default="theory", validator=v_choice(ROOM_TYPES))
    spread = yes_no("Spread across semester?", default=True)
    data["subjects"].append({
        "id": sid,
        "name": name,
        "blocks_required": blocks,
        "room_type": rtype,
        "spread": spread,
    })
    print("  ✓ Subject added")


def select_by_id(items: List[Dict[str, Any]], kind: str) -> Dict[str, Any]:
    if not items:
        print(f"  No {kind} available")
        return None
    print(f"Available {kind} IDs:")
    for it in items:
        print("  -", it["id"])
    sid = prompt(f"Enter {kind} ID")
    found = next((s for s in items if s["id"] == sid), None)
    if not found:
        print("  ✗ Not found")
    return found


def edit_subject(data: Dict[str, Any]):
    s = select_by_id(data["subjects"], "subject")
    if not s:
        return
    print("Editing (press Enter to keep current value)")
    s["name"] = prompt("Name", default=s["name"], validator=v_nonempty)
    s["blocks_required"] = prompt("Blocks required", default=s["blocks_required"], validator=v_int(1))
    s["room_type"] = prompt("Room type", default=s["room_type"], validator=v_choice(ROOM_TYPES))
    s["spread"] = yes_no("Spread across semester?", default=bool(s.get("spread", False)))
    print("  ✓ Subject updated")


def delete_subject(data: Dict[str, Any]):
    s = select_by_id(data["subjects"], "subject")
    if not s:
        return
    if yes_no(f"Delete subject {s['id']}?", default=False):
        data["subjects"].remove(s)
        print("  ✓ Deleted")


# ---- Rooms ----

def rooms_menu(data: Dict[str, Any]):
    while True:
        ch = list_menu(["Add room", "Edit room", "Delete room", "List rooms"], "Rooms (Practical Only - Theory Auto-Generated)")
        if ch == 0:
            return
        if ch == 1:
            add_room(data)
        elif ch == 2:
            edit_room(data)
        elif ch == 3:
            delete_room(data)
        elif ch == 4:
            print("\n  Note: 10 theory rooms (#1-#10, 50 capacity) are automatically generated.")
            print("  Practical rooms in JSON:")
            for r in data["rooms"]:
                print(f"  - {r['id']}: {r['name']} ({r['room_type']}, cap={r['capacity']})")


def add_room(data: Dict[str, Any]):
    print("\nAdd Room (Practical Only)")
    print("  Note: 10 theory rooms are auto-generated. Only add practical rooms here.")
    rid = prompt("ID (e.g., P1)", validator=v_nonempty)
    if any(r["id"] == rid for r in data["rooms"]):
        print("  ✗ ID already exists")
        return
    name = prompt("Name", validator=v_nonempty)
    rtype = prompt("Room type", default="practical", validator=v_choice(ROOM_TYPES))
    if rtype == "theory":
        print("  ✗ Theory rooms are auto-generated. Only add practical rooms.")
        return
    cap = prompt("Capacity", validator=v_int(1))
    data["rooms"].append({"id": rid, "name": name, "room_type": rtype, "capacity": cap})
    print("  ✓ Room added")


def edit_room(data: Dict[str, Any]):
    r = select_by_id(data["rooms"], "room")
    if not r:
        return
    r["name"] = prompt("Name", default=r["name"], validator=v_nonempty)
    r["room_type"] = prompt("Room type", default=r["room_type"], validator=v_choice(ROOM_TYPES))
    r["capacity"] = prompt("Capacity", default=r["capacity"], validator=v_int(1))
    print("  ✓ Room updated")


def delete_room(data: Dict[str, Any]):
    r = select_by_id(data["rooms"], "room")
    if not r:
        return
    if yes_no(f"Delete room {r['id']}?", default=False):
        data["rooms"].remove(r)
        print("  ✓ Deleted")


# ---- Student Groups ----

def groups_menu(data: Dict[str, Any]):
    while True:
        ch = list_menu(["Add group", "Edit group", "Delete group", "List groups"], "Student Groups")
        if ch == 0:
            return
        if ch == 1:
            add_group(data)
        elif ch == 2:
            edit_group(data)
        elif ch == 3:
            delete_group(data)
        elif ch == 4:
            for g in data["student_groups"]:
                print(f"  - {g['id']}: {g['name']} -> {len(g['subject_ids'])} subjects")


def add_group(data: Dict[str, Any]):
    print("\nAdd Student Group")
    gid = prompt("ID (e.g., G1)", validator=v_nonempty)
    if any(g["id"] == gid for g in data["student_groups"]):
        print("  ✗ ID already exists")
        return
    name = prompt("Name", validator=v_nonempty)
    subject_ids = []
    print("Enter subject IDs this group attends (blank to finish). Existing subjects:")
    print("  ", ", ".join(s["id"] for s in data["subjects"]))
    while True:
        sid = input("  Subject ID: ").strip()
        if not sid:
            break
        subject_ids.append(sid)
    data["student_groups"].append({"id": gid, "name": name, "subject_ids": subject_ids})
    print("  ✓ Group added")


def edit_group(data: Dict[str, Any]):
    g = select_by_id(data["student_groups"], "group")
    if not g:
        return
    g["name"] = prompt("Name", default=g["name"], validator=v_nonempty)
    if yes_no("Edit subject IDs?", default=False):
        subject_ids = []
        print("Enter subject IDs (blank to finish). Existing subjects:")
        print("  ", ", ".join(s["id"] for s in data["subjects"]))
        while True:
            sid = input("  Subject ID: ").strip()
            if not sid:
                break
            subject_ids.append(sid)
        g["subject_ids"] = subject_ids
    print("  ✓ Group updated")


def delete_group(data: Dict[str, Any]):
    g = select_by_id(data["student_groups"], "group")
    if not g:
        return
    if yes_no(f"Delete group {g['id']}?", default=False):
        data["student_groups"].remove(g)
        print("  ✓ Deleted")


# ---- Lecturers ----

def lecturers_menu(data: Dict[str, Any]):
    while True:
        ch = list_menu(["Add lecturer", "Edit lecturer", "Delete lecturer", "List lecturers", "Build availability (patterns)", "Convert availability format"], "Lecturers")
        if ch == 0:
            return
        if ch == 1:
            add_lecturer(data)
        elif ch == 2:
            edit_lecturer(data)
        elif ch == 3:
            delete_lecturer(data)
        elif ch == 4:
            for l in data["lecturers"]:
                summary = summarize_availability(l.get('availability'))
                print(f"  - {l['id']}: {l['name']} subj={l['subject_id']} priority={l['priority']} {summary}")
        elif ch == 5:
            pattern_builder_global(data)
        elif ch == 6:
            convert_availability_global(data)


def add_lecturer(data: Dict[str, Any]):
    print("\nAdd Lecturer")
    lid = prompt("ID (e.g., L1)", validator=v_nonempty)
    if any(l["id"] == lid for l in data["lecturers"]):
        print("  ✗ ID already exists")
        return
    name = prompt("Name", validator=v_nonempty)
    subject_id = prompt("Subject ID (existing)", validator=v_nonempty)
    priority = prompt("Priority (1=highest)", validator=v_int(1))
    availability = []
    if priority <= 5:
        if yes_no("Use pattern-based availability builder?", default=True):
            availability = pattern_builder_single(data)
        elif yes_no("Enter raw slots manually?", default=False):
            availability = prompt_availability(data)
    data["lecturers"].append({
        "id": lid,
        "name": name,
        "subject_id": subject_id,
        "priority": priority,
        "availability": availability,
    })
    print("  ✓ Lecturer added")


def prompt_availability(data: Dict[str, Any]) -> List[List[Any]]:
    weeks = data["configuration"]["weeks"]
    days = data["configuration"]["days_per_week"]
    print("Enter availability as triples: week(0..), day(1..), timeslot(morning/afternoon). Blank to finish.")
    avail = []
    while True:
        w = input("  Week (0-based, blank to finish): ").strip()
        if w == "":
            break
        d = input("  Day (1-5): ").strip()
        t = input("  Timeslot (morning/afternoon): ").strip().lower()
        try:
            w_i = int(w)
            d_i = int(d)
        except ValueError:
            print("  ✗ Week/Day must be integers")
            continue
        if w_i < 0 or w_i >= weeks:
            print(f"  ✗ Week must be in 0..{weeks-1}")
            continue
        if d_i < 1 or d_i > days:
            print(f"  ✗ Day must be in 1..{days}")
            continue
        if t not in TYPESLOTS:
            print(f"  ✗ Timeslot must be one of {TYPESLOTS}")
            continue
        avail.append([w_i, d_i, t])
    return avail


def edit_lecturer(data: Dict[str, Any]):
    l = select_by_id(data["lecturers"], "lecturer")
    if not l:
        return
    l["name"] = prompt("Name", default=l["name"], validator=v_nonempty)
    l["subject_id"] = prompt("Subject ID", default=l["subject_id"], validator=v_nonempty)
    l["priority"] = prompt("Priority", default=l["priority"], validator=v_int(1))
    if l["priority"] <= 5 and yes_no("Edit availability?", default=False):
        # Detect format
        current = l.get('availability', [])
        print(f"Current availability format: {'pattern' if isinstance(current, dict) else 'list'}")
        mode_choice = list_menu(["Pattern builder", "Manual slot list", "Cancel"], "Edit Availability Mode")
        if mode_choice == 1:
            l["availability"] = pattern_builder_single(data, existing=current if isinstance(current, dict) else None)
        elif mode_choice == 2:
            l["availability"] = prompt_availability(data)
        else:
            print("  ✱ Availability unchanged")
    print("  ✓ Lecturer updated")

# ---- Availability Helpers ----

DAY_CODES = ["Mon","Tue","Wed","Thu","Fri"]

def summarize_availability(avail) -> str:
    if not avail:
        return "avail=0 slots"
    if isinstance(avail, list):
        return f"avail={len(avail)} slots (list)"
    if isinstance(avail, dict):
        patterns = len(avail.get('patterns', []) or [])
        exceptions = len(avail.get('exceptions', []) or [])
        blackouts = len(avail.get('blackouts', []) or [])
        return f"patterns={patterns}, exceptions={exceptions}, blackouts={blackouts}"
    return "avail=?"

def pattern_builder_single(data: Dict[str, Any], existing: Dict[str, Any] = None) -> Dict[str, Any]:
    weeks_total = data["configuration"]["weeks"]
    print(f"\nPattern Availability Builder (weeks 1..{weeks_total})")
    if existing:
        print("Existing patterns detected; starting with them.")
    availability = existing.copy() if existing else {"patterns": [], "exceptions": [], "blackouts": []}

    while True:
        print("\nAdd / Edit a Pattern")
        weeks_expr = prompt("Weeks expression (e.g. 1-5,7,10-12)", default=f"1-{weeks_total}")
        # Initialize empty selection grid
        selection = {d: {"morning": False, "afternoon": False} for d in DAY_CODES}
        # Interactive toggling loop
        print("Toggle slots. Commands: 'mon m', 'tue a', 'wed both', 'all', 'done', 'show'.")
        while True:
            cmd = input("  slot> ").strip().lower()
            if cmd in ("done", "finish"):
                break
            if cmd == "show":
                _print_selection(selection)
                continue
            if cmd == "all":
                for d in DAY_CODES:
                    selection[d]["morning"] = True
                    selection[d]["afternoon"] = True
                _print_selection(selection)
                continue
            parts = cmd.split()
            if not parts:
                continue
            day_part = parts[0]
            slot_part = parts[1] if len(parts) > 1 else None
            day_match = _match_day(day_part)
            if not day_match:
                print("  ✗ Unknown day code")
                continue
            if slot_part in (None, "both"):
                selection[day_match]["morning"] = not selection[day_match]["morning"]
                selection[day_match]["afternoon"] = not selection[day_match]["afternoon"]
            elif slot_part in ("m", "morning"):
                selection[day_match]["morning"] = not selection[day_match]["morning"]
            elif slot_part in ("a", "afternoon"):
                selection[day_match]["afternoon"] = not selection[day_match]["afternoon"]
            else:
                print("  ✗ Unknown slot; use morning/m or afternoon/a/both")
                continue
            _print_selection(selection)
        # Build pattern days map
        days_map = {}
        for d in DAY_CODES:
            slots = [s for s, v in selection[d].items() if v]
            if slots:
                days_map[d] = slots
        availability["patterns"].append({"weeks": weeks_expr, "days": days_map})
        print("  ✓ Pattern added")
        if not yes_no("Add another pattern?", default=False):
            break

    # Exceptions
    if yes_no("Add exceptions (specific adds/removes)?", default=False):
        while True:
            week = prompt("Exception week", validator=v_int(1, weeks_total))
            day = prompt("Day (Mon/Tue/...)", validator=v_choice(DAY_CODES))
            action = prompt("Action (remove/add)", validator=v_choice(["remove","add"]))
            slots_raw = prompt("Slots comma list (morning,afternoon)", default="morning")
            slots = [s.strip() for s in slots_raw.split(',') if s.strip() in TYPESLOTS]
            availability["exceptions"].append({"week": week, "day": day, action: slots})
            print("  ✓ Exception added")
            if not yes_no("Add another exception?", default=False):
                break

    # Blackouts
    if yes_no("Add blackouts (vacation ranges)?", default=False):
        while True:
            from_w = prompt("From week", validator=v_int(1, weeks_total))
            to_w = prompt("To week", default=from_w, validator=v_int(1, weeks_total))
            days_raw = prompt("Days comma list (blank=all)", default="")
            days_list = [d.strip() for d in days_raw.split(',') if d.strip() in DAY_CODES]
            availability["blackouts"].append({"from_week": from_w, "to_week": to_w, "days": days_list})
            print("  ✓ Blackout added")
            if not yes_no("Add another blackout?", default=False):
                break

    return availability

def _match_day(token: str) -> str:
    token = token.lower()
    for d in DAY_CODES:
        if d.lower().startswith(token):
            return d
    return None

def _print_selection(selection: Dict[str, Dict[str,bool]]):
    print("    Day       Morning Afternoon")
    for d in DAY_CODES:
        m = '✓' if selection[d]['morning'] else '·'
        a = '✓' if selection[d]['afternoon'] else '·'
        print(f"    {d:<3}       {m:^7} {a:^9}")

def pattern_builder_global(data: Dict[str, Any]):
    print("\nAssign patterns to multiple lecturers (priority <=5).")
    targets = [l for l in data['lecturers'] if l.get('priority', 999) <= 5]
    if not targets:
        print("  ✗ No priority lecturers found.")
        return
    print("Priority lecturers:")
    for l in targets:
        print(f"  - {l['id']}: {l['name']} ({summarize_availability(l.get('availability'))})")
    if not yes_no("Proceed building a pattern and apply to all (append)?", default=False):
        return
    pattern_avail = pattern_builder_single(data)
    for l in targets:
        existing = l.get('availability')
        if isinstance(existing, dict):
            existing['patterns'].extend(pattern_avail['patterns'])
            existing['exceptions'].extend(pattern_avail['exceptions'])
            existing['blackouts'].extend(pattern_avail['blackouts'])
        else:
            l['availability'] = pattern_avail
    print("  ✓ Pattern applied to all priority lecturers")

def convert_availability_global(data: Dict[str, Any]):
    print("\nConvert list-based availability to pattern schema.")
    for l in data['lecturers']:
        avail = l.get('availability')
        if isinstance(avail, list) and avail:
            # Group by day/slot ignoring weeks for a base pattern
            weeks_total = data['configuration']['weeks']
            weeks_expr = f"1-{weeks_total}"
            day_slot = {d: set() for d in DAY_CODES}
            for w, d, slot in avail:
                # d is numeric day (1-5)
                day_name = DAY_CODES[d - 1] if 1 <= d <= 5 else None
                if day_name:
                    day_slot[day_name].add(slot)
            days_map = {d: sorted(slots) for d, slots in day_slot.items() if slots}
            l['availability'] = {"patterns": [{"weeks": weeks_expr, "days": days_map}], "exceptions": [], "blackouts": []}
            print(f"  ✓ Converted lecturer {l['id']} -> pattern format")
    print("Conversion complete.")


def delete_lecturer(data: Dict[str, Any]):
    l = select_by_id(data["lecturers"], "lecturer")
    if not l:
        return
    if yes_no(f"Delete lecturer {l['id']}?", default=False):
        data["lecturers"].remove(l)
        print("  ✓ Deleted")


# ---- Configuration ----

def config_menu(data: Dict[str, Any]):
    cfg = data["configuration"]
    print("\nConfiguration (press Enter to keep current value)")
    cfg["weeks"] = prompt("Weeks (semester length)", default=cfg["weeks"], validator=v_int(1))
    cfg["days_per_week"] = prompt("Days per week", default=cfg["days_per_week"], validator=v_int(1, 7))
    cfg["timeslots_per_day"] = prompt("Timeslots per day", default=cfg["timeslots_per_day"], validator=v_int(1))
    # fixed timeslots for now
    print(f"Timeslots supported: {', '.join(TYPESLOTS)}")
    print("  ✓ Configuration updated")


# ---- Main Menu ----

def main_menu():
    data = load_data()
    while True:
        print("\nOsteopathy Scheduler - Input Wizard")
        print("=" * 40)
        print("1) Subjects")
        print("2) Rooms (Practical only - 10 theory auto-generated)")
        print("3) Student Groups")
        print("4) Lecturers")
        print("5) Configuration")
        print("6) Validate and Save")
        print("7) Save without validation")
        print("0) Exit")
        choice = prompt("Select option", validator=v_int(0,7))
        if choice == 0:
            break
        if choice == 1:
            subjects_menu(data)
        elif choice == 2:
            rooms_menu(data)
        elif choice == 3:
            groups_menu(data)
        elif choice == 4:
            lecturers_menu(data)
        elif choice == 5:
            config_menu(data)
        elif choice == 6:
            from validate_input import validate_data, print_report
            ok, report = validate_data(data)
            print_report(ok, report)
            if ok and yes_no("Save changes?", default=True):
                save_data(data)
        elif choice == 7:
            if yes_no("Save changes without validation?", default=False):
                save_data(data)


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting...")
