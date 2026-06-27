# 06. Зв'язані списки (Linked Lists)

> Тренують роботу з **вказівниками** — навичку, яку приховує Python list. Класика інтерв'ю: reverse, cycle detection, merge.

---

## L1 — Junior: інтуїція

**Аналогія — потяг із вагонів.** Кожен вагон (node) тримає **вантаж** (дані) і **зчіпку** до наступного вагона (`next`). Щоб дійти до 5-го вагона — пройди через 1→2→3→4→5 (немає «телепортації» за індексом, як у масиві).

```python
class ListNode:
    def __init__(self, val: int = 0, next: "ListNode | None" = None) -> None:
        self.val = val
        self.next = next

# 1 → 2 → 3 → None
head = ListNode(1, ListNode(2, ListNode(3)))
```

**Linked list vs масив:**
| | Масив (list) | Зв'язаний список |
|---|---|---|
| Доступ за індексом | O(1) | **O(n)** (треба пройти) |
| Вставка на початок | O(n) (зсув) | **O(1)** (переставив зчіпку) |
| Пам'ять | суцільна | розкидана (вузли + вказівники) |

---

## L2 — Middle: базові операції

### Обхід і друк
```python
def print_list(head: ListNode | None) -> None:
    values = []
    curr = head
    while curr:                  # поки не дійшли до None
        values.append(curr.val)
        curr = curr.next         # крок до наступного
    print(" → ".join(map(str, values)))
```

### Реверс списку (THE класична задача) — O(n), O(1) пам'ять
```python
def reverse_list(head: ListNode | None) -> ListNode | None:
    prev = None
    curr = head
    while curr:
        next_node = curr.next    # 1. ЗАПАМ'ЯТАТИ наступний (інакше втратимо!)
        curr.next = prev         # 2. РОЗВЕРНУТИ зчіпку назад
        prev = curr              # 3. posунути prev
        curr = next_node         # 4. посунути curr
    return prev                  # prev — новий head
```
**Візуалізація:** `None ← 1   2 → 3` (поступово розвертаємо кожну стрілку).

### Реверс рекурсивно
```python
def reverse_recursive(head: ListNode | None) -> ListNode | None:
    if head is None or head.next is None:    # база: порожній або один вузол
        return head
    new_head = reverse_recursive(head.next)  # розвернути хвіст
    head.next.next = head                    # наступний тепер вказує на нас
    head.next = None                         # ми стаємо кінцем
    return new_head
```

### Знайти середину (fast & slow pointers)
```python
def find_middle(head: ListNode | None) -> ListNode | None:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next         # повільний — 1 крок
        fast = fast.next.next    # швидкий — 2 кроки
    return slow                  # коли fast у кінці, slow — посередині
```

### Видалити N-й з кінця (за один прохід)
```python
def remove_nth_from_end(head: ListNode | None, n: int) -> ListNode | None:
    dummy = ListNode(0, head)    # dummy спрощує видалення head
    fast = slow = dummy
    for _ in range(n):           # fast на n кроків уперед
        fast = fast.next
    while fast.next:             # рухаємо обидва, поки fast не в кінці
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next   # пропустити (видалити) вузол
    return dummy.next
```

**Gotcha — dummy node:** «фіктивний» вузол перед head рятує від спецобробки видалення/вставки **на початку** списку. Класичний прийом, що прибирає купу `if head is None` перевірок.

---

## L3 — Senior: цикли, merge, складні маніпуляції

### Floyd's Cycle Detection (алгоритм «черепаха і заєць») — O(n), O(1)
Чи є цикл у списку? Швидкий і повільний вказівники: якщо є цикл — вони **зустрінуться** всередині.
```python
def has_cycle(head: ListNode | None) -> bool:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next         # 1 крок
        fast = fast.next.next    # 2 кроки
        if slow is fast:         # зустрілись → цикл!
            return True
    return False                 # fast дійшов до None → циклу немає
```

**Знайти ПОЧАТОК циклу (математичний трюк):**
```python
def detect_cycle_start(head: ListNode | None) -> ListNode | None:
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:                     # зустріч
            slow = head                      # один — на початок
            while slow is not fast:          # обидва по 1 кроку
                slow = slow.next
                fast = fast.next
            return slow                      # точка зустрічі = початок циклу
    return None
```
**Чому працює:** математика — від голови до початку циклу `a`, від початку до зустрічі `b`. Можна довести, що `a = (довжина циклу) - b`, тому два вказівники по 1 кроку з head і з точки зустрічі зійдуться саме на початку циклу. Це питання люблять на senior-інтерв'ю.

### Злиття двох відсортованих списків — O(n+m)
```python
def merge_two_lists(l1: ListNode | None, l2: ListNode | None) -> ListNode | None:
    dummy = ListNode()
    tail = dummy
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 or l2         # причепити залишок
    return dummy.next
```

### Чому fast & slow настільки потужний
Один шаблон (`slow += 1, fast += 2`) розв'язує: середину, цикл, початок циклу, n-й з кінця, паліндром-список. Ідея — **різна швидкість** дає інформацію про структуру за **один прохід, O(1) пам'ять**. Альтернатива (зберегти всі вузли в set для пошуку циклу) — O(n) пам'ять.

### Трейдоф linked list vs масив у Python
**Важливо:** у Python **рідко** використовують власні linked lists у проді — `list` (динамічний масив) і `collections.deque` (двобічна черга на блоках) покривають потреби, та ще й із кращою локальністю кешу. Linked list виправданий, коли:
- Часті вставки/видалення **в середині** за відомим вузлом — O(1) проти O(n) у масиві.
- Не потрібен довільний доступ за індексом.

Але навіть тоді `deque` зазвичай кращий (O(1) з обох кінців + краща пам'ять). Тому linked list — це переважно **навчальна/інтерв'ю** структура в Python-світі (на відміну від C, де вони всюди). Цінність — **тренування вказівникового мислення**, що переноситься на дерева й графи.

### Gotcha — `is` vs `==` для вузлів
Порівнюй вузли через `is` (ідентичність об'єкта), а не `==` (значення). `slow is fast` перевіряє, що це **той самий вузол**, а не «однакові val» (блок основних питань п.28).

---

## 🎯 Задачі для практики
- Reverse Linked List (206), Reverse Linked List II (92).
- Linked List Cycle (141), Cycle II (142, початок циклу).
- Middle of the Linked List (876).
- Merge Two Sorted Lists (21), Merge k Sorted Lists (23, з купою — файл 09).
- Remove Nth Node From End (19).
- Palindrome Linked List (234, fast/slow + reverse).
- Reorder List (143), Add Two Numbers (2), Copy List with Random Pointer (138).

**Далі:** [07_stacks_queues.md](07_stacks_queues.md) — стеки, черги, monotonic stack.

> ⚠️ У реальному Python-коді бери `list`/`deque`, а не саморобний linked list. Цей файл — про патерни вказівників і підготовку до дерев/графів.
