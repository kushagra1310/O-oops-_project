"""Kruskal's MST algorithm."""
from typing import List, Tuple
from utils import Edge, UnionFind

def kruskal_mst(n: int, edges: List[Edge]) -> List[Edge]:
    """Kruskal's algorithm: O(m log m).
    
    Args:
        n: number of vertices
        edges: list of (u, v, weight)
    
    Returns:
        List of MST edges
    """
    uf = UnionFind(n)
    mst = []
    
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if uf.union(u, v):
            mst.append((u, v, w))
            if len(mst) == n - 1:
                break
    
    return mst
