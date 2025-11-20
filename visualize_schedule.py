"""
Schedule calendar visualization tool.
Creates visual calendars showing the schedule by room and student group.
"""
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import numpy as np
from collections import defaultdict
import re


def parse_schedule_output(filename='schedule_output.txt'):
    """Parse the text schedule output into structured data"""
    schedule_blocks = []
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Split by weeks
    week_sections = re.split(r'WEEK (\d+)', content)
    
    for i in range(1, len(week_sections), 2):
        week_num = int(week_sections[i])
        week_content = week_sections[i + 1]
        
        # Split by days
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        for day_idx, day_name in enumerate(day_names, 1):
            # Find day section
            day_pattern = rf'{day_name}:(.*?)(?=(?:Monday:|Tuesday:|Wednesday:|Thursday:|Friday:|WEEK|\Z))'
            day_match = re.search(day_pattern, week_content, re.DOTALL)
            
            if not day_match:
                continue
            
            day_content = day_match.group(1)
            
            # Parse morning and afternoon
            for timeslot in ['MORNING', 'AFTERNOON']:
                timeslot_pattern = rf'{timeslot}:(.*?)(?=(?:MORNING:|AFTERNOON:|\Z))'
                timeslot_match = re.search(timeslot_pattern, day_content, re.DOTALL)
                
                if not timeslot_match:
                    continue
                
                timeslot_content = timeslot_match.group(1)
                
                # Parse individual blocks - now expects "Room #X (type)" format
                blocks = re.findall(
                    r'- Subject: (.*?) \((.*?)\)\s+Lecturer: (.*?)\s+Group: (.*?)\s+Room: (.*?) \((.*?)\)',
                    timeslot_content
                )
                
                for block in blocks:
                    schedule_blocks.append({
                        'week': week_num,
                        'day': day_idx,
                        'day_name': day_name,
                        'timeslot': timeslot.lower(),
                        'subject_name': block[0],
                        'subject_id': block[1],
                        'lecturer': block[2],
                        'group': block[3],
                        'room': block[4],  # Now contains "Room #X" format
                        'room_type': block[5]
                    })
    
    return schedule_blocks


def create_room_calendar(schedule_blocks, weeks=15):
    """Create a calendar view showing what's scheduled in each room"""
    # Get unique rooms
    rooms = sorted(set(block['room'] for block in schedule_blocks))
    
    # Create one figure per room
    for room in rooms:
        room_blocks = [b for b in schedule_blocks if b['room'] == room]
        
        if not room_blocks:
            continue
        
        # Create figure
        fig, axes = plt.subplots(5, 3, figsize=(16, 10))
        fig.suptitle(f'Room Calendar: {room}', fontsize=14, fontweight='bold')
        
        # Flatten axes for easier indexing
        axes = axes.flatten()
        
        # Create calendar for each week
        for week in range(1, min(weeks + 1, 16)):
            ax = axes[week - 1]
            
            week_blocks = [b for b in room_blocks if b['week'] == week]
            
            # Create a 5x2 grid (5 days, 2 timeslots)
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
            
            # Draw grid
            for day_idx in range(5):
                for slot_idx in range(2):
                    x = day_idx
                    y = 1 - slot_idx  # Flip y-axis
                    
                    # Find block for this slot
                    day_num = day_idx + 1
                    timeslot = 'morning' if slot_idx == 0 else 'afternoon'
                    
                    block = next((b for b in week_blocks 
                                 if b['day'] == day_num and b['timeslot'] == timeslot), None)
                    
                    if block:
                        # Color by subject type
                        color = '#e74c3c' if block['room_type'] == 'practical' else '#3498db'
                        rect = Rectangle((x, y - 0.4), 0.9, 0.4, 
                                       facecolor=color, edgecolor='black', linewidth=1.5, alpha=0.7)
                        ax.add_patch(rect)
                        
                        # Add text
                        text = f"{block['subject_id']}\n{block['group'].split('-')[0].strip()}"
                        ax.text(x + 0.45, y - 0.2, text, 
                               ha='center', va='center', fontsize=7, fontweight='bold')
                    else:
                        # Empty slot
                        rect = Rectangle((x, y - 0.4), 0.9, 0.4,
                                       facecolor='white', edgecolor='gray', linewidth=0.5, alpha=0.3)
                        ax.add_patch(rect)
            
            # Set limits and labels
            ax.set_xlim(-0.1, 5)
            ax.set_ylim(-0.5, 1.5)
            ax.set_xticks(np.arange(5) + 0.45)
            ax.set_xticklabels(days)
            ax.set_yticks([0.2, 0.8])
            ax.set_yticklabels(['Afternoon', 'Morning'])
            ax.set_title(f'Week {week}', fontweight='bold')
            ax.grid(False)
            ax.set_aspect('equal')
        
        # Hide unused subplots
        for idx in range(weeks, len(axes)):
            axes[idx].axis('off')
        
        # Add legend
        theory_patch = mpatches.Patch(color='#3498db', label='Theory', alpha=0.7)
        practical_patch = mpatches.Patch(color='#e74c3c', label='Practical', alpha=0.7)
        fig.legend(handles=[theory_patch, practical_patch], 
                  loc='lower right', fontsize=10)
        
        plt.tight_layout()
        
        # Save figure
        room_filename = room.replace(' ', '_').replace('/', '_')
        output_dir = os.path.join('images', 'schedule')
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f'calendar_room_{room_filename}.png')
        fig.savefig(path, dpi=110, bbox_inches='tight', pil_kwargs={'optimize': True})
        print(f"✓ Room calendar saved: {path}")
        plt.close(fig)


def create_group_calendar(schedule_blocks, weeks=15):
    """Create a calendar view showing each student group's schedule"""
    # Get unique groups
    groups = sorted(set(block['group'] for block in schedule_blocks))
    
    # Create one figure per group
    for group in groups:
        group_blocks = [b for b in schedule_blocks if b['group'] == group]
        
        if not group_blocks:
            continue
        
        # Create figure
        fig, axes = plt.subplots(5, 3, figsize=(16, 10))
        fig.suptitle(f'Student Group Calendar: {group}', fontsize=14, fontweight='bold')
        
        # Flatten axes for easier indexing
        axes = axes.flatten()
        
        # Create calendar for each week
        for week in range(1, min(weeks + 1, 16)):
            ax = axes[week - 1]
            
            week_blocks = [b for b in group_blocks if b['week'] == week]
            
            # Create a 5x2 grid (5 days, 2 timeslots)
            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
            
            # Draw grid
            for day_idx in range(5):
                for slot_idx in range(2):
                    x = day_idx
                    y = 1 - slot_idx  # Flip y-axis
                    
                    # Find block for this slot
                    day_num = day_idx + 1
                    timeslot = 'morning' if slot_idx == 0 else 'afternoon'
                    
                    block = next((b for b in week_blocks 
                                 if b['day'] == day_num and b['timeslot'] == timeslot), None)
                    
                    if block:
                        # Color by subject type
                        color = '#e74c3c' if block['room_type'] == 'practical' else '#3498db'
                        rect = Rectangle((x, y - 0.4), 0.9, 0.4, 
                                       facecolor=color, edgecolor='black', linewidth=1.5, alpha=0.7)
                        ax.add_patch(rect)
                        
                        # Show room number (e.g., "#5")
                        room_display = block['room'].replace('Room ', '')
                        text = f"{block['subject_id']}\n{room_display}"
                        ax.text(x + 0.45, y - 0.2, text, 
                               ha='center', va='center', fontsize=7, fontweight='bold')
                    else:
                        # Empty slot
                        rect = Rectangle((x, y - 0.4), 0.9, 0.4,
                                       facecolor='white', edgecolor='gray', linewidth=0.5, alpha=0.3)
                        ax.add_patch(rect)
            
            # Set limits and labels
            ax.set_xlim(-0.1, 5)
            ax.set_ylim(-0.5, 1.5)
            ax.set_xticks(np.arange(5) + 0.45)
            ax.set_xticklabels(days)
            ax.set_yticks([0.2, 0.8])
            ax.set_yticklabels(['Afternoon', 'Morning'])
            ax.set_title(f'Week {week}', fontweight='bold')
            ax.grid(False)
            ax.set_aspect('equal')
        
        # Hide unused subplots
        for idx in range(weeks, len(axes)):
            axes[idx].axis('off')
        
        # Add legend
        theory_patch = mpatches.Patch(color='#3498db', label='Theory', alpha=0.7)
        practical_patch = mpatches.Patch(color='#e74c3c', label='Practical', alpha=0.7)
        fig.legend(handles=[theory_patch, practical_patch], 
                  loc='lower right', fontsize=10)
        
        plt.tight_layout()
        
        # Save figure
        group_filename = group.replace(' ', '_').replace('-', '_')
        output_dir = os.path.join('images', 'schedule')
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f'calendar_group_{group_filename}.png')
        fig.savefig(path, dpi=110, bbox_inches='tight', pil_kwargs={'optimize': True})
        print(f"✓ Group calendar saved: {path}")
        plt.close(fig)


def create_weekly_overview(schedule_blocks, weeks_to_show=5):
    """Create a comprehensive weekly overview showing all activities"""
    
    for week in range(1, weeks_to_show + 1):
        week_blocks = [b for b in schedule_blocks if b['week'] == week]
        
        if not week_blocks:
            continue
        
        # Create figure
        fig, ax = plt.subplots(figsize=(16, 9))
        fig.suptitle(f'Week {week} - Complete Schedule Overview', 
                fontsize=14, fontweight='bold')
        
        # Get unique rooms and sort them
        rooms = sorted(set(block['room'] for block in week_blocks))
        
        # Create grid: days x rooms
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        
        # Setup grid
        y_positions = {}
        for idx, room in enumerate(rooms):
            y_positions[room] = len(rooms) - idx - 1
        
        # Draw grid and blocks
        for day_idx, day in enumerate(days):
            for room_idx, room in enumerate(rooms):
                y = y_positions[room]
                
                # Draw room row background
                if day_idx == 0:
                    ax.text(-0.5, y, room.split()[0] + '\n' + room.split()[1] if len(room.split()) > 1 else room,
                           va='center', ha='right', fontsize=8, fontweight='bold')
                
                # Morning slot
                morning_block = next((b for b in week_blocks 
                                    if b['day'] == day_idx + 1 
                                    and b['timeslot'] == 'morning' 
                                    and b['room'] == room), None)
                
                x_morning = day_idx * 2
                if morning_block:
                    color = '#e74c3c' if morning_block['room_type'] == 'practical' else '#3498db'
                    rect = Rectangle((x_morning, y), 0.9, 0.9,
                                   facecolor=color, edgecolor='black', linewidth=1.5, alpha=0.7)
                    ax.add_patch(rect)
                    
                    text = f"{morning_block['subject_id']}\n{morning_block['group'].split('-')[0].strip()}"
                    ax.text(x_morning + 0.45, y + 0.45, text,
                           ha='center', va='center', fontsize=7, fontweight='bold')
                else:
                    rect = Rectangle((x_morning, y), 0.9, 0.9,
                                   facecolor='white', edgecolor='gray', linewidth=0.5, alpha=0.3)
                    ax.add_patch(rect)
                
                # Afternoon slot
                afternoon_block = next((b for b in week_blocks 
                                      if b['day'] == day_idx + 1 
                                      and b['timeslot'] == 'afternoon' 
                                      and b['room'] == room), None)
                
                x_afternoon = day_idx * 2 + 1
                if afternoon_block:
                    color = '#e74c3c' if afternoon_block['room_type'] == 'practical' else '#3498db'
                    rect = Rectangle((x_afternoon, y), 0.9, 0.9,
                                   facecolor=color, edgecolor='black', linewidth=1.5, alpha=0.7)
                    ax.add_patch(rect)
                    
                    text = f"{afternoon_block['subject_id']}\n{afternoon_block['group'].split('-')[0].strip()}"
                    ax.text(x_afternoon + 0.45, y + 0.45, text,
                           ha='center', va='center', fontsize=7, fontweight='bold')
                else:
                    rect = Rectangle((x_afternoon, y), 0.9, 0.9,
                                   facecolor='white', edgecolor='gray', linewidth=0.5, alpha=0.3)
                    ax.add_patch(rect)
        
        # Set axis properties
        ax.set_xlim(-1, 10)
        ax.set_ylim(-0.5, len(rooms) + 0.5)

        # Add vertical lines to divide days (at boundaries between days)
        for boundary in [0, 2, 4, 6, 8, 10]:
            ax.axvline(boundary, color='lightgray', linewidth=1.0, alpha=0.8, zorder=0)

        # X-axis: show day names on top, one label per day
        day_centers = [i * 2 + 0.95 for i in range(len(days))]
        ax.set_xticks(day_centers)
        ax.set_xticklabels(days, fontsize=9, fontweight='bold')
        ax.xaxis.tick_top()
        ax.tick_params(axis='x', labelbottom=False)

        ax.set_yticks([])
        ax.set_ylabel('Rooms', fontsize=12, fontweight='bold')
        
        # Add legend
        theory_patch = mpatches.Patch(color='#3498db', label='Theory', alpha=0.7)
        practical_patch = mpatches.Patch(color='#e74c3c', label='Practical', alpha=0.7)
        ax.legend(handles=[theory_patch, practical_patch], 
                 loc='upper right', fontsize=10)
        
        ax.grid(False)
        ax.set_aspect('equal')
        
        plt.tight_layout()
        
        # Save figure
        output_dir = os.path.join('images', 'schedule')
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f'calendar_week_{week}_overview.png')
        fig.savefig(path, dpi=110, bbox_inches='tight', pil_kwargs={'optimize': True})
        print(f"✓ Week {week} overview saved: {path}")
        plt.close(fig)


def create_utilization_heatmap(schedule_blocks, weeks=15):
    """Create heatmaps showing room and group utilization"""
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 7))
    fig.suptitle('Utilization Analysis', fontsize=14, fontweight='bold')
    
    # Room utilization heatmap
    ax = axes[0]
    rooms = sorted(set(block['room'] for block in schedule_blocks))
    
    # Create matrix: weeks x rooms
    room_utilization = np.zeros((weeks, len(rooms)))
    
    for week in range(1, weeks + 1):
        for room_idx, room in enumerate(rooms):
            # Count blocks for this room in this week
            count = len([b for b in schedule_blocks 
                        if b['week'] == week and b['room'] == room])
            room_utilization[week - 1, room_idx] = count
    
    im = ax.imshow(room_utilization, cmap='YlOrRd', aspect='auto')
    ax.set_title('Room Utilization per Week', fontsize=12, fontweight='bold')
    ax.set_xlabel('Room')
    ax.set_ylabel('Week')
    ax.set_xticks(range(len(rooms)))
    ax.set_xticklabels([r.split()[0] + '\n' + r.split()[1] if len(r.split()) > 1 else r 
                        for r in rooms], fontsize=7, rotation=45, ha='right')
    ax.set_yticks(range(0, weeks, 2))
    ax.set_yticklabels(range(1, weeks + 1, 2))
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Number of Blocks', rotation=270, labelpad=15)
    
    # Omit per-cell value annotations to reduce render time and file size
    
    # Group utilization heatmap
    ax = axes[1]
    groups = sorted(set(block['group'] for block in schedule_blocks))
    
    # Create matrix: weeks x groups
    group_utilization = np.zeros((weeks, len(groups)))
    
    for week in range(1, weeks + 1):
        for group_idx, group in enumerate(groups):
            # Count blocks for this group in this week
            count = len([b for b in schedule_blocks 
                        if b['week'] == week and b['group'] == group])
            group_utilization[week - 1, group_idx] = count
    
    im = ax.imshow(group_utilization, cmap='YlGnBu', aspect='auto')
    ax.set_title('Student Group Utilization per Week', fontsize=12, fontweight='bold')
    ax.set_xlabel('Student Group')
    ax.set_ylabel('Week')
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([g.split('-')[0].strip() for g in groups], fontsize=8)
    ax.set_yticks(range(0, weeks, 2))
    ax.set_yticklabels(range(1, weeks + 1, 2))
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Number of Blocks', rotation=270, labelpad=15)
    
    # Omit per-cell value annotations to reduce render time and file size
    
    plt.tight_layout()
    output_dir = os.path.join('images', 'schedule')
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'calendar_utilization_heatmap.png')
    fig.savefig(path, dpi=110, bbox_inches='tight', pil_kwargs={'optimize': True})
    print(f"✓ Utilization heatmap saved: {path}")
    plt.close(fig)


def create_lecturer_calendar(schedule_blocks, weeks=15):
    """Create a calendar view showing each lecturer's schedule"""
    lecturers = sorted(set(block['lecturer'] for block in schedule_blocks))

    for lecturer in lecturers:
        lec_blocks = [b for b in schedule_blocks if b['lecturer'] == lecturer]
        if not lec_blocks:
            continue

        fig, axes = plt.subplots(5, 3, figsize=(16, 10))
        fig.suptitle(f'Lecturer Calendar: {lecturer}', fontsize=14, fontweight='bold')
        axes = axes.flatten()

        for week in range(1, min(weeks + 1, 16)):
            ax = axes[week - 1]
            week_blocks = [b for b in lec_blocks if b['week'] == week]

            days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']

            for day_idx in range(5):
                for slot_idx in range(2):
                    x = day_idx
                    y = 1 - slot_idx
                    day_num = day_idx + 1
                    timeslot = 'morning' if slot_idx == 0 else 'afternoon'
                    block = next((b for b in week_blocks if b['day'] == day_num and b['timeslot'] == timeslot), None)

                    if block:
                        color = '#e74c3c' if block['room_type'] == 'practical' else '#3498db'
                        rect = Rectangle((x, y - 0.4), 0.9, 0.4,
                                         facecolor=color, edgecolor='black', linewidth=1.5, alpha=0.7)
                        ax.add_patch(rect)
                        # Show room number (e.g., "#5")
                        room_display = block['room'].replace('Room ', '')
                        text = f"{block['subject_id']}\n{room_display}"
                        ax.text(x + 0.45, y - 0.2, text, ha='center', va='center', fontsize=7, fontweight='bold')
                    else:
                        rect = Rectangle((x, y - 0.4), 0.9, 0.4,
                                         facecolor='white', edgecolor='gray', linewidth=0.5, alpha=0.3)
                        ax.add_patch(rect)

            # Set limits and labels
            ax.set_xlim(-0.1, 5)
            ax.set_ylim(-0.5, 1.5)
            ax.set_xticks(np.arange(5) + 0.45)
            ax.set_xticklabels(days)
            ax.set_yticks([0.2, 0.8])
            ax.set_yticklabels(['Afternoon', 'Morning'])
            ax.set_title(f'Week {week}', fontweight='bold')
            ax.grid(False)
            ax.set_aspect('equal')

        for idx in range(weeks, len(axes)):
            axes[idx].axis('off')

        theory_patch = mpatches.Patch(color='#3498db', label='Theory', alpha=0.7)
        practical_patch = mpatches.Patch(color='#e74c3c', label='Practical', alpha=0.7)
        fig.legend(handles=[theory_patch, practical_patch], loc='lower right', fontsize=10)

        plt.tight_layout()

        lec_filename = lecturer.replace(' ', '_').replace('-', '_')
        output_dir = os.path.join('images', 'schedule')
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f'calendar_lecturer_{lec_filename}.png')
        fig.savefig(path, dpi=110, bbox_inches='tight', pil_kwargs={'optimize': True})
        print(f"✓ Lecturer calendar saved: {path}")
        plt.close(fig)

def main():
    """Main function to generate all calendar visualizations"""
    print("="*60)
    print("SCHEDULE CALENDAR VISUALIZATION")
    print("="*60)
    
    print("\nParsing schedule output...")
    schedule_blocks = parse_schedule_output()
    print(f"✓ Parsed {len(schedule_blocks)} scheduled blocks")
    
    print("\nGenerating visualizations...")
    print("\n1. Room Calendars:")
    create_room_calendar(schedule_blocks, weeks=15)
    
    print("\n2. Student Group Calendars:")
    create_group_calendar(schedule_blocks, weeks=15)

    print("\n3. Lecturer Calendars:")
    create_lecturer_calendar(schedule_blocks, weeks=15)
    
    print("\n4. Weekly Overviews:")
    create_weekly_overview(schedule_blocks, weeks_to_show=5)
    
    print("\n5. Utilization Analysis:")
    create_utilization_heatmap(schedule_blocks, weeks=15)
    
    print("\n" + "="*60)
    print("All calendar visualizations generated successfully!")
    print("="*60)


if __name__ == "__main__":
    main()
