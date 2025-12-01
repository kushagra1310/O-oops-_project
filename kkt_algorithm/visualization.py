import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Tuple
import os

def plot_scaling(results: Dict[str, List[Tuple[int, int, float]]]) -> None:
    """Plot time vs graph size (n log n vs linear scaling)."""
    plt.figure(figsize=(10, 6))
    
    markers = {'Prim': 'o-', 'Kruskal': 's-', 'KKT': '^-', 'Theory': '--'}
    colors = {'Prim': '#1f77b4', 'Kruskal': '#ff7f0e', 'KKT': '#2ca02c', 'Theory': '#d62728'}
    
    for algo in ['Prim', 'Kruskal', 'KKT']:
        times = results[algo]
        ns = [n for n, m, t in times]
        ts = [t for n, m, t in times]
        
        plt.plot(ns, ts, markers[algo], color=colors[algo], linewidth=2.5, 
                markersize=8, label=f'{algo} (observed)')
    
    # Theoretical curves
    ns = np.logspace(np.log10(100), np.log10(3e6), 100)
    plt.plot(ns, 1e-8 * ns * np.log(ns), '--', color='#1f77b4', alpha=0.7, label="O(n log n)")
    plt.plot(ns, 5e-8 * ns, '--', color='#2ca02c', alpha=0.7, label="O(n) KKT")
    
    plt.xlabel('Vertices (n)', fontsize=12)
    plt.ylabel('Runtime (seconds)', fontsize=12)
    plt.title('MST Algorithm Scaling: KKT Linear vs Classical log n', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    plt.yscale('log')
    plt.tight_layout()
    plt.savefig('mst_scaling.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_speedup(results: Dict[str, List[Tuple[int, int, float]]]) -> None:
    """Bar chart: KKT speedup over classical algorithms."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    sizes = ['n=1K', 'n=5K', 'n=2.1M']
    prim_times = [r[0] for r in results['Prim']]
    kruskal_times = [r[0] for r in results['Kruskal']]
    kkt_times = [r[0] for r in results['KKT']]
    
    x = np.arange(len(sizes))
    width = 0.25
    
    ax1.bar(x - width, prim_times, width, label='Prim', alpha=0.8, color='#1f77b4')
    ax1.bar(x, kruskal_times, width, label='Kruskal', alpha=0.8, color='#ff7f0e')
    ax1.bar(x + width, kkt_times, width, label='KKT', alpha=0.8, color='#2ca02c')
    ax1.set_xlabel('Graph Size')
    ax1.set_ylabel('Runtime (s)')
    ax1.set_title('Absolute Runtime')
    ax1.set_xticks(x)
    ax1.set_xticklabels(sizes)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Speedup bars
    prim_speedup = [prim_t / kkt_t for prim_t, kkt_t in zip(prim_times, kkt_times)]
    kruskal_speedup = [kruskal_t / kkt_t for kruskal_t, kkt_t in zip(kruskal_times, kkt_times)]
    ax2.bar(x - width/2, prim_speedup, width, label='vs Prim', color='#1f77b4', alpha=0.8)
    ax2.bar(x + width/2, kruskal_speedup, width, label='vs Kruskal', color='#ff7f0e', alpha=0.8)
    ax2.axhline(y=1, color='k', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Graph Size')
    ax2.set_ylabel('Speedup (higher = KKT faster)')
    ax2.set_title('KKT Speedup')
    ax2.set_xticks(x)
    ax2.set_xticklabels(sizes)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('mst_speedup.png', dpi=300, bbox_inches='tight')
    plt.show()

def save_results_csv(results: Dict[str, List[Tuple[int, int, float]]]) -> None:
    """Save raw timing data."""
    import csv
    with open('mst_benchmark_results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Algorithm', 'n', 'm', 'time_s'])
        for algo, data in results.items():
            for n, m, t in data:
                writer.writerow([algo, n, m, t])
