# Індекс відповідей — Node.js / JavaScript / TypeScript

Кожна відповідь за **Принципом Сходів**: L1 Junior → L2 Middle → L3 Senior.
Сучасний стек: Node.js 20+, ES2022+, TypeScript 5+. Без галюцинацій — спірні деталі рушіїв позначені `⚠️`.

| № | Файл | Тема | Питань |
|---|------|------|--------|
| 01 | [01_nodejs_junior.md](01_nodejs_junior.md) | Node.js — Junior | 16 |
| 02 | [02_express_junior.md](02_express_junior.md) | Express.js — Middleware (Junior) | 4 |
| 03 | [03_javascript.md](03_javascript.md) | JavaScript (async, var/let/const, this, Promise, Set/Map) | 19 |
| 04 | [04_web_html_css.md](04_web_html_css.md) | WEB (CORS, DNS, REST) + HTML/CSS (центрування, схлопування) | 9 |
| 05 | [05_html_script_practical.md](05_html_script_practical.md) | HTML/Script (defer/async, tabindex) + практичні JS-задачі | 12 |
| 06 | [06_nodejs_middle_q66_q83.md](06_nodejs_middle_q66_q83.md) | Node.js Middle/Senior: concurrency, пам'ять, модулі, libuv, кеш | 18 |
| 07 | [07_nodejs_middle_q84_q96.md](07_nodejs_middle_q84_q96.md) | Node.js Middle/Senior: middleware, EventEmitter, стрими, сигнали, pino | 13 |
| 08 | [08_typescript.md](08_typescript.md) | TypeScript: типи, generics, narrowing, utility/mapped/conditional, discriminated unions | 20 |
| 09 | [09_react.md](09_react.md) | React: компоненти, Hooks, Context API, оптимізація, Vite, Shadcn UI | 20 |
| 10 | [10_javascript_advanced.md](10_javascript_advanced.md) | JS/Node Advanced: замикання, прототипи, currying, generators, Proxy, coercion, Buffer, memory leaks | 20 |

## Блок 01 — зміст (швидка навігація)
1. Що таке Node.js
2. Переваги та недоліки Node.js
3. Для яких завдань Node.js не підходить (CPU-bound)
4. Головні компоненти (V8, libuv, core modules)
5. Як один потік обробляє багато запитів (event loop + non-blocking I/O)
6. Кілька потоків (worker_threads, child_process, cluster)
7. Інтерпретація чи компіляція (V8 JIT: Ignition + TurboFan)
8. Читання великих файлів (streams, backpressure)
9. libuv і V8 (призначення кожного)
10. Microtasks vs Macrotasks (+ process.nextTick)
11. Що таке stream
12. Види стримів (Readable/Writable/Duplex/Transform)
13. Event loop (фази, як працює)
14. Логування і моніторинг (pino, event loop delay)
15. Моноліт vs мікросервіс
16. `string` vs `String` (примітив vs обгортка, autoboxing)

## Блок 02 — зміст (швидка навігація)
17. Для чого middleware (cross-cutting, Chain of Responsibility)
18. Перехід між middleware (`next()`, `next(err)`, async-пастка)
19. Пріоритизація middleware (порядок реєстрації)
20. Організація error handler (4 аргументи, централізація)

## Блок 03 — зміст (швидка навігація)
21. Асинхронність і асинхронний код
22. `var` / `let` / `const` (scope, hoisting, TDZ)
23. Відкласти виконання (setTimeout/Interval, debounce)
24. Способи оголошення функції
25. Анонімна функція
26. IIFE (самовиклик)
27. Function expression vs declaration (hoisting)
28. Фільтрація масиву (`filter`)
29. Видалення елемента масиву/об'єкта (splice/delete/immutable)
30. Тип `void` (JS-оператор vs TS-тип)
31. `super()` (наслідування класів)
32. `this` (динамічний контекст, arrow, bind)
33. `NaN` (Number.isNaN, IEEE 754)
34. NPM та аналоги
35. NPM vs Yarn/pnpm
36. Promise API (all/allSettled/race/any)
37. HTTP request/response (fetch-специфіка)
38. `Set` і `Map` (vs Object, WeakMap)
39. `&&` / `||` / `??` (nullish coalescing, short-circuit)

## Блок 04 — зміст (швидка навігація)
46. CORS (Same-Origin Policy, preflight)
47. Як отримати CORS-помилку (діагностика)
48. HTTP-методи RESTful/CRUD
49. DNS (резолюція, типи записів)
50. Центрування елемента (flex/grid/absolute)
51. Селектори атрибутів (`[href$=".com"]`) + приховування
52. Фіксація кліку через HTML+CSS (checkbox hack)
53. Схлопування (margin collapsing)
54. Відстань між елементами (⚠️ обрізане — потрібен код)

> Питання 40–45 пропущено в нумерації користувача.

## Блок 10 — зміст (JS/Node Advanced)
1. Замикання (closures) · 2. Прототипне наслідування (`__proto__` vs `prototype`) · 3. Оператор `new` (4 кроки) · 4. Debounce vs Throttle · 5. Currying та partial application · 6. Memoization · 7. Generators та iterators · 8. Symbols · 9. Proxy та Reflect · 10. `==` vs `===` та coercion · 11. Shallow vs deep copy (`structuredClone`) · 12. Event delegation/bubbling/capturing · 13. Immutability (`Object.freeze`) · 14. map/filter/reduce + чейнінг · 15. Array мутуючі vs немутуючі + `sort()`-пастка · 16. Обробка помилок · 17. Spread/rest/destructuring · 18. Buffer та бінарні дані · 19. `nextTick` vs `setImmediate` vs `setTimeout` · 20. Витоки пам'яті

## Блок 06 — зміст (Node.js Middle/Senior 66–83)
66. Переваги Node.js проти інших технологій
67. Коли кілька процесів/потоків
68. Паралельне vs асинхронне (на серверах)
69. Типи асинхронних операцій
70. Які модулі Node знаєте
71. Операційні помилки vs помилки програміста
72. Сервіси моніторингу й логування
73. libuv та його складові
74. Шаблони розподілених транзакцій (2PC/Saga)
75. Контроль пам'яті програмно (WeakRef, ліміти)
76. Garbage Collector (V8, generational)
77. Витік пам'яті та запобігання
78. Дебаг heap out of memory (snapshots)
79. Налаштування кешування (in-memory/Redis/HTTP)
80. child_process vs worker_threads vs cluster
81. ES modules vs CommonJS
82. EventEmitter (node:events)
83. Скільки ядер за замовчуванням (одне)

## Блок 07 — зміст (Node.js Middle/Senior 84–96)
84. Middleware — чому окремо від коду сервісу
85. EventEmitter (стисло)
86. Призначення package.json
87. Читання великого файлу (300MB → стрим)
88. Цикл подій (event loop, фази)
89. Thread Pool / Worker Pool (libuv, 4 потоки)
90. SIGTERM vs SIGINT (graceful shutdown)
91. Backpressure у стримах
92. PassThrough і pipe/pipeline
93. Події data/end/error/finish
94. Обробка помилок у стримах (pipeline > pipe)
95. Приклади стримів різних типів
96. pino (structured logging)

## Блок 05 — зміст (швидка навігація)
54. Відстань між елементами (повна задача: block 25px / flex)
55. `<script>` перед `</body>` vs у `<head>`
56. Атрибути `defer` і `async`
57. `tabindex` (доступність, фокус)
58. Число кратне 11 (`% 11 === 0`)
59. Копія масиву без посилання (spread, shallow vs deep)
60. `delete trees[3]` → 5, undefined (sparse array)
61. Масив без дублікатів + лише дублікати (Set)
62. Деструктуризація вкладеного об'єкта (дефолти)
63. Declaration vs Expression (+ syntax error у задачі)
64. Опціональний ланцюжок `?.`
65. Асинхронний map об'єкта (Promise.all + fromEntries)
