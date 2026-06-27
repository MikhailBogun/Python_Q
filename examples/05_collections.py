"""The collections module — the senior's toolbox. Stop reinventing these.

Run me:  uv run python learn/examples/05_collections.py
"""

from collections import Counter, defaultdict, deque, namedtuple


def counter_demo() -> None:
    votes = ["a", "b", "a", "c", "a", "b"]
    counts = Counter(votes)
    print("counts        :", counts)
    print("counts['a']   :", counts["a"])
    print("most_common(2):", counts.most_common(2))
    # Counters do arithmetic, too:
    print("a + b sums    :", Counter("aab") + Counter("abc"))


def defaultdict_demo() -> None:
    # Group words by their first letter — no missing-key checks needed.
    words = ["apple", "avocado", "banana", "cherry", "cranberry"]
    groups = defaultdict(list)
    for w in words:
        groups[w[0]].append(w)        # key auto-creates an empty list on first touch
    print("grouped:", dict(groups))

    # Compare to the manual version juniors write:
    manual: dict[str, list[str]] = {}
    for w in words:
        manual.setdefault(w[0], []).append(w)
    print("manual :", manual)


def deque_demo() -> None:
    dq = deque([1, 2, 3])
    dq.append(4)            # O(1) right
    dq.appendleft(0)        # O(1) left  ← a list can't do this cheaply
    print("deque       :", dq)
    print("pop()       :", dq.pop())       # 4
    print("popleft()   :", dq.popleft())   # 0
    print("remaining   :", dq)

    # Bonus: a fixed-size sliding window. Old items fall off the left automatically.
    window = deque(maxlen=3)
    for n in range(6):
        window.append(n)
        print(f"  push {n} -> {list(window)}")


def namedtuple_demo() -> None:
    Color = namedtuple("Color", ["r", "g", "b"])
    orange = Color(255, 165, 0)
    print("orange:", orange, "| .r =", orange.r)


if __name__ == "__main__":
    print("== Counter =="); counter_demo()
    print("\n== defaultdict =="); defaultdict_demo()
    print("\n== deque =="); deque_demo()
    print("\n== namedtuple =="); namedtuple_demo()
