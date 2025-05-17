def teacher_movement(teacher_rooms_used):
    teacher_move_viol = 0
    
    # Process each teacher's room usage
    for t, used in teacher_rooms_used.items():
        # Group room usage by day to simplify the processing
        by_day = {}
        for (d, tm, r) in used:
            by_day.setdefault(d, []).append((tm, r))
            
        # Check consecutive classes within each day
        for d, entries in by_day.items():
            # Sort entries by time to check consecutive classes
            entries.sort(key=lambda x: x[0])
            # Check each pair of consecutive classes
            for idx in range(len(entries) - 1):
                time_idx, room_idx = entries[idx]
                next_time_idx, next_room_idx = entries[idx + 1]
                # If classes are consecutive (next time slot)
                if next_time_idx == time_idx + 1:
                    # Check if teacher had to move between different rooms
                    if room_idx is not None and next_room_idx is not None and room_idx != next_room_idx:
                        teacher_move_viol += 1
    
    return teacher_move_viol

def teacher_room_reuse(teacher_rooms_used):
    teacher_same_room_viol = 0
    
    # Process each teacher's room usage
    for t in teacher_rooms_used:
        # Track unique rooms used by the teacher
        rooms_for_teacher = set()
        for (_, _, room_idx) in teacher_rooms_used[t]:
            if room_idx is not None:
                rooms_for_teacher.add(room_idx)
        
        # Calculate violations based on room diversity
        total_classes = len(teacher_rooms_used[t])
        distinct_rooms = len(rooms_for_teacher)
        if total_classes > 0:
            # Penalise each class beyond the first in a different room
            teacher_same_room_viol += (total_classes - distinct_rooms)
    
    return teacher_same_room_viol

def group_splits(assignments, lessons, teachers):
    group_split_viol = 0
    
    # Process each teacher's schedule
    for t in teachers:
        # Group lessons by student group
        grp_lessons = {}
        for i, assign in enumerate(assignments):
            if assign is None: 
                continue
            if lessons[i]["lecturer"] != t:
                continue
            date_idx, time_idx, _ = assign
            # Track lesson times for each group
            for grp in lessons[i].get("groups", []):
                grp_lessons.setdefault(grp, []).append((date_idx, time_idx))
        
        # Check for split classes within each group
        for grp, times in grp_lessons.items():
            # Sort lessons by date and time
            times.sort()
            # Initialise flags to track isolated classes
            lonely_flags = [True]*len(times)
            # Check consecutive classes
            for k in range(len(times)-1):
                d1, t1 = times[k]
                d2, t2 = times[k+1]
                # If classes are on the same day and consecutive
                if d1 == d2 and t2 == t1 + 1:
                    # Mark both classes as not isolated
                    lonely_flags[k] = False
                    lonely_flags[k+1] = False
            # Count isolated classes as violations
            for flag in lonely_flags:
                if flag:
                    group_split_viol += 1
    
    return group_split_viol

def teacher_overload(teacher_schedule):
    overload_viol = 0
    
    # Process each teacher's daily schedule
    for t in teacher_schedule:
        for d, times in teacher_schedule[t].items():
            count = len(times)
            # Penalise classes beyond the daily limit of 4
            if count > 4:
                overload_viol += (count - 4)
                # Additional penalty for higher workload (more than 6 classes)
                if count > 6:
                    overload_viol += (count - 6)
    
    return overload_viol
