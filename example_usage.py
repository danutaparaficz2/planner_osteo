"""
Example usage of the Osteopathy Scheduler

This script demonstrates how to use the scheduler with sample data.
"""

from datetime import date, timedelta
from scheduler import (
    Lecturer, Subject, Room, StudentGroup, Scheduler, TimeSlot
)


def create_sample_data():
    """Create sample data for demonstration"""
    
    # Create 15 subjects
    subjects = [
        Subject(1, "Anatomy Fundamentals", 10),
        Subject(2, "Osteopathic Principles", 12),
        Subject(3, "Cranial Osteopathy", 8),
        Subject(4, "Visceral Manipulation", 15),
        Subject(5, "Structural Techniques", 20),
        Subject(6, "Pediatric Osteopathy", 6),
        Subject(7, "Sports Medicine", 10),
        Subject(8, "Clinical Assessment", 14),
        Subject(9, "Biomechanics", 8),
        Subject(10, "Pathology", 12),
        Subject(11, "Neurology", 10),
        Subject(12, "Research Methods", 5),
        Subject(13, "Ethics and Practice", 4),
        Subject(14, "Diagnosis Techniques", 16),
        Subject(15, "Advanced Manipulation", 18),
    ]
    
    # Create 15 lecturers (each teaches one subject - one lecturer per subject)
    lecturers = [
        Lecturer(1, "Dr. Smith", 1, 10),      # Top 5 most important
        Lecturer(2, "Dr. Johnson", 2, 9),
        Lecturer(3, "Dr. Williams", 3, 8),
        Lecturer(4, "Dr. Brown", 4, 7),
        Lecturer(5, "Dr. Davis", 5, 6),
        Lecturer(6, "Dr. Miller", 6, 5),      # Not in top 5
        Lecturer(7, "Dr. Wilson", 7, 4),
        Lecturer(8, "Dr. Moore", 8, 3),
        Lecturer(9, "Dr. Taylor", 9, 2),
        Lecturer(10, "Dr. Anderson", 10, 1),
        Lecturer(11, "Dr. Thomas", 11, 1),
        Lecturer(12, "Dr. Jackson", 12, 1),
        Lecturer(13, "Dr. White", 13, 1),
        Lecturer(14, "Dr. Harris", 14, 1),
        Lecturer(15, "Dr. Martin", 15, 1),
    ]
    
    # Create 10 theory rooms
    rooms = [
        Room(1, "Room A", 30),
        Room(2, "Room B", 30),
        Room(3, "Room C", 30),
        Room(4, "Room D", 30),
        Room(5, "Room E", 30),
        Room(6, "Room F", 30),
        Room(7, "Room G", 30),
        Room(8, "Room H", 30),
        Room(9, "Room I", 30),
        Room(10, "Room J", 30),
    ]
    
    # Create 5 student groups
    student_groups = [
        StudentGroup(1, "Group A", 25),
        StudentGroup(2, "Group B", 28),
        StudentGroup(3, "Group C", 24),
        StudentGroup(4, "Group D", 26),
        StudentGroup(5, "Group E", 27),
    ]
    
    return lecturers, subjects, rooms, student_groups


def add_lecturer_availability(lecturers, start_date, end_date):
    """
    Add availability calendars for lecturers
    
    For this example, we'll make top lecturers available on most days
    with some variation in their schedules.
    """
    
    # Get top 5 lecturers (by importance)
    top_lecturers = sorted(lecturers, key=lambda l: l.importance, reverse=True)[:5]
    
    current_date = start_date
    day_counter = 0
    
    while current_date <= end_date:
        # Skip weekends
        if current_date.weekday() < 5:  # Monday = 0, Friday = 4
            
            for i, lecturer in enumerate(top_lecturers):
                # Each lecturer has a slightly different availability pattern
                # to make scheduling more realistic
                
                if i == 0:  # Dr. Smith - available most days
                    if day_counter % 5 != 0:  # Not available every 5th day
                        lecturer.add_availability(current_date, TimeSlot.MORNING)
                        lecturer.add_availability(current_date, TimeSlot.AFTERNOON)
                
                elif i == 1:  # Dr. Johnson - available mornings mostly
                    lecturer.add_availability(current_date, TimeSlot.MORNING)
                    if day_counter % 3 == 0:
                        lecturer.add_availability(current_date, TimeSlot.AFTERNOON)
                
                elif i == 2:  # Dr. Williams - available afternoons mostly
                    lecturer.add_availability(current_date, TimeSlot.AFTERNOON)
                    if day_counter % 3 == 0:
                        lecturer.add_availability(current_date, TimeSlot.MORNING)
                
                elif i == 3:  # Dr. Brown - available 3 days a week
                    if day_counter % 2 == 0:
                        lecturer.add_availability(current_date, TimeSlot.MORNING)
                        lecturer.add_availability(current_date, TimeSlot.AFTERNOON)
                
                else:  # Dr. Davis - available most afternoons
                    if day_counter % 4 != 0:
                        lecturer.add_availability(current_date, TimeSlot.AFTERNOON)
                    if day_counter % 5 == 0:
                        lecturer.add_availability(current_date, TimeSlot.MORNING)
            
            day_counter += 1
        
        current_date += timedelta(days=1)


def main():
    """Main function to run the example"""
    
    print("\n" + "="*80)
    print("OSTEOPATHY SCHEDULER - EXAMPLE USAGE")
    print("="*80 + "\n")
    
    # Create sample data
    lecturers, subjects, rooms, student_groups = create_sample_data()
    
    # Define semester dates (3 months)
    semester_start = date(2024, 9, 1)  # September 1, 2024
    semester_end = date(2024, 11, 30)   # November 30, 2024
    
    print(f"Semester: {semester_start} to {semester_end}")
    print(f"Total lecturers: {len(lecturers)} (each teaches one subject)")
    print(f"Total subjects: {len(subjects)}")
    print(f"Total rooms: {len(rooms)}")
    print(f"Total student groups: {len(student_groups)}")
    
    # Add availability for lecturers
    print("\nSetting up lecturer availability calendars...")
    add_lecturer_availability(lecturers, semester_start, semester_end)
    
    # Create scheduler
    scheduler = Scheduler(
        lecturers=lecturers,
        subjects=subjects,
        rooms=rooms,
        student_groups=student_groups,
        semester_start=semester_start,
        semester_end=semester_end
    )
    
    # Get top 5 lecturers
    top_lecturers = scheduler.get_top_lecturers(5)
    print(f"\nTop 5 most important lecturers:")
    for i, lecturer in enumerate(top_lecturers, 1):
        subject = next(s for s in subjects if s.id == lecturer.subject_id)
        print(f"  {i}. {lecturer.name} - teaches {subject.name} (importance: {lecturer.importance})")
    
    # Run the scheduler
    print("\nRunning scheduler...")
    schedule = scheduler.schedule_subjects()
    
    # Print the schedule
    scheduler.print_schedule()
    
    print("\nScheduling complete!")


if __name__ == "__main__":
    main()
