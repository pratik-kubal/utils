"""
===================================================================
MODULE 4  -  Block A, Problem 1            Technique: divide & conquer
-------------------------------------------------------------------
PROBLEM: Count Inversions                              Difficulty: Hard

Given an integer array `nums`, return the number of INVERSIONS — pairs
of indices (i, j) such that i < j and nums[i] > nums[j]. In other
words, count the pairs where the earlier element is strictly greater
than a later element.

Example 1:
  Input:  nums = [2, 4, 1, 3, 5]
  Output: 3
Example 2:
  Input:  nums = [5, 4, 3, 2, 1]
  Output: 10

Constraints:
  - 0 <= len(nums) <= 10**5
  - -10**9 <= nums[i] <= 10**9
  - Strict: i < j AND nums[i] > nums[j]
  - Return the count as an int (can be up to n*(n-1)/2, exceeds 2**31).
===================================================================
"""
from typing import List
import hashlib


# === YOUR SOLUTION =================================================
from typing import Tuple
def solve(nums: List[int]) -> int:
    def merge_sort(array: List[int], count) -> Tuple[list, int]:
        if len(array) > 1:
            # Divide
            split = len(array) // 2
            left_sorted, left_count = merge_sort(array[0:split], count)
            right_sorted, right_count = merge_sort(array[split:], count)
            # Conquer
            return_array = []
            i,j, count = 0, 0, left_count + right_count
            while i < len(left_sorted) and j < len(right_sorted):
                if left_sorted[i] > right_sorted[j]:
                    count += len(left_sorted) - i
                    return_array.append(right_sorted[j])
                    j += 1
                else:
                    return_array.append(left_sorted[i])
                    i += 1
            if i < len(left_sorted):
                return_array.extend(left_sorted[i:])
            if j < len(right_sorted):
                return_array.extend(right_sorted[j:])
            return return_array, count
        else:
            return array, 0
    _, count = merge_sort(nums, 0)
    return count


# === TEST HARNESS (don't edit below) ===============================
VERBOSE = False   # True -> reveal failing hidden INPUTS (never expected outputs)

def _h(r) -> str:
    return hashlib.sha256(repr(r).encode()).hexdigest()[:12]

BIG = list(range(100000, 0, -1))

SAMPLE_TESTS = [
    (([2, 4, 1, 3, 5],), 3),
    (([5, 4, 3, 2, 1],), 10),
]

HIDDEN_TESTS = [
    (([],), '5feceb66ffc8'),
    (([5],), '5feceb66ffc8'),
    (([1, 2, 3, 4, 5],), '5feceb66ffc8'),
    (([5, 4, 3, 2, 1],), '4a44dc153642'),
    (([3, 1, 2],), 'd4735e3a265e'),
    (([1, 1, 1, 1],), '5feceb66ffc8'),
    (([-1, -3, -2, 1],), 'd4735e3a265e'),
    ((BIG,), '9819da9e5a0f'),
]

def _short(x, n=120):
    s = repr(x)
    return s if len(s) <= n else s[:n] + f"...<len {len(x)}>"

def run():
    sp = sh = 0
    print("SAMPLE TESTS")
    for args, exp in SAMPLE_TESTS:
        got = solve(*args)
        ok = got == exp
        sp += ok
        print(f"  {'PASS' if ok else 'FAIL'}  nums={args[0]!r}  expected={exp}  got={got}")
    print("\nHIDDEN TESTS")
    for i, (args, exph) in enumerate(HIDDEN_TESTS, 1):
        got = solve(*args)
        ok = _h(got) == exph
        sh += ok
        line = f"  Hidden {i}: {'PASS' if ok else 'FAIL'}"
        if not ok and VERBOSE:
            line += f"    (input: nums={_short(args[0])})"
        print(line)
    print(f"\nSCORE   samples {sp}/{len(SAMPLE_TESTS)}    hidden {sh}/{len(HIDDEN_TESTS)}")

if __name__ == "__main__":
    run()