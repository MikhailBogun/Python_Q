# 07. Стеки та черги

> Дві фундаментальні структури. Stack — основа DFS, рекурсії, парсингу. Queue — основа BFS. Monotonic stack — потужний патерн інтерв'ю.

---

## L1 — Junior: інтуїція

- **Stack (стек)** — стопка тарілок: кладеш і береш **зверху**. **LIFO** (Last In, First Out). Остання покладена — перша знята.
- **Queue (черга)** — черга в магазині: стаєш у **кінець**, обслуговують з **початку**. **FIFO** (First In, First Out).

```python
# STACK — звичайний list (append/pop з кінця — O(1))
stack: list[int] = []
stack.append(1); stack.append(2)    # [1, 2]
top = stack.pop()                    # 2 (останній) — LIFO

# QUEUE — collections.deque (НЕ list!)
from collections import deque
queue: deque[int] = deque()
queue.append(1); queue.append(2)    # [1, 2]
first = queue.popleft()              # 1 (перший) — FIFO, O(1)
```

**Gotcha (важливо!):** для черги **не використовуй `list.pop(0)`** — це **O(n)** (зсуває всі елементи). Бери `collections.deque.popleft()` — **O(1)**.

---

## L2 — Middle: класичні застосування

### Stack: валідні дужки
```python
def is_valid_parentheses(s: str) -> bool:
    stack: list[str] = []
    pairs = {")": "(", "]": "[", "}": "{"}
    for ch in s:
        if ch in "([{":
            stack.append(ch)             # відкривна → на стек
        else:
            if not stack or stack.pop() != pairs[ch]:
                return False             # закривна не збігається з вершиною
    return not stack                     # стек має бути порожнім
# "([])" → True, "([)]" → False
```

### Stack: обчислення зворотного польського запису (RPN)
```python
def eval_rpn(tokens: list[str]) -> int:
    stack: list[int] = []
    ops = {"+": lambda a, b: a + b, "-": lambda a, b: a - b,
           "*": lambda a, b: a * b, "/": lambda a, b: int(a / b)}
    for t in tokens:
        if t in ops:
            b, a = stack.pop(), stack.pop()   # порядок! b знятий перший
            stack.append(ops[t](a, b))
        else:
            stack.append(int(t))
    return stack[0]
# ["2","1","+","3","*"] → (2+1)*3 = 9
```

### Min Stack — стек з O(1) мінімумом
```python
class MinStack:
    def __init__(self) -> None:
        self._stack: list[int] = []
        self._mins: list[int] = []       # паралельний стек мінімумів

    def push(self, x: int) -> None:
        self._stack.append(x)
        self._mins.append(min(x, self._mins[-1] if self._mins else x))

    def pop(self) -> None:
        self._stack.pop()
        self._mins.pop()

    def get_min(self) -> int:
        return self._mins[-1]            # O(1)!
```

### Queue: deque як двобічна черга
```python
from collections import deque
dq: deque[int] = deque([1, 2, 3])
dq.append(4)        # додати в кінець       O(1)
dq.appendleft(0)    # додати на початок     O(1)
dq.pop()            # зняти з кінця         O(1)
dq.popleft()        # зняти з початку       O(1)
```

---

## L3 — Senior: Monotonic Stack — патерн «наступний більший»

### Що це і навіщо
**Монотонний стек** тримає елементи у **зростаючому або спадному** порядку. Коли новий елемент порушує порядок — «виштовхуємо» зі стека, обробляючи. Розв'язує клас задач «**наступний/попередній більший/менший елемент**» за **O(n)** замість O(n²).

### Next Greater Element — O(n)
Для кожного елемента — перший більший праворуч.
```python
def next_greater(nums: list[int]) -> list[int]:
    result = [-1] * len(nums)
    stack: list[int] = []                # зберігаємо ІНДЕКСИ, спадний за значенням
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            idx = stack.pop()            # знайшли більший для нього → x
            result[idx] = x
        stack.append(i)
    return result
# [2,1,2,4,3] → [4,2,4,-1,-1]
```

### Daily Temperatures — скільки днів чекати теплішого
```python
def daily_temperatures(temps: list[int]) -> list[int]:
    result = [0] * len(temps)
    stack: list[int] = []                # індекси, спадна температура
    for i, t in enumerate(temps):
        while stack and temps[stack[-1]] < t:
            prev = stack.pop()
            result[prev] = i - prev      # різниця в днях
        stack.append(i)
    return result
# [73,74,75,71,69,72,76,73] → [1,1,4,2,1,1,0,0]
```

### Largest Rectangle in Histogram — складна, O(n)
```python
def largest_rectangle(heights: list[int]) -> int:
    stack: list[int] = []                # індекси зростаючих висот
    max_area = 0
    heights = heights + [0]              # «страж» у кінці виштовхує все
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            height = heights[stack.pop()]
            width = i if not stack else i - stack[-1] - 1
            max_area = max(max_area, height * width)
        stack.append(i)
    return max_area
```

### Чому monotonic stack — O(n)
Кожен елемент **заходить** на стек один раз і **сходить** максимум один раз → сумарно ≤ 2n операцій, попри вкладений `while`. Це той самий амортизований аргумент, що в sliding window (файл 05): внутрішній цикл не «скидається». Без стека ця ж задача — O(n²) (для кожного шукати більший перебором).

### Stack ↔ рекурсія (глибокий зв'язок)
**Виклик функції використовує call stack** (блок 6, п.75). Тому **будь-яку рекурсію можна переписати явним стеком** — це роблять, коли глибина рекурсії перевищує ліміт Python (~1000), напр. для глибокого DFS (файл 08/10):
```python
# Рекурсивний DFS → ітеративний зі стеком
def dfs_iterative(graph: dict, start) -> list:
    visited, order, stack = set(), [], [start]
    while stack:
        node = stack.pop()               # LIFO → глибина-перший
        if node not in visited:
            visited.add(node)
            order.append(node)
            stack.extend(graph[node])    # додати сусідів
    return order
```
**BFS** — те саме, але з `deque.popleft()` (FIFO) замість `stack.pop()` (LIFO). Різниця LIFO/FIFO = різниця DFS/BFS. Це фундаментальний інсайт для графів.

### Трейдофи реалізації в Python
| Структура | Чим робити | Уникати |
|---|---|---|
| Stack | `list` (append/pop) | — |
| Queue | `collections.deque` | ❌ `list.pop(0)` — O(n) |
| Двобічна черга | `deque` | — |
| Priority queue | `heapq` (файл 09) | — |

`deque` реалізована як **двозв'язний список блоків** → O(1) з обох кінців, але O(n) доступ за індексом усередині. `list` — навпаки (O(1) індекс, O(n) вставка на початок). Вибір — за патерном доступу (блок основних питань п.50).

---

## 🎯 Задачі для практики
**Stack:** Valid Parentheses (20), Min Stack (155), Evaluate RPN (150), Basic Calculator (224), Decode String (394), Asteroid Collision (735).
**Monotonic Stack:** Daily Temperatures (739), Next Greater Element (496, 503), Largest Rectangle in Histogram (84), Trapping Rain Water (42), Remove K Digits (402).
**Queue:** Implement Queue using Stacks (232), Sliding Window Maximum (239, monotonic deque), Number of Recent Calls (933).

**Далі:** [08_trees.md](08_trees.md) — дерева, обходи, BST, trie.

> ⚠️ Найчастіша помилка продуктивності з чергами в Python — `list.pop(0)` замість `deque.popleft()`. У великому циклі це перетворює O(n) на O(n²).
