import copy
import random
import os
import logging
from datetime import datetime
import numpy as np
from schedule_optimisation.logging import plot_cost_history
from schedule_optimisation.cost import compute_cost
from schedule_optimisation.constants import TABU_LIST_CLEAR_THRESHOLD, NEIGHBOUR_CHECKS_LIMIT

def tabu_search(current_assignments, lessons, teachers, groups, rooms, time_slots, total_slots, 
                max_iters=1000, tabu_tenure=50, no_improvement_limit=None):
    # Setup logging to file
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"logs/logs_ts_{timestamp}.txt"
    logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(message)s')

    num_lessons = len(lessons)

    # Tabu list to store forbidden moves
    tabu_list = {}

    # Initialise cost function values and penalties
    current_cost, current_penalties = compute_cost(current_assignments, lessons, teachers, groups, rooms, iteration=0)
    best_assignments = copy.deepcopy(current_assignments)
    best_cost = current_cost
    best_penalties = current_penalties

    logging.debug(f"[TS] Starting Tabu Search with initial cost: {current_cost:.4f}")

    # Main Tabu Search loop
    cost_history = [current_cost]  # Track cost history
    it_count = 0
    no_improve_counter = 0  # Counter for iterations without improvement
    for iteration in range(max_iters):
        it_count += 1
        print(f"[TS] Iteration {it_count}/{max_iters}. Current cost: {current_cost:.4f}")
        logging.debug(f"[TS] Iteration {it_count}/{max_iters}. Current cost: {current_cost:.4f}")
        
        # Generate neighbouring solutions
        best_neighbour = None
        best_neighbour_cost = float('inf')
        best_neighbour_penalties = None
        best_move = None 
        
        # Generate neighbouring solutions
        neighbour_checks = 0
        while neighbour_checks < NEIGHBOUR_CHECKS_LIMIT:
            # Random choose to swap two lessons or move one lesson
            if random.random() < 0.5:
                # Move a single lesson
                lesson_idx = random.randrange(num_lessons)
                old_assign = current_assignments[lesson_idx]
                # Choose a random new time slot
                new_slot_idx = random.randrange(total_slots)
                d_new, t_new = time_slots[new_slot_idx]
                
                # Find available rooms for the new time slot 
                if old_assign is not None:
                    used_rooms_in_slot = {
                        rooms[assign[2]]
                        for assign in current_assignments
                        if assign is not None
                        and assign[2] is not None
                        and assign[0] == d_new
                        and assign[1] == t_new
                        and (assign[0], assign[1]) != (old_assign[0], old_assign[1])
                    }
                else:
                    used_rooms_in_slot = {
                        rooms[assign[2]]
                        for assign in current_assignments
                        if assign is not None
                        and assign[2] is not None
                        and assign[0] == d_new
                        and assign[1] == t_new
                    }
                
                # Get the first available room index
                new_room_idx = None
                for r_index, room in enumerate(rooms):
                    if room not in used_rooms_in_slot:
                        new_room_idx = r_index
                        break  # available room found, break the loop
                if new_room_idx is None:
                    logging.debug(f"[TS] No available room for lesson {lesson_idx} in slot {new_slot_idx} -> skipping")
                    neighbour_checks += 1
                    continue  # no available rooms in this slot, skip
                
                # Create a new assignment for the lesson
                new_assign = (d_new, t_new, new_room_idx)
                move = ("move", lesson_idx, old_assign, new_assign)
            else:
                # Swap two lessons (exchange their time slots and rooms)
                a = random.randrange(num_lessons)
                b = random.randrange(num_lessons)
                if a == b:
                    continue  # skip if the two lessons are the same
                assign_a = current_assignments[a]
                assign_b = current_assignments[b]
                # Create new assignments by swapping their slots and rooms
                move = ("swap", a, b, assign_a, assign_b)
            neighbour_checks += 1
            
            # Check if the move is tabu
            tabu_key = None
            if move[0] == "move":
                _, lesson_idx, old_asgn, new_asgn = move
                # Prevent returning lesson_idx to its previous slot
                tabu_key = (lesson_idx, old_asgn)  # key: lesson and previous slot
            elif move[0] == "swap":
                _, a_idx, b_idx, assign_a, assign_b = move
                # Prevent reverse swap of the same lessons
                tabu_key = ("swap", a_idx, b_idx)
            if tabu_key in tabu_list and tabu_list[tabu_key] > iteration:
                logging.debug(f"[TS] Move is tabu: {move}")
                continue
            
            # Get a neighbouring solution
            neighbour_assignments = copy.deepcopy(current_assignments)
            if move[0] == "move":
                _, lesson_idx, old_asgn, new_asgn = move
                neighbour_assignments[lesson_idx] = new_asgn
            elif move[0] == "swap":
                _, a_idx, b_idx, assign_a, assign_b = move
                neighbour_assignments[a_idx] = assign_b
                neighbour_assignments[b_idx] = assign_a
                
            # Find the cost of the neighbouring solution
            neighbour_cost, neighbour_penalties = compute_cost(neighbour_assignments, lessons, teachers, groups, rooms, iteration=iteration)
            
            # If the solution improves or is at least as good as the current best neighbour, consider it
            if neighbour_cost < best_neighbour_cost:
                best_neighbour_cost = neighbour_cost
                best_neighbour_penalties = neighbour_penalties
                best_neighbour = neighbour_assignments
                best_move = move

        # End of neighbour generation if no valid neighbour found
        if best_neighbour is None:
            logging.debug("[TS] No valid neighbour found - terminating search")
            break  # no valid neighbour found due to all moves are tabu or no moves available
        
        # Accept the best neighbouring solution, even if it is worse than current (uphill move is allowed)
        current_assignments = best_neighbour
        current_cost = best_neighbour_cost
        current_penalties = best_neighbour_penalties
        
        # Update tabu list based on the performed move
        if best_move:
            if best_move[0] == "move":
                _, lesson_idx, old_asgn, new_asgn = best_move
                # Prevent reverse move: returning this lesson to its old slot
                tabu_list[(lesson_idx, old_asgn)] = iteration + tabu_tenure
            elif best_move[0] == "swap":
                _, a_idx, b_idx, assign_a, assign_b = best_move
                # Prevent reverse swap of the same two lessons in both directions
                tabu_list[("swap", a_idx, b_idx)] = iteration + tabu_tenure
                tabu_list[("swap", b_idx, a_idx)] = iteration + tabu_tenure
                
        # Limit tabu list size by removing expired entries
        if len(tabu_list) > TABU_LIST_CLEAR_THRESHOLD:
            # Clean up expired tabu entries
            tabu_list = {k:v for k,v in tabu_list.items() if v > iteration}
            logging.debug(f"[TS] Tabu list size after cleanup: {len(tabu_list)}")
        
        # Update best solution found with the current solution
        if current_cost < best_cost:
            logging.debug(f"[TS] New best solution found: cost {current_cost:.4f} (prev best {best_cost:.4f})")
            best_cost = current_cost
            best_assignments = copy.deepcopy(current_assignments)
            best_penalties = current_penalties
            no_improve_counter = 0  # Reset counter when improvement is found
        else:
            no_improve_counter += 1  # Increment counter when no improvement

        # Check if we should stop due to no improvement
        if no_improvement_limit is not None and no_improve_counter >= no_improvement_limit:
            logging.debug(f"[TS] Stopping search: No improvement for {no_improvement_limit} iterations")
            break

        # Track cost history
        cost_history.append(current_cost)

    # Plot cost history after search is complete
    plot_cost_history(cost_history=cost_history, algorithm_name='ts', path_to_save=f'logs/figures/cost_figure_ts_{timestamp}.png')

    logging.debug(f"[TS] Search completed. Best cost: {best_cost:.4f}")
    return best_assignments, best_cost, best_penalties

def quantum_inspired_tabu_search(current_assignments, lessons, teachers, groups, rooms, time_slots, total_slots,
                                 max_iters=1000, tabu_tenure=50, no_improvement_limit=None):
    # Setup logging configuration
    os.makedirs("logs", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = f"logs/logs_qits_{timestamp}.txt"
    logging.basicConfig(filename=log_path, level=logging.DEBUG, format='%(message)s')

    # Initialize algorithm parameters and state
    num_lessons = len(lessons)
    tabu_list = {}

    # Calculate initial solution cost and store best solution
    current_cost, current_penalties = compute_cost(current_assignments, lessons, teachers, groups, rooms, iteration=0)
    best_assignments = copy.deepcopy(current_assignments)
    best_cost = current_cost
    best_penalties = current_penalties

    logging.debug(f"[QITS] Starting Quantum-Inspired Tabu Search with initial cost: {current_cost:.4f}")

    # Main algorithm loop
    cost_history = [current_cost]  # Track cost history
    it_count = 0
    no_improve_counter = 0
    for iteration in range(max_iters):
        it_count += 1
        print(f"[QITS] Iteration {it_count}/{max_iters}. Current cost: {current_cost:.4f}")
        logging.debug(f"[QITS] Iteration {it_count}/{max_iters}. Current cost: {current_cost:.4f}")

        # Generate neighbour solutions
        neighbours = []
        neighbour_checks = 0
        while neighbour_checks < NEIGHBOUR_CHECKS_LIMIT:
            # Randomly choose between move and swap operations
            if random.random() < 0.5:
                # Move operation: Move a single lesson to a new time slot
                lesson_idx = random.randrange(num_lessons)
                old_assign = current_assignments[lesson_idx]
                new_slot_idx = random.randrange(total_slots)
                d_new, t_new = time_slots[new_slot_idx]

                # Find available rooms in the new time slot
                if old_assign is not None:
                    used_rooms_in_slot = {
                        rooms[assign[2]]
                        for assign in current_assignments
                        if assign is not None
                        and assign[2] is not None
                        and assign[0] == d_new
                        and assign[1] == t_new
                        and (assign[0], assign[1]) != (old_assign[0], old_assign[1])
                    }
                else:
                    used_rooms_in_slot = {
                        rooms[assign[2]]
                        for assign in current_assignments
                        if assign is not None
                        and assign[2] is not None
                        and assign[0] == d_new
                        and assign[1] == t_new
                    }

                # Find first available room
                new_room_idx = None
                for r_index, room in enumerate(rooms):
                    if room not in used_rooms_in_slot:
                        new_room_idx = r_index
                        break
                if new_room_idx is None:
                    neighbour_checks += 1
                    continue

                new_assign = (d_new, t_new, new_room_idx)
                move = ("move", lesson_idx, old_assign, new_assign)
                tabu_key = (lesson_idx, old_assign)

            else:
                # Exchange time slots between two lessons
                a = random.randrange(num_lessons)
                b = random.randrange(num_lessons)
                if a == b:
                    continue
                assign_a = current_assignments[a]
                assign_b = current_assignments[b]
                move = ("swap", a, b, assign_a, assign_b)
                tabu_key = ("swap", a, b)

            # Check if move is tabu
            if tabu_key in tabu_list and tabu_list[tabu_key] > iteration:
                neighbour_checks += 1
                continue

            # Apply move and evaluate new solution
            neighbour_assignments = copy.deepcopy(current_assignments)
            if move[0] == "move":
                _, lesson_idx, _, new_asgn = move
                neighbour_assignments[lesson_idx] = new_asgn
            elif move[0] == "swap":
                _, a_idx, b_idx, assign_a, assign_b = move
                neighbour_assignments[a_idx] = assign_b
                neighbour_assignments[b_idx] = assign_a

            neighbour_cost, neighbour_penalties = compute_cost(
                neighbour_assignments, lessons, teachers, groups, rooms, iteration=iteration
            )

            neighbours.append((move, neighbour_assignments, neighbour_cost, neighbour_penalties))
            neighbour_checks += 1

        if not neighbours:
            logging.debug("[QITS] No valid quantum neighbours found - terminating search")
            break

        # Probabilistic selection from top-K solutions
        top_k_ratio = max(0.1, 0.3 - 0.2 * (iteration / max_iters))  # adaptive K size
        k = max(1, int(top_k_ratio * len(neighbours)))  # number of neighbours to consider
        sorted_neighbours = sorted(neighbours, key=lambda x: x[2])[:k]  # sort neighbours by cost

        # Calculate selection probabilities based on inverse costs
        top_costs = np.array([n[2] for n in sorted_neighbours])  # top neighbours cost
        inv_top_costs = 1 / (top_costs + 1e-6)  # invert costs and add small number to avoid division by zero
        top_probs = inv_top_costs / np.sum(inv_top_costs)  # normalise probabilities

        # Select next solution probabilistically
        chosen_index = np.random.choice(len(sorted_neighbours), p=top_probs)  # choose neighbour (collapse)
        best_move, best_neighbour, best_neighbour_cost, best_neighbour_penalties = sorted_neighbours[chosen_index]

        # Update current solution
        current_assignments = best_neighbour
        current_cost = best_neighbour_cost
        current_penalties = best_neighbour_penalties

        # Update tabu list
        if best_move[0] == "move":
            _, lesson_idx, old_asgn, _ = best_move
            tabu_list[(lesson_idx, old_asgn)] = iteration + tabu_tenure
        elif best_move[0] == "swap":
            _, a_idx, b_idx, _, _ = best_move
            tabu_list[("swap", a_idx, b_idx)] = iteration + tabu_tenure
            tabu_list[("swap", b_idx, a_idx)] = iteration + tabu_tenure

        # Clean up tabu list if it gets too large
        if len(tabu_list) > TABU_LIST_CLEAR_THRESHOLD:
            tabu_list = {k: v for k, v in tabu_list.items() if v > iteration}
            logging.debug(f"[QITS] Tabu list size after cleanup: {len(tabu_list)}")

        # Update best solution if improvement found
        if current_cost < best_cost:
            logging.debug(f"[QITS] New best solution: cost {current_cost:.4f} (prev best {best_cost:.4f})")
            best_cost = current_cost
            best_assignments = copy.deepcopy(current_assignments)
            best_penalties = current_penalties
            no_improve_counter = 0
        else:
            no_improve_counter += 1

        # Check if we should stop due to no improvement
        if no_improvement_limit is not None and no_improve_counter >= no_improvement_limit:
            logging.debug(f"[QITS] Stopping search: No improvement for {no_improvement_limit} iterations")
            break

        # Track cost history
        cost_history.append(current_cost)

    # Plot cost history after search is complete
    plot_cost_history(cost_history=cost_history, algorithm_name='qits', path_to_save=f'logs/figures/cost_figure_qits_{timestamp}.png')

    logging.debug(f"[QITS] Search complete. Best cost: {best_cost:.4f}")
    return best_assignments, best_cost, best_penalties
