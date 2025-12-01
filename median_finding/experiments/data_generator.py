import random

def generate_uniform_random(n: int, value_range: tuple = (0, 1000000)) -> list:
    """
    Generates a list of n random integers.
    The 'Standard Playground'.
    """
    return [random.randint(value_range[0], value_range[1]) for _ in range(n)]

def generate_sorted(n: int) -> list:
    """
    Generates a list of n integers in ascending order.
    """
    return list(range(n))

def generate_reverse_sorted(n: int) -> list:
    """
    Generates a list of n integers in descending order.
    """
    return list(range(n, 0, -1))

def generate_adversarial_sequence(n: int) -> list:
    """
    Generates a 'Gasarch' style killer sequence for Median-of-3.
    This places elements such that the median-of-3 logic acts
    perversely, consistently picking bad pivots.
    """
    if n == 0:
        return []
    
    # Initialize array with a basic sorted sequence
    arr = list(range(n))
    
    # We modify the array to trick the pivot selection.
    # We want to force the 'median' of (low, mid, high) to be 
    # one of the extremes of the subarray.
    
    # Logic:
    # 1. k is the middle index
    # 2. Swap mid with low
    # 3. Swap low with high
    # Repeat this process recursively to build the pattern
    
    for i in range(n):
        # Calculate the middle index for the current "window"
        # simulating the binary search nature of the sort
        mid = (0 + i) // 2 
        
        # Swap current 'mid' to the front (0)
        arr[mid], arr[0] = arr[0], arr[mid]
        
        # Then swap front (0) to the current end (i)
        arr[0], arr[i] = arr[i], arr[0]
        
    return arr