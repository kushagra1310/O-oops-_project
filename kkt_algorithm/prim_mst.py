"""Prim's MST algorithm using binary heap."""
from typing import List, Tuple
import heapq
from utils import Edge, UnionFind

def prim_mst(n: int, edges: List[Edge]) -> List[Edge]:
    """Prim's algorithm for MST or minimum spanning forest."""
    graph = [[] for _ in range(n)]
    for u, v, w in edges:
        graph[u].append((v, w))
        graph[v].append((u, w))
    
    mst = []
    visited = [False] * n
    
    for start in range(n):
        if visited[start]:
            continue
        pq = [(0, start, -1)]  # (weight, vertex, parent)
        
        while pq:
            w, u, parent = heapq.heappop(pq)
            if visited[u]:
                continue
            visited[u] = True
            if parent != -1:
                mst.append((parent, u, w))
            
            for v, weight in graph[u]:
                if not visited[v]:
                    heapq.heappush(pq, (weight, v, u))
    
    return mst

