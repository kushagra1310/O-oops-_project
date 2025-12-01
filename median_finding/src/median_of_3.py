import sys
from src.utils import swap, partition_lomuto

def median_of_3_quickselect(arr: list, k: int) -> int:
    """
    Finds the k-th smallest element using Deterministic Median-of-3 Quickselect.
    
    Args:
        arr (list): A list of integers (or TrackedInts).
        k (int): The rank of the element to find.

    Returns:
        int: The value of the k-th smallest element.
    """
    if not 0 <= k < len(arr):
        raise ValueError(f"k={k} is out of bounds.")

    # Increase recursion limit for safety
    sys_limit = sys.getrecursionlimit()
    if sys_limit < len(arr) + 100:
        sys.setrecursionlimit(len(arr) + 1000)

    return _mo3_recursive(arr, 0, len(arr) - 1, k)

def _mo3_recursive(arr: list, low: int, high: int, k: int) -> int:
    if low == high:
        return arr[low]

    # --- Median of 3 Logic Start ---
    mid = (low + high) // 2
    
    # Sort low, mid, high in-place
    if arr[high] < arr[low]:
        swap(arr, low, high)
    if arr[mid] < arr[low]:
        swap(arr, low, mid)
    if arr[high] < arr[mid]:
        swap(arr, mid, high)
        
    # Now arr[low] <= arr[mid] <= arr[high]
    # arr[mid] is our pivot. Swap it to 'high' to use Lomuto partition.
    swap(arr, mid, high)
    # --- Median of 3 Logic End ---

    pivot_final_index = partition_lomuto(arr, low, high)

    if k == pivot_final_index:
        return arr[k]
    elif k < pivot_final_index:
        return _mo3_recursive(arr, low, pivot_final_index - 1, k)
    else:
        return _mo3_recursive(arr, pivot_final_index + 1, high, k)