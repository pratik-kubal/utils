"""
===================================================================
WARM-UP                                  Module 1 / fluency rep
-------------------------------------------------------------------
PROBLEM: Compress Runs                                 Difficulty: Easy

Given a string `s` of lowercase letters, return a new string where every
maximal run of the same character is replaced by the character followed
by the length of the run. If a run has length 1, do NOT append the count —
include the character alone.

Example 1:
  Input:  s = "aaabccdddde"
  Output: "a3bc2d4e"
Example 2:
  Input:  s = "abc"
  Output: "abc"
Example 3:
  Input:  s = ""
  Output: ""

Constraints:
  - 0 <= len(s) <= 10**4
  - s contains only lowercase letters (a-z)
  - Length-1 runs: character only, NO count appended.
  - Empty input -> empty output.
===================================================================
"""
import hashlib


# === YOUR SOLUTION =================================================
def solve(s: str) -> str:
    result_array = []
    if len(s) == 0:
        return ""
    prev_char = s[0]
    count = 1
    for curr_char in s[1:]:
        if curr_char == prev_char:
            count += 1
        else:
            if count > 1:
                result_array.append(prev_char + str(count))
            else:
                result_array.append(prev_char)
            prev_char = curr_char
            count = 1
    if count > 1:
        result_array.append(prev_char + str(count))
    else:
        result_array.append(prev_char)
    return "".join(result_array)


# === TEST HARNESS (don't edit below) ===============================
VERBOSE = False   # True -> reveal failing hidden INPUTS (never the expected output)

def _h(r) -> str:
    return hashlib.sha256(repr(r).encode()).hexdigest()[:12]

BIG = "abcde" * 2000

SAMPLE_TESTS = [
    (("aaabccdddde",), "a3bc2d4e"),
    (("abc",), "abc"),
    (("",), ""),
]

HIDDEN_TESTS = [
    (('',), '6f49cdbd80e1'),
    (('a',), 'd749929fe94b'),
    (('aaaaa',), '81be05f08f40'),
    (('aabb',), 'b39bd6a8e97e'),
    (('aabaa',), 'd1d8607b0a1a'),
    (('abcddd',), '29c0bfa15299'),
    (('aaab',), '78c8ced757ec'),
    ((BIG,), 'dee3c493fb63'),
]

def _short(x, n=80):
    s = repr(x)
    return s if len(s) <= n else s[:n] + f"...<len {len(x)}>"

def run():
    sp = sh = 0
    print("SAMPLE TESTS")
    for args, exp in SAMPLE_TESTS:
        got = solve(*args)
        ok = got == exp
        sp += ok
        print(f"  {'PASS' if ok else 'FAIL'}  s={args[0]!r:30}  expected={exp!r:18}  got={got!r}")
    print("\nHIDDEN TESTS")
    for i, (args, exph) in enumerate(HIDDEN_TESTS, 1):
        got = solve(*args)
        ok = _h(got) == exph
        sh += ok
        line = f"  Hidden {i}: {'PASS' if ok else 'FAIL'}"
        if not ok and VERBOSE:
            line += f"    (input: s={_short(args[0])})"
        print(line)
    print(f"\nSCORE   samples {sp}/{len(SAMPLE_TESTS)}    hidden {sh}/{len(HIDDEN_TESTS)}")

if __name__ == "__main__":
    run()