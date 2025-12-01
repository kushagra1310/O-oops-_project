# Karger Min-Cut Experiments

The analysis are based on three result files:

- `karger_results.csv` – 100 runs of Karger on a single small test graph.[1]
- `karger_vs_stoerwagner.csv` – Karger vs Stoer–Wagner on 50 random graphs.[2]
***

## 1. Karger on the test graph (`karger_results.csv`)

This file records 100 independent runs of Karger on the fixed 5-node test graph, with columns:

- `run` – run index (1–100).  
- `cut_value` – cut weight found by that run.  
- `partition_S`, `partition_T` – the corresponding partition of nodes.

### What the results show

- The **minimum cut of this graph is 4**. There are many runs with `cut_value = 4` and partition `{1} | {2,3,4,5}`. [1]  
- Other runs return higher cuts (5, 6, 7, 8, 9, 11), which are **not** minimum cuts.[1]

### Takeaway

- A **single run of Karger is not guaranteed to find the global min-cut**.  
- For this small graph, roughly a significant fraction of runs hit the true min-cut  
- This illustrates the **randomized nature** of the algorithm: same input graph, different random choices, sometimes optimal, sometimes not.

***

## 2. Karger vs Stoer–Wagner (`karger_vs_stoerwagner.csv`)

This file contains experiments on **50 random connected graphs** with \(n = 10\), \(m = 20\). Columns:

- `graph` – graph index (1–50).  
- `karger_cut`, `karger_time` – cut and runtime for one Karger run.  
- `sw_cut`, `sw_time` – cut and runtime for Stoer–Wagner.  
- `karger_correct` – `True` if `karger_cut == sw_cut`.[2]

### Accuracy

- Stoer–Wagner always returns the exact global min-cut by design.  
- Karger is correct only on some graphs (rows where `karger_correct` is `True`).[2]
- Empirically, Karger’s **per-run accuracy is much less than 1**; it often finds a cut strictly larger than the true min-cut.

### Runtime

- Both `karger_time` and `sw_time` are around \(10^{-4}\) seconds per graph; they are **of the same order of magnitude** for \(n=10\).[2]
- On average, **Karger is slightly faster per run** than Stoer–Wagner in this setting, because it only does random contractions while Stoer–Wagner performs more structured phases.

### Takeaway

  - Karger trades **speed for accuracy** (some runs wrong).  
  - Stoer–Wagner trades **more work** for **always correct** results.

***

## 3. Karger vs Edmonds–Karp vs Stoer–Wagner (`algorithm_comparison.csv`)

This file compares three algorithms on 48 random graphs (same size range):

- `karger_*` – Karger’s cut and time.  
- `ek_*` – Edmonds–Karp max-flow/min-cut run on a chosen source–sink pair.  
- `sw_*` – Stoer–Wagner global min-cut.  
- `karger_correct`, `ek_correct` – whether each algorithm’s cut matches Stoer–Wagner’s cut for that graph.[3]

### Accuracy comparison

- `sw_cut` is treated as the ground truth global min-cut.  
- `karger_correct` is `True` only for some graphs, showing **probabilistic success**.[3]
### Runtime comparison

- For these small graphs, **all three algorithms run in roughly \(10^{-4}–10^{-3}\) seconds** per instance.[3]

### Takeaway

- Stoer–Wagner is the **reliable exact reference**.  
- Karger is **fast per run but only probabilistically correct**.  

***

## 4. Overall conclusions

- **Correctness**
  - Stoer–Wagner always finds the global minimum cut.  
  - Karger may return different cuts on different runs; repeating it many times and taking the best result raises the success probability.  

- **Runtime**
  - On the small graphs tested, all algorithms run very quickly; Karger has the smallest mean time per run, but the gap is small.[2][3]
  - Theoretical time complexity:
    - Karger single run: about \(O(n^2)\) (or \(O(nm)\)); with many repetitions for high success probability, about \(O(n^4 \log n)\).   
    - Stoer–Wagner: \(O(nm + n^2 \log n)\), roughly \(O(n^3)\) on dense graphs.   

- **When to use which**
  - Use **Stoer–Wagner** if you need an exact global min-cut and the graph sizes are moderate.  
  - Use **Karger** when you are okay with a randomized answer and want a simple algorithm; repeat it multiple times if accuracy is important.  