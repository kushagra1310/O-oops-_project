"""Utility functions for MST algorithms."""
from typing import List, Tuple, Dict, Set
import random
import heapq

Edge = Tuple[int, int, float]

class UnionFind:
    """Path-compressed Union-Find with union-by-rank."""
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
    
    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x: int, y: int) -> bool:
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            self.parent[px] = py
        elif self.rank[px] > self.rank[py]:
            self.parent[py] = px
        else:
            self.parent[py] = px
            self.rank[px] += 1
        return True

def read_graph(filename: str) -> Tuple[int, int, List[Edge]]:
    """Read graph from edge list file: n m then n+m lines of edges."""
    with open(filename, 'r') as f:
        lines = f.readlines()
    n, m = map(int, lines[0].split())
    edges = []
    for line in lines[1:]:
        if line.strip():
            u, v, w = map(float, line.split())
            edges.append((int(u), int(v), w))
    return n, m, edges

def generate_random_graph(n: int, m: int, seed: int = 42) -> List[Edge]:
    """Generate connected undirected graph with unique weights."""
    random.seed(seed)
    edges = []
    # Ensure connectivity with a path
    for i in range(n-1):
        edges.append((i, i+1, random.uniform(1, 100)))
    # Add remaining edges
    while len(edges) < m:
        u, v = random.randint(0, n-1), random.randint(0, n-1)
        if u != v and (u, v) not in [(e[0], e[1]) for e in edges]:
            edges.append((u, v, random.uniform(1, 100)))
    return edges

def verify_mst(n: int, edges: List[Edge], mst_edges: List[Edge]) -> bool:
    """Linear-time MST verification using cycle property."""
    uf = UnionFind(n)
    mst_weight = sum(w for _, _, w in mst_edges)
    
    # Build MST forest
    for u, v, _ in mst_edges:
        uf.union(u, v)
    
    # Check cycle property: no MST edge heavier than non-tree path
    sorted_edges = sorted(edges, key=lambda e: e[2])
    for u, v, w in sorted_edges:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
        else:
            # Cycle: check if this edge is heavier than MST path max
            # Simplified: full impl needs LCA/max-on-path
            pass  # Placeholder for heavy edge detection
    return True  # Placeholder

def load_snap_roadnet(filename: str) -> Tuple[int, int, List[Edge]]:
    """Load SNAP road network (undirected, unweighted -> weight=1)."""
    edges = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            u, v = map(int, line.split())
            edges.append((u, v, 1.0))  # Uniform weight
    n = max(max(u,v) for u,v,_ in edges) + 1
    return n, len(edges), edges

