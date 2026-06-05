"""
===================================================================
FORMAT DEMO  -  this is NOT a scored rep, just the harness shape.

PROBLEM: Even-Sum Pairs            [demo]            Difficulty: Easy
Given an integer array `nums`, return the number of index pairs
(i, j) with i < j such that nums[i] + nums[j] is even.

Example 1:
  Input:  nums = [1, 2, 3, 4]
  Output: 2          # pairs (1,3) and (2,4)
Example 2:
  Input:  nums = [2, 2, 2]
  Output: 3

Constraints:
  - 0 <= len(nums) <= 10**5
  - -10**9 <= nums[i] <= 10**9
  - strict pairs: i < j
===================================================================
"""
from typing import List
import hashlib


# === YOUR SOLUTION =================================================
def solve(nums: List[int]) -> int:
    # TODO: write your solution here
    even_count = 0
    odd_count = 0
    for num1 in nums:
        if num1 % 2 == 0:
            even_count += 1
        else:
            odd_count += 1
    even_pairs = (even_count * (even_count - 1)) // 2
    odd_pairs = (odd_count * (odd_count - 1)) // 2
    return even_pairs + odd_pairs


# === TEST HARNESS (don't edit below) ===============================
VERBOSE = False   # set True to reveal failing hidden INPUTS (never the expected output)

def _canon(r) -> str:
    return repr(r)        # output is a single int; compared by its repr

def _h(r) -> str:
    return hashlib.sha256(_canon(r).encode()).hexdigest()[:12]

# visible (these are the problem examples): (args_tuple, expected)
SAMPLE_TESTS = [
    (([1, 2, 3, 4],), 2),
    (([2, 2, 2],), 3),
]

# hidden: inputs shown, expected OUTPUT hashed. each probes a constraint.
HIDDEN_TESTS = [
    (([],), '5feceb66ffc8'),
    (([7],), '5feceb66ffc8'),
    (([-1, -3, 2, 4],), 'd4735e3a265e'),
    (([1, 1, 1, 1, 1],), '4a44dc153642'),
    (([1000000000, -1000000000],), '6b86b273ff34'),
]

def run():
    sp = sh = 0
    print("SAMPLE TESTS")
    for args, exp in SAMPLE_TESTS:
        got = solve(*args)
        ok = got == exp
        sp += ok
        print(f"  {'PASS' if ok else 'FAIL'}  in={args[0]!r}  expected={exp}  got={got}")
    print("\nHIDDEN TESTS")
    for i, (args, exph) in enumerate(HIDDEN_TESTS, 1):
        got = solve(*args)
        ok = _h(got) == exph
        sh += ok
        line = f"  Hidden {i}: {'PASS' if ok else 'FAIL'}"
        if not ok and VERBOSE:
            line += f"    (input was {args[0]!r})"
        print(line)
    print(f"\nSCORE   samples {sp}/{len(SAMPLE_TESTS)}    hidden {sh}/{len(HIDDEN_TESTS)}")

if __name__ == "__main__":
    run()