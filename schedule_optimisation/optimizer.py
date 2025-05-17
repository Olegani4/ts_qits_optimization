"""
Schedule Optimisation Module

The Schedule Optimisation Module contains main functions for optimising schedules using different 
algorithms. The functions from this module are used to optimise schedules.
"""

from typing import Callable
from schedule_optimisation.cost import compute_cost
from schedule_optimisation.data_preparation import prepare_input_data, prepare_output_data
from schedule_optimisation.algorithms import tabu_search, quantum_inspired_tabu_search

def optimise_schedule(schedule_data, lessons_times, start_date, end_date, algorithm='ts', max_iters=1000, tabu_tenure=50):
    # Prepare input data for optimisation
    lessons, teachers, groups, rooms, time_slots, total_slots, all_dates, current_assignments = prepare_input_data(
        schedule_data, lessons_times, start_date, end_date
    )
        
    # Calculate initial solution cost and penalties
    initial_cost, initial_penalties = compute_cost(current_assignments, lessons, teachers, groups, rooms, iteration=0)

    # Choose the algorithm to use
    if algorithm == 'ts':
        opt_algorithm: Callable = tabu_search
    elif algorithm == 'qits':
        opt_algorithm: Callable = quantum_inspired_tabu_search
    else:
        raise ValueError(f"Invalid algorithm: '{algorithm}'. Available algorithms: 'ts' - Tabu Search, 'qits' - Quantum Inspired Tabu Search.")

    # Run chosen algorithm
    best_assignments, best_cost, best_penalties = opt_algorithm(
        current_assignments, lessons, teachers, groups, rooms, 
        time_slots, total_slots, max_iters, tabu_tenure
    )
    
    # Format the optimised schedule and find performance metrics
    optimised_schedule, metrics = prepare_output_data(
        best_assignments, lessons, rooms, lessons_times, all_dates,
        initial_cost, initial_penalties, best_cost, best_penalties
    )

    return optimised_schedule, metrics
