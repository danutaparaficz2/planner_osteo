import os
import sys
import tkinter as tk
from tkinter import messagebox

# Ensure workspace root is on module search path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Silence messageboxes during automated test
messagebox.showerror = lambda *args, **kwargs: None
messagebox.showinfo = lambda *args, **kwargs: None

from gui_input_tk import InputEditor


def main():
    root = tk.Tk()
    root.withdraw()
    editor = InputEditor(root)

    # Prepare in-memory data
    editor.data = {
        "subjects": [
            {"id": "S1", "name": "Sub1", "blocks_required": 2, "room_type": "theory", "spread": False},
            {"id": "S2", "name": "Sub2", "blocks_required": 1, "room_type": "theory", "spread": False},
        ],
        "lecturers": [
            {"id": "L1", "name": "Lect", "subject_id": "S1", "priority": 1, "availability_type": "fixed", "vacations": []}
        ],
        "student_groups": [
            {"id": "G1", "name": "Group", "subject_ids": ["S1", "S2"]}
        ],
        "config": editor.data.get("config", {})
    }

    # Uniqueness: duplicate should fail when not ignored
    assert editor._is_unique_subject_id("S1", ignore_index=None) is False, "Duplicate ID should be rejected"
    # Uniqueness: same ID allowed when editing the same row
    assert editor._is_unique_subject_id("S1", ignore_index=0) is True, "Same ID for same row should be allowed"
    # Uniqueness: new unused ID
    assert editor._is_unique_subject_id("S3", ignore_index=None) is True, "New unused ID should be allowed"

    # Replace references
    editor._replace_subject_id("S1", "S1X")
    assert editor.data["lecturers"][0]["subject_id"] == "S1X", "Lecturer subject_id should update"
    assert editor.data["student_groups"][0]["subject_ids"][0] == "S1X", "Group subject_ids should update"

    print("OK: Subject ID validation and reference updates working.")


if __name__ == "__main__":
    main()
