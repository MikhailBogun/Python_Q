# Python-відповіді Q9–Q13 (структури даних + надійність)

> Формат — **Принцип Сходів**: L1 → L2 → L3.
> 🆕 (ring buffer, producer-consumer) — детально з кодом; 🔗 — стисло + контекст + посилання.

---

## 9. 🆕 Ring buffer / `deque` для буферизації кадрів ⭐

### L1 — Junior
**Аналогія — карусель на N місць.** Треба тримати **останні N кадрів** (jitter buffer, DVR-вікно, аналіз руху). **Ring buffer (кільцевий буфер)** — фіксований розмір: коли заповнений, новий кадр **витісняє найстаріший**. У Python — `collections.deque(maxlen=N)`.

```python
from collections import deque

frame_buffer = deque(maxlen=30)     # останні 30 кадрів (1 сек @ 30fps)
frame_buffer.append(new_frame)      # старий автоматично випадає при переповненні
```

### L2 — Middle
**Чому `deque`, а не `list`:**
```python
# ❌ list — O(n) на видалення з початку + ручне обмеження розміру
buffer = []
buffer.append(frame)
if len(buffer) > 30:
    buffer.pop(0)              # O(n)! зсуває всі елементи

# ✅ deque(maxlen) — O(1) з обох кінців + авто-обмеження
buffer = deque(maxlen=30)
buffer.append(frame)          # O(1), старий випадає сам
```

| Операція | `list` | `deque` |
|---|---|---|
| append (кінець) | O(1) аморт. | **O(1)** |
| pop(0) / popleft | **O(n)** | **O(1)** |
| auto-maxlen | вручну | **вбудовано** |
| доступ за індексом | O(1) | O(n) усередині |

**Gotcha:** `deque` дає O(1) з кінців, але **O(n) доступ за індексом усередині** (на відміну від list). Для буфера кадрів (додаємо в кінець, читаємо останні) — ідеально; для частого довільного доступу за індексом — гірше.

### L3 — Senior
**Manual ring buffer (zero-allocation, для гарячого шляху):** `deque(maxlen)` алокує/звільняє об'єкти при витісненні. Для максимального перформансу (мільйони кадрів, GC-тиск) — **попередньо виділений** кільцевий буфер фіксованого розміру, що **перевикористовує** слоти:
```python
class RingBuffer:
    """Fixed-size, перевикористовує слоти — мінімум алокацій/GC-тиску."""
    def __init__(self, size: int):
        self._buf: list = [None] * size      # виділено наперед
        self._size = size
        self._head = 0
        self._count = 0

    def append(self, item) -> None:
        self._buf[self._head] = item          # перезапис слота (без алокації)
        self._head = (self._head + 1) % self._size
        self._count = min(self._count + 1, self._size)

    def latest(self, n: int = 1) -> list:
        """Останні n елементів (від найновішого до найстарішого)."""
        out = []
        for i in range(min(n, self._count)):
            idx = (self._head - 1 - i) % self._size
            out.append(self._buf[idx])
        return out
```

**Застосування у стримінгу:**
- **Jitter buffer** — згладжування нерівномірного прибуття пакетів (Q10 у відео-відповідях).
- **DVR / instant replay** — тримати останні N секунд для перемотки.
- **Аналіз руху / детекція** — порівняння поточного кадру з попередніми.
- **Pre-recording** — буфер до тригера (зберегти що було «до» події).

**Трейдоф:** `deque(maxlen)` — простий, ідіоматичний, O(1), достатній для 99% ↔ алокує при витісненні. Manual ring buffer — нуль алокацій (важливо для real-time без GC-пауз) ↔ більше коду, ручне керування. Senior бере `deque` за замовчуванням, manual — лише коли профайлер показав GC-тиск від витіснення (real-time, високий fps).

> ⚠️ Для thread-safe буфера між capture/encode потоками — або `deque` (append/popleft атомарні в CPython завдяки GIL), або краще `queue.Queue` (Q11) з явною синхронізацією.

---

## 10. 🔗 Складність структур: list/deque/dict/set — коли що

### L1 — Junior
Обирай структуру за **патерном доступу**:
- **list** — впорядкована послідовність, доступ за індексом.
- **deque** — черга/буфер з обох кінців (Q9).
- **dict/set** — швидкий пошук «чи є» / за ключем (O(1)).

### L2 — Middle
| Структура | Пошук | Вставка | Видалення | Коли у відео |
|---|---|---|---|---|
| `list` | O(n) | O(1) кінець | O(n) початок | послідовність, індекс |
| `deque` | O(n) | **O(1) обидва кінці** | O(1) кінці | буфер кадрів, черга |
| `dict`/`set` | **O(1)** | O(1) | O(1) | реєстр потоків, дедуплікація |

**Gotcha:** `if x in big_list` — O(n); `if x in big_set` — O(1). У циклі це O(n²) → O(n). `list.pop(0)` — O(n), для черги бери `deque.popleft()` (O(1)).

### L3 — Senior
dict/set — хеш-таблиці (O(1) середній, O(n) гірший при колізіях). deque — двозв'язний список блоків (O(1) кінці, O(n) індекс). Вибір = функція від патерну: реєстр активних потоків за ID → dict; буфер кадрів → deque; пріоритетна обробка → heap. «basic algorithms + complexity» (вимога вакансії) перевіряє саме це — назви Big-O і обґрунтуй вибір.

**📖 Повна відповідь:** [answers/02_python.md](../answers/02_python.md) п.47, 48, 50 + [answers/algorithms/README.md](../answers/algorithms/README.md).

---

## 11. 🆕 Producer-Consumer: `queue.Queue` / `asyncio.Queue` ⭐

### L1 — Junior
**Аналогія — кухня з роздачею.** Один працівник **захоплює** кадри (producer), інший **кодує** (consumer). Між ними — **черга** (буфер). Якщо черга переповнена — producer **чекає** (backpressure), щоб не з'їсти всю пам'ять.

```python
import queue
frames = queue.Queue(maxsize=100)   # обмежена черга = backpressure
```

### L2 — Middle — потокова версія (`queue.Queue`, thread-safe)
```python
import queue, threading

frame_queue = queue.Queue(maxsize=100)   # ліміт → backpressure
SENTINEL = None                          # сигнал завершення

def producer():                          # захоплення кадрів
    while capturing:
        frame = capture_frame()
        frame_queue.put(frame)           # БЛОКУЄ, якщо черга повна (backpressure!)
    frame_queue.put(SENTINEL)            # сказати consumer'у «кінець»

def consumer():                          # енкодинг
    while True:
        frame = frame_queue.get()        # БЛОКУЄ, якщо черга порожня
        if frame is SENTINEL:
            break
        encode(frame)
        frame_queue.task_done()

t1 = threading.Thread(target=producer)
t2 = threading.Thread(target=consumer)
t1.start(); t2.start()
```
**Чому `queue.Queue`:** **thread-safe** з коробки (внутрішні замки) — не треба вручну синхронізувати. `maxsize` дає **backpressure**: producer не може бігти швидше за consumer → пам'ять обмежена.

### L2.5 — async-версія (`asyncio.Queue`)
```python
import asyncio

async def producer(q: asyncio.Queue):
    while capturing:
        frame = await capture_frame_async()
        await q.put(frame)               # чекає, якщо повна
    await q.put(None)

async def consumer(q: asyncio.Queue):
    while (frame := await q.get()) is not None:
        await encode_async(frame)

async def main():
    q = asyncio.Queue(maxsize=100)
    await asyncio.gather(producer(q), consumer(q))
```

**Gotcha:** `queue.Queue` (потоки) ≠ `asyncio.Queue` (корутини) — **не змішуй**. `queue.Queue.get()` блокує потік (у async вішає loop); `asyncio.Queue` — `await`. Для CPU-важкого consumer (енкодинг) краще потоки/процеси, не asyncio.

### L3 — Senior
**Backpressure — ключова концепція (зв'язок зі стримами):** обмежена черга (`maxsize`) **поглинає сплески** й **зв'язує** швидкості producer/consumer. Якщо джерело (камера 60fps) швидше за енкодер (30fps) — без ліміту черга росте → OOM (Q5). З лімітом — producer **блокується** → природне регулювання (або дропає кадри, якщо latency важливіша за повноту).

**Стратегії при переповненні (трейдоф):**
- **Блокувати producer** (`put`) — не втрачаємо кадри, але джерело гальмується (для запису/VOD).
- **Дропати кадри** (`put_nowait` + `except queue.Full`) — зберігаємо real-time, втрачаємо кадри (для live, «краще пропустити, ніж відстати» — як UDP, Q10).

```python
try:
    frame_queue.put_nowait(frame)        # не блокувати
except queue.Full:
    dropped_frames += 1                  # дропнути → лишитись у реальному часі
```

**Архітектура capture→encode→deliver (вакансія):**
```
[Capture thread] → Queue(maxsize) → [Encode thread/process] → Queue → [Deliver async]
                   backpressure                              backpressure
```
**Senior-суть:** producer-consumer + bounded queue + стратегія переповнення — **фундаментальний патерн** відео-pipeline. Він зв'язує конкурентність (Q1), пам'ять (Q5) і real-time трейдофи (latency vs повнота). Це майже напевно зрине як практична задача на цій ролі.

> ⚠️ Тонкощі shutdown (sentinel vs `task_done`/`join`), кілька consumer'ів, обробка винятків у потоках — звіряй з docs `queue`/`asyncio`.

---

## 12. 🔗 Context managers для ресурсів (24/7)

### L1 — Junior
**`with`** гарантує звільнення ресурсу (файл, сокет, pipeline) **навіть при помилці**. Для 24/7 — критично (інакше витік дескрипторів/пам'яті).

```python
with open("stream.ts", "rb") as f:
    process(f)                  # f.close() гарантовано, навіть при exception
```

### L2 — Middle
**Власний context manager для GStreamer pipeline / ресурсу:**
```python
from contextlib import contextmanager

@contextmanager
def gst_pipeline(description):
    pipeline = Gst.parse_launch(description)
    pipeline.set_state(Gst.State.PLAYING)
    try:
        yield pipeline
    finally:
        pipeline.set_state(Gst.State.NULL)   # гарантовано зупинити/звільнити
        print("pipeline cleaned up")

with gst_pipeline("v4l2src ! x264enc ! ...") as p:
    run(p)                       # навіть при краху — pipeline зупиниться
```

**Gotcha:** без `with`/`finally` помилка в обробці лишає pipeline/сокет «висіти» → витік ресурсів накопичується за дні аптайму → деградація 24/7-сервісу.

### L3 — Senior
`__enter__`/`__exit__` (або `@contextmanager`) гарантують cleanup через `finally`-семантику — надійніше за `__del__` (недетермінований, залежить від GC). Для відео: pipeline, сокети, файли, GPU-контексти, lock'и. **`ExitStack`** — для динамічної кількості ресурсів (N потоків/з'єднань). `__exit__` отримує виняток → може залогувати/обробити, не глушити (return False).

**📖 Повна відповідь:** [answers/02_python.md](../answers/02_python.md) п.36.

---

## 13. 🔗 Обробка помилок і стійкість (24/7 production) ⭐

### L1 — Junior
Сервіс має **пережити** помилку одного кадру/пакета, **не падаючи весь**. `try/except` навколо обробки + логування + продовження.

```python
for frame in stream:
    try:
        encode(frame)
    except DecodeError as e:
        log.warning(f"битий кадр, пропускаю: {e}")
        continue                 # один поганий кадр не валить стрім
```

### L2 — Middle
```python
# Кастомна ієрархія винятків — структурована обробка
class StreamError(Exception): ...
class DecodeError(StreamError): ...
class EncoderOverload(StreamError): ...

try:
    process_stream()
except DecodeError:
    skip_frame()                 # відновлювана — пропустити
except EncoderOverload:
    drop_quality()               # деградувати, не падати
except StreamError as e:
    alert_oncall(e)              # серйозна — ескалювати
    raise
```
**EAFP (Pythonic):** «спробуй і злови», а не «перевіряй наперед» — менше гонок у конкурентному коді.

**Gotcha:** не глуши помилки німо (`except: pass`) — у 24/7 це ховає деградацію. Мінімум — структуроване логування + метрика (скільки кадрів дропнуто).

### L3 — Senior
**Graceful degradation — серце 24/7:** сервіс **деградує, а не падає**. Битий кадр → пропустити (concealment); енкодер перевантажений → знизити якість/дропати (Q11); джерело впало → перепідключення з backoff; Redis недоступний → fallback. **Circuit breaker** запобігає каскадним збоям.

**Process-level safety:** необроблений виняток у потоці/корутині не має класти весь сервіс. `sys.excepthook`, обробка винятків у воркерах, supervisor/systemd для рестарту (під оркестратором). Логування з correlation ID (трасування проблемного потоку). **Retry з exponential backoff + jitter** для відновлюваних збоїв (перепідключення до джерела/CDN).

**Senior-суть:** для live 24/7 надійність = **ізоляція збоїв** (один кадр/потік/клієнт не валить інших) + **деградація** (працювати гірше, але працювати) + **спостережуваність** (метрики дропів/помилок) + **відновлення** (retry, рестарт). Це поєднує обробку помилок (Q13), backpressure (Q11), пам'ять (Q5) і troubleshooting (відео-Q6).

**📖 Повна відповідь:** [answers/02_python.md](../answers/02_python.md) п.43.

---

## ✅ Підсумок усіх 13
**Наскрізна історія для відео-сервісу на Python:**
```
asyncio (Q2) диригує → Capture → Queue+backpressure (Q11) → 
   Encode (C/процеси, обхід GIL Q1) ← zero-copy memoryview (Q6) + struct-парсинг (Q7)
   → Ring buffer (Q9) для jitter/DVR → Deliver
Усе через context managers (Q12), з обробкою помилок/деградацією (Q13),
   контролем пам'яті (Q5), профілюванням (Q4), на правильних структурах (Q10).
Генератори (Q3) — для лінивої потокової обробки.
```

**🆕 Найцінніше під роль (практичні задачі):** Q6 (memoryview/zero-copy), Q9 (ring buffer), Q11 (producer-consumer), Q7 (struct). Це те, що відрізняє відео-інженера.

> Код у цьому файлі (ring buffer, producer-consumer, struct, memoryview) перевірено запуском.
