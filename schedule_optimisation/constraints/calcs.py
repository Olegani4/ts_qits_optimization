from schedule_optimisation.constraints.soft import teacher_movement, teacher_room_reuse, group_splits, teacher_overload
from schedule_optimisation.constraints.hard import teacher_conflicts, room_conflicts, group_conflicts
from schedule_optimisation.weights import TEACHER_MOVE_BETWEEN_CONSECUTIVE, TEACHER_SAME_ROOM_FOR_DIFF, GROUP_SPLIT_DOUBLE, TEACHER_DAILY_OVERLOAD

def calculate_hard_constraints_violations(assignments, lessons, rooms):
    # Calculate the violations for each type of hard constraint
    teacher_conflicts_viol = teacher_conflicts(assignments, lessons)
    room_conflicts_viol = room_conflicts(assignments, rooms)
    group_conflicts_viol = group_conflicts(assignments, lessons)

    # Sum up all hard constraint violations
    hard_violations = teacher_conflicts_viol + room_conflicts_viol + group_conflicts_viol

    # Prepare detailed metrics for analysis and reporting
    hard_metrics = {
        "teacher_conflicts": teacher_conflicts_viol,
        "room_conflicts": room_conflicts_viol,
        "group_conflicts": group_conflicts_viol
    }
    
    return hard_violations, hard_metrics

def build_schedules(assignments, lessons, teachers, groups):
    # Initialise empty schedule structures
    teacher_schedule = {t: {} for t in teachers}  # {teacher: {date: [time_indices]}}
    teacher_rooms_used = {t: [] for t in teachers}  # {teacher: [(date_idx, time_idx, room_idx)]}
    group_schedule = {g: {} for g in groups}  # {group: {date: [time_indices]}}
    
    # Process each lesson assignment to build the schedules
    for i, assign in enumerate(assignments):
        if assign is None: 
            continue  # TODO: Log skipped lessons
        
        # Extract assignment details
        date_idx, time_idx, room_idx = assign
        teacher = lessons[i]["lecturer"]
        grp_list = lessons[i].get("groups", [])
        
        # Update teacher's schedule and room usage
        teacher_schedule[teacher].setdefault(date_idx, []).append(time_idx)  # add time slot to teacher's schedule for this date
        teacher_rooms_used[teacher].append((date_idx, time_idx, room_idx))  # record room usage for this teacher
        
        # Update schedules for each group in the lesson
        for grp in grp_list:
            if grp not in group_schedule:
                group_schedule[grp] = {}
            group_schedule[grp].setdefault(date_idx, []).append(time_idx)  # add time slot to group's schedule for this date
    
    # Time slots sorting within each day for all schedules
    for t in teachers:
        for d in teacher_schedule[t]:
            teacher_schedule[t][d].sort()  # sort time slots within each day for teacher's schedule
    for g in groups:
        for d in group_schedule[g]:
            group_schedule[g][d].sort()  # sort time slots within each day for group's schedule
    
    return teacher_schedule, teacher_rooms_used, group_schedule

def calculate_soft_constraints_violations(assignments, lessons, teachers, groups, rooms):
    # Build structured schedules for easier analysis
    teacher_schedule, teacher_rooms_used, group_schedule = build_schedules(
        assignments, lessons, teachers, groups
    )
        
    # Calculate violations for each type of soft constraint
    teacher_move_viol = teacher_movement(teacher_rooms_used)
    teacher_same_room_viol = teacher_room_reuse(teacher_rooms_used)
    group_split_viol = group_splits(assignments, lessons, teachers)
    overload_viol = teacher_overload(teacher_schedule)

    # Calculate total weighted cost of violations
    soft_violations = (teacher_move_viol * TEACHER_MOVE_BETWEEN_CONSECUTIVE +
                       teacher_same_room_viol * TEACHER_SAME_ROOM_FOR_DIFF +
                       group_split_viol * GROUP_SPLIT_DOUBLE +
                       overload_viol * TEACHER_DAILY_OVERLOAD)
    
    # Prepare detailed metrics for analysis and reporting
    soft_metrics = {
        "teacher_move_between_consecutive": teacher_move_viol,
        "teacher_same_room_for_diff": teacher_same_room_viol,
        "group_split_double": group_split_viol,
        "teacher_daily_overload": overload_viol
    }

    return soft_violations, soft_metrics
