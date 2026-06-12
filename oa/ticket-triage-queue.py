"""
===================================================================
PROBLEM: Support Ticket Triage Queue              Difficulty: Medium-Hard

You run a support desk. You're given a list of open tickets, each a tuple:

    (ticket_id, severity, age_hours, customer_tier)

Return the ticket_ids ordered from MOST urgent to LEAST urgent, by this
priority order:

  1. Higher severity first.
  2. Among equal severity, higher-priority customer tier first, where
         enterprise  >  pro  >  free.
  3. Among those still tied, older tickets first (greater age_hours).
  4. Among those still tied, smaller ticket_id first (lexicographic ascending).

Return a list of ticket_ids in triage order.

Example 1:
  Input: [("T3",2,10,"free"), ("T1",5,3,"pro"),
          ("T2",5,3,"enterprise"), ("T4",2,20,"pro")]
  Output: ["T2", "T1", "T4", "T3"]

Example 2:
  Input: [("B",3,5,"free"), ("A",3,5,"pro"), ("C",3,8,"free")]
  Output: ["A", "C", "B"]

Constraints:
  - 0 <= len(tickets) <= 10^5
  - severity is an integer in [1, 5]; higher is more urgent.
  - age_hours is an integer >= 0.
  - customer_tier is exactly one of "enterprise", "pro", "free".
  - ticket_ids are unique strings.
  - Return [] for an empty input.

Output format: a list of ticket_id strings, order significant.
===================================================================
"""
from typing import List, Tuple
import hashlib


# === YOUR SOLUTION =================================================
def solve(tickets: List[Tuple[str, int, int, str]]) -> List[str]:
    if len(tickets) == 0:
        return []
    sev_dict = {
        "enterprise":0,
        "pro": 1,
        "free": 2
    }
    return_list = sorted(tickets, key=lambda x: (-x[1], sev_dict[x[3]], -x[2], x[0]))
    output = []
    for ticket_id,_,_,_ in return_list:
        output.append(ticket_id)
    return output


# === TEST HARNESS (don't edit below) ===============================
VERBOSE = False   # True -> reveal failing hidden INPUTS (never expected outputs)

def _h(r) -> str:
    return hashlib.sha256(repr(r).encode()).hexdigest()[:12]

# visible (the problem examples): (args_tuple, expected)
SAMPLE_TESTS = [
    (([("T3",2,10,"free"),("T1",5,3,"pro"),("T2",5,3,"enterprise"),("T4",2,20,"pro")],), ["T2","T1","T4","T3"]),
    (([("B",3,5,"free"),("A",3,5,"pro"),("C",3,8,"free")],), ["A","C","B"]),
]

# hidden: inputs shown, expected OUTPUT hashed. each probes a constraint.
HIDDEN_TESTS = [
    (([],), '4f53cda18c2b'),                                                                        # empty boundary
    (([('solo', 3, 7, 'pro')],), '0265944d499e'),                                                   # single element
    (([('X', 3, 5, 'free'), ('Y', 3, 5, 'pro')],), '696621d906c3'),                                 # tier custom-rank, NOT alphabetical
    (([('A', 1, 0, 'free'), ('B', 5, 0, 'free')],), 'b963ecafb2b3'),                                # severity descending
    (([('A', 3, 5, 'pro'), ('B', 3, 20, 'pro')],), 'b963ecafb2b3'),                                 # age descending (older first)
    (([('zebra', 3, 5, 'pro'), ('apple', 3, 5, 'pro')],), '3f0216502468'),                          # id ascending (input order reversed)
    (([('t5', 4, 2, 'free'), ('t1', 4, 2, 'enterprise'), ('t2', 4, 10, 'free'), ('t3', 5, 1, 'pro'), ('t4', 4, 2, 'free')],), 'e670d8a59e82'),  # full integration
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
        print(f"  {'PASS' if ok else 'FAIL'}  args={args!r}  expected={exp}  got={got}")
    print("\nHIDDEN TESTS")
    for i, (args, exph) in enumerate(HIDDEN_TESTS, 1):
        got = solve(*args)
        ok = _h(got) == exph
        sh += ok
        line = f"  Hidden {i}: {'PASS' if ok else 'FAIL'}"
        if not ok and VERBOSE:
            line += f"    (input: {_short(args)})"
        print(line)
    print(f"\nSCORE   samples {sp}/{len(SAMPLE_TESTS)}    hidden {sh}/{len(HIDDEN_TESTS)}")

if __name__ == "__main__":
    run()