def teacher_conflicts(assignments, lessons):
    # Track teacher assignments for each time slot
    slot_teacher = {}
    violations = 0
    
    # Check each lesson assignment
    for i, assign in enumerate(assignments):
        if assign is None:
            continue
        date_idx, time_idx, _ = assign
        teacher = lessons[i]["lecturer"]
        slot = (date_idx, time_idx)
        
        # Check if teacher is already assigned to this time slot
        if slot in slot_teacher:
            if teacher == slot_teacher[slot]:
                violations += 1
        else:
            slot_teacher[slot] = teacher

    return violations

def room_conflicts(assignments, rooms):
    # Track room assignments for each time slot
    slot_room = {}
    violations = 0
    
    # Check each lesson assignment
    for i, assign in enumerate(assignments):
        if assign is None:
            continue
        date_idx, time_idx, room_idx = assign
        room = rooms[room_idx] if room_idx is not None else None
        slot = (date_idx, time_idx)
        
        # Check if room is already assigned to this time slot
        if room is not None:
            if slot in slot_room:
                if room == slot_room[slot]:
                    violations += 1
            else:
                slot_room[slot] = room

    return violations

def group_conflicts(assignments, lessons):
    # Track group assignments for each time slot
    slot_groups = {}
    violations = 0
    
    # Check each lesson assignment
    for i, assign in enumerate(assignments):
        if assign is None:
            continue
        date_idx, time_idx, _ = assign
        grp_list = lessons[i].get("groups", [])
        slot = (date_idx, time_idx)
        
        # Initialise group set for this time slot if not exists
        if slot not in slot_groups:
            slot_groups[slot] = set()
            
        # Check each group in the lesson
        for grp in grp_list:
            # Check if group is already assigned to this time slot
            if grp in slot_groups[slot]:
                violations += 1
            else:
                slot_groups[slot].add(grp)

    return violations
