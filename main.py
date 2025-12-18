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
import json
import random
from data_loader import load_from_json, print_data_summary
from scheduler import OsteopathyScheduler
from visualize_schedule import parse_schedule_output, create_weekly_overview, create_room_calendar, create_utilization_heatmap, create_group_calendar


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
    lecturers, subjects, rooms, student_groups, semester_weeks, year, canton = load_from_json('input_data.json')
    # Load scheduled_days from configuration (default Mon-Fri)
    try:
        with open('input_data.json', 'r') as f:
            raw_cfg = json.load(f).get('configuration', {})
        scheduled_days = raw_cfg.get('scheduled_days', ["Monday","Tuesday","Wednesday","Thursday","Friday"])
    except Exception:
        scheduled_days = ["Monday","Tuesday","Wednesday","Thursday","Friday"]
    print_data_summary(lecturers, subjects, rooms, student_groups)
    print(f"Year: {year}, Canton: {canton.upper()}")
    print()
    
    # Create scheduler
    print("Initializing scheduler...")
    scheduler = OsteopathyScheduler(
        lecturers=lecturers,
        subjects=subjects,
        rooms=rooms,
        student_groups=student_groups,
        semester_weeks=semester_weeks,
        year=year,
        canton=canton,
        scheduled_days=scheduled_days
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
    print()
    
    # Generate visualizations
    print("Generating schedule visualizations...")
    schedule_blocks = parse_schedule_output('schedule_output.txt')
    create_weekly_overview(schedule_blocks, weeks_to_show=semester_weeks)
    create_room_calendar(schedule_blocks, weeks=semester_weeks)
    create_group_calendar(schedule_blocks, weeks=semester_weeks)
    create_utilization_heatmap(schedule_blocks, weeks=semester_weeks)
    print("Visualizations saved to: images/schedule/")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
