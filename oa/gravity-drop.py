"""
===================================================================
MODULE 3                                Technique: grid simulation
-------------------------------------------------------------------
PROBLEM: Gravity Drop                          Difficulty: Medium-Hard

You're given a 2D grid of characters where each cell is either '.'
(empty) or '#' (a solid block). Simulate gravity: every block falls
straight down within its column until it lands on either the bottom
of the grid or on top of another block. Return the resulting grid
as a list of strings (one string per row).

Example 1:
  Input:  grid = [".#.", "...", "#..", ".#.", "..."]
  Output: ["...", "...", "...", ".#.", "##."]
Example 2:
  Input:  grid = ["..#", "##.", ".#."]
  Output: ["...", ".#.", "###"]

Constraints:
  - 1 <= rows, cols <= 1000
  - Each cell is either '.' or '#'
  - Return a list of strings with the same dimensions as input.
  - Strings in Python are immutable.
===================================================================
"""
from typing import List
import hashlib


# === YOUR SOLUTION =================================================
def solve(grid: List[str]) -> List[str]:
    n, m = len(grid), len(grid[0])
    col_counts = [ 0 for _ in range(m)]
    imm = [ [ "" for _ in range(m)] for _ in range(n)]
    result = []
    for _row in range(n):
        for col, char in enumerate(grid[_row]):
            if char == '#':
                col_counts[col] += 1
    for row in range(n):
        for col in range(m):
            if col_counts[col] <= n - row and col_counts[col] > 0:
                # Fill
                imm[n - row - 1][col] = "#"
                # Decrease the count
                col_counts[col] -= 1
            else:
                imm[n - row - 1][col] = "."
    # Fix result
    for row in range(n):
        result.append("".join(imm[row]))
    return result


# === TEST HARNESS (don't edit below) ===============================
VERBOSE = False   # True -> reveal failing hidden INPUTS (never expected outputs)

def _h(r) -> str:
    return hashlib.sha256(repr(r).encode()).hexdigest()[:12]

BIG_ROWS = 1000
BIG = ['#' * BIG_ROWS if r % 2 else '.' * BIG_ROWS for r in range(BIG_ROWS)]

SAMPLE_TESTS = [
    (([".#.", "...", "#..", ".#.", "..."],),
        ["...", "...", "...", ".#.", "##."]),
    ((["..#", "##.", ".#."],),
        ["...", ".#.", "###"]),
]

HIDDEN_TESTS = [
    ((['#'],), 'd14e8dfbbb62'),
    ((['.'],), '5cf88a341b5a'),
    ((['...'],), '46ed8ab2ced6'),
    ((['###', '...'],), '0b3ffd181a9c'),
    ((['#', '#', '.'],), '11d67ca05e72'),
    ((['##', '##'],), '47231efa9dd7'),
    ((['....', '....', '....'],), 'df2782c2300c'),
    ((BIG,), 'd9c388a46243'),
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
        print(f"  {'PASS' if ok else 'FAIL'}  grid={args[0]!r}")
        print(f"      expected={exp}")
        print(f"      got     ={got}")
    print("\nHIDDEN TESTS")
    for i, (args, exph) in enumerate(HIDDEN_TESTS, 1):
        got = solve(*args)
        ok = _h(got) == exph
        sh += ok
        line = f"  Hidden {i}: {'PASS' if ok else 'FAIL'}"
        if not ok and VERBOSE:
            line += f"    (input: grid={_short(args[0])})"
        print(line)
    print(f"\nSCORE   samples {sp}/{len(SAMPLE_TESTS)}    hidden {sh}/{len(HIDDEN_TESTS)}")

if __name__ == "__main__":
    run()