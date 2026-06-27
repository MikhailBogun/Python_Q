# 09. Купи / Priority Queue (Heaps)

> Структура для «найбільшого/найменшого зараз» за O(log n). Основа top-K, Dijkstra (файл 10), планувальників, медіани потоку.

---

## L1 — Junior: інтуїція

**Аналогія — приймальня лікарні за терміновістю.** Неважливо, хто прийшов першим — спочатку приймають **найтерміновішого**. **Priority Queue** завжди віддає елемент із найвищим пріоритетом (найменший/найбільший), не зберігаючи повний порядок решти.

**Heap (купа)** — реалізація priority queue. У Python — модуль `heapq` (**min-heap**: найменший зверху).

```python
import heapq

heap: list[int] = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 1)
heapq.heappush(heap, 3)
print(heap[0])              # 1 — найменший завжди на вершині, O(1)
print(heapq.heappop(heap))  # 1 — витягти найменший, O(log n)
```

---

## L2 — Middle: операції та патерни

### Базові операції
```python
import heapq

nums = [5, 1, 3, 8, 2]
heapq.heapify(nums)              # O(n) — перетворити список на купу НА МІСЦІ
heapq.heappush(nums, 0)          # O(log n) — додати
smallest = heapq.heappop(nums)   # O(log n) — витягти найменший
peek = nums[0]                   # O(1) — подивитись найменший (не виймаючи)

# Зручні готові функції:
heapq.nlargest(3, [5,1,8,3,9])   # [9, 8, 5] — 3 найбільші
heapq.nsmallest(3, [5,1,8,3,9])  # [1, 3, 5] — 3 найменші
```

### Max-heap трюк (Python має лише min-heap!)
Інвертуй знак — і min-heap працює як max-heap:
```python
max_heap: list[int] = []
for x in [5, 1, 8, 3]:
    heapq.heappush(max_heap, -x)     # кладемо з мінусом
largest = -heapq.heappop(max_heap)   # 8 — найбільший (інвертуємо назад)
```

### Top-K elements — головний патерн
```python
def k_largest(nums: list[int], k: int) -> list[int]:
    """K найбільших через min-heap розміру k — O(n log k)."""
    heap: list[int] = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)          # викидаємо найменший → лишаються k найбільших
    return heap                          # купа з k найбільших

def kth_largest(nums: list[int], k: int) -> int:
    return heapq.nlargest(k, nums)[-1]   # або min-heap розміру k → heap[0]
```
**Ключова ідея:** для «K найбільших» тримай **min-heap розміру K** (не max-heap!). Найменший із K-найбільших — на вершині, легко витіснити. O(n log k) < O(n log n) повного сортування.

### Heap із кортежів (пріоритет + дані)
```python
tasks: list[tuple[int, str]] = []
heapq.heappush(tasks, (2, "помити посуд"))
heapq.heappush(tasks, (1, "терміново: пожежа"))    # менший пріоритет = вищий
heapq.heappush(tasks, (3, "колись"))
priority, task = heapq.heappop(tasks)              # (1, "терміново: пожежа")
```

**Gotcha:** при рівних пріоритетах heap порівнює **другий** елемент кортежу. Якщо це непорівнюваний об'єкт (напр. dict) → `TypeError`. Рішення: додай унікальний лічильник `(priority, count, item)` як tie-breaker.

---

## L3 — Senior: під капотом, два патерни, трейдофи

### Як heap влаштований (binary heap)
Heap — **повне бінарне дерево**, що зберігається в **масиві** (без вказівників!):
- Корінь — `arr[0]` (мінімум).
- Діти вузла `i`: `arr[2i+1]` і `arr[2i+2]`.
- Батько `i`: `arr[(i-1)//2]`.

**Інваріант min-heap:** батько ≤ обидва діти (тому мінімум завжди в корені).

Операції тримають інваріант через **«просіювання»**:
- `push`: додати в кінець → **sift up** (міняти з батьком, поки менший) → O(log n).
- `pop`: взяти корінь, перенести останній у корінь → **sift down** (міняти з меншим дитям) → O(log n).

### Чому heapify — O(n), а не O(n log n)
Наївно: n вставок × O(log n) = O(n log n). Але `heapify` (Floyd's build-heap) йде **знизу вгору** (sift-down від останнього батька). Більшість вузлів — на нижніх рівнях із малою висотою → математична сума дає **O(n)**, а не O(n log n). Тонкий, але улюблений senior-факт.

### Два потужні патерни

**1. K-way merge (злити k відсортованих списків) — файл 06**
```python
def merge_k_sorted(lists: list[list[int]]) -> list[int]:
    heap: list[tuple[int, int, int]] = []    # (значення, № списку, № елемента)
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))
    result = []
    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        if elem_idx + 1 < len(lists[list_idx]):
            nxt = lists[list_idx][elem_idx + 1]
            heapq.heappush(heap, (nxt, list_idx, elem_idx + 1))
    return result
# O(N log k), де N — усього елементів, k — кількість списків
```

**2. Two heaps — медіана з потоку (LC 295)**
```python
class MedianFinder:
    def __init__(self) -> None:
        self.small: list[int] = []   # max-heap (з мінусом) — менша половина
        self.large: list[int] = []   # min-heap — більша половина

    def add_num(self, num: int) -> None:
        heapq.heappush(self.small, -num)
        heapq.heappush(self.large, -heapq.heappop(self.small))   # балансування
        if len(self.large) > len(self.small):                    # розміри ~рівні
            heapq.heappush(self.small, -heapq.heappop(self.large))

    def find_median(self) -> float:
        if len(self.small) > len(self.large):
            return -self.small[0]
        return (-self.small[0] + self.large[0]) / 2
# add: O(log n), median: O(1). Дві купи тримають «середину» доступною.
```

### Трейдофи: heap vs sorted vs інше
| Потреба | Структура | Чому |
|---|---|---|
| «найменший/найбільший зараз», динамічно | **heap** | O(log n) push/pop, O(1) peek |
| K найбільших із n | **heap розміру k** | O(n log k) < O(n log n) |
| повний відсортований порядок | **sorted()** | heap не дає повного порядку дешево |
| top-K **один раз** статично | `heapq.nlargest` або quickselect | quickselect O(n) average |

**Heap vs повне сортування для top-K:** sort — O(n log n), heap розміру k — O(n log k). Для k ≪ n (топ-10 з мільйона) heap значно швидший. Для k ≈ n — простіше відсортувати.

**Heap vs quickselect:** для **k-го** елемента (не всіх k) quickselect дає **O(n) average** (краще за heap O(n log k)), але O(n²) worst і руйнує вхід. Heap — стабільніше й працює на **потоці** (дані надходять поступово), де quickselect неможливий.

### Чому heap не дає O(1) пошук довільного елемента
Heap впорядкований лише «вертикально» (батько-дитя), не «горизонтально». Тому знайти/видалити **довільний** елемент — O(n) (немає індексу). Для цього потрібен інший інструмент (dict + heap, або балансоване дерево). Heap оптимізований **лише** під «дай екстремум».

---

## 🎯 Задачі для практики
- Kth Largest Element in Array (215), Kth Largest in Stream (703).
- Top K Frequent Elements (347), K Closest Points to Origin (973).
- Merge k Sorted Lists (23), Find Median from Data Stream (295, two heaps).
- Task Scheduler (621), Reorganize String (767).
- Sliding Window Median (480), IPO (502), Meeting Rooms II (253).

**Далі:** [10_graphs.md](10_graphs.md) — вершина складності: BFS/DFS, Dijkstra, MST, Union-Find.

> ⚠️ `heapq` — лише min-heap. Для max-heap інвертуй знаки. При кортежах став tie-breaker, щоб уникнути порівняння непорівнюваних об'єктів.
