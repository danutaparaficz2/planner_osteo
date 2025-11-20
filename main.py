#!/usr/bin/env python3
"""
Main execution script for the Osteopathy Education Scheduler.

This scheduler creates a semester schedule that:
- Prioritizes the top 5 lecturers and uses their availability calendars
- Distributes subject blocks across the semester
- Spreads "spread" subjects evenly across the semester
- Handles practical subjects (A, B, C, D) with the single practical room
- Mixes practical subjects across the semester
- Assigns theory rooms for theory subjects
"""
import sys
import random
from data_loader import load_from_json, print_data_summary
from scheduler import OsteopathyScheduler


def main():
    """Main execution function"""
    print("=" * 80)
    print("OSTEOPATHY EDUCATION SCHEDULER")
    print("=" * 80)
    print()
    
    # Set random seed for reproducibility
    random.seed(42)
    
    # Load data from JSON file
    print("Loading data from input_data.json...")
    lecturers, subjects, rooms, student_groups, semester_weeks = load_from_json('input_data.json')
    print_data_summary(lecturers, subjects, rooms, student_groups)
    print()
    
    # Create scheduler
    print("Initializing scheduler...")
    scheduler = OsteopathyScheduler(
        lecturers=lecturers,
        subjects=subjects,
        rooms=rooms,
        student_groups=student_groups,
        semester_weeks=semester_weeks
    )
    print()
    
    # Create schedule
    print("Creating schedule...")
    schedule = scheduler.create_schedule()
    print()
    
    # Print statistics
    scheduler.print_statistics()
    print()
    
    # Print full schedule
    print("Generating detailed schedule...")
    scheduler.print_schedule(output_file="schedule_output.txt")
    print()
    
    print("=" * 80)
    print("Scheduling complete!")
    print(f"Total blocks scheduled: {len(schedule.blocks)}")
    print("Detailed schedule saved to: schedule_output.txt")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
