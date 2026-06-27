# 10. Графи (Graphs) — вершина складності

> Найбагатша тема: BFS, DFS, топологічне сортування, Dijkstra, Union-Find, MST. Багато реальних задач (мережі, карти, залежності, соцграфи) — це графи. Потрібні файли 04 (рекурсія), 07 (стек/черга), 09 (купа).

---

## L1 — Junior: інтуїція та представлення

**Аналогія — карта міст із дорогами.** **Вершини (vertices/nodes)** — міста, **ребра (edges)** — дороги. Граф може бути:
- **Орієнтований** (directed) — дороги односторонні (Twitter: A фоловить B ≠ B фоловить A).
- **Зважений** (weighted) — у ребер є вага (відстань, вартість).

### Два представлення
```python
# 1. Adjacency List (список суміжності) — найчастіше, O(V+E) пам'яті
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C"],
}

# 2. Adjacency Matrix (матриця суміжності) — O(V²) пам'яті
#      A  B  C  D
# A  [ 0, 1, 1, 0 ]
# B  [ 1, 0, 0, 1 ]   matrix[i][j] = 1 якщо є ребро i→j
matrix = [[0,1,1,0],[1,0,0,1],[1,0,0,1],[0,1,1,0]]
```

**Коли що:** adjacency **list** — для **розріджених** графів (мало ребер, типовий випадок). Adjacency **matrix** — для **щільних** графів або коли потрібен O(1) тест «чи є ребро i→j».

---

## L2 — Middle: BFS і DFS — два кити

### BFS (Breadth-First Search) — по рівнях, з чергою
Знаходить **найкоротший шлях у незваженому** графі (мінімум ребер).
```python
from collections import deque

def bfs(graph: dict, start: str) -> list[str]:
    visited = {start}                    # ОДРАЗУ позначаємо при додаванні в чергу
    queue = deque([start])
    order = []
    while queue:
        node = queue.popleft()           # FIFO → найближчі першими
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order

def shortest_path_bfs(graph: dict, start: str, target: str) -> int:
    visited = {start}
    queue = deque([(start, 0)])          # (вузол, відстань)
    while queue:
        node, dist = queue.popleft()
        if node == target:
            return dist                  # перше досягнення = найкоротший шлях!
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, dist + 1))
    return -1
```

### DFS (Depth-First Search) — углиб, рекурсія або стек
Для **зв'язності, усіх шляхів, циклів, компонент**.
```python
def dfs(graph: dict, start: str) -> list[str]:
    visited = set()
    order = []
    def visit(node: str) -> None:
        visited.add(node)
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                visit(neighbor)
    visit(start)
    return order

# Ітеративний DFS (для глибоких графів, без ліміту рекурсії — файл 07)
def dfs_iterative(graph: dict, start: str) -> list[str]:
    visited, order, stack = set(), [], [start]
    while stack:
        node = stack.pop()               # LIFO → углиб
        if node not in visited:
            visited.add(node)
            order.append(node)
            stack.extend(graph[node])
    return order
```

### Класика: підрахунок островів (DFS на сітці)
```python
def num_islands(grid: list[list[str]]) -> int:
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    count = 0
    def sink(r: int, c: int) -> None:
        if not (0 <= r < rows and 0 <= c < cols) or grid[r][c] != "1":
            return
        grid[r][c] = "0"                 # «затопити» (позначити відвідане)
        sink(r+1, c); sink(r-1, c); sink(r, c+1); sink(r, c-1)
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                count += 1
                sink(r, c)               # затопити весь острів
    return count
```

**Gotcha — позначай visited ВЧАСНО:** у BFS додавай у `visited` **при додаванні в чергу**, а не при витяганні — інакше один вузол потрапить у чергу багато разів (через кілька сусідів) → O(V²) або TLE.

**BFS vs DFS:** обидва O(V+E). BFS → найкоротший шлях/рівні (черга, більше пам'яті на широких графах). DFS → зв'язність/шляхи/цикли (стек/рекурсія, менше пам'яті на глибоких). Різниця — лише **FIFO vs LIFO** (файл 07).

---

## L3 — Senior: топосорт, Dijkstra, Union-Find, MST

### Топологічне сортування (порядок залежностей у DAG)
Лінійний порядок вершин так, що кожне ребро u→v: u перед v. Для **планувальників, збірок, розкладів курсів**. Працює лише на **DAG** (Directed Acyclic Graph).

**Kahn's algorithm (BFS-based, через in-degree):**
```python
from collections import deque

def topological_sort(graph: dict, num_nodes: int) -> list[int]:
    in_degree = [0] * num_nodes
    for node in graph:
        for neighbor in graph[node]:
            in_degree[neighbor] += 1
    queue = deque([n for n in range(num_nodes) if in_degree[n] == 0])  # без залежностей
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1     # «прибрали» залежність
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    return order if len(order) == num_nodes else []   # порожній = є цикл!
```
**Виявлення циклу:** якщо в результат потрапили не всі вершини → є цикл (Course Schedule, LC 207). Це й спосіб **детекції циклу** в орієнтованому графі.

### Dijkstra — найкоротший шлях зі вагами ≥ 0
BFS не працює зі вагами (рахує ребра, не суму ваг). Dijkstra використовує **min-heap** (файл 09): завжди розширюємо найближчу неопрацьовану вершину.
```python
import heapq

def dijkstra(graph: dict[int, list[tuple[int, int]]], start: int, n: int) -> list[float]:
    dist = [float("inf")] * n
    dist[start] = 0
    heap = [(0, start)]                   # (відстань, вузол)
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:                # застаріла відстань → пропустити
            continue
        for neighbor, weight in graph[node]:
            new_dist = d + weight
            if new_dist < dist[neighbor]: # знайшли коротший шлях
                dist[neighbor] = new_dist
                heapq.heappush(heap, (new_dist, neighbor))
    return dist
# O((V+E) log V) завдяки купі
```
**Чому ваги мають бути ≥ 0:** Dijkstra «фіксує» найкоротшу відстань, коли вершина виходить із купи (жадібно). Від'ємне ребро могло б згодом зменшити вже зафіксовану відстань → алгоритм ламається. Для **від'ємних ваг — Bellman-Ford** (O(V·E), ще й детектує від'ємні цикли).

### Union-Find (Disjoint Set Union) — компоненти зв'язності
Структура для «чи в одній групі?» і «об'єднати групи» за майже O(1). Основа Kruskal MST, детекції циклів у неорієнтованому графі.
```python
class UnionFind:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))     # кожен сам собі корінь
        self.rank = [0] * n              # для балансування

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])   # PATH COMPRESSION
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        px, py = self.find(x), self.find(y)
        if px == py:
            return False                 # уже в одній групі (цикл!)
        if self.rank[px] < self.rank[py]:   # UNION BY RANK
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True
```
**Дві оптимізації разом** (path compression + union by rank) дають амортизовану складність **O(α(n))** — обернена функція Аккермана, практично **константа** (α(n) < 5 для будь-якого реального n). Без них — O(n) на операцію.

### MST (мінімальне кістякове дерево) — Kruskal через Union-Find
З'єднати всі вершини мінімальною сумарною вагою ребер (мережі, кластеризація).
```python
def kruskal(n: int, edges: list[tuple[int, int, int]]) -> int:
    """edges = [(вага, u, v)]. Повертає вагу MST."""
    edges.sort()                         # ребра за зростанням ваги — жадібно
    uf = UnionFind(n)
    total = 0
    for weight, u, v in edges:
        if uf.union(u, v):               # додаємо ребро, якщо не створює цикл
            total += weight
    return total
# O(E log E) — домінує сортування ребер
```
**Prim** (альтернатива MST) — росте дерево від однієї вершини через min-heap, O(E log V). Kruskal краще для розріджених графів, Prim — для щільних.

### Зведена таблиця графових алгоритмів
| Алгоритм | Складність | Призначення | Структура |
|---|---|---|---|
| BFS | O(V+E) | найкоротший шлях (незважений), рівні | черга |
| DFS | O(V+E) | зв'язність, цикли, шляхи | стек/рекурсія |
| Topological Sort | O(V+E) | порядок залежностей (DAG) | черга (in-degree) |
| Dijkstra | O((V+E)log V) | найкоротший шлях, ваги ≥ 0 | min-heap |
| Bellman-Ford | O(V·E) | найкоротший шлях, від'ємні ваги | — |
| Floyd-Warshall | O(V³) | усі пари шляхів | DP-матриця |
| Union-Find | ~O(α(n)) | компоненти, цикли (неорієнт.) | масив parent |
| Kruskal/Prim MST | O(E log V) | мінімальне кістякове дерево | UF / heap |

### Розпізнавання патерну (Senior-евристика)
- «найкоротший шлях», «мінімум кроків», «найближче» **без ваг** → **BFS**.
- «усі шляхи», «зв'язність», «острови», «цикл» → **DFS**.
- «порядок», «залежності», «розклад» (можна зробити X лише після Y) → **Topological Sort**.
- «найкоротший шлях зі **вагами**» → **Dijkstra** (≥0) / **Bellman-Ford** (від'ємні).
- «групи», «з'єднати», «чи в одному компоненті» → **Union-Find**.
- «з'єднати все мінімальною вартістю» → **MST**.

---

## 🎯 Задачі для практики
**BFS/DFS:** Number of Islands (200), Clone Graph (133), Rotting Oranges (994), Word Ladder (127), Pacific Atlantic Water Flow (417), Flood Fill (733).
**Topo Sort:** Course Schedule (207, 210), Alien Dictionary (269).
**Dijkstra:** Network Delay Time (743), Cheapest Flights Within K Stops (787, Bellman-Ford), Path with Minimum Effort (1631).
**Union-Find:** Number of Connected Components (323), Redundant Connection (684), Accounts Merge (721), Graph Valid Tree (261).
**MST:** Min Cost to Connect All Points (1584), Connecting Cities (1135).

**Далі:** [11_dynamic_programming.md](11_dynamic_programming.md) — найстрашніша тема інтерв'ю, але за системою.

> ⚠️ Dijkstra НЕ працює з від'ємними вагами (потрібен Bellman-Ford). Складність α(n) для Union-Find — обернена Аккермана; точний доказ — CLRS. Глибокий DFS → ітеративний (ліміт рекурсії).
