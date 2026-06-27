# 11. Динамічне програмування (DP)

> Найстрашніша тема інтерв'ю — але за системою цілком приборкувана. DP = рекурсія (файл 04) + запам'ятовування результатів. Якщо є **перекривні підзадачі** та **оптимальна підструктура** — це DP.

---

## L1 — Junior: інтуїція

**Аналогія — рахуєш сходинки, записуючи проміжне.** Щоб піднятись на 10 сходинок (по 1 чи 2 за раз), не перераховуй щоразу — **запиши**, скількома способами дійти до кожної сходинки, і використовуй попередні. DP = «не рахуй те саме двічі».

**Дві ознаки, що це DP:**
1. **Overlapping subproblems** — задача розпадається на підзадачі, які **повторюються**.
2. **Optimal substructure** — оптимум усієї задачі будується з оптимумів підзадач.

```python
# Фібоначчі — найпростіший DP. Наївна рекурсія рахує fib(3) багато разів:
#         fib(5)
#        /      \
#     fib(4)   fib(3)      ← fib(3) рахується ДВІЧІ
#     /    \
#  fib(3) fib(2)           ← і ще раз!
```

---

## L2 — Middle: два підходи (memoization vs tabulation)

### Climbing Stairs — канонічний приклад
**Скількома способами піднятись на n сходинок (по 1 або 2)?** `ways(n) = ways(n-1) + ways(n-2)` — це Фібоначчі!

**Підхід 1: Top-Down (memoization) — рекурсія + кеш**
```python
from functools import cache

@cache                               # автоматична мемоізація!
def climb_memo(n: int) -> int:
    if n <= 2:
        return n
    return climb_memo(n - 1) + climb_memo(n - 2)
# O(n) час, O(n) пам'ять (кеш + стек рекурсії)
```

**Підхід 2: Bottom-Up (tabulation) — ітеративно, таблиця**
```python
def climb_tab(n: int) -> int:
    if n <= 2:
        return n
    dp = [0] * (n + 1)
    dp[1], dp[2] = 1, 2
    for i in range(3, n + 1):
        dp[i] = dp[i-1] + dp[i-2]    # будуємо знизу вгору
    return dp[n]
# O(n) час, O(n) пам'ять
```

**Підхід 3: оптимізація пам'яті — O(1)**
```python
def climb_optimized(n: int) -> int:
    if n <= 2:
        return n
    prev, curr = 1, 2                # тримаємо лише 2 останні значення
    for _ in range(3, n + 1):
        prev, curr = curr, prev + curr
    return curr
# O(n) час, O(1) пам'ять!
```

### Memoization vs Tabulation
| | Top-Down (memo) | Bottom-Up (tab) |
|---|---|---|
| Стиль | рекурсія + `@cache` | цикл + масив |
| Інтуїтивність | ✅ (природний перехід з рекурсії) | складніше «побачити» |
| Пам'ять | кеш + стек рекурсії | лише таблиця |
| Ризик | ліміт рекурсії на глибоких | — |
| Рахує | лише потрібні підзадачі | усі підзадачі |

**Gotcha:** `@functools.cache` працює лише з **hashable** аргументами (не list/dict). Для списків передавай `tuple` або індекси.

---

## L3 — Senior: класичні задачі та фреймворк

### Фреймворк розв'язання DP (5 кроків)
1. **Define state** — що означає `dp[i]`? (напр. «макс. сума до індексу i»).
2. **Recurrence** — як `dp[i]` виражається через попередні?
3. **Base case** — початкові значення.
4. **Order** — у якому порядку заповнювати (щоб залежності були готові).
5. **Answer** — де відповідь (`dp[n]`? `max(dp)`?).

### 1. Coin Change — мінімум монет на суму (LC 322)
```python
def coin_change(coins: list[int], amount: int) -> int:
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0                            # 0 монет на суму 0
    for i in range(1, amount + 1):
        for coin in coins:
            if coin <= i:
                dp[i] = min(dp[i], dp[i - coin] + 1)   # узяти монету + решта
    return dp[amount] if dp[amount] != float("inf") else -1
# state: dp[i] = мін. монет на суму i. O(amount × coins)
```

### 2. 0/1 Knapsack (рюкзак) — взяти/не взяти
```python
def knapsack(weights: list[int], values: list[int], capacity: int) -> int:
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(capacity + 1):
            dp[i][w] = dp[i-1][w]                        # не беремо предмет i
            if weights[i-1] <= w:                        # якщо влазить — пробуємо взяти
                dp[i][w] = max(dp[i][w],
                               dp[i-1][w - weights[i-1]] + values[i-1])
    return dp[n][capacity]
# O(n × capacity) — псевдополіноміально (файл 01: capacity — значення, не розмір!)
```

### 3. Longest Common Subsequence (LCS) — 2D DP
```python
def lcs(text1: str, text2: str) -> int:
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i-1] == text2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1              # збіг → +1 по діагоналі
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])   # макс. без одного символа
    return dp[m][n]
# "abcde", "ace" → 3 ("ace"). O(m × n)
```

### 4. Edit Distance (Левенштейн) — 2D DP
```python
def edit_distance(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i                     # видалити i символів
    for j in range(n + 1):
        dp[0][j] = j                     # вставити j символів
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i-1] == word2[j-1]:
                dp[i][j] = dp[i-1][j-1]                  # збіг — нічого не робимо
            else:
                dp[i][j] = 1 + min(dp[i-1][j],           # видалити
                                   dp[i][j-1],           # вставити
                                   dp[i-1][j-1])         # замінити
    return dp[m][n]
```

### 5. Longest Increasing Subsequence (LIS)
```python
def lis(nums: list[int]) -> int:
    if not nums:
        return 0
    dp = [1] * len(nums)                 # dp[i] = довжина LIS, що закінчується на i
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
# O(n²). Існує O(n log n) версія через binary search (bisect, файл 03)!

import bisect
def lis_fast(nums: list[int]) -> int:
    tails: list[int] = []                # tails[i] = найменший «хвіст» LIS довжини i+1
    for x in nums:
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)                    # O(n log n)
```

### 6. House Robber — DP на лінії
```python
def rob(nums: list[int]) -> int:
    prev, curr = 0, 0                    # не можна грабувати сусідні
    for x in nums:
        prev, curr = curr, max(curr, prev + x)   # max(пропустити, узяти+позаминулий)
    return curr
# O(n) час, O(1) пам'ять
```

### Класифікація DP-задач (Senior розпізнавання)
| Тип | Сигнал | Приклади |
|---|---|---|
| 1D лінійний | «послідовність», «до індексу» | Climbing Stairs, House Robber, LIS |
| 2D сітка | дві послідовності / grid | LCS, Edit Distance, Unique Paths |
| Knapsack | «обрати підмножину з обмеженням» | 0/1 Knapsack, Coin Change, Partition |
| Інтервальний | «розбити діапазон» | Matrix Chain, Burst Balloons |
| На деревах/графах | DP по вузлах | House Robber III |
| Бітмаска | малий n (≤20), стани як біти | TSP, Assignment |

### DP vs інші підходи (трейдофи)
- **DP vs Backtracking (файл 04):** обидва перебирають, але DP **кешує** перекривні підзадачі → з O(2ⁿ) робить O(n²)/O(n·W). Якщо підзадачі **не** перекриваються — кеш марний, потрібен чистий backtracking.
- **DP vs Greedy (файл 12):** DP розглядає **всі** варіанти (гарантований оптимум), greedy бере локально найкращий (швидше, але не завжди оптимум). Coin Change: greedy працює для «канонічних» монет, DP — для **будь-яких**.
- **Top-down vs bottom-up:** memo рахує лише **досяжні** стани (добре, якщо простір станів розріджений), tab рахує **всі** (але без overhead рекурсії й дозволяє оптимізацію пам'яті до O(1)/O(одного рядка)).

### Чому «псевдополіноміальний» (важливий нюанс)
Knapsack O(n·W) і Coin Change O(amount·coins) виглядають поліноміально, але `W`/`amount` — це **значення**, що кодуються `log W` бітами. Тому від **розміру входу** це **експоненційно** → 0/1 Knapsack — NP-складна задача, а O(n·W) — псевдополіноміальний (файл 01). Тому при `W = 10⁹` цей DP не спрацює.

---

## 🎯 Задачі для практики (за зростанням складності)
**Базові:** Climbing Stairs (70), House Robber (198, 213), Min Cost Climbing Stairs (746), Fibonacci (509).
**1D:** Coin Change (322), Word Break (139), LIS (300), Max Product Subarray (152), Decode Ways (91).
**2D:** Unique Paths (62, 63), LCS (1143), Edit Distance (72), Minimum Path Sum (64).
**Knapsack:** Partition Equal Subset Sum (416), Target Sum (494), Coin Change II (518).
**Складні:** Longest Palindromic Substring (5), Burst Balloons (312), Regular Expression Matching (10), Best Time to Buy/Sell Stock (121/122/123/188).

**Далі:** [12_greedy.md](12_greedy.md) — коли локально найкраще = глобально найкраще.

> ⚠️ `@cache` потребує hashable аргументів. Псевдополіноміальні DP (Knapsack) не масштабуються на великі значення W. Для деяких задач O(n²) DP має O(n log n) альтернативу (LIS) — знай обидві.
