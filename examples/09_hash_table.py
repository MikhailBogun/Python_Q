"""Hash table — what's actually UNDER dict and set.

You already used dict/set. Now see the machine inside, so 'O(1) average' and
'keys must be hashable' stop being magic words and become things you understand.

Run me:  uv run python learn/examples/09_hash_table.py
"""


def what_is_a_hash() -> None:
    """hash() turns an object into an int. That int picks a storage slot."""
    print("hash('apple') :", hash("apple"))
    print("hash(42)      :", hash(42))
    print("hash((1, 2))  :", hash((1, 2)))      # tuples are hashable
    print("same value -> same hash:", hash("apple") == hash("apple"))
    try:
        hash([1, 2])                            # lists are NOT hashable
    except TypeError as e:
        print("hash([1, 2])  ->", e)
    # WHY: a list can change. If its hash changed after you stored it, the table
    # would look in the wrong slot and 'lose' your value. Immutable = safe key.


def the_core_idea() -> None:
    """slot = hash(key) % number_of_buckets. That's the whole trick."""
    buckets = 8
    for key in ["alice", "bob", "carol", "dave"]:
        slot = hash(key) % buckets
        print(f"  {key:6} -> hash % {buckets} = slot {slot}")
    # Because we jump straight to a computed slot instead of scanning, lookup is
    # O(1) on average — it doesn't matter how many items are stored.


# ---------------------------------------------------------------------------
# A toy hash table built from scratch, using "separate chaining" for collisions
# (each bucket holds a list of (key, value) pairs). This is roughly how dict
# works conceptually — real CPython is far more optimized, but the idea is this.
# ---------------------------------------------------------------------------
class HashTable:
    def __init__(self, num_buckets: int = 8) -> None:
        self._buckets: list[list[tuple]] = [[] for _ in range(num_buckets)]
        self._size = 0

    def _slot(self, key) -> int:
        return hash(key) % len(self._buckets)

    def put(self, key, value) -> None:
        bucket = self._buckets[self._slot(key)]
        for i, (k, _) in enumerate(bucket):
            if k == key:                 # key exists -> overwrite
                bucket[i] = (key, value)
                return
        bucket.append((key, value))      # collision? just append to this bucket
        self._size += 1

    def get(self, key):
        bucket = self._buckets[self._slot(key)]
        for k, v in bucket:              # scan ONLY this bucket, not everything
            if k == key:
                return v
        raise KeyError(key)

    def show(self) -> None:
        for i, bucket in enumerate(self._buckets):
            if bucket:
                print(f"  bucket {i}: {bucket}")


def toy_table_demo() -> None:
    table = HashTable(num_buckets=4)     # small on purpose -> forces collisions
    for name, age in [("ada", 36), ("linus", 54), ("grace", 85), ("guido", 68)]:
        table.put(name, age)
    print("internal layout (some buckets hold >1 pair = collisions):")
    table.show()
    print("get('grace') ->", table.get("grace"))
    table.put("ada", 37)                 # overwrite, not duplicate
    print("after update, get('ada') ->", table.get("ada"))
    # KEY INSIGHT: collisions degrade O(1) toward O(n) if a bucket gets long.
    # Real dicts keep buckets short by RESIZING (growing the array) when the
    # 'load factor' (items / buckets) gets too high. That's why dict stays fast.


if __name__ == "__main__":
    print("== what is a hash? =="); what_is_a_hash()
    print("\n== the core idea =="); the_core_idea()
    print("\n== a hash table from scratch =="); toy_table_demo()
