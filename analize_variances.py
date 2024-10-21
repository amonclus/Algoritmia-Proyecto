import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np  # To calculate variance

def run_percolation_program(executable, dimacs_file, percolation_type, step):
    # Run the C++ program and capture the output
    result = subprocess.run(
        [executable],
        input=f"{dimacs_file}\n{percolation_type}\n{step}\n",
        text=True,
        capture_output=True
    )
    #print(result.stdout)

    # Check for errors
    if result.returncode != 0:
        print("Error running the program:", result.stderr)
        return None, None
    
    percolationThreshold = 0.0

    # Parse output to retrieve results
    results = []
    for line in result.stdout.splitlines():
        if line.startswith("q ="):
            # Extract values of q and number of connected components
            parts = line.split(", ")
            q_value = float(parts[0].split("= ")[1])
            num_components = int(parts[1])
            cluster_size = int(parts[2])
            N_sc = float(parts[3])
            results.append((q_value, num_components, cluster_size, N_sc))

        elif line.startswith("Percolación detectada a q ="):
            percolationThreshold = float(line.split("= ")[1])
            print(f"Percolation threshold detected: q = {percolationThreshold}\n")
    
    return results, percolationThreshold


def plot_variance_vs_iterations(iterations, variances):
    # Plot the variance vs number of iterations
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, variances, marker="o", linestyle="-", color="r", label="Variance")
    plt.xlabel("Number of Iterations")
    plt.ylabel("Variance of Percolation Threshold")
    plt.title("Variance of Percolation Threshold vs Number of Iterations")
    plt.legend()
    plt.grid()
    plt.savefig("variance_percolation_iterations2.png")  # Save the plot as a file
    plt.show()


# Parameters
executable = "./programa"  # Path to the C++ executable
dimacs_file = "malla.dimacs"  # DIMACS file
percolation_type = 1  # Bond(1) or Site(2) percolation
step = 0.01  # Step for q
epsilon = 1e-7  # Threshold for variance stability
max_iterations = 10000  # Maximum number of iterations
window_size = 15  # Number of iterations to check for stability

# Initialize variables
thresholds = []
iterations = []
variances = []

for i in range(1, max_iterations + 1):
    print(f"Running iteration {i}")
    
    # Run the C++ program and get results
    results, percolationThreshold = run_percolation_program(executable, dimacs_file, percolation_type, step)
    
    if percolationThreshold is not None:
        thresholds.append(percolationThreshold)

    # Calculate the variance for the current number of thresholds
    if len(thresholds) > 1:
        variance = np.var(thresholds)
        iterations.append(i)
        variances.append(variance)
        print(f"Variance after {i} iterations: {variance}")

        # Check variance stabilization over the rolling window
        if len(variances) > window_size:
            # Calculate the average change in variance over the window
            variance_changes = [
                abs(variances[-(k+1)] - variances[-(k+2)]) for k in range(window_size-1)
            ]
            avg_change_in_variance = np.mean(variance_changes)

            print(f"Average change in variance over the last {window_size} iterations: {avg_change_in_variance}")

            if avg_change_in_variance < epsilon:
                print(f"Variance has stabilized at iteration {i}")
                break
    else:
        # If only one threshold, variance is zero
        variances.append(0)
        iterations.append(i)

# Calculate total variance after the final iteration
total_variance = np.var(thresholds)
print(f"Total variance after {i} iterations: {total_variance}")

# Plot the variance vs iterations
plot_variance_vs_iterations(iterations, variances)