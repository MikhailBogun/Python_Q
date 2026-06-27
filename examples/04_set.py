"""set — unique, unordered, O(1) membership.

Run me:  uv run python learn/examples/04_set.py
"""


def basics() -> None:
    seen = {1, 2, 3}
    seen.add(4)             # O(1)
    seen.add(2)             # no-op, already present (sets are unique)
    print("set:", seen)
    print("3 in seen?", 3 in seen)      # O(1) membership — the killer feature
    seen.discard(99)        # safe even if absent (remove() would raise)
    print("after discard:", seen)


def deduplication() -> None:
    raw = [1, 1, 2, 3, 3, 3, 4]
    unique = set(raw)
    print("unique values:", unique)
    # Need to keep order? dict.fromkeys preserves insertion order:
    unique_ordered = list(dict.fromkeys(raw))
    print("unique, order kept:", unique_ordered)


def set_algebra() -> None:
    a = {1, 2, 3, 4}
    b = {3, 4, 5, 6}
    print("a & b (intersection — in both)      :", a & b)
    print("a | b (union — in either)           :", a | b)
    print("a - b (difference — in a not b)     :", a - b)
    print("a ^ b (symmetric — in exactly one)  :", a ^ b)
    print("a <= b (is a a subset of b)?        :", a <= b)


def real_world() -> None:
    """'Which users are in group A but not group B?' — one readable line."""
    group_a = {"ada", "linus", "grace", "dennis"}
    group_b = {"grace", "dennis", "guido"}
    only_a = group_a - group_b
    in_both = group_a & group_b
    print("only in A:", only_a)
    print("in both  :", in_both)


def frozenset_demo() -> None:
    # frozenset is the immutable, hashable set — usable as a dict key / set member.
    regions = {frozenset({"us", "ca"}): "north-america",
               frozenset({"de", "fr"}): "europe"}
    print(regions[frozenset({"ca", "us"})])   # order doesn't matter for sets


if __name__ == "__main__":
    print("== basics =="); basics()
    print("\n== deduplication =="); deduplication()
    print("\n== set algebra =="); set_algebra()
    print("\n== real world =="); real_world()
    print("\n== frozenset =="); frozenset_demo()
