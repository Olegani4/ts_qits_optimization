from schedule_optimisation.constraints.calcs import calculate_hard_constraints_violations, calculate_soft_constraints_violations
from schedule_optimisation.weights import HARD_CONFLICTS_PENALTY
import numpy as np

def compute_cost(assignments, lessons, teachers, groups, rooms, iteration=None):
    cost = 0
    
    # Check hard constraints
    hc_cost, hc_metrics = calculate_hard_constraints_violations(assignments, lessons, rooms)
    # If there are violations, return the cost and violation metrics
    if hc_cost > 0:
        cost += hc_cost * HARD_CONFLICTS_PENALTY
        return cost, {"hard_conflicts": hc_metrics, "soft_conflicts": {}}
        
    # Sum up costs considering weights
    sc_cost, sc_metrics = calculate_soft_constraints_violations(assignments, lessons, teachers, groups, rooms)
    cost += sc_cost
    
    # Return total cost and violation metrics
    return cost, {"hard_conflicts": hc_metrics, "soft_conflicts": sc_metrics}


def compute_cost_with_noise(assignments, lessons, teachers, groups, rooms, iteration=None):
    hard_cost, hc_metrics = calculate_hard_constraints_violations(assignments, lessons, rooms)
    if hard_cost > 0:
        return 10_000, {"hard_conflicts": hc_metrics, "soft_conflicts": {}}

    soft_cost, sc_metrics = calculate_soft_constraints_violations(assignments, lessons, teachers, groups, rooms)

    modifier = 400 * np.sin(soft_cost / 20) * np.cos(soft_cost / 30)  # new local minimums
    cost = 100 + soft_cost + modifier + np.random.normal(0, 3)  # cost computation with new local minimums and noise


    return cost, {"hard_conflicts": hc_metrics, "soft_conflicts": sc_metrics}

# compute_cost = compute_cost_with_noise
