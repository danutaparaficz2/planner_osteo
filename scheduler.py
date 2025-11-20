"""
Core scheduling algorithm for osteopathy education planner.
"""
from typing import List, Dict, Optional, Set, Tuple
from models import (
    Lecturer, Subject, Room, StudentGroup, Schedule, 
    ScheduledBlock, TimeSlot, RoomType
)
import random


class OsteopathyScheduler:
    """
    Scheduler for osteopathy education that prioritizes top lecturers
    and distributes subjects across a semester.
    """
    
    def __init__(self, 
                 lecturers: List[Lecturer],
                 subjects: List[Subject],
                 rooms: List[Room],
                 student_groups: List[StudentGroup],
                 semester_weeks: int = 15):
        self.lecturers = {l.id: l for l in lecturers}
        self.subjects = {s.id: s for s in subjects}
        self.rooms = {r.id: r for r in rooms}
        self.student_groups = {g.id: g for g in student_groups}
        self.semester_weeks = semester_weeks
        self.schedule = Schedule(weeks=semester_weeks)
        
        # Organize lecturers by priority
        self.priority_lecturers = [l for l in lecturers if l.priority <= 5]
        self.priority_lecturers.sort(key=lambda x: x.priority)
        
        # Organize rooms by type
        self.theory_rooms = [r for r in rooms if r.room_type == RoomType.THEORY]
        self.practical_rooms = [r for r in rooms if r.room_type == RoomType.PRACTICAL]
        
    def create_schedule(self) -> Schedule:
        """
        Create the complete schedule following the priority rules:
        1. Schedule top 5 priority lecturers first using their availability
        2. Handle spread subjects with even distribution
        3. Schedule practical subjects (A, B, C, D) mixed across semester
        """
        print(f"Creating schedule for {self.semester_weeks} weeks...")
        print(f"Priority lecturers: {len(self.priority_lecturers)}")
        
        # Step 1: Schedule priority lecturers' theory subjects
        theory_subjects_priority = []
        for lecturer in self.priority_lecturers:
            subject = self.subjects.get(lecturer.subject_id)
            if subject and subject.room_type == RoomType.THEORY:
                theory_subjects_priority.append((lecturer, subject))
        
        for lecturer, subject in theory_subjects_priority:
            print(f"Scheduling priority lecturer: {lecturer.name} - Subject: {subject.name}")
            self._schedule_subject_for_lecturer(lecturer, subject)
        
        # Step 2: Schedule practical subjects (A, B, C, D) mixed across semester
        practical_subjects = [s for s in self.subjects.values() 
                            if s.room_type == RoomType.PRACTICAL and s.id in ['A', 'B', 'C', 'D']]
        
        if practical_subjects:
            print(f"Scheduling {len(practical_subjects)} practical subjects mixed across semester...")
            self._schedule_practical_subjects_mixed(practical_subjects)
        
        # Step 3: Schedule remaining subjects
        remaining_subjects = [s for s in self.subjects.values() 
                            if s.id not in [b.subject_id for b in self.schedule.blocks]]
        
        for subject in remaining_subjects:
            lecturer = self._get_lecturer_for_subject(subject.id)
            if lecturer:
                print(f"Scheduling remaining subject: {subject.name}")
                self._schedule_subject_for_lecturer(lecturer, subject)
        
        print(f"Schedule complete: {len(self.schedule.blocks)} blocks scheduled")
        return self.schedule
    
    def _schedule_subject_for_lecturer(self, lecturer: Lecturer, subject: Subject) -> None:
        """Schedule all blocks for a subject considering lecturer availability"""
        # Determine which student groups need this subject
        groups_needing_subject = [g for g in self.student_groups.values() 
                                 if subject.id in g.subject_ids]
        
        for group in groups_needing_subject:
            if subject.spread:
                self._schedule_spread_blocks(lecturer, subject, group)
            else:
                self._schedule_compact_blocks(lecturer, subject, group)
    
    def _schedule_spread_blocks(self, lecturer: Lecturer, subject: Subject, 
                               group: StudentGroup) -> None:
        """Schedule blocks spread evenly across the semester"""
        blocks_needed = subject.blocks_required
        
        # Calculate ideal spacing
        total_slots = self.semester_weeks * 5 * 2  # weeks * days * timeslots
        ideal_gap = total_slots // (blocks_needed + 1) if blocks_needed > 0 else total_slots
        
        scheduled = 0
        attempts = 0
        current_position = ideal_gap
        
        while scheduled < blocks_needed and attempts < 500:
            # Convert position to week, day, timeslot
            week = (current_position // 10) % self.semester_weeks
            day = ((current_position // 2) % 5) + 1
            timeslot = TimeSlot.MORNING if current_position % 2 == 0 else TimeSlot.AFTERNOON
            
            if week < self.semester_weeks and week >= 0:
                if self._try_schedule_block(lecturer, subject, group, week, day, timeslot):
                    scheduled += 1
                    current_position += ideal_gap
                else:
                    current_position += 1
            else:
                current_position += 1
            
            attempts += 1
        
        # If we couldn't schedule all blocks with spreading, fill in remaining
        if scheduled < blocks_needed:
            self._schedule_remaining_blocks(lecturer, subject, group, blocks_needed - scheduled)
    
    def _schedule_compact_blocks(self, lecturer: Lecturer, subject: Subject, 
                                 group: StudentGroup) -> None:
        """Schedule blocks as compactly as possible"""
        self._schedule_remaining_blocks(lecturer, subject, group, subject.blocks_required)
    
    def _schedule_remaining_blocks(self, lecturer: Lecturer, subject: Subject, 
                                   group: StudentGroup, blocks_needed: int) -> None:
        """Schedule remaining blocks in any available slot"""
        scheduled = 0
        
        for week in range(self.semester_weeks):
            for day in range(1, 6):  # Monday-Friday
                for timeslot in [TimeSlot.MORNING, TimeSlot.AFTERNOON]:
                    if scheduled >= blocks_needed:
                        return
                    
                    if self._try_schedule_block(lecturer, subject, group, week, day, timeslot):
                        scheduled += 1
    
    def _try_schedule_block(self, lecturer: Lecturer, subject: Subject, 
                           group: StudentGroup, week: int, day: int, 
                           timeslot: TimeSlot) -> bool:
        """Try to schedule a single block at the specified time"""
        # Check lecturer availability for priority lecturers
        if lecturer.priority <= 5:
            if not lecturer.is_available(week, day, timeslot):
                return False
        
        # Find available room
        room = self._find_available_room(subject.room_type, week, day, timeslot, 
                                        lecturer.id, group.id)
        if not room:
            return False
        
        # Check if slot is available for lecturer, room, and group
        if not self.schedule.is_slot_available(week, day, timeslot, 
                                              lecturer.id, room.id, group.id):
            return False
        
        # Create and add block
        block = ScheduledBlock(
            subject_id=subject.id,
            lecturer_id=lecturer.id,
            student_group_id=group.id,
            room_id=room.id,
            week=week,
            day=day,
            timeslot=timeslot,
            room_number=room.room_number
        )
        
        return self.schedule.add_block(block)
    
    def _schedule_practical_subjects_mixed(self, subjects: List[Subject]) -> None:
        """Schedule practical subjects (A, B, C, D) mixed across semester"""
        # Get the single practical room
        if not self.practical_rooms:
            print("Warning: No practical room available")
            return
        
        practical_room = self.practical_rooms[0]
        
        # Create a list of all slots that need to be filled for all practical subjects
        subject_blocks = []
        for subject in subjects:
            lecturer = self._get_lecturer_for_subject(subject.id)
            if not lecturer:
                continue
            
            groups_needing_subject = [g for g in self.student_groups.values() 
                                     if subject.id in g.subject_ids]
            
            for group in groups_needing_subject:
                for _ in range(subject.blocks_required):
                    subject_blocks.append((subject, lecturer, group))
        
        # Shuffle to mix subjects
        random.shuffle(subject_blocks)
        
        # Schedule blocks in mixed order
        scheduled = 0
        for week in range(self.semester_weeks):
            for day in range(1, 6):  # Monday-Friday
                for timeslot in [TimeSlot.MORNING, TimeSlot.AFTERNOON]:
                    if scheduled >= len(subject_blocks):
                        return
                    
                    subject, lecturer, group = subject_blocks[scheduled]
                    
                    # Check if lecturer is available (for priority lecturers)
                    if lecturer.priority <= 5:
                        if not lecturer.is_available(week, day, timeslot):
                            continue
                    
                    # Check if slot is available
                    if self.schedule.is_slot_available(week, day, timeslot,
                                                      lecturer.id, practical_room.id, group.id):
                        block = ScheduledBlock(
                            subject_id=subject.id,
                            lecturer_id=lecturer.id,
                            student_group_id=group.id,
                            room_id=practical_room.id,
                            week=week,
                            day=day,
                            timeslot=timeslot,
                            room_number=practical_room.room_number
                        )
                        
                        if self.schedule.add_block(block):
                            scheduled += 1
    
    def _find_available_room(self, room_type: RoomType, week: int, day: int, 
                            timeslot: TimeSlot, lecturer_id: str, 
                            group_id: str) -> Optional[Room]:
        """Find an available room of the specified type"""
        rooms = self.theory_rooms if room_type == RoomType.THEORY else self.practical_rooms
        
        for room in rooms:
            if self.schedule.is_slot_available(week, day, timeslot, 
                                              lecturer_id, room.id, group_id):
                return room
        
        return None
    
    def _get_lecturer_for_subject(self, subject_id: str) -> Optional[Lecturer]:
        """Get the lecturer who teaches a subject"""
        for lecturer in self.lecturers.values():
            if lecturer.subject_id == subject_id:
                return lecturer
        return None
    
    def print_schedule(self, output_file: Optional[str] = None) -> None:
        """Print the schedule in a readable format"""
        output = []
        output.append("=" * 80)
        output.append("OSTEOPATHY EDUCATION SCHEDULE")
        output.append("=" * 80)
        
        # Group by week
        for week in range(self.semester_weeks):
            week_blocks = [b for b in self.schedule.blocks if b.week == week]
            if not week_blocks:
                continue
            
            output.append(f"\nWEEK {week + 1}")
            output.append("-" * 80)
            
            # Group by day
            for day in range(1, 6):
                day_blocks = [b for b in week_blocks if b.day == day]
                if not day_blocks:
                    continue
                
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
                output.append(f"\n  {day_names[day - 1]}:")
                
                # Group by timeslot
                for timeslot in [TimeSlot.MORNING, TimeSlot.AFTERNOON]:
                    slot_blocks = [b for b in day_blocks if b.timeslot == timeslot]
                    if slot_blocks:
                        output.append(f"    {timeslot.value.upper()}:")
                        for block in slot_blocks:
                            subject = self.subjects[block.subject_id]
                            lecturer = self.lecturers[block.lecturer_id]
                            group = self.student_groups[block.student_group_id]
                            room = self.rooms[block.room_id]
                            
                            room_display = f"Room #{room.room_number}" if room.room_number else room.name
                            output.append(f"      - Subject: {subject.name} ({subject.id})")
                            output.append(f"        Lecturer: {lecturer.name}")
                            output.append(f"        Group: {group.name}")
                            output.append(f"        Room: {room_display} ({room.room_type.value})")
                            output.append("")
        
        output.append("=" * 80)
        output.append(f"TOTAL BLOCKS SCHEDULED: {len(self.schedule.blocks)}")
        output.append("=" * 80)
        
        result = "\n".join(output)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(result)
            print(f"Schedule written to {output_file}")
        else:
            print(result)
    
    def print_statistics(self) -> None:
        """Print scheduling statistics"""
        print("\n" + "=" * 80)
        print("SCHEDULING STATISTICS")
        print("=" * 80)
        
        # Blocks per subject
        print("\nBlocks scheduled per subject:")
        for subject_id, subject in self.subjects.items():
            blocks = self.schedule.get_blocks_for_subject(subject_id)
            print(f"  {subject.name} ({subject_id}): {len(blocks)}/{subject.blocks_required} blocks")
            
            if subject.spread and len(blocks) > 1:
                # Calculate actual spacing
                weeks = sorted([b.week for b in blocks])
                gaps = [weeks[i+1] - weeks[i] for i in range(len(weeks)-1)]
                avg_gap = sum(gaps) / len(gaps) if gaps else 0
                print(f"    Average gap: {avg_gap:.1f} weeks (spread subject)")
        
        # Blocks per lecturer
        print("\nBlocks per lecturer:")
        lecturer_blocks = {}
        for block in self.schedule.blocks:
            lecturer_blocks[block.lecturer_id] = lecturer_blocks.get(block.lecturer_id, 0) + 1
        
        for lecturer_id, count in sorted(lecturer_blocks.items(), 
                                         key=lambda x: self.lecturers[x[0]].priority):
            lecturer = self.lecturers[lecturer_id]
            print(f"  {lecturer.name} (Priority {lecturer.priority}): {count} blocks")
        
        # Room utilization
        print("\nRoom utilization:")
        room_blocks = {}
        for block in self.schedule.blocks:
            room_blocks[block.room_id] = room_blocks.get(block.room_id, 0) + 1
        
        for room_id, count in sorted(room_blocks.items(), key=lambda x: -x[1]):
            room = self.rooms[room_id]
            total_slots = self.semester_weeks * 5 * 2  # weeks * days * timeslots
            utilization = (count / total_slots) * 100
            print(f"  {room.name} ({room.room_type.value}): {count} blocks ({utilization:.1f}% utilization)")
        
        print("=" * 80)
