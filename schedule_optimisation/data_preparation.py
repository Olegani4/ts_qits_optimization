import copy
from datetime import datetime, timedelta

def prepare_input_data(schedule_data, lessons_times, start_date, end_date):
    # Convert date strings to datetime objects if they are not datetime objects
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Create a list of all weekdays in the specified date range
    all_dates = []
    cur_date = start_date
    while cur_date <= end_date:
        # Where monday=0, tuesday=1, wednesday=2, thursday=3, friday=4
        if cur_date.weekday() < 5:
            all_dates.append(cur_date.strftime("%Y-%m-%d"))
        cur_date += timedelta(days=1)
    
    # Create all possible time slots (date + time index) for lessons
    # Each slot is identified by a pair (date_index, time_index)
    time_slots = []
    for di, date in enumerate(all_dates):
        for ti, t in enumerate(lessons_times):
            time_slots.append((di, ti))
    total_slots = len(time_slots)
    
    # Filter lessons by type 'Lesson'
    lessons = [lesson for lesson in schedule_data if lesson.get("type") == "Lesson"]
    # Remove from lessons cancelled lessons
    lessons = [lesson for lesson in lessons if str(lesson.get("room")).lower() != "cancelled" and str(lesson.get("room")).lower() != "canceled"]

    # Extract unique resources for checking the constraints
    teachers = {lesson["lecturer"] for lesson in lessons}
    rooms = set() 
    for lesson in schedule_data:
        room = lesson.get("room")
        # Add all rooms from the original schedule to the set, excluding none, null, or cancelled
        if room and str(room).lower() not in ["none", "null", "cancelled"]:
            rooms.add(room)
    rooms = list(rooms)
    groups = set() 
    for lesson in lessons:
        for grp in lesson.get("groups", []):
            groups.add(grp)
    
    # Remain existing time and room assignments and
    # create a list of assignments with lessons length (len(lessons)):
    # - if a lesson has a valid assignment (date, time, room), then save it as (date_index, time_index, room_index)
    # - if a lesson not yet assigned, set it to None
    # NOTE: The assignments in Tabu Search must be the same length as the lessons list.
    full_assignments = [None] * len(lessons)
    for i, lesson in enumerate(lessons):
        found = False
        if lesson.get("date") and lesson.get("time") and lesson.get("room"):
            if lesson["date"] in all_dates:
                date_index = all_dates.index(lesson["date"])
                time_index = next((j for j, t in enumerate(lessons_times)
                                   if t["start_time"] == lesson["time"]["start"]
                                   and t["end_time"] == lesson["time"]["end"]), None)
                if time_index is not None and lesson["room"] in rooms:
                    room_index = rooms.index(lesson["room"])
                    full_assignments[i] = (date_index, time_index, room_index)
                    found = True
        if not found:
            # Set to None if valid assignment not found
            full_assignments[i] = None  # Explicitly indicate no assignment
    
    # Conversion to list for indexing for random selection
    groups = list(groups)
    
    return lessons, teachers, groups, rooms, time_slots, total_slots, all_dates, full_assignments

def prepare_output_data(best_assignments, lessons, rooms, lessons_times, all_dates, initial_cost, initial_penalties, best_cost, best_penalties):
    # Format output data
    optimised_schedule = []
    for i, assign in enumerate(best_assignments):
        lesson = copy.deepcopy(lessons[i])
        if assign is None:
            # Means that the lesson was not assigned and it should not happen for a valid solution
            # TODO: Log this
            continue
        d_idx, t_idx, r_idx = assign
        date_str = all_dates[d_idx]
        time_slot = lessons_times[t_idx]
        # Save date and time in original format
        lesson["date"] = date_str
        lesson["time"] = {"start": time_slot["start_time"], "end": time_slot["end_time"]}
        lesson["room"] = rooms[r_idx] if r_idx is not None else None
        optimised_schedule.append(lesson)

    # Quality metrics (cost and violations)
    metrics = {
        "initial_cost": initial_cost,
        "initial_penalties": initial_penalties,
        "best_cost": best_cost,
        "best_penalties": best_penalties
    }
    
    return optimised_schedule, metrics
