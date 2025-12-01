import sys
import os
import time
import csv
import matplotlib.pyplot as plt

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import Metrics, TrackedInt
from src.quickselect import randomized_quickselect
from src.median_of_3 import median_of_3_quickselect
from src.median_of_medians import median_of_medians_quickselect
from src.floyd_rivest import floyd_rivest_quickselect
from src.introselect import introselect

from experiments.data_generator import (
    generate_uniform_random, 
    generate_sorted, 
    generate_adversarial_sequence
)

# Ensure results directories exist
os.makedirs("results/plots", exist_ok=True)
os.makedirs("results/raw_data", exist_ok=True)

def measure_performance(algo, data, k):
    """
    Double-Pass Measurement:
    1. Runs with raw ints to measure accurate TIME.
    2. Runs with TrackedInts to measure accurate COMPARISONS.
    """
    # --- Pass 1: Measure Time (Raw Integers) ---
    data_for_time = data[:] 
    start = time.perf_counter()
    algo(data_for_time, k)
    duration = time.perf_counter() - start

    # --- Pass 2: Measure Comparisons (TrackedInts) ---
    Metrics.reset()
    data_for_comps = [TrackedInt(x) for x in data] 
    algo(data_for_comps, k)
    comparisons = Metrics.comparisons

    return duration, comparisons

def save_csv(filename, headers, rows):
    path = os.path.join("results/raw_data", filename)
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"Saved CSV: {path}")

# ==========================================
# EXPERIMENT 1: The Heuristic Evaluation
# (Modified to include Killer Sequence)
# ==========================================
def exp_random_vs_heuristic():
    print("\n--- Running Exp I: Randomness vs Heuristic (Uniform, Sorted, Killer) ---")
    
   
    N = 10000
    k = N // 2
    
    scenarios = [
        ("Uniform", generate_uniform_random(N)),
        ("Sorted", generate_sorted(N)),
        ("Killer", generate_adversarial_sequence(N))
    ]
    
    csv_rows = []
    labels = []
    qs_times, qs_comps = [], []
    mo3_times, mo3_comps = [], []

    for label, data in scenarios:
        print(f"  Testing {label} Data...")
        # Run Quickselect
        t_qs, c_qs = measure_performance(randomized_quickselect, data, k)
        
        # Run Median-of-3
        t_mo3, c_mo3 = measure_performance(median_of_3_quickselect, data, k)
        
        csv_rows.append([label, t_qs, c_qs, t_mo3, c_mo3])
        labels.append(label)
        qs_times.append(t_qs); qs_comps.append(c_qs)
        mo3_times.append(t_mo3); mo3_comps.append(c_mo3)

    save_csv("exp1_detailed.csv", ["Dataset", "QS_Time", "QS_Comps", "Mo3_Time", "Mo3_Comps"], csv_rows)

    # Plotting
    x = range(len(labels))
    width = 0.35
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Time Plot
    ax1.bar([i - width/2 for i in x], qs_times, width, label='Rand QS')
    ax1.bar([i + width/2 for i in x], mo3_times, width, label='Median-3')
    ax1.set_title(f'Execution Time (N={N})')
    ax1.set_ylabel('Seconds')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.legend()
    # Note: Mo3 bar on Killer will be HUGE.

    # Comparison Plot
    ax2.bar([i - width/2 for i in x], qs_comps, width, label='Rand QS')
    ax2.bar([i + width/2 for i in x], mo3_comps, width, label='Median-3')
    ax2.set_title(f'Comparisons (N={N})')
    ax2.set_ylabel('Total Comparisons')
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.legend()

    plt.tight_layout()
    plt.savefig("results/plots/Exp1_Heuristic_Full_Spectrum.png")
    plt.close()

# ==========================================
# EXPERIMENT 2: Speed vs Safety
# ==========================================
def exp_speed_vs_safety():
    print("\n--- Running Exp II: Speed vs Safety ---")
    sizes = [1000, 2500, 5000, 7500, 10000]
    
    qs_t, qs_c = [], []
    mom_t, mom_c = [], []
    
    for n in sizes:
        data = generate_uniform_random(n)
        k = n // 2
        
        t1, c1 = measure_performance(randomized_quickselect, data, k)
        t2, c2 = measure_performance(median_of_medians_quickselect, data, k)
        
        qs_t.append(t1); qs_c.append(c1)
        mom_t.append(t2); mom_c.append(c2)
        print(f"N={n} processed.")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Time
    ax1.plot(sizes, qs_t, marker='o', label='Quickselect')
    ax1.plot(sizes, mom_t, marker='x', label='Median of Medians')
    ax1.set_title('Wall-Clock Time')
    ax1.set_xlabel('N')
    ax1.set_ylabel('Seconds')
    ax1.legend()
    ax1.grid(True)
    
    # Comparisons
    ax2.plot(sizes, qs_c, marker='o', label='Quickselect')
    ax2.plot(sizes, mom_c, marker='x', label='Median of Medians')
    ax2.set_title('Total Comparisons')
    ax2.set_xlabel('N')
    ax2.set_ylabel('Count')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig("results/plots/Exp2_Speed_Safety.png")
    plt.close()

# ==========================================
# EXPERIMENT 3: Convergence
# ==========================================
def exp_convergence():
    print("\n--- Running Exp III: Convergence (QS vs Floyd-Rivest) ---")
    sizes = [1000, 5000, 10000, 25000, 50000]
    qs_res = [] 
    fr_res = []
    
    for n in sizes:
        data = generate_uniform_random(n)
        k = n // 2
        qs_res.append(measure_performance(randomized_quickselect, data, k))
        fr_res.append(measure_performance(floyd_rivest_quickselect, data, k))
        print(f"N={n} processed.")

    qs_c_per_n = [r[1]/n for r, n in zip(qs_res, sizes)]
    fr_c_per_n = [r[1]/n for r, n in zip(fr_res, sizes)]

    plt.figure(figsize=(8, 5))
    plt.plot(sizes, qs_c_per_n, marker='o', label='Quickselect')
    plt.plot(sizes, fr_c_per_n, marker='s', label='Floyd-Rivest')
    plt.axhline(y=1.5, color='g', linestyle='--', alpha=0.5, label='Theoretical 1.5')
    plt.axhline(y=3.38, color='b', linestyle='--', alpha=0.5, label='Theoretical 3.38')
    plt.title('Comparisons per Element (C/N)')
    plt.xlabel('N')
    plt.ylabel('C / N')
    plt.legend()
    plt.grid(True)
    plt.savefig("results/plots/Exp3_Convergence.png")
    plt.close()

# ==========================================
# EXPERIMENT 4: Practicality Check (Modified)
# QS vs MoM vs Introselect on NORMAL Data
# ==========================================
def exp_practicality_check():
    print("\n--- Running Exp IV: Practicality (QS vs MoM vs Introselect on Uniform) ---")
    sizes = [1000, 5000, 10000, 20000]
    
    # Storage
    r_qs = {'t': [], 'c': []}
    r_mom = {'t': [], 'c': []}
    r_intro = {'t': [], 'c': []}
    
    for n in sizes:
        data = generate_uniform_random(n)
        k = n // 2
        
        # 1. Quickselect (Baseline)
        t, c = measure_performance(randomized_quickselect, data, k)
        r_qs['t'].append(t); r_qs['c'].append(c)
        
        # 2. Median of Medians (The Heavyweight)
        t, c = measure_performance(median_of_medians_quickselect, data, k)
        r_mom['t'].append(t); r_mom['c'].append(c)
        
        # 3. Introselect (The Hybrid)
        t, c = measure_performance(introselect, data, k)
        r_intro['t'].append(t); r_intro['c'].append(c)
        
        print(f"N={n} processed.")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Time Plot
    ax1.plot(sizes, r_qs['t'], marker='o', label='Rand QS')
    ax1.plot(sizes, r_mom['t'], marker='x', label='MoM (Pure)')
    ax1.plot(sizes, r_intro['t'], marker='s', label='Introselect', linestyle='--')
    ax1.set_title('Time on Normal Data (The Overhead Check)')
    ax1.set_ylabel('Seconds')
    ax1.set_xlabel('N')
    ax1.legend()
    ax1.grid(True)

    # Comparison Plot
    ax2.plot(sizes, r_qs['c'], marker='o', label='Rand QS')
    ax2.plot(sizes, r_mom['c'], marker='x', label='MoM (Pure)')
    ax2.plot(sizes, r_intro['c'], marker='s', label='Introselect', linestyle='--')
    ax2.set_title('Comparisons on Normal Data')
    ax2.set_ylabel('Count')
    ax2.set_xlabel('N')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.savefig("results/plots/Exp4_Practicality_Check.png")
    plt.close()

if __name__ == "__main__":
    sys.setrecursionlimit(50000)
    
    exp_random_vs_heuristic()
    exp_speed_vs_safety()
    exp_convergence()
    exp_practicality_check()
    
    print("\nAnalysis complete. Check /results/plots folder.")