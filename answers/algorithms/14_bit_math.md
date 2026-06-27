# 14. Бітові операції та математичні алгоритми

> Бітові трюки дають O(1) рішення там, де наївно O(n). Математичні алгоритми (GCD, решето, швидке піднесення) — класика, що приховує елегантні ідеї.

---

## L1 — Junior: інтуїція бітових операцій

**Аналогія — ряд вимикачів.** Число в пам'яті — це ряд бітів (0/1, вимкнено/увімкнено). Бітові операції вмикають/вимикають/перевіряють ці вимикачі **напряму**, дуже швидко.

```python
a, b = 0b1100, 0b1010   # 12 і 10 у двійковому

a & b    # AND  → 0b1000 (8)  — 1 лише де ОБИДВА 1
a | b    # OR   → 0b1110 (14) — 1 де ХОЧА Б ОДИН 1
a ^ b    # XOR  → 0b0110 (6)  — 1 де РІЗНІ
~a       # NOT  → інвертувати всі біти
a << 1   # зсув вліво  → 0b11000 (24) = ×2
a >> 1   # зсув вправо → 0b0110 (6)   = //2

bin(13)        # '0b1101' — подивитись біти
13 .bit_count()  # 3 — кількість одиничних бітів (Python 3.10+)
```

**Чому корисно:** `x << 1` = `x * 2`, `x >> 1` = `x // 2`, `x & 1` = парність — усе за один такт CPU.

---

## L2 — Middle: класичні бітові трюки

### Перевірка/маніпуляція бітів
```python
def is_even(x: int) -> bool:
    return x & 1 == 0                # останній біт 0 → парне

def is_power_of_two(x: int) -> bool:
    return x > 0 and (x & (x - 1)) == 0   # у степеня 2 рівно один біт!
# 8 = 1000, 7 = 0111, 8 & 7 = 0000 → True

def get_bit(x: int, i: int) -> int:
    return (x >> i) & 1              # i-й біт

def set_bit(x: int, i: int) -> int:
    return x | (1 << i)             # увімкнути i-й біт

def clear_bit(x: int, i: int) -> int:
    return x & ~(1 << i)            # вимкнути i-й біт

def toggle_bit(x: int, i: int) -> int:
    return x ^ (1 << i)            # перемкнути i-й біт
```

### XOR-трюки (улюблене на інтерв'ю)
```python
def single_number(nums: list[int]) -> int:
    """Усі числа парами, крім одного. Знайти його — O(n), O(1)."""
    result = 0
    for x in nums:
        result ^= x                 # x ^ x = 0, x ^ 0 = x → пари знищуються
    return result
# [4,1,2,1,2] → 4

def swap_without_temp(a: int, b: int) -> tuple[int, int]:
    a ^= b; b ^= a; a ^= b          # обмін без тимчасової змінної
    return a, b

def missing_number(nums: list[int]) -> int:
    """0..n, одне відсутнє. XOR індексів і значень."""
    result = len(nums)
    for i, x in enumerate(nums):
        result ^= i ^ x
    return result
```

### Підрахунок одиничних бітів (Brian Kernighan)
```python
def count_set_bits(x: int) -> int:
    count = 0
    while x:
        x &= x - 1                  # прибирає НАЙМОЛОДШИЙ одиничний біт
        count += 1
    return count
# O(кількість одиниць), а не O(всіх бітів). Або просто x.bit_count()
```

**Gotcha:** у Python цілі **необмеженого розміру** (big integers) і `~x = -(x+1)` (two's complement з нескінченним знаком). Тому бітові маски фіксованої ширини (як у C `uint32`) потребують явного `& 0xFFFFFFFF`. Це джерело багів при портуванні бітових алгоритмів.

---

## L3 — Senior: bitmask, математичні алгоритми

### Bitmask — множина як ціле число
Підмножину з n елементів (n ≤ ~20) кодуємо як n біт → швидкі операції над множинами, основа bitmask-DP (файл 11).
```python
def all_subsets_bitmask(nums: list[int]) -> list[list[int]]:
    n = len(nums)
    result = []
    for mask in range(1 << n):          # 2^n масок = усі підмножини
        subset = [nums[i] for i in range(n) if mask & (1 << i)]
        result.append(subset)
    return result
# Кожен біт маски = «чи входить i-й елемент». Елегантно для n ≤ 20.
```

### Euclid's GCD (найбільший спільний дільник) — O(log min(a,b))
```python
def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b             # gcd(a,b) = gcd(b, a mod b)
    return a
# gcd(48, 18) → gcd(18,12) → gcd(12,6) → gcd(6,0) → 6
# У stdlib: math.gcd(a, b), math.lcm(a, b)

def lcm(a: int, b: int) -> int:
    return a * b // gcd(a, b)        # НСК через НСД
```
**Чому O(log):** кожен крок `a % b` зменшує числа щонайменше вдвічі за дві ітерації (теорема Ламе, пов'язана з Фібоначчі). Один із найстаріших алгоритмів (Евклід, ~300 до н.е.).

### Sieve of Eratosthenes (решето) — усі прості до n за O(n log log n)
```python
def sieve(n: int) -> list[int]:
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, n + 1, i):   # викреслюємо кратні i (з i² — менші вже)
                is_prime[j] = False
    return [i for i in range(n + 1) if is_prime[i]]
# sieve(30) → [2,3,5,7,11,13,17,19,23,29]
```
**Чому з `i*i`:** кратні `i`, менші за `i²`, уже викреслені меншими простими множниками. Складність O(n log log n) — майже лінійна.

### Перевірка простоти одного числа — O(√n)
```python
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True                  # 2, 3
    if n % 2 == 0:
        return False
    for i in range(3, int(n**0.5) + 1, 2):   # лише непарні дільники до √n
        if n % i == 0:
            return False
    return True
```
**Чому до √n:** якщо `n = a·b`, то один із множників ≤ √n. Перевіривши до √n, покриваємо всі можливі дільники.

### Fast Exponentiation (швидке піднесення) — O(log n)
```python
def fast_pow(base: int, exp: int, mod: int | None = None) -> int:
    result = 1
    while exp > 0:
        if exp & 1:                  # якщо поточний біт exp = 1
            result = result * base
            if mod:
                result %= mod
        base = base * base           # квадрат бази
        if mod:
            base %= mod
        exp >>= 1                    # наступний біт
    return result
# fast_pow(2, 10) = 1024 за ~4 множення замість 10
# Python вбудоване: pow(base, exp, mod) — оптимізоване в C
```
**Ідея:** `2^10 = 2^8 · 2^2` — розкладаємо степінь на **степені двійки** (біти exp). O(log n) множень замість O(n). Критично для криптографії (RSA — `pow(m, e, n)`, блок основних питань про хешування/шифрування).

### Зведення: складності математичних алгоритмів
| Алгоритм | Складність | Застосування |
|---|---|---|
| GCD (Euclid) | O(log min(a,b)) | дроби, НСК, криптографія |
| Sieve | O(n log log n) | усі прості до n |
| Prime check | O(√n) | одне число |
| Fast pow | O(log n) | степені, модульна арифметика, RSA |
| Bitmask subsets | O(2ⁿ · n) | перебір підмножин (n ≤ 20) |

### Трейдофи й коли застосовувати
- **Бітові трюки** — елегантні й швидкі (O(1) на такт), але **знижують читабельність**. У проді коментуй (`x & (x-1)` неочевидно). Передчасна бітова мікрооптимізація — антипатерн; застосовуй, де реально критично (вбудовані системи, хеші, маски прав).
- **Sieve vs is_prime:** потрібно **багато** перевірок простоти до n → решето (один раз O(n log log n), далі O(1) lookup). Одна-дві перевірки великого числа → `is_prime` O(√n) (решето з'їло б пам'ять).
- **Fast pow** — завжди для модульного степеня (`pow(a,b,m)` у Python вже це робить). Наївний `a**b % m` рахує гігантський `a**b` перед `% m` — повільно й пам'ятежерливо для великих b.
- **Bitmask** обмежений ~20 елементами (2²⁰ ≈ мільйон станів). Для більшого — інші техніки.

**Senior-нота:** у Python великі числа «безкоштовні» (big int, блок основних питань п.75), тому модульна арифметика часто не обов'язкова для уникнення переповнення (на відміну від C/Java). Але `pow(a, b, m)` усе одно швидший за `a**b % m` для великих степенів — використовуй триаргументний `pow`.

---

## 🎯 Задачі для практики
**Біти:** Single Number (136, 137, 260), Number of 1 Bits (191), Counting Bits (338), Reverse Bits (190), Missing Number (268), Power of Two (231), Sum of Two Integers (371, без +), Bitwise AND of Range (201).
**Bitmask:** Subsets (78, через маски), Maximum XOR (421), Partition to K Equal Sum Subsets (698).
**Математика:** Pow(x,n) (50, fast pow), Count Primes (204, sieve), GCD of Strings (1071), Excel Column (168/171), Happy Number (202), Ugly Number (263/264).

**🎉 Це фінальний файл курсу!** Повернутись до огляду — [README.md](README.md).

> ⚠️ У Python int необмежені й `~x = -(x+1)` — бітові маски фіксованої ширини потребують `& 0xFFFFFFFF`. Для модульного степеня використовуй вбудований `pow(a, b, m)`, а не `a**b % m`.
