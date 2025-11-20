#!/usr/bin/env python3
"""
Test script to validate the new pattern-based availability schema works end-to-end.
Creates a mini dataset with pattern availability, loads it, and verifies expansion.
"""
import json
import os
from data_loader import load_from_json, _expand_availability

def test_pattern_expansion():
    """Test that patterns expand correctly"""
    print("Testing pattern expansion...")
    
    # Test case 1: Simple pattern
    pattern1 = {
        "patterns": [
            {
                "weeks": "1-3",
                "days": {
                    "Mon": ["morning", "afternoon"],
                    "Wed": ["morning"]
                }
            }
        ],
        "exceptions": [],
        "blackouts": []
    }
    result1 = _expand_availability(pattern1, 15)
    expected_slots = 3 * 2 + 3 * 1  # 3 weeks * 2 Mon slots + 3 weeks * 1 Wed slot = 9
    assert len(result1) == expected_slots, f"Expected {expected_slots} slots, got {len(result1)}"
    print(f"  ✓ Pattern 1: {len(result1)} slots expanded correctly")
    
    # Test case 2: Pattern with exceptions
    pattern2 = {
        "patterns": [
            {
                "weeks": "1-5",
                "days": {
                    "Mon": ["morning"],
                    "Tue": ["morning"],
                    "Wed": ["morning"],
                    "Thu": ["morning"],
                    "Fri": ["morning"]
                }
            }
        ],
        "exceptions": [
            {"week": 3, "day": "Wed", "remove": ["morning"]},
            {"week": 4, "day": "Fri", "add": ["afternoon"]}
        ],
        "blackouts": []
    }
    result2 = _expand_availability(pattern2, 15)
    # 5 weeks * 5 days * 1 slot = 25, -1 (Wed week 3), +1 (Fri week 4 afternoon) = 25
    assert len(result2) == 25, f"Expected 25 slots, got {len(result2)}"
    print(f"  ✓ Pattern 2 with exceptions: {len(result2)} slots")
    
    # Test case 3: Pattern with blackout
    pattern3 = {
        "patterns": [
            {
                "weeks": "1-10",
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
        "blackouts": [
            {"from_week": 5, "to_week": 5, "days": ["Thu", "Fri"]}
        ]
    }
    result3 = _expand_availability(pattern3, 15)
    # 10 weeks * 5 days * 2 slots = 100, -4 (Thu+Fri both slots in week 5) = 96
    assert len(result3) == 96, f"Expected 96 slots, got {len(result3)}"
    print(f"  ✓ Pattern 3 with blackout: {len(result3)} slots")
    
    # Test case 4: Backward compatibility with list
    list_avail = [[1, 1, "morning"], [1, 2, "afternoon"], [2, 3, "morning"]]
    result4 = _expand_availability(list_avail, 15)
    assert len(result4) == 3, f"Expected 3 slots, got {len(result4)}"
    print(f"  ✓ List format backward compatibility: {len(result4)} slots")
    
    print("\n✓ All pattern expansion tests passed!\n")


def create_test_json_with_patterns():
    """Create a minimal test JSON with pattern-based availability"""
    test_data = {
        "subjects": [
            {
                "id": "S1",
                "name": "Anatomy",
                "blocks_required": 10,
                "room_type": "theory",
                "spread": True
            },
            {
                "id": "P1",
                "name": "Clinical Practice",
                "blocks_required": 8,
                "room_type": "practical",
                "spread": True
            }
        ],
        "lecturers": [
            {
                "id": "L1",
                "name": "Dr. Pattern",
                "subject_id": "S1",
                "priority": 1,
                "availability": {
                    "patterns": [
                        {
                            "weeks": "1-8",
                            "days": {
                                "Mon": ["morning", "afternoon"],
                                "Tue": ["morning"],
                                "Wed": ["afternoon"],
                                "Thu": ["morning", "afternoon"],
                                "Fri": ["morning"]
                            }
                        },
                        {
                            "weeks": "9-15",
                            "days": {
                                "Mon": ["morning"],
                                "Wed": ["morning", "afternoon"],
                                "Fri": ["afternoon"]
                            }
                        }
                    ],
                    "exceptions": [
                        {"week": 5, "day": "Thu", "remove": ["afternoon"]},
                        {"week": 10, "day": "Tue", "add": ["morning"]}
                    ],
                    "blackouts": [
                        {"from_week": 7, "to_week": 7, "days": ["Mon", "Fri"]}
                    ]
                }
            },
            {
                "id": "L2",
                "name": "Dr. Legacy",
                "subject_id": "P1",
                "priority": 2,
                "availability": [[1, 1, "morning"], [1, 2, "afternoon"], [2, 1, "morning"], [2, 3, "afternoon"]]
            }
        ],
        "student_groups": [
            {
                "id": "G1",
                "name": "Year 1",
                "subject_ids": ["S1", "P1"]
            }
        ],
        "configuration": {
            "weeks": 15,
            "days_per_week": 5,
            "timeslots_per_day": 2,
            "timeslots": ["morning", "afternoon"]
        }
    }
    
    with open("test_pattern_data.json", "w") as f:
        json.dump(test_data, f, indent=2)
    print("✓ Created test_pattern_data.json")
    return "test_pattern_data.json"


def test_full_load():
    """Test loading the JSON through the full data_loader"""
    print("\nTesting full data load...")
    test_file = create_test_json_with_patterns()
    
    try:
        lecturers, subjects, rooms, student_groups, weeks = load_from_json(test_file)
        
        print(f"  ✓ Loaded {len(lecturers)} lecturers")
        print(f"  ✓ Loaded {len(subjects)} subjects")
        print(f"  ✓ Loaded {len(rooms)} rooms (auto-generated)")
        print(f"  ✓ Loaded {len(student_groups)} groups")
        
        # Check pattern lecturer
        pattern_lec = next(l for l in lecturers if l.id == "L1")
        print(f"\n  Dr. Pattern availability: {len(pattern_lec.availability)} slots")
        
        # Check legacy lecturer
        legacy_lec = next(l for l in lecturers if l.id == "L2")
        print(f"  Dr. Legacy availability: {len(legacy_lec.availability)} slots")
        
        # Verify both types work
        assert len(pattern_lec.availability) > 0, "Pattern lecturer should have availability"
        assert len(legacy_lec.availability) == 4, "Legacy lecturer should have 4 slots"
        
        print("\n✓ Full data load test passed!")
        
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"  Cleaned up {test_file}")


if __name__ == "__main__":
    print("=" * 60)
    print("PATTERN AVAILABILITY SCHEMA TEST")
    print("=" * 60)
    print()
    
    test_pattern_expansion()
    test_full_load()
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
