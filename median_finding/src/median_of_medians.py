import sys
from src.utils import swap, partition_lomuto

def median_of_medians_quickselect(arr: list, k: int) -> int:
    """
    Finds the k-th smallest element using Median of Medians (MoM).
    Guarantees O(N) worst-case time complexity, but with high constant factors.
    
    Args:
        arr (list): A list of integers (or TrackedInts).
        k (int): The rank of the element to find.
    """
    if not 0 <= k < len(arr):
        raise ValueError(f"k={k} is out of bounds.")

    # MoM is recursion-heavy.
    sys_limit = sys.getrecursionlimit()
    if sys_limit < len(arr) + 1000:
        sys.setrecursionlimit(len(arr) + 2000)

    return _mom_recursive(arr, 0, len(arr) - 1, k)

def _mom_recursive(arr: list, low: int, high: int, k: int) -> int:
    """
    Standard Selection logic, but uses MoM to pick the pivot.
    """
    if low == high:
        return arr[low]
    
    # 1. Select Pivot using Median of Medians
    # This function guarantees the pivot is roughly in the middle 30-70% range
    pivot_index = _select_pivot_mom(arr, low, high)
    
    # 2. Move pivot to end for Lomuto partition
    swap(arr, pivot_index, high)
    
    # 3. Standard Partition
    pivot_final_index = partition_lomuto(arr, low, high)
    
    # 4. Recurse
    if k == pivot_final_index:
        return arr[k]
    elif k < pivot_final_index:
        return _mom_recursive(arr, low, pivot_final_index - 1, k)
    else:
        return _mom_recursive(arr, pivot_final_index + 1, high, k)

def _select_pivot_mom(arr: list, low: int, high: int) -> int:
    """
    Finds the 'Median of Medians' of the subarray arr[low...high].
    Returns the INDEX of that median.
    """
    n = high - low + 1
    
    # Base case for small arrays: just sort and pick median
    # 5 is the magic number for MoM analysis, but practically < 10 is fine.
    if n <= 5:
        return _insertion_sort_median(arr, low, high)
        
    # --- Step 1: Divide into groups of 5 and find medians ---
    # We will swap the medians of these groups to the beginning of the array:
    # arr[low], arr[low+1], ... arr[low + num_groups - 1]
    
    num_groups = (n + 4) // 5 # Ceiling division
    
    for i in range(num_groups):
        group_start = low + i * 5
        group_end = min(low + (i * 5) + 4, high)
        
        # Find median of this specific group
        median_idx = _insertion_sort_median(arr, group_start, group_end)
        
        # Move the found median to the 'storage area' at the start of array
        swap(arr, low + i, median_idx)
        
    # --- Step 2: Recursively find the median of the medians ---
    # The medians are now stored in arr[low ... low + num_groups - 1]
    # We need the median of THIS range.
    mom_val = _mom_recursive(arr, low, low + num_groups - 1, low + (num_groups // 2))
    # We need the INDEX of this value within the current window [low...high].
    
    for i in range(low, high + 1):
        if arr[i] == mom_val: # This uses the safer __eq__ now
            return i

def _insertion_sort_median(arr: list, low: int, high: int) -> int:
    """
    Helper: Sorts the small range arr[low...high] and returns the index of the median.
    Using simple insertion sort (or bubble sort) since N <= 5.
    """
    # Simple sort for the small window
    for i in range(low + 1, high + 1):
        key_val = arr[i]
        j = i - 1
        # Note: We compare values but we must be careful not to lose TrackedInt wrappers
        # if you were reconstructing. Here we just swap in place.
        while j >= low and arr[j] > key_val:
            swap(arr, j, j + 1) # Use swap to increment metric counters
            j -= 1
        # Since we swapped element-by-element, the hole is at j+1
        # But our swap helper is naive. 
        # For strict correctness with 'swap' counting, bubble sort is easier for small N.
        
    # Re-implementing with Bubble Sort for strict swap counting 
    # (Insertion sort logic above with `swap` is tricky to align with strict indices)
    # Since N is max 5, performance difference is negligible.
    for i in range(low, high + 1):
        for j in range(low, high - i + low):
            if arr[j] > arr[j + 1]:
                swap(arr, j, j + 1)
                
    # Return the index of the middle element
    return low + (high - low) // 2