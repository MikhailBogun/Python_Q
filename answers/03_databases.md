# Блок 3. Бази даних (SQL у Python)

> Формат: **L1 Junior** → **L2 Middle** → **L3 Senior**.
> Приклади під стек проєкту: **PostgreSQL** + `psycopg` (sync) / `asyncpg` (async), вихід на SQLAlchemy / SQLModel.

**Спільна схема для прикладів** (використовується в усіх питаннях):
```sql
users(id, name, email, created_at)
orders(id, user_id → users.id, amount, status, created_at)
employees(id, name, manager_id → employees.id, department_id → departments.id, salary)
departments(id, name)
```

---

## 54. Базові методи роботи з SQL-базою в Python

### L1 — Junior
**Аналогія — телефонна розмова з базою:**
1. **Подзвонити** (`connect`) — встановити з'єднання.
2. **Взяти слухавку** (`cursor`) — об'єкт, через який «говоримо».
3. **Сказати, що треба** (`execute` — надіслати SQL).
4. **Вислухати відповідь** (`fetch` — забрати рядки).
5. **Підтвердити зміни** (`commit`).
6. **Покласти слухавку** (`close`).

### L2 — Middle
Усі sync-драйвери в Python дотримуються **DB-API 2.0 (PEP 249)** — єдиний інтерфейс, тому код схожий для PostgreSQL/MySQL/SQLite.

```python
import psycopg   # psycopg3 — драйвер PostgreSQL

# Context manager сам закриває з'єднання й курсор
with psycopg.connect("postgresql://user:pass@localhost:5432/mydb") as conn:
    with conn.cursor() as cur:
        # ✅ Параметризований запит — %s, НЕ f-string!
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
            ("Іван", "ivan@example.com"),
        )
        new_id = cur.fetchone()[0]

        cur.execute("SELECT id, name FROM users WHERE id = %s", (new_id,))
        row = cur.fetchone()        # один рядок → кортеж
        # cur.fetchall()            # усі рядки → list[tuple]
        # cur.fetchmany(100)        # порція

    conn.commit()                   # зафіксувати транзакцію
```

**Ключові методи DB-API:**
| Метод | Призначення |
|---|---|
| `connect()` | з'єднання |
| `conn.cursor()` | курсор |
| `cur.execute(sql, params)` | один запит |
| `cur.executemany(sql, seq)` | багато наборів параметрів (bulk) |
| `cur.fetchone() / fetchmany(n) / fetchall()` | читання результату |
| `conn.commit() / conn.rollback()` | фіксація / відкат |
| `conn.close()` | закриття |

**Best practices:**
- **Завжди параметризація** (`%s` / `?`), ніколи не конкатенуй SQL — інакше SQL injection (блок 1, п.11).
- `with` для conn/cursor — гарантований cleanup.
- `RETURNING id` (PostgreSQL) — забрати згенерований id одразу.
- Для зручності — `row_factory` (dict-курсор), щоб отримувати `dict`, а не кортеж.

**Gotcha:** psycopg/postgres **не в autocommit** за замовчуванням — без `commit()` зміни **відкотяться** при закритті з'єднання. Часта помилка новачка: «вставив, а в базі нема».

### L3 — Senior
**Рівні абстракції** — Senior свідомо обирає під задачу:
1. **DB-API (raw)** — `psycopg`/`asyncpg`: повний контроль над SQL, максимальна швидкість, але вручну мапиш рядки в об'єкти.
2. **SQLAlchemy Core** — Query Builder: SQL виражається Python-об'єктами (типобезпечно, без рядків), без повного ORM.
3. **ORM (SQLAlchemy / SQLModel / Django)** — об'єкти ↔ рядки автоматично, lazy loading, identity map, але overhead і ризик N+1.

**Connection pooling — критично для прода:** відкриття TCP+TLS+auth з'єднання до Postgres коштує мілісекунди й ресурси сервера. Пул (`psycopg_pool`, SQLAlchemy `QueuePool`, зовнішній **PgBouncer**) **перевикористовує** з'єднання → у рази менша латентність і захист від вичерпання `max_connections` Postgres.

**Async:** `asyncpg` (або psycopg3 async) не блокує event loop — `await cur.execute(...)`. Для FastAPI це обов'язково: блокуючий `psycopg.connect` у `async def` зупинить увесь loop (блок 2, п.30/52).

**Трейдоф raw vs ORM:** raw — швидкість і контроль ціною бойлерплейту й ризику SQLi при недбалості; ORM — продуктивність розробки й безпека ціною overhead, «магії» та N+1. Senior часто **гібрид**: ORM для CRUD, raw/Core для складних аналітичних запитів.

> ⚠️ Плейсхолдери залежать від драйвера (`paramstyle`): psycopg — `%s`, sqlite3/asyncpg — `?`/`$1`. Звіряй із docs драйвера.

---

## 55. Що таке SQL-транзакція?

### L1 — Junior
**Аналогія — переказ грошей.** Зняти з рахунку А і додати на рахунок Б — це **дві дії, що мають статися разом**. Якщо світло вимкнули після зняття, але до зарахування — гроші зникли. **Транзакція** гарантує: або **обидві** дії, або **жодної**. «Все або нічого».

```sql
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;     -- якщо тут помилка → ROLLBACK, гроші не зникли
```

### L2 — Middle
Транзакція гарантує **ACID**:
- **Atomicity** — усе або нічого.
- **Consistency** — БД переходить з одного валідного стану в інший (не порушує constraints).
- **Isolation** — паралельні транзакції не заважають одна одній.
- **Durability** — після `COMMIT` дані переживуть збій (записані на диск).

У Python:
```python
with psycopg.connect(dsn) as conn:
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE accounts SET balance = balance - 100 WHERE id = 1")
            cur.execute("UPDATE accounts SET balance = balance + 100 WHERE id = 2")
        conn.commit()          # обидва UPDATE разом
    except Exception:
        conn.rollback()        # будь-яка помилка → відкат обох
        raise
```

**Savepoints** — вкладені «контрольні точки» всередині транзакції:
```sql
SAVEPOINT sp1;
  -- ризикована операція
ROLLBACK TO sp1;   -- відкат лише до точки, решта транзакції жива
```

**Gotcha:** довгі транзакції тримають **блокування (locks)** і заважають іншим → завжди тримай транзакцію **короткою**. Не роби HTTP-запити / `time.sleep` усередині відкритої транзакції.

### L3 — Senior
**Рівні ізоляції** (ANSI SQL, від слабшого до сильнішого) і аномалії, які вони прибирають:
| Рівень | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| Read Uncommitted | ✅ можливий | ✅ | ✅ |
| Read Committed | ❌ | ✅ | ✅ |
| Repeatable Read | ❌ | ❌ | ✅* |
| Serializable | ❌ | ❌ | ❌ |

**PostgreSQL-специфіка (важливо):**
- Дефолт — **Read Committed**.
- Read Uncommitted у PG **= Read Committed** (брудного читання нема ніколи, бо MVCC).
- **Repeatable Read у PG** прибирає й phantom reads (строгіше за стандарт) завдяки snapshot-ізоляції.
- **Serializable** реалізований як **SSI** (Serializable Snapshot Isolation) — може кинути `serialization_failure`, і транзакцію треба **повторити**.

**MVCC (Multi-Version Concurrency Control)** — ядро Postgres: замість блокувань на читання БД тримає **кілька версій рядка**. Кожна транзакція бачить «знімок» (snapshot) на момент старту → читачі не блокують письменників і навпаки. Ціна: «мертві» версії рядків (dead tuples) → потрібен **VACUUM** для очищення.

**Трейдоф ізоляція ↔ конкурентність:** сильніша ізоляція = менше аномалій, але більше блокувань/відкатів і нижча пропускна здатність. Senior обирає рівень під бізнес-інваріант: фінанси/інвентар з конкуренцією → Serializable (з retry-логікою); звичайний CRUD → Read Committed достатньо.

**Оптимістичне vs песимістичне блокування:**
- **Песимістичне** — `SELECT ... FOR UPDATE` (захопити рядок наперед).
- **Оптимістичне** — version-колонка, перевірка при `UPDATE ... WHERE version = N` (для low-contention).

> ⚠️ Реалізація рівнів ізоляції сильно різниться між СУБД (PG ≠ MySQL/InnoDB ≠ Oracle). Звіряй з docs конкретної бази.

---

## 56. Вибірка з простою агрегацією

### L1 — Junior
**Аналогія — каса супермаркету.** Агрегація — це коли замість «покажи кожен товар» питаєш «скільки всього товарів?», «яка загальна сума?», «середній чек?». БД **згортає** багато рядків в одне число.

```sql
SELECT COUNT(*) FROM orders;          -- скільки замовлень
SELECT SUM(amount) FROM orders;       -- загальна сума
SELECT AVG(amount) FROM orders;       -- середнє
```

### L2 — Middle
**Агрегатні функції:** `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`.

**`GROUP BY`** — рахувати не по всій таблиці, а **по групах**:
```sql
-- Сума й кількість замовлень ПО КОЖНОМУ користувачу
SELECT
    user_id,
    COUNT(*)        AS orders_count,
    SUM(amount)     AS total_spent,
    AVG(amount)     AS avg_order
FROM orders
WHERE status = 'paid'           -- фільтр РЯДКІВ до групування
GROUP BY user_id
HAVING SUM(amount) > 1000       -- фільтр ГРУП після групування
ORDER BY total_spent DESC
LIMIT 10;
```

З Python:
```python
cur.execute("""
    SELECT user_id, COUNT(*) AS cnt, SUM(amount) AS total
    FROM orders
    WHERE status = %s
    GROUP BY user_id
    HAVING SUM(amount) > %s
""", ("paid", 1000))
for user_id, cnt, total in cur.fetchall():
    ...
```

**Gotcha — `WHERE` vs `HAVING`** (улюблене питання):
- `WHERE` фільтрує **рядки ДО** групування (не може використовувати агрегати).
- `HAVING` фільтрує **групи ПІСЛЯ** агрегації (працює з `SUM`, `COUNT`).

**Gotcha 2:** усі неагрегатні колонки в `SELECT` мають бути в `GROUP BY` (PostgreSQL це **суворо** вимагає, MySQL історично дозволяв пропуск — джерело багів).

### L3 — Senior
**Порядок логічного виконання SQL** (не збігається з порядком написання!):
```
FROM → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```
Це пояснює, чому `WHERE` не бачить аліасів із `SELECT` (SELECT виконується пізніше) і чому `HAVING` може використовувати агрегати (після GROUP BY).

**`COUNT(*)` vs `COUNT(col)` vs `COUNT(DISTINCT col)`:**
- `COUNT(*)` — усі рядки (включно з тими, де `col IS NULL`).
- `COUNT(col)` — лише де `col IS NOT NULL` (агрегати **ігнорують NULL**).
- `COUNT(DISTINCT col)` — унікальні ненульові значення (дорожче — потрібне сортування/хешування).

**Продуктивність:** `GROUP BY` виконується через **HashAggregate** (хеш-таблиця груп, `O(n)`) або **GroupAggregate** (вимагає відсортованого входу, `O(n log n)`) — планувальник обирає за статистикою й наявністю індексів. Індекс на колонці групування/фільтрації може перетворити повний скан (`O(n)`) на index scan.

**Віконні функції (window functions)** — коли треба агрегат **без згортання рядків** (агрегат поряд із деталями):
```sql
SELECT user_id, amount,
       SUM(amount) OVER (PARTITION BY user_id) AS user_total,
       RANK()      OVER (PARTITION BY user_id ORDER BY amount DESC) AS rnk
FROM orders;
```
Це часте senior-питання: `GROUP BY` **зменшує** кількість рядків, `OVER()` — **ні**.

**Трейдоф:** агрегація на боці БД (близько до даних, використовує індекси) майже завжди швидша за «витягнути все в Python і порахувати» (мережа + пам'ять + GIL). Правило: **рахуй у базі**, тягни в застосунок лише результат.

---

## 57. JOIN між таблицями і self-join

### L1 — Junior
**Аналогія — склеювання двох списків за спільним полем.** Є список замовлень (з `user_id`) і список користувачів (з `id`). **JOIN** склеює їх, щоб у результаті біля кожного замовлення було ім'я користувача.

**Self-join** — склеювання таблиці **самої із собою**: наприклад, у таблиці співробітників кожен має `manager_id`, що вказує на іншого співробітника в **тій самій** таблиці.

### L2 — Middle
**Типи JOIN:**
```sql
-- INNER: лише ті, у кого є пара в обох таблицях
SELECT u.name, o.amount
FROM users u
INNER JOIN orders o ON o.user_id = u.id;

-- LEFT: усі users, навіть без замовлень (orders-колонки = NULL)
SELECT u.name, o.amount
FROM users u
LEFT JOIN orders o ON o.user_id = u.id;

-- RIGHT: усі orders, навіть «осиротілі»; FULL: усі з обох боків
```

| JOIN | Що повертає |
|---|---|
| `INNER` | лише збіги в обох |
| `LEFT` | усі ліві + збіги (праві NULL, якщо нема) |
| `RIGHT` | усі праві + збіги |
| `FULL OUTER` | усі з обох, NULL де нема пари |
| `CROSS` | декартів добуток (усі×усі) |

**Self-join** — обов'язково **аліаси**, щоб розрізнити «дві копії» таблиці:
```sql
-- Кожен співробітник і його керівник (з тієї ж таблиці)
SELECT
    e.name      AS employee,
    m.name      AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
-- LEFT, щоб не загубити СЕО (у нього manager_id IS NULL)
```

З Python — звичайний параметризований запит:
```python
cur.execute("""
    SELECT e.name, m.name
    FROM employees e
    LEFT JOIN employees m ON e.manager_id = m.id
    WHERE e.department_id = %s
""", (dept_id,))
```

**Gotcha:** `INNER JOIN` у self-join **відкине** записи без пари (CEO без менеджера зникне). Для ієрархій частіше `LEFT JOIN`. І завжди задавай **аліаси** — без них `employees.id` неоднозначний.

### L3 — Senior
**Алгоритми JOIN** (планувальник обирає за статистикою/розмірами/індексами):
- **Nested Loop Join** — для кожного рядка лівої таблиці шукати у правій. Швидко, якщо права маленька / є індекс. `O(n × m)` без індексу, `O(n × log m)` з індексом.
- **Hash Join** — будує хеш-таблицю меншої таблиці, проганяє більшу. Гарно для великих таблиць без сортування. `O(n + m)`, але потребує пам'яті (`work_mem`).
- **Merge Join** — обидві відсортовані за ключем, зливаються. Гарно, якщо дані вже впорядковані (індекс). `O(n log n + m log m)`.

`EXPLAIN ANALYZE` показує обраний план — головний інструмент діагностики повільних JOIN.

**Self-join і рекурсія:** прості ієрархії (1 рівень) — self-join. **Глибока ієрархія довільної глибини** (усі підлеглі підлеглих) — **рекурсивний CTE**:
```sql
WITH RECURSIVE subordinates AS (
    SELECT id, name, manager_id FROM employees WHERE id = 1
    UNION ALL
    SELECT e.id, e.name, e.manager_id
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates;
```

**Індекси на FK — критично:** `JOIN ON o.user_id = u.id` без індексу на `orders.user_id` → послідовний скан на кожен JOIN. PostgreSQL **не створює** індекс на FK автоматично (на відміну від PK) — це часта причина повільних JOIN у проді.

**Трейдоф нормалізація vs денормалізація:** нормалізована схема (багато JOIN) уникає дублювання й аномалій оновлення ↔ дорожчі читання (багато JOIN). Денормалізація (дублювання даних) пришвидшує читання ↔ ризик неузгодженості й складніші записи. OLTP → нормалізація; аналітика/OLAP → денормалізація (star schema).

**N+1 у Python/ORM:** головна пастка — замість одного JOIN ORM робить 1 запит на список + N запитів на пов'язані об'єкти. Лікування: eager loading (`selectinload`/`joinedload` у SQLAlchemy) або явний JOIN.

> ⚠️ Поведінка планувальника й вибір алгоритму JOIN залежать від СУБД, статистики й конфігу (`work_mem`). Перевіряй через `EXPLAIN ANALYZE` на реальних даних.

---

## 58. Як відправляти запити в SQL без ORM?

### L1 — Junior
**Аналогія:** говорити з базою **рідною мовою (SQL) напряму**, без перекладача (ORM). Ти сам пишеш SQL-рядок і відправляєш його через драйвер.

```python
import psycopg
with psycopg.connect(dsn) as conn, conn.cursor() as cur:
    cur.execute("SELECT id, name FROM users WHERE id = %s", (1,))
    print(cur.fetchone())
```

### L2 — Middle
**Повний робочий приклад (psycopg3, PostgreSQL):**
```python
import psycopg
from psycopg.rows import dict_row

dsn = "postgresql://user:pass@localhost:5432/mydb"

with psycopg.connect(dsn, row_factory=dict_row) as conn:
    with conn.cursor() as cur:
        # SELECT з параметрами → dict-рядки
        cur.execute(
            "SELECT id, name, email FROM users WHERE created_at > %s",
            ("2024-01-01",),
        )
        users = cur.fetchall()          # list[dict]

        # INSERT з поверненням id
        cur.execute(
            "INSERT INTO users (name, email) VALUES (%(name)s, %(email)s) RETURNING id",
            {"name": "Іван", "email": "ivan@example.com"},   # іменовані параметри
        )
        new_id = cur.fetchone()["id"]

        # Bulk insert — executemany
        cur.executemany(
            "INSERT INTO orders (user_id, amount) VALUES (%s, %s)",
            [(new_id, 100), (new_id, 250), (new_id, 99)],
        )
    conn.commit()
```

**Best practices без ORM:**
- **Тільки параметризовані запити** (`%s`, `%(name)s`) — захист від SQL injection. **Ніколи** `f"... {value}"`.
- `RETURNING` замість окремого SELECT після INSERT.
- `executemany` / `COPY` для масових вставок (швидше за цикл `execute`).
- `dict_row` / `class_row` — щоб не працювати з безіменними кортежами.
- Транзакції — явний `commit/rollback` (п.55).

**Async-варіант (`asyncpg`):**
```python
import asyncpg
conn = await asyncpg.connect(dsn)
rows = await conn.fetch("SELECT id, name FROM users WHERE id = $1", 1)  # $1 — плейсхолдер
await conn.close()
```

**Gotcha:** **плейсхолдер ≠ форматування рядка.** `%s` у psycopg — це **не** Python `%`-форматування; драйвер сам екранує й підставляє значення на боці протоколу. Тому `cur.execute("... %s", (val,))` безпечно, а `cur.execute("... %s" % val)` — діра SQLi.

### L3 — Senior
**Рівні «без ORM»:**
1. **Сирий DB-API** (`psycopg`/`asyncpg`) — рядки SQL вручну. Максимальний контроль/швидкість, але мапінг у Python-структури — твоя відповідальність.
2. **SQLAlchemy Core** — «золота середина»: SQL будується типобезпечними Python-виразами (`select(users).where(users.c.id == 1)`), композиційно, без рядкових конкатенацій, але **без** identity map / lazy loading / units of work повного ORM.

**Параметризація — це не лише безпека, а й продуктивність:** з параметрами БД **кешує план запиту** (prepared statement). Той самий запит із різними значеннями переиспользує план → менше парсингу/планування. Конкатенація значень у текст ламає кешування плану (кожен запит унікальний).

**Server-side cursors для великих вибірок:** `cur.fetchall()` тягне **весь** результат у пам'ять Python (`O(n)` RAM — небезпечно для мільйонів рядків). Named/server-side cursor стрімить порціями:
```python
with conn.cursor(name="big") as cur:    # server-side cursor
    cur.execute("SELECT * FROM huge_table")
    for row in cur:                     # ліниво, порціями, O(1) пам'яті
        process(row)
```

**`COPY` замість INSERT для bulk:** для завантаження мільйонів рядків `COPY` на порядки швидший за `executemany` (мінімум round-trip і парсингу).

**Трейдоф raw SQL vs ORM:**
| | Raw SQL | ORM |
|---|---|---|
| Швидкість виконання | максимум | overhead |
| Контроль над SQL | повний | обмежений |
| Безпека SQLi | вручну (легко забути) | за замовчуванням |
| N+1 | немає (ти пишеш JOIN) | ризик (lazy loading) |
| Швидкість розробки | повільніше | швидше |
| Складні запити | природно | інколи незручно |

Senior-стратегія: **ORM для рутинного CRUD** (швидкість розробки + безпека), **raw/Core для гарячих/складних запитів** (аналітика, звіти, оптимізовані JOIN). Не «релігія», а вибір за контекстом.

> ⚠️ Синтаксис плейсхолдерів і API різні: psycopg (`%s`, `%(name)s`), asyncpg (`$1`), sqlite3 (`?`, `:name`). Звіряй `paramstyle` драйвера в docs.
