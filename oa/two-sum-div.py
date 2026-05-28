"""
===================================================================
MODULE 4  -  Block A, Problem 1            Technique: hashmap counting
-------------------------------------------------------------------
PROBLEM: Divisible Pair Count                          Difficulty: Hard

Given an integer array `nums` and a positive integer `k`, return the
number of index pairs (i, j) with i < j such that
(nums[i] + nums[j]) is divisible by k.

Example 1:
  Input:  nums = [1, 2, 3, 4, 5, 6], k = 3
  Output: 5
Example 2:
  Input:  nums = [-4, -2, 0, 2, 4], k = 4
  Output: 4

Constraints:
  - 1 <= len(nums) <= 10**5
  - -10**9 <= nums[i] <= 10**9
  - 1 <= k <= 10**5
  - Return the count as an int (it can exceed 2**31).
===================================================================
"""
from typing import List
import hashlib


# === YOUR SOLUTION =================================================
from collections import defaultdict
def solve(nums: List[int], k: int) -> int:
    # TODO: write your solution here
    count = 0
    map = defaultdict(int)
    for num in nums:
        r = num % k
        complement = (k - r)
        if r == 0 and r in map:
            count += map[r]
        elif complement in map:
            count += map[complement]
        map[r] += 1
    return count


# === TEST HARNESS (don't edit below) ===============================
VERBOSE = False   # True -> reveal failing hidden INPUTS (never the expected output)

def _h(r) -> str:
    return hashlib.sha256(repr(r).encode()).hexdigest()[:12]

BIG = [(i * 7) % 13 for i in range(200000)]

# visible (the problem examples): (args_tuple, expected)
SAMPLE_TESTS = [
    (([1, 2, 3, 4, 5, 6], 3), 5),
    (([-4, -2, 0, 2, 4], 4), 4),
]

# hidden: inputs shown, expected OUTPUT hashed. each probes a constraint.
HIDDEN_TESTS = [
    (([], 1), '5feceb66ffc8'),
    (([7], 5), '5feceb66ffc8'),
    (([1, 1, 2, 2, 2], 3), 'e7f6c011776e'),
    (([-1, 1, -3, 3], 2), 'e7f6c011776e'),
    (([5, -2, 100, 0], 1), 'e7f6c011776e'),
    (([3, 6, 9], 3), '4e07408562be'),
    (([1000000000, 1000000000, -1000000000], 2), '4e07408562be'),
    ((BIG, 13), 'ad9bfb56e07f'),
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
        print(f"  {'PASS' if ok else 'FAIL'}  nums={args[0]!r} k={args[1]}  expected={exp}  got={got}")
    print("\nHIDDEN TESTS")
    for i, (args, exph) in enumerate(HIDDEN_TESTS, 1):
        got = solve(*args)
        ok = _h(got) == exph
        sh += ok
        line = f"  Hidden {i}: {'PASS' if ok else 'FAIL'}"
        if not ok and VERBOSE:
            line += f"    (input: nums={_short(args[0])} k={args[1]})"
        print(line)
    print(f"\nSCORE   samples {sp}/{len(SAMPLE_TESTS)}    hidden {sh}/{len(HIDDEN_TESTS)}")

if __name__ == "__main__":
    run()