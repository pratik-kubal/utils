"""
===================================================================
MODULE 4  -  Block A, Problem 3            Technique: greedy
-------------------------------------------------------------------
PROBLEM: Maximum Non-Overlapping Tasks                 Difficulty: Hard

You're given a list `tasks` where each tasks[i] = [start_i, end_i]
represents a task with a fixed start and end time. You can only
perform one task at a time. Two tasks [a, b] and [c, d] are
COMPATIBLE if b <= c or d <= a — i.e., they don't overlap. Touching
at an endpoint (b == c or d == a) is allowed.

Return the maximum number of tasks you can complete.

Example 1:
  Input:  tasks = [[1, 4], [2, 3], [3, 5], [6, 7]]
  Output: 3
Example 2:
  Input:  tasks = [[1, 10], [2, 3], [3, 4], [4, 5]]
  Output: 3

Constraints:
  - 0 <= len(tasks) <= 10**5
  - 0 <= start_i < end_i <= 10**9
  - Compatible: b <= c or d <= a (endpoint touch is OK).
  - Input NOT guaranteed sorted.
  - Return the count as an int.
===================================================================
"""
from typing import List
import hashlib


# === YOUR SOLUTION =================================================
from math import inf
def solve(tasks: List[List[int]]) -> int:
    tasks.sort(key=lambda item: item[1])
    num_tasks = 0
    last_end_time = -inf
    for task in tasks:
        begin_time = task[0]
        end_time = task[1]
        if last_end_time <= begin_time:
            num_tasks += 1
            last_end_time = end_time
    return num_tasks


# === TEST HARNESS (don't edit below) ===============================
VERBOSE = False   # True -> reveal failing hidden INPUTS (never the expected output)

def _h(r) -> str:
    return hashlib.sha256(repr(r).encode()).hexdigest()[:12]

BIG = [[i, i + (i % 5) + 1] for i in range(50000)]

# visible (the problem examples): (args_tuple, expected)
SAMPLE_TESTS = [
    (([[1, 4], [2, 3], [3, 5], [6, 7]],), 3),
    (([[1, 10], [2, 3], [3, 4], [4, 5]],), 3),
]

# hidden: inputs shown, expected OUTPUT hashed. each probes a constraint.
HIDDEN_TESTS = [
    (([],), '5feceb66ffc8'),
    (([[1, 5]],), '6b86b273ff34'),
    (([[1, 10], [2, 9], [3, 8]],), '6b86b273ff34'),
    (([[1, 2], [3, 4], [5, 6], [7, 8]],), '4b227777d4dd'),
    (([[1, 10], [2, 3], [3, 4], [4, 5]],), '4e07408562be'),
    (([[1, 3], [3, 5], [5, 7], [7, 9]],), '4b227777d4dd'),
    (([[5, 6], [1, 2], [3, 4], [7, 8]],), '4b227777d4dd'),
    ((BIG,), 'fc82267b45dc'),
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
        print(f"  {'PASS' if ok else 'FAIL'}  tasks={args[0]!r}  expected={exp}  got={got}")
    print("\nHIDDEN TESTS")
    for i, (args, exph) in enumerate(HIDDEN_TESTS, 1):
        got = solve(*args)
        ok = _h(got) == exph
        sh += ok
        line = f"  Hidden {i}: {'PASS' if ok else 'FAIL'}"
        if not ok and VERBOSE:
            line += f"    (input: tasks={_short(args[0])})"
        print(line)
    print(f"\nSCORE   samples {sp}/{len(SAMPLE_TESTS)}    hidden {sh}/{len(HIDDEN_TESTS)}")

if __name__ == "__main__":
    run()