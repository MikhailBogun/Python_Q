# Python-відповіді Q1–Q8 (конкурентність + пам'ять/бінарні дані)

> Формат — **Принцип Сходів**: L1 Junior → L2 Middle → L3 Senior.
> 🆕 (memoryview, struct) — детально з кодом; 🔗 — стисло + відео-контекст + посилання на повну відповідь.

---

## 1. 🔗 GIL: threading vs multiprocessing vs asyncio

### L1 — Junior
**GIL (Global Interpreter Lock)** — лише один потік виконує Python-байткод одночасно. Тому:
- **CPU-bound** (енкодинг кадрів) → `multiprocessing` / код на C.
- **I/O-bound** (роздача стриму) → `threading` / `asyncio`.

### L2 — Middle
```python
# CPU-bound: енкодинг по ядрах (обхід GIL)
from concurrent.futures import ProcessPoolExecutor
with ProcessPoolExecutor() as ex:
    encoded = list(ex.map(encode_frame, frames))

# I/O-bound: роздача сегментів тисячам клієнтів
import asyncio
async def serve(client):
    async for seg in segments:
        await client.send(seg)
```
**Ключове для відео:** GStreamer/PyAV/numpy/OpenCV **відпускають GIL** у важких C-операціях → потоки можуть паралелити енкодинг через них. Python = диригент, важке = C.

### L3 — Senior
GIL існує через неатомарний reference counting. Архітектура: `asyncio` (мережа) + делегування важкого в C (енкодинг відпускає GIL) + `multiprocessing` (паралельний транскодинг). Передача кадрів між процесами — дорога (pickle) → `SharedMemory`/zero-copy.

**📖 Повна відповідь:** [01_answers_q1_q5.md](01_answers_q1_q5.md) Q1 + [answers/02_python.md](../answers/02_python.md) п.30.

---

## 2. 🔗 async/await та event loop

### L1 — Junior
**asyncio** — один потік обслуговує багато I/O-задач, чергуючись на `await` (як офіціант на багато столиків). Для роздачі стриму/мережі — ідеально.

### L2 — Middle
```python
import asyncio
async def handle_viewer(reader, writer):
    while chunk := await read_segment():
        writer.write(chunk)
        await writer.drain()        # backpressure: не переповнити буфер

# Паралельно тягнути кілька джерел:
results = await asyncio.gather(fetch(s1), fetch(s2), fetch(s3))
```
**Gotcha:** блокуючий виклик (важкий CPU, `time.sleep`, `requests`) у корутині **вішає весь loop** → усі глядачі стоять. Виносити в `asyncio.to_thread()` / executor.

### L3 — Senior
Event loop поверх `epoll`/`kqueue` — «спить» на I/O, прокидається на події. Cooperative (перемикання лише на `await`) → менше гонок, але один «жадібний» виклик блокує всіх. Для відео: async для **роздачі/оркестрації**, важке кодування — окремо (C/процеси).

**📖 Повна відповідь:** [answers/06_python_advanced.md](../answers/06_python_advanced.md) п.73.

---

## 3. 🔗 Генератори та ітератори (потокова обробка) ⭐

### L1 — Junior
**Аналогія — конвеєр, а не склад.** Генератор видає елементи **по одному на вимогу**, не тримаючи все в пам'яті. **Відео — це потік**, тому генератори природні: обробляй кадр за кадром, не вантажачи весь файл/потік.

```python
def read_frames(path):
    with open(path, "rb") as f:
        while chunk := f.read(FRAME_SIZE):
            yield chunk             # один кадр — O(1) пам'яті
```

### L2 — Middle
```python
# Конвеєр обробки через генератори — ліниво, O(1) пам'яті
def pipeline(source):
    frames = read_frames(source)
    decoded = (decode(f) for f in frames)      # genexpr
    processed = (enhance(d) for d in decoded)
    return processed                            # нічого ще не виконано!

for frame in pipeline("stream.ts"):             # тягнемо по одному
    encode(frame)
```
**Перевага для стримінгу:** обробка потоку, **більшого за RAM** (години відео), із постійною пам'яттю. Можна обірвати будь-коли.

### L3 — Senior
Генератор зберігає **frame** (стан) між викликами — це корутина на рівні реалізації. `O(1)` пам'яті проти `O(n)` у списку — критично для довгих потоків. Трейдоф: одноразовість, немає `len()`/індексації, складніший дебаг. `yield from` для делегування підгенераторам (композиція pipeline-стадій).

**📖 Повна відповідь:** [answers/02_python.md](../answers/02_python.md) п.32, 34, 37.

---

## 4. 🔗 Профілювання й оптимізація

### L1 — Junior
**Спершу виміряй, потім оптимізуй.** Не вгадуй, де повільно — `cProfile`/`py-spy` покажуть гаряче місце.

### L2 — Middle
```python
import cProfile
cProfile.run("process_video(frames)")
# py-spy для прода (без зміни коду): py-spy top --pid <PID>
```
Типове у відео: зайве копіювання кадрів (→ zero-copy, Q6), Python-цикли по пікселях (→ numpy), per-frame overhead.

### L3 — Senior
Ієрархія: алгоритм → делегування в C (відпускає GIL) → zero-copy → паралелізм → мікрооптимізації. Метрики відео: **frames dropped**, **encode latency/frame**, **event loop lag**. `py-spy` (sampling, без overhead) — стандарт для живого прода.

**📖 Повна відповідь:** [02_answers_q6_q10.md](02_answers_q6_q10.md) Q7.

---

## 5. 🔗 Керування пам'яттю: GC + reference counting + витоки (24/7) ⭐

### L1 — Junior
Python чистить пам'ять автоматично: **reference counting** (лічильник посилань → 0 = звільнити одразу) + **cyclic GC** (ловить циклічні посилання). Для **24/7 сервісу** головна загроза — **memory leak** (пам'ять росте за дні аптайму → OOM).

### L2 — Middle
```python
import gc, tracemalloc

tracemalloc.start()
# ... працює сервіс ...
snapshot = tracemalloc.take_snapshot()
for stat in snapshot.statistics("lineno")[:10]:
    print(stat)                    # де найбільше алокацій

gc.collect()                       # примусовий збір циклів
```
**Типові витоки у live-сервісі:**
- Необмежений буфер/кеш кадрів (росте вічно) → bounded `deque(maxlen=N)` (Q9).
- Замикання/callbacks, що тримають великі об'єкти.
- Глобальні списки, куди весь час `append`.
- Циклічні посилання + `__del__` (заважають GC).

### L3 — Senior
**Refcount** — детерміновано (звільнення миттєве), але не ловить цикли й тримає GIL. **Generational GC** — для циклів (3 покоління, «молоді вмирають швидко»). Для відео-сервісу кадри великі (~6MB) → навіть короткий витік швидко з'їдає RAM.

**Інструменти діагностики витоку:** `tracemalloc` (де алокації), `objgraph` (хто тримає посилання), моніторинг RSS у часі, `gc.get_objects()`. `weakref` для кешів, що не повинні тримати об'єкти. Інколи `gc.freeze()` після старту (оптимізація форк-моделі, менше copy-on-write).

**📖 Повна відповідь:** [answers/06_python_advanced.md](../answers/06_python_advanced.md) п.75, 77.

---

## 6. 🆕 Бінарні дані: `bytes`, `bytearray`, `memoryview`, buffer protocol ⭐

### L1 — Junior
**Аналогія — дивитись у вікно vs виносити меблі.** Відеокадр — це масив байтів (~6MB для 1080p). Копіювати його щоразу — дорого. **`memoryview`** дозволяє **дивитись** на частину буфера **без копіювання** (zero-copy), як вікно в пам'ять.

```python
data = bytes([1, 2, 3, 4])      # незмінний масив байтів
buf = bytearray([1, 2, 3, 4])   # ЗМІНЮВАНИЙ масив байтів
buf[0] = 99                      # ✅ можна (bytearray)
```

### L2 — Middle
**Три типи + різниця:**
| Тип | Змінюваний | Призначення |
|---|---|---|
| `bytes` | ❌ | незмінні бінарні дані (результат read, мережа) |
| `bytearray` | ✅ | змінюваний буфер (накопичення, in-place зміни) |
| `memoryview` | — | **zero-copy view** в інший буфер |

**Головна пастка — slicing КОПІЮЄ:**
```python
frame = bytearray(6_220_800)     # 1920×1080×3 = ~6MB кадр

# ❌ slice bytes/bytearray — КОПІЮЄ (нові 2MB!)
chunk = frame[0:2_073_600]       # копія першої третини

# ✅ memoryview — НЕ копіює (вікно в той самий буфер)
mv = memoryview(frame)
chunk = mv[0:2_073_600]          # zero-copy! спільна пам'ять
chunk[0] = 255                   # міняє оригінальний frame (якщо bytearray)
```

**Чому критично для відео:** при 30fps кожна зайва копія кадру = +180MB/с навантаження на пам'ять/CPU. `memoryview` прибирає це.

**Gotcha:** `memoryview` на `bytes` — read-only (бо bytes незмінні); на `bytearray`/numpy — можна писати. Зрізати/передавати в C-бібліотеки без копії.

### L3 — Senior
**Buffer protocol** — C-рівневий інтерфейс, що дозволяє об'єкту **експонувати свою сиру пам'ять** іншим без копіювання. Його реалізують `bytes`, `bytearray`, `array.array`, **numpy**, кадри з PyAV/OpenCV. Тому `memoryview(numpy_frame)` чи передача numpy-масиву в GStreamer `appsrc` — **zero-copy**.

```python
mv = memoryview(frame)
mv.nbytes            # розмір без копіювання
mv.cast("B")         # переінтерпретувати формат (напр. байти ↔ uint8)
sub = mv[100:200]    # subview, спільна пам'ять
mv.release()         # звільнити view (важливо для буферів, що блокуються)
```

**Трейдоф/застосування у стримінгу:**
- **Zero-copy ланцюг:** capture → memoryview → encode → memoryview → network, без жодного копіювання 6MB-кадрів. Це **головна оптимізація** відео-pipeline у Python.
- **Інтеграція з C:** numpy/OpenCV/PyAV/GStreamer спілкуються через buffer protocol — кадр живе в одному буфері, всі бачать його через views.
- **Обережно:** поки memoryview живий, він **блокує** зміну розміру/звільнення базового буфера (`BufferError`). Звільняй (`.release()` / `with memoryview(...)`).

**Senior-суть:** розуміння `memoryview` + buffer protocol — це **те, що відрізняє відео-інженера** від звичайного бекендера. Уся продуктивність обробки кадрів у Python тримається на zero-copy через buffer protocol; без нього Python нежиттєздатний для відео.

> ⚠️ Деталі взаємодії з numpy/PyAV/GStreamer (формати, strides, contiguous vs non-contiguous) — звіряй з docs конкретної бібліотеки.

---

## 7. 🆕 `struct` та бінарні протоколи (парсинг пакетів) ⭐

### L1 — Junior
**Аналогія — розрізати ковбасу за схемою.** Мережевий/медіа-пакет — це **послідовність байтів** за чіткою схемою (перші 2 байти — версія, наступні 2 — номер...). Модуль **`struct`** пакує/розпаковує байти за **форматним рядком**.

```python
import struct
# Розпакувати: 2 байти big-endian як ціле число
seq, = struct.unpack(">H", b"\x00\x2a")   # 42
packed = struct.pack(">H", 42)             # b'\x00\x2a'
```

### L2 — Middle
**Форматні символи:**
| Символ | Тип | Розмір |
|---|---|---|
| `B` | unsigned char | 1 |
| `H` | unsigned short | 2 |
| `I` | unsigned int | 4 |
| `Q` | unsigned long long | 8 |
| `>` / `!` | big-endian (мережевий порядок) | — |
| `<` | little-endian | — |

**Реальний приклад — парсинг RTP-заголовка** (12 байтів, мережевий порядок):
```python
import struct

def parse_rtp_header(data: bytes) -> dict:
    # Байт0: V(2) P(1) X(1) CC(4); Байт1: M(1) PT(7); потім seq, timestamp, SSRC
    b0, b1, seq, timestamp, ssrc = struct.unpack("!BBHII", data[:12])
    return {
        "version": b0 >> 6,            # старші 2 біти
        "padding": (b0 >> 5) & 1,
        "extension": (b0 >> 4) & 1,
        "cc": b0 & 0x0F,               # молодші 4 біти
        "marker": b1 >> 7,
        "payload_type": b1 & 0x7F,     # 7 біт
        "sequence": seq,
        "timestamp": timestamp,
        "ssrc": ssrc,
    }
```

**Gotcha:** **endianness** — мережеві протоколи (RTP, TS) — **big-endian** (`!` або `>`). Переплутаєш порядок → числа «навиворіт». `!` = network byte order (= big-endian) — канонічно для протоколів.

### L3 — Senior
**`struct.Struct` (компільований) для гарячого шляху:**
```python
# Компілюємо формат ОДИН раз → швидше при мільйонах пакетів
RTP = struct.Struct("!BBHII")

def parse_fast(data: memoryview):       # + zero-copy через memoryview (Q6)
    b0, b1, seq, ts, ssrc = RTP.unpack_from(data, 0)   # без зрізу/копії
    ...
```
- `Struct.unpack_from(buffer, offset)` — парсить **з буфера за зміщенням** без копіювання (працює з `memoryview`!) → поєднання Q6+Q7 для zero-copy парсингу.
- `Struct` об'єкт кешує скомпільований формат → швидше за `struct.unpack` щоразу.
- `struct.calcsize(fmt)` — розмір за форматом.

**Застосування у відео:** парсинг RTP/RTCP, MPEG-TS пакетів (188 байт, синхробайт 0x47), NAL-юнітів H.264, заголовків контейнерів. Senior комбінує `struct` (схема) + `memoryview` (zero-copy) + бітові операції (розпаковка прапорів) — це типова задача роботи з медіа на байтовому рівні.

**Трейдоф:** `struct` — стандартний, простий для фіксованих схем ↔ для складних/змінних форматів (вкладені, опціональні поля) краще спеціалізовані парсери (construct, kaitai) або C-розширення. Для гарячого шляху з мільйонами пакетів — `Struct` + `unpack_from` або взагалі парсинг у C (GStreamer уже це робить).

> ⚠️ Точні формати протоколів (RTP RFC 3550, MPEG-TS) звіряй зі специфікаціями — біти/поля мають точну розкладку.

---

## 8. 🔗 Mutable vs immutable + пастка default args

### L1 — Junior
**Immutable** (незмінні): `int, str, tuple, bytes, frozenset`. **Mutable** (змінювані): `list, dict, set, bytearray`. Для буферів — `bytearray` (можна міняти на місці).

### L2 — Middle
**Класична пастка — mutable default argument:**
```python
# ❌ БАГ: список/буфер створюється ОДИН раз, шариться між викликами
def add_frame(frame, buffer=[]):
    buffer.append(frame)
    return buffer

# ✅ Правильно:
def add_frame(frame, buffer=None):
    if buffer is None:
        buffer = []
    buffer.append(frame)
    return buffer
```
**Чому небезпечно у відео:** акумулятор кадрів як default-аргумент → витік пам'яті + змішування даних між потоками/викликами.

### L3 — Senior
Default-аргумент обчислюється **один раз** при визначенні функції (не на кожен виклик) → mutable default шариться. Immutable безпечні (їх не змінити). Для буферів свідомо бери `bytearray`/`deque`, але **не** як default-аргумент. Immutability дає thread-safety (нічого не змінюється — нема гонок) — корисно в конкурентному відео-коді.

**📖 Повна відповідь:** [answers/02_python.md](../answers/02_python.md) п.25.

---

**Далі:** [05_python_answers_q9_q13.md](05_python_answers_q9_q13.md) — структури даних (ring buffer, producer-consumer) + надійність.
