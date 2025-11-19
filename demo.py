#!/usr/bin/env python3
"""
Quick demonstration of the Osteopathy Education Scheduler.
Shows key features and validates the implementation.
"""
import random
from sample_data import create_sample_data
from scheduler import OsteopathyScheduler
from models import RoomType

def main():
    print("\n" + "=" * 80)
    print("OSTEOPATHY EDUCATION SCHEDULER - DEMONSTRATION")
    print("=" * 80 + "\n")
    
    # Set seed for reproducibility
    random.seed(42)
    
    # Generate sample data
    lecturers, subjects, rooms, student_groups = create_sample_data()
    
    print("📊 CONFIGURATION")
    print("-" * 80)
    print(f"Student Groups: {len(student_groups)}")
    print(f"Lecturers: {len(lecturers)}")
    print(f"Subjects: {len(subjects)} (Theory: {len([s for s in subjects if s.room_type == RoomType.THEORY])}, Practical: {len([s for s in subjects if s.room_type == RoomType.PRACTICAL])})")
    print(f"Rooms: {len(rooms)} (Theory: {len([r for r in rooms if r.room_type == RoomType.THEORY])}, Practical: {len([r for r in rooms if r.room_type == RoomType.PRACTICAL])})")
    print(f"Semester: 15 weeks")
    print()
    
    print("⭐ TOP 5 PRIORITY LECTURERS")
    print("-" * 80)
    priority_lecturers = sorted([l for l in lecturers if l.priority <= 5], key=lambda x: x.priority)
    for lect in priority_lecturers:
        subj = next(s for s in subjects if s.id == lect.subject_id)
        avail = len(lect.availability)
        print(f"  {lect.priority}. {lect.name:20} → {subj.name:20} ({avail:3} available slots)")
    print()
    
    # Create scheduler
    scheduler = OsteopathyScheduler(
        lecturers=lecturers,
        subjects=subjects,
        rooms=rooms,
        student_groups=student_groups,
        semester_weeks=15
    )
    
    print("🚀 CREATING SCHEDULE...")
    print("-" * 80)
    schedule = scheduler.create_schedule()
    print()
    
    print("✅ RESULTS")
    print("-" * 80)
    print(f"Total blocks scheduled: {len(schedule.blocks)}")
    
    morning = sum(1 for b in schedule.blocks if b.timeslot.value == 'morning')
    afternoon = sum(1 for b in schedule.blocks if b.timeslot.value == 'afternoon')
    print(f"  Morning: {morning} | Afternoon: {afternoon}")
    print()
    
    # Show practical subjects mixing
    print("🔬 PRACTICAL SUBJECTS MIXING")
    print("-" * 80)
    practical_subjects = ['A', 'B', 'C', 'D']
    practical_blocks = sorted([b for b in schedule.blocks if b.subject_id in practical_subjects],
                             key=lambda x: (x.week, x.day, x.timeslot.value))
    
    sequence = [b.subject_id for b in practical_blocks[:15]]
    print(f"First 15 practical blocks: {' → '.join(sequence)}")
    
    for subj_id in practical_subjects:
        blocks = [b for b in schedule.blocks if b.subject_id == subj_id]
        weeks = sorted(set(b.week for b in blocks))
        print(f"  Subject {subj_id}: {len(blocks):2} blocks (weeks {min(weeks)+1}-{max(weeks)+1})")
    print()
    
    # Show spread subjects
    print("📈 SPREAD SUBJECTS DISTRIBUTION")
    print("-" * 80)
    spread_subjects = [s for s in subjects if s.spread]
    for subj in spread_subjects[:3]:  # Show first 3
        blocks = [b for b in schedule.blocks if b.subject_id == subj.id]
        if len(blocks) > 1:
            weeks = sorted([b.week for b in blocks])
            gaps = [weeks[i+1] - weeks[i] for i in range(len(weeks)-1)]
            avg_gap = sum(gaps) / len(gaps) if gaps else 0
            print(f"  {subj.name:20} {len(blocks):3} blocks, avg gap: {avg_gap:.1f} weeks")
    print()
    
    # Show room utilization
    print("🏢 ROOM UTILIZATION")
    print("-" * 80)
    room_usage = {}
    for block in schedule.blocks:
        room_usage[block.room_id] = room_usage.get(block.room_id, 0) + 1
    
    for room_id in sorted(room_usage.keys(), key=lambda x: -room_usage[x])[:5]:
        room = next(r for r in rooms if r.id == room_id)
        usage = room_usage[room_id]
        total_slots = 15 * 5 * 2
        percent = (usage / total_slots) * 100
        print(f"  {room.name:20} ({room.room_type.value:9}): {usage:3} blocks ({percent:5.1f}%)")
    print()
    
    print("=" * 80)
    print("DEMONSTRATION COMPLETE ✓")
    print("Run 'python3 main.py' for full schedule output")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
