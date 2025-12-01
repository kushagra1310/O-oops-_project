from verify_mst import verify_all_msts, print_verification
"""Complete MST benchmark with visualization support."""
import time
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
sys.path.append('.')


from typing import List, Tuple, Dict
from utils import generate_random_graph, Edge, load_snap_roadnet
from prim_mst import prim_mst
from kruskal_mst import kruskal_mst
from kkt_mst import compute_kkt_mst


def run_timing(n: int, edges: List[Edge]) -> Dict[str, float]:
    """Time all three algorithms once."""
    times = {}
    
    # Prim
    start = time.perf_counter()
    _ = prim_mst(n, edges)
    times['Prim'] = time.perf_counter() - start
    
    # Kruskal  
    start = time.perf_counter()
    _ = kruskal_mst(n, edges)
    times['Kruskal'] = time.perf_counter() - start
    
    # KKT
    start = time.perf_counter()
    _ = compute_kkt_mst(n, edges)
    times['KKT'] = time.perf_counter() - start
    
    return times


def benchmark(n: int, m: int, runs: int = 5, edges: List[Edge] = None, verify: bool = True) -> Dict[str, float]:
    if edges is None:
        edges = generate_random_graph(n, m)
    
    print(f"Graph: n={n:,}, m={m:,}")
    
    if verify:
        results = verify_all_msts(n, edges)
        print_verification(results)
        if not all(abs(r['weight'] - results['Kruskal']['weight']) < 1e-6 and r['valid'] for r in results.values()):
            print(" Skipping timing - correctness failed!")
            return {}
    
    all_times = {'Prim': [], 'Kruskal': [], 'KKT': []}
    for i in range(runs):
        print(f"  Run {i+1}/{runs}...", end=' ')
        try:
            times = run_timing(n, edges)
            for algo in all_times:
                all_times[algo].append(times[algo])
            print("OK")
        except Exception as e:
            print(f"Error during timing: {e}")
            return {}
    
    avg_times = {algo: sum(t) / len(t) for algo, t in all_times.items()}
    
    print("| Algorithm | Avg Time (s) |")
    print("|-----------|--------------|")
    for algo in ['Prim', 'Kruskal', 'KKT']:
        print(f"| {algo:<9} | {avg_times[algo]:10.4f} |")
    
    return avg_times



def plot_results(all_results: Dict[str, List[Tuple[int, float]]]) -> None:
    """Generate publication-quality plots."""
    plt.style.use('default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Scaling plot
    for algo in ['Prim', 'Kruskal', 'KKT']:
        ns = [r[0] for r in all_results[algo]]
        ts = [r[1] for r in all_results[algo]]
        marker = {'Prim': 'o', 'Kruskal': 's', 'KKT': '^'}[algo]
        color = {'Prim': 'blue', 'Kruskal': 'orange', 'KKT': 'green'}[algo]
        ax1.plot(ns, ts, marker+'-', linewidth=2.5, markersize=8, 
                label=f'{algo}', color=color)
    
    ax1.set_xlabel('Vertices n (log scale)')
    ax1.set_ylabel('Runtime (seconds)')
    ax1.set_title('MST Algorithm Scaling')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_xscale('log')
    
    # Bar chart
    sizes = ['n=1K', 'n=5K', 'n=2.1M']
    prim_t = [all_results['Prim'][i][1] for i in range(min(3, len(all_results['Prim'])))]
    kruskal_t = [all_results['Kruskal'][i][1] for i in range(min(3, len(all_results['Kruskal'])))]
    kkt_t = [all_results['KKT'][i][1] for i in range(min(3, len(all_results['KKT'])))]
    
    x = np.arange(len(sizes[:len(prim_t)]))
    width = 0.25
    ax2.bar(x - width, prim_t, width, label='Prim', alpha=0.8)
    ax2.bar(x, kruskal_t, width, label='Kruskal', alpha=0.8)
    ax2.bar(x + width, kkt_t, width, label='KKT', alpha=0.8)
    ax2.set_xlabel('Graph Size')
    ax2.set_ylabel('Runtime (s)')
    ax2.set_title('Runtime Comparison')
    ax2.set_xticks(x)
    ax2.set_xticklabels(sizes[:len(x)])
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('mst_benchmark.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✅ Saved: mst_benchmark.png")


if __name__ == "__main__":
    print("KKT vs Prim vs Kruskal MST Benchmark")
    print("=" * 60)
    
    # Collect results for plotting
    all_results = {'Prim': [], 'Kruskal': [], 'KKT': []}
    
    # Small synthetic graphs
    sizes = [(1000, 5000), (5000, 25000)]
    for n, m in sizes:
        print("\n" + "="*60)
        avgs = benchmark(n, m, runs=3)
        if avgs and len(avgs) == 3:  # Prim, Kruskal, KKT exist
            for algo in all_results:
                all_results[algo].append((n, avgs[algo]))
        else:
            print(f"⚠️ Skipping data collection for n={n}, m={m} due to failed correctness or timing")

    
    # Large real dataset
    if os.path.exists('roadNet-CA.txt'):
        print("\n" + "="*60)
        print("LARGE DATASET: CA Road Network")
        print("=" * 60)
        n, m, edges = load_snap_roadnet('roadNet-CA.txt')
        avgs = benchmark(n, m, runs=1, edges=edges)
        if avgs and len(avgs) == 3:
            for algo in all_results:
                all_results[algo].append((n, avgs[algo]))
        else:
            print(f"⚠️ Skipping data collection for large dataset due to failed correctness or timing")
    
    # Generate visualization
    print("\n🎨 Generating plots...")
    plot_results(all_results)
    print("✅ Complete! Check mst_benchmark.png")
