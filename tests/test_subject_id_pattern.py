import os
import sys
import tkinter as tk
from tkinter import messagebox

# Silence messageboxes during automated test
messagebox.showerror = lambda *args, **kwargs: None
messagebox.askyesno = lambda *args, **kwargs: True

# Ensure workspace root is on module search path
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gui_input_tk import InputEditor


def main():
    root = tk.Tk()
    root.withdraw()
    editor = InputEditor(root)
    editor.data = {"subjects": []}

    assert editor._is_unique_subject_id("Good_ID-123") is True
    assert editor._is_unique_subject_id("bad id") is False, "Spaces should be rejected"
    assert editor._is_unique_subject_id("Bad@ID") is False, "Special characters should be rejected"
    assert editor._is_unique_subject_id("") is False, "Empty should be rejected"

    print("OK: Subject ID pattern validation working.")


if __name__ == "__main__":
    main()
