"""'Array' has three meanings in Python: list, array.array, numpy.ndarray.

Run me:  uv run python learn/examples/08_array.py
"""

from array import array


def meaning_1_list() -> None:
    """99% of the time, 'array' in Python means a plain list."""
    data = [1, "two", 3.0, [4]]      # can hold mixed types, grows freely
    print("a list holds anything:", data)


def meaning_2_array_array() -> None:
    """array.array — a compact, TYPED numeric array. Saves memory, niche."""
    a = array("i", [1, 2, 3, 4])     # "i" = signed int; ALL elements must be ints
    a.append(5)
    print("array.array:", a)
    print("typecode   :", a.typecode, "| itemsize bytes:", a.itemsize)
    try:
        a.append("oops")             # type-enforced, unlike a list
    except TypeError as e:
        print("type-enforced ->", e)


def meaning_3_numpy() -> None:
    """numpy.ndarray — the real 'array' for numeric work. Vectorized & fast."""
    try:
        import numpy as np
    except ImportError:
        print("numpy not installed — `uv add numpy` to try this part.")
        print("Conceptually: np.array([1,2,3]) * 2 == array([2, 4, 6])")
        print("It operates on the whole array at once, with no Python loop.")
        return

    v = np.array([1, 2, 3, 4])
    print("v          :", v)
    print("v * 2      :", v * 2)         # whole-array math, no loop
    print("v + v      :", v + v)
    print("v.mean()   :", v.mean())
    m = np.array([[1, 2], [3, 4]])       # multidimensional
    print("matrix sum :", m.sum(axis=0))  # column sums: [4 6]


if __name__ == "__main__":
    print("== meaning 1: list =="); meaning_1_list()
    print("\n== meaning 2: array.array =="); meaning_2_array_array()
    print("\n== meaning 3: numpy =="); meaning_3_numpy()
