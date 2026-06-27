"""list — your default ordered, mutable, growable workhorse.

Run me:  uv run python learn/examples/01_list.py
Then change values, predict the output, and re-run.
"""


def basics() -> None:
    fruits = ["apple", "banana", "cherry"]

    # Adding
    fruits.append("date")          # add one to the end          — O(1)
    fruits.extend(["fig", "kiwi"]) # add many to the end         — O(k)
    fruits.insert(0, "avocado")    # insert at index 0           — O(n), shifts all
    print("after adds:", fruits)

    # Accessing
    print("first:", fruits[0])
    print("last :", fruits[-1])    # negative indexes count from the end
    print("slice:", fruits[1:3])   # [start:stop), stop is exclusive

    # Removing
    fruits.pop()                   # remove & return last        — O(1)
    fruits.pop(0)                  # remove & return at index 0  — O(n)
    fruits.remove("banana")        # remove first matching value — O(n)
    print("after removes:", fruits)


def slicing() -> None:
    nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    print("nums[2:5] :", nums[2:5])    # [2, 3, 4]
    print("nums[::2] :", nums[::2])    # every 2nd: [0, 2, 4, 6, 8]
    print("nums[::-1]:", nums[::-1])   # reversed (a NEW list)
    print("nums[-3:] :", nums[-3:])    # last three


def comprehensions() -> None:
    squares = [x * x for x in range(6)]
    evens = [x for x in range(10) if x % 2 == 0]
    pairs = [(x, y) for x in range(2) for y in range(2)]
    print("squares:", squares)
    print("evens  :", evens)
    print("pairs  :", pairs)


def the_on2_trap() -> None:
    """Why 'x in list' inside a loop is the classic performance bug."""
    haystack = list(range(10_000))
    needles = [9999, 5000, 0]
    # Each `n in haystack` scans up to 10k items — O(n) per check.
    # Inside a loop, that's O(n*m). For big data this is your bottleneck.
    found = [n for n in needles if n in haystack]   # works, but O(n*m)
    print("found (list scan):", found)

    # The fix: a set gives O(1) membership.
    fast = set(haystack)
    found_fast = [n for n in needles if n in fast]  # O(m)
    print("found (set lookup):", found_fast)


if __name__ == "__main__":
    print("== basics =="); basics()
    print("\n== slicing =="); slicing()
    print("\n== comprehensions =="); comprehensions()
    print("\n== the O(n^2) trap =="); the_on2_trap()
