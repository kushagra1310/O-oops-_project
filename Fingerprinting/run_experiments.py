import time
import matplotlib.pyplot as plt
import csv
from algorithms.utils import create_random_matrix
from algorithms.baseline_multiply import deterministic_multiply
from algorithms.freivalds_test import freivalds_test, k_freivalds_test

plt.style.use('ggplot')

def run_experiment_1():
    """
    Runs Experiment 1: Performance (Time vs. Matrix Size n)
    Generates: performance_data.csv
    """
    print("Running Experiment 1: Performance Benchmark...")
    
    n_sizes = [10, 25, 50, 75, 100, 125, 150]
    times_n3 = []
    times_n2 = []
    
    # Store detailed data
    data_rows = []
    
    for n in n_sizes:
        print(f"  Testing n = {n}...")
        A = create_random_matrix(n)
        B = create_random_matrix(n)
        
        # Time O(n^3) algorithm
        start_time = time.perf_counter()
        C = deterministic_multiply(A, B)
        end_time = time.perf_counter()
        time_n3 = end_time - start_time
        times_n3.append(time_n3)
        
        # Time O(n^2) algorithm
        start_time = time.perf_counter()
        freivalds_test(A, B, C)
        end_time = time.perf_counter()
        time_n2 = end_time - start_time
        times_n2.append(time_n2)
        
        # Calculate speedup
        speedup = time_n3 / time_n2 if time_n2 > 0 else 0
        
        data_rows.append({
            'matrix_size': n,
            'deterministic_time_s': time_n3,
            'freivalds_time_s': time_n2,
            'speedup_factor': speedup
        })
    
    # Save to CSV
    with open('performance_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['matrix_size', 'deterministic_time_s', 
                                                 'freivalds_time_s', 'speedup_factor'])
        writer.writeheader()
        writer.writerows(data_rows)
    
    print("Experiment 1 Complete. Generated 'performance_data.csv'.\n")
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(n_sizes, times_n3, 'o-', label='O(n³) Deterministic Multiply', linewidth=2)
    plt.plot(n_sizes, times_n2, 's-', label="O(n²) Freivald's Test", linewidth=2)
    plt.xlabel("Matrix Size (n)", fontsize=12)
    plt.ylabel("Time (seconds)", fontsize=12)
    plt.title("Performance: Deterministic O(n³) vs. Randomized O(n²)", fontsize=14)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("performance_graph.png", dpi=300)
    print("Generated 'performance_graph.png'.")
    plt.show()

def run_experiment_2():
    """
    Runs Experiment 2: Error Detection Probability
    Generates: error_detection_data.csv
    """
    print("Running Experiment 2: Error Probability...")
    N_TRIALS = 1000
    MATRIX_SIZE = 50
    
    A = create_random_matrix(MATRIX_SIZE)
    B = create_random_matrix(MATRIX_SIZE)
    C_correct = deterministic_multiply(A, B)
    
    # Create an INCORRECT C'
    C_incorrect = [row[:] for row in C_correct]
    C_incorrect[0][0] = C_incorrect[0][0] + 1
    
    detections = 0
    detection_by_batch = []  # Track detection rate every 100 trials
    
    for i in range(N_TRIALS):
        if not freivalds_test(A, B, C_incorrect):
            detections += 1
        
        # Record every 100 trials
        if (i + 1) % 100 == 0:
            batch_rate = (detections / (i + 1)) * 100
            detection_by_batch.append({
                'trials_completed': i + 1,
                'errors_detected': detections,
                'detection_rate_percent': batch_rate
            })
    
    detection_rate = (detections / N_TRIALS) * 100
    
    # Save to CSV
    with open('error_detection_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['trials_completed', 'errors_detected', 
                                                 'detection_rate_percent'])
        writer.writeheader()
        writer.writerows(detection_by_batch)
    
    print("Experiment 2 Complete. Generated 'error_detection_data.csv'.")
    print("Results for Report Table (Section 4.2) ")
    print(f"  Total Trials: {N_TRIALS}")
    print(f"  Errors Detected (returned False): {detections}")
    print(f"  Observed Detection Rate: {detection_rate:.1f}%")
    print(f"  Theoretical Rate: ~50%")

def run_bonus_experiment():
    """
    Runs Bonus Experiment: Improving Reliability with k Iterations
    Generates: k_iterations_data.csv
    """
    print("Running Bonus Experiment: k-Iterations Test...")
    
    K_VALUES = [1, 2, 3, 5, 10, 15, 20]
    K_TRIALS = 200
    MATRIX_SIZE = 50
    
    data_rows = []
    
    for k in K_VALUES:
        print(f"  Testing k = {k}...")
        
        # Create fresh matrices for each k
        A = create_random_matrix(MATRIX_SIZE)
        B = create_random_matrix(MATRIX_SIZE)
        C_correct = deterministic_multiply(A, B)
        C_incorrect = [row[:] for row in C_correct]
        C_incorrect[0][0] = C_incorrect[0][0] + 1
        
        false_positives = 0
        total_time = 0
        
        for _ in range(K_TRIALS):
            start = time.perf_counter()
            if k_freivalds_test(A, B, C_incorrect, k):
                false_positives += 1
            total_time += time.perf_counter() - start
        
        false_positive_rate = (false_positives / K_TRIALS) * 100
        theoretical_error = (1 / 2**k) * 100
        avg_time = total_time / K_TRIALS
        
        data_rows.append({
            'k_iterations': k,
            'trials': K_TRIALS,
            'false_positives': false_positives,
            'false_positive_rate_percent': false_positive_rate,
            'theoretical_error_percent': theoretical_error,
            'avg_time_s': avg_time
        })
    
    # Save to CSV
    with open('k_iterations_data.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['k_iterations', 'trials', 'false_positives',
                                                 'false_positive_rate_percent', 
                                                 'theoretical_error_percent', 'avg_time_s'])
        writer.writeheader()
        writer.writerows(data_rows)
    
    print("Bonus Experiment Complete. Generated 'k_iterations_data.csv'.")
    print("Results for Report (Section 5.3)")
    for row in data_rows:
        print(f"  k={row['k_iterations']:2d}: False Positives={row['false_positives']:3d}/{K_TRIALS} "
              f"({row['false_positive_rate_percent']:5.2f}%), "
              f"Theoretical={row['theoretical_error_percent']:6.4f}%")

def generate_summary_report():
    """
    Creates a summary report combining all experiments
    """
    print("Generating summary report...")
    
    with open('experiment_summary.txt', 'w') as f:
        f.write("FREIVALD'S ALGORITHM - EXPERIMENTAL RESULTS SUMMARY\n")
        f.write("\n")
        
        f.write("DATASETS GENERATED:\n")
        f.write("  1. performance_data.csv - Time complexity comparison\n")
        f.write("  2. error_detection_data.csv - Error detection rates\n")
        f.write("  3. k_iterations_data.csv - Reliability vs. iterations\n\n")
        
        f.write("VISUALIZATIONS:\n")
        f.write("  - performance_graph.png\n\n")
        
    
    print("Generated 'experiment_summary.txt'\n")

if __name__ == "__main__":
    run_experiment_1()
    run_experiment_2()
    run_bonus_experiment()
    generate_summary_report()
    
    print("ALL EXPERIMENTS COMPLETE!")