"""
===================================================================
MODULE 4  -  Block A, Problem 2            Technique: two pointers
-------------------------------------------------------------------
PROBLEM: Count Pairs Below Threshold                   Difficulty: Hard

Given an integer array `nums` and an integer `target`, return the
number of index pairs (i, j) with i < j such that
    nums[i] + nums[j] < target.

Example 1:
  Input:  nums = [1, 2, 3, 4], target = 5
  Output: 2
Example 2:
  Input:  nums = [-2, 0, 1, 3], target = 2
  Output: 4

Constraints:
  - 1 <= len(nums) <= 10**5
  - -10**9 <= nums[i] <= 10**9
  - -2*10**9 <= target <= 2*10**9
  - Strictly less than: nums[i] + nums[j] < target
  - Return the count as an int (it can be large).
===================================================================
"""
from typing import List
import hashlib


# === YOUR SOLUTION =================================================
def solve(nums: List[int], target: int) -> int:
    # TODO: write your solution here
    nums = sorted(nums)
    l,r = 0, len(nums) - 1
    count = 0
    while l < r:
        if nums[l] + nums[r] >= target:
            r -= 1
        else:
            count += r - l
            l += 1
    return count


# === TEST HARNESS (don't edit below) ===============================
VERBOSE = False   # True -> reveal failing hidden INPUTS (never the expected output)

def _h(r) -> str:
    return hashlib.sha256(repr(r).encode()).hexdigest()[:12]

BIG = list(range(200000))

# visible (the problem examples): (args_tuple, expected)
SAMPLE_TESTS = [
    (([1, 2, 3, 4], 5), 2),
    (([-2, 0, 1, 3], 2), 4),
]

# hidden: inputs shown, expected OUTPUT hashed. each probes a constraint.
HIDDEN_TESTS = [
    (([], 100), '5feceb66ffc8'),
    (([5], 10), '5feceb66ffc8'),
    (([1, 1, 1, 1], 2), '5feceb66ffc8'),
    (([1, 1, 1, 1], 3), 'e7f6c011776e'),
    (([-5, -3, -1, 1, 3, 5], 0), 'e7f6c011776e'),
    (([1, 2, 3], 100), '4e07408562be'),
    (([1000000000, 1000000000, -1000000000, -1000000000], 0), '6b86b273ff34'),
    ((BIG, 100000), 'cc547b7bd43b'),
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
        print(f"  {'PASS' if ok else 'FAIL'}  nums={args[0]!r} target={args[1]}  expected={exp}  got={got}")
    print("\nHIDDEN TESTS")
    for i, (args, exph) in enumerate(HIDDEN_TESTS, 1):
        got = solve(*args)
        ok = _h(got) == exph
        sh += ok
        line = f"  Hidden {i}: {'PASS' if ok else 'FAIL'}"
        if not ok and VERBOSE:
            line += f"    (input: nums={_short(args[0])} target={args[1]})"
        print(line)
    print(f"\nSCORE   samples {sp}/{len(SAMPLE_TESTS)}    hidden {sh}/{len(HIDDEN_TESTS)}")

if __name__ == "__main__":
    run()