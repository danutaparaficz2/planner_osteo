"""Tkinter-based editor for input_data.json.

Provides tabbed views for Subjects, Lecturers, Student Groups, and Configuration.
Includes availability editor that supports quick pattern creation plus raw JSON editing.
Runs existing validation before saving.
"""
import json
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any, Dict, List, Optional
from data_loader import _expand_availability
from swiss_holidays import CANTONS, is_holiday

from validate_input import validate_data

DAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
DEFAULT_PATH = "input_data.json"


def _safe_load(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return json.load(f)


def _safe_dump(data: Dict[str, Any], path: str) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


class InputEditor:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Planner Input Editor")
        self.data: Dict[str, Any] = {}
        self.file_path = DEFAULT_PATH

        self._build_menu()
        self._build_tabs()
        self._load_initial()
        # Ensure window opens large enough for lecturers columns
        self.root.after(0, self._ensure_min_window_size)

    # UI construction -------------------------------------------------
    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open JSON…", command=self._choose_file)
        filemenu.add_command(label="Save", command=self._save)
        filemenu.add_command(label="Save As…", command=self._save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Validate", command=self._run_validation)
        filemenu.add_command(label="Quit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def _build_tabs(self) -> None:
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.summary_tab = ttk.Frame(self.notebook)
        self.subjects_tab = ttk.Frame(self.notebook)
        self.lecturers_tab = ttk.Frame(self.notebook)
        self.groups_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)
        self.validation_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.summary_tab, text="Summary")
        # Place Configuration immediately after Summary
        self.notebook.add(self.config_tab, text="Configuration")
        self.notebook.add(self.subjects_tab, text="Subjects")
        self.notebook.add(self.lecturers_tab, text="Lecturers")
        self.notebook.add(self.groups_tab, text="Student Groups")
        self.notebook.add(self.validation_tab, text="Run & Validate")

        self._build_summary_tab()
        self._build_config_tab()
        self._build_subjects_tab()
        self._build_lecturers_tab()
        self._build_groups_tab()
        self._build_validation_tab()

    def _build_summary_tab(self) -> None:
        container = ttk.Frame(self.summary_tab, padding=16)
        container.pack(fill=tk.BOTH, expand=True)

        self.summary_title = ttk.Label(container, text="OSTHEOPATHY PLANNER", font=("Helvetica", 18, "bold"))
        self.summary_title.pack(anchor="center", pady=(0, 8))

        # Display image.jpeg (above stats)
        calendar_frame = ttk.Frame(container)
        calendar_frame.pack(fill=tk.X, pady=(8, 10))
        self.calendar_image_label = ttk.Label(calendar_frame)
        self.calendar_image_label.pack(anchor="center")
        self._load_summary_image()

        action_frame = ttk.Frame(container)
        action_frame.pack(fill=tk.X, pady=6)
        ttk.Button(action_frame, text="Open images folder", command=self._open_images_folder).pack(side=tk.LEFT)

        # Stats cards under the calendar
        self.summary_cards = {}
        cards_frame = ttk.Frame(container)
        cards_frame.pack(fill=tk.X, pady=4)

        for key, label in (
            ("subjects", "Subjects"),
            ("lecturers", "Lecturers"),
            ("groups", "Student Groups"),
            ("weeks", "Weeks"),
            ("days", "Days/Week"),
            ("slots", "Timeslots/Day"),
        ):
            card = ttk.Frame(cards_frame, padding=8)
            card.pack(side=tk.LEFT, padx=6, pady=6)
            ttk.Label(card, text=label, font=("Helvetica", 10, "bold")).pack(anchor="center")
            val = ttk.Label(card, text="-", font=("Helvetica", 12))
            val.pack(anchor="center", pady=(4, 0))
            self.summary_cards[key] = val

        self.summary_details = tk.Text(container, height=12, wrap="word", state=tk.DISABLED)
        self.summary_details.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    def _build_subjects_tab(self) -> None:
        frame = ttk.Frame(self.subjects_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        cols = ("id", "name", "blocks", "room_type", "spread")
        self.subjects_tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        headings = {
            "id": "ID",
            "name": "Name",
            "blocks": "Blocks",
            "room_type": "Room Type",
            "spread": "Spread",
        }
        for cid, text in headings.items():
            self.subjects_tree.heading(cid, text=text)
            self.subjects_tree.column(cid, width=110 if cid != "name" else 200, anchor="center")
        self.subjects_tree.pack(fill=tk.BOTH, expand=True)

        btns = ttk.Frame(frame)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Add", command=self._add_subject).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Delete", command=self._delete_subject).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Save", command=self._save).pack(side=tk.RIGHT, padx=4)

    def _build_lecturers_tab(self) -> None:
        frame = ttk.Frame(self.lecturers_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        cols = ("id", "name", "subject_id", "priority", "availability_type", "vacations", "visualize")
        tree_wrap = ttk.Frame(frame)
        tree_wrap.pack(fill=tk.BOTH, expand=True)
        self.lecturers_tree = ttk.Treeview(tree_wrap, columns=cols, show="headings", height=12)
        headings = {
            "id": "ID",
            "name": "Name",
            "subject_id": "Subject",
            "priority": "Priority",
            "availability_type": "Availability",
            "vacations": "Vacations",
            "visualize": "Visualize",
        }
        for cid, text in headings.items():
            self.lecturers_tree.heading(cid, text=text)
            if cid == "vacations":
                self.lecturers_tree.column(cid, width=260, anchor="center", stretch=True)
            elif cid == "name":
                self.lecturers_tree.column(cid, width=200, anchor="center", stretch=True)
            elif cid == "visualize":
                self.lecturers_tree.column(cid, width=110, anchor="center", stretch=False)
            else:
                self.lecturers_tree.column(cid, width=120, anchor="center", stretch=False)
        self.lecturers_tree.pack(fill=tk.BOTH, expand=True)

        xscroll = ttk.Scrollbar(tree_wrap, orient="horizontal", command=self.lecturers_tree.xview)
        self.lecturers_tree.configure(xscrollcommand=xscroll.set)
        xscroll.pack(fill=tk.X)

        btns = ttk.Frame(frame)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Add", command=self._add_lecturer).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Delete", command=self._delete_lecturer).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Save", command=self._save).pack(side=tk.RIGHT, padx=4)

    def _build_groups_tab(self) -> None:
        frame = ttk.Frame(self.groups_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        cols = ("id", "name", "subjects")
        self.groups_tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        headings = {
            "id": "ID",
            "name": "Name",
            "subjects": "Subject IDs",
        }
        for cid, text in headings.items():
            self.groups_tree.heading(cid, text=text)
            self.groups_tree.column(cid, width=140 if cid != "name" else 200, anchor="center")
        self.groups_tree.pack(fill=tk.BOTH, expand=True)

        btns = ttk.Frame(frame)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Add", command=self._add_group).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Delete", command=self._delete_group).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Save", command=self._save).pack(side=tk.RIGHT, padx=4)

    def _build_config_tab(self) -> None:
        frame = ttk.Frame(self.config_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.config_vars = {
            "weeks": tk.StringVar(),
            "scheduled_days": {},  # Dictionary of {day_name: BooleanVar}
            "year": tk.StringVar(),
            "canton": tk.StringVar(),
        }

        # Rooms info banner
        theory_count, practical_count = self._get_room_counts()
        banner = ttk.Label(frame, text=f"Rooms (default if unspecified): Theory {theory_count}, Practical {practical_count}",
                           font=("Helvetica", 10, "bold"))
        banner.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

        row = 1
        ttk.Label(frame, text="Weeks").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.config_vars["weeks"], width=40).grid(row=row, column=1, sticky="w", pady=4)
        row += 1

        # Days selection (checkboxes)
        ttk.Label(frame, text="Scheduled Days").grid(row=row, column=0, sticky="nw", pady=4)
        days_frame = ttk.Frame(frame)
        days_frame.grid(row=row, column=1, sticky="w", pady=4)
        
        from models import DAY_NAMES
        for day_name in DAY_NAMES:
            var = tk.BooleanVar()
            self.config_vars["scheduled_days"][day_name] = var
            ttk.Checkbutton(days_frame, text=day_name, variable=var).pack(anchor="w")
        
        row += 1
        ttk.Label(frame, text="Year (ISO weeks)").grid(row=row, column=0, sticky="w", pady=4)
        ttk.Entry(frame, textvariable=self.config_vars["year"], width=40).grid(row=row, column=1, sticky="w", pady=4)
        row += 1

        ttk.Label(frame, text="Canton (holidays)").grid(row=row, column=0, sticky="w", pady=4)
        canton_combo = ttk.Combobox(frame, values=list(CANTONS.keys()), textvariable=self.config_vars["canton"], state="readonly", width=37)
        canton_combo.grid(row=row, column=1, sticky="w", pady=4)
        row += 1

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=row, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Apply", command=self._apply_config).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_frame, text="Save", command=self._save).pack(side=tk.LEFT, padx=4)

    def _build_validation_tab(self) -> None:
        frame = ttk.Frame(self.validation_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        ttk.Button(frame, text="Validate", command=self._run_validation).pack(anchor="w")

        run_box = ttk.Frame(frame)
        run_box.pack(fill=tk.X, pady=6)
        ttk.Button(run_box, text="Run Scheduler", command=self._run_scheduler).pack(side=tk.LEFT, padx=4)
        ttk.Button(run_box, text="Open scheduler images", command=self._open_schedule_images_folder).pack(side=tk.LEFT, padx=4)

        self.validation_output = tk.Text(frame, height=18, wrap="word")
        self.validation_output.pack(fill=tk.BOTH, expand=True, pady=8)

    # Data loading and refreshing ------------------------------------
    def _load_initial(self) -> None:
        try:
            self.data = _safe_load(self.file_path)
        except FileNotFoundError:
            self.data = {
                "subjects": [],
                "lecturers": [],
                "student_groups": [],
                "configuration": {
                    "weeks": 15,
                    "scheduled_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                    "timeslots_per_day": 2,
                    "timeslots": ["morning", "afternoon"],
                    "year": 2025,
                },
            }
        self._refresh_all()

    def _refresh_all(self) -> None:
        self._update_summary()
        self._refresh_subjects()
        self._refresh_lecturers()
        self._refresh_groups()
        self._refresh_config()
        self._update_config_tab_title()

    def _update_config_tab_title(self) -> None:
        # Update the Configuration tab label to include room counts
        theory, practical = self._get_room_counts()
        # Keep tab title as just 'Configuration' per request
        if hasattr(self, "notebook") and hasattr(self, "config_tab"):
            self.notebook.tab(self.config_tab, text="Configuration")

    def _get_room_counts(self) -> tuple[int, int]:
        rooms = self.data.get("rooms", []) or []
        if rooms:
            theory = sum(1 for r in rooms if isinstance(r, dict) and r.get("room_type") == "theory")
            practical = sum(1 for r in rooms if isinstance(r, dict) and r.get("room_type") == "practical")
        else:
            # Defaults from data_loader: 10 theory, 1 practical
            theory, practical = 10, 1
        return theory, practical

    def _update_summary(self) -> None:
        cfg = self.data.get("configuration", {})
        self.summary_cards["subjects"].config(text=str(len(self.data.get("subjects", []))))
        self.summary_cards["lecturers"].config(text=str(len(self.data.get("lecturers", []))))
        self.summary_cards["groups"].config(text=str(len(self.data.get("student_groups", []))))
        self.summary_cards["weeks"].config(text=str(cfg.get("weeks", "-")))
        scheduled_days = cfg.get("scheduled_days", [])
        days_str = ", ".join(scheduled_days[:3]) + ("..." if len(scheduled_days) > 3 else "")
        self.summary_cards["days"].config(text=days_str if scheduled_days else "-")
        self.summary_cards["slots"].config(text=str(cfg.get("timeslots_per_day", "-")))

        self._load_summary_image()

        lines = [
            f"File: {self.file_path}",
            "",
            "Timeslots: " + (", ".join(cfg.get("timeslots", [])) if cfg.get("timeslots") else "-"),
            "",
            "Priority lecturers (1-5):",
        ]
        top = [l for l in self.data.get("lecturers", []) if isinstance(l.get("priority"), int) and l.get("priority") <= 5]
        top = sorted(top, key=lambda x: x.get("priority", 99))[:5]
        if top:
            for lec in top:
                lines.append(f"  P{lec.get('priority')}: {lec.get('name', '')}")
        else:
            lines.append("  (none)")

        self.summary_details.config(state=tk.NORMAL)
        self.summary_details.delete("1.0", tk.END)
        self.summary_details.insert(tk.END, "\n".join(lines))
        self.summary_details.config(state=tk.DISABLED)

    def _refresh_subjects(self) -> None:
        self.subjects_tree.delete(*self.subjects_tree.get_children())
        for s in self.data.get("subjects", []):
            self.subjects_tree.insert("", tk.END, values=(
                s.get("id", ""),
                s.get("name", ""),
                s.get("blocks_required", ""),
                s.get("room_type", ""),
                "yes" if s.get("spread") else "no",
            ))
        self.subjects_tree.bind("<Double-1>", self._start_edit_subject_cell)

    def _refresh_lecturers(self) -> None:
        self.lecturers_tree.delete(*self.lecturers_tree.get_children())
        for l in self.data.get("lecturers", []):
            avail = l.get("availability", [])
            label = "patterns" if isinstance(avail, dict) else "list" if isinstance(avail, list) else "-"
            vacations = "-"
            if isinstance(avail, dict):
                blks = avail.get("blackouts", []) or []
                if blks:
                    vacations = f"{len(blks)}"
                else:
                    exc = avail.get("exceptions", []) or []
                    slots = sum(len(e.get("remove", []) or []) for e in exc)
                    if slots:
                        vacations = f"{slots} slots"
            self.lecturers_tree.insert("", tk.END, values=(
                l.get("id", ""),
                l.get("name", ""),
                l.get("subject_id", ""),
                l.get("priority", ""),
                label,
                vacations,
                "view",
            ))
        self.lecturers_tree.bind("<Double-1>", self._start_edit_lecturer_cell)

    def _refresh_groups(self) -> None:
        self.groups_tree.delete(*self.groups_tree.get_children())
        for g in self.data.get("student_groups", []):
            subj_str = ", ".join(g.get("subject_ids", []))
            self.groups_tree.insert("", tk.END, values=(g.get("id", ""), g.get("name", ""), subj_str))
        self.groups_tree.bind("<Double-1>", self._start_edit_group_cell)

    def _refresh_config(self) -> None:
        cfg = self.data.get("configuration", {})
        self.config_vars["weeks"].set(str(cfg.get("weeks", "")))
        
        # Load scheduled days
        scheduled_days = cfg.get("scheduled_days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        for day_name, var in self.config_vars["scheduled_days"].items():
            var.set(day_name in scheduled_days)
        
        self.config_vars["year"].set(str(cfg.get("year", "")))
        self.config_vars["canton"].set(cfg.get("canton", "valais"))

    def _save(self) -> None:
        self._save_to_disk(show_dialog=True)

    def _choose_file(self) -> None:
        path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            self.file_path = path
            self._load_initial()
            self._update_summary()

    def _save_as(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            self.file_path = path
            self._save()
            self._update_summary()

    def _save_to_disk(self, show_dialog: bool = False) -> bool:
        ok, report = validate_data(self.data)
        if not ok:
            if show_dialog:
                messagebox.showerror("Validation failed", "Fix issues before saving. See Run & Validate tab for details.")
                self._render_validation(ok, report)
            return False
        _safe_dump(self.data, self.file_path)
        if show_dialog:
            messagebox.showinfo("Saved", f"Saved to {self.file_path}")
        return True

    # Validation ------------------------------------------------------
    def _run_validation(self) -> None:
        ok, report = validate_data(self.data)
        self._render_validation(ok, report)

    def _render_validation(self, ok: bool, report: List[str]) -> None:
        self.validation_output.delete("1.0", tk.END)
        if ok:
            self.validation_output.insert(tk.END, "✓ All checks passed.\n")
        else:
            self.validation_output.insert(tk.END, "✗ Issues found:\n")
            for e in report:
                self.validation_output.insert(tk.END, f"- {e}\n")

    # External runners ----------------------------------------------
    def _run_script(self, script: str) -> None:
        try:
            # When running as a PyInstaller app, call bundled helper EXEs on Windows
            if getattr(sys, 'frozen', False):
                exe_name = None
                if os.name == 'nt':
                    mapping = {
                        'main.py': 'PlannerScheduler.exe',
                        'visualize_schedule.py': 'PlannerVisualizeSchedule.exe',
                        'visualize_input_data.py': 'PlannerVisualizeInput.exe',
                    }
                    exe_name = mapping.get(script)
                    if exe_name:
                        exe_path = os.path.join(os.path.dirname(sys.executable), exe_name)
                        proc = subprocess.run([exe_path], capture_output=True, text=True, cwd=os.path.dirname(sys.executable))
                    else:
                        proc = subprocess.run([sys.executable], capture_output=True, text=True, cwd=os.path.dirname(sys.executable))
                else:
                    # On macOS/Linux, try running the unfrozen Python with the script (developer environment)
                    proc = subprocess.run([sys.executable, script], capture_output=True, text=True, cwd=".")
            else:
                proc = subprocess.run([sys.executable, script], capture_output=True, text=True, cwd=".")
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not find {script}")
            return

        output = proc.stdout.strip()
        err = proc.stderr.strip()

        self.validation_output.delete("1.0", tk.END)
        self.validation_output.insert(tk.END, f"Command: {script}\nExit code: {proc.returncode}\n\n")
        if output:
            self.validation_output.insert(tk.END, "STDOUT:\n" + output + "\n\n")
        if err:
            self.validation_output.insert(tk.END, "STDERR:\n" + err + "\n")

        if proc.returncode == 0:
            messagebox.showinfo("Done", f"{script} finished successfully")
        else:
            messagebox.showerror("Failed", f"{script} exited with code {proc.returncode}")

    def _run_scheduler(self) -> None:
        self._run_script("main.py")

    def _visualize_input(self) -> None:
        self._run_script("visualize_input_data.py")

    def _visualize_schedule(self) -> None:
        self._run_script("visualize_schedule.py")

    # Subject handlers -----------------------------------------------
    def _add_subject(self) -> None:
        self._subject_form()

    def _edit_subject(self) -> None:
        return

    def _delete_subject(self) -> None:
        sel = self.subjects_tree.selection()
        if not sel:
            return
        idx = self.subjects_tree.index(sel[0])
        del self.data["subjects"][idx]
        self._refresh_all()

    def _subject_form(self, index: Optional[int] = None) -> None:
        win = tk.Toplevel(self.root)
        win.title("Subject")
        subj = self.data["subjects"][index] if index is not None else {}

        vars_map = {
            "id": tk.StringVar(value=subj.get("id", "")),
            "name": tk.StringVar(value=subj.get("name", "")),
            "blocks_required": tk.StringVar(value=subj.get("blocks_required", "")),
            "room_type": tk.StringVar(value=subj.get("room_type", "theory")),
            "spread": tk.BooleanVar(value=subj.get("spread", False)),
        }

        row = 0
        for key, label in (
            ("id", "ID"),
            ("name", "Name"),
            ("blocks_required", "Blocks required"),
        ):
            ttk.Label(win, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=6)
            ttk.Entry(win, textvariable=vars_map[key], width=30).grid(row=row, column=1, pady=4, padx=6)
            row += 1

        ttk.Label(win, text="Room type").grid(row=row, column=0, sticky="w", pady=4, padx=6)
        room_combo = ttk.Combobox(win, values=["theory", "practical"], textvariable=vars_map["room_type"], state="readonly")
        room_combo.grid(row=row, column=1, pady=4, padx=6)
        row += 1

        ttk.Checkbutton(win, text="Spread", variable=vars_map["spread"]).grid(row=row, column=0, sticky="w", pady=4, padx=6)
        row += 1

        def submit() -> None:
            try:
                blocks = int(vars_map["blocks_required"].get())
            except ValueError:
                messagebox.showerror("Invalid", "Blocks required must be an integer")
                return
            new_obj = {
                "id": vars_map["id"].get().strip(),
                "name": vars_map["name"].get().strip(),
                "blocks_required": blocks,
                "room_type": vars_map["room_type"].get(),
                "spread": bool(vars_map["spread"].get()),
            }
            if index is None:
                self.data["subjects"].append(new_obj)
            else:
                self.data["subjects"][index] = new_obj
            self._refresh_all()
            self._save_to_disk(show_dialog=False)
            win.destroy()

        ttk.Button(win, text="Save", command=submit).grid(row=row, column=0, columnspan=2, pady=10)

    # Lecturer handlers ----------------------------------------------
    def _add_lecturer(self) -> None:
        self._lecturer_form()

    def _edit_lecturer(self) -> None:
        return

    def _start_edit_lecturer_cell(self, event: tk.Event) -> None:
        row_id = self.lecturers_tree.identify_row(event.y)
        col_id = self.lecturers_tree.identify_column(event.x)
        if not row_id or not col_id:
            return
        col_idx = int(col_id.replace("#", "")) - 1
        bbox = self.lecturers_tree.bbox(row_id, col_id)
        if not bbox:
            return
        item_index = self.lecturers_tree.index(row_id)
        lecturer = self.data["lecturers"][item_index]

        # Availability column opens the availability editor directly
        if col_idx == 4:
            new_avail = self._availability_editor(lecturer.get("availability", []))
            if new_avail is not None:
                lecturer["availability"] = new_avail
                self._refresh_all()
            return

        # Vacations column opens dedicated calendar-based vacation editor
        if col_idx == 5:
            current = lecturer.get("availability", {})
            if not isinstance(current, dict):
                current = {"patterns": [], "exceptions": [], "blackouts": []}
            new_avail = self._vacation_calendar_editor(current)
            if new_avail is not None:
                lecturer["availability"] = new_avail
                self._refresh_all()
            return

        # Visualize column: open read-only availability calendar
        if col_idx == 6:
            self._visualize_lecturer_availability(lecturer)
            return

        x, y, w, h = bbox
        current_values = list(self.lecturers_tree.item(row_id, "values"))
        current_value = current_values[col_idx]

        entry = tk.Entry(self.lecturers_tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, current_value)
        entry.focus()

        def commit(event: tk.Event | None = None) -> None:
            new_val = entry.get().strip()
            entry.destroy()
            try:
                if col_idx == 0:
                    lecturer["id"] = new_val
                elif col_idx == 1:
                    lecturer["name"] = new_val
                elif col_idx == 2:
                    lecturer["subject_id"] = new_val
                elif col_idx == 3:
                    lecturer["priority"] = int(new_val)
            except ValueError:
                messagebox.showerror("Invalid", "Priority must be an integer")
                return
            self._refresh_all()

        entry.bind("<Return>", commit)
        entry.bind("<FocusOut>", commit)
        entry.bind("<Escape>", lambda e: entry.destroy())

    def _delete_lecturer(self) -> None:
        sel = self.lecturers_tree.selection()
        if not sel:
            return
        idx = self.lecturers_tree.index(sel[0])
        del self.data["lecturers"][idx]
        self._refresh_all()

    def _lecturer_form(self, index: Optional[int] = None) -> None:
        win = tk.Toplevel(self.root)
        win.title("Lecturer")
        lec = self.data["lecturers"][index] if index is not None else {}

        vars_map = {
            "id": tk.StringVar(value=lec.get("id", "")),
            "name": tk.StringVar(value=lec.get("name", "")),
            "subject_id": tk.StringVar(value=lec.get("subject_id", "")),
            "priority": tk.StringVar(value=lec.get("priority", "")),
        }

        row = 0
        for key, label in (
            ("id", "ID"),
            ("name", "Name"),
            ("subject_id", "Subject ID"),
            ("priority", "Priority"),
        ):
            ttk.Label(win, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=6)
            ttk.Entry(win, textvariable=vars_map[key], width=34).grid(row=row, column=1, pady=4, padx=6)
            row += 1

        avail_preview = tk.StringVar(value="patterns" if isinstance(lec.get("availability"), dict) else "list" if isinstance(lec.get("availability"), list) else "-")
        ttk.Label(win, text="Availability").grid(row=row, column=0, sticky="w", pady=4, padx=6)
        ttk.Label(win, textvariable=avail_preview).grid(row=row, column=1, sticky="w", pady=4, padx=6)
        row += 1

        def open_availability() -> None:
            new_avail = self._availability_editor(lec.get("availability", []))
            if new_avail is not None:
                lec["availability"] = new_avail
                avail_preview.set("patterns" if isinstance(new_avail, dict) else "list")

        ttk.Button(win, text="Edit availability", command=open_availability).grid(row=row, column=0, columnspan=2, pady=6)
        row += 1

        def submit() -> None:
            try:
                prio = int(vars_map["priority"].get())
            except ValueError:
                messagebox.showerror("Invalid", "Priority must be an integer")
                return
            new_obj = {
                "id": vars_map["id"].get().strip(),
                "name": vars_map["name"].get().strip(),
                "subject_id": vars_map["subject_id"].get().strip(),
                "priority": prio,
                "availability": lec.get("availability", []),
            }
            if index is None:
                self.data["lecturers"].append(new_obj)
            else:
                self.data["lecturers"][index] = new_obj
            self._refresh_all()
            self._save_to_disk(show_dialog=False)
            win.destroy()

        ttk.Button(win, text="Save", command=submit).grid(row=row, column=0, columnspan=2, pady=10)

    def _availability_editor(self, current: Any) -> Any | None:
        win = tk.Toplevel(self.root)
        win.title("Availability")
        win.geometry("520x520")

        cfg_timeslots = self.data.get("configuration", {}).get("timeslots", ["morning", "afternoon"])
        weeks = self.data.get("configuration", {}).get("weeks", 15)

        builder_frame = ttk.LabelFrame(win, text="Quick pattern")
        builder_frame.pack(fill=tk.X, padx=8, pady=6)

        week_expr = tk.StringVar(value=f"1-{weeks}")
        ttk.Label(builder_frame, text="Weeks (e.g., 1-15,7)").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(builder_frame, textvariable=week_expr, width=30).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        day_slot_vars: Dict[str, Dict[str, tk.BooleanVar]] = {}
        for r, day in enumerate(DAY_LABELS, start=1):
            ttk.Label(builder_frame, text=day).grid(row=r, column=0, sticky="w", padx=6, pady=2)
            slot_vars: Dict[str, tk.BooleanVar] = {}
            for c, slot in enumerate(cfg_timeslots, start=1):
                var = tk.BooleanVar(value=False)
                ttk.Checkbutton(builder_frame, text=slot, variable=var).grid(row=r, column=c, sticky="w", padx=4, pady=2)
                slot_vars[slot] = var
            day_slot_vars[day] = slot_vars

        def apply_quick() -> None:
            nonlocal result
            pattern_days: Dict[str, List[str]] = {}
            for day, slots in day_slot_vars.items():
                chosen = [slot for slot, var in slots.items() if var.get()]
                if chosen:
                    pattern_days[day] = chosen
            if not pattern_days:
                messagebox.showwarning("No slots", "Select at least one slot to create a pattern")
                return
            # Create pattern and save directly
            result = {"patterns": [{"weeks": week_expr.get().strip(), "days": pattern_days}], "exceptions": [], "blackouts": []}
            win.destroy()

        ttk.Button(builder_frame, text="Apply pattern (saves & closes)", command=apply_quick).grid(row=len(DAY_LABELS) + 1, column=0, columnspan=2, pady=6)

        ttk.Label(win, text="OR manually edit availability JSON below and click 'Use value'").pack(anchor="w", padx=8, pady=(8, 0))
        ttk.Label(win, text="(list or pattern dict format)").pack(anchor="w", padx=8)
        raw_editor = tk.Text(win, height=16, wrap="word")
        raw_editor.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        raw_editor.insert(tk.END, json.dumps(current, indent=2))

        result: Dict[str, Any] | List[Any] | None = None

        def save_and_close() -> None:
            nonlocal result
            text = raw_editor.get("1.0", tk.END).strip()
            if not text:
                result = []
                win.destroy()
                return
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as exc:
                messagebox.showerror("Invalid JSON", f"Could not parse availability: {exc}")
                return
            if not isinstance(parsed, (list, dict)):
                messagebox.showerror("Invalid", "Availability must be list or dict")
                return
            result = parsed
            win.destroy()

        ttk.Button(win, text="Use value", command=save_and_close).pack(pady=8)
        win.wait_window()
        return result

    def _vacation_editor(self, blackouts: List[dict]) -> List[dict] | None:
        win = tk.Toplevel(self.root)
        win.title("Vacations / Blackouts")
        win.geometry("560x520")

        # Help section with clear guidance and examples
        help_frame = ttk.LabelFrame(win, text="How to fill in vacations")
        help_frame.pack(fill=tk.X, padx=8, pady=8)
        help_text = (
            "Enter a list of blackout entries. Each entry blocks a lecturer for whole or partial weeks.\n"
            "Format per entry: {from_week: int, to_week: int, days: [Mon..Fri]}\n"
            "Notes:\n"
            "- Use week numbers starting at 1.\n"
            "- days can be omitted or [] to block ALL days in the range.\n"
            "Examples:\n"
            "  • Single day in one week: {\"from_week\": 7, \"to_week\": 7, \"days\": [\"Fri\"]}\n"
            "  • Whole weeks 10–12: {\"from_week\": 10, \"to_week\": 12, \"days\": []}\n"
            "  • Multiple days in one week: {\"from_week\": 5, \"to_week\": 5, \"days\": [\"Mon\", \"Wed\"]}"
        )
        ttk.Label(help_frame, text=help_text, justify="left").pack(fill=tk.X, padx=8, pady=6)

        # Quick add form
        builder = ttk.LabelFrame(win, text="Quick add blackout")
        builder.pack(fill=tk.X, padx=8, pady=6)
        from_var = tk.StringVar()
        to_var = tk.StringVar()
        ttk.Label(builder, text="From week").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(builder, textvariable=from_var, width=8).grid(row=0, column=1, sticky="w", padx=6, pady=4)
        ttk.Label(builder, text="To week").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        ttk.Entry(builder, textvariable=to_var, width=8).grid(row=0, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(builder, text="Days").grid(row=1, column=0, sticky="w", padx=6)
        day_vars: Dict[str, tk.BooleanVar] = {}
        for i, day in enumerate(DAY_LABELS):
            var = tk.BooleanVar(value=False)
            ttk.Checkbutton(builder, text=day, variable=var).grid(row=1, column=1 + i, sticky="w", padx=4)
            day_vars[day] = var

        def add_blackout_entry() -> None:
            try:
                fw = int(from_var.get())
                tw = int(to_var.get())
            except ValueError:
                messagebox.showerror("Invalid", "From/To week must be integers")
                return
            if fw <= 0 or tw <= 0:
                messagebox.showerror("Invalid", "Weeks must be positive integers (starting at 1)")
                return
            if fw > tw:
                fw, tw = tw, fw
            chosen_days = [d for d, v in day_vars.items() if v.get()]
            # Read current JSON, append, and write back
            try:
                current = json.loads(text.get("1.0", tk.END) or "[]")
            except json.JSONDecodeError as exc:
                messagebox.showerror("Invalid JSON", f"Fix JSON before adding: {exc}")
                return
            if not isinstance(current, list):
                messagebox.showerror("Invalid JSON", "Root must be a list of blackout entries")
                return
            current.append({"from_week": fw, "to_week": tw, "days": chosen_days})
            text.delete("1.0", tk.END)
            text.insert(tk.END, json.dumps(current, indent=2))

        ttk.Button(builder, text="Add entry", command=add_blackout_entry).grid(row=0, column=4, rowspan=2, padx=8)

        example_bar = ttk.Frame(win)
        example_bar.pack(fill=tk.X, padx=8, pady=4)

        def insert_example_single():
            text.delete("1.0", tk.END)
            text.insert(tk.END, json.dumps([
                {"from_week": 7, "to_week": 7, "days": ["Fri"]}
            ], indent=2))

        def insert_example_range():
            text.delete("1.0", tk.END)
            text.insert(tk.END, json.dumps([
                {"from_week": 10, "to_week": 12, "days": []}
            ], indent=2))

        ttk.Button(example_bar, text="Insert example: Week 7 (Fri)", command=insert_example_single).pack(side=tk.LEFT, padx=4)
        ttk.Button(example_bar, text="Insert example: Weeks 10–12 (all days)", command=insert_example_range).pack(side=tk.LEFT, padx=4)

        # Raw JSON editor
        ttk.Label(win, text="Blackouts JSON (editable)").pack(anchor="w", padx=8)
        text = tk.Text(win, height=12, wrap="word")
        text.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        text.insert(tk.END, json.dumps(blackouts or [], indent=2))

        result: List[dict] | None = None

        def save_and_close() -> None:
            nonlocal result
            try:
                parsed = json.loads(text.get("1.0", tk.END))
            except json.JSONDecodeError as exc:
                messagebox.showerror("Invalid JSON", f"Could not parse blackouts: {exc}")
                return
            if not isinstance(parsed, list):
                messagebox.showerror("Invalid", "Blackouts must be a list of objects")
                return
            # Basic structural validation and day name check
            allowed_days = set(DAY_LABELS)
            for idx, item in enumerate(parsed):
                if not isinstance(item, dict):
                    messagebox.showerror("Invalid", f"Entry {idx+1} must be an object")
                    return
                fw = item.get("from_week")
                tw = item.get("to_week")
                days = item.get("days", [])
                if not isinstance(fw, int) or not isinstance(tw, int) or fw <= 0 or tw <= 0:
                    messagebox.showerror("Invalid", f"Entry {idx+1}: from_week/to_week must be positive integers")
                    return
                if not isinstance(days, list):
                    messagebox.showerror("Invalid", f"Entry {idx+1}: days must be a list (or omitted)")
                    return
                for d in days:
                    if d not in allowed_days:
                        messagebox.showerror("Invalid", f"Entry {idx+1}: invalid day '{d}' (use Mon..Fri)")
                        return
            result = parsed
            win.destroy()

        ttk.Button(win, text="Save", command=save_and_close).pack(pady=8)
        win.wait_window()
        return result

    def _vacation_calendar_editor(self, availability: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # Interactive multi-week grid; compiles to exceptions (remove slots)
        from datetime import date
        cfg = self.data.get("configuration", {})
        weeks_total = int(cfg.get("weeks", 15))
        year = int(cfg.get("year", date.today().year))
        timeslots = cfg.get("timeslots", ["morning", "afternoon"])[:2] or ["morning", "afternoon"]

        win = tk.Toplevel(self.root)
        win.title("Edit Vacations (select AM/PM per day across all weeks)")
        win.geometry("900x700")

        ttk.Label(win, text=f"Year: {year} — Select slots to mark as vacation (removed)").pack(anchor="w", padx=10, pady=8)

        # Build scrollable area
        wrap = ttk.Frame(win)
        wrap.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(wrap, highlightthickness=0)
        vscroll = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        inner = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor="nw")

        def on_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", on_configure)

        # Selected vacation slots: set of (week, day_int, timeslot)
        selected: set[tuple[int, int, str]] = set()
        
        # Store checkbox variables for updating when using Select/Clear week buttons
        checkbox_vars: dict[tuple[int, int, str], tk.BooleanVar] = {}

        # Preload from availability exceptions (remove) and blackouts
        exc_list = availability.get("exceptions", []) or []
        for exc in exc_list:
            w = exc.get("week")
            dname = exc.get("day")
            removes = exc.get("remove", []) or []
            if isinstance(w, int) and dname in DAY_LABELS:
                d_idx = DAY_LABELS.index(dname) + 1
                for sl in removes:
                    if sl in timeslots:
                        selected.add((w, d_idx, sl))
        blks = availability.get("blackouts", []) or []
        for blk in blks:
            fw = blk.get("from_week")
            tw = blk.get("to_week")
            days = blk.get("days", []) or DAY_LABELS
            if isinstance(fw, int) and isinstance(tw, int):
                if fw > tw:
                    fw, tw = tw, fw
                for w in range(fw, tw + 1):
                    for dname in days:
                        if dname in DAY_LABELS:
                            d_idx = DAY_LABELS.index(dname) + 1
                            for sl in timeslots:
                                selected.add((w, d_idx, sl))

        # Place week frames in columns to fill window
        columns = 3 if weeks_total >= 9 else 2
        for w in range(1, weeks_total + 1):
            r = (w - 1) // columns
            c = (w - 1) % columns
            try:
                start_dt = date.fromisocalendar(year, w, 1)
                end_dt = date.fromisocalendar(year, w, 5)
                title = f"Week {w}: {start_dt.strftime('%d %b')}–{end_dt.strftime('%d %b')}"
            except Exception:
                title = f"Week {w}"
            panel = ttk.LabelFrame(inner, text=title, padding=6)
            panel.grid(row=r, column=c, padx=8, pady=8, sticky="n")

            # Quick week actions (row 0)
            action_row = ttk.Frame(panel)
            action_row.grid(row=0, column=0, columnspan=len(timeslots)+1, sticky="w", pady=(0, 6))
            def make_select_week(_w=w):
                def select_all():
                    for d in range(1, 6):
                        for sl in timeslots:
                            key = (_w, d, sl)
                            selected.add(key)
                            if key in checkbox_vars:
                                checkbox_vars[key].set(True)
                return select_all
            def make_clear_week(_w=w):
                def clear_all():
                    for d in range(1, 6):
                        for sl in timeslots:
                            key = (_w, d, sl)
                            selected.discard(key)
                            if key in checkbox_vars:
                                checkbox_vars[key].set(False)
                return clear_all
            ttk.Button(action_row, text="Select week", command=make_select_week()).pack(side=tk.LEFT, padx=2)
            ttk.Button(action_row, text="Clear week", command=make_clear_week()).pack(side=tk.LEFT, padx=2)

            # Header row (row 1)
            ttk.Label(panel, text="").grid(row=1, column=0, padx=4)
            for i, sl in enumerate(timeslots, start=1):
                ttk.Label(panel, text=sl.capitalize()).grid(row=1, column=i, padx=4)
            # Days rows (starting row 2)
            for d_idx, day in enumerate(DAY_LABELS, start=1):
                try:
                    dt = date.fromisocalendar(year, w, d_idx)
                    dlabel = f"{day} {dt.strftime('%d %b')}"
                except Exception:
                    dlabel = day
                ttk.Label(panel, text=dlabel).grid(row=d_idx+1, column=0, sticky="w", padx=4, pady=2)
                for i, sl in enumerate(timeslots, start=1):
                    key = (w, d_idx, sl)
                    var = tk.BooleanVar(value=key in selected)
                    checkbox_vars[key] = var  # Store reference for Select/Clear week buttons
                    def make_toggle(_key=key, _var=var):
                        def _toggle():
                            if _var.get():
                                selected.add(_key)
                            else:
                                selected.discard(_key)
                        return _toggle
                    ttk.Checkbutton(panel, variable=var, command=make_toggle()).grid(row=d_idx+1, column=i, padx=4)

        # Save button handler
        result = None
        def save_and_close() -> None:
            nonlocal result
            # Recompute grouped from current selected set
            from collections import defaultdict
            grouped = defaultdict(set)
            for w, d, sl in selected:
                grouped[(w, d)].add(sl)
            
            exceptions = []
            for (w, d), slots in grouped.items():
                day_name = DAY_LABELS[d - 1]
                exceptions.append({"week": w, "day": day_name, "remove": sorted(slots)})
            result = {
                "patterns": availability.get("patterns", []),
                "exceptions": exceptions,
                "blackouts": [],
            }
            win.destroy()

        footer = ttk.Frame(win)
        footer.pack(fill=tk.X, padx=10, pady=8)
        ttk.Button(footer, text="Save", command=save_and_close).pack(side=tk.RIGHT)
        ttk.Button(footer, text="Cancel", command=win.destroy).pack(side=tk.RIGHT, padx=8)

        win.wait_window()
        return result

    def _load_summary_image(self) -> None:
        # Load and display image.jpeg in the summary tab
        try:
            from PIL import Image, ImageTk
            image_path = os.path.join(os.path.dirname(self.file_path), "image.jpeg")
            if not os.path.exists(image_path):
                # Try current directory if not found next to JSON file
                image_path = "image.jpeg"
            if os.path.exists(image_path):
                img = Image.open(image_path)
                # Resize to fit nicely in the summary (max width 500, maintain aspect ratio)
                max_width = 500
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.calendar_image_label.config(image=photo)
                self.calendar_image_label.image = photo  # Keep a reference
            else:
                self.calendar_image_label.config(text="(image.jpeg not found)")
        except ImportError:
            self.calendar_image_label.config(text="(PIL/Pillow not installed)")
        except Exception as e:
            self.calendar_image_label.config(text=f"(Error loading image: {e})")

    def _open_images_folder(self) -> None:
        images_path = os.path.join(os.getcwd(), "images")
        if not os.path.isdir(images_path):
            messagebox.showinfo("Not found", "images folder does not exist yet.")
            return
        try:
            if sys.platform.startswith("darwin"):
                subprocess.run(["open", images_path], check=False)
            elif os.name == "nt":
                os.startfile(images_path)  # type: ignore[attr-defined]
            else:
                subprocess.run(["xdg-open", images_path], check=False)
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Error", f"Could not open images folder: {exc}")

    def _open_schedule_images_folder(self) -> None:
        schedule_path = os.path.join(os.getcwd(), "images", "schedule")
        if not os.path.isdir(schedule_path):
            messagebox.showinfo("Not found", "images/schedule folder does not exist yet. Run the scheduler first.")
            return
        try:
            if sys.platform.startswith("darwin"):
                subprocess.run(["open", schedule_path], check=False)
            elif os.name == "nt":
                os.startfile(schedule_path)  # type: ignore[attr-defined]
            else:
                subprocess.run(["xdg-open", schedule_path], check=False)
        except Exception as exc:  # pragma: no cover
            messagebox.showerror("Error", f"Could not open schedule images folder: {exc}")

    def _visualize_lecturer_availability(self, lecturer: Dict[str, Any]) -> None:
        from datetime import date
        cfg = self.data.get("configuration", {})
        weeks_total = int(cfg.get("weeks", 15))
        year = int(cfg.get("year", date.today().year))
        canton = cfg.get("canton", "valais")
        timeslots = cfg.get("timeslots", ["morning", "afternoon"])[:2] or ["morning", "afternoon"]

        raw_avail = lecturer.get("availability", [])
        # Expand availability; for priority>5 and empty availability, treat as always available
        expanded = set()
        try:
            expanded = _expand_availability(raw_avail, weeks_total)
        except Exception:
            expanded = set()
        if (not expanded) and isinstance(lecturer.get("priority"), int) and lecturer.get("priority") > 5:
            for w in range(1, weeks_total + 1):
                for d in range(1, 6):
                    for sl in timeslots:
                        expanded.add((w, d, sl))

        # Normalize to string slots for rendering
        norm: set[tuple[int, int, str]] = set()
        for w, d, ts in expanded:
            slot = ts.value if hasattr(ts, "value") else ts
            norm.add((w, d, slot))

        win = tk.Toplevel(self.root)
        win.title(f"Availability: {lecturer.get('name','')}")
        win.geometry("900x700")

        ttk.Label(win, text=f"Year: {year}, Canton: {canton.upper()} — Green = available | Red = holiday").pack(anchor="w", padx=10, pady=8)

        wrap = ttk.Frame(win)
        wrap.pack(fill=tk.BOTH, expand=True)
        canvas = tk.Canvas(wrap, highlightthickness=0)
        vscroll = ttk.Scrollbar(wrap, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vscroll.set)
        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        inner = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=inner, anchor="nw")
        def on_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        inner.bind("<Configure>", on_configure)

        columns = 3 if weeks_total >= 9 else 2
        for w in range(1, weeks_total + 1):
            r = (w - 1) // columns
            c = (w - 1) % columns
            try:
                start_dt = date.fromisocalendar(year, w, 1)
                end_dt = date.fromisocalendar(year, w, 5)
                title = f"Week {w}: {start_dt.strftime('%d %b')}–{end_dt.strftime('%d %b')}"
            except Exception:
                title = f"Week {w}"
            panel = ttk.LabelFrame(inner, text=title, padding=6)
            panel.grid(row=r, column=c, padx=8, pady=8, sticky="n")

            ttk.Label(panel, text="").grid(row=0, column=0, padx=4)
            for i, sl in enumerate(timeslots, start=1):
                ttk.Label(panel, text=sl.capitalize()).grid(row=0, column=i, padx=4)
            for d_idx, day in enumerate(DAY_LABELS, start=1):
                try:
                    dt = date.fromisocalendar(year, w, d_idx)
                    dlabel = f"{day} {dt.strftime('%d %b')}"
                    # Check if this day is a holiday
                    is_hol = is_holiday(canton, year, dt.month, dt.day)
                except Exception:
                    dlabel = day
                    is_hol = False
                ttk.Label(panel, text=dlabel).grid(row=d_idx, column=0, sticky="w", padx=4, pady=2)
                for i, sl in enumerate(timeslots, start=1):
                    x = ttk.Frame(panel, width=18, height=18)
                    x.grid_propagate(False)
                    x.grid(row=d_idx, column=i, padx=4, pady=2)
                    # Red for holidays, green for available, grey for unavailable
                    if is_hol:
                        color = "#ff6b6b"  # red
                    elif (w, d_idx, sl) in norm:
                        color = "#66bb6a"  # green
                    else:
                        color = "#dddddd"  # grey
                    cell = tk.Canvas(x, width=18, height=18, highlightthickness=0, bg=color)
                    cell.pack(fill=tk.BOTH, expand=True)

    def _add_group(self) -> None:
        self._group_form()

    def _edit_group(self) -> None:
        return

    def _delete_group(self) -> None:
        sel = self.groups_tree.selection()
        if not sel:
            return
        idx = self.groups_tree.index(sel[0])
        del self.data["student_groups"][idx]
        self._refresh_all()

    def _group_form(self, index: Optional[int] = None) -> None:
        win = tk.Toplevel(self.root)
        win.title("Student Group")
        grp = self.data["student_groups"][index] if index is not None else {}

        vars_map = {
            "id": tk.StringVar(value=grp.get("id", "")),
            "name": tk.StringVar(value=grp.get("name", "")),
            "subject_ids": tk.StringVar(value=", ".join(grp.get("subject_ids", []))),
        }

        row = 0
        for key, label in (
            ("id", "ID"),
            ("name", "Name"),
            ("subject_ids", "Subject IDs (comma separated)"),
        ):
            ttk.Label(win, text=label).grid(row=row, column=0, sticky="w", pady=4, padx=6)
            ttk.Entry(win, textvariable=vars_map[key], width=40).grid(row=row, column=1, pady=4, padx=6)
            row += 1

        def submit() -> None:
            subj_ids = [s.strip() for s in vars_map["subject_ids"].get().split(",") if s.strip()]
            new_obj = {
                "id": vars_map["id"].get().strip(),
                "name": vars_map["name"].get().strip(),
                "subject_ids": subj_ids,
            }
            if index is None:
                self.data["student_groups"].append(new_obj)
            else:
                self.data["student_groups"][index] = new_obj
            self._refresh_all()
            self._save_to_disk(show_dialog=False)
            win.destroy()

        ttk.Button(win, text="Save", command=submit).grid(row=row, column=0, columnspan=2, pady=10)

    # Config handlers -------------------------------------------------
    def _apply_config(self) -> None:
        cfg = self.data.get("configuration", {})
        try:
            cfg["weeks"] = int(self.config_vars["weeks"].get())
        except ValueError:
            messagebox.showerror("Invalid", "Weeks must be an integer")
            return
        
        # Collect selected days
        scheduled_days = [day for day, var in self.config_vars["scheduled_days"].items() if var.get()]
        if not scheduled_days:
            messagebox.showerror("Invalid", "Select at least one day")
            return
        cfg["scheduled_days"] = sorted(scheduled_days, key=lambda d: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"].index(d))
        
        try:
            yr = int(self.config_vars["year"].get()) if self.config_vars["year"].get().strip() else None
        except ValueError:
            yr = None
        if yr:
            cfg["year"] = yr
        canton = self.config_vars["canton"].get().strip().lower()
        if canton in CANTONS:
            cfg["canton"] = canton
        self._refresh_config()

    def _start_edit_subject_cell(self, event: tk.Event) -> None:
        row_id = self.subjects_tree.identify_row(event.y)
        col_id = self.subjects_tree.identify_column(event.x)
        if not row_id or not col_id:
            return
        col_idx = int(col_id.replace("#", "")) - 1
        bbox = self.subjects_tree.bbox(row_id, col_id)
        if not bbox:
            return
        x, y, w, h = bbox
        item_index = self.subjects_tree.index(row_id)
        current_values = list(self.subjects_tree.item(row_id, "values"))
        current_value = current_values[col_idx]

        entry = tk.Entry(self.subjects_tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, current_value)
        entry.focus()

        def commit(event: tk.Event | None = None) -> None:
            new_val = entry.get().strip()
            entry.destroy()
            subj = self.data["subjects"][item_index]
            if col_idx == 0:
                subj["id"] = new_val
            elif col_idx == 1:
                subj["name"] = new_val
            elif col_idx == 2:
                try:
                    subj["blocks_required"] = int(new_val) if new_val else 0
                except ValueError:
                    pass
            elif col_idx == 3:
                subj["room_type"] = new_val
            elif col_idx == 4:
                subj["spread"] = new_val.lower() in ("yes", "true", "1")
            self._refresh_all()
            self._save_to_disk(show_dialog=False)

        entry.bind("<Return>", commit)
        entry.bind("<FocusOut>", commit)
        entry.bind("<Escape>", lambda e: entry.destroy())

    def _start_edit_group_cell(self, event: tk.Event) -> None:
        row_id = self.groups_tree.identify_row(event.y)
        col_id = self.groups_tree.identify_column(event.x)
        if not row_id or not col_id:
            return
        col_idx = int(col_id.replace("#", "")) - 1
        bbox = self.groups_tree.bbox(row_id, col_id)
        if not bbox:
            return
        x, y, w, h = bbox
        item_index = self.groups_tree.index(row_id)
        current_values = list(self.groups_tree.item(row_id, "values"))
        current_value = current_values[col_idx]

        entry = tk.Entry(self.groups_tree)
        entry.place(x=x, y=y, width=w, height=h)
        entry.insert(0, current_value)
        entry.focus()

        def commit(event: tk.Event | None = None) -> None:
            new_val = entry.get().strip()
            entry.destroy()
            grp = self.data["student_groups"][item_index]
            if col_idx == 0:
                grp["id"] = new_val
            elif col_idx == 1:
                grp["name"] = new_val
            elif col_idx == 2:
                grp["subject_ids"] = [s.strip() for s in new_val.split(",") if s.strip()]
            self._refresh_all()

        entry.bind("<Return>", commit)
        entry.bind("<FocusOut>", commit)
        entry.bind("<Escape>", lambda e: entry.destroy())

    # Window sizing --------------------------------------------------
    def _ensure_min_window_size(self) -> None:
        try:
            # Sum configured widths of lecturer columns
            total = 0
            for cid in self.lecturers_tree["columns"]:
                try:
                    w = int(self.lecturers_tree.column(cid, "width"))
                except Exception:
                    w = 120
                total += w
            # Add padding for tree borders, scrollbar, margins
            total += 120
            min_w = max(1200, total)
            min_h = 800
            # Apply minsize and expand current geometry if smaller
            self.root.minsize(min_w, min_h)
            self.root.update_idletasks()
            cur_w = self.root.winfo_width()
            cur_h = self.root.winfo_height()
            if cur_w < min_w or cur_h < min_h:
                self.root.geometry(f"{max(cur_w, min_w)}x{max(cur_h, min_h)}")
        except Exception:
            # Fallback minimal sizing
            self.root.minsize(1200, 800)


def main() -> None:
    root = tk.Tk()
    root.geometry("1280x850")
    root.minsize(1200, 800)
    InputEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
