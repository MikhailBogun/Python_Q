# Індекс відповідей

Кожна відповідь розкрита за **Принципом Сходів**: L1 Junior → L2 Middle → L3 Senior.

| № | Файл | Тема | Питань |
|---|------|------|--------|
| 01 | [01_general_cs_web.md](01_general_cs_web.md) | Загальне з Computer Science та Web Development | 23 |
| 02 | [02_python.md](02_python.md) | Python (мова, типи, ООП, async, декоратори, колекції) | 30 |
| 03 | [03_databases.md](03_databases.md) | Бази даних (SQL у Python: DB-API, транзакції, JOIN, raw SQL) | 5 |
| 04 | [04_algorithms.md](04_algorithms.md) | Алгоритми (Big-O, сортування, лінійна складність) | 4 |
| 05 | [05_middle_architecture.md](05_middle_architecture.md) | Middle-level: архітектура, системи, практика | 10 |
| 06 | [06_python_advanced.md](06_python_advanced.md) | Python advanced (async, пам'ять, GC, slots, typing) | 11 |
| 07 | [07_db_devops_ds.md](07_db_devops_ds.md) | БД поглиблено, Frontend, DevOps, Linux, Data Science | 10 |
| 08 | [08_python_senior_systems.md](08_python_senior_systems.md) | Python Senior + розподілені системи, низькорівневе, пам'ять | 9 |

**Разом: 102 питання у 8 блоках.**

---

## 📚 Поглиблений курс алгоритмів

Окрема тека [algorithms/](algorithms/) — повний курс «всі алгоритми з прикладами на Python», 14 тем + дорожня карта:

| № | Файл | Тема |
|---|------|------|
| — | [algorithms/README.md](algorithms/README.md) | Дорожня карта + майстер-шпаргалка Big-O + гайд патернів |
| 01 | [algorithms/01_complexity.md](algorithms/01_complexity.md) | Аналіз складності (Big-O, Master theorem, amortized) |
| 02 | [algorithms/02_sorting.md](algorithms/02_sorting.md) | Сортування (всі алгоритми) |
| 03 | [algorithms/03_searching.md](algorithms/03_searching.md) | Пошук (binary search + варіанти) |
| 04 | [algorithms/04_recursion_backtracking.md](algorithms/04_recursion_backtracking.md) | Рекурсія та Backtracking |
| 05 | [algorithms/05_two_pointers_sliding_window.md](algorithms/05_two_pointers_sliding_window.md) | Two Pointers & Sliding Window |
| 06 | [algorithms/06_linked_lists.md](algorithms/06_linked_lists.md) | Зв'язані списки |
| 07 | [algorithms/07_stacks_queues.md](algorithms/07_stacks_queues.md) | Стеки та черги (monotonic stack) |
| 08 | [algorithms/08_trees.md](algorithms/08_trees.md) | Дерева (обходи, BST, trie) |
| 09 | [algorithms/09_heaps.md](algorithms/09_heaps.md) | Купи / Priority Queue |
| 10 | [algorithms/10_graphs.md](algorithms/10_graphs.md) | Графи (BFS/DFS, Dijkstra, Union-Find, MST) |
| 11 | [algorithms/11_dynamic_programming.md](algorithms/11_dynamic_programming.md) | Динамічне програмування |
| 12 | [algorithms/12_greedy.md](algorithms/12_greedy.md) | Жадібні алгоритми |
| 13 | [algorithms/13_strings.md](algorithms/13_strings.md) | Рядкові алгоритми (KMP, Rabin-Karp) |
| 14 | [algorithms/14_bit_math.md](algorithms/14_bit_math.md) | Бітові операції та математика |

## Блок 01 — зміст (швидка навігація)
1. Інженерія і процес розробки
2. Принципи програмування (DRY/KISS/YAGNI, SOLID)
3. Процедурна vs ООП парадигми
4. Принципи ООП (інкапсуляція, наслідування, поліморфізм)
5. Множинне наслідування (MRO, C3, diamond problem)
6. SDLC (6 етапів) + Agile vs Kanban
7. HTTP-методи (idempotency, safety)
8. HTTP request/response (структура, статус-коди)
9. Авторизація (AuthN vs AuthZ, JWT, sessions)
10. Cookies (HttpOnly, Secure, SameSite)
11. Вебвразливості (OWASP, SQLi, XSS, CSRF)
12. Класичні бази даних (SQL/NoSQL, ACID, CAP)
13. Як читати специфікацію (PEP8)
14. Взаємодія клієнт-сервер (DNS→TCP→TLS→HTTP)
15. Підходи до проєктування API (REST/GraphQL/gRPC)
16. Патерни програмування (GoF, antipatterns)
17. Acceptance Testing
18. Unit / Integration / API-тести (піраміда)
19. Як писати unit-тести (AAA, FIRST)
20. Best practices автотестів
21. Базові команди VCS (Git internals)
22. Як використовувати Git (workflow, merge vs rebase)
23. Хешування vs шифрування

## Блок 02 — зміст (швидка навігація)
24. Python — інтерпретується чи компілюється (байт-код, PVM, JIT)
25. Mutable vs immutable типи
26. Область видимості (LEGB, global/nonlocal)
27. Introspection
28. `is` vs `==` (кеш int, інтернування)
29. `__init__` vs `__new__`
30. Threads vs processes (GIL)
31. Види імпорту
32. Клас / ітератор / генератор
33. Метаклас і змінна циклу (late binding)
34. Ітератори vs генератори
35. `staticmethod` vs `classmethod`
36. Декоратори й контекстні менеджери
37. Comprehensions (list/dict/set)
38. Кілька декораторів на функцію
39. Декоратор із класу
40. Популярні пакети
41. Lambda-функції
42. `*args`, `**kwargs`
43. Exceptions, `try-except` (EAFP)
44. PEP (8, 484, ...)
45. Hello-world сервіс (FastAPI)
46. list vs tuple
47. Вбудовані колекції (list/set/dict)
48. Складність доступу до dict (хеш-таблиця)
49. Створення об'єкта (`__new__`/`__init__`)
50. Модуль `collections` та інші stdlib
51. Шаблонізатор (Jinja2)
52. Python і HTTP-сервер (WSGI/ASGI)
53. Віртуальне середовище

## Блок 03 — зміст (швидка навігація)
54. Базові методи роботи з SQL у Python (DB-API 2.0)
55. SQL-транзакція (ACID, ізоляція, MVCC)
56. Вибірка з агрегацією (GROUP BY / HAVING)
57. JOIN між таблицями і self-join
58. Запити в SQL без ORM (raw, параметризація)

## Блок 04 — зміст (швидка навігація)
59. Що таке алгоритми, Big-O notation
60. Базові алгоритми сортування (порівняння)
61. Bubble Sort (як працює, чому не використовують)
62. Лінійна складність сортування (counting/radix, межа n log n)

## Блок 05 — зміст (швидка навігація)
63. Орієнтація в *nix, скрипти/автоматизація
64. Багатопотоковість (concurrency vs parallelism, GIL)
65. Архітектура вебсервісів (шари, monolith vs microservices)
66. Навантажений вебзастосунок (Twitter/Instagram, fan-out)
67. Сервіс середнього розміру (redis/celery/кеш/логи/метрики)
68. Написати/задеплоїти/підтримувати мікросервіс (CI/CD, 12-factor)
69. Масштабування API (vertical/horizontal, bottleneck)
70. Code review (best practices, культура)
71. Абстрактна фабрика (патерн, навіщо)
72. Цикломатична складність

## Блок 06 — зміст (швидка навігація)
73. Async Python (event loop, корутини, під капотом)
74. Порівняння async web-фреймворків
75. Модель пам'яті Python (heap, аллокатор, посилання)
76. SQLAlchemy (Core/ORM) та альтернативи
77. Garbage collection і reference counting
78. Thread locals (+ contextvars для async)
79. `__slots__`
80. Передача аргументів (call by sharing)
81. Type annotations
82. Нижні підкреслення в іменах
83. Статичні аналізатори (Flake8, Pylint, Radon, Ruff)

## Блок 07 — зміст (швидка навігація)
84. SQL vs NoSQL (ACID vs BASE)
85. Оптимізація SQL-запитів (EXPLAIN, індекси, N+1)
86. Рівні ізоляції транзакцій (аномалії, MVCC)
87. Види індексів (B-tree, GIN, BRIN, composite, partial)
88. Вибір БД і рушіїв (PostgreSQL/MySQL, InnoDB, OLTP/OLAP)
89. Frontend: сучасний JS (Babel, Webpack, TS, ES)
90. DevOps (Docker, K8s: pod/node/deployment/service, Kibana)
91. Часова складність алгоритму (time complexity)
92. Поглиблений Linux (SSH, пакети, середовище, операції)
93. Data Science (NumPy, Pandas, векторизація, візуалізація)

## Блок 08 — зміст (швидка навігація)
94. `@property` (дескриптор даних, обчислювані атрибути)
95. Паралельний запуск Python (процеси/потоки/async/розподілено)
96. Робота зі stdlib (batteries included, трейдофи)
97. Задачі для метакласів (+ PEP 487 як простіша заміна)
98. Дескриптори (фундамент атрибутів, data vs non-data)
99. Знання інших мов (як подавати + порівняння концепцій)
100. Розподілені системи (CAP, consensus, реплікація, saga)
101. Низькорівневі особливості мов і фреймворків
102. Керування пам'яттю (refcount/GC/RAII/ownership)
