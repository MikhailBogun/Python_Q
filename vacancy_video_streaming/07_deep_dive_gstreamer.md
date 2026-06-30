# GStreamer — повний deep-dive для Strong Junior (відео-інженер)

> Усе, що має знати Strong Junior для ролі «gstreamer-based encoding service». Від ментальної моделі до Python-коду, caps negotiation, дебагу й архітектури сервісу.
> ⚠️ GStreamer API глибокий — назви елементів/властивостей/сигналів звіряй з `gst-inspect-1.0` і docs для своєї версії. Python-приклади — стандартний PyGObject API (не запускалися в цьому середовищі).

---

## 1. Що таке GStreamer і навіщо для цієї ролі

### Суть «на пальцях»
**Аналогія — конструктор LEGO для мультимедіа.** GStreamer — це **фреймворк** для побудови **конвеєрів обробки медіа** (відео/аудіо) зі стандартних блоків. Хочеш «камера → стиснути → відправити по мережі»? Збираєш ланцюг блоків, і дані течуть крізь них.

**Точніше:** GStreamer — крос-платформний **pipeline-based мультимедійний фреймворк** із **плагінною архітектурою**. На ньому будують: програвачі, енкодери, стримінг-сервери, транскодери, конференц-системи (так працює багато реальних відео-продуктів).

### Чому це ядро вакансії
«Writing gstreamer-based encoding service» — **прямий обов'язок**. Для цієї ролі GStreamer — головний інструмент: захоплення зі студії → енкодинг → пакування → стримінг. Питатимуть **точно**, і не лише теорію — а чи розумієш ти **модель** (елементи, pads, caps, потік даних) і чи можеш зібрати/налагодити pipeline.

### GStreamer vs FFmpeg (часте порівняння)
| | GStreamer | FFmpeg |
|---|---|---|
| Модель | граф елементів (модульний) | монолітний інструмент/бібліотека |
| Гнучкість | висока (втручання в середину потоку, події) | менша (лінійний транскод) |
| Динамічна реконфігурація | так | важко |
| Інтеграція з кодом | `appsrc`/`appsink`, pad probes | libav* API |
| Складність | вища | нижча для простих задач |

Для **кастомного encoding-сервісу з event-обробкою** (вакансія) GStreamer гнучкіший — можна вставляти свою логіку в потік.

---

## 2. Ментальна модель — pipeline як конвеєр

```
┌─────────────────────── PIPELINE (bin) ───────────────────────┐
│                                                               │
│  [source] ──> [filter] ──> [encoder] ──> [payloader] ──> [sink]
│   камера      конвертер     H.264        RTP-пакування    мережа
│      ↑           ↑            ↑              ↑              ↑
│   src pad    sink/src      sink/src      sink/src       sink pad
│      └─ caps ──┘  └─ caps ──┘  └─ caps ──┘  └─ caps ──┘        │
│                                                               │
│   дані течуть зліва направо у вигляді BUFFER'ів               │
│   керування/повідомлення йдуть через BUS                     │
└───────────────────────────────────────────────────────────────┘
```
**Запам'ятай:** pipeline = **граф елементів**, з'єднаних **pads**, по яких течуть **buffers** (дані), у форматі, описаному **caps**, а повідомлення (помилки, кінець) йдуть через **bus**.

---

## 3. Базові концепції (фундамент — знати назубок)

### 3.1 Element (елемент) — базовий блок
Найменша одиниця обробки. Три ролі:
- **Source** (джерело) — лише **src pad** (видає дані): `v4l2src` (камера), `filesrc`, `udpsrc`, `appsrc`.
- **Filter/Transform** — **sink pad** (вхід) + **src pad** (вихід): `videoconvert`, `x264enc`, `queue`, `tee`.
- **Sink** (стік) — лише **sink pad** (споживає дані): `filesink`, `udpsink`, `autovideosink`, `appsink`.

### 3.2 Pad — точка з'єднання елемента
- **Src pad** — вихід елемента (звідки течуть дані).
- **Sink pad** — вхід елемента (куди течуть дані).
- Дані течуть: **src pad одного → sink pad наступного**.
- Типи pad'ів:
  - **Static** — є завжди (звичайні елементи).
  - **Dynamic (sometimes)** — з'являються в рантаймі (`decodebin`, `rtpbin` — не знають наперед, скільки потоків). → треба сигнал `pad-added` (розділ 7.7).
  - **Request** — створюються на вимогу (`tee` — додаєш вихід під кожного споживача).

### 3.3 Caps (Capabilities) — формат даних на pad
Опис **що саме** тече: media type + властивості.
```
video/x-raw, format=I420, width=1920, height=1080, framerate=30/1
video/x-h264, stream-format=byte-stream, profile=high
application/x-rtp, media=video, encoding-name=H264, payload=96
```
Сусідні елементи **домовляються** (caps negotiation, розділ 8): чи сумісні їх формати. Несумісні → потрібен конвертер (`videoconvert`) або помилка `not-negotiated`.

### 3.4 Bin і Pipeline — контейнери елементів
- **Bin** — група елементів, що поводиться як один елемент (інкапсуляція).
- **Pipeline** — top-level bin, що **керує станами й годинником** (clock), має **bus**.

### 3.5 Bus — канал повідомлень
Pipeline → застосунок: помилки (`ERROR`), кінець потоку (`EOS`), зміни стану (`STATE_CHANGED`), QoS, теги. Слухаєш bus, щоб реагувати (розділ 7.5). **Це твій головний канал для event-обробки й моніторингу.**

### 3.6 Buffer — одиниця даних, що тече
`GstBuffer` — шматок медіа (кадр, аудіо-семпли) + метадані (timestamp PTS/DTS, тривалість, прапори). Сюди ж — твій zero-copy: buffer обгортає пам'ять (мапиться в Python через `map`, розділ 7.6).

### 3.7 Event і Query — керування в потоці
- **Event** — керівна інформація, що тече **разом з даними**: `EOS` (кінець), `SEEK` (перемотка), `FLUSH`, зміна caps. Можуть йти за потоком (downstream) і проти (upstream).
- **Query** — запит інформації по pipeline (тривалість, позиція, latency).

### 3.8 States (стани) — життєвий цикл pipeline
```
NULL → READY → PAUSED → PLAYING
 ↑       ↑        ↑         ↑
немає  ресурси  preroll   грає
ресурс  є       (1й кадр   (дані
        (порти, у sink)    течуть)
        пам'ять)
```
- **NULL** — нічого (початок/кінець, ресурси звільнені).
- **READY** — ресурси виділені (відкриті пристрої/порти), даних немає.
- **PAUSED** — **preroll**: дані доходять до sink, але «на паузі» (перший кадр готовий). Для live-джерел поводиться особливо.
- **PLAYING** — дані течуть, годинник іде.

Зміна стану: `pipeline.set_state(Gst.State.PLAYING)`. **Gotcha:** зміна стану **асинхронна** (особливо PAUSED→PLAYING із live-джерелами) — перевіряй результат і чекай через bus.

### 3.9 Clock і синхронізація
Pipeline має **clock** — спільний годинник, за яким sink'и відтворюють buffer'и в правильний час (за PTS — presentation timestamp). Це механізм A/V-синхронізації й коректного тайму відтворення.

---

## 4. Типи елементів (що використовуватимеш)

| Категорія | Елементи (приклади) | Призначення |
|---|---|---|
| **Sources** | `v4l2src`, `filesrc`, `videotestsrc`, `udpsrc`, `rtspsrc`, `appsrc` | джерела медіа/тестові/мережеві/з коду |
| **Convert/scale** | `videoconvert`, `audioconvert`, `videoscale`, `videorate` | формат/розмір/fps |
| **Encoders** | `x264enc`, `x265enc`, `vaapih264enc`, `nvh264enc` | стиснення (soft/HW) |
| **Decoders** | `avdec_h264`, `vaapidecode`, `decodebin` | розкодування |
| **Parsers** | `h264parse`, `aacparse` | розбір елементарного потоку |
| **Muxers** | `mpegtsmux`, `mp4mux`, `matroskamux`, `flvmux` | пакування в контейнер |
| **Demuxers** | `qtdemux`, `tsdemux`, `matroskademux` | розпакування контейнера |
| **RTP pay/depay** | `rtph264pay`, `rtph264depay` | пакування в/з RTP |
| **Flow control** | `queue`, `tee`, `capsfilter`, `identity` | буферизація/розгалуження/фільтр caps |
| **Sinks** | `autovideosink`, `filesink`, `udpsink`, `rtmpsink`, `appsink`, `fakesink` | вивід на екран/файл/мережу/код |

**Ключові «службові» елементи:**
- **`queue`** — буфер + **межа потоків** (створює новий thread, розділ 9). Критичний для розв'язки швидкостей.
- **`tee`** — розгалуження одного потоку на кілька (запис + стрім одночасно).
- **`capsfilter`** — нав'язати конкретні caps (`! video/x-raw,width=1280 !`).
- **`appsrc`/`appsink`** — міст між pipeline і твоїм Python-кодом (розділ 7.6).

---

## 5. `gst-launch-1.0` — CLI для прототипування

Найшвидший спосіб зібрати/перевірити pipeline без коду. Синтаксис: елементи через **`!`** (link).

```bash
# Тестове відео на екран
gst-launch-1.0 videotestsrc ! autovideosink

# Властивості елемента (key=value)
gst-launch-1.0 videotestsrc pattern=ball ! videoconvert ! autovideosink

# Caps у pipeline (нав'язати формат)
gst-launch-1.0 videotestsrc ! video/x-raw,width=1280,height=720,framerate=30/1 ! autovideosink

# Іменовані елементи (для розгалуження/складних графів)
gst-launch-1.0 videotestsrc ! tee name=t  t. ! queue ! autovideosink  t. ! queue ! fakesink
```
- **`!`** — з'єднати src pad ← sink pad сусідніх елементів.
- **`name=t` + `t.`** — посилання на елемент (для tee/мультиплексування).
- **властивості** — `pattern=ball`, `port=5000`, прямо в рядку.
- **caps** — як «елемент» між `!` (насправді capsfilter).

**Strong Junior must:** уміти читати/писати `gst-launch` pipeline — це мова спілкування в GStreamer-світі й перший крок прототипування перед Python.

---

## 6. Практичні pipeline (під відео-стримінг)

```bash
# 1. Камера → H.264 → запис у файл (MP4)
gst-launch-1.0 v4l2src ! videoconvert ! x264enc ! mp4mux ! filesink location=out.mp4

# 2. Камера → H.264 → RTP → відправка по UDP (СТРИМІНГ!) ⭐
gst-launch-1.0 v4l2src ! videoconvert ! x264enc tune=zerolatency ! \
    rtph264pay ! udpsink host=10.0.0.5 port=5000

# 3. Прийом RTP по UDP → декод → екран (інша машина)
gst-launch-1.0 udpsrc port=5000 caps="application/x-rtp,media=video,encoding-name=H264,payload=96" ! \
    rtph264depay ! avdec_h264 ! videoconvert ! autovideosink

# 4. Транскодинг файлу (демукс → декод → енкод → мукс)
gst-launch-1.0 filesrc location=in.mp4 ! qtdemux ! h264parse ! avdec_h264 ! \
    videoconvert ! x264enc bitrate=2000 ! mp4mux ! filesink location=out.mp4

# 5. Tee — запис І стрім одночасно ⭐
gst-launch-1.0 v4l2src ! videoconvert ! x264enc tune=zerolatency ! tee name=t \
    t. ! queue ! mp4mux ! filesink location=rec.mp4 \
    t. ! queue ! rtph264pay ! udpsink host=10.0.0.5 port=5000
```
**Зверни увагу:** `tune=zerolatency` на `x264enc` (без B-frames, мінімум буферизації — критично для live, зв'язок з кадрами Q5/відео). `queue` після `tee` — обов'язково (розв'язка потоків, розділ 9).

---

## 7. GStreamer + Python (PyGObject) — головне для ролі ⭐

GStreamer біндиться в Python через **PyGObject (`gi`)**. Це те, чим писатимеш encoding-сервіс.

### 7.1 Ініціалізація + простий pipeline через `parse_launch`
```python
import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

Gst.init(None)                                  # обов'язково перед усім

# Найпростіший спосіб — той самий рядок, що в gst-launch
pipeline = Gst.parse_launch(
    "videotestsrc ! videoconvert ! autovideosink"
)
pipeline.set_state(Gst.State.PLAYING)
```

### 7.2 Ручна побудова pipeline (повний контроль)
```python
Gst.init(None)
pipeline = Gst.Pipeline.new("encoder")

src = Gst.ElementFactory.make("videotestsrc", "source")
conv = Gst.ElementFactory.make("videoconvert", "convert")
enc = Gst.ElementFactory.make("x264enc", "encoder")
sink = Gst.ElementFactory.make("udpsink", "sink")

if not all([src, conv, enc, sink]):
    raise RuntimeError("не вдалося створити елемент (плагін відсутній?)")

# Властивості
enc.set_property("tune", "zerolatency")
sink.set_property("host", "10.0.0.5")
sink.set_property("port", 5000)

# Додати в pipeline й з'єднати
for el in (src, conv, enc, sink):
    pipeline.add(el)
src.link(conv)
conv.link(enc)
enc.link(sink)                                  # повертає False при несумісних caps!

pipeline.set_state(Gst.State.PLAYING)
```

### 7.3 Властивості елементів
```python
element.set_property("bitrate", 2000)
value = element.get_property("bitrate")
# Дізнатись доступні властивості: gst-inspect-1.0 x264enc
```

### 7.4 Стани
```python
ret = pipeline.set_state(Gst.State.PLAYING)
if ret == Gst.StateChangeReturn.FAILURE:
    log.error("не вдалося запустити pipeline")
# ASYNC — для live чекай через bus (ASYNC_DONE)
```

### 7.5 Bus — обробка повідомлень (помилки, EOS) + main loop ⭐
```python
def on_message(bus, message, loop):
    t = message.type
    if t == Gst.MessageType.EOS:
        print("кінець потоку")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        print(f"ПОМИЛКА: {err}  |  {debug}")     # debug — безцінний для діагностики
        loop.quit()
    elif t == Gst.MessageType.STATE_CHANGED:
        old, new, pending = message.parse_state_changed()
    elif t == Gst.MessageType.QOS:
        pass                                      # quality-of-service (дропи) — моніторинг
    return True

loop = GLib.MainLoop()
bus = pipeline.get_bus()
bus.add_signal_watch()                            # вмикає сигнали bus
bus.connect("message", on_message, loop)
pipeline.set_state(Gst.State.PLAYING)
try:
    loop.run()                                    # головний цикл — обробляє події
except KeyboardInterrupt:
    pass
finally:
    pipeline.set_state(Gst.State.NULL)            # ЗАВЖДИ звільнити (як with/cleanup)
```
**Це твій event-handler фундамент** (вакансія: «event-based handler»): bus-повідомлення = події pipeline/обладнання.

### 7.6 `appsink` — дістати кадри в Python (zero-copy) ⭐
Найважливіше для кастомної обробки: pipeline віддає buffer'и в твій код.
```python
appsink = Gst.ElementFactory.make("appsink", "sink")
appsink.set_property("emit-signals", True)
appsink.set_property("max-buffers", 1)            # не накопичувати (low-latency)
appsink.set_property("drop", True)                # дропати старі (real-time)
appsink.connect("new-sample", on_new_sample)

def on_new_sample(sink):
    sample = sink.emit("pull-sample")             # GstSample
    buf = sample.get_buffer()                     # GstBuffer
    ok, mapinfo = buf.map(Gst.MapFlags.READ)      # мапимо пам'ять (zero-copy!)
    if ok:
        data = mapinfo.data                       # bytes-подібне → memoryview (Q6)
        # ... твоя обробка кадру (numpy/ML/метрики) ...
        buf.unmap(mapinfo)                        # ОБОВ'ЯЗКОВО звільнити
    return Gst.FlowReturn.OK
```
**Зв'язок із Python-блоком:** `mapinfo.data` дає доступ до буфера кадру **без копіювання** (buffer protocol, Q6) — основа продуктивності.

### 7.7 `appsrc` — подати кадри з Python у pipeline ⭐
Зворотний міст: твій код генерує/модифікує кадри й штовхає в pipeline.
```python
appsrc = Gst.ElementFactory.make("appsrc", "source")
appsrc.set_property("format", Gst.Format.TIME)
appsrc.set_property("is-live", True)              # live-джерело

def push_frame(frame_bytes: bytes):
    buf = Gst.Buffer.new_wrapped(frame_bytes)     # обгорнути дані в GstBuffer
    buf.pts = ...                                  # presentation timestamp
    ret = appsrc.emit("push-buffer", buf)
    return ret == Gst.FlowReturn.OK
```

### 7.8 Pad probes — інспекція/модифікація потоку (метрики, логіка)
```python
# Підчепитись до pad'а й бачити кожен buffer (для метрик/логування/модифікації)
pad = enc.get_static_pad("src")
def probe(pad, info):
    buf = info.get_buffer()
    # порахувати кадри, виміряти latency, додати метадані...
    return Gst.PadProbeReturn.OK                   # пропустити далі (або DROP)
pad.add_probe(Gst.PadProbeType.BUFFER, probe)
```

### 7.9 Dynamic pads — `decodebin`/`rtpbin` (часта складність)
Деякі елементи створюють pad'и **в рантаймі** (не знають наперед, скільки потоків). Лінкуєш у callback'у:
```python
decodebin = Gst.ElementFactory.make("decodebin", "dec")
def on_pad_added(element, pad):
    caps = pad.get_current_caps()
    name = caps.to_string()
    if name.startswith("video/"):
        pad.link(videoconvert.get_static_pad("sink"))  # лінкуємо динамічно
decodebin.connect("pad-added", on_pad_added)
```
**Gotcha:** забути обробити `pad-added` для `decodebin`/`uridecodebin` → «нічого не лінкується, pipeline не грає». Класична пастка новачка.

---

## 8. Caps negotiation — найважче (звідки `not-negotiated`) ⭐

**Серце GStreamer.** Сусідні елементи **домовляються** про формат на льоту. Якщо формати несумісні — `link()` повертає `False` або pipeline падає з `not-negotiated`.

```
v4l2src (дає YUYV) ──X── x264enc (хоче I420)   → НЕСУМІСНО → not-negotiated
v4l2src ── videoconvert (перетворить YUYV→I420) ── x264enc   → OK
```

**Правила:**
- Між елементами з несумісними форматами — **конвертер** (`videoconvert`, `audioconvert`, `videoscale`).
- **`capsfilter`** нав'язує конкретний формат: `! video/x-raw,format=I420,width=1920 !`.
- `not-negotiated` помилка → майже завжди **бракує конвертера** або **несумісні caps**.

**Як діагностувати:** `GST_DEBUG=3` покаже, де negotiation провалилась; `gst-inspect-1.0 x264enc` покаже, які caps елемент приймає на sink pad.

**Strong Junior must:** розуміти, що `not-negotiated` = «два сусіди не домовились про формат» → додати `videoconvert`/`videoscale`/`capsfilter`. Це найчастіша помилка при складанні pipeline.

---

## 9. `queue` і модель потоків (threading)

За замовчуванням pipeline працює в **обмеженій кількості потоків**. **`queue`** додає **буфер + межу потоків** — дані по інший бік queue обробляються в **окремому потоці**.

**Навіщо `queue`:**
- **Розв'язка швидкостей** — повільний sink не блокує швидкий source.
- **Після `tee`** — **обов'язково** queue на кожну гілку (інакше одна гілка блокує іншу → deadlock).
- **Буферизація** проти ривків.

```bash
# tee БЕЗ queue → deadlock; з queue → кожна гілка у своєму потоці
... ! tee name=t  t. ! queue ! sink1  t. ! queue ! sink2
```
**Gotcha:** забути `queue` після `tee` → pipeline зависає (гілки блокують одна одну). Параметри queue (`max-size-buffers/bytes/time`, `leaky`) керують буфером і стратегією дропу (для live — `leaky=downstream`, дропати старі).

---

## 10. Низька латентність (критично для live)

- **`x264enc tune=zerolatency`** — вимикає B-frames (Q5) і буферизацію look-ahead → мінімум затримки.
- **`appsink drop=true max-buffers=1`** — не накопичувати, віддавати найсвіжіший.
- **`queue leaky=downstream`** — дропати старі buffer'и замість зростання затримки.
- **малий GOP / keyframe interval** на енкодері (Q5).
- уникати зайвих `queue`/буферів у ланцюгу.

```bash
gst-launch-1.0 v4l2src ! videoconvert ! \
    x264enc tune=zerolatency speed-preset=ultrafast key-int-max=30 ! \
    rtph264pay ! udpsink host=... port=5000 sync=false
```
`sync=false` на sink — не чекати годинник (для мінімальної затримки live).

---

## 11. Hardware acceleration (HW-енкодинг)

Софт-енкодинг (`x264enc`) їсть CPU. Для high-load — апаратні енкодери:
- **VAAPI** (Intel): `vaapih264enc`, `vaapipostproc`.
- **NVENC** (NVIDIA): `nvh264enc`, `nvv4l2h264enc`.
- **V4L2 stateful** (вбудовані/ARM).

**Трейдоф:** HW-енкодинг розвантажує CPU й дає більше паралельних потоків ↔ прив'язка до заліза, інколи нижча якість/гнучкість за `x264`, складніше налаштування. Для «large/high-load systems» (nice to have) — HW майже обов'язковий.

> ⚠️ Наявність HW-елементів залежить від заліза/драйверів/збірки GStreamer. Перевіряй `gst-inspect-1.0 vaapih264enc`.

---

## 12. Дебаг GStreamer (must для troubleshooting)

```bash
# Рівні логування (0=нічого ... 9=все); за категоріями
GST_DEBUG=3 gst-launch-1.0 ...                    # WARNING+
GST_DEBUG=4,x264enc:6 gst-launch-1.0 ...           # глобально INFO, x264enc — детально

# Дамп графа pipeline у .dot (візуалізувати структуру + caps)
GST_DEBUG_DUMP_DOT_DIR=/tmp gst-launch-1.0 ...     # → dot -Tpng pipeline.dot

# Інспекція елемента: властивості, pads, caps, сигнали
gst-inspect-1.0 x264enc
gst-inspect-1.0 | grep h264                        # які H.264 елементи є
```
- **`GST_DEBUG`** — головний інструмент: показує negotiation, стани, помилки.
- **`GST_DEBUG_DUMP_DOT_DIR`** — візуальний граф pipeline (видно, де caps не зійшлись).
- **`gst-inspect-1.0`** — що елемент приймає/віддає, які властивості. Перед використанням елемента — інспектуй.

---

## 13. Типові помилки й рішення (Strong Junior)

| Помилка/симптом | Причина | Рішення |
|---|---|---|
| `not-negotiated` | несумісні caps між елементами | додати `videoconvert`/`videoscale`/`capsfilter` |
| Pipeline зависає на tee | немає `queue` після `tee` | `queue` на кожну гілку |
| `decodebin` нічого не грає | не оброблено `pad-added` | підписатись на `pad-added`, лінкувати динамічно |
| `no element "x264enc"` | плагін не встановлено | поставити `gst-plugins-ugly`/потрібний пакет |
| Велика затримка | буферизація/B-frames | `tune=zerolatency`, `sync=false`, малий queue |
| Pipeline не стартує | помилка стану | слухати bus `ERROR` (parse_error → debug-рядок) |
| Витік пам'яті | забув `buf.unmap()` / не звільнив | завжди unmap після map; `set_state(NULL)` |

---

## 14. Архітектура encoding-сервісу на GStreamer (під вакансію) ⭐

```
                    ┌──── GStreamer Pipeline ────┐
[Студія/камера] →   │ appsrc/v4l2src/rtspsrc      │
                    │   → videoconvert            │
[твій Python код] → │   → encoder (HW/x264)       │ → tee → rtph264pay → udpsink (стрім)
   (кадри, логіка)  │   → ...                     │      └→ mp4mux → filesink (запис)
                    └──────────┬──────────────────┘
                               │
                    BUS (повідомлення) → твій event-handler:
                       - ERROR → лог/алерт/рестарт
                       - EOS → завершення
                       - STATE_CHANGED → керування
                       - QOS → метрики (дропи)
                    PAD PROBES → метрики (fps, latency, лічильники)
                    appsink → кадри в Python (ML/аналіз/метрики)
```

**Як це лягає на обов'язки вакансії:**
- **«gstreamer-based encoding service»** → pipeline з encoder + payloader + sink.
- **«event-based handler for equipment»** → **bus-повідомлення** (ERROR/EOS/state) + сигнали = події обладнання/pipeline.
- **«code performance optimization»** → zero-copy через `appsink` buffer map (Q6), HW-енкодинг, мінімум `queue`.
- **«scalable streaming server»** → tee на кілька виходів, кілька pipeline, керування станами.

---

## 15. ✅ Чеклист Strong Junior (GStreamer)

**Концепції (мусиш пояснити):**
- [ ] Що таке pipeline / element / pad / caps / bin / bus / buffer / state.
- [ ] Три ролі елементів (source/filter/sink) і їх pads.
- [ ] Стани NULL→READY→PAUSED→PLAYING і що таке preroll.
- [ ] Що таке caps negotiation і чому виникає `not-negotiated`.
- [ ] Навіщо `queue` і чому обов'язково після `tee`.

**Практика (мусиш зробити):**
- [ ] Зібрати pipeline в `gst-launch-1.0` (камера → encode → file/UDP).
- [ ] Те саме в Python (parse_launch + ручна побудова).
- [ ] Обробити bus (ERROR/EOS) з `GLib.MainLoop`.
- [ ] Дістати кадри через `appsink` (map/unmap).
- [ ] Подати кадри через `appsrc`.
- [ ] Налагодити `not-negotiated` (додати videoconvert).
- [ ] Налаштувати low-latency (`tune=zerolatency`, drop).

**Інструменти:**
- [ ] `GST_DEBUG` рівні, `GST_DEBUG_DUMP_DOT_DIR`, `gst-inspect-1.0`.

**Зв'язки з рештою:** zero-copy buffer map ↔ memoryview (Q6); bus event-handler ↔ обробка помилок (Q13); appsink→черга ↔ producer-consumer (Q11); RTP/UDP sink ↔ UDP deep-dive (06); tune=zerolatency ↔ I/P/B-кадри (Q5).

---

## 🔑 Головна порада
GStreamer **не вивчиш лише читанням** — це граф із багатьма нюансами (caps, потоки, динамічні pads). **Постав GStreamer і пройди руками**: `gst-launch` приклади (розділ 6), потім Python (розділ 7). На інтерв'ю Strong Junior очікують, що ти **зібрав хоч одну реальну pipeline** і розумієш потік даних + caps negotiation + bus, а не лише терміни.

> ⚠️ Назви елементів, властивостей і сигналів звіряй з `gst-inspect-1.0` та офіційною документацією GStreamer (вони залежать від версії й встановлених плагінів). Python-приклади тут — стандартний PyGObject-патерн; перевір на своєму середовищі з реальним GStreamer.
