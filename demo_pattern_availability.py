#!/usr/bin/env python3
"""
Demo script showing the new pattern-based availability builder.
Converts existing lecturers to use the new schema and demonstrates usage.
"""
import json
import shutil
from datetime import datetime

def backup_input_data():
    """Backup the current input_data.json"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"input_data_backup_{timestamp}.json"
    shutil.copy("input_data.json", backup_name)
    print(f"✓ Backed up to {backup_name}")
    return backup_name

def convert_lecturer_to_pattern(lecturer_data, weeks=15):
    """Convert a lecturer from list-based to pattern-based availability"""
    avail = lecturer_data.get("availability", [])
    
    if not avail or isinstance(avail, dict):
        return lecturer_data  # Already pattern or empty
    
    # Analyze the list to find patterns
    # Group by day and slot across all weeks
    day_slots = {1: set(), 2: set(), 3: set(), 4: set(), 5: set()}
    
    for week, day, slot in avail:
        if 1 <= day <= 5:
            day_slots[day].add(slot)
    
    # Convert to pattern format
    day_names = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}
    days_map = {}
    
    for day_num, slots in day_slots.items():
        if slots:
            days_map[day_names[day_num]] = sorted(list(slots))
    
    pattern_avail = {
        "patterns": [
            {
                "weeks": f"1-{weeks}",
                "days": days_map
            }
        ],
        "exceptions": [],
        "blackouts": []
    }
    
    lecturer_data["availability"] = pattern_avail
    return lecturer_data

def demo_pattern_examples():
    """Show various pattern examples"""
    print("\n" + "="*60)
    print("PATTERN AVAILABILITY EXAMPLES")
    print("="*60)
    
    examples = [
        {
            "name": "Full-time lecturer (always available)",
            "pattern": {
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
        },
        {
            "name": "Part-time lecturer (Mon/Wed/Fri mornings)",
            "pattern": {
                "patterns": [
                    {
                        "weeks": "1-15",
                        "days": {
                            "Mon": ["morning"],
                            "Wed": ["morning"],
                            "Fri": ["morning"]
                        }
                    }
                ],
                "exceptions": [],
                "blackouts": []
            }
        },
        {
            "name": "Variable schedule with mid-semester change",
            "pattern": {
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
                ],
                "exceptions": [],
                "blackouts": []
            }
        },
        {
            "name": "With vacation and exceptions",
            "pattern": {
                "patterns": [
                    {
                        "weeks": "1-15",
                        "days": {
                            "Mon": ["morning", "afternoon"],
                            "Tue": ["morning", "afternoon"],
                            "Wed": ["morning", "afternoon"],
                            "Thu": ["morning", "afternoon"],
                            "Fri": ["morning"]
                        }
                    }
                ],
                "exceptions": [
                    {"week": 3, "day": "Thu", "remove": ["afternoon"]},
                    {"week": 10, "day": "Fri", "add": ["afternoon"]}
                ],
                "blackouts": [
                    {"from_week": 7, "to_week": 7, "days": ["Mon", "Tue", "Wed", "Thu", "Fri"]}
                ]
            }
        }
    ]
    
    for example in examples:
        print(f"\n{example['name']}:")
        print(json.dumps(example['pattern'], indent=2))
    
    print("\n" + "="*60)

def convert_input_data():
    """Convert current input_data.json to use pattern-based availability"""
    print("\n" + "="*60)
    print("CONVERTING INPUT DATA TO PATTERN SCHEMA")
    print("="*60)
    
    # Backup first
    backup_name = backup_input_data()
    
    # Load data
    with open("input_data.json", "r") as f:
        data = json.load(f)
    
    weeks = data["configuration"]["weeks"]
    converted_count = 0
    
    # Convert each lecturer
    for lecturer in data["lecturers"]:
        if isinstance(lecturer.get("availability"), list) and lecturer["availability"]:
            print(f"Converting {lecturer['name']}...")
            convert_lecturer_to_pattern(lecturer, weeks)
            converted_count += 1
    
    # Save updated data
    with open("input_data_pattern.json", "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"\n✓ Converted {converted_count} lecturers")
    print(f"✓ Saved to input_data_pattern.json")
    print(f"✓ Original backed up to {backup_name}")
    print("\nTo use the new format:")
    print("  mv input_data.json input_data_old.json")
    print("  mv input_data_pattern.json input_data.json")

if __name__ == "__main__":
    print("="*60)
    print("PATTERN AVAILABILITY DEMO")
    print("="*60)
    
    demo_pattern_examples()
    
    print("\n")
    response = input("Convert your input_data.json to pattern format? (y/N): ").strip().lower()
    if response == 'y':
        convert_input_data()
    else:
        print("\nSkipping conversion. Run this script again to convert.")
    
    print("\n" + "="*60)
    print("USAGE TIPS")
    print("="*60)
    print("""
1. CLI Pattern Builder:
   - Run: python user_input_cli.py
   - Choose: 4) Lecturers
   - Choose: 5) Build availability (patterns)
   - Interactive toggle interface for selecting days/slots
   
2. Individual Lecturer:
   - Edit existing lecturer
   - Choose pattern builder mode
   - Define base weekly pattern
   - Add exceptions for specific weeks
   - Add blackouts for vacation periods
   
3. Batch Conversion:
   - Choose: 6) Convert availability format
   - Automatically converts all list-based to pattern-based
   
4. Benefits:
   - 150+ manual entries → ~10 pattern definitions
   - Easy to express "always Mon/Wed mornings except week 7"
   - Mid-semester changes via additional patterns
   - Vacation weeks via blackouts
   - Backward compatible with old format
    """)
