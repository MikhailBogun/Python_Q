# 04. Рекурсія та Backtracking

> Рекурсія — основа дерев (08), графів (10), divide&conquer (02), DP (11). Backtracking — систематичний перебір усіх варіантів. Без цього файлу не зрозуміти половину курсу.

---

## L1 — Junior: інтуїція рекурсії

**Аналогія — матрьошка.** Щоб порахувати всі ляльки, відкриваєш одну → всередині така сама задача (порахувати решту) → відкриваєш наступну... аж до найменшої, що не відкривається (**база**). Потім «складаєш» відповіді назад.

**Кожна рекурсія = 2 частини (інакше нескінченність):**
1. **Базовий випадок (base case)** — коли зупинитись (без рекурсії).
2. **Рекурсивний випадок** — розв'яжи менший шматок + поклич себе.

```python
def factorial(n: int) -> int:
    if n <= 1:                    # БАЗА: зупинка
        return 1
    return n * factorial(n - 1)   # РЕКУРСІЯ: менша задача

def sum_list(arr: list[int]) -> int:
    if not arr:                   # база: порожній список
        return 0
    return arr[0] + sum_list(arr[1:])   # перший + сума решти
```

**Gotcha:** забув базу → `RecursionError` (нескінченні виклики). Python має ліміт ~1000 вкладених викликів (`sys.getrecursionlimit()`).

---

## L2 — Middle: call stack, типи рекурсії, мемоізація

### Як працює call stack
Кожен виклик додає **frame** на стек (свої локальні змінні). Стек росте при заглибленні, «розкручується» при поверненні:
```python
def factorial_traced(n: int, depth: int = 0) -> int:
    indent = "  " * depth
    print(f"{indent}-> factorial({n})")        # ВХІД (стек росте)
    if n <= 1:
        return 1
    result = n * factorial_traced(n - 1, depth + 1)
    print(f"{indent}<- factorial({n}) = {result}")   # ВИХІД (стек спадає)
    return result
# factorial_traced(4): -> 4, -> 3, -> 2, -> 1, <- 2, <- 6, <- 24
```

### Рекурсія vs ітерація
Будь-яку рекурсію можна переписати циклом (явним стеком). Коли що:
- **Рекурсія** природна для **дерев/графів/вкладених структур** (мирорить форму даних).
- **Ітерація** — для лінійних задач (немає ліміту глибини, менше overhead на frames).

```python
def factorial_iterative(n: int) -> int:
    result = 1
    for i in range(2, n + 1):     # те саме без рекурсії
        result *= i
    return result
```

### Пастка експоненційної рекурсії → мемоізація
Наївний Фібоначчі **перераховує** ті самі значення → O(2ⁿ):
```python
def fib_naive(n: int) -> int:
    if n < 2:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)    # O(2ⁿ) — fib(35) уже повільно

from functools import cache
@cache                            # кешує результати → кожен n рахується ОДИН раз
def fib_fast(n: int) -> int:
    if n < 2:
        return n
    return fib_fast(n - 1) + fib_fast(n - 2)       # O(n) — fib(100) миттєво
```
Це міст до DP (файл 11): мемоізація = top-down DP.

### Gotcha — `arr[1:]` копіює
`sum_list(arr[1:])` створює **новий список** щоразу → O(n²) пам'яті/часу прихований. Краще передавати **індекс**:
```python
def sum_list(arr: list[int], i: int = 0) -> int:
    if i == len(arr):
        return 0
    return arr[i] + sum_list(arr, i + 1)     # без копіювання
```

---

## L3 — Senior: Backtracking — універсальний шаблон

### Що таке backtracking
**Систематичний перебір** усіх варіантів: будуємо рішення крок за кроком, а коли заходимо в глухий кут — **відкочуємось** (undo) і пробуємо інше. Це DFS по «дереву рішень».

**Універсальний шаблон (запам'ятай назавжди):**
```python
def backtrack(state, choices):
    if is_solution(state):           # дійшли до повного рішення
        result.append(state.copy())  # ЗБЕРЕГТИ КОПІЮ (state змінюється далі!)
        return
    for choice in choices:           # перебираємо варіанти
        if is_valid(choice, state):
            state.add(choice)        # 1. ЗРОБИТИ вибір
            backtrack(state, ...)    # 2. РЕКУРСІЯ глибше
            state.remove(choice)     # 3. ВІДКОТИТИ (backtrack!)
```

### 1. Підмножини (subsets) — O(2ⁿ)
```python
def subsets(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []

    def backtrack(start: int, path: list[int]) -> None:
        result.append(path[:])               # кожен вузол — валідна підмножина
        for i in range(start, len(nums)):
            path.append(nums[i])             # вибрати
            backtrack(i + 1, path)           # глибше (i+1 — без повторів)
            path.pop()                       # відкотити

    backtrack(0, [])
    return result
# subsets([1,2,3]) → [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]
```

### 2. Перестановки (permutations) — O(n!)
```python
def permutations(nums: list[int]) -> list[list[int]]:
    result: list[list[int]] = []

    def backtrack(path: list[int], remaining: list[int]) -> None:
        if not remaining:                    # використали всі → готова перестановка
            result.append(path[:])
            return
        for i in range(len(remaining)):
            path.append(remaining[i])
            backtrack(path, remaining[:i] + remaining[i+1:])   # без i-го
            path.pop()

    backtrack([], nums)
    return result
# permutations([1,2,3]) → 6 перестановок
```

### 3. Комбінації (combinations) — обрати k з n
```python
def combinations(n: int, k: int) -> list[list[int]]:
    result: list[list[int]] = []

    def backtrack(start: int, path: list[int]) -> None:
        if len(path) == k:                   # набрали k → готово
            result.append(path[:])
            return
        for i in range(start, n + 1):
            path.append(i)
            backtrack(i + 1, path)
            path.pop()

    backtrack(1, [])
    return result
# combinations(4, 2) → [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
```

### 4. N-Queens — класика backtracking
Розставити N ферзів на N×N так, щоб не били одна одну.
```python
def solve_n_queens(n: int) -> int:
    count = 0
    cols: set[int] = set()
    diag1: set[int] = set()                  # r - c (діагональ ↘)
    diag2: set[int] = set()                  # r + c (діагональ ↙)

    def backtrack(row: int) -> None:
        nonlocal count
        if row == n:                         # усі рядки заповнені → рішення
            count += 1
            return
        for col in range(n):
            if col in cols or (row-col) in diag1 or (row+col) in diag2:
                continue                     # під боєм → пропустити
            cols.add(col); diag1.add(row-col); diag2.add(row+col)   # поставити
            backtrack(row + 1)               # наступний рядок
            cols.discard(col); diag1.discard(row-col); diag2.discard(row+col)  # зняти

    backtrack(0)
    return count
# solve_n_queens(4) → 2, solve_n_queens(8) → 92
```

### 5. Word Search (backtracking на сітці)
```python
def exist(board: list[list[str]], word: str) -> bool:
    rows, cols = len(board), len(board[0])

    def dfs(r: int, c: int, i: int) -> bool:
        if i == len(word):                   # знайшли все слово
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[i]:
            return False
        tmp, board[r][c] = board[r][c], "#"  # позначити відвідане
        found = (dfs(r+1, c, i+1) or dfs(r-1, c, i+1) or
                 dfs(r, c+1, i+1) or dfs(r, c-1, i+1))
        board[r][c] = tmp                    # відкотити (backtrack)
        return found

    return any(dfs(r, c, 0) for r in range(rows) for c in range(cols))
```

### Складність backtracking і pruning
- **Subsets:** O(2ⁿ) — кожен елемент є/немає.
- **Permutations:** O(n!) — усі порядки.
- **Combinations:** O(C(n,k)).

**Pruning (відсікання) — ключ до ефективності:** чим раніше відкидаєш безнадійні гілки (`is_valid`, `continue`), тим менше дерево. N-Queens без перевірок — O(nⁿ); з перевірками діагоналей — на порядки менше. Senior завжди шукає, **де обрізати** перебір раніше.

### Чому 3 кроки (вибір → рекурсія → відкат) критичні
`result.append(path[:])` — **копія**, бо `path` мутується далі (після pop). Забути `[:]` → усі елементи `result` посилаються на **один** список, що в кінці порожній — класичний баг (зв'язок з блоком 6 п.80: mutable shared reference).

### Трейдоф рекурсія vs явний стек
Рекурсія читабельна (мирорить структуру), але:
- **Ліміт глибини** (`sys.setrecursionlimit`) — глибокі дерева/графи (>1000) → `RecursionError`. Рішення: ітеративний DFS з явним `stack = []`.
- **Overhead** на frame'и (пам'ять + час). Python **не має** tail-call optimization (Гвідо свідомо відмовив — заради читабельних трейсбеків).

```python
import sys
sys.setrecursionlimit(10000)     # обережно: глибше → ризик переповнення C-стека
```

---

## 🎯 Задачі для практики
- Subsets (78), Subsets II (90, з дублікатами).
- Permutations (46), Permutations II (47).
- Combinations (77), Combination Sum (39, 40).
- N-Queens (51), Sudoku Solver (37).
- Word Search (79), Generate Parentheses (22), Letter Combinations (17).
- Palindrome Partitioning (131).

**Далі:** [05_two_pointers_sliding_window.md](05_two_pointers_sliding_window.md) — лінійні патерни на масивах.

> ⚠️ `sys.setrecursionlimit` піднімає ліміт Python, але C-стек скінченний — надто велике значення → краш інтерпретатора (segfault), а не чистий виняток.
