from typing import List, Tuple, Dict
from utils import Edge, UnionFind
import hashlib

def count_components(n: int, edges: List[Edge]) -> int:
    """Count number of connected components by union-find."""
    uf = UnionFind(n)
    for u, v, _ in edges:
        uf.union(u, v)
    # Count distinct parents
    return len(set(uf.find(i) for i in range(n)))


def mst_weight(mst_edges: List[Edge]) -> float:
    """Total MST weight."""
    return sum(w for _, _, w in mst_edges)

def mst_signature(mst_edges: List[Edge]) -> str:
    """Unique hash of MST edges (sorted)."""
    sorted_edges = sorted((min(u,v), max(u,v), w) for u,v,w in mst_edges)
    return hashlib.md5(str(sorted_edges).encode()).hexdigest()

def verify_all_msts(n: int, edges: List[Edge]) -> Dict[str, Dict]:
    """Run all MST algorithms and verify correctness."""
    from prim_mst import prim_mst
    from kruskal_mst import kruskal_mst
    from kkt_mst import compute_kkt_mst
    
    results = {}
    
    prim_mst_edges = prim_mst(n, edges)
    kruskal_mst_edges = kruskal_mst(n, edges)
    kkt_mst_edges = compute_kkt_mst(n, edges)
    
    num_components = count_components(n, edges)
    expected_edge_count = n - num_components
    expected_weight = None  # We'll use Kruskal weight as reference
    
    results['Prim'] = {
        'edges': prim_mst_edges,
        'weight': sum(w for _, _, w in prim_mst_edges),
        'valid': len(prim_mst_edges) == expected_edge_count
    }
    results['Kruskal'] = {
        'edges': kruskal_mst_edges,
        'weight': sum(w for _, _, w in kruskal_mst_edges),
        'valid': len(kruskal_mst_edges) == expected_edge_count
    }
    results['KKT'] = {
        'edges': kkt_mst_edges,
        'weight': sum(w for _, _, w in kkt_mst_edges),
        'valid': len(kkt_mst_edges) == expected_edge_count
    }
    
    expected_weight = results['Kruskal']['weight']
    
    # Check weights match Kruskal
    for algo in results:
        results[algo]['weight_match'] = abs(results[algo]['weight'] - expected_weight) < 1e-6
    
    return results


def print_verification(results: Dict[str, Dict]) -> None:
    """Print verification showing weight match and minimum spanning forest validity."""
    print("\n🔍 MST CORRECTNESS VERIFICATION")
    print("=" * 60)
    print("| Algorithm | Weight  | #Edges | Weight Match | Valid MST Forest? |")
    print("|-----------|---------|--------|--------------|-------------------|")
    
    for algo in ['Prim', 'Kruskal', 'KKT']:
        r = results[algo]
        weight_str = f"{r['weight']:.1f}"
        print(f"| {algo:<9} | {weight_str:>7} | {len(r['edges']):6} | "
              f"{str(r['weight_match']):<12} | {str(r['valid']):<17} |")
    
    all_match = all(r['weight_match'] and r['valid'] for r in results.values())
    print(f"\n🎯 RESULT: {'ALL WEIGHTS MATCH & VALID MSF ✅' if all_match else 'VALIDATION FAILURE ❌'}")



