# 03. Пошук — Binary Search і всі його варіанти

> Binary search — найчастіший і найпідступніший патерн на інтерв'ю. «Легко зрозуміти, важко написати без багів» (за дослідженнями, ~90% програмістів пишуть його з помилкою з першого разу).

---

## L1 — Junior: інтуїція

**Аналогія — пошук слова в паперовому словнику.** Ти не гортаєш сторінку за сторінкою (це linear search, O(n)). Відкриваєш **посередині**: слово раніше за алфавітом? — шукаєш у лівій половині, інакше — у правій. Щоразу **відкидаєш половину** → дуже швидко (O(log n)).

**Головна умова:** дані мають бути **відсортовані**.

```python
# Linear search — O(n), працює на будь-яких даних
def linear_search(arr: list[int], target: int) -> int:
    for i, x in enumerate(arr):
        if x == target:
            return i
    return -1

# Binary search — O(log n), лише на ВІДСОРТОВАНИХ
def binary_search(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1            # шукаємо праворуч
        else:
            hi = mid - 1            # шукаємо ліворуч
    return -1
```

Чому O(log n): n → n/2 → n/4 → ... → 1. Кількість ділень = `log₂(n)`. Для мільярда елементів — лише ~30 кроків!

---

## L2 — Middle: канонічний шаблон і пастки

### Інваріант і межі (де всі помиляються)
Тримай у голові **інваріант**: «target, якщо є, лежить у `[lo, hi]`».
```python
def binary_search(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1     # ОБИДВА кінці включно → while lo <= hi
    while lo <= hi:              # <= бо коли lo == hi, ще один елемент для перевірки
        mid = lo + (hi - lo) // 2   # захист від переповнення (в інших мовах)
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            lo = mid + 1         # +1 ОБОВ'ЯЗКОВО — інакше нескінченний цикл
        else:
            hi = mid - 1         # -1 теж обов'язково
    return -1
```

**Три найчастіші баги:**
1. `while lo < hi` замість `<=` → пропускаєш останній елемент.
2. `lo = mid` замість `lo = mid + 1` → **нескінченний цикл** (mid не рухається).
3. `mid = (lo + hi) // 2` — у Python ок, але в C/Java **переповнення**; звичка `lo + (hi-lo)//2`.

### Готове в stdlib — модуль `bisect`
Не пиши свій binary search для базових задач — використовуй `bisect`:
```python
import bisect

arr = [1, 3, 3, 3, 5, 7, 9]
bisect.bisect_left(arr, 3)    # 1 — перша позиція, куди вставити 3 (lower bound)
bisect.bisect_right(arr, 3)   # 4 — остання позиція (upper bound)
bisect.bisect_left(arr, 4)    # 4 — куди вставити 4, щоб лишилось відсортовано
bisect.insort(arr, 4)         # вставити, зберігши порядок — O(n) (зсув)
```

### Lower bound / Upper bound (фундаментальні варіанти)
```python
def lower_bound(arr: list[int], target: int) -> int:
    """Перший індекс, де arr[i] >= target (= bisect_left)."""
    lo, hi = 0, len(arr)         # hi = len (НЕ len-1) — напіввідкритий [lo, hi)
    while lo < hi:               # < бо межа напіввідкрита
        mid = (lo + hi) // 2
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid             # БЕЗ -1 — mid може бути відповіддю
    return lo

def upper_bound(arr: list[int], target: int) -> int:
    """Перший індекс, де arr[i] > target (= bisect_right)."""
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid] <= target:
            lo = mid + 1
        else:
            hi = mid
    return lo

# Кількість входжень target = upper_bound - lower_bound
arr = [1, 2, 2, 2, 3]
count = upper_bound(arr, 2) - lower_bound(arr, 2)   # 3
```

**Gotcha — два шаблони:** «знайти точне» використовує `[lo, hi]` (closed, `<=`, `mid±1`). «Знайти межу/bound» — `[lo, hi)` (half-open, `<`, `hi = mid`). Не змішуй їх — обери один стиль і дотримуйся.

---

## L3 — Senior: просунуті варіанти й «binary search on answer»

### 1. Перше/останнє входження (дублікати)
```python
def find_first(arr: list[int], target: int) -> int:
    lo, hi, res = 0, len(arr) - 1, -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            res = mid
            hi = mid - 1          # знайшли, але шукаємо ЛІВІШЕ (перше)
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return res
```

### 2. Пошук у поверненому (rotated) відсортованому масиві
`[4,5,6,7,0,1,2]` — відсортований, але «прокручений». Класика інтерв'ю (LeetCode 33).
```python
def search_rotated(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target:
            return mid
        if arr[lo] <= arr[mid]:           # ліва половина відсортована
            if arr[lo] <= target < arr[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                              # права половина відсортована
            if arr[mid] < target <= arr[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1
```

### 3. Binary Search on Answer (найпотужніший патерн!)
Коли відповідь — **число в монотонному діапазоні**, і ти можеш перевірити «чи годиться X», — бінарний пошук **по відповіді**, а не по масиву.

**Задача:** мінімальна швидкість поїдання бананів `k`, щоб з'їсти всі за `h` годин (LeetCode 875).
```python
import math

def min_eating_speed(piles: list[int], h: int) -> int:
    def hours_needed(k: int) -> int:
        return sum(math.ceil(p / k) for p in piles)

    lo, hi = 1, max(piles)               # діапазон можливих відповідей
    while lo < hi:
        mid = (lo + hi) // 2
        if hours_needed(mid) <= h:       # годиться → пробуємо менше
            hi = mid
        else:                            # не встигає → треба більше
            lo = mid + 1
    return lo
```
**Ідея:** є монотонний предикат `can(X)` (якщо швидкість годиться, то й більша годиться). Шукаємо **межу** переходу false→true за O(log(range)·перевірка). Так розв'язують: «мінімальна потужність», «найменший дільник», «split array», «капітальне планування».

### 4. Binary search по дійсних числах (точність)
```python
def sqrt_binary(x: float, eps: float = 1e-9) -> float:
    lo, hi = 0.0, max(1.0, x)
    while hi - lo > eps:                  # критерій — точність, не lo<=hi
        mid = (lo + hi) / 2
        if mid * mid < x:
            lo = mid
        else:
            hi = mid
    return lo
```

### Складність і трейдофи
| Метод | Час | Умова |
|---|---|---|
| Linear search | O(n) | будь-які дані |
| Binary search | O(log n) | відсортовані |
| Hash (set/dict) | O(1) | потрібна хеш-таблиця, без діапазонів |

**Коли binary search програє hash:** для **точного** «чи є елемент» `set` дає O(1) < O(log n). Binary search виграє, коли потрібні **діапазонні** запити, **сусідні** елементи (lower/upper bound), **порядок**, або дані вже відсортовані й немає пам'яті на хеш.

**Чому log n настільки потужний:** кожен крок **подвоює** охоплений діапазон. 20 кроків → мільйон, 30 → мільярд, 40 → трильйон. Тому «можеш швидше за O(n)?» на відсортованих даних = майже завжди «binary search до O(log n)».

**Senior-евристика розпізнавання:** бачиш «**відсортований** масив» або «знайти **мінімальне/максимальне X, що задовольняє** монотонну умову» → думай binary search (по масиву або по відповіді). Друге — найнедооцінніший патерн, що перетворює O(n·range) перебір на O(n·log range).

---

## 🎯 Задачі для практики
- Binary Search (LC 704), Search Insert Position (35) — базові.
- First/Last Position (34) — lower/upper bound.
- Search in Rotated Sorted Array (33), Find Minimum in Rotated (153).
- Koko Eating Bananas (875), Capacity to Ship Packages (1011), Split Array Largest Sum (410) — **binary search on answer**.
- Median of Two Sorted Arrays (4) — складний binary search.
- Sqrt(x) (69) — пошук по числах.

**Далі:** [04_recursion_backtracking.md](04_recursion_backtracking.md) — рекурсія як основа дерев, графів, DP.

> ⚠️ `bisect` працює лише на відсортованих послідовностях і не перевіряє це. На невідсортованих дасть мовчазно неправильний результат.
