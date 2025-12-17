"""Tkinter-based editor for input_data.json.

Provides tabbed views for Subjects, Lecturers, Student Groups, and Configuration.
Includes availability editor that supports quick pattern creation plus raw JSON editing.
Runs existing validation before saving.
"""
import json
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Any, Dict, List, Optional

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
        self.notebook.add(self.subjects_tab, text="Subjects")
        self.notebook.add(self.lecturers_tab, text="Lecturers")
        self.notebook.add(self.groups_tab, text="Student Groups")
        self.notebook.add(self.config_tab, text="Configuration")
        self.notebook.add(self.validation_tab, text="Run & Validate")

        self._build_summary_tab()
        self._build_subjects_tab()
        self._build_lecturers_tab()
        self._build_groups_tab()
        self._build_config_tab()
        self._build_validation_tab()

    def _build_summary_tab(self) -> None:
        self.summary_info = tk.StringVar()
        label = ttk.Label(self.summary_tab, textvariable=self.summary_info, anchor="w", justify="left")
        label.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

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
        ttk.Button(btns, text="Edit", command=self._edit_subject).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Delete", command=self._delete_subject).pack(side=tk.LEFT, padx=4)

    def _build_lecturers_tab(self) -> None:
        frame = ttk.Frame(self.lecturers_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        cols = ("id", "name", "subject_id", "priority", "availability_type")
        self.lecturers_tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        headings = {
            "id": "ID",
            "name": "Name",
            "subject_id": "Subject",
            "priority": "Priority",
            "availability_type": "Availability",
        }
        for cid, text in headings.items():
            self.lecturers_tree.heading(cid, text=text)
            self.lecturers_tree.column(cid, width=120 if cid != "name" else 200, anchor="center")
        self.lecturers_tree.pack(fill=tk.BOTH, expand=True)

        btns = ttk.Frame(frame)
        btns.pack(fill=tk.X, pady=6)
        ttk.Button(btns, text="Add", command=self._add_lecturer).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Edit", command=self._edit_lecturer).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Delete", command=self._delete_lecturer).pack(side=tk.LEFT, padx=4)

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
        ttk.Button(btns, text="Edit", command=self._edit_group).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Delete", command=self._delete_group).pack(side=tk.LEFT, padx=4)

    def _build_config_tab(self) -> None:
        frame = ttk.Frame(self.config_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.config_vars = {
            "weeks": tk.StringVar(),
            "days_per_week": tk.StringVar(),
            "timeslots_per_day": tk.StringVar(),
            "timeslots": tk.StringVar(),
        }

        row = 0
        for key, label in (
            ("weeks", "Weeks"),
            ("days_per_week", "Days per week"),
            ("timeslots_per_day", "Timeslots per day"),
            ("timeslots", "Timeslots list (comma)"),
        ):
            ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=4)
            ttk.Entry(frame, textvariable=self.config_vars[key], width=40).grid(row=row, column=1, sticky="w", pady=4)
            row += 1

        ttk.Button(frame, text="Apply", command=self._apply_config).grid(row=row, column=0, columnspan=2, pady=10)

    def _build_validation_tab(self) -> None:
        frame = ttk.Frame(self.validation_tab)
        frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        ttk.Button(frame, text="Run Validation", command=self._run_validation).pack(anchor="w")
        ttk.Button(frame, text="Save", command=self._save).pack(anchor="w", pady=6)

        run_box = ttk.Frame(frame)
        run_box.pack(fill=tk.X, pady=6)
        ttk.Button(run_box, text="Run Scheduler", command=self._run_scheduler).pack(side=tk.LEFT, padx=4)
        ttk.Button(run_box, text="Visualize Input", command=self._visualize_input).pack(side=tk.LEFT, padx=4)
        ttk.Button(run_box, text="Visualize Schedule", command=self._visualize_schedule).pack(side=tk.LEFT, padx=4)

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
                    "days_per_week": 5,
                    "timeslots_per_day": 2,
                    "timeslots": ["morning", "afternoon"],
                },
            }
        self._refresh_all()

    def _refresh_all(self) -> None:
        self._update_summary()
        self._refresh_subjects()
        self._refresh_lecturers()
        self._refresh_groups()
        self._refresh_config()

    def _update_summary(self) -> None:
        cfg = self.data.get("configuration", {})
        summary = [
            f"File: {self.file_path}",
            "",
            f"Subjects: {len(self.data.get('subjects', []))}",
            f"Lecturers: {len(self.data.get('lecturers', []))}",
            f"Student Groups: {len(self.data.get('student_groups', []))}",
            "",
            f"Weeks: {cfg.get('weeks', '-')}",
            f"Days/week: {cfg.get('days_per_week', '-')}",
            f"Timeslots/day: {cfg.get('timeslots_per_day', '-')}",
            f"Timeslots: {', '.join(cfg.get('timeslots', [])) if cfg.get('timeslots') else '-'}",
        ]
        self.summary_info.set("\n".join(summary))

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

    def _refresh_lecturers(self) -> None:
        self.lecturers_tree.delete(*self.lecturers_tree.get_children())
        for l in self.data.get("lecturers", []):
            avail = l.get("availability", [])
            label = "patterns" if isinstance(avail, dict) else "list" if isinstance(avail, list) else "-"
            self.lecturers_tree.insert("", tk.END, values=(
                l.get("id", ""),
                l.get("name", ""),
                l.get("subject_id", ""),
                l.get("priority", ""),
                label,
            ))

    def _refresh_groups(self) -> None:
        self.groups_tree.delete(*self.groups_tree.get_children())
        for g in self.data.get("student_groups", []):
            subj_str = ", ".join(g.get("subject_ids", []))
            self.groups_tree.insert("", tk.END, values=(g.get("id", ""), g.get("name", ""), subj_str))

    def _refresh_config(self) -> None:
        cfg = self.data.get("configuration", {})
        self.config_vars["weeks"].set(str(cfg.get("weeks", "")))
        self.config_vars["days_per_week"].set(str(cfg.get("days_per_week", "")))
        self.config_vars["timeslots_per_day"].set(str(cfg.get("timeslots_per_day", "")))
        timeslots = cfg.get("timeslots", [])
        self.config_vars["timeslots"].set(", ".join(timeslots) if timeslots else "")

    # File actions ----------------------------------------------------
    def _choose_file(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("All", "*")])
        if path:
            self.file_path = path
            self.data = _safe_load(path)
            self._refresh_all()

    def _save(self) -> None:
        ok, report = validate_data(self.data)
        if not ok:
            messagebox.showerror("Validation failed", "Fix issues before saving. See Validate tab for details.")
            self._render_validation(ok, report)
            return
        _safe_dump(self.data, self.file_path)
        messagebox.showinfo("Saved", f"Saved to {self.file_path}")

    def _save_as(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            self.file_path = path
            self._save()
            self._update_summary()

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
            proc = subprocess.run([sys.executable, script], capture_output=True, text=True, cwd="." )
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
        sel = self.subjects_tree.selection()
        if not sel:
            return
        idx = self.subjects_tree.index(sel[0])
        self._subject_form(index=idx)

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
            win.destroy()

        ttk.Button(win, text="Save", command=submit).grid(row=row, column=0, columnspan=2, pady=10)

    # Lecturer handlers ----------------------------------------------
    def _add_lecturer(self) -> None:
        self._lecturer_form()

    def _edit_lecturer(self) -> None:
        sel = self.lecturers_tree.selection()
        if not sel:
            return
        idx = self.lecturers_tree.index(sel[0])
        self._lecturer_form(index=idx)

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
            pattern_days: Dict[str, List[str]] = {}
            for day, slots in day_slot_vars.items():
                chosen = [slot for slot, var in slots.items() if var.get()]
                if chosen:
                    pattern_days[day] = chosen
            if not pattern_days:
                messagebox.showwarning("No slots", "Select at least one slot to create a pattern")
                return
            avail_obj = {"patterns": [{"weeks": week_expr.get().strip(), "days": pattern_days}], "exceptions": [], "blackouts": []}
            raw_editor.delete("1.0", tk.END)
            raw_editor.insert(tk.END, json.dumps(avail_obj, indent=2))

        ttk.Button(builder_frame, text="Apply pattern", command=apply_quick).grid(row=len(DAY_LABELS) + 1, column=0, columnspan=2, pady=6)

        ttk.Label(win, text="Raw availability JSON (list or pattern dict)").pack(anchor="w", padx=8)
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

    # Group handlers --------------------------------------------------
    def _add_group(self) -> None:
        self._group_form()

    def _edit_group(self) -> None:
        sel = self.groups_tree.selection()
        if not sel:
            return
        idx = self.groups_tree.index(sel[0])
        self._group_form(index=idx)

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
            win.destroy()

        ttk.Button(win, text="Save", command=submit).grid(row=row, column=0, columnspan=2, pady=10)

    # Config handlers -------------------------------------------------
    def _apply_config(self) -> None:
        cfg = self.data.get("configuration", {})
        try:
            cfg["weeks"] = int(self.config_vars["weeks"].get())
            cfg["days_per_week"] = int(self.config_vars["days_per_week"].get())
            cfg["timeslots_per_day"] = int(self.config_vars["timeslots_per_day"].get())
        except ValueError:
            messagebox.showerror("Invalid", "Configuration numeric fields must be integers")
            return
        cfg["timeslots"] = [t.strip() for t in self.config_vars["timeslots"].get().split(",") if t.strip()]
        self.data["configuration"] = cfg
        self._refresh_all()


def main() -> None:
    root = tk.Tk()
    root.geometry("860x640")
    InputEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
