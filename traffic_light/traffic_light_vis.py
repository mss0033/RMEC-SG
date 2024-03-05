import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# Assuming 'best_individual' is the output from the improved EC script
# For demonstration, let's define a sample individual manually
best_individual = [119, 119, 117, 119, 119]  # Sample timings for each intersection

# Parameters for simulation
simulation_duration = sum(best_individual)  # Total duration of one cycle of all lights
num_intersections = len(best_individual)
vehicles_per_minute = [15, 25, 20, 30, 10]  # Vehicle inflow rates

# Prepare data for visualization
def prepare_visualization_data(best_individual):
    time_steps = list(range(simulation_duration))
    light_statuses = np.zeros((num_intersections, simulation_duration))  # 0 for red, 1 for green
    
    # Determine light status over time for each intersection
    cycle_time = 0
    for i, duration in enumerate(best_individual):
        for t in range(simulation_duration):
            if cycle_time <= t < cycle_time + duration:
                light_statuses[i, t] = 1  # Green
            else:
                light_statuses[i, t] = 0  # Red
        cycle_time += duration

    return time_steps, light_statuses

# Visualization function (simplified static visualization example)
def visualize_traffic_lights(time_steps, light_statuses):
    plt.figure(figsize=(10, 6))
    for i in range(num_intersections):
        plt.plot(time_steps, light_statuses[i] + i * 1.1, label=f'Intersection {i+1}')  # Offset each line for clarity
    
    plt.xlabel('Time (seconds)')
    plt.ylabel('Traffic Light Status')
    plt.yticks([])
    plt.title('Traffic Light Timing Visualization')
    plt.legend()
    plt.show()

# Main function to run the visualization
def main():
    time_steps, light_statuses = prepare_visualization_data(best_individual)
    visualize_traffic_lights(time_steps, light_statuses)

if __name__ == "__main__":
    main()