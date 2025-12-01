import math
import random
from src.utils import swap

def floyd_rivest_quickselect(arr: list, k: int) -> int:
    """
    Finds the k-th smallest element using the Floyd-Rivest algorithm.
    Optimized for very large datasets (N > 10,000).
    
    Comparisons expected: ~1.5 * N (vs 3.4 * N for standard Quickselect).
    
    Args:
        arr (list): List of integers (or TrackedInts).
        k (int): Rank of the element.
    """
    if not 0 <= k < len(arr):
        raise ValueError(f"k={k} is out of bounds.")
        
    # We use an iterative structure (or tail-recursion optimization) 
    # because FR modifies the 'left' and 'right' bounds in a loop 
    # to narrow in on the target.
    left = 0
    right = len(arr) - 1
    
    while right > left:
        
        # --- optimization: Sampling Step ---
        # Only use sampling if the range is large enough (heuristic > 600)
        if right - left > 600:
            n = right - left + 1
            i = k - left + 1 # Rank relative to current window
            z = math.log(n)
            
            # Sample size formula from the original paper
            s = 0.5 * math.exp(2 * z / 3)
            
            # Standard deviation adjustment
            # sign determines if we look slightly left or right
            sign = 1 if i - n / 2 >= 0 else -1
            sd = 0.5 * math.sqrt(z * s * (n - s) / n) * sign
            
            # Calculate indices for the new smaller range inside the array
            # We are selecting a sample centered around our target 'k'
            new_left = max(left, int(k - i * s / n + sd))
            new_right = min(right, int(k + (n - i) * s / n + sd))
            
            # Recursively call SELECT on the sample to fix the pivots
            # Note: This looks like recursion, but in FR implementation 
            # it effectively swaps elements into the correct regions 
            # to prepare for the partition below.
            _fr_select(arr, new_left, new_right, k)
        
        # --- Standard Partition Step ---
        # After the sampling step above, arr[k] is a very good pivot guess.
        # We swap it to 'left' (or right) to do the standard partition.
        
        # In the classic FR implementation (Algorithm 489), 
        # the partition is slightly different: it partitions around arr[k].
        
        t = arr[k]
        i = left
        j = right
        
        # Swap pivots to ends to prepare for partition
        swap(arr, left, k)
        if arr[right] > t:
            swap(arr, right, left)
            
        # Standard Hoare-like partition logic specific to FR
        while i < j:
            # Move i right and j left
            swap(arr, i, j) 
            i += 1
            j -= 1
            while arr[i] < t:
                i += 1
            while arr[j] > t:
                j -= 1
                
        # Adjust pivots after partition
        if arr[left] == t:
            swap(arr, left, j)
        else:
            j += 1
            swap(arr, right, j)
            
        # Adjust bounds for next iteration
        if j <= k:
            left = j + 1
        if k <= j:
            right = j - 1
            
    return arr[k]

def _fr_select(arr, left, right, k):
    """
    Recursive helper is not strictly needed if we implement the 
    iterative loop fully, but often FR is described recursively.
    The logic above includes the recursive step inside the main loop 
    by modifying `left` and `right`.
    
    However, the sampling block calls specific recursion.
    We map the recursive step back to the main function logic 
    via the 'new_left' and 'new_right' updates.
    
    In the pure Algorithm 489, the recursive call is:
    SELECT(new_left, new_right, k)
    
    Here, we can simulate that by calling the main function,
    but we must be careful about infinite loops. 
    The original paper swaps elements.
    """
    # Simply calling the main function on the sub-range
    floyd_rivest_quickselect_recursive_step(arr, left, right, k)

def floyd_rivest_quickselect_recursive_step(arr, left, right, k):
    """
    A non-exposed helper to handle the specific recursion inside the sampling block.
    This mimics the logic of the main loop but restricted to a range.
    """
    while right > left:
        if right - left > 600:
            n = right - left + 1
            i = k - left + 1
            z = math.log(n)
            s = 0.5 * math.exp(2 * z / 3)
            sign = 1 if i - n / 2 >= 0 else -1
            sd = 0.5 * math.sqrt(z * s * (n - s) / n) * sign
            new_left = max(left, int(k - i * s / n + sd))
            new_right = min(right, int(k + (n - i) * s / n + sd))
            floyd_rivest_quickselect_recursive_step(arr, new_left, new_right, k)
        
        t = arr[k]
        i = left
        j = right
        swap(arr, left, k)
        if arr[right] > t:
            swap(arr, right, left)
        while i < j:
            swap(arr, i, j)
            i += 1
            j -= 1
            while arr[i] < t:
                i += 1
            while arr[j] > t:
                j -= 1
        if arr[left] == t:
            swap(arr, left, j)
        else:
            j += 1
            swap(arr, right, j)
        if j <= k:
            left = j + 1
        if k <= j:
            right = j - 1