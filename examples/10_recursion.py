"""Recursion — a function that calls itself. The muscle behind tree/graph work.

Every recursion needs two things or it dies:
  1. a BASE CASE   — when to stop (no recursion)
  2. a RECURSIVE CASE — solve a smaller piece, then call yourself

Forget the base case and you get RecursionError (infinite self-calls).

Run me:  uv run python learn/examples/10_recursion.py
"""

import sys
from functools import cache


def factorial(n: int) -> int:
    """n! = n * (n-1)!  — the textbook recursion."""
    if n <= 1:                 # BASE CASE: stop here
        return 1
    return n * factorial(n - 1)   # RECURSIVE CASE: smaller problem


def factorial_traced(n: int, depth: int = 0) -> int:
    """Same thing, but printing so you SEE the call stack grow then unwind."""
    indent = "  " * depth
    print(f"{indent}-> factorial({n})")
    if n <= 1:
        print(f"{indent}   base case, return 1")
        return 1
    result = n * factorial_traced(n - 1, depth + 1)
    print(f"{indent}<- factorial({n}) = {result}")
    return result


def fib_naive(n: int) -> int:
    """Naive Fibonacci. CORRECT but a performance TRAP: it recomputes the same
    values exponentially many times. fib_naive(35) already feels slow."""
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


@cache  # functools.cache memoizes results -> each n computed ONCE. O(2^n) -> O(n).
def fib_fast(n: int) -> int:
    if n < 2:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)


def sum_nested(data) -> int:
    """Where recursion SHINES: arbitrarily nested data. Try writing this with a
    plain loop and you'll feel the pain — recursion mirrors the shape of the data."""
    total = 0
    for item in data:
        if isinstance(item, list):
            total += sum_nested(item)     # recurse into the sub-list
        else:
            total += item
    return total


def countdown_iterative(n: int) -> list[int]:
    """Most recursion can be rewritten as a loop. Loops have no depth limit and
    are often clearer for simple linear cases — don't recurse just to look clever."""
    return list(range(n, 0, -1))


if __name__ == "__main__":
    print("== factorial =="); print("5! =", factorial(5))

    print("\n== watch the call stack (grow then unwind) ==")
    factorial_traced(4)

    print("\n== fibonacci: naive vs memoized ==")
    import time
    t0 = time.perf_counter(); fib_naive(30); naive_t = time.perf_counter() - t0
    t0 = time.perf_counter(); fib_fast(30); fast_t = time.perf_counter() - t0
    print(f"fib_naive(30): {naive_t:.4f}s")
    print(f"fib_fast(30) : {fast_t:.6f}s  (memoized with @cache)")
    print("fib_fast(100):", fib_fast(100), "  <- naive would never finish this")

    print("\n== recursion fits nested data ==")
    print("sum of [1, [2, 3, [4, 5]], 6] =", sum_nested([1, [2, 3, [4, 5]], 6]))

    print("\n== Python's recursion limit ==")
    print("default limit:", sys.getrecursionlimit(),
          "(~that many nested calls before RecursionError)")
    print("iterative countdown(5):", countdown_iterative(5))
