#!/usr/bin/env python3
"""
All-in-one CLI app to manage the full workflow:
- Edit input data (wizard)
- Validate input
- Run scheduler
- Generate visualizations (input + schedule)

Designed to run both via Python and as a PyInstaller onefile app.
"""
import os
import sys


def _set_working_dir_for_bundle():
    try:
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(base_dir)
    except Exception:
        pass


_set_working_dir_for_bundle()


def _press_enter():
    try:
        input("\nPress Enter to continue...")
    except EOFError:
        pass


def _run_wizard():
    import user_input_cli as wiz
    wiz.main_menu()


def _run_validation():
    from validate_input import load_json, validate_data, print_report
    data = load_json("input_data.json")
    ok, report = validate_data(data)
    print_report(ok, report)
    return ok


def _run_scheduler():
    import main as scheduler_main
    try:
        rc = scheduler_main.main()
        print(f"\nScheduler finished with exit code {rc}.")
    except Exception as e:
        print("\nScheduler failed:", e)


def _viz_input():
    try:
        import visualize_input_data as vid
        vid.main()
    except Exception as e:
        print("\nInput visualization failed:", e)
        print("Tip: Ensure matplotlib/numpy are available if running outside the bundled app.")


def _viz_schedule():
    try:
        import visualize_schedule as vs
        vs.main()
    except Exception as e:
        print("\nSchedule visualization failed:", e)
        print("Tip: Ensure matplotlib/numpy are available if running outside the bundled app.")


def main_menu():
    while True:
        print("\nOsteopathy Planner - All-in-One App")
        print("=" * 40)
        print("1) Edit input (wizard)")
        print("2) Validate input")
        print("3) Run scheduler")
        print("4) Visualize input data")
        print("5) Visualize schedule")
        print("0) Exit")
        choice = input("Select option: ").strip()
        if choice == "0":
            break
        elif choice == "1":
            _run_wizard()
        elif choice == "2":
            _run_validation()
            _press_enter()
        elif choice == "3":
            # Validate first for safety
            ok = _run_validation()
            if not ok:
                print("\nValidation failed. Fix issues before running the scheduler.")
                _press_enter()
                continue
            _run_scheduler()
            _press_enter()
        elif choice == "4":
            _viz_input()
            _press_enter()
        elif choice == "5":
            _viz_schedule()
            _press_enter()
        else:
            print("Please choose a valid option.")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\nExiting...")
