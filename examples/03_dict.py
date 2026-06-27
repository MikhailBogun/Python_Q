"""dict — the hash map that runs the world. O(1) lookup by key.

Run me:  uv run python learn/examples/03_dict.py
"""


def basics() -> None:
    user = {"name": "Ada", "age": 36}
    print("name:", user["name"])           # O(1) — but KeyError if missing
    print("email:", user.get("email"))     # None — safe
    print("email:", user.get("email", "n/a"))  # with a default

    user["email"] = "ada@compute.io"        # insert/update — O(1)
    print("has 'age'?", "age" in user)      # key membership — O(1)
    del user["age"]
    print("final:", user)


def iterating() -> None:
    user = {"name": "Ada", "age": 36, "role": "engineer"}
    print("keys  :", list(user))               # iterating a dict yields keys
    print("values:", list(user.values()))
    for key, value in user.items():            # the one you'll use most
        print(f"  {key} = {value}")


def comprehension() -> None:
    squares = {n: n * n for n in range(5)}
    print("squares:", squares)
    # invert a dict (swap keys and values)
    inverted = {v: k for k, v in squares.items()}
    print("inverted:", inverted)


def counting_patterns() -> None:
    words = ["apple", "banana", "apple", "cherry", "banana", "apple"]

    # Junior version — verbose:
    counts = {}
    for w in words:
        if w not in counts:
            counts[w] = 0
        counts[w] += 1
    print("manual    :", counts)

    # Cleaner with setdefault:
    counts2: dict[str, int] = {}
    for w in words:
        counts2[w] = counts2.get(w, 0) + 1
    print("with .get :", counts2)

    # Best — Counter (see 05_collections.py):
    from collections import Counter
    print("Counter   :", dict(Counter(words)))


def merging() -> None:
    defaults = {"theme": "dark", "lang": "en"}
    overrides = {"lang": "ru"}
    merged = defaults | overrides           # 3.9+: right side wins on conflicts
    print("merged:", merged)


if __name__ == "__main__":
    print("== basics =="); basics()
    print("\n== iterating =="); iterating()
    print("\n== comprehension =="); comprehension()
    print("\n== counting patterns =="); counting_patterns()
    print("\n== merging =="); merging()
