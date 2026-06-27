"""Queue — First In, First Out (FIFO). Use a deque, NOT list.pop(0).

Run me:  uv run python learn/examples/07_queue.py
"""

import time
from collections import deque


def basic_queue() -> None:
    queue: deque[str] = deque()
    queue.append("task1")      # enqueue — add to back
    queue.append("task2")
    queue.append("task3")
    print("queue:", queue)
    print("serve:", queue.popleft())   # "task1" — first in, first out, O(1)
    print("serve:", queue.popleft())   # "task2"
    print("queue:", queue)


def why_not_list() -> None:
    """Show the cost difference: list.pop(0) is O(n), deque.popleft() is O(1)."""
    n = 200_000

    lst = list(range(n))
    t0 = time.perf_counter()
    while lst:
        lst.pop(0)              # O(n) each time -> O(n^2) total. Ouch.
    list_time = time.perf_counter() - t0

    dq = deque(range(n))
    t0 = time.perf_counter()
    while dq:
        dq.popleft()            # O(1) each time -> O(n) total.
    deque_time = time.perf_counter() - t0

    print(f"list.pop(0)   over {n:,} items: {list_time:.3f}s")
    print(f"deque.popleft over {n:,} items: {deque_time:.3f}s")
    print(f"deque was ~{list_time / deque_time:.0f}x faster")


def bfs_demo() -> None:
    """Breadth-first traversal of a tiny graph — queues power BFS."""
    graph = {
        "A": ["B", "C"],
        "B": ["D", "E"],
        "C": ["F"],
        "D": [], "E": [], "F": [],
    }
    queue = deque(["A"])
    visited: list[str] = []
    while queue:
        node = queue.popleft()      # FIFO => explore level by level
        visited.append(node)
        queue.extend(graph[node])
    print("BFS order:", " -> ".join(visited))


if __name__ == "__main__":
    print("== basic queue =="); basic_queue()
    print("\n== why not a list? =="); why_not_list()
    print("\n== BFS uses a queue =="); bfs_demo()
