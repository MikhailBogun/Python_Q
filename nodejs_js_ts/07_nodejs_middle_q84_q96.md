# Блок 7. Node.js — Middle/Senior (питання 84–96)

> Формат — **Принцип Сходів**: L1 → L2 → L3. Стрими — центральна тема цього блоку.

---

## 84. Middleware — чому там, а не в коді сервісу? ⭐

### L1 — Junior
**Middleware** — функція в «конвеєрі» обробки запиту (між отриманням і відповіддю), що робить **наскрізні задачі** (auth, логування, парсинг). *(База — Express-блок Q17.)*

**Чому окремо, а не в сервісі:** щоб **бізнес-логіка лишалась чистою**, а спільні речі (auth/logging) — переиспользувались, а не дублювались у кожному хендлері.

### L2 — Middle
```javascript
// ❌ Якби auth/logging були В КОЖНОМУ сервісі — дублювання
app.get("/orders", (req, res) => {
  if (!checkAuth(req)) return res.status(401).end();   // дубль у кожному!
  logRequest(req);                                      // дубль!
  res.json(getOrders());                                // ← лише ЦЕ бізнес-логіка
});

// ✅ Middleware — спільне винесено, хендлер чистий
app.use(authMiddleware);     // auth для всіх
app.use(loggingMiddleware);  // logging для всіх
app.get("/orders", (req, res) => res.json(getOrders()));  // лише суть
```

**Чому саме middleware (не в коді сервісу):**
| Причина | Пояснення |
|---|---|
| **DRY** | один auth на 100 ендпоінтів, не 100 копій |
| **Separation of concerns** | бізнес-логіка не змішана з інфраструктурою |
| **Композиція** | складна поведінка з простих незалежних ланок |
| **Переиспользування** | той самий middleware на різних маршрутах |
| **Єдина точка зміни** | поміняв логування — в одному місці |

### L3 — Senior
Middleware реалізує **Chain of Responsibility** + **cross-cutting concerns** (наскрізні аспекти): речі, потрібні **багатьом** хендлерам, але **не є** їх суттю (auth, logging, CORS, rate limit, валідація). Винесення в middleware = **відокремлення інфраструктури від домену** (як декоратори/AOP).

**Чому НЕ в коді сервісу (глибше):** бізнес-логіка має тестуватись/змінюватись **незалежно** від інфраструктури. Якщо auth вшитий у хендлер — не протестуєш логіку без auth, не зміниш auth без зачіпання логіки, дублюєш по всіх ендпоінтах. Middleware = **інверсія**: інфраструктура «обгортає» логіку ззовні. Трейдоф: чистота + переиспользування ↔ неявність (порядок/умови розкидані, складніший трасинг — Express-блок Q19).

---

## 85. Що таке EventEmitter? 

*(Повна відповідь — блок 6, питання 82.)* Стисло:

**EventEmitter** (`node:events`) — внутрішньопроцесний механізм подій (pub-sub): `on`/`once` (підписка), `emit` (публікація), `off`/`removeListener` (відписка). Багато Node-API — EventEmitter'и (streams, http server, process). Синхронний за замовчуванням. Не відписані listeners → витік. Особлива подія `error` (без слухача → краш).

```javascript
import { EventEmitter } from "node:events";
class StreamMonitor extends EventEmitter {}      // успадкувати
const m = new StreamMonitor();
m.on("frame-dropped", (n) => alert(n));
m.emit("frame-dropped", 42);
```

---

## 86. Призначення package.json ⭐

### L1 — Junior
**`package.json`** — «паспорт» Node-проєкту: метадані, **залежності**, **скрипти**, версія, точка входу.

### L2 — Middle
```json
{
  "name": "stream-encoder",
  "version": "1.2.0",
  "type": "module",                    // ESM (питання 81)
  "main": "index.js",                  // точка входу
  "scripts": {
    "start": "node index.js",
    "test": "vitest",
    "dev": "node --watch index.js"
  },
  "dependencies": { "pino": "^9.0.0" },         // потрібні в проді
  "devDependencies": { "vitest": "^2.0.0" },    // лише для розробки
  "engines": { "node": ">=20" }                 // потрібна версія Node
}
```
- **dependencies** vs **devDependencies** — прод vs розробка/тести.
- **scripts** — `npm run <name>`.
- **`type`** — `"module"` (ESM) чи `"commonjs"`.
- **`package-lock.json`** — точні версії всього дерева (відтворюваність — комітити!).

### L3 — Senior
package.json — **контракт проєкту** для npm і Node. Senior-нюанси:
- **`exports`** — контролює, що видно ззовні (entry points, dual ESM/CJS — питання 81).
- **Semver** (`^`, `~`) — `^1.2.0` дозволяє minor/patch, `~` лише patch; lock-файл фіксує точні.
- **`engines`** — гейт версії Node.
- **scripts hooks** — `pre`/`post` (preinstall тощо) — вектор supply-chain атак, обережно.
- Мінімізувати залежності (кожна — ризик + вага). Комітити **lock-файл** (без нього — недетерміновані білди).

---

## 87. Прочитати лог-файл; файл понад 300MB? ⭐

### L1 — Junior
**Малий файл** — `fs.readFile` (весь у пам'ять). **Великий (300MB+)** — **стрим** (`createReadStream`), читати **шматками**, бо весь у пам'ять = OOM + блокування.

### L2 — Middle
```javascript
import { readFile } from "node:fs/promises";
import { createReadStream } from "node:fs";
import { createInterface } from "node:readline";

// ❌ Малий файл ОК; для 300MB — OOM + блокує
const data = await readFile("small.log", "utf8");

// ✅ Великий файл — СТРИМ (постійна пам'ять)
const stream = createReadStream("huge.log", { encoding: "utf8" });
stream.on("data", (chunk) => process(chunk));    // по шматку
stream.on("end", () => console.log("готово"));
stream.on("error", (err) => console.error(err));

// ✅ Построково (логи — рядкові) через readline поверх стриму
const rl = createInterface({ input: createReadStream("huge.log") });
for await (const line of rl) {                   // async iterator — по рядку
  if (line.includes("ERROR")) process(line);
}
```

**Gotcha:** `readFileSync`/`readFile` для 300MB = (1) весь файл у RAM (OOM на кількох паралельних), (2) `readFileSync` ще й **блокує event loop**. Завжди стрим для великих файлів.

### L3 — Senior
**Чому стрим:** постійна пам'ять `O(1)` незалежно від розміру файлу — обробляєш файли **більші за RAM** (зв'язок з Python-генераторами). **Backpressure** (питання 91): якщо обробка повільніша за читання — стрим **призупиняється**, не накопичуючи в пам'яті. `highWaterMark` (дефолт 64KB для файлів) — розмір буфера читання. Для построкової обробки — `readline` (не тримає весь файл). Async iterator (`for await...of`) — сучасний, лінійний спосіб обходу стриму (замість подій).

---

## 88. Цикл подій (event loop) у Node ⭐

### L1 — Junior
**Event loop** — цикл, що обходить «станції» й виконує готові callbacks (таймери, I/O), ніколи не блокуючись. Серце неблокуючості. *(База — Junior-блок Q13.)*

### L2 — Middle
**Фази (libuv), по колу:**
```
timers          → setTimeout/setInterval callbacks
pending callbacks → відкладені системні
idle, prepare   → внутрішнє
poll            → ← НОВИЙ I/O, "спить" тут чекаючи події
check           → setImmediate
close callbacks → socket.on('close')
```
**Між кожним callback** — спорожнення `process.nextTick` + Promise microtasks (вищий пріоритет).

### L3 — Senior
**Ключове (зв'язок з Junior Q10/Q13):**
- **poll** — найважливіша фаза: Node «спить» тут на `epoll`, чекаючи I/O (неблокуюче для потоку).
- **Microtasks > усі фази:** `process.nextTick` → Promise microtasks спорожнюються **між кожним** callback → Promise завжди «обганяє» setTimeout.
- **`setImmediate` (check) vs `setTimeout(0)` (timers):** усередині I/O-callback `setImmediate` завжди перший; у головному модулі — недетерміновано.
- **Голодування loop:** важкий синхронний код у callback блокує перехід фаз → **event loop lag** (моніторити, питання 72). Один блокуючий виклик вішає весь сервер — фундаментальний трейдоф Node.

---

## 89. Thread Pool (Worker Pool) — що це й навіщо? ⭐

### L1 — Junior
**libuv thread pool** — пул потоків (за замовчуванням **4**), що виконує **деякі** асинхронні операції, яким немає неблокуючого ОС-API: файли, DNS, crypto, zlib.

### L2 — Middle
**Що йде в thread pool:**
- `fs.*` (файлові операції)
- `dns.lookup` (не `dns.resolve`)
- `crypto` (pbkdf2, randomBytes, scrypt)
- `zlib` (стиснення)

**Що НЕ йде** (через ОС напряму, epoll): мережеві сокети (HTTP, TCP, UDP).

```bash
# Розмір пулу (дефолт 4, до 1024)
UV_THREADPOOL_SIZE=8 node app.js
```

### L3 — Senior
**Чому пул існує:** мережа має надійний неблокуючий ОС-API (epoll/kqueue) → libuv обходиться без потоків. А **файловий I/O НЕ має** надійного async-API на всіх ОС → libuv емулює асинхронність, виконуючи його **синхронно в потоках пулу**. DNS/crypto/zlib — те саме (CPU/блокуючі).

**Прихований bottleneck (часте senior-питання):** пул = 4 потоки. 5 паралельних `crypto.pbkdf2`/важких fs → 5-й **чекає** в черзі → латентність. Симптом: «чому файлові/crypto-операції повільні під навантаженням?» → пул вичерпано. Лікування: `UV_THREADPOOL_SIZE` (під кількість ядер) або винести в окремий сервіс. Це обмеження **окреме** від event loop (мережа його не торкається).

---

## 90. SIGTERM vs SIGINT ⭐

### L1 — Junior
Обидва — **сигнали зупинки** процесу, які можна перехопити для **graceful shutdown**:
- **SIGTERM** — «чемне прохання завершитись» (від `kill`, оркестратора, `docker stop`).
- **SIGINT** — «переривання» (від **Ctrl+C** у терміналі).

### L2 — Middle
```javascript
async function gracefulShutdown(signal) {
  console.log(`${signal}: закриваюсь...`);
  server.close();                    // перестати приймати нові з'єднання
  await db.close();                  // закрити БД
  await flushLogs();                 // дописати логи
  process.exit(0);
}
process.on("SIGTERM", () => gracefulShutdown("SIGTERM"));  // оркестратор
process.on("SIGINT", () => gracefulShutdown("SIGINT"));    // Ctrl+C
```

| | SIGTERM | SIGINT |
|---|---|---|
| Джерело | `kill`, k8s, `docker stop` | Ctrl+C (термінал) |
| Семантика | «заверши коректно» | «перервати» |
| Перехоплюваний | ✅ | ✅ |
| У проді | основний для shutdown | переважно dev |

### L3 — Senior
**Переваги/недоліки й навіщо graceful shutdown:**
- **SIGTERM** — стандарт для прода: оркестратор шле його, **чекає** (grace period, напр. 30с), потім **SIGKILL** (9, не перехоплюється, рве на місці). Тому на SIGTERM треба **встигнути** прибратись (дозакрити з'єднання, дослати дані) до SIGKILL.
- **SIGINT** — для розробки (Ctrl+C); та сама обробка.
- **SIGKILL/SIGSTOP** — **не перехоплюються** (примусово).

**Чому важливо (24/7):** без graceful shutdown при деплої/рестарті — обриваються активні запити/стріми, губляться недописані дані, з'єднання «висять». Правильний цикл: SIGTERM → перестати приймати нове → дочекати активне (з таймаутом) → закрити ресурси → exit. Недолік: якщо cleanup довший за grace period → SIGKILL обірве. Senior балансує grace period vs швидкість деплою.

---

## 91. Backpressure у стримах ⭐

### L1 — Junior
**Backpressure (зворотний тиск)** — коли **джерело швидше за споживача**: дані накопичуються в буфері → ризик OOM. Рішення — **сповільнити джерело**, поки споживач не наздожене.

**Аналогія — лійка:** ллєш воду швидше, ніж витікає → переповнення. Треба лити повільніше.

### L2 — Middle
```javascript
// write() повертає false, коли буфер переповнений → треба чекати 'drain'
const writable = createWriteStream("out.log");
function write(data) {
  if (!writable.write(data)) {          // false = буфер повний
    writable.once("drain", () => resume());  // чекати, поки спорожніє
    pause();                            // призупинити джерело
  }
}

// ✅ pipe/pipeline керують backpressure АВТОМАТИЧНО
import { pipeline } from "node:stream/promises";
await pipeline(source, transform, destination);  // сам призупиняє/відновлює
```

**Gotcha:** ручне `source.on("data", d => dest.write(d))` **ігнорує** backpressure → якщо dest повільний, пам'ять росте → OOM. **Використовуй `pipeline()`/`pipe()`** — вони керують цим.

### L3 — Senior
**Механізм:** writable-стрим має внутрішній буфер (`highWaterMark`). `write()` повертає `false`, коли буфер перевищено → producer має **призупинитись** і чекати `drain`. `pipe`/`pipeline` роблять це автоматично: коли consumer не встигає, **призупиняють** readable (`pause`), коли встигає — `resume`. Так пам'ять обмежена незалежно від різниці швидкостей.

**Зв'язок із розподіленими системами:** backpressure — це той самий принцип, що bounded queue в producer-consumer (Python Q11) і черги в стрімінгу — **поглинання різниці швидкостей без OOM**. Без нього швидкий producer «затоплює» повільного consumer. Senior завжди використовує `pipeline()` (не ручний `.on("data")`) саме заради коректного backpressure + error handling.

---

## 92. stream.PassThrough і pipe/pipeline ⭐

### L1 — Junior
- **`pipe`/`pipeline`** — з'єднати стрими в ланцюг (джерело → ... → призначення), щоб дані текли з backpressure.
- **`PassThrough`** — стрим, що **пропускає дані без змін** (для моніторингу/розгалуження/дебагу).

### L2 — Middle
```javascript
import { pipeline } from "node:stream/promises";
import { createReadStream, createWriteStream } from "node:fs";
import { createGzip } from "node:zlib";
import { PassThrough } from "node:stream";

// pipeline — ланцюг з backpressure + обробка помилок + cleanup
await pipeline(
  createReadStream("in.log"),
  createGzip(),                        // стиснути
  createWriteStream("in.log.gz")
);

// PassThrough — «прозорий» стрим: підглянути/виміряти, не змінюючи
const monitor = new PassThrough();
let bytes = 0;
monitor.on("data", (chunk) => { bytes += chunk.length; });  // лічильник
await pipeline(source, monitor, destination);  // дані течуть, monitor рахує
```

**`pipe` vs `pipeline`:**
```javascript
source.pipe(transform).pipe(dest);   // старий — НЕ передає помилки, немає cleanup
await pipeline(source, transform, dest);  // ✅ помилки + cleanup усього ланцюга
```

### L3 — Senior
**`pipeline` > `.pipe()` (важливо):** `.pipe()` **не пробрасує помилки** по ланцюгу й **не чистить** стрими при збої → витоки/незакриті дескриптори. `pipeline()` (з `stream/promises`) — коректно обробляє помилки на **кожному** етапі й гарантовано закриває всі стрими. У проді — завжди `pipeline`.

**PassThrough — навіщо:** Transform, що нічого не трансформує. Юзкейси: **моніторинг** (виміряти throughput/кількість байтів, не змінюючи потік), **tee** (розгалузити в кілька призначень), **відкладене з'єднання** (повернути стрим зараз, під'єднати джерело пізніше), **тестування**. Це «прозора труба» з хуками на події.

---

## 93. Події data/end/error/finish у стримах ⭐

### L1 — Junior
| Подія | Коли | Тип стриму |
|---|---|---|
| **`data`** | прийшов шматок | Readable |
| **`end`** | дані закінчились (читання) | Readable |
| **`error`** | сталася помилка | будь-який |
| **`finish`** | усе записано | Writable |

### L2 — Middle
```javascript
readable.on("data", (chunk) => process(chunk));   // шматок (Readable)
readable.on("end", () => console.log("читання завершено"));  // Readable
writable.on("finish", () => console.log("запис завершено")); // Writable
stream.on("error", (err) => console.error(err));  // ОБОВ'ЯЗКОВО

// + close — стрим закрито (ресурси звільнено)
stream.on("close", () => cleanup());
```

**Gotcha:** `end` (Readable — дані скінчились) ≠ `finish` (Writable — все записано) ≠ `close` (ресурс закрито). Не плутати: Readable дає `end`, Writable — `finish`.

### L3 — Senior
**Сучасний підхід замість подій — async iterators:**
```javascript
for await (const chunk of readable) {   // замість .on("data")+.on("end")
  await process(chunk);                  // лінійно, з backpressure
}
```
`for await...of` обробляє `data`/`end` автоматично, дає лінійний код (не callback-події), коректно з backpressure. Події (`data`/`end`/`finish`) — нижчий рівень; для більшості задач `pipeline()` або async iterator чистіші. `error` — завжди обробляй (без слухача → краш).

---

## 94. Як обробляти помилки в стримах? ⭐

### L1 — Junior
**Завжди слухай подію `error`** — інакше помилка стриму **валить процес** (необроблена). Або використовуй `pipeline()`, що робить це за тебе.

### L2 — Middle
```javascript
// ❌ pipe НЕ передає помилки — помилка source НЕ дійде до обробника dest
source.pipe(dest);
source.on("error", handle);    // треба на КОЖНОМУ стримі окремо — легко забути

// ✅ pipeline — обробка помилок усього ланцюга в одному місці + cleanup
import { pipeline } from "node:stream/promises";
try {
  await pipeline(source, transform, dest);
} catch (err) {
  console.error("стрим впав:", err);    // помилка з БУДЬ-ЯКОГО етапу
}
```

### L3 — Senior
**Чому `.pipe()` небезпечний для помилок:** при помилці в середині ланцюга `.pipe()` **не закриває** інші стрими й **не пробрасує** помилку → витік дескрипторів + незавершені стрими + можливий краш (необроблений `error`). **`pipeline()`** вирішує обидва: централізована обробка помилок + гарантований cleanup усіх стримів (destroy) при збої.

**Правила (senior):**
- `pipeline()` замість `.pipe()` для будь-якого ланцюга.
- На окремих стримах (поза pipeline) — **завжди** `.on("error")`.
- `stream.destroy(err)` — коректно зруйнувати стрим із помилкою.
- Не ігнорувати `error` (необроблений → `uncaughtException` → краш, питання 71).

---

## 95. Приклади стримів різних типів ⭐

### L1 — Junior
4 типи: **Readable** (читаємо), **Writable** (пишемо), **Duplex** (обидва), **Transform** (перетворюємо). *(База — Junior-блок Q12.)*

### L2 — Middle
```javascript
import { createReadStream, createWriteStream } from "node:fs";
import { createGzip } from "node:zlib";
import { Transform, PassThrough } from "node:stream";
import { pipeline } from "node:stream/promises";

// Readable — джерело (файл, HTTP-запит, process.stdin)
const readable = createReadStream("in.txt");

// Writable — призначення (файл, HTTP-відповідь, process.stdout)
const writable = createWriteStream("out.txt");

// Transform — вхід → перетворення → вихід (gzip, шифрування, парсинг)
const upper = new Transform({
  transform(chunk, enc, cb) { cb(null, chunk.toString().toUpperCase()); },
});

// Duplex — і читання, і запис незалежно (TCP-сокет)
// net.Socket — приклад Duplex

// Реальний конвеєр: читати → upper → gzip → писати
await pipeline(readable, upper, createGzip(), writable);
```

### L3 — Senior
| Тип | Приклади в Node | Призначення |
|---|---|---|
| **Readable** | `fs.createReadStream`, `http req`, `process.stdin`, `net.Socket` | джерело даних |
| **Writable** | `fs.createWriteStream`, `http res`, `process.stdout` | приймач |
| **Duplex** | `net.Socket` (TCP), WebSocket | незалежні читання+запис |
| **Transform** | `zlib.createGzip`, crypto cipher | вхід→f→вихід |
| **PassThrough** | моніторинг/tee | прозора труба (питання 92) |

**Object mode** — стрими можуть нести **об'єкти** (не лише Buffer/string): `objectMode: true` → конвеєри обробки даних (ETL, парсинг → трансформація → запис). HTTP `req`/`res` — стрими (тому потокова обробка тіла «з коробки»). Senior мислить стрімами для **будь-яких великих/безперервних даних** (файли, мережа, обробка) — `O(1)` пам'яті + backpressure.

---

## 96. Чи працювали з pino?

### L1 — Junior
**pino** — **дуже швидкий** структурований (JSON) логер для Node. Стандарт для продакшн-логування (замість `console.log`).

```javascript
import pino from "pino";
const log = pino();
log.info({ streamId: 42 }, "стрім стартував");   // → JSON-рядок
log.error({ err }, "помилка енкодера");
```

### L2 — Middle
```javascript
const log = pino({ level: "info" });

log.info({ userId: 7, route: "/stream" }, "запит");   // структуровано
log.warn("попередження");
log.error({ err }, "помилка");

// Child logger — успадковує контекст (correlation ID на запит)
const reqLog = log.child({ requestId: "abc-123" });
reqLog.info("обробка");        // автоматично додасть requestId

// Redaction — приховати чутливі поля
const log2 = pino({ redact: ["password", "token", "*.secret"] });
```

**Чому pino, не winston/console.log:**
- **Швидкий** — мінімальний overhead (важливо: логування не має гальмувати, зв'язок з event loop).
- **JSON** — структуровано → легко шукати/агрегувати (ELK/Loki).
- **Child loggers** — контекст (correlation ID).

### L3 — Senior
**Чому pino швидкий (під капотом):** мінімізує роботу в основному потоці — серіалізує в JSON ефективно, а **транспорт** (запис у файл/мережу, форматування) виносить в **окремий процес/worker** (`pino.transport`) → не блокує event loop. `console.log` синхронний на TTY → у проді може блокувати; winston гнучкіший, але повільніший.

**Best practices (senior):**
- **Структуровані логи** (об'єкт + повідомлення), не рядкова конкатенація → searchable.
- **Рівні** (trace/debug/info/warn/error/fatal) + керування через env.
- **Child loggers** для correlation ID (трасування запиту через сервіси).
- **Redaction** секретів (паролі/токени — GDPR, питання безпеки).
- Логи в **stdout** (12-factor) → збирає оркестратор/агрегатор, не писати в файли напряму.

**Чесно:** якщо досвіду з pino нема — скажи прямо («працював з winston / console, з pino знайомий концептуально — швидкий JSON-логер з child loggers і async-транспортом»). Чесність > блеф (правило з нашого підходу).

---

## ✅ Підсумок блоку
**Стрими — наскрізна тема:** Readable/Writable/Duplex/Transform/PassThrough (92, 95), backpressure (91), pipeline > pipe (92, 94), події data/end/error/finish + async iterators (93), великі файли (87). **Ключове senior-правило:** `pipeline()` замість `.pipe()` (backpressure + помилки + cleanup).

**Інфраструктура:** middleware = cross-cutting concerns окремо від домену (84), graceful shutdown на SIGTERM (90), pino для structured logging (96), error types (71 — у блоці 6).

**Зв'язки:** стрими ↔ Python producer-consumer/backpressure; event loop/thread pool ↔ Junior-блок Q13/Q9; пам'ять (76-78) ↔ Python GC.
