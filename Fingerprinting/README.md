# Randomized Fingerprinting: Freivald’s Algorithm

> **Team Member:** Sai Veeksha Tavva

## 📌 Project Overview

This project investigates the efficiency of **Randomized Algorithms** for verifying matrix multiplication. Specifically, it implements **Freivald's Algorithm** (Fingerprinting) to verify if $A \times B = C$ in $O(n^2)$ time, compared to the standard deterministic verification which takes $O(n^3)$.

The implementation is built **from scratch** in pure Python (without using NumPy for core matrix logic) to strictly demonstrate the algorithmic complexity and probabilistic guarantees.

## 📂 Project Structure

Based on the repository organization:

```text
AAD_PROJECT/
├── algorithms/                 # Core logic modules
│   ├── baseline_multiply.py    # Deterministic O(n^3) matrix multiplication
│   ├── freivalds_test.py       # Randomized O(n^2) Freivald's verification
│   └── utils.py                # Matrix generation and helper functions
├── Fingerprinting.ipynb        # Main project report, analysis, and visualization
├── run_experiment.py           # Script to run performance benchmarks
├── requirements.txt            # Python dependencies
├── performance_graph.png       # Generated performance comparison plot
├── Project_Report.md           # Markdown export of the analysis
└── README.md                   # Project documentation