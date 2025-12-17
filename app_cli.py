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
    """Set working directory and ensure module path is correct for both frozen and normal execution."""
    try:
        if getattr(sys, 'frozen', False):
            # PyInstaller extracts to sys._MEIPASS
            if hasattr(sys, '_MEIPASS'):
                # Add the extracted location to sys.path FIRST for module imports
                meipass = sys._MEIPASS
                if meipass not in sys.path:
                    sys.path.insert(0, meipass)
                # Also check if .py files are in current dir next to exe
                exe_dir = os.path.dirname(sys.executable)
                if exe_dir not in sys.path:
                    sys.path.insert(0, exe_dir)
            # Set working directory to where the executable is
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            if base_dir not in sys.path:
                sys.path.insert(0, base_dir)
        os.chdir(base_dir)
    except Exception as e:
        print(f"Warning: Could not set working directory: {e}")


_set_working_dir_for_bundle()


def _press_enter():
    try:
        input("\nPress Enter to continue...")
    except EOFError:
        pass


def _run_wizard():
    try:
        import user_input_cli
        user_input_cli.main_menu()
    except ImportError as e:
        print(f"\nError importing wizard: {e}")
        print("Make sure user_input_cli.py is in the same directory.")


def _run_validation():
    try:
        import validate_input
        data = validate_input.load_json("input_data.json")
        ok, report = validate_input.validate_data(data)
        validate_input.print_report(ok, report)
        return ok
    except ImportError as e:
        print(f"\nError importing validation: {e}")
        return False


def _run_scheduler():
    try:
        import main
        rc = main.main()
        print(f"\nScheduler finished with exit code {rc}.")
    except ImportError as e:
        print(f"\nError importing scheduler: {e}")
    except Exception as e:
        print("\nScheduler failed:", e)


def _viz_input():
    try:
        import visualize_input_data
        visualize_input_data.main()
    except ImportError as e:
        print(f"\nError importing input visualization: {e}")
    except Exception as e:
        print("\nInput visualization failed:", e)
        print("Tip: Ensure matplotlib/numpy are available if running outside the bundled app.")


def _viz_schedule():
    try:
        import visualize_schedule
        visualize_schedule.main()
    except ImportError as e:
        print(f"\nError importing schedule visualization: {e}")
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
