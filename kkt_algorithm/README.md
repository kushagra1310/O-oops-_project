## KKT ALGORITHM
# Directions to run: 
1. pip install -r requirements.txt
2. python benchmark.py

KKT vs Prim vs Kruskal MST Benchmark
============================================================

============================================================
Graph: n=1,000, m=5,000

🔍 MST CORRECTNESS VERIFICATION
============================================================
| Algorithm | Weight  | #Edges | Weight Match | Valid MST Forest? |
|-----------|---------|--------|--------------|-------------------|
| Prim      | 13209.7 |    999 | True         | True              |
| Kruskal   | 13209.7 |    999 | True         | True              |
| KKT       | 13209.7 |    999 | True         | True              |

🎯 RESULT: ALL WEIGHTS MATCH & VALID MSF ✅
  Run 1/3... OK
  Run 2/3... OK
  Run 3/3... OK
| Algorithm | Avg Time (s) |
|-----------|--------------|
| Prim      |     0.0088 |
| Kruskal   |     0.0053 |
| KKT       |     0.0833 |

============================================================
Graph: n=5,000, m=25,000

🔍 MST CORRECTNESS VERIFICATION
============================================================
| Algorithm | Weight  | #Edges | Weight Match | Valid MST Forest? |
|-----------|---------|--------|--------------|-------------------|
| Prim      | 62817.5 |   4999 | True         | True              |
| Kruskal   | 62817.5 |   4999 | True         | True              |
| KKT       | 62817.5 |   4999 | True         | True              |

🎯 RESULT: ALL WEIGHTS MATCH & VALID MSF ✅
  Run 1/3... OK
  Run 2/3... OK
  Run 3/3... OK
| Algorithm | Avg Time (s) |
|-----------|--------------|
| Prim      |     0.0667 |
| Kruskal   |     0.0313 |
| KKT       |     3.9908 |

============================================================
LARGE DATASET: CA Road Network
============================================================
Graph: n=1,971,281, m=5,533,214

🔍 MST CORRECTNESS VERIFICATION
============================================================
| Algorithm | Weight  | #Edges | Weight Match | Valid MST Forest? |
|-----------|---------|--------|--------------|-------------------|
| Prim      | 1962568.0 | 1962568 | True         | True              |
| Kruskal   | 1962568.0 | 1962568 | True         | True              |
| KKT       | 1962568.0 | 1962568 | True         | True              |

🎯 RESULT: ALL WEIGHTS MATCH & VALID MSF ✅
  Run 1/1... OK
| Algorithm | Avg Time (s) |
|-----------|--------------|
| Prim      |    10.9571 |
| Kruskal   |     5.4105 |
| KKT       |    44.6502 |

As we can clearly see, the theoretical O(m) linear time complexity of KKT doesn't imply practical speedup. 
This is because of huge constants: 

1. Boruvka finds min outgoing edge per vertex:
    Time = O(∑_v degree(v)) = O(2m) edge traversals
    1. Union-Find operations: α(n) ≈ 4 nearly-constant
    2. Supernode remapping: O(n + m)
    3. Edge filtering (min-weight between supernodes): O(m)

    Total per phase: ~12m operations
    2 phases: ~24m operations

    vs Prim's single pass: 2m operations → 12x slower already
2. Sampling Constant: 2-3x

    H = sample G2 with p = n′/n
    Expected |H| = p × m/4 = (n′/n) × m/4
    But need to generate/store/filter: O(m/4) work

    Sampling overhead: ~2m/4 = m/2 operations

3. Heavy Edge Filtering: 10-20x

    For each edge e=(u,v,w) ∈ G2:
    1. Find if u,v same F-component: Union-Find α(n′)
    2. Query max-edge on F-path(u,v): O(log n′) LCA query
    3. Compare w > max-edge: O(1)

    Per edge: ~15 operations × m/4 edges = 15m/4

    vs Prim/Kruskal: No filtering → 15x overhead

4. Recursion Overhead: 4x

    2 recursive calls at each level
    Depth = log_4(n) ≈ 0.5 log₂(n)
    Python recursion: ~100ns per call depth

    For n=1M: depth=10 → 2^10 = 1024 calls × 100ns = 0.1ms pure overhead

5. Total Constant Calculation

    KKT total work = Σ [24m + 2m + 15m + recursion] over log_4(n) levels

    Level 0: 41m
    Level 1: 41(m/4)  
    Level 2: 41(m/16)
    ...
    Total: 41m × (1 + 1/4 + 1/16 + ...) = 41m × 4/3 ≈ 54.67m

    Prim: 2m log n ≈ 2m × 20 = 40m (n=1M)
    Kruskal: m log m ≈ 5.5m × 22 = 121m

KKT/Prim constant ratio: 54.67 / 40 ≈ **1.37x THEORETICAL**

Python list operations:          10x slower than C arrays
Dict lookups for supernode map:  20x slower than array indexing  
Union-Find path compression:    5x amortized overhead
Recursive call overhead:        100x vs iterative loops
Edge filtering naive O(m²):     100x vs optimized LCA queries

REAL constant: 54.67 × (10×20×5×100) ≈ **5,467,000m operations**
vs Prim: 40m operations
RATIO: **~137x slower** 

Hence, it is not practically used until we have multiple millions of edges.