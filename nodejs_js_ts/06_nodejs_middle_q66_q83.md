# Блок 6. Node.js — Middle/Senior (питання 66–83)

> Формат — **Принцип Сходів**: L1 Junior → L2 Middle → L3 Senior.
> Дотичні до Junior-блоку (01) питання розкрито **глибше** з крос-посиланнями.

---

## 66. Переваги Node.js проти інших серверних технологій

### L1 — Junior
**Аналогія — універсальний майстер, що швидко бігає між справами.** Node чудовий, коли треба обслужити **багато одночасних з'єднань**, що переважно **чекають** (I/O), і коли цінується **одна мова** на фронт і бек.

### L2 — Middle
| Перевага | Проти кого виграє |
|---|---|
| Неблокуючий I/O, тисячі з'єднань | проти thread-per-request (Java/PHP-FPM) — менше пам'яті |
| Одна мова full-stack (JS/TS) | проти Python+JS, Java+JS — спільний код/типи |
| **npm** — найбільший реєстр | швидкість розробки |
| JSON-native | менше серіалізації (REST/GraphQL) |
| Real-time (WebSocket) | природний для чатів/нотифікацій |
| Швидкий старт/прототипування | проти Java/C# (менше бойлерплейту) |

### L3 — Senior
**Де Node об'єктивно виграє — I/O-конкурентність:** один event loop тримає десятки тисяч з'єднань майже без overhead (проти ~MB стека на потік у thread-per-request). Для **API-gateway, проксі, real-time, BFF, мікросервісів-оркестраторів** — ідеально.

**Де програє (чесно):** CPU-bound (Go/Rust/Java швидші й паралельні), важкі обчислення (один потік + GIL-подібне обмеження JS). **Трейдоф:** продуктивність розробки + I/O-конкурентність ↔ слабкість на CPU, динамічна типізація (лікується TS), npm supply-chain ризик. Senior обирає Node **під профіль навантаження** (I/O-важке), не догматично.

---

## 67. Коли використати кілька процесів/потоків?

### L1 — Junior
- **CPU-важке** (обробка зображень/відео, шифрування, складні обчислення) → `worker_threads`/процеси.
- **Задіяти всі ядра** веб-сервером → `cluster`.
- **Ізоляція / зовнішні програми** → `child_process`.

### L2 — Middle
| Задача | Інструмент |
|---|---|
| CPU-bound обчислення (не блокувати loop) | `worker_threads` |
| Масштабувати HTTP-сервер на всі ядра | `cluster` |
| Запустити зовнішню програму (ffmpeg, скрипт) | `child_process` (`spawn`/`exec`) |
| Ізольована важка задача | `child_process.fork` |

**Gotcha:** один Node-процес = один потік JS (питання 83). Важкий CPU блокує event loop → усі запити стоять. Тому CPU виносять у воркери/процеси.

### L3 — Senior
**Трейдоф (деталі — питання 80):** `worker_threads` дешевші, можуть ділити пам'ять (`SharedArrayBuffer`); `child_process` — повна ізоляція, дорожчий старт, IPC; `cluster` — N процесів на одному порту для горизонтального масштабування. **CPU-bound → worker_threads/процеси; масштаб HTTP → cluster; зовнішні бінарники → child_process.** Для відео (ffmpeg/обробка кадрів) — child_process на ffmpeg або worker_threads на обчислення.

---

## 68. Паралельне vs асинхронне програмування (на серверах) ⭐

### L1 — Junior
- **Асинхронне** — один працівник **не простоює**, чергуючи справи (поки чекає одне — робить інше). **Один потік.**
- **Паралельне** — кілька працівників роблять **одночасно** (різні ядра).

### L2 — Middle
```
АСИНХРОННЕ (Node за замовчуванням): один потік, задачі ЧЕРГУЮТЬСЯ на await/I/O
  Запит1 [чекає БД...] Запит2 [чекає БД...] Запит3 → усі прогресують, але по черзі на CPU

ПАРАЛЕЛЬНЕ (cluster/worker_threads): кілька потоків/процесів ОДНОЧАСНО на різних ядрах
  Ядро1: Запит1   Ядро2: Запит2   Ядро3: Запит3 → справді одночасно
```
**На сервері:** Node **асинхронно** обслуговує тисячі I/O-запитів на **одному** потоці (поки один чекає БД — обробляє інші). Це **не паралелізм** — лише один запит виконує JS-код у будь-який момент.

### L3 — Senior
**Конкурентність ≠ паралелізм** (фундамент):
- **Конкурентність** (async) — задачі **прогресують разом**, чергуючись (один потік). Для **I/O** ідеально (чекання дешеве).
- **Паралелізм** — задачі виконуються **фізично одночасно** (багато ядер). Для **CPU** потрібен.

Node дає конкурентність «з коробки» (event loop), паралелізм — лише через `cluster`/`worker_threads`. **Серверний приклад:** 10000 з'єднань, що чекають БД → async (один потік, дешево); 10000 обчислень хешів → потрібен паралелізм (процеси/воркери, бо один потік рахуватиме послідовно). Senior розрізняє: «багато чекання» → async; «багато рахунку» → паралелізм.

---

## 69. Типи асинхронних операцій Node

### L1 — Junior
Node вміє неблокуюче: **мережа** (HTTP, сокети), **файли** (читання/запис), **таймери** (setTimeout), **БД-запити**, **DNS**, **криптографія**.

### L2 — Middle
| Тип | Приклади | Як виконується |
|---|---|---|
| **Мережевий I/O** | HTTP, TCP/UDP сокети | неблокуюче через ОС (epoll/kqueue) |
| **Файловий I/O** | `fs.readFile` | **thread pool** libuv (питання 89) |
| **DNS** | `dns.lookup` | thread pool |
| **Crypto** | `crypto.pbkdf2`, randomBytes | thread pool |
| **Стиснення** | `zlib` | thread pool |
| **Таймери** | setTimeout/setInterval | event loop (фаза timers) |
| **Microtasks** | Promise, queueMicrotask | між фазами |

### L3 — Senior
**Два механізми асинхронності (ключове):**
1. **Native async (ОС):** мережеві сокети — неблокуюче через `epoll`/`kqueue`/`IOCP`, **без потоків** (один потік питає ОС «що готове?»).
2. **Thread pool (libuv):** файли, DNS, crypto, zlib — у пулі з **4 потоків**, бо в них **немає** надійного неблокуючого ОС-API (питання 89).

**Gotcha:** 5 важких `crypto.pbkdf2` одночасно → 5-й **чекає** звільнення потока пулу (черга). `UV_THREADPOOL_SIZE` це налаштовує. Прихований bottleneck.

---

## 70. Які модулі Node знаєте?

### L1 — Junior
Вбудовані (core): `fs` (файли), `http` (сервер), `path` (шляхи), `os` (система), `events` (події), `stream` (потоки), `crypto` (криптографія).

### L2 — Middle
| Модуль | Призначення |
|---|---|
| `fs` / `fs/promises` | файлова система |
| `http` / `https` / `http2` | веб-сервери/клієнти |
| `net` / `dgram` | TCP / UDP сокети |
| `path` | робота зі шляхами |
| `os` | інфо про систему |
| `events` | EventEmitter (питання 82) |
| `stream` | потоки (питання 91-95) |
| `buffer` | бінарні дані |
| `crypto` | шифрування/хеші |
| `child_process` / `worker_threads` / `cluster` | багатопроцесність (питання 80) |
| `util` | утиліти (promisify) |
| `process` | поточний процес (argv, env, signals) |
| `zlib` | стиснення |
| `url` / `querystring` | URL |

**Best practice:** імпорт із префіксом `node:` (`import fs from "node:fs"`) — явно вбудований, не плутати з npm-пакетом.

### L3 — Senior
Core-модулі — це **тонкі JS-обгортки над C++ bindings** до libuv/V8/системних бібліотек. `fs.readFile` → C++ → libuv thread pool → системний `read`. Знання, **який** модуль що робить асинхронно (питання 69) — основа продуктивності. Багато core-API — **EventEmitter** (http server, streams, process) або повертають **Promise** (`fs/promises`).

---

## 71. Операційні помилки vs помилки програміста ⭐

### L1 — Junior
- **Операційна помилка** — очікувана проблема **середовища**: мережа впала, файл не знайдено, невалідний ввід. **Обробляємо** gracefully.
- **Помилка програміста** — **баг** у коді: `undefined is not a function`, забув `await`, опечатка. **Не обробляємо — виправляємо** (нехай падає голосно).

### L2 — Middle
| | Операційна | Програміста (bug) |
|---|---|---|
| Приклади | timeout, 404, ECONNREFUSED, невалідний JSON | TypeError, ReferenceError, забутий await |
| Передбачувана? | так (частина системи) | ні (дефект) |
| Що робити | обробити (retry, fallback, 4xx) | виправити код; краще crash + рестарт |

```javascript
// Операційна — обробляємо
try {
  await fetch(url);
} catch (err) {
  if (err.code === "ECONNREFUSED") return retryLater();  // очікувано
}
// Програміста — НЕ ловимо (нехай впаде, побачимо стектрейс)
// user.naem  ← опечатка → TypeError → виправити, не try/catch
```

### L3 — Senior
**Це фундаментальний принцип надійності Node** (з Node best practices / Joyent). Чому важливо:
- **Операційні** — нормальна частина системи → graceful degradation (retry з backoff, circuit breaker, 4xx/5xx).
- **Помилки програміста** — стан процесу **невідомий/зіпсований** → найкраще **дати впасти** (`uncaughtException`) і **рестартувати** під supervisor (systemd/PM2/k8s). Намагатись «продовжити» після бага — небезпечно (corrupt state).

**Gotcha:** ловити **всі** помилки одним `try/catch` і продовжувати — антипатерн: маскує баги, лишає процес у поганому стані. Розрізняй: операційні — обробляй за типом; програмні — fail fast + рестарт.

---

## 72. Сервіси для моніторингу й логування

### L1 — Junior
- **Логування** (запис подій): **pino**, winston, bunyan.
- **Моніторинг** (здоров'я системи): Prometheus + Grafana, Datadog, New Relic.
- **Помилки**: Sentry.

### L2 — Middle
| Категорія | Інструменти |
|---|---|
| Структуровані логи | **pino** (швидкий), winston |
| Агрегація логів | ELK (Elasticsearch+Logstash+Kibana), Grafana Loki, Splunk |
| Метрики | Prometheus + Grafana |
| APM (трасування, перформанс) | Datadog, New Relic, Dynatrace, Elastic APM |
| Error tracking | Sentry, Rollbar |
| Process manager + базовий моніторинг | PM2 |
| Uptime | UptimeRobot, Pingdom |

### L3 — Senior
**Три стовпи observability:** **logs** (що сталося), **metrics** (скільки/як швидко), **traces** (де затик у розподіленій системі). Node-специфіка: моніторити **event loop lag** (`perf_hooks.monitorEventLoopDelay`) — прямий показник «чи не блокується loop» (зв'язок з питанням 88), **heap usage / GC-паузи** (питання 76-78), active handles. Структуровані JSON-логи (pino) + correlation ID для трасування запиту. Не логувати секрети (GDPR).

---

## 73. Що таке libuv? Його складові ⭐

### L1 — Junior
**libuv** — C-бібліотека, що дає Node **асинхронний I/O** і **event loop**. Це «двигун неблокуючості». *(База — Junior-блок Q9.)*

### L2 — Middle
**Складові libuv:**
| Складова | Призначення |
|---|---|
| **Event loop** | головний цикл, що обробляє події (питання 88) |
| **Thread pool** | пул потоків (4) для fs/dns/crypto/zlib (питання 89) |
| **Async I/O абстракція** | epoll (Linux) / kqueue (macOS) / IOCP (Windows) — крос-платформність |
| **Handles** | довгоживучі об'єкти (сокети, таймери, сервери) |
| **Requests** | короткоживучі операції (одне читання файлу, DNS-запит) |
| **Timers** | setTimeout/setInterval |

### L3 — Senior
libuv **відокремлює** Node-код від платформи: дає єдиний API над різними ОС-механізмами неблокуючого I/O (epoll/kqueue/IOCP). **Handles vs Requests** — ключове розрізнення: handle живе довго (TCP-сервер слухає), request — одноразова операція (`fs.read`). Event loop крутить handles, thread pool виконує «синхронні» операції (файли), що не мають async ОС-API (питання 89). **V8 виконує JS, libuv дає асинхронність** — Node склеює їх (Junior-блок Q9).

> ⚠️ Точний перелік «складових» libuv у джерелах варіюється — суть: event loop + thread pool + крос-платформна async-I/O абстракція + handles/requests. Звіряй з docs libuv.

---

## 74. Шаблони розподілених транзакцій ⭐

### L1 — Junior
Коли операція зачіпає **кілька сервісів/БД**, не можна зробити звичайну ACID-транзакцію. Потрібні **спеціальні шаблони**, щоб тримати дані узгодженими.

### L2 — Middle
| Шаблон | Суть |
|---|---|
| **2PC (Two-Phase Commit)** | координатор: prepare → commit/rollback на всіх. Атомарно, але **блокуюче** |
| **Saga** | ланцюг локальних транзакцій + **компенсуючі** дії при відкаті |
| **TCC (Try-Confirm-Cancel)** | зарезервувати → підтвердити / скасувати |
| **Outbox** | записати подію в ту ж БД-транзакцію → асинхронно опублікувати |

```
Saga (замовлення): Платіж → Резерв складу → Доставка
   якщо Доставка впала → компенсація: Скасувати резерв → Повернути платіж
```

### L3 — Senior
*(Глибше — Python-блоки про розподілені системи.)* **2PC** — сильна узгодженість, але координатор = SPOF + блокування (повисання) → погано масштабується. **Saga** — стандарт для мікросервісів: **eventual consistency** замість атомарності, кожен крок має **компенсацію** (відкат). Choreography (події) vs orchestration (центральний координатор). **Outbox** вирішує проблему «записав у БД, але не опублікував подію» (atomicity між БД і брокером).

**Трейдоф:** 2PC — консистентність ціною доступності/масштабу; Saga — масштаб/доступність ціною складності (компенсації, проміжні неузгоджені стани). У Node-мікросервісах зазвичай **Saga + Outbox + ідемпотентність**.

> ⚠️ Це оглядово; деталі реалізації (брокери, ідемпотентність, isolation) — окрема глибока тема. Звіряй з джерелами про мікросервіси (Microservices Patterns, Richardson).

---

## 75. Чи можна програмно контролювати пам'ять у Node?

### L1 — Junior
**Прямо — ні** (GC керує автоматично, немає `free()` як у C). Але **впливати — так**: відпускати посилання, обмежувати кеші, керувати буферами, налаштовувати ліміти heap.

### L2 — Middle
```javascript
// Звільнити посилання → GC згодом прибере
let bigData = loadHuge();
process(bigData);
bigData = null;                    // допомогти GC (прибрати посилання)

// Примусовий GC (лише з прапором --expose-gc, для дебагу)
if (global.gc) global.gc();

// Інфо про пам'ять
console.log(process.memoryUsage());  // { rss, heapTotal, heapUsed, external }

// Ліміт heap
// node --max-old-space-size=4096 app.js   (4GB)
```

### L3 — Senior
**Інструменти впливу (не контролю):**
- **`WeakRef`/`WeakMap`/`WeakSet`** — слабкі посилання, що **не заважають** GC (кеші, що не тримають об'єкти).
- **Buffer** — пам'ять поза V8-heap (`external`), для бінарних даних/zero-copy.
- **Streams** — обробляти дані шматками, не вантажити все (питання 87).
- **`--max-old-space-size`** — ліміт old space.
- Нуляти посилання, прибирати listeners/timers (питання 77).

**Трейдоф:** автоматичний GC прибирає клас багів (use-after-free) ↔ немає детермінованого контролю (як C/Rust). «Контроль» у Node = **дисципліна посилань** + правильні структури, а не ручне `free`.

---

## 76. Що таке Garbage Collector? ⭐

### L1 — Junior
**GC (збирач сміття)** — частина V8, що **автоматично звільняє** пам'ять об'єктів, на які **більше ніхто не посилається**. Ти не звільняєш вручну — GC сам знаходить «сміття» й прибирає.

### L2 — Middle
**V8 GC — generational (за поколіннями):**
```
New space (young) — нові об'єкти, збирається ЧАСТО (швидко, Scavenge)
   ↓ пережив кілька збірок
Old space (old) — довгоживучі, збирається РІДШЕ (Mark-Sweep-Compact, дорожче)
```
Базується на гіпотезі: **більшість об'єктів вмирають молодими** → молоде покоління чистити часто й дешево.

### L3 — Senior
**Алгоритми V8:**
- **Scavenge** (new space) — copying GC, швидкий, часто; копіює живі об'єкти між двома half-spaces.
- **Mark-Sweep-Compact** (old space) — позначити досяжне → звільнити решту → ущільнити (проти фрагментації). Дорожче, рідше.

**Stop-the-world паузи:** під час GC виконання JS **призупиняється** → латентність. V8 використовує **incremental/concurrent** GC, щоб мінімізувати паузи (частину роботи — паралельно/порціями). Для low-latency сервісів GC-паузи — реальна проблема (моніторити, питання 72).

**Трейдоф vs refcount (Python):** tracing-GC ловить цикли, без overhead на присвоєння, але паузи й недетермінований момент звільнення. (Зв'язок з Python-блоком п.77.)

---

## 77. Витік пам'яті — що це й як запобігти? ⭐

### L1 — Junior
**Memory leak** — пам'ять, що **більше не потрібна**, але **не звільняється** (бо десь лишилось посилання). Процес росте, поки не впаде (OOM). Критично для довгоживучих сервісів.

### L2 — Middle
**Типові причини в Node:**
```javascript
// 1. Не видалені event listeners (накопичуються!)
emitter.on("data", handler);       // без removeListener → витік
emitter.removeListener("data", handler);  // ✅

// 2. Не очищені таймери
const t = setInterval(work, 1000); // тримає замикання вічно
clearInterval(t);                  // ✅

// 3. Необмежений кеш/глобальний масив
const cache = {};                  // росте вічно → витік
// ✅ → LRU-кеш з лімітом / WeakMap / TTL

// 4. Замикання, що тримають великі об'єкти
function leak() {
  const huge = loadHuge();
  return () => huge.x;             // замикання тримає huge назавжди
}
```

### L3 — Senior
**Запобігання (систематично):**
- **Прибирати listeners** (`removeListener`/`once`); стежити за `MaxListenersExceededWarning` (ознака витоку listeners).
- **Очищати таймери** (`clearInterval`/`clearTimeout`) у cleanup.
- **Bounded кеші** (`lru-cache` з maxSize/TTL), не голі об'єкти/Map, що ростуть.
- **`WeakMap`/`WeakRef`** для метаданих/кешів, що не повинні тримати об'єкти.
- Уникати **глобальних** акумуляторів.
- **Streams** замість завантаження всього (питання 87).

**Діагностика:** `process.memoryUsage()` у часі (RSS/heapUsed росте?), **heap snapshots** (Chrome DevTools `--inspect`, порівняти два знімки → що накопичилось), `clinic.js`, `heapdump`. (Зв'язок з питанням 78.)

---

## 78. Як налагодити «heap out of memory»?

### L1 — Junior
Помилка `JavaScript heap out of memory` = V8-heap переповнено (витік або реально замало). Перші кроки: **підняти ліміт** (тимчасово) і **знайти витік** (профілювати).

### L2 — Middle
```bash
# 1. Тимчасово підняти ліміт heap (діагностика, не лікування!)
node --max-old-space-size=4096 app.js     # 4GB

# 2. Профілювати — heap snapshots
node --inspect app.js                      # → chrome://inspect → Memory → Heap snapshot
# зробити 2 знімки (до/після навантаження) → порівняти → що росте

# 3. Інструменти
# clinic.js doctor / heapprofiler
# heapdump — програмно зняти знімок
```

### L3 — Senior
**Методика (як думає senior):**
1. **Підтвердити витік vs реальна потреба:** `process.memoryUsage().heapUsed` у часі — **монотонне зростання** під стабільним навантаженням = витік; стрибок під піком = можливо просто замало.
2. **Heap snapshots діаграма:** 2-3 знімки → **comparison view** у DevTools → об'єкти з зростаючим retained size → хто їх тримає (retainers path).
3. **Знайти джерело** (питання 77): listeners, timers, кеш, замикання, глобали.
4. **Полагодити** (прибрати посилання/обмежити), не просто піднімати `--max-old-space-size` (це маскує, не лікує).

**Production-safety:** під оркестратором OOM-процес рестартується (тимчасовий пластир), але корінь треба знайти. `--max-old-space-size` ставлять свідомо під RAM контейнера (інакше k8s OOM-killer вб'є до того, як V8 спробує GC).

---

## 79. Як налаштувати кешування?

### L1 — Junior
**Кеш** — зберігати результат, щоб не рахувати/тягнути щоразу. Рівні: у пам'яті процесу (швидко, але локально), у Redis (спільно між інстансами), HTTP-кеш/CDN (на клієнті/edge).

### L2 — Middle
```javascript
// 1. In-memory (швидко, але не шариться між інстансами, втрачається при рестарті)
import { LRUCache } from "lru-cache";
const cache = new LRUCache({ max: 1000, ttl: 1000 * 60 });  // 1000 елементів, 60с
cache.set("key", value);
const v = cache.get("key");

// 2. Redis (розподілений — спільний для всіх інстансів)
await redis.set("user:42", JSON.stringify(user), "EX", 300);  // TTL 300с
const cached = await redis.get("user:42");

// 3. HTTP-кеш (заголовки → браузер/CDN)
res.set("Cache-Control", "public, max-age=3600");
```
**Cache-aside (найпоширеніший):**
```javascript
async function getUser(id) {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);        // hit
  const user = await db.findUser(id);           // miss → БД
  await redis.set(`user:${id}`, JSON.stringify(user), "EX", 300);
  return user;
}
```

### L3 — Senior
**Стратегії й трейдофи:**
- **In-memory** — найшвидше (наносекунди), але локальне (не шариться), губиться при рестарті, їсть heap (ризик OOM, питання 77).
- **Redis/Memcached** — спільне між інстансами, переживає рестарт ↔ мережевий хоп (мс), нова точка відмови.
- **HTTP/CDN** — розвантажує сервер повністю ↔ складна інвалідація.

**Головні проблеми кешу:** **інвалідація** (TTL vs event-based vs write-through), **cache stampede** (кеш протух → тисячі запитів б'ють БД одночасно → locks/stale-while-revalidate), **hot keys**. (Зв'язок з Python-блоком п.66-67.) Senior балансує consistency ↔ latency ↔ складність; обирає рівень під патерн доступу.

---

## 80. child_process vs worker_threads vs cluster ⭐

### L1 — Junior
Три способи вийти за межі одного потоку:
- **`child_process`** — окремі **процеси** (запуск програм/скриптів).
- **`worker_threads`** — справжні **потоки** (CPU-задачі).
- **`cluster`** — кілька **процесів** на одному порту (масштабування сервера).
*(База — Junior-блок Q6.)*

### L2 — Middle
| | child_process | worker_threads | cluster |
|---|---|---|---|
| Одиниця | процес | потік | процес |
| Пам'ять | ізольована | спільна (SharedArrayBuffer) | ізольована |
| Старт | дорогий | дешевший | дорогий |
| Комунікація | IPC (serialize) | message + transfer (zero-copy ArrayBuffer) | IPC |
| Юзкейс | зовнішні програми (ffmpeg) | CPU-обчислення | масштаб HTTP на ядра |

```javascript
// worker_threads — CPU-важке без блокування loop
import { Worker } from "node:worker_threads";
new Worker("./heavy.js", { workerData: { n: 1e9 } });

// cluster — N воркерів на ядра
import cluster from "node:cluster";
import os from "node:os";
if (cluster.isPrimary) {
  for (let i = 0; i < os.cpus().length; i++) cluster.fork();
} else {
  startServer();   // кожен воркер слухає той самий порт
}

// child_process — зовнішня програма
import { spawn } from "node:child_process";
const ffmpeg = spawn("ffmpeg", ["-i", "in.mp4", "out.mp4"]);
```

### L3 — Senior
**Вибір (трейдоф):**
- **worker_threads** — CPU-bound у межах сервісу; легші за процеси, ділять пам'ять (`SharedArrayBuffer` — без копіювання великих даних), transfer для zero-copy ArrayBuffer. Для обробки відеокадрів/обчислень.
- **child_process** — запуск **зовнішніх бінарників** (ffmpeg, GStreamer-утиліти) або повна ізоляція; IPC через serialization (дорого для великих даних).
- **cluster** — горизонтальне масштабування HTTP на всі ядра (майстер балансує з'єднання через SO_REUSEPORT/round-robin). Альтернатива — N контейнерів за балансувальником (часто краще для k8s).

**Сучасне:** для веб-масштабу часто **контейнери + оркестратор** замість `cluster` (простіше масштабувати/деплоїти). `cluster` — коли треба багатоядерність в одному інстансі.

---

## 81. ES modules vs CommonJS ⭐

### L1 — Junior
Два способи модулів у JS:
- **CommonJS (CJS)** — старий Node: `require()` / `module.exports`.
- **ES Modules (ESM)** — сучасний стандарт: `import` / `export`.

```javascript
// CommonJS
const fs = require("fs");
module.exports = { foo };

// ESM
import fs from "node:fs";
export { foo };
```

### L2 — Middle
| | CommonJS | ES Modules |
|---|---|---|
| Синтаксис | `require`/`module.exports` | `import`/`export` |
| Завантаження | синхронне, у рантаймі | асинхронне, статичний аналіз |
| Tree-shaking | ні | **так** (видалення невикористаного) |
| Top-level await | ні | **так** |
| `__dirname`/`__filename` | є | немає (`import.meta.url`) |
| Динамічний імпорт | `require(var)` | `await import(var)` |
| Активація | за замовчуванням | `"type": "module"` або `.mjs` |

**Gotcha:** не можна `require()` ESM-модуль напряму (різні системи); ESM може `import` CJS (з нюансами default-експорту). Змішування — джерело болю.

### L3 — Senior
**Чому ESM — майбутнє:** **статична структура** (import'и відомі до виконання) → tree-shaking (бандлери видаляють мертвий код), кращий аналіз, browser-сумісність (один стандарт фронт+бек), top-level await. **CJS** — динамічний (require у будь-якому місці, умовний), синхронний → простіший, але не оптимізується.

**Трейдоф/реальність:** екосистема **в перехідному стані** — багато пакетів CJS, interop болючий (dual packages, `__dirname` через `import.meta`, named exports з CJS). Сучасні проєкти йдуть на ESM (`"type": "module"`), але legacy/сумісність тримає CJS. Node підтримує обидва. Senior знає нюанси interop (умовні exports у package.json, `.mjs`/`.cjs`).

---

## 82. EventEmitter з `node:events` ⭐

### L1 — Junior
**EventEmitter** — механізм **«підписка-публікація»** всередині процесу: один код «емітить» подію, інший «слухає» й реагує. Багато Node-API на ньому (streams, http server).

```javascript
import { EventEmitter } from "node:events";
const bus = new EventEmitter();
bus.on("frame", (data) => console.log("кадр:", data));   // слухач
bus.emit("frame", { id: 1 });                            // подія
```

### L2 — Middle
```javascript
const emitter = new EventEmitter();
emitter.on("event", handler);          // підписатись (багато разів)
emitter.once("event", handler);        // лише ОДИН раз
emitter.emit("event", arg1, arg2);     // викликати всіх слухачів
emitter.removeListener("event", handler);  // відписатись (проти витоку!)
emitter.off("event", handler);         // = removeListener
emitter.listenerCount("event");
```
**Де в Node:** `http.Server` (`.on("request")`), streams (`.on("data")`), `process` (`.on("SIGTERM")`), сокети. Власні EventEmitter — для подієвої архітектури (обробники подій обладнання — як у відео-вакансії).

**Gotcha:** не відписані listeners → **витік пам'яті** + `MaxListenersExceededWarning` (за замовч. ліміт 10). Використовуй `once` для одноразових; прибирай listeners.

### L3 — Senior
EventEmitter — **синхронний** за замовчуванням: `emit` викликає слухачів **по черзі, синхронно** (не через event loop) → важкий слухач блокує. Це не Pub/Sub між процесами (лише в межах процесу). Помилка в слухачі без обробки `error`-події → краш процесу (особлива подія `error` — якщо нема слухача, кидається).

**Трейдоф:** проста подієва декомпозиція (розв'язка компонентів) ↔ синхронність (блокує), складність трасування (хто на що підписаний), витоки listeners. Для async-подій — обгортати в `setImmediate`/проміси. Для між-процесної/розподіленої події — брокер (Redis pub/sub, Kafka), не EventEmitter.

---

## 83. Скільки ядер задіяно за замовчуванням?

### L1 — Junior
**Одне.** JS-код Node виконується в **одному потоці** на одному ядрі. Щоб задіяти всі ядра — `cluster`/`worker_threads`.

### L2 — Middle
- **JS-виконання** — один потік (один core).
- **libuv thread pool** (4 потоки) — використовує кілька ядер для fs/crypto/dns (питання 89), але це не «твій» JS.
- **V8 GC** — частина роботи в окремих потоках.
Тобто «за замовчуванням» твій код — на одному ядрі; службові речі — трохи більше.

### L3 — Senior
**Чому один потік для JS:** модель Node — event loop на одному потоці (немає shared-mutable-state гонок у JS-коді). Наслідок: 8-ядерний сервер із одним Node-процесом використовує **~1 ядро** для застосунку → решта простоює. Тому в проді: **`cluster`** (N процесів) або **N контейнерів** = кількість ядер, за балансувальником. CPU-bound → worker_threads. Це фундаментальне обмеження, яке senior враховує при capacity planning (зв'язок з питаннями 67, 80).

---

**Далі:** [07_nodejs_middle_q84_q96.md](07_nodejs_middle_q84_q96.md) — middleware, EventEmitter, стрими, сигнали, pino.
