# 02. Сортування — усі алгоритми з кодом

> *(Базу заклали в основних блоках п.60–62 — тут повні реалізації кожного.)*
> На практиці завжди `sorted()`/`list.sort()` (Timsort). Свої реалізації — для розуміння й інтерв'ю.

---

## L1 — Junior: інтуїція

**Аналогія — впорядкувати колоду карт.** Способи різні: міняти сусідів (bubble), щоразу брати найменшу (selection), вставляти кожну на місце в готову частину (insertion), ділити навпіл і зливати (merge). Усі дають відсортоване, але різною ціною.

Два терміни на все життя:
- **Stable (стабільне)** — зберігає порядок рівних елементів (важливо для сортування за кількома ключами).
- **In-place** — O(1) додаткової пам'яті (сортує «на місці»).

---

## L2 — Middle: реалізації

### 1. Bubble Sort — O(n²), stable, in-place
Найбільший «спливає» в кінець за кожен прохід.
```python
def bubble_sort(arr: list[int]) -> None:
    n = len(arr)
    for i in range(n):
        swapped = False
        for j in range(n - i - 1):           # останні i вже на місці
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:                       # відсортовано → вихід (best O(n))
            break
```

### 2. Selection Sort — O(n²), НЕ stable, in-place
Щоразу знаходимо мінімум і ставимо на початок. Мінімум **swap'ів** (O(n) обмінів).
```python
def selection_sort(arr: list[int]) -> None:
    n = len(arr)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
```

### 3. Insertion Sort — O(n²) worst / O(n) best, stable, in-place
Бере елемент і **вставляє** в уже відсортовану ліву частину. Чудовий на **майже відсортованих** і **малих** даних.
```python
def insertion_sort(arr: list[int]) -> None:
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:        # зсуваємо більші вправо
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
```

### 4. Merge Sort — O(n log n) завжди, stable, O(n) пам'яті
**Divide & conquer:** ділимо навпіл, сортуємо кожну, **зливаємо**.
```python
def merge_sort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:                          # база
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])               # T(n/2)
    right = merge_sort(arr[mid:])              # T(n/2)
    return merge(left, right)                  # O(n) злиття

def merge(left: list[int], right: list[int]) -> list[int]:
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:                # <= робить сортування STABLE
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])                    # додаємо «хвости»
    result.extend(right[j:])
    return result
```

### 5. Quick Sort — O(n log n) average / O(n²) worst, НЕ stable, O(log n) стек
**Divide & conquer:** обираємо **pivot**, ділимо на менші/більші, рекурсивно.
```python
def quick_sort(arr: list[int]) -> list[int]:
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]                 # pivot із середини (краще за крайній)
    left = [x for x in arr if x < pivot]
    mid = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + mid + quick_sort(right)

# In-place (Lomuto partition) — як питають на інтерв'ю:
def quick_sort_inplace(arr: list[int], lo: int = 0, hi: int | None = None) -> None:
    if hi is None:
        hi = len(arr) - 1
    if lo < hi:
        p = partition(arr, lo, hi)
        quick_sort_inplace(arr, lo, p - 1)
        quick_sort_inplace(arr, p + 1, hi)

def partition(arr: list[int], lo: int, hi: int) -> int:
    pivot = arr[hi]                            # pivot = останній
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[hi] = arr[hi], arr[i + 1]
    return i + 1
```

### 6. Heap Sort — O(n log n) завжди, НЕ stable, O(1) пам'яті
Будуємо max-heap, по черзі витягуємо максимум у кінець. *(Купи — файл 09.)*
```python
import heapq

def heap_sort(arr: list[int]) -> list[int]:
    heapq.heapify(arr)                         # O(n) — min-heap на місці
    return [heapq.heappop(arr) for _ in range(len(arr))]   # n × O(log n)
```

### 7. Counting Sort — O(n + k), stable, для цілих у діапазоні [0..k]
**Без порівнянь** — рахуємо входження. *(Деталі п.62.)*
```python
def counting_sort(arr: list[int]) -> list[int]:
    if not arr:
        return []
    k = max(arr)
    counts = [0] * (k + 1)
    for x in arr:                              # O(n)
        counts[x] += 1
    result = []
    for value, cnt in enumerate(counts):       # O(k)
        result.extend([value] * cnt)
    return result
```

### 8. Radix Sort — O(d·(n + k)), stable, для цілих/рядків
Сортуємо порозрядно (LSD — від молодшого розряду), стабільним counting на кожен розряд.
```python
def radix_sort(arr: list[int]) -> list[int]:
    if not arr:
        return []
    max_val = max(arr)
    exp = 1
    while max_val // exp > 0:                  # d ітерацій (по розрядах)
        arr = counting_by_digit(arr, exp)
        exp *= 10
    return arr

def counting_by_digit(arr: list[int], exp: int) -> list[int]:
    output = [0] * len(arr)
    counts = [0] * 10
    for x in arr:
        counts[(x // exp) % 10] += 1
    for i in range(1, 10):                      # префіксні суми → позиції
        counts[i] += counts[i - 1]
    for x in reversed(arr):                     # reversed зберігає стабільність
        d = (x // exp) % 10
        counts[d] -= 1
        output[counts[d]] = x
    return output
```

### Перевірка — усі дають однаковий результат
```python
data = [5, 2, 9, 1, 5, 6]
assert sorted(data) == merge_sort(data[:]) == quick_sort(data[:]) \
       == counting_sort(data[:]) == radix_sort(data[:])
```

---

## L3 — Senior: вибір, трейдофи, Timsort

### Зведена таблиця
| Алгоритм | Best | Avg | Worst | Space | Stable | Коли використовувати |
|---|---|---|---|---|---|---|
| Bubble | O(n) | O(n²) | O(n²) | O(1) | ✅ | ніколи (педагогіка) |
| Selection | O(n²) | O(n²) | O(n²) | O(1) | ❌ | коли swap дорогий (мінімум обмінів) |
| Insertion | O(n) | O(n²) | O(n²) | O(1) | ✅ | малі/майже відсортовані дані |
| Merge | O(n log n) | O(n log n) | O(n log n) | O(n) | ✅ | стабільність, linked list, зовнішнє |
| Quick | O(n log n) | O(n log n) | O(n²) | O(log n) | ❌ | загальний in-memory (найшвидший на практиці) |
| Heap | O(n log n) | O(n log n) | O(n log n) | O(1) | ❌ | гарантія + O(1) пам'ять, top-K |
| Counting | O(n+k) | O(n+k) | O(n+k) | O(n+k) | ✅ | цілі, малий діапазон k |
| Radix | O(d(n+k)) | — | O(d(n+k)) | O(n+k) | ✅ | великі масиви цілих/рядків |

### Чому однакове O(n log n), а швидкість різна
- **Merge** стабільний і гарантований, але O(n) пам'яті (буфер) → для linked lists і зовнішнього сортування (дані не влазять у RAM).
- **Quick** має O(n²) worst (поганий pivot), зате **найкраща локальність кешу** й мала константа → найшвидший на практиці in-memory. Захист від O(n²): рандомізований pivot / median-of-three / **introsort** (перехід на heap при деградації глибини рекурсії).
- **Heap** гарантований + O(1) пам'ять, але погана локальність кешу (стрибки по масиву) → повільніший за quick.

### Чому межа comparison sort — Ω(n log n)
Будь-яке порівняльне сортування — це **decision tree** із `n!` листками (усі перестановки). Висота ≥ `log₂(n!) ≈ n log n` (Стірлінг). Тому **жоден** алгоритм на порівняннях не може бути швидшим за `Ω(n log n)`. Лінійні (counting/radix) обходять межу, **не порівнюючи** (використовують значення як індекси), ціною обмежень на дані. *(Доказ — п.62.)*

### Stable vs in-place — фундаментальний трейдоф
Зазвичай не можна дешево мати обидва: Merge стабільний, але не in-place; Quick/Heap in-place, але не стабільні. Це компроміс **пам'ять ↔ збереження порядку**.

**Навіщо стабільність:** сортування за кількома ключами по черзі. Спершу за іменем, потім стабільно за віком → усередині однакового віку зберігається порядок за іменем.
```python
people = [("Іван", 30), ("Анна", 25), ("Олег", 30)]
people.sort(key=lambda p: p[0])      # за іменем
people.sort(key=lambda p: p[1])      # стабільно за віком → імена впорядковані всередині
```

### Timsort — чому обрав Python
Реальні дані часто **частково відсортовані**. Timsort (гібрид merge + insertion):
1. Знаходить уже відсортовані ділянки — **runs**.
2. Малі runs досортовує **insertion sort** (швидкий на дрібних, мала константа).
3. Зливає runs **merge**'ом із оптимізаціями (galloping mode).

Результат: **O(n)** на майже відсортованих, гарантований **O(n log n)** у гіршому, **стабільний**. Універсальний — сортує будь-що з `__lt__`.

```python
# Практика: ніколи не пиши свій сорт — Timsort оптимізований роками
data.sort()                          # in-place, None
new = sorted(data, reverse=True)     # новий список
data.sort(key=lambda x: (x.age, x.name))   # за кількома ключами (стабільно)
```

**Gotcha:** `list.sort()` повертає `None` (сортує на місці!), `sorted()` повертає новий список. `x = data.sort()` → `x is None` — найчастіша помилка.

---

## 🎯 Задачі для практики (LeetCode patterns)
- Sort Colors (Dutch flag, 3-way partition) — варіант quick partition.
- Merge Intervals — sort + прохід.
- Kth Largest Element — heap або quickselect (O(n) average).
- Largest Number — custom comparator (`functools.cmp_to_key`).
- Sort List — merge sort на linked list (O(1) пам'ять для списку).

**Далі:** [03_searching.md](03_searching.md) — binary search і всі його підступні варіанти.

> ⚠️ Точна поведінка Timsort (minrun, galloping) — деталі CPython (`Objects/listsort.txt`). Складності стандартні (CLRS), реальна швидкість залежить від даних і кеша.
