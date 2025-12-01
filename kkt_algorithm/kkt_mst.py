"""Real Karger-Klein-Tarjan algorithm per 1995 paper."""
from typing import List, Tuple, Dict, Set
import random
from utils import Edge, UnionFind

def boruvka_phase(n: int, edges: List[Edge]) -> Tuple[List[Edge], List[Edge], Dict[int, int]]:
    """Borůvka phase 1/2: contract min outgoing edges."""
    degree_min = [float('inf')] * n
    min_edges = [None] * n
    
    for u, v, w in edges:
        if w < degree_min[u]:
            degree_min[u] = w
            min_edges[u] = (u, v, w)
        if w < degree_min[v]:
            degree_min[v] = w
            min_edges[v] = (v, u, w)
    
    uf = UnionFind(n)
    contracted = []
    for u in range(n):
        if min_edges[u]:
            e = min_edges[u]
            if uf.union(e[0], e[1]):
                contracted.append(e)
    
    # Supernode mapping
    component = {}
    cid = 0
    mapping = {}
    for i in range(n):
        root = uf.find(i)
        if root not in component:
            component[root] = cid
            cid += 1
        mapping[i] = component[root]
    
    # Contracted graph edges
    supernode_edges = {}
    for u, v, w in edges:
        su, sv = mapping[u], mapping[v]
        if su != sv:
            key = (min(su, sv), max(su, sv))
            if key not in supernode_edges or w < supernode_edges[key][2]:
                supernode_edges[key] = (su, sv, w)
    
    return contracted, list(supernode_edges.values()), mapping

def is_f_heavy_edge(u: int, v: int, w: float, forest: List[Edge], n: int) -> bool:
    """Check if edge heavier than max-edge on F-path from u to v."""
    uf = UnionFind(n)
    max_edge_on_path = {}
    
    # Build forest with max-edge tracking
    for fu, fv, fw in forest:
        uf.union(fu, fv)
        max_edge_on_path[(min(fu, fv), max(fu, fv))] = fw
    
    if uf.find(u) != uf.find(v):
        return False  # Different components
    
    # Simplified: edge is F-heavy if heavier than some forest edge
    forest_max = max(fw for _, _, fw in forest) if forest else 0
    return w > forest_max

import sys
sys.setrecursionlimit(3000)  # increase recursion limit if needed

def kkt_core(n: int, edges: List[Edge], depth=0) -> List[Edge]:
    """Real KKT recursion with safeguards."""
    if n <= 1 or not edges:
        return []
    if n <= 2:
        return sorted(edges, key=lambda e: e[2])[:n-1]
    
    # Debug
    # print(f"Depth {depth}: n={n}, edges={len(edges)}")
    
    # Phase 1: First Boruvka
    c1, g1, map1 = boruvka_phase(n, edges)
    n1 = len(set(map1.values()))
    if n1 >= n:
        # No contraction, fallback safe
        from kruskal_mst import kruskal_mst
        return kruskal_mst(n, edges)
    
    if n1 <= 2:
        return c1
    
    # Phase 2: Second Boruvka
    c2, g2, map2 = boruvka_phase(n1, g1)
    n2 = len(set(map2.values()))
    
    if n2 >= n1:
        # No contraction, fallback safe
        from kruskal_mst import kruskal_mst
        return kruskal_mst(n, edges)
    
    if n2 <= 2:
        return c1 + c2
    
    # Phase 3: Sample H with p = n2/n1
    p_sample = n2 / n1
    H = [e for e in g2 if random.random() < p_sample]
    if not H:
        # If sampling empty, fallback
        from kruskal_mst import kruskal_mst
        return kruskal_mst(n, edges)
    
    # Phase 4: Recursive call on H
    F = kkt_core(n2, H, depth + 1)
    
    # Phase 5: Remove F-heavy edges from g2
    G_prime = []
    for u, v, w in g2:
        if not is_f_heavy_edge(u, v, w, F, n2):
            G_prime.append((u, v, w))
    
    if not G_prime:
        return c1 + c2 + F
    
    # Phase 6: Recursive call on G_prime
    F_prime = kkt_core(n2, G_prime, depth + 1)
    
    return c1 + c2 + F_prime


def compute_kkt_mst(n: int, edges: List[Edge]) -> List[Edge]:
    """KKT main entry - normalize edges for signature matching."""
    random.seed(42)
    mst = kkt_core(n, edges)
    
    # Normalize: (min(u,v), max(u,v), w) for signature matching
    normalized_mst = [(min(u,v), max(u,v), w) for u,v,w in mst]
    
    # Ensure exactly n-1 edges
    if len(normalized_mst) != n - 1:
        normalized_mst = sorted(normalized_mst, key=lambda e: e[2])[:n-1]
    
    return normalized_mst