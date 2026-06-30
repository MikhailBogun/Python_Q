# asyncio — детально, як працює (deep-dive)

> Повне розуміння asyncio: ментальна модель → практика → **під капотом** (event loop, корутини, Task/Future, selectors). Під відео-роль: роздача стриму тисячам клієнтів, оркестрація pipeline, producer-consumer.
> Формат — Принцип Сходів. Код перевірений запуском.

---

## 1. Яку проблему вирішує asyncio

### L1 — інтуїція
**Аналогія — один офіціант на 50 столиків.** Він **не стоїть** біля столу, чекаючи, поки гості оберуть. Прийняв замовлення → пішов до іншого → повернувся, коли кухня готова. **Один** працівник (потік) обслуговує багатьох, бо **не простоює в очікуванні**.

asyncio дає **конкурентність на одному потоці** для **I/O-bound** задач: поки одна корутина чекає мережу/диск, інші працюють.

### Чому це важливо для відео
- **Роздача стриму** тисячам глядачів (кожен — повільне мережеве з'єднання) — класичний I/O-bound. Потоки коштували б ~MB стека кожен; asyncio — корутини по kB → десятки тисяч з'єднань на одному потоці.
- **Оркестрація** — приймати команди, керувати pipeline, координувати джерела, поки **важкий енкодинг** робить C-код/процеси (asyncio диригує, не рахує).

### Конкурентність ≠ паралелізм (фундамент)
- **asyncio** — **конкурентність**: задачі чергуються на **одному** потоці (один CPU). Для **I/O** (чекання) — ідеально.
- **НЕ паралелізм** — не виконує код на багатьох ядрах одночасно. Для **CPU-bound** (енкодинг) asyncio **не допоможе** → процеси/C (Q1).

---

## 2. Три ключові поняття

```
async def → КОРУТИНА (coroutine) — функція, що вміє призупинятись
await     → точка ПРИЗУПИНЕННЯ — "віддай керування loop'у, поки це не готове"
event loop → ПЛАНУВАЛЬНИК — крутить корутини, чекає I/O, відновлює готові
```

```python
import asyncio

async def fetch(name):           # КОРУТИНА
    print(f"{name}: старт")
    await asyncio.sleep(1)        # ПРИЗУПИНЕННЯ (не блокує інших!)
    print(f"{name}: готово")
    return name

async def main():
    # gather — запустити КОНКУРЕНТНО (разом ~1с, а не 3с)
    results = await asyncio.gather(fetch("A"), fetch("B"), fetch("C"))
    print(results)

asyncio.run(main())              # EVENT LOOP запускається тут
```

**Ключове:** `await asyncio.sleep(1)` не блокує **потік** — він призупиняє лише **цю корутину**, віддаючи керування loop'у, який запускає інші. Тому 3 корутини по 1с виконуються за ~1с (паралельне чекання), а не 3с.

---

## 3. Як це працює ПІД КАПОТОМ ⭐

### 3.1 Корутини побудовані на генераторах
`async/await` — синтаксична еволюція **генераторів** (`yield from`). Корутина, як генератор, має `send()`, `throw()`, `close()`. **`await` ≈ `yield from`**: делегує очікуваному об'єкту й **призупиняє**, зберігаючи **frame** (стек, локальні), доки очікуване не готове.

```python
# Корутина — це об'єкт зі станом, який можна "крокувати"
async def coro():
    await asyncio.sleep(1)
    return 42

c = coro()                       # НЕ виконує тіло! створює об'єкт-корутину
# c.send(None) — крокнути до наступного await (так робить event loop)
```
**Gotcha:** виклик `coro()` **не виконує** код — лише створює об'єкт. Виконання починається, коли loop почне його «крокувати» (`send`). Без `await`/`create_task` — `RuntimeWarning: coroutine was never awaited`.

### 3.2 Event loop — серце системи
Event loop тримає **три структури**:
```
┌─ Event Loop ────────────────────────────────────┐
│ 1. _ready    — черга callbacks, ГОТОВИХ до запуску (deque)
│ 2. _scheduled — таймери (call_later/call_at) — min-heap за часом
│ 3. selector  — реєстр файлових дескрипторів (сокети) — epoll/kqueue
└──────────────────────────────────────────────────┘
```

**Одна ітерація loop (`_run_once`) — спрощено:**
```
1. timeout = час до найближчого таймера (або 0, якщо є готові callbacks)
2. events = selector.select(timeout)   ← "СПИТЬ" тут, чекаючи I/O (неблокуюче для потоку!)
3. для кожного готового fd → запланувати його callback у _ready
4. перенести "дозрілі" таймери з _scheduled у _ready
5. виконати ВСІ callbacks із _ready (по черзі)
6. повторити
```

**Ключовий момент — крок 2:** у фазі `selector.select(timeout)` потік **«спить»**, чекаючи події від ОС (`epoll`). Це і є «неблокуюче очікування»: потік не зайнятий, ОС розбудить, коли сокет готовий. Так один потік обслуговує тисячі з'єднань.

### 3.3 Як корутина призупиняється й відновлюється (повний цикл)
```
1. loop викликає coro.send(None) → корутина виконується ДО першого await
2. await на I/O (напр. читання сокета):
   - реєструє fd у selector + створює Future
   - "yield" Future назовні → корутина ПРИЗУПИНЯЄТЬСЯ (frame збережено)
3. loop отримує Future, додає callback "відновити цю корутину, коли Future готовий"
4. loop крутиться далі, обслуговує інші корутини
5. ОС: сокет готовий → selector.select повертає fd
6. loop встановлює результат Future → це тригерить callback
7. callback викликає coro.send(результат) → корутина ВІДНОВЛЮЄТЬСЯ з місця await
```
Тобто **немає магії потоків** — один потік, кооперативне перемикання на `await`, а очікування делеговане ОС через `epoll`. Це той самий механізм, що в Node.js/libuv (зв'язок з блоком Node).

---

## 4. Task vs Future vs Coroutine (плутають!) ⭐

| | Що це | Запланована на loop? |
|---|---|---|
| **Coroutine** | результат `async def` — «рецепт» | **ні** (поки не await/wrap) |
| **Future** | низькорівневий «обіцяний результат» (placeholder) | — |
| **Task** | `Future`, що **обгортає й планує корутину** | **так** |

```python
async def work(): ...

# Coroutine — просто об'єкт, ще НЕ виконується
coro = work()

# Task — обгортає корутину й ПЛАНУЄ її на loop (виконується конкурентно ОДРАЗУ)
task = asyncio.create_task(work())     # стартує негайно у фоні

# await чекає завершення
result = await task
```

**Як Task драйвить корутину (під капотом):**
```
create_task(coro) → Task обгортає coro → планує перший крок через loop.call_soon
Task.__step():
   result = coro.send(None)        # крокнути корутину до наступного await
   # corо віддала Future (від await) →
   future.add_done_callback(Task.__step)   # відновити, коли Future готовий
```
Task — це «двигун», що крокує корутину від `await` до `await`, підписуючись на Future'и між ними.

**Future** — об'єкт із результатом + списком callbacks. `await future` призупиняє корутину, доки хтось не викличе `future.set_result(...)`. Це міст між «низьким» світом (callbacks, I/O) і «високим» (async/await).

---

## 5. Запуск конкурентно — патерни ⭐

### Послідовно vs конкурентно (КРИТИЧНА різниця)
```python
# ❌ ПОСЛІДОВНО — await у циклі чекає кожен по черзі → сума часів
async def slow():
    for url in urls:
        await fetch(url)             # 10 × 1с = 10с

# ✅ КОНКУРЕНТНО — gather запускає всі разом → час найдовшого
async def fast():
    await asyncio.gather(*[fetch(url) for url in urls])    # ~1с
```

### Основні інструменти
```python
# gather — запустити всі, дочекатись усіх, повернути результати
results = await asyncio.gather(a(), b(), c())

# create_task — запустити у фоні (fire-and-forget або await пізніше)
task = asyncio.create_task(background_work())

# TaskGroup (3.11+) — структурована конкурентність (рекомендовано)
async with asyncio.TaskGroup() as tg:
    tg.create_task(a())
    tg.create_task(b())
# тут усі завершені; якщо одна впала — інші коректно скасовуються

# as_completed — обробляти результати в порядку ЗАВЕРШЕННЯ
for coro in asyncio.as_completed([a(), b(), c()]):
    result = await coro              # перший готовий — перший оброблений

# wait_for / timeout — обмежити час
result = await asyncio.wait_for(slow(), timeout=5.0)
async with asyncio.timeout(5.0):     # 3.11+
    await slow()
```

**Gotcha:** `gather` — **fail-fast**: одна корутина впала → весь gather кидає виняток (інші можуть лишитись виконуватись). `return_exceptions=True` — зібрати помилки замість падіння (як `allSettled` у JS).

---

## 6. Блокування loop — головний гріх ⭐⭐

**Один блокуючий виклик у корутині вішає ВЕСЬ loop** — усі тисячі з'єднань стоять.

```python
import time

# ❌ КАТАСТРОФА: блокує loop на 5с → усі глядачі заморожені
async def bad():
    time.sleep(5)                    # синхронний sleep — блокує потік!
    cpu_heavy_encode()               # CPU-важке — теж блокує

# ✅ Правильно:
async def good():
    await asyncio.sleep(5)           # async sleep — віддає керування loop
    # CPU-важке → винести з loop:
    await asyncio.to_thread(cpu_heavy_encode)        # у потік (3.9+)
    # або в процес для справжнього паралелізму:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(process_pool, cpu_heavy_encode)
```

**Що блокує loop (уникати в корутинах):**
- `time.sleep()` → `asyncio.sleep()`.
- `requests.get()` → `aiohttp`/`httpx` async.
- Важкий CPU (енкодинг, JSON великого об'єкта) → `to_thread`/process pool.
- Блокуючий файловий I/O → `aiofiles` або `to_thread`.
- Блокуючі БД-драйвери → async-драйвери (`asyncpg`).

**Метрика:** **event loop lag** (`loop.time()` дельти, або `asyncio` debug mode) — якщо росте, десь блокуючий виклик. Для відео-сервісу це прямий показник здоров'я (зв'язок з troubleshooting Q6).

---

## 7. Кооперативність — наслідки (Senior)

asyncio — **кооперативне** планування: перемикання **лише на явному `await`**, не примусове (на відміну від потоків — preemptive).

**Наслідки:**
- **+** Між двома `await` код **атомарний** → менше race conditions (не треба замки на простий спільний стан, бо ніхто не перерве посеред).
- **+** Корутини дешеві (kB) → десятки тисяч.
- **−** Один «жадібний» (блокуючий) виклик вішає всіх (розділ 6).
- **−** Треба писати неблокуюче **наскрізно** — «зараза» async (одна async-функція тягне async по всьому ланцюгу).

**vs потоки (трейдоф):**
| | asyncio | threading |
|---|---|---|
| Перемикання | кооперативне (на await) | примусове (ОС будь-коли) |
| Race conditions | менше (атомарно між await) | багато (потрібні замки) |
| Масштаб | десятки тисяч | сотні (стек ~MB) |
| CPU-паралелізм | ні (GIL + один потік) | ні (GIL), процеси — так |
| Блокуючий код | вішає все | ок (інші потоки працюють) |

---

## 8. Скасування (cancellation) і обробка помилок

```python
task = asyncio.create_task(work())
task.cancel()                        # запит на скасування
try:
    await task
except asyncio.CancelledError:
    print("скасовано")               # cleanup

# Коректний cleanup при скасуванні:
async def worker():
    try:
        while True:
            await process_frame()
    except asyncio.CancelledError:
        await cleanup()              # звільнити ресурси
        raise                        # ПЕРЕкинути (не глушити!)
```

**Gotcha:** **fire-and-forget Task губить винятки.** Якщо створив Task і не await — виняток у ньому може «зникнути» (лише warning). Тримай посилання + обробляй (`task.add_done_callback` або await). `TaskGroup` (3.11+) це вирішує — збирає й піднімає помилки.

---

## 9. asyncio для відео-сервісу (під роль) ⭐

### Async-сервер роздачі (TCP/HTTP streams)
```python
async def handle_viewer(reader, writer):
    """Кожен глядач — окрема корутина (легка, не потік)."""
    while chunk := await get_next_segment():
        writer.write(chunk)
        await writer.drain()         # backpressure: не переповнити буфер
    writer.close()

async def main():
    server = await asyncio.start_server(handle_viewer, "0.0.0.0", 8080)
    async with server:
        await server.serve_forever()
```

### UDP (зв'язок з 06_deep_dive_udp)
```python
class RTPReceiver(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        process_packet(data)         # викликається loop'ом на кожну датаграму

transport, _ = await loop.create_datagram_endpoint(
    RTPReceiver, local_addr=("0.0.0.0", 5004))
```

### Producer-consumer через asyncio.Queue (зв'язок з Q11)
```python
async def capture(q: asyncio.Queue):
    while True:
        await q.put(await grab_frame())   # backpressure якщо maxsize

async def encode_loop(q: asyncio.Queue):
    while (frame := await q.get()) is not None:
        await asyncio.to_thread(encode, frame)   # CPU → в потік!

q = asyncio.Queue(maxsize=100)
await asyncio.gather(capture(q), encode_loop(q))
```

### Інтеграція з GStreamer (реальний виклик!)
GStreamer використовує **GLib MainLoop** (свій event loop), а asyncio — свій. Дві loop в одному потоці конфліктують. Рішення:
- Запустити GLib loop в **окремому потоці**, спілкуватись через thread-safe чергу/`loop.call_soon_threadsafe`.
- Або bridge-бібліотеки. ⚠️ Це нетривіально — реальна архітектурна задача для такого сервісу.

**Архітектура:** asyncio диригує (приймає команди, роздає, координує) ← важкий енкодинг у GStreamer (C, відпускає GIL, окремий потік) ← CPU-fallback у процеси. asyncio — **orchestration layer**, не місце для обчислень.

---

## 10. Типові помилки (чеклист gotchas)

| Помилка | Наслідок | Рішення |
|---|---|---|
| `coro()` без await | не виконується (warning) | `await` / `create_task` |
| `time.sleep` у корутині | вішає весь loop | `asyncio.sleep` |
| блокуючий CPU/I/O у корутині | вішає loop | `to_thread`/executor |
| `await` у циклі замість gather | послідовно (повільно) | `asyncio.gather` |
| fire-and-forget task | губить винятки | тримати ref / `TaskGroup` |
| змішування sync/async loop | конфлікт | один loop, `call_soon_threadsafe` |
| `gather` без `return_exceptions` | один fail валить усе | `return_exceptions=True` за потреби |

---

## ✅ Чеклист «розумію asyncio» (інтерв'ю)

**Базово:**
- [ ] Конкурентність ≠ паралелізм; asyncio для I/O, не CPU.
- [ ] `async def` / `await` / event loop — три поняття.
- [ ] `await asyncio.sleep` не блокує потік (на відміну від `time.sleep`).

**Середній:**
- [ ] gather (конкурентно) vs await у циклі (послідовно).
- [ ] Task vs coroutine vs Future.
- [ ] **Не блокувати loop**; `to_thread`/executor для блокуючого.
- [ ] Event loop lag як метрика.

**Senior:**
- [ ] Як працює під капотом: корутини на генераторах, `send`/yield Future, selector/epoll, Task драйвить корутину.
- [ ] Кооперативне планування — наслідки (атомарність між await, один жадібний вішає всіх).
- [ ] Cancellation + cleanup; fire-and-forget губить винятки; TaskGroup.
- [ ] asyncio як orchestration layer (важке — в C/процеси); інтеграція з GLib (GStreamer).

---

## 🔑 Головне
asyncio = **один потік + event loop + кооперативне перемикання на `await` + делегування I/O в ОС (epoll)**. Чудовий для I/O-конкурентності (роздача стриму, мережа), **марний для CPU** (енкодинг → C/процеси). Головне правило: **ніколи не блокуй loop**.

## 🔗 Зв'язки
- **GIL / concurrency / коли async vs процеси:** [04_python_answers_q1_q8.md](04_python_answers_q1_q8.md) Q1, Q2.
- **Producer-consumer (asyncio.Queue):** [05_python_answers_q9_q13.md](05_python_answers_q9_q13.md) Q11.
- **UDP DatagramProtocol:** [06_deep_dive_udp.md](06_deep_dive_udp.md).
- **GStreamer (GLib loop інтеграція):** [07_deep_dive_gstreamer.md](07_deep_dive_gstreamer.md).
- **Повна відповідь по async:** [answers/06_python_advanced.md](../answers/06_python_advanced.md) п.73.

> ⚠️ Внутрішня реалізація (Task.__step, Future callbacks, `_run_once`) — деталі CPython asyncio, що еволюціонують. Концептуально стабільні; точні деталі звіряй з docs/сорсами `asyncio` своєї версії. `TaskGroup`/`asyncio.timeout` — 3.11+.
