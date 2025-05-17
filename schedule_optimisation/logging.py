import matplotlib.pyplot as plt
import numpy as np

def plot_cost_history(cost_history, algorithm_name, path_to_save, show_ema=False):
    plt.figure(figsize=(10, 5))
    plt.plot(cost_history, label='Cost History', alpha=0.3)

    if show_ema:
        # Exponential Moving Average
        alpha = 0.02  # The less is alpha, the more is smoothing
        ema = []
        for i, v in enumerate(cost_history):
            if i == 0:
                ema.append(v)
            else:
                ema.append(alpha * v + (1 - alpha) * ema[-1])
        plt.plot(ema, label=f'EMA (alpha={alpha})', color='red', linewidth=3)

    plt.xlabel('Iteration')
    plt.ylabel('Cost')
    plt.title(f'Cost History (algorithm={algorithm_name})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(path_to_save)
    plt.show()
    plt.close()
