"""tuple — the immutable, hashable record.

Run me:  uv run python learn/examples/02_tuple.py
"""

from typing import NamedTuple


def immutability() -> None:
    point = (3, 4)
    print("point:", point)
    try:
        point[0] = 99           # tuples can't be changed
    except TypeError as e:
        print("can't mutate a tuple ->", e)


def unpacking() -> None:
    point = (3, 4)
    x, y = point                # tuple unpacking — used constantly in Python
    print("x =", x, "| y =", y)

    # swap without a temp variable (this is tuple packing/unpacking under the hood)
    a, b = 1, 2
    a, b = b, a
    print("after swap: a =", a, "| b =", b)

    # star-unpacking grabs "the rest"
    first, *middle, last = (1, 2, 3, 4, 5)
    print("first:", first, "| middle:", middle, "| last:", last)


def hashability() -> None:
    # A tuple of hashable things can be a dict key — a list cannot.
    grid = {(0, 0): "origin", (1, 2): "treasure"}
    print("grid[(1, 2)] =", grid[(1, 2)])
    try:
        broken = {[0, 0]: "nope"}   # list is unhashable
    except TypeError as e:
        print("list as key ->", e)


def the_one_element_gotcha() -> None:
    not_a_tuple = (5)       # just the int 5 — parentheses alone do nothing
    real_tuple = (5,)       # the COMMA makes the tuple
    print("(5)  is a", type(not_a_tuple).__name__)
    print("(5,) is a", type(real_tuple).__name__)


def named_tuples() -> None:
    """Bare tuples are cryptic; NamedTuple gives you readable field access."""
    class Point(NamedTuple):
        x: int
        y: int

    p = Point(3, 4)
    print("p.x =", p.x, "| p.y =", p.y)   # readable!
    print("still unpacks:", (lambda a, b: f"{a},{b}")(*p))
    print("still a tuple:", isinstance(p, tuple))


if __name__ == "__main__":
    print("== immutability =="); immutability()
    print("\n== unpacking =="); unpacking()
    print("\n== hashability =="); hashability()
    print("\n== one-element gotcha =="); the_one_element_gotcha()
    print("\n== named tuples =="); named_tuples()
