import random
from src.utils import swap, partition_lomuto
import sys

def randomized_quickselect(arr: list, k: int) -> int:
    """
    Finds the k-th smallest element in an unordered list using Randomized Quickselect.
    
    This is a wrapper function to handle edge cases and recursion limits.
    
    Args:
        arr (list): A list of integers (or TrackedInts).
        k (int): The rank of the element to find (0-based index). 
                 k=0 is the minimum, k=n-1 is the maximum.

    Returns:
        int: The value of the k-th smallest element.
    """
    if not 0 <= k < len(arr):
        raise ValueError(f"k={k} is out of bounds for array length {len(arr)}")

    # Increase recursion limit for deep recursion on large datasets
    # Standard Python limit is 1000, which breaks on N=10,000 sorted inputs
    sys_limit = sys.getrecursionlimit()
    if sys_limit < len(arr) + 100:
        sys.setrecursionlimit(len(arr) + 1000)

    return _quickselect_recursive(arr, 0, len(arr) - 1, k)

def _quickselect_recursive(arr: list, low: int, high: int, k: int) -> int:
    """
    Internal recursive function for Quickselect.
    """
    # Base case: if the list contains only one element
    if low == high:
        return arr[low]

    # 1. Random Selection: Pick a random pivot index between low and high
    pivot_index = random.randint(low, high)

    # 2. Move pivot to the end to use standard Lomuto partition
    swap(arr, pivot_index, high)

    # 3. Partition the array
    pivot_final_index = partition_lomuto(arr, low, high)

    # 4. Decision: Recurse Left, Right, or Return
    if k == pivot_final_index:
        return arr[k]
    elif k < pivot_final_index:
        return _quickselect_recursive(arr, low, pivot_final_index - 1, k)
    else:
        return _quickselect_recursive(arr, pivot_final_index + 1, high, k)