import sys

class Metrics:
    """
    Global singleton to track operation counts across recursive calls.
    """
    comparisons = 0
    swaps = 0

    @classmethod
    def reset(cls):
        """Resets all metrics to zero."""
        cls.comparisons = 0
        cls.swaps = 0

class TrackedInt:
    """
    A wrapper around an integer to automatically count comparisons.
    Use this for the 'Comparison Count' experiments.
    """
    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        Metrics.comparisons += 1
        return self.value < other.value

    def __gt__(self, other):
        Metrics.comparisons += 1
        return self.value > other.value

    def __le__(self, other):
        Metrics.comparisons += 1
        return self.value <= other.value

    def __ge__(self, other):
        Metrics.comparisons += 1
        return self.value >= other.value

    def __eq__(self, other):
        Metrics.comparisons += 1
        return self.value == other.value
    
    def __repr__(self):
        return str(self.value)

def swap(arr: list, i: int, j: int) -> None:
    """
    Swaps two elements in a list in-place.
    
    Args:
        arr (list): The list containing elements.
        i (int): Index of the first element.
        j (int): Index of the second element.
    """
    if i != j:
        Metrics.swaps += 1
        arr[i], arr[j] = arr[j], arr[i]

def partition_lomuto(arr: list, low: int, high: int) -> int:
    """
    Partitions the array around the last element (arr[high]).
    Elements smaller than pivot go left; larger go right.
    
    Args:
        arr (list): The list to partition.
        low (int): The starting index.
        high (int): The ending index (pivot).

    Returns:
        int: The final index of the pivot element.
    """
    pivot = arr[high]
    i = low
    
    for j in range(low, high):
        # If current element is smaller than or equal to pivot
        if arr[j] < pivot: # This triggers Metrics.comparisons if using TrackedInt
            swap(arr, i, j)
            i += 1
            
    swap(arr, i, high)
    return i