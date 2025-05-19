# Weights for soft constraints
TEACHER_MOVE_BETWEEN_CONSECUTIVE = 10  # Penalty for teacher who has to move between rooms for consecutive classes
TEACHER_SAME_ROOM_FOR_DIFF = 1         # Penalty for using the same room for different teacher's classes
GROUP_SPLIT_DOUBLE = 5                 # Penalty for splitting a double class (non-consecutive classes for a group with same teacher)
TEACHER_DAILY_OVERLOAD = 2             # Penalty for teacher who has more than 4 classes per day

# Weights for hard constraints
HARD_CONFLICTS_PENALTY = 100_000       # Large penalty multiplier for violating any hard constraint
