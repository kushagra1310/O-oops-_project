import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import random
import matplotlib.pyplot as plt

class GabberGalilExpander:
    """
    Implementation of the Gabber-Galil Expander Graph.
    Vertices are pairs (x, y) in Z_m x Z_m. Total vertices N = m^2.
    Degree is 8.
    """
    def __init__(self, m):
        self.m = m
        self.N = m * m
        self.adj_matrix = None

    def get_neighbors(self, x, y):
        """
        Returns the list of 8 neighbors for vertex (x, y) modulo m.
        According to standard Gabber-Galil / Margulis definitions.
        """
        m = self.m
        neighbors = []
        
        # 1. Standard Grid Neighbors (4)
        neighbors.append(((x + 1) % m, y))
        neighbors.append(((x - 1) % m, y))
        neighbors.append((x, (y + 1) % m))
        neighbors.append((x, (y - 1) % m))
        
        # 2. Shear / Affine Transformations (4)
        # Transformation S: (x, y) -> (x, x+y)
        neighbors.append((x, (x + y) % m))
        neighbors.append((x, (x + y + 1) % m))
        
        # Transformation T: (x, y) -> (x+y, y)
        neighbors.append(((x + y) % m, y))
        neighbors.append(((x + y + 1) % m, y))
        
        return neighbors

    def index_to_coord(self, idx):
        """Convert linear index 0..N-1 to (x, y)."""
        return (idx // self.m, idx % self.m)

    def coord_to_index(self, x, y):
        """Convert (x, y) to linear index 0..N-1."""
        return x * self.m + y

    def build_adjacency_matrix(self):
        """
        Builds the sparse adjacency matrix for spectral analysis.
        """
        row_ind = []
        col_ind = []
        data = []

        for x in range(self.m):
            for y in range(self.m):
                u = self.coord_to_index(x, y)
                nbrs = self.get_neighbors(x, y)
                for nx, ny in nbrs:
                    v = self.coord_to_index(nx, ny)
                    row_ind.append(u)
                    col_ind.append(v)
                    data.append(1)
        
        # Create Compressed Sparse Row matrix
        self.adj_matrix = sp.csr_matrix((data, (row_ind, col_ind)), shape=(self.N, self.N))

    def compute_spectral_gap(self):
        """
        Computes the two largest eigenvalues (magnitude) to verify expansion.
        Returns (lambda_1, lambda_2, gap).
        Expect lambda_1 = 8 (degree).
        """
        if self.adj_matrix is None:
            self.build_adjacency_matrix()
        
        # Compute top 2 eigenvalues
        # 'LM' = Largest Magnitude
        evals = spla.eigs(self.adj_matrix, k=2, which='LM', return_eigenvectors=False)
        
        # Sort by magnitude (descending)
        sorted_evals = sorted(np.abs(evals), reverse=True)
        lambda_1 = sorted_evals[0]
        lambda_2 = sorted_evals[1]
        
        return lambda_1, lambda_2, lambda_1 - lambda_2

    def random_walk(self, k, start_node=None):
        """
        Performs a random walk of length k.
        Returns a list of k vertices (linear indices).
        """
        if start_node is None:
            # Pick uniform random start
            current_idx = random.randint(0, self.N - 1)
        else:
            current_idx = start_node
            
        path = [current_idx]
        
        for _ in range(k - 1):
            cx, cy = self.index_to_coord(current_idx)
            nbrs = self.get_neighbors(cx, cy)
            # Pick a random neighbor (simulating consuming O(1) bits)
            nx, ny = random.choice(nbrs)
            current_idx = self.coord_to_index(nx, ny)
            path.append(current_idx)
            
        return path

# --- EXPERIMENT: Freivalds' Algorithm Application ---

def freivalds_check(A, B, C, r_vector):
    """
    Checks if A * B = C using random vector r.
    Returns True if consistency check passes (A*B*r == C*r).
    """
    # Br = B * r
    Br = np.dot(B, r_vector)
    # A(Br)
    ABr = np.dot(A, Br)
    # Cr
    Cr = np.dot(C, r_vector)
    
    return np.allclose(ABr, Cr)

def generate_matrices(n, error_injection=False):
    """Generates A, B and C = A*B. If error_injection, changes one entry in C."""
    A = np.random.randint(0, 10, (n, n))
    B = np.random.randint(0, 10, (n, n))
    C = np.dot(A, B)
    if error_injection:
        C[0, 0] += 1  # Inject error
    return A, B, C

def run_experiment():
    print("=== BONUS: Expander Graph Experiment ===")
    
    # 1. Setup Expander
    m = 32 # Grid size 32x32 -> 1024 vertices
    N = m*m
    print(f"Constructing Gabber-Galil Graph (N={N} vertices, Degree=8)...")
    gg = GabberGalilExpander(m)
    
    # 2. Verify Spectral Gap
    print("Computing Eigenvalues (may take a moment)...")
    l1, l2, gap = gg.compute_spectral_gap()
    print(f"Lambda_1 (Degree): {l1:.4f}")
    print(f"Lambda_2:          {l2:.4f}")
    print(f"Spectral Gap:      {gap:.4f}")
    if gap > 0.1:
        print(">> Graph is a valid Expander!")
    else:
        print(">> Warning: Spectral gap is small.")
        
    # 3. Probability Amplification Experiment
    print("\n--- Running Probability Amplification on Freivalds' ---")
    
    # Generate bad matrices (AB != C)
    dim = 50
    A, B, C = generate_matrices(dim, error_injection=True)
    
    # We map graph vertices to random vectors.
    # Each vertex index (0..1023) is a seed for a random vector.
    # To keep it deterministic given the seed:
    def get_vector_from_seed(seed, size):
        np.random.seed(seed)
        return np.random.randint(0, 2, size) # binary vector

    # Compare Independent vs Expander Walk
    k_values = [1, 3, 5, 7, 10]
    trials = 1000 # Number of times to repeat the whole experiment to get avg failure rate
    
    print(f"{'k (Walk Len)':<15} | {'Indep. Fail Rate':<20} | {'Expander Fail Rate':<20}")
    print("-" * 65)
    
    for k in k_values:
        # A. Independent Sampling
        # Failure: All k checks say "Correct" (False Negative)
        indep_failures = 0
        for _ in range(trials):
            # Pick k independent seeds
            seeds = [random.randint(0, N-1) for _ in range(k)]
            all_passed = True
            for s in seeds:
                r = get_vector_from_seed(s, dim)
                if not freivalds_check(A, B, C, r):
                    all_passed = False # Caught the error
                    break
            if all_passed:
                indep_failures += 1
                
        # B. Expander Walk Sampling
        exp_failures = 0
        for _ in range(trials):
            # Walk length k
            seeds = gg.random_walk(k)
            all_passed = True
            for s in seeds:
                r = get_vector_from_seed(s, dim)
                if not freivalds_check(A, B, C, r):
                    all_passed = False
                    break
            if all_passed:
                exp_failures += 1
                
        print(f"{k:<15} | {indep_failures/trials:<20.4f} | {exp_failures/trials:<20.4f}")

if __name__ == "__main__":
    run_experiment()