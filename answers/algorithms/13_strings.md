# 13. Рядкові алгоритми

> Пошук підрядка (KMP, Rabin-Karp), анаграми, паліндроми. Багато перетинається з two pointers (05), sliding window (05), trie (08), DP (11).

---

## L1 — Junior: інтуїція + особливості рядків у Python

**Аналогія — пошук фрази в книзі.** Наївно: прикладаєш шаблон до кожної позиції тексту й порівнюєш. Розумні алгоритми (KMP) **не повертаються назад** даремно — пам'ятають, що вже збіглося.

**Рядки в Python — immutable (блок основних питань п.25):**
```python
s = "hello"
s[0] = "H"               # ❌ TypeError — рядок незмінний
s = "H" + s[1:]          # ✅ створюємо НОВИЙ рядок

# Конкатенація в циклі — пастка O(n²)!
result = ""
for ch in chars:
    result += ch         # ❌ кожен += створює новий рядок → O(n²)
result = "".join(chars)  # ✅ O(n)
```

---

## L2 — Middle: часті патерни

### Наївний пошук підрядка — O(n·m)
```python
def naive_search(text: str, pattern: str) -> int:
    n, m = len(text), len(pattern)
    for i in range(n - m + 1):
        if text[i:i+m] == pattern:       # порівняння O(m) на кожній позиції
            return i
    return -1
# O(n·m) у гіршому ("aaaa...a" + "aaab")
```

### Анаграми (частотний підхід)
```python
from collections import Counter

def is_anagram(s: str, t: str) -> bool:
    return Counter(s) == Counter(t)      # однакові частоти символів → O(n)

def group_anagrams(strs: list[str]) -> list[list[str]]:
    groups: dict[tuple, list[str]] = {}
    for s in strs:
        key = tuple(sorted(s))           # відсортований рядок — спільний ключ
        groups.setdefault(key, []).append(s)
    return list(groups.values())
# ["eat","tea","tan","ate"] → [["eat","tea","ate"],["tan"]]
```

### Паліндром (two pointers, файл 05)
```python
def is_palindrome(s: str) -> bool:
    s = [c.lower() for c in s if c.isalnum()]   # лише букви/цифри
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1; right -= 1
    return True
```

### Найдовший паліндромний підрядок (expand around center) — O(n²)
```python
def longest_palindrome(s: str) -> str:
    def expand(left: int, right: int) -> str:
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1; right += 1
        return s[left+1:right]           # розширюємо від центру назовні
    result = ""
    for i in range(len(s)):
        odd = expand(i, i)               # центр — символ (непарна довжина)
        even = expand(i, i+1)            # центр — між символами (парна)
        result = max(result, odd, even, key=len)
    return result
```

---

## L3 — Senior: KMP та Rabin-Karp

### KMP (Knuth-Morris-Pratt) — пошук підрядка за O(n + m)
**Ідея:** при незбігу наївний алгоритм відкочує текст назад. KMP **не відкочує текст** — використовує попередньо обчислену таблицю **failure function (LPS — Longest Proper Prefix that is also Suffix)**, щоб знати, на скільки можна «перестрибнути».
```python
def kmp_search(text: str, pattern: str) -> int:
    if not pattern:
        return 0
    lps = build_lps(pattern)             # препроцесинг шаблону O(m)
    i = j = 0                            # i — по тексту, j — по шаблону
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1; j += 1
            if j == len(pattern):
                return i - j             # знайшли!
        elif j > 0:
            j = lps[j - 1]               # «перестрибнути» (НЕ відкочуючи i)
        else:
            i += 1
    return -1

def build_lps(pattern: str) -> list[int]:
    """lps[i] = довжина найдовшого власного префікса, що = суфіксу для pattern[:i+1]."""
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length > 0:
            length = lps[length - 1]     # відкат у самому шаблоні
        else:
            lps[i] = 0
            i += 1
    return lps
```
**Чому O(n+m):** `i` (по тексту) **ніколи не відкочується** назад → ≤ n кроків; препроцесинг LPS — O(m). Наївний — O(n·m), бо при кожному незбігу починає спочатку.

### Rabin-Karp — пошук через rolling hash, O(n + m) середній
**Ідея:** порівнювати не рядки (дорого), а їх **хеші** (числа, O(1)). «Rolling hash» оновлює хеш вікна за O(1) при зсуві (як sliding window, файл 05).
```python
def rabin_karp(text: str, pattern: str) -> int:
    n, m = len(text), len(pattern)
    if m > n:
        return -1
    base, mod = 256, 10**9 + 7
    high = pow(base, m - 1, mod)         # base^(m-1) mod p
    p_hash = t_hash = 0
    for i in range(m):                   # хеш шаблону й першого вікна
        p_hash = (p_hash * base + ord(pattern[i])) % mod
        t_hash = (t_hash * base + ord(text[i])) % mod
    for i in range(n - m + 1):
        if p_hash == t_hash:             # хеші збіглись
            if text[i:i+m] == pattern:   # ПЕРЕВІРКА (захист від колізій!)
                return i
        if i < n - m:                    # rolling: оновити хеш за O(1)
            t_hash = ((t_hash - ord(text[i]) * high) * base
                      + ord(text[i+m])) % mod
            t_hash %= mod
    return -1
```
**Gotcha — колізії:** різні рядки можуть мати однаковий хеш → при збігу хешів **обов'язково** звіряємо самі рядки. Без перевірки — false positive. Гірший випадок (багато колізій) — O(n·m), середній — O(n+m).

### Трейдофи алгоритмів пошуку підрядка
| Алгоритм | Час (avg) | Час (worst) | Препроцесинг | Коли |
|---|---|---|---|---|
| Naive | O(n·m) | O(n·m) | — | короткі рядки |
| KMP | O(n+m) | **O(n+m)** | O(m) | один патерн, гарантія |
| Rabin-Karp | O(n+m) | O(n·m) | O(m) | **багато патернів** (один хеш на всі) |
| Trie/Aho-Corasick | — | O(n+сумма) | O(патерни) | багато патернів одночасно |

**Коли що:**
- **KMP** — один шаблон, потрібна **гарантія** O(n+m) (worst-case безпечний).
- **Rabin-Karp** — шукати **багато** шаблонів однакової довжини (порівнюєш хеш вікна з множиною хешів патернів), або задачі на rolling hash (дублікати підрядків).
- На практиці в Python `text.find(pattern)` / `in` вже оптимізовані (CPython використовує гібрид, історично Boyer-Moore-подібний); власний KMP пишуть **на інтерв'ю**, не в проді.

### Чому в реальному коді — вбудоване
```python
text.find(pattern)        # позиція або -1
pattern in text           # bool
text.count(pattern)       # кількість входжень
text.replace(old, new)    # заміна
```
CPython реалізує пошук підрядка в C з оптимізаціями → швидше за будь-який Python-KMP. Знання KMP/Rabin-Karp — для **розуміння** й рідкісних кастомних задач (rolling hash для «найдовший повторюваний підрядок»).

---

## 🎯 Задачі для практики
**Базові:** Valid Anagram (242), Group Anagrams (49), Valid Palindrome (125), Longest Palindromic Substring (5), Palindromic Substrings (647).
**Sliding window (файл 05):** Longest Substring Without Repeating (3), Minimum Window Substring (76), Find All Anagrams (438).
**Пошук підрядка:** Implement strStr (28, KMP), Repeated String Match (686), Shortest Palindrome (214, KMP).
**Rolling hash:** Longest Duplicate Substring (1044), Longest Common Subpath (1923).
**Інше:** Encode/Decode Strings (271), String to Integer atoi (8), Longest Common Prefix (14).

**Далі:** [14_bit_math.md](14_bit_math.md) — бітові трюки та математичні алгоритми.

> ⚠️ Rabin-Karp потребує перевірки рядків при збігу хешів (колізії). У проді — вбудовані `find`/`in` (оптимізовані в C), а не саморобний KMP.
