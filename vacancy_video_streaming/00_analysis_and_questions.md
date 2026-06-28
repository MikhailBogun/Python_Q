# Вакансія: Python Live Video Streaming Engineer — аналіз і прогноз питань

> Мета: розібрати вакансію на навички, передбачити, **що питатимуть**, і підготуватись.
> Цей файл — **аналіз + перші 10 питань**. Повні відповіді за Принципом Сходів — наступним кроком (скажи «відповідай»).

---

## 🔍 Аналіз вакансії

### Що це за роль (читаємо між рядків)
**Junior/Middle інженер у команді live-відео, 24/7 production.** Ключове: це **не** чистий бекенд — це **відео-інженерія** (signal flow, capture, encoding, streaming, monitoring, troubleshooting). Багато домену відео + Python як інструмент.

### Розкладка навичок за пріоритетом

**🔴 Обов'язкові (питатимуть точно):**
| З вакансії | Що перевірятимуть |
|---|---|
| Python knowledge | core Python, конкурентність (GIL!), performance |
| Basic algorithms + complexity | проста задача + Big-O |
| **Excellent troubleshooting** | діагностика проблем у проді (24/7!) — **головний акцент** |
| Problem-solving | сценарні задачі «що зламалось і чому» |
| English | співбесіда/спілкування англійською |

**🟠 Відповідальності (з них виводяться технічні питання):**
| Відповідальність | Тема питань |
|---|---|
| Scalable video streaming server | system design, протоколи стримінгу, high-load |
| **GStreamer encoding service** | GStreamer pipelines, elements, encoding |
| Web player | HTML5 video, MSE, hls.js/dash.js, ABR |
| Code performance optimization | профілювання, zero-copy, C-розширення, GIL |
| Event-based handler for equipment | event loop, async, message queues, стани |

**🟢 Nice to have (питатимуть оглядово, плюс якщо знаєш):**
- High-load системи, network engineering
- Encoding, **video codecs & containers**
- **WebRTC streaming server**
- Linux, Docker

### Який формат співбесіди очікувати
1. **Warm-up Python** (1–2 питання) — перевірити базу.
2. **Алгоритми + складність** — проста задача (вони пишуть «basic», тож не LeetCode Hard).
3. **Домен відео** — codecs/containers, протоколи, encoding (**головна частина**).
4. **GStreamer** — конкретно, бо це в обов'язках.
5. **Troubleshooting-сценарій** — «стрім завис о 3 ночі, твої дії» (найважливіше для 24/7).
6. **Performance** — як прискорити обробку відео в Python.
7. **WebRTC / networking** — якщо доходять (nice to have, але часто питають).

> **Стратегічна порада:** для цієї ролі **troubleshooting і доменні знання відео важливіші за алгоритми**. Вони прямо пишуть «basic algorithms», але «**excellent** troubleshooting» і ціла секція відео-обов'язків. Готуйся передусім до сценарних питань «що зламалось» і до відео-фундаменту (codecs, протоколи, latency).

---

## 🎯 Перші 10 питань (найімовірніші)

> Формат кожного: **питання** → **чому ймовірне** (мапінг на вакансію) → **що перевіряють** (на що звернути увагу при підготовці). Складність/тип позначені.

---

### 1. Python concurrency для відео-стримінгу
> «Як обробляти кілька одночасних відеопотоків у Python? Коли брати `threading`, коли `multiprocessing`, коли `asyncio` — і до чого тут GIL?»

- **Чому ймовірне:** «Python knowledge» + «scalable streaming server» + «performance optimization». GIL — питання №1 для будь-якої Python-ролі з конкурентністю.
- **Що перевіряють:** розуміння GIL, I/O-bound vs CPU-bound (відео-енкодинг — CPU-bound → процеси / C), що бібліотеки на C (GStreamer, numpy, PyAV) **відпускають GIL**.
- **Тип:** core Python, обов'язкове.

---

### 2. Codec vs Container + H.264/H.265
> «Яка різниця між кодеком і контейнером? Поясни H.264 vs H.265 (HEVC). Коли обрати MP4, коли MPEG-TS, коли fMP4 для стримінгу?»

- **Чому ймовірне:** «Knowledge about video codecs and containers» — прямо з вакансії. Фундамент відео-інженерії.
- **Що перевіряють:** кодек = алгоритм стиснення (H.264, H.265, AV1, VP9); контейнер = «обгортка» (MP4, MKV, TS, fMP4). Для **live** — MPEG-TS / fMP4 (можна стрімити по шматках), MP4 — для VOD.
- **Тип:** домен відео, обов'язкове.

---

### 3. Протоколи стримінгу: RTMP / HLS / DASH / WebRTC
> «Порівняй RTMP, HLS, DASH і WebRTC. Які в них затримки (latency) і коли який обрати?»

- **Чому ймовірне:** «scalable video streaming server» + «WebRTC streaming server» (nice to have). Серце ролі.
- **Що перевіряють:** RTMP (ingest, ~2-5с), HLS/DASH (масштабовані через CDN, але latency 6-30с; LL-HLS менше), **WebRTC (sub-second, ~200мс)** для real-time. Трейдоф latency ↔ масштабованість.
- **Тип:** домен/архітектура, дуже ймовірне.

---

### 4. GStreamer pipeline
> «Поясни модель GStreamer: elements, pads, caps, bins. Як би ти побудував просту pipeline для енкодингу (capture → encode → stream)?»

- **Чому ймовірне:** «Writing gstreamer-based encoding service» — **прямий обов'язок**. Питатимуть майже точно.
- **Що перевіряють:** елементи (source/filter/sink), pads (з'єднання), caps (формати/negotiation), bins (групування), `gst-launch-1.0` синтаксис, як зв'язати елементи.
- **Тип:** домен-специфіка, дуже ймовірне.
- ⚠️ *Якщо GStreamer для тебе новий — це пріоритет №1 для підготовки (його важко «наговорити», треба розуміти модель).*

---

### 5. I/P/B-кадри та GOP
> «Поясни I-frame, P-frame, B-frame і структуру GOP. Як інтервал ключових кадрів (keyframe interval) впливає на затримку й перемотку в live-стримінгу?»

- **Чому ймовірне:** «encoding experience», основа розуміння, **чому** стрім поводиться так (latency, seeking, артефакти).
- **Що перевіряють:** I-frame (повний кадр), P-frame (різниця від попереднього), B-frame (двостороння різниця — додає latency!), GOP (group of pictures). Короткий GOP → менше latency + більше трафіку; B-frames погані для low-latency.
- **Тип:** домен відео, ймовірне.

---

### 6. Troubleshooting-сценарій (24/7 production) ⭐
> «О 3 ночі live-стрім почав періодично замерзати / сипати артефактами в проді. Проведи мене через свою діагностику — крок за кроком.»

- **Чому ймовірне:** «**Excellent troubleshooting skills**» + «24/7 production» + «monitoring». Це **найважливіше** питання ролі.
- **Що перевіряють:** **системність** мислення: шари (мережа → capture → encode → packaging → CDN → player). Перевірити: packet loss/jitter (мережа), CPU/event loop (енкодер), логи, метрики, bitrate, dropped frames. Ізолювати: один потік чи всі? Коли почалось? Що змінилось?
- **Тип:** behavioral/сценарний, **критично важливе**. Тут перевіряють не знання, а **підхід**.

---

### 7. Performance optimization обробки кадрів
> «Python-сервіс обробляє відеокадри, але занадто повільний / висока CPU. Як профілювати й оптимізувати?»

- **Чому ймовірне:** «Code performance optimization» — прямий обов'язок.
- **Що перевіряють:** профілювання (`cProfile`, `py-spy`), знайти bottleneck, **не вгадувати**; zero-copy (`memoryview`, buffer protocol), винести гаряче в C/Cython/numpy (відпускає GIL), уникати копіювання великих буферів, процеси для CPU-паралелізму.
- **Тип:** Python + performance, ймовірне.

---

### 8. WebRTC: як встановлюється з'єднання
> «Як WebRTC встановлює з'єднання? Поясни signaling, STUN/TURN, ICE, SDP.»

- **Чому ймовірне:** «Experience with WebRTC streaming server» (nice to have, але для real-time стримінгу — ключове).
- **Що перевіряють:** signaling (обмін SDP — поза WebRTC), ICE (пошук шляху), STUN (дізнатись свій публічний IP за NAT), TURN (relay коли P2P неможливий), SDP (опис медіа/кодеків). Чому UDP. SFU vs MCU для багатьох учасників.
- **Тип:** домен/мережа, ймовірне (плюс якщо знаєш).

---

### 9. Web player + Media Source Extensions (MSE)
> «Як побудувати веб-плеєр для стримінгу? Що таке MSE (Media Source Extensions)? Як працюють hls.js / dash.js і adaptive bitrate (ABR)?»

- **Чому ймовірне:** «Create a web player» — прямий обов'язок.
- **Що перевіряють:** `<video>` + **MSE** (подавати медіа-сегменти з JS у буфер), hls.js/dash.js (парсять манифест, тягнуть сегменти), **ABR** (перемикання якості за пропускною здатністю), WebRTC-плеєр для low-latency. Чому не просто `<video src>` для адаптивного стримінгу.
- **Тип:** домен/фронт, ймовірне.

---

### 10. UDP vs TCP для live-відео + мережеві проблеми
> «Чому для live/real-time відео часто обирають UDP, а не TCP? Поясни jitter, packet loss, latency й трейдоф буферизації.»

- **Чому ймовірне:** «Network engineering» (nice to have) + основа розуміння стримінгу й troubleshooting (питання 6).
- **Що перевіряють:** TCP (надійність + retransmit = latency, head-of-line blocking) vs UDP (швидко, але втрати — для real-time краще «втратити кадр, ніж чекати»). Jitter (нерівномірність) → jitter buffer. Трейдоф latency ↔ якість/надійність. RTP поверх UDP.
- **Тип:** мережа/домен, ймовірне.

---

## 📋 Бонус — теми, що можуть зринути далі (для розширення)
- **Алгоритми + Big-O** — проста задача (буфер, черга кадрів, ring buffer) + складність (обов'язкова вимога, але «basic»).
- **Event-based handler** — як обробляти події від обладнання (стани, конечні автомати, async, черги повідомлень).
- **System design** — спроєктуй масштабований streaming server (ingest → transcode → package → CDN/edge → player).
- **Linux/Docker** — контейнеризація сервісу, ресурси, налагодження в контейнері.
- **Bitrate / resolution / framerate** — як обрати під канал; transcoding ladder (ABR).
- **SRT / RIST** — сучасні протоколи надійного транспорту по UDP.
- **Monitoring відео** — метрики якості (dropped frames, bitrate, latency, QoE), що алертити в 24/7.
- **Поведінкові** — досвід із продакшн-інцидентами, робота в команді, англійська.

---

## ✅ Як рухатись далі
- Скажи **«відповідай на питання 1–10»** — і я розпишу кожне за Принципом Сходів (Junior → Middle → Senior) із кодом, як у попередніх блоках.
- Або **«додай ще питань»** по конкретній темі (GStreamer / WebRTC / codecs / troubleshooting) — поглибимо прогноз.
- Рекомендую почати з відповідей на **6 (troubleshooting), 2 (codecs/containers), 3 (протоколи), 4 (GStreamer)** — вони найважливіші й найімовірніші саме для цієї ролі.

> ⚠️ Прогноз ґрунтується на тексті вакансії та типових співбесідах для відео-стримінг ролей. Реальний набір залежить від компанії/інтерв'юера. Доменні деталі (GStreamer API, WebRTC, кодеки) звіряй з офіційною документацією — це швидкозмінні й глибокі теми.
