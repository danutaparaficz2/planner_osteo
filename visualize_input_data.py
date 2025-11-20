"""
Visualization script for input data analysis.
Creates comprehensive plots to understand the scheduling problem.
"""
import json
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from collections import defaultdict, Counter
import numpy as np


def load_input_data(filename='input_data.json'):
    """Load input data from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)


def plot_subjects_overview(data):
    """Plot subjects by type, blocks required, and spread requirement"""
    subjects = data['subjects']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Subjects Overview', fontsize=16, fontweight='bold')
    
    # 1. Subjects by room type
    room_types = Counter(s['room_type'] for s in subjects)
    ax = axes[0, 0]
    colors = ['#3498db', '#e74c3c']
    ax.bar(room_types.keys(), room_types.values(), color=colors)
    ax.set_title('Subjects by Room Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Subjects')
    ax.grid(axis='y', alpha=0.3)
    for i, (k, v) in enumerate(room_types.items()):
        ax.text(i, v + 0.2, str(v), ha='center', fontweight='bold')
    
    # 2. Blocks required per subject
    ax = axes[0, 1]
    subject_ids = [s['id'] for s in subjects]
    blocks = [s['blocks_required'] for s in subjects]
    colors_map = ['#e74c3c' if s['room_type'] == 'practical' else '#3498db' for s in subjects]
    bars = ax.barh(subject_ids, blocks, color=colors_map)
    ax.set_title('Blocks Required per Subject', fontsize=12, fontweight='bold')
    ax.set_xlabel('Number of Blocks')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    
    # Add legend
    theory_patch = mpatches.Patch(color='#3498db', label='Theory')
    practical_patch = mpatches.Patch(color='#e74c3c', label='Practical')
    ax.legend(handles=[theory_patch, practical_patch])
    
    # 3. Total blocks by type
    ax = axes[1, 0]
    theory_blocks = sum(s['blocks_required'] for s in subjects if s['room_type'] == 'theory')
    practical_blocks = sum(s['blocks_required'] for s in subjects if s['room_type'] == 'practical')
    ax.bar(['Theory', 'Practical'], [theory_blocks, practical_blocks], color=['#3498db', '#e74c3c'])
    ax.set_title('Total Blocks Required by Type', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Blocks')
    ax.grid(axis='y', alpha=0.3)
    for i, v in enumerate([theory_blocks, practical_blocks]):
        ax.text(i, v + 2, str(v), ha='center', fontweight='bold', fontsize=14)
    
    # 4. Spread vs Non-spread subjects
    ax = axes[1, 1]
    spread_subjects = [s for s in subjects if s['spread']]
    non_spread_subjects = [s for s in subjects if not s['spread']]
    
    spread_blocks = sum(s['blocks_required'] for s in spread_subjects)
    non_spread_blocks = sum(s['blocks_required'] for s in non_spread_subjects)
    
    x = np.arange(2)
    width = 0.35
    
    ax.bar(x[0], len(spread_subjects), width, label='Spread', color='#2ecc71')
    ax.bar(x[1], len(non_spread_subjects), width, label='Non-spread', color='#95a5a6')
    
    ax2 = ax.twinx()
    ax2.bar(x[0] + width, spread_blocks, width, color='#27ae60', alpha=0.7)
    ax2.bar(x[1] + width, non_spread_blocks, width, color='#7f8c8d', alpha=0.7)
    
    ax.set_ylabel('Number of Subjects', color='#2ecc71')
    ax2.set_ylabel('Total Blocks', color='#27ae60')
    ax.set_title('Spread Requirement Analysis', fontsize=12, fontweight='bold')
    ax.set_xticks(x + width / 2)
    ax.set_xticklabels(['Spread', 'Non-spread'])
    ax.tick_params(axis='y', labelcolor='#2ecc71')
    ax2.tick_params(axis='y', labelcolor='#27ae60')
    
    plt.tight_layout()
    return fig


def plot_lecturers_analysis(data):
    """Plot lecturer priority distribution and availability"""
    lecturers = data['lecturers']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Lecturers Analysis', fontsize=16, fontweight='bold')
    
    # 1. Lecturers by priority
    ax = axes[0, 0]
    priorities = [l['priority'] for l in lecturers]
    ax.hist(priorities, bins=20, color='#9b59b6', edgecolor='black', alpha=0.7)
    ax.axvline(x=5.5, color='red', linestyle='--', linewidth=2, label='Priority threshold')
    ax.set_title('Lecturer Priority Distribution', fontsize=12, fontweight='bold')
    ax.set_xlabel('Priority Level (lower = higher priority)')
    ax.set_ylabel('Number of Lecturers')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # 2. Availability calendar for top 5 priority lecturers
    ax = axes[0, 1]
    top_lecturers = sorted(lecturers, key=lambda x: x['priority'])[:5]
    
    availability_counts = []
    labels = []
    for lecturer in top_lecturers:
        count = len(lecturer['availability'])
        availability_counts.append(count)
        labels.append(f"{lecturer['name']}\n(P{lecturer['priority']})")
    
    bars = ax.barh(labels, availability_counts, color='#1abc9c')
    ax.set_title('Top 5 Priority Lecturers - Available Slots', fontsize=12, fontweight='bold')
    ax.set_xlabel('Number of Available Time Slots')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(availability_counts):
        ax.text(v + 0.5, i, str(v), va='center', fontweight='bold')
    
    # 3. Availability heatmap for top priority lecturer
    ax = axes[1, 0]
    if top_lecturers and top_lecturers[0]['availability']:
        top_lecturer = top_lecturers[0]
        availability = top_lecturer['availability']
        
        # Create availability matrix (weeks x days x timeslots)
        weeks = 5  # Show first 5 weeks
        days = 5
        
        # Create matrix for morning and afternoon
        morning_matrix = np.zeros((weeks, days))
        afternoon_matrix = np.zeros((weeks, days))
        
        for slot in availability:
            week, day, timeslot = slot
            if week < weeks and 1 <= day <= 5:
                if timeslot == 'morning':
                    morning_matrix[week, day-1] = 1
                else:
                    afternoon_matrix[week, day-1] = 1
        
        # Combined visualization
        combined = morning_matrix + afternoon_matrix * 2
        im = ax.imshow(combined, cmap='RdYlGn', aspect='auto', vmin=0, vmax=2)
        
        ax.set_title(f'{top_lecturer["name"]} - Availability (First 5 Weeks)', 
                    fontsize=12, fontweight='bold')
        ax.set_xlabel('Day of Week')
        ax.set_ylabel('Week')
        ax.set_xticks(range(5))
        ax.set_xticklabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
        ax.set_yticks(range(weeks))
        ax.set_yticklabels([f'W{i}' for i in range(weeks)])
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_ticks([0, 1, 2])
        cbar.set_ticklabels(['None', 'Morning', 'Afternoon'])
    else:
        ax.text(0.5, 0.5, 'No availability data', ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Availability Heatmap', fontsize=12, fontweight='bold')
    
    # 4. Subjects taught by multiple lecturers
    ax = axes[1, 1]
    subject_lecturer_count = defaultdict(list)
    for lecturer in lecturers:
        subject_lecturer_count[lecturer['subject_id']].append(lecturer['name'])
    
    subject_counts = {k: len(v) for k, v in subject_lecturer_count.items()}
    subjects_multi = [(k, v) for k, v in subject_counts.items() if v > 1]
    subjects_single = sum(1 for v in subject_counts.values() if v == 1)
    
    if subjects_multi:
        labels = [s[0] for s in subjects_multi]
        counts = [s[1] for s in subjects_multi]
        ax.bar(labels, counts, color='#f39c12', edgecolor='black', alpha=0.7)
        ax.axhline(y=1, color='gray', linestyle='--', alpha=0.5)
        ax.set_title(f'Subjects with Multiple Lecturers\n({subjects_single} subjects have 1 lecturer)', 
                    fontsize=12, fontweight='bold')
        ax.set_ylabel('Number of Lecturers')
        ax.set_xlabel('Subject ID')
        ax.grid(axis='y', alpha=0.3)
        
        for i, v in enumerate(counts):
            ax.text(i, v + 0.05, str(v), ha='center', fontweight='bold')
    else:
        ax.text(0.5, 0.5, 'Each subject has one lecturer', 
               ha='center', va='center', transform=ax.transAxes)
        ax.set_title('Subjects with Multiple Lecturers', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_rooms_and_groups(data):
    """Plot room capacity and student group assignments"""
    rooms = data['rooms']
    groups = data['student_groups']
    subjects = data['subjects']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Rooms and Student Groups', fontsize=16, fontweight='bold')
    
    # 1. Room distribution by type
    ax = axes[0, 0]
    room_types = Counter(r['room_type'] for r in rooms)
    colors = ['#3498db', '#e74c3c']
    wedges, texts, autotexts = ax.pie(room_types.values(), labels=room_types.keys(), 
                                       autopct='%1.1f%%', colors=colors, startangle=90)
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    ax.set_title('Room Distribution by Type', fontsize=12, fontweight='bold')
    
    # 2. Room capacity
    ax = axes[0, 1]
    room_names = [r['name'] for r in rooms]
    capacities = [r['capacity'] for r in rooms]
    colors_map = ['#e74c3c' if r['room_type'] == 'practical' else '#3498db' for r in rooms]
    
    ax.barh(room_names, capacities, color=colors_map)
    ax.set_title('Room Capacity', fontsize=12, fontweight='bold')
    ax.set_xlabel('Capacity (Students)')
    ax.invert_yaxis()
    ax.grid(axis='x', alpha=0.3)
    
    for i, v in enumerate(capacities):
        ax.text(v + 0.5, i, str(v), va='center', fontweight='bold')
    
    # 3. Student groups - number of subjects
    ax = axes[1, 0]
    group_names = [g['name'] for g in groups]
    subject_counts = [len(g['subject_ids']) for g in groups]
    
    ax.bar(range(len(group_names)), subject_counts, color='#16a085', edgecolor='black', alpha=0.7)
    ax.set_title('Subjects per Student Group', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Subjects')
    ax.set_xticks(range(len(group_names)))
    ax.set_xticklabels([g['id'] for g in groups])
    ax.grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(subject_counts):
        ax.text(i, v + 0.1, str(v), ha='center', fontweight='bold')
    
    # 4. Total blocks per student group
    ax = axes[1, 1]
    subject_blocks = {s['id']: s['blocks_required'] for s in subjects}
    
    group_blocks = []
    group_labels = []
    for group in groups:
        total_blocks = sum(subject_blocks.get(sid, 0) for sid in group['subject_ids'])
        group_blocks.append(total_blocks)
        group_labels.append(group['id'])
    
    bars = ax.bar(range(len(group_labels)), group_blocks, color='#8e44ad', edgecolor='black', alpha=0.7)
    ax.set_title('Total Blocks Required per Student Group', fontsize=12, fontweight='bold')
    ax.set_ylabel('Total Blocks')
    ax.set_xticks(range(len(group_labels)))
    ax.set_xticklabels(group_labels)
    ax.grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(group_blocks):
        ax.text(i, v + 1, str(v), ha='center', fontweight='bold')
    
    plt.tight_layout()
    return fig


def plot_scheduling_constraints(data):
    """Plot scheduling constraints and capacity analysis"""
    config = data['configuration']
    subjects = data['subjects']
    rooms = data['rooms']
    groups = data['student_groups']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Scheduling Constraints & Capacity Analysis', fontsize=16, fontweight='bold')
    
    # 1. Time capacity analysis
    ax = axes[0, 0]
    total_slots = config['weeks'] * config['days_per_week'] * config['timeslots_per_day']
    theory_rooms = len([r for r in rooms if r['room_type'] == 'theory'])
    practical_rooms = len([r for r in rooms if r['room_type'] == 'practical'])
    
    theory_capacity = total_slots * theory_rooms
    practical_capacity = total_slots * practical_rooms
    
    theory_blocks_needed = sum(s['blocks_required'] for s in subjects if s['room_type'] == 'theory')
    practical_blocks_needed = sum(s['blocks_required'] for s in subjects if s['room_type'] == 'practical')
    
    x = np.arange(2)
    width = 0.35
    
    bars1 = ax.bar(x - width/2, [theory_capacity, practical_capacity], width, 
                   label='Capacity', color='#2ecc71', alpha=0.7)
    bars2 = ax.bar(x + width/2, [theory_blocks_needed, practical_blocks_needed], width,
                   label='Required', color='#e74c3c', alpha=0.7)
    
    ax.set_title('Room Capacity vs Required Blocks', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Blocks')
    ax.set_xticks(x)
    ax.set_xticklabels(['Theory Rooms', 'Practical Rooms'])
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Add percentage labels
    for i, (cap, req) in enumerate([(theory_capacity, theory_blocks_needed), 
                                     (practical_capacity, practical_blocks_needed)]):
        utilization = (req / cap * 100) if cap > 0 else 0
        ax.text(i, max(cap, req) + 20, f'{utilization:.1f}%', ha='center', fontweight='bold')
    
    # 2. Subject type distribution per group
    ax = axes[0, 1]
    group_theory = []
    group_practical = []
    group_labels = []
    
    subject_types = {s['id']: s['room_type'] for s in subjects}
    
    for group in groups:
        theory_count = sum(1 for sid in group['subject_ids'] if subject_types.get(sid) == 'theory')
        practical_count = sum(1 for sid in group['subject_ids'] if subject_types.get(sid) == 'practical')
        group_theory.append(theory_count)
        group_practical.append(practical_count)
        group_labels.append(group['id'])
    
    x = np.arange(len(group_labels))
    width = 0.35
    
    ax.bar(x - width/2, group_theory, width, label='Theory', color='#3498db')
    ax.bar(x + width/2, group_practical, width, label='Practical', color='#e74c3c')
    
    ax.set_title('Subject Type Distribution per Group', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Subjects')
    ax.set_xlabel('Student Group')
    ax.set_xticks(x)
    ax.set_xticklabels(group_labels)
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # 3. Weekly scheduling load distribution
    ax = axes[1, 0]
    total_blocks = sum(s['blocks_required'] for s in subjects)
    avg_blocks_per_week = total_blocks / config['weeks']
    slots_per_week = config['days_per_week'] * config['timeslots_per_day']
    num_groups = len(groups)
    
    # Each group can have 2 slots per day (morning/afternoon)
    group_capacity_per_week = slots_per_week
    total_group_capacity = group_capacity_per_week * num_groups
    
    categories = ['Average Weekly\nLoad', 'Weekly Capacity\nper Group', 'Total Weekly\nCapacity']
    values = [avg_blocks_per_week, group_capacity_per_week, total_group_capacity]
    colors_list = ['#e67e22', '#16a085', '#2ecc71']
    
    bars = ax.bar(categories, values, color=colors_list, edgecolor='black', alpha=0.7)
    ax.set_title('Weekly Scheduling Capacity', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Blocks/Slots')
    ax.grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(values):
        ax.text(i, v + 0.5, f'{v:.1f}', ha='center', fontweight='bold')
    
    # 4. Configuration summary
    ax = axes[1, 1]
    ax.axis('off')
    
    summary_text = f"""
    SCHEDULING CONFIGURATION
    {'='*40}
    
    Semester Duration: {config['weeks']} weeks
    Days per Week: {config['days_per_week']} (Mon-Fri)
    Timeslots per Day: {config['timeslots_per_day']} (morning/afternoon)
    
    Total Time Slots: {total_slots}
    
    RESOURCES
    {'='*40}
    Student Groups: {len(groups)}
    Subjects: {len(subjects)} (Theory: {len([s for s in subjects if s['room_type'] == 'theory'])}, Practical: {len([s for s in subjects if s['room_type'] == 'practical'])})
    Lecturers: {len(data['lecturers'])} (Priority 1-5: {len([l for l in data['lecturers'] if l['priority'] <= 5])})
    Rooms: {len(rooms)} (Theory: {theory_rooms}, Practical: {practical_rooms})
    
    WORKLOAD
    {'='*40}
    Total Blocks Required: {total_blocks}
    Average per Week: {avg_blocks_per_week:.1f}
    Average per Group: {total_blocks/len(groups):.1f}
    
    CAPACITY UTILIZATION
    {'='*40}
    Theory: {(theory_blocks_needed/theory_capacity*100):.1f}% of capacity
    Practical: {(practical_blocks_needed/practical_capacity*100):.1f}% of capacity
    """
    
    ax.text(0.1, 0.95, summary_text, transform=ax.transAxes, 
           fontfamily='monospace', fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    return fig


def main():
    """Main function to generate all visualizations"""
    print("Loading input data...")
    data = load_input_data()
    
    print("Generating visualizations...")
    
    # Create all plots
    output_dir = os.path.join('images', 'input')
    os.makedirs(output_dir, exist_ok=True)

    fig1 = plot_subjects_overview(data)
    fig1.savefig(os.path.join(output_dir, 'viz_subjects_overview.png'), dpi=110, bbox_inches='tight', pil_kwargs={'optimize': True})
    print("✓ Subjects overview saved to:", os.path.join(output_dir, 'viz_subjects_overview.png'))
    plt.close(fig1)
    
    fig2 = plot_lecturers_analysis(data)
    fig2.savefig(os.path.join(output_dir, 'viz_lecturers_analysis.png'), dpi=110, bbox_inches='tight', pil_kwargs={'optimize': True})
    print("✓ Lecturers analysis saved to:", os.path.join(output_dir, 'viz_lecturers_analysis.png'))
    plt.close(fig2)
    
    fig3 = plot_rooms_and_groups(data)
    fig3.savefig(os.path.join(output_dir, 'viz_rooms_and_groups.png'), dpi=110, bbox_inches='tight', pil_kwargs={'optimize': True})
    print("✓ Rooms and groups saved to:", os.path.join(output_dir, 'viz_rooms_and_groups.png'))
    plt.close(fig3)
    
    fig4 = plot_scheduling_constraints(data)
    fig4.savefig(os.path.join(output_dir, 'viz_scheduling_constraints.png'), dpi=110, bbox_inches='tight', pil_kwargs={'optimize': True})
    print("✓ Scheduling constraints saved to:", os.path.join(output_dir, 'viz_scheduling_constraints.png'))
    plt.close(fig4)
    
    print("\n" + "="*60)
    print("All visualizations generated successfully!")
    print("="*60)
    
    # Ensure all figures are closed to free memory
    plt.close('all')


if __name__ == "__main__":
    main()
