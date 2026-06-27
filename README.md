# Python Data Structures — From Junior to Middle+

Hey. Sit down, grab a coffee. We're going to go through the data structures you'll actually
use every single day as a Python engineer. Not the textbook way — the way that gets you
through code reviews, design discussions, and interviews without flinching.

Here's the deal I'm offering you: I won't just tell you *what* a list is. Any tutorial does
that. I'll tell you **when to reach for it, what it costs, and how it bites people.** That
last part — knowing the cost and the trap — is most of what separates a middle engineer from
a junior. A junior makes it work. A middle engineer makes it work *and* can defend the choice.

> **How to read this:** Each section has runnable code in the `examples/` folder. Don't just
> read — run them, break them, change them. Run a file with:
> ```bash
> uv run python learn/examples/01_list.py
> ```

---

## The mental model you need first

Before any specific structure, internalize four ideas. Everything else hangs off these.

### 1. Mutable vs. immutable
Can the object change after creation?
- **Mutable:** `list`, `dict`, `set`, `bytearray` — you can modify them in place.
- **Immutable:** `tuple`, `str`, `int`, `float`, `frozenset`, `bytes` — any "change" creates a
  *new* object.

This isn't trivia. It decides whether something can be a dict key, whether passing it to a
function can surprise you, and whether two variables secretly share state.

### 2. Identity vs. equality
- `==` asks "do these have the same *value*?"
- `is` asks "are these literally the *same object* in memory?"

Use `==` for values, `is` only for singletons (`None`, `True`, `False`). Writing
`if x is "hello"` is a junior tell and may break depending on string interning.

### 3. Hashability
A "hashable" object has a stable `__hash__()` and can live in a `set` or be a `dict` key.
Rule of thumb: **immutable = hashable, mutable = not.** That's why you can't use a list as a
dict key but you can use a tuple.

### 4. Big-O — the cost label on every operation
You don't need a CS degree, but you must know roughly how expensive an operation is as data
grows. The three you'll meet constantly:
- **O(1)** — constant. Doesn't care how big the collection is. (dict lookup, list append)
- **O(n)** — linear. Twice the data, twice the work. (scanning a list, `x in some_list`)
- **O(n²)** — quadratic. The thing that makes your code "mysteriously slow" in production.
  (usually a loop inside a loop, or `x in list` *inside* a loop)

Keep these in your head. We'll attach them to every structure below.

---

## The Big Four (built-in, you'll use these hourly)

| Structure | Syntax        | Ordered | Mutable | Duplicates | Lookup by    | Hashable |
|-----------|---------------|---------|---------|------------|--------------|----------|
| `list`    | `[1, 2, 3]`   | Yes     | Yes     | Yes        | index / scan | No       |
| `tuple`   | `(1, 2, 3)`   | Yes     | No      | Yes        | index / scan | Yes\*    |
| `dict`    | `{"a": 1}`    | Yes\*\* | Yes     | keys: no   | key          | No       |
| `set`     | `{1, 2, 3}`   | No      | Yes     | No         | membership   | No       |

\* A tuple is hashable only if *everything inside it* is hashable.
\*\* Dicts preserve **insertion order** since Python 3.7. This is a language guarantee, not luck.

---

## 1. `list` — your default workhorse

A growable, ordered, mutable sequence. When you don't know what to use, you probably want a
list. It's backed by a dynamic array (a contiguous block of pointers that resizes itself).

```python
fruits = ["apple", "banana", "cherry"]
fruits.append("date")        # add to end       — O(1) amortized
fruits[0]                    # index access     — O(1)
fruits.insert(0, "kiwi")     # insert at front  — O(n)  ← shifts everything
"banana" in fruits           # membership test  — O(n)  ← scans the whole thing
fruits.pop()                 # remove from end   — O(1)
fruits.pop(0)                # remove from front — O(n)  ← shifts everything
```

**The thing juniors get wrong:** using `list` for membership tests in a hot loop.
`if user in users_list` is O(n). Do that inside a loop over n items and you've built an O(n²)
machine without noticing. If you're checking membership repeatedly, **use a `set`.**

**Slicing** — learn it cold, it's everywhere:
```python
nums = [0, 1, 2, 3, 4, 5]
nums[1:4]     # [1, 2, 3]   — start:stop (stop is exclusive)
nums[::2]     # [0, 2, 4]   — every 2nd element
nums[::-1]    # [5, 4, 3..] — reversed (a copy, not in place)
nums[-1]      # 5           — last element
```

**List comprehensions** — the single most "Pythonic" thing. Master them:
```python
squares = [x * x for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]
matrix  = [[row * col for col in range(3)] for row in range(3)]
```
A comprehension is faster and clearer than `for ... append()`. But if it stops fitting on one
readable line or needs branching logic, write the explicit loop — readability wins.

➡️ Run `examples/01_list.py`

---

## 2. `tuple` — the immutable record

Same as a list but **frozen**. You cannot add, remove, or reassign elements. Why would you
want a *worse* list? Because immutability is a feature:

1. **It signals intent.** A tuple says "this is a fixed group of things that belong together"
   — like coordinates `(x, y)` or an RGB color `(255, 128, 0)`. A list says "a collection that
   will grow and shrink."
2. **It's hashable**, so it can be a dict key or set member.
3. **It's safer** — nobody can mutate it out from under you.

```python
point = (3, 4)
x, y = point          # tuple unpacking — you'll use this constantly
print(x, y)           # 3 4

# A tuple as a dict key — impossible with a list:
grid = {(0, 0): "origin", (1, 2): "treasure"}

# The famous one-element tuple gotcha:
not_a_tuple = (5)     # this is just the int 5!
real_tuple  = (5,)    # the comma makes the tuple, not the parentheses
```

**`NamedTuple` — the upgrade that makes you look senior.** Bare tuples are cryptic:
`person[0]` — what's index 0? Use a named tuple and access fields by name:
```python
from typing import NamedTuple

class Point(NamedTuple):
    x: int
    y: int

p = Point(3, 4)
p.x            # 3  — readable!
p.y            # 4
# Still a real tuple: immutable, unpackable, hashable. Best of both worlds.
```
For mutable structured data, reach for `@dataclass` instead — same readability, but mutable.

➡️ Run `examples/02_tuple.py`

---

## 3. `dict` — the structure that runs the world

A hash map: key → value, with **O(1) average** lookup, insert, and delete. If lists are your
workhorse, dicts are your superpower. A huge fraction of "make it fast" is really "replace a
list scan with a dict lookup."

```python
user = {"name": "Ada", "age": 36}
user["name"]                 # "Ada"     — O(1)
user.get("email")            # None      — safe, no KeyError
user.get("email", "n/a")     # "n/a"     — with a default
user["email"] = "a@b.io"     # insert    — O(1)
"age" in user                # True      — O(1) key membership
del user["age"]              # remove    — O(1)
```

**`.get()` vs `[]`** — `user["missing"]` raises `KeyError`; `user.get("missing")` returns
`None`. Use `[]` when a missing key is genuinely a bug you want to hear about; use `.get()`
when absence is normal.

**Iterating — know all three:**
```python
for key in user:                  # keys (default)
    ...
for value in user.values():       # values
    ...
for key, value in user.items():   # both — this is the one you'll use most
    ...
```

**Dict comprehensions** work just like list ones:
```python
squares = {n: n * n for n in range(5)}      # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}
```

**The classic pattern — counting/grouping.** A junior writes:
```python
counts = {}
for word in words:
    if word not in counts:
        counts[word] = 0
    counts[word] += 1
```
A middle engineer writes `collections.Counter(words)` (see below) or
`counts.setdefault(word, 0)`. Know that these exist.

➡️ Run `examples/03_dict.py`

---

## 4. `set` — membership and uniqueness, fast

An unordered collection of **unique, hashable** elements. Two killer use cases:

1. **Deduplication:** `unique = set(my_list)` — done.
2. **Fast membership:** `x in my_set` is **O(1)**, vs O(n) for a list. This is the fix for the
   O(n²) trap I mentioned under lists.

```python
seen = {1, 2, 3}
seen.add(4)            # O(1)
seen.add(2)            # no-op, already there
3 in seen              # True — O(1)
seen.remove(99)        # KeyError if absent
seen.discard(99)       # safe, no error if absent
```

**Set algebra — gorgeous for comparing collections:**
```python
a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
a & b     # {3, 4}        intersection — in both
a | b     # {1,2,3,4,5,6} union        — in either
a - b     # {1, 2}        difference   — in a but not b
a ^ b     # {1, 2, 5, 6}  symmetric    — in exactly one
```
"Which users are in group A but not group B?" → `set_a - set_b`. One line, O(n), reads like the
sentence you'd say out loud.

`frozenset` is the immutable, hashable version — use it when you need a set *inside* another set
or as a dict key.

➡️ Run `examples/04_set.py`

---

## Under the hood: how a hash table actually works

Here's a thing that separates people who *use* `dict`/`set` from people who *understand* them:
both are **hash tables**, and knowing the machine inside explains every rule you've been told to
just memorize. If you can explain this in an interview, you're past junior.

**The core trick.** A hash table is an array of "buckets." To store a key, it computes
`hash(key) % number_of_buckets` to pick a slot, and drops the value there. To look it up, it
runs the *same* calculation and jumps straight to that slot. No scanning — that's why lookup is
**O(1) on average**. It doesn't matter whether there are 10 items or 10 million.

```python
buckets = 8
hash("alice") % buckets    # -> some slot, e.g. 3 — we jump straight there
```

**Why keys must be hashable (= immutable).** The slot is derived from the key's hash. If the key
could change after you stored it, its hash would change, and the table would compute a *different*
slot on lookup — it would lose your value. That's the whole reason a `list` can't be a dict key
but a `tuple` can. Now "keys must be hashable" isn't a rule to memorize; it's an obvious
consequence.

**Collisions.** Two different keys can land in the same slot (`hash(a) % n == hash(b) % n`). The
table handles this — CPython probes for another open slot; the classic teaching version keeps a
little list per bucket ("separate chaining"). Either way, a lookup that collides has to check a
few candidates, so a *bad* hash spread degrades O(1) toward O(n).

**Load factor & resizing.** To keep buckets short and stay fast, the table watches its **load
factor** (items ÷ buckets). When it gets too full, it **resizes** — allocates a bigger array and
re-inserts everything. That occasional resize is why we say append/insert is O(1) *amortized*:
almost always cheap, rarely expensive, cheap *on average*.

The example builds a working hash table from scratch (with visible collisions) so you can watch
all of this happen. That's the best way to make it stick.

➡️ Run `examples/09_hash_table.py`

---

## The `collections` module — the senior's toolbox

The built-ins cover 90% of cases. The standard-library `collections` module covers most of the
rest, and *knowing it exists* is a real seniority marker. Stop reinventing these.

### `Counter` — counting done right
```python
from collections import Counter

votes = ["a", "b", "a", "c", "a", "b"]
counts = Counter(votes)          # Counter({'a': 3, 'b': 2, 'c': 1})
counts["a"]                      # 3
counts.most_common(2)            # [('a', 3), ('b', 2)]
```

### `defaultdict` — no more "is the key there yet?"
```python
from collections import defaultdict

groups = defaultdict(list)       # missing keys auto-create an empty list
groups["fruits"].append("apple") # no KeyError, no setdefault dance
# groups == {"fruits": ["apple"]}
```

### `deque` — a *real* queue (this is your stack/queue answer)
A list is O(n) to pop from the front. A `deque` ("deck") is O(1) at **both** ends. This is the
right tool for queues and for sliding windows.
```python
from collections import deque

dq = deque([1, 2, 3])
dq.append(4)          # add right   — O(1)
dq.appendleft(0)      # add left    — O(1)
dq.pop()              # remove right — O(1)
dq.popleft()          # remove left  — O(1)  ← list can't do this cheaply
```

### `OrderedDict` and `namedtuple`
`namedtuple` is the functional cousin of the `NamedTuple` class shown earlier. `OrderedDict`
mattered a lot before 3.7; now regular dicts keep order, so you'll rarely need it (its remaining
edge: order-sensitive equality and `move_to_end`).

➡️ Run `examples/05_collections.py`

---

## 5. Stack — Last In, First Out (LIFO)

A stack isn't a separate type — it's a *usage pattern*. Think a stack of plates: you add and
remove from the **top**. Last thing in is the first thing out. Used for: undo history, browser
back button, function call stacks, expression parsing, depth-first traversal.

**Just use a `list`.** Append and pop from the end — both O(1):
```python
stack = []
stack.append("page1")    # push
stack.append("page2")    # push
top = stack.pop()        # pop → "page2" (last in, first out)
```
That's it. Don't overthink it. `append` = push, `pop` = pop. A list *is* a perfectly good stack.

➡️ Run `examples/06_stack.py`

---

## 6. Queue — First In, First Out (FIFO)

The opposite pattern: a line at a coffee shop. First person in line is served first. Used for:
task/job queues, breadth-first traversal, buffering, scheduling.

**Do NOT use a plain list for this.** `list.pop(0)` removes from the front and is **O(n)** —
it shifts every remaining element down. Use a `deque`:
```python
from collections import deque

queue = deque()
queue.append("task1")     # enqueue (add to back)
queue.append("task2")
first = queue.popleft()   # dequeue (remove from front) → "task1" — O(1)
```
This — knowing to use `deque` instead of `list.pop(0)` for a queue — is a textbook
middle-engineer signal. Juniors reach for `list.pop(0)` and ship an accidental O(n²).

**For threads/async or multiprocessing**, there are purpose-built thread-safe queues:
`queue.Queue` (threads) and `asyncio.Queue` (async). Different tool, same idea — reach for them
when you have producers and consumers on different threads, not for plain single-threaded FIFO.

➡️ Run `examples/07_queue.py`

---

## 7. "Array" — a word with three meanings in Python

This trips people up because "array" means different things depending on who's talking:

1. **The `list`** — when most people say "array" in Python, they mean a list. 99% of the time,
   this is what you want. It can hold mixed types and grows freely.

2. **`array.array`** — a built-in, *typed*, compact numeric array. Stores raw machine values
   (e.g. all 32-bit ints) instead of Python objects, so it uses far less memory. Niche — you'd
   use it for large homogeneous numeric data when memory matters but you don't want NumPy.
   ```python
   from array import array
   a = array("i", [1, 2, 3])   # "i" = signed int; all elements must be ints
   ```

3. **`numpy.ndarray`** — the real "array" for any numeric/scientific work: vectorized math,
   multidimensional, blazing fast (it's C under the hood). Not in the standard library, but the
   foundation of the entire data/ML ecosystem. If you're doing math on lots of numbers, you want
   NumPy, not a list.
   ```python
   import numpy as np
   v = np.array([1, 2, 3])
   v * 2          # array([2, 4, 6]) — operates on the whole array at once, no loop
   ```

**Bottom line:** say "list" when you mean a list. Reach for `numpy` when you're doing serious
numeric work. `array.array` is a rare specialist.

➡️ Run `examples/08_array.py`

---

## 8. Recursion — a function that calls itself

Not a data structure — a *technique*. But it's the natural way to process **nested or
self-similar data** (trees, file systems, nested JSON, graphs), so it belongs in your toolkit
right next to the structures above. Many a junior fears recursion; a middle engineer reaches for
it when — and only when — it fits.

**Every recursion needs exactly two parts.** Miss either and it breaks:
1. **Base case** — the condition that *stops* the recursion (no further self-call).
2. **Recursive case** — solve a *smaller* piece of the problem, then call yourself.

```python
def factorial(n):
    if n <= 1:                  # BASE CASE — stop
        return 1
    return n * factorial(n - 1) # RECURSIVE CASE — smaller problem
```

**The call stack — what's really happening.** Each call pauses and waits for the inner call to
return, stacking up in memory, then unwinds back out:
```
factorial(4)
└─ 4 * factorial(3)
      └─ 3 * factorial(2)
            └─ 2 * factorial(1)   ← base case returns 1
```
This stack is finite. Python caps it (default ~1000 frames, see
`sys.getrecursionlimit()`); blow past it and you get a `RecursionError`. **Python does *not*
optimize tail calls** — so deep linear recursion is a real risk, and a plain loop is often the
safer, clearer choice. Recurse for *branching* structure (trees), loop for *linear* sequences.

**The trap: naive recursion that recomputes everything.** The classic example is Fibonacci:
```python
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)   # 🔴 recomputes the same values exponentially
```
`fib(35)` makes ~30 million calls for a 36th number. The fix is **memoization** — cache results
so each input is computed once. The standard library hands it to you for free:
```python
from functools import cache

@cache                       # remembers every result — O(2^n) collapses to O(n)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)
```
In the example file you'll see this exact change take Fibonacci from ~0.1s to ~15 *micro*seconds.
Recognizing "this recursion recomputes subproblems → memoize it" is the doorway to dynamic
programming, and a very common interview turn.

**Where recursion truly shines — nested data:**
```python
def sum_nested(data):
    total = 0
    for item in data:
        total += sum_nested(item) if isinstance(item, list) else item
    return total

sum_nested([1, [2, 3, [4, 5]], 6])   # 21 — the code mirrors the data's shape
```
Try writing that with a plain loop and you'll feel why recursion exists.

➡️ Run `examples/10_recursion.py`

---

## Choosing the right structure — the cheat sheet

This is the decision table. When you can answer "why this structure?" instantly, you're
operating at middle level.

| I need to...                                    | Use            | Why                              |
|-------------------------------------------------|----------------|----------------------------------|
| Keep an ordered, growable collection            | `list`         | The default                      |
| Store a fixed group that won't change           | `tuple`        | Immutable, signals intent        |
| Look things up by a key/name                    | `dict`         | O(1) lookup                      |
| Check "is X in here?" a lot                     | `set`          | O(1) membership                  |
| Guarantee uniqueness                            | `set`          | Drops duplicates automatically   |
| Count occurrences                               | `Counter`      | Purpose-built                    |
| Group items by a key                            | `defaultdict`  | No missing-key boilerplate       |
| LIFO (undo, DFS, history)                       | `list`         | `append`/`pop` are O(1)          |
| FIFO (job queue, BFS)                           | `deque`        | O(1) at both ends                |
| Use a collection as a dict key                  | `tuple`/`frozenset` | Hashable                    |
| Heavy numeric math                              | `numpy.ndarray`| Vectorized, fast                 |
| Process nested / tree-shaped data               | recursion      | Code mirrors the data's shape    |
| Speed up recursion that repeats subproblems     | `@cache`       | Memoize — O(2ⁿ) → O(n)           |

---

## Performance cheat sheet (memorize the surprises)

The ones that catch people are marked 🔴 — those are the O(n) operations hiding in a structure
people *think* is fast.

| Operation                  | list      | deque  | dict   | set    |
|----------------------------|-----------|--------|--------|--------|
| Index access `x[i]`        | O(1)      | O(n)   | —      | —      |
| Append to end              | O(1)      | O(1)   | —      | —      |
| Insert/remove at front     | 🔴 O(n)   | O(1)   | —      | —      |
| Membership `x in c`        | 🔴 O(n)   | O(n)   | O(1)   | O(1)   |
| Lookup/insert by key       | —         | —      | O(1)   | —      |
| Add/remove element         | —         | —      | O(1)   | O(1)   |

Two takeaways that fix most real-world slowness:
- **Repeated `x in some_list`?** → switch to a `set` or `dict`.
- **`list.pop(0)` or `list.insert(0, ...)`?** → switch to a `deque`.

---

## Common traps that catch juniors (read this twice)

**1. The mutable default argument.** This one is famous and *will* be in an interview:
```python
def add(item, bucket=[]):     # 🔴 the [] is created ONCE, shared across all calls
    bucket.append(item)
    return bucket

add(1)    # [1]
add(2)    # [1, 2]  ← surprise! Same list reused.

def add(item, bucket=None):   # ✅ the fix
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket
```

**2. Copying — assignment doesn't copy.**
```python
a = [1, 2, 3]
b = a            # b is the SAME list, not a copy
b.append(4)
a                # [1, 2, 3, 4]  ← a changed too!

b = a.copy()     # or a[:] or list(a) — now a shallow copy
```
For nested structures, even `.copy()` isn't enough — inner objects are still shared. Use
`copy.deepcopy()` when you need a fully independent clone.

**3. Modifying a collection while iterating over it.**
```python
for x in my_list:
    if condition(x):
        my_list.remove(x)    # 🔴 skips elements / undefined behavior
```
Iterate over a copy (`for x in my_list[:]`) or build a new list with a comprehension.

**4. `is` vs `==` on values.** Use `==` for values; `is` only for `None`/`True`/`False`.

---

## How to actually get good at this

1. **Run every file in `examples/`.** Then change a value and predict the output before
   re-running. Being right consistently is the goal.
2. **For every structure, be able to say its cost.** When you write `x in collection`, a little
   voice should ask "is this a list? then it's O(n) — should it be a set?"
3. **In code review, ask "why this structure?"** of your own code before someone else does.
4. **Read the docs once, end to end:** the [`collections`](https://docs.python.org/3/library/collections.html)
   module and the [built-in types](https://docs.python.org/3/library/stdtypes.html) page. You'll
   discover methods you've been hand-rolling for years.

You don't become middle+ by memorizing syntax — you become middle+ by reflexively reaching for
the *right* structure and being able to explain the trade-off. Get the four built-ins and
`deque`/`Counter`/`defaultdict` into your fingers, and you're most of the way there.

Now go run the examples. — Your senior dev 🦾
