import math
import sys
import random
from src.utils import swap, partition_lomuto
from src.median_of_medians import median_of_medians_quickselect

def introselect(arr: list, k: int) -> int:
    """
    Finds the k-th smallest element using Randomized Introselect.
    
    Hybrid Approach:
    1. Starts with Randomized Quickselect (Fastest Average Case).
    2. Tracks recursion depth.
    3. If depth > 2 * log(N), switches to Median-of-Medians (Guaranteed Safety).
    
    Args:
        arr (list): List of integers (or TrackedInts).
        k (int): Rank.
    """
    if not 0 <= k < len(arr):
        raise ValueError(f"k={k} is out of bounds.")
        
    sys_limit = sys.getrecursionlimit()
    if sys_limit < len(arr) + 1000:
        sys.setrecursionlimit(len(arr) + 2000)

    # Depth limit heuristic: 2 * log2(n)
    # If we go deeper than this, we assume we hit a pathological case.
    depth_limit = 2 * int(math.log2(len(arr)))
    
    return _introselect_recursive(arr, 0, len(arr) - 1, k, depth_limit)

def _introselect_recursive(arr: list, low: int, high: int, k: int, depth_limit: int) -> int:
    n = high - low + 1
    
    # Base case
    if n == 1:
        return arr[low]
        
    # --- SAFETY SWITCH ---
    # If recursion depth exceeds limit, switch to Median of Medians
    if depth_limit == 0:
        # Pass the specific sub-window to Median of Medians
        # We slice here for simplicity in this project structure
        subarray = arr[low : high+1]
        result = median_of_medians_quickselect(subarray, k - low)
        return result

    # --- Randomized Logic (Primary Strategy) ---
    # Pick a random pivot index
    pivot_index = random.randint(low, high)
    
    # Move pivot to the end for standard Lomuto partition
    swap(arr, pivot_index, high)
    
    # Partition
    pivot_final_index = partition_lomuto(arr, low, high)
    
    # Recurse with decremented depth limit
    if k == pivot_final_index:
        return arr[k]
    elif k < pivot_final_index:
        return _introselect_recursive(arr, low, pivot_final_index - 1, k, depth_limit - 1)
    else:
        return _introselect_recursive(arr, pivot_final_index + 1, high, k, depth_limit - 1)