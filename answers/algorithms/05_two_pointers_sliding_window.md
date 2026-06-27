# 05. Two Pointers та Sliding Window

> Два найчастіші патерни для масивів і рядків. Перетворюють O(n²) перебір на O(n). Якщо опануєш — закриєш величезний клас задач інтерв'ю.

---

## L1 — Junior: інтуїція

**Two Pointers** — два «пальці», що рухаються по масиву (з кінців назустріч або обидва зліва). Замість перебору всіх пар (O(n²)) — один прохід (O(n)).

**Sliding Window** — «вікно» (діапазон `[left, right]`), що ковзає масивом. Розширюємо праву межу, звужуємо ліву — підтримуємо потрібну умову. Замість перерахунку кожного підмасиву (O(n²)) — інкрементально (O(n)).

**Аналогія:** two pointers — двоє йдуть назустріч у коридорі. Sliding window — гусениця: голова повзе вперед, хвіст підтягується.

---

## L2 — Middle: Two Pointers

### Патерн 1: Назустріч (opposite ends) — на відсортованому
```python
def two_sum_sorted(arr: list[int], target: int) -> tuple[int, int] | None:
    left, right = 0, len(arr) - 1
    while left < right:
        s = arr[left] + arr[right]
        if s == target:
            return (left, right)
        elif s < target:
            left += 1            # треба більше → рухаємо ліву праворуч
        else:
            right -= 1           # треба менше → рухаємо праву ліворуч
    return None
# Замість O(n²) перебору пар — O(n), бо масив відсортований
```

### Патерн 2: Перевірка паліндрома
```python
def is_palindrome(s: str) -> bool:
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True
```

### Патерн 3: Швидкий/повільний (видалення дублікатів in-place)
```python
def remove_duplicates(arr: list[int]) -> int:
    if not arr:
        return 0
    slow = 0                     # повільний — позиція для запису
    for fast in range(1, len(arr)):     # швидкий — сканує
        if arr[fast] != arr[slow]:
            slow += 1
            arr[slow] = arr[fast]
    return slow + 1              # довжина унікальної частини
```

### Патерн 4: Три вказівники (3Sum) — O(n²)
```python
def three_sum(nums: list[int]) -> list[list[int]]:
    nums.sort()                  # O(n log n)
    result: list[list[int]] = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue             # пропустити дублікат
        left, right = i + 1, len(nums) - 1
        while left < right:      # two pointers всередині — O(n)
            s = nums[i] + nums[left] + nums[right]
            if s < 0:
                left += 1
            elif s > 0:
                right -= 1
            else:
                result.append([nums[i], nums[left], nums[right]])
                left += 1; right -= 1
                while left < right and nums[left] == nums[left-1]:
                    left += 1    # пропустити дублікати
    return result                # разом O(n²)
```

---

## L2 — Middle: Sliding Window

### Тип 1: Фіксований розмір вікна
```python
def max_sum_subarray(arr: list[int], k: int) -> int:
    """Максимальна сума підмасиву довжини k."""
    window_sum = sum(arr[:k])    # перше вікно
    max_sum = window_sum
    for i in range(k, len(arr)):
        window_sum += arr[i] - arr[i - k]   # додати новий, прибрати старий — O(1)!
        max_sum = max(max_sum, window_sum)
    return max_sum
# Замість O(n·k) — O(n): вікно оновлюється інкрементально
```

### Тип 2: Динамічний розмір (найдовше/найкоротше з умовою)
```python
def longest_substring_no_repeat(s: str) -> int:
    """Найдовший підрядок без повторюваних символів (LC 3)."""
    seen: dict[str, int] = {}    # символ → останній індекс
    left = 0
    max_len = 0
    for right, ch in enumerate(s):
        if ch in seen and seen[ch] >= left:
            left = seen[ch] + 1  # звузити вікно: перестрибнути дублікат
        seen[ch] = right
        max_len = max(max_len, right - left + 1)
    return max_len
# "abcabcbb" → 3 ("abc")
```

### Тип 3: Найкоротше вікно з умовою
```python
def min_subarray_len(target: int, nums: list[int]) -> int:
    """Найкоротший підмасив із сумою >= target (LC 209)."""
    left = 0
    window_sum = 0
    min_len = float("inf")
    for right in range(len(nums)):
        window_sum += nums[right]            # розширюємо праворуч
        while window_sum >= target:          # умова виконана → звужуємо
            min_len = min(min_len, right - left + 1)
            window_sum -= nums[left]
            left += 1
    return min_len if min_len != float("inf") else 0
```

**Gotcha:** sliding window працює, коли розширення/звуження вікна **монотонно** впливає на умову (додав елемент — сума росте). Для масивів із **від'ємними** числами «сума ≥ target» так не працює (звуження може й збільшити суму) — там потрібен prefix sum + інші техніки.

---

## L3 — Senior: чому це працює і коли застосовувати

### Чому O(n), а не O(n²) — амортизований аргумент
У sliding window обидва вказівники (`left`, `right`) рухаються **лише вперед** і **жоден не повертається**. Кожен елемент входить у вікно один раз і виходить один раз → сумарно ≤ 2n рухів → **O(n)**, попри вкладений `while`. Це ключовий інсайт: вкладений цикл ≠ O(n²), якщо внутрішній вказівник не скидається.

```python
for right in range(n):       # n
    while condition:         # виглядає як O(n²)...
        left += 1            # ...але left рухається сумарно ≤ n разів за весь час
# Разом: O(n), не O(n²)!
```

### Коли який патерн (розпізнавання)
| Сигнал у задачі | Патерн |
|---|---|
| «пара/трійка з сумою» у **відсортованому** | Two Pointers (назустріч) |
| «паліндром», «реверс на місці» | Two Pointers (назустріч) |
| «видалити дублікати/елемент in-place» | Two Pointers (fast/slow) |
| «найдовший/найкоротший **підрядок/підмасив** з умовою» | Sliding Window |
| «**неперервний** діапазон» + сума/унікальність/частота | Sliding Window |
| «K різних символів», «не більше K» | Sliding Window + hashmap |

### Передумови застосування
- **Two pointers назустріч** вимагає **відсортованості** (або симетрії, як паліндром). Сортування додає O(n log n) — інколи варте того, щоб замінити O(n²) hash-перебір.
- **Sliding window** вимагає, щоб вікно було **неперервним** і умова — **монотонною** при розширенні/звуженні.

### Трейдоф vs хеш-таблиця
Two Sum на **невідсортованому** масиві:
- **Hash (dict):** O(n) час, O(n) пам'ять, повертає індекси.
- **Two pointers:** потрібно відсортувати O(n log n), O(1) пам'ять, але **губить вихідні індекси**.

Senior обирає: потрібні **оригінальні індекси** або масив несортований → hash; масив уже відсортований або потрібна O(1) пам'ять → two pointers.

### Зв'язок із prefix sums
Для задач «сума діапазону» без обмеження на знак — **prefix sum** (`prefix[i] = arr[0]+...+arr[i-1]`): сума `[l, r)` = `prefix[r] - prefix[l]` за O(1) після O(n) препроцесингу. Часто комбінується з hash («subarray sum equals K», LC 560).
```python
def subarray_sum_equals_k(nums: list[int], k: int) -> int:
    count = 0
    prefix = 0
    seen = {0: 1}                # prefix sum → скільки разів зустрічався
    for x in nums:
        prefix += x
        count += seen.get(prefix - k, 0)   # скільки префіксів дають потрібну різницю
        seen[prefix] = seen.get(prefix, 0) + 1
    return count
# Працює і з від'ємними числами (на відміну від sliding window)
```

---

## 🎯 Задачі для практики
**Two Pointers:** Two Sum II (167), 3Sum (15), Container With Most Water (11), Trapping Rain Water (42), Valid Palindrome (125), Move Zeroes (283), Remove Duplicates (26).
**Sliding Window:** Longest Substring Without Repeating (3), Minimum Window Substring (76), Longest Repeating Character Replacement (424), Max Consecutive Ones III (1004), Permutation in String (567), Subarray Sum Equals K (560, prefix sum).

**Далі:** [06_linked_lists.md](06_linked_lists.md) — алгоритми на зв'язаних списках.

> ⚠️ Sliding window НЕ застосовний наосліп — перевір монотонність умови (особливо з від'ємними числами). Якщо вікно немонотонне — prefix sum / інша техніка.
