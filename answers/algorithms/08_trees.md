# 08. Дерева (Trees)

> Ієрархічні структури. Обходи (traversals) — основа сотень задач. BST дає O(log n) пошук. Trie — для рядків/префіксів. Потрібна рекурсія (файл 04).

---

## L1 — Junior: інтуїція

**Аналогія — генеалогічне дерево / структура папок.** Є **корінь** (root), у кожного вузла є **діти** (children), вузол без дітей — **листок** (leaf). Дерево росте «вниз» від кореня.

**Бінарне дерево** — кожен вузол має ≤ 2 дітей (left, right).

```python
class TreeNode:
    def __init__(self, val: int = 0,
                 left: "TreeNode | None" = None,
                 right: "TreeNode | None" = None) -> None:
        self.val = val
        self.left = left
        self.right = right

#       1
#      / \
#     2   3
#    / \
#   4   5
root = TreeNode(1, TreeNode(2, TreeNode(4), TreeNode(5)), TreeNode(3))
```

**Терміни:** висота (height) — найдовший шлях від кореня до листка; глибина (depth) — відстань вузла від кореня; рівень (level).

---

## L2 — Middle: обходи (traversals)

### DFS — три порядки (рекурсивно)
```python
def inorder(node: TreeNode | None, result: list[int]) -> None:
    """Left → Root → Right. Для BST дає ВІДСОРТОВАНИЙ порядок!"""
    if node:
        inorder(node.left, result)
        result.append(node.val)          # корінь МІЖ піддеревами
        inorder(node.right, result)

def preorder(node: TreeNode | None, result: list[int]) -> None:
    """Root → Left → Right. Для копіювання/серіалізації дерева."""
    if node:
        result.append(node.val)          # корінь ПЕРШИЙ
        preorder(node.left, result)
        preorder(node.right, result)

def postorder(node: TreeNode | None, result: list[int]) -> None:
    """Left → Right → Root. Для видалення/обчислення знизу вгору."""
    if node:
        postorder(node.left, result)
        postorder(node.right, result)
        result.append(node.val)          # корінь ОСТАННІЙ
```
Для дерева вище: inorder=[4,2,5,1,3], preorder=[1,2,4,5,3], postorder=[4,5,2,3,1].

### BFS — обхід по рівнях (level order) з чергою
```python
from collections import deque

def level_order(root: TreeNode | None) -> list[list[int]]:
    if not root:
        return []
    result: list[list[int]] = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):      # обробляємо ВЕСЬ поточний рівень
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result
# [[1], [2,3], [4,5]]
```

### Базові рекурсивні задачі
```python
def max_depth(root: TreeNode | None) -> int:
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))

def is_same_tree(p: TreeNode | None, q: TreeNode | None) -> bool:
    if not p and not q:
        return True
    if not p or not q or p.val != q.val:
        return False
    return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)

def invert_tree(root: TreeNode | None) -> TreeNode | None:
    if root:
        root.left, root.right = invert_tree(root.right), invert_tree(root.left)
    return root
```

**Gotcha:** база рекурсії для дерев — `if not node: return ...`. Забудеш — `AttributeError` на `None.left`.

---

## L3 — Senior: BST, балансування, Trie, ітеративні обходи

### Binary Search Tree (BST) — O(log n) пошук
**Інваріант:** ліве піддерево < вузол < праве піддерево. Дає швидкий пошук/вставку (якщо збалансоване).
```python
def search_bst(root: TreeNode | None, target: int) -> TreeNode | None:
    while root:
        if target == root.val:
            return root
        root = root.left if target < root.val else root.right   # йдемо в один бік
    return None

def insert_bst(root: TreeNode | None, val: int) -> TreeNode:
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = insert_bst(root.left, val)
    else:
        root.right = insert_bst(root.right, val)
    return root

def is_valid_bst(root: TreeNode | None) -> bool:
    def validate(node: TreeNode | None, low: float, high: float) -> bool:
        if not node:
            return True
        if not (low < node.val < high):     # порушення меж
            return False
        return (validate(node.left, low, node.val) and
                validate(node.right, node.val, high))
    return validate(root, float("-inf"), float("inf"))
```

**Ключовий факт:** **inorder обхід BST дає відсортовану послідовність**. Багато BST-задач (kth smallest, validate) спираються на це.

### Чому BST вироджується і навіщо балансування
Незбалансоване BST (вставка відсортованих даних) вироджується у **зв'язаний список** → O(n) замість O(log n):
```
вставка 1,2,3,4,5 → 1→2→3→4→5 (всі праворуч) = O(n) пошук!
```
Тому в проді — **самобалансовані** дерева: **AVL** (строго збалансоване, швидкий пошук), **Red-Black** (слабше, швидші вставки — використовує `std::map` у C++, TreeMap у Java). Балансування через **ротації** при вставці/видаленні тримає висоту O(log n).

**У Python:** немає вбудованого збалансованого BST. Для впорядкованих структур — `sortedcontainers` (сторонній, на B-tree-подібній структурі) або `dict`/`heapq` залежно від задачі. dict дає O(1), але не зберігає порядок ключів за значенням.

### Ітеративний inorder (без рекурсії, явний стек)
```python
def inorder_iterative(root: TreeNode | None) -> list[int]:
    result, stack, curr = [], [], root
    while curr or stack:
        while curr:                      # йдемо максимально ліворуч
            stack.append(curr)
            curr = curr.left
        curr = stack.pop()               # обробляємо вузол
        result.append(curr.val)
        curr = curr.right                # переходимо праворуч
    return result
```
Навіщо: глибокі дерева (>1000) → рекурсія впирається в ліміт (файл 04). **Morris traversal** дає inorder за O(1) пам'ять (без стека) через тимчасові threading-зв'язки — senior-рівень.

### Trie (префіксне дерево) — для рядків/автодоповнення
```python
class Trie:
    def __init__(self) -> None:
        self.children: dict[str, "Trie"] = {}
        self.is_word = False

    def insert(self, word: str) -> None:
        node = self
        for ch in word:
            node = node.children.setdefault(ch, Trie())
        node.is_word = True

    def search(self, word: str) -> bool:
        node = self._find(word)
        return node is not None and node.is_word

    def starts_with(self, prefix: str) -> bool:
        return self._find(prefix) is not None

    def _find(self, s: str) -> "Trie | None":
        node = self
        for ch in s:
            if ch not in node.children:
                return None
            node = node.children[ch]
        return node
```
**Trie** дає пошук слова/префікса за **O(довжини слова)**, незалежно від кількості слів. Застосування: автодоповнення, перевірка орфографії, IP-роутинг, словники. Трейдоф: швидкий префіксний пошук ↔ велика витрата пам'яті (вузол на кожен символ).

### Складності
| Операція | BST збалансоване | BST вироджене | Trie |
|---|---|---|---|
| Пошук | O(log n) | O(n) | O(довжина) |
| Вставка | O(log n) | O(n) | O(довжина) |
| Обхід усіх | O(n) | O(n) | O(всі символи) |

Обхід будь-якого дерева — **O(n)** (відвідуємо кожен вузол раз), пам'ять — O(h) на рекурсію, де h — висота (O(log n) збалансоване, O(n) вироджене).

### Трейдоф DFS vs BFS на деревах
- **DFS** (рекурсія/стек): O(h) пам'ять — добре для глибоких вузьких дерев; природний для «шляхів», «знизу вгору».
- **BFS** (черга): O(ширина) пам'ять — добре для «найближчого», «рівнів», «мінімальної глибини». На широких деревах їсть більше пам'яті (останній рівень ≈ половина вузлів).

---

## 🎯 Задачі для практики
**Обходи:** Binary Tree Inorder/Preorder/Postorder (94, 144, 145), Level Order (102), Zigzag Level Order (103).
**Властивості:** Maximum Depth (104), Same Tree (100), Symmetric Tree (101), Invert Tree (226), Balanced Binary Tree (110), Diameter (543).
**BST:** Validate BST (98), Kth Smallest (230), Lowest Common Ancestor (235/236), Convert Sorted Array to BST (108).
**Складні:** Serialize/Deserialize (297), Path Sum (112/113), Binary Tree Maximum Path Sum (124).
**Trie:** Implement Trie (208), Word Search II (212), Add and Search Word (211).

**Далі:** [09_heaps.md](09_heaps.md) — купи та пріоритетні черги.

> ⚠️ Python не має вбудованого збалансованого BST. Для впорядкованих колекцій з O(log n) — `sortedcontainers` (сторонній). Глибокі дерева → ітеративні обходи (ліміт рекурсії).
