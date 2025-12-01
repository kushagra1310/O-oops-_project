import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


import random
from utils import Metrics, TrackedInt
from introselect import introselect

# 1. Generate Random Data
raw_data = [3,2,1,4,5,0]
k = 3


# 2. Wrap data in TrackedInt to count comparisons
tracked_data = [TrackedInt(x) for x in raw_data]

# 3. Reset Metrics
Metrics.reset()

# 4. Run Algorithm
result_obj = introselect(tracked_data, k)

# 5. Verify correctness against Python's built-in sort
sorted_raw = sorted(raw_data)
expected = sorted_raw[k]

print(f"Algorithm Found: {result_obj.value}")
print(f"Correct Answer:  {expected}")
print(f"Comparisons:     {Metrics.comparisons}")
print(f"Swaps:           {Metrics.swaps}")

assert result_obj.value == expected
print("SUCCESS: Randomized Quickselect works.")