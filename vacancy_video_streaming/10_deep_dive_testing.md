# Тестування на Python (pytest, mocking, patching) — deep-dive

> Усе про тестування для ролі: pytest, **mocking/patching**, fixtures, async-тести, best practices. Заточено під відео-сервіс (тести без реальної камери/мережі/GStreamer).
> Формат — Принцип Сходів. Код перевірений запуском pytest.

---

## 0. Навіщо тести (особливо для 24/7 відео)

Для **24/7 production** тести — не формальність, а виживання: зміна не має ламати робочий стрім. Тести дають:
- **Впевненість** при рефакторингу/оптимізації (а вакансія = «performance optimization»).
- **Швидкий фідбек** (зловив баг до прода, не о 3 ночі).
- **Документацію** поведінки (як працює парсер пакетів/буфер).
- **Захист від регресій** (виправив баг → тест, щоб не повернувся).

**Виклик відео-тестування:** не можна в тестах піднімати реальну камеру/мережу/GStreamer. Рішення — **mocking** (підробити межі системи) + **розділення** чистої логіки від I/O (чисті функції легко тестувати без моків).

---

## 1. pytest — основи

### L1 — найпростіший тест
```python
# test_basic.py — запуск: pytest test_basic.py
def is_divisible_by_11(n):
    return n % 11 == 0

def test_divisible():               # функція з префіксом test_
    assert is_divisible_by_11(121)  # просто assert — pytest покаже деталі при фейлі
    assert not is_divisible_by_11(50)
```
```bash
pytest                    # запустити всі тести
pytest test_basic.py      # один файл
pytest -v                 # verbose (видно кожен тест)
pytest -k "divisible"     # за іменем
pytest -x                 # стоп на першому фейлі
```

### Структура AAA (Arrange-Act-Assert)
```python
def test_ring_buffer_drops_old():
    # Arrange — підготувати
    buf = RingBuffer(maxlen=3)
    # Act — виконати
    for i in range(5):
        buf.append(i)
    # Assert — перевірити
    assert list(buf) == [2, 3, 4]
```

### L2 — pytest переваги
- **Звичайний `assert`** (не `self.assertEqual`) — pytest «розбирає» вираз і показує значення при фейлі.
- **Авто-виявлення** — `test_*.py`, функції `test_*`, класи `Test*`.
- Багата екосистема: `pytest-asyncio`, `pytest-cov`, `pytest-mock`, `freezegun`.

---

## 2. Fixtures — підготовка й очищення

**Fixture** — переиспользувана підготовка (setup) + очищення (teardown), що «впорскується» в тест як аргумент.

```python
import pytest

@pytest.fixture
def frame_buffer():
    buf = RingBuffer(maxlen=10)     # SETUP
    yield buf                        # віддати тесту
    buf.clear()                      # TEARDOWN (після yield)

def test_uses_buffer(frame_buffer):  # ім'я аргументу = ім'я fixture
    frame_buffer.append(b"frame")
    assert len(frame_buffer) == 1
```

**Scope (як часто створювати):**
```python
@pytest.fixture(scope="function")  # дефолт — новий на КОЖЕН тест (ізоляція)
@pytest.fixture(scope="module")    # один на файл
@pytest.fixture(scope="session")   # один на весь запуск (дорогі ресурси: БД, сервер)
```

**`conftest.py`** — спільні fixtures для всіх тестів у теці (без імпорту).

**Gotcha:** дефолтний scope `function` дає **ізоляцію** (кожен тест — свіжий стан) — це правильно (тести незалежні). `session`/`module` — лише для дорогого setup (підняти тестову БД), обережно зі спільним станом.

---

## 3. Parametrize — багато кейсів одним тестом

```python
import pytest

@pytest.mark.parametrize("value, expected", [
    (121, True),
    (33, True),
    (50, False),
    (0, True),                       # edge case
    (-22, True),                     # від'ємне
])
def test_divisible(value, expected):
    assert is_divisible_by_11(value) == expected
# pytest запустить 5 окремих тестів — видно, ЯКИЙ кейс упав
```
**Перевага:** один тест → багато кейсів; при фейлі видно конкретний вхід. Заміна копіпасти.

---

## 4. Mocking і Patching — серце теми ⭐⭐

### L1 — навіщо
**Аналогія — каскадер замість актора в небезпечній сцені.** У тестах не можна викликати реальну мережу/камеру/платіжку (повільно, ненадійно, побічні ефекти). **Mock** — підробка («каскадер»), що вдає реальний об'єкт, але під контролем тесту.

**Mock vs Patch:**
- **Mock** — підроблений **об'єкт** (вдає що завгодно).
- **Patch** — **тимчасово замінити** реальний об'єкт моком (на час тесту).

### L2 — `unittest.mock`
```python
from unittest.mock import Mock, MagicMock

# Mock — налаштовуваний фейк
mock = Mock()
mock.read.return_value = b"fake frame"   # що повертає метод
mock.read()                               # b"fake frame"
mock.read.assert_called_once()           # перевірити, що викликали
mock.read.assert_called_with()           # з якими аргументами

# side_effect — функція / виняток / послідовність
mock.connect.side_effect = ConnectionError("мережа впала")  # кине виняток
mock.recv.side_effect = [b"pkt1", b"pkt2", b""]            # послідовні значення
```

### `patch` — замінити реальний об'єкт ⭐
```python
from unittest.mock import patch

# Як декоратор (мок передається аргументом)
@patch("myapp.service.socket.socket")     # замінити socket у service
def test_send(mock_socket):
    mock_socket.return_value.sendto.return_value = 100
    send_packet(b"data")
    mock_socket.return_value.sendto.assert_called_once()

# Як context manager
def test_fetch():
    with patch("myapp.service.requests.get") as mock_get:
        mock_get.return_value.json.return_value = {"status": "ok"}
        result = fetch_status()
        assert result == "ok"

# patch.object — замінити атрибут конкретного об'єкта
with patch.object(encoder, "encode", return_value=b"encoded"):
    ...
```

### ⭐ ГОЛОВНЕ ПРАВИЛО: «patch where it's used, not where defined»
Найчастіша помилка з patch. Патчиш там, **де ім'я шукається**, а не де визначене:
```python
# myapp/service.py
from myapp.network import send_udp     # імпортовано СЮДИ

def process():
    send_udp(data)

# ❌ НЕ працює — патчиш джерело, а service вже має своє посилання
@patch("myapp.network.send_udp")
# ✅ Працює — патчиш ТАМ, де воно ВИКОРИСТОВУЄТЬСЯ
@patch("myapp.service.send_udp")
```
Бо `from x import y` створює **нове ім'я** в модулі-споживачі. Патчити треба це ім'я.

### `autospec` — безпечніший мок
```python
@patch("myapp.service.send_udp", autospec=True)  # мок копіює сигнатуру реальної функції
def test(mock_send):
    # якщо викличеш із неправильними аргументами — тест впаде (як реальна функція)
    ...
```
**Чому корисно:** звичайний Mock приймає **будь-що** (`mock.anything(1,2,3)` — ок) → можна не помітити, що реальний код викликає неправильно. `autospec` ловить це.

### L3 — що мокати (межі!), а що ні ⭐
**Мокай МЕЖІ системи, не власну логіку:**
| Мокати ✅ | НЕ мокати ❌ |
|---|---|
| Мережа (сокети, HTTP) | свою бізнес-логіку |
| Зовнішні API/сервіси | чисті функції (парсери, обчислення) |
| Файлова система/БД | структури даних (ring buffer) |
| Час (`datetime.now`), random | прості перетворення |
| Залізо (камера, енкодер) | — |

**Чому:** over-mocking (мокати все підряд) → тести перевіряють **моки**, а не код; ламаються на кожному рефакторингу (прив'язані до реалізації, не поведінки). Мокай **на краях** (де система торкається зовнішнього світу), тестуй **реальну** логіку всередині.

**Для відео:** мокай `socket`/мережу, джерело кадрів (камеру), час (для jitter buffer тестів); тестуй **реально** — парсинг RTP-заголовка (чиста функція!), ring buffer, логіку дропу. Розділяй I/O від логіки → логіка тестується без моків.

---

## 5. `monkeypatch` — pytest-fixture для патчингу

pytest має вбудований `monkeypatch` (простіший за `patch` для атрибутів/env):
```python
def test_with_monkeypatch(monkeypatch):
    # Підмінити атрибут
    monkeypatch.setattr("myapp.service.send_udp", lambda data: 100)
    # Підмінити змінну оточення
    monkeypatch.setenv("STREAM_PORT", "5004")
    # Видалити
    monkeypatch.delattr("myapp.service.dangerous_call")
    # ... тест ...
    # автоматично відкочується після тесту (не треба cleanup)
```
**`patch` vs `monkeypatch`:** `monkeypatch` — pytest-нативний, авто-відкат, зручний для env/атрибутів. `unittest.mock.patch` — потужніший (assert_called, side_effect, autospec). Часто комбінують.

**`pytest-mock` (`mocker`)** — обгортка `unittest.mock` у вигляді fixture (авто-cleanup):
```python
def test_with_mocker(mocker):
    mock_send = mocker.patch("myapp.service.send_udp", return_value=100)
    process()
    mock_send.assert_called_once()
```

---

## 6. Async-тести (для asyncio-коду) ⭐

Для тестування корутин — `pytest-asyncio` + **`AsyncMock`**:
```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_async_handler():
    mock_db = AsyncMock()                    # мок для async-функцій
    mock_db.fetch.return_value = {"id": 1}
    result = await handle_request(mock_db)
    assert result["id"] == 1
    mock_db.fetch.assert_awaited_once()      # перевірити await (не лише call)
```
**Gotcha:** для async-функцій потрібен **`AsyncMock`** (не звичайний `Mock`) — інакше `await mock()` впаде (Mock не awaitable). `assert_awaited*` — перевірка саме await.

---

## 7. Тестування винятків і часу

```python
import pytest

# Перевірити, що кидається виняток
def test_raises():
    with pytest.raises(ValueError, match="division by zero"):
        divide(10, 0)

# Мокати час (freezegun) — для jitter buffer, таймаутів, TTL
from freezegun import freeze_time

@freeze_time("2026-01-01 12:00:00")
def test_timestamp():
    assert get_current_hour() == 12          # час "заморожений" — детерміновано
```
**Чому мокати час:** тести з реальним `datetime.now()`/`time.time()` — **недетерміновані** (flaky). Заморозь час → стабільний результат. Критично для тестів з таймаутами/буферами.

---

## 8. Покриття (coverage)

```bash
pytest --cov=myapp --cov-report=term-missing   # які рядки НЕ покриті
pytest --cov=myapp --cov-report=html           # HTML-звіт
```
**Gotcha:** 100% покриття ≠ відсутність багів — можна виконати рядок, не перевіривши результат. Coverage показує **що не протестовано** (корисно), але не **якість** тестів. Краще орієнтир — чи покриті **критичні шляхи** й edge cases.

---

## 9. Best practices (FIRST + поведінка)

**FIRST — якісний тест:**
- **F**ast — мілісекунди (інакше їх не ганяють).
- **I**solated — незалежні, будь-який порядок.
- **R**epeatable — той самий результат завжди (без random/now/мережі → мокати).
- **S**elf-validating — pass/fail без ручної перевірки.
- **T**imely — пишуться вчасно (ідеально TDD).

**Принципи:**
- **Тестуй поведінку, не реалізацію** — тест, прив'язаний до внутрішніх викликів (over-mock), ламається на кожному рефакторингу.
- **Один тест — одна поведінка** (одна логічна перевірка).
- **Описові імена:** `test_ring_buffer_drops_oldest_when_full`.
- **Покривай happy path + edge cases + помилки** (порожній, 0, None, межі, виняток).
- **Знайшов баг → спочатку тест**, що його відтворює (regression).

**Gotcha — flaky-тести** (то зелені, то червоні) гірше за відсутність тестів: команда перестає довіряти CI. Причини: залежність від часу/порядку/мережі/race. Лікувати або видаляти.

---

## 10. Типи тестів (піраміда)

| Тип | Що | Швидкість | Для відео-сервісу |
|---|---|---|---|
| **Unit** | одна функція ізольовано (моки) | дуже швидко | парсер пакетів, ring buffer, логіка дропу |
| **Integration** | взаємодія компонентів | повільніше | producer-consumer + черга, БД |
| **E2E** | уся система | найповільніше | реальний стрім (мало, критичні шляхи) |

**Піраміда:** багато unit → менше integration → ще менше E2E. Для відео E2E дорогі (треба реальне джерело/мережу) → мало, лише happy path; основа — швидкі unit на чистій логіці.

---

## 11. Приклад під роль — тестуємо парсер RTP (без мережі!)

```python
import struct, pytest

def parse_rtp_header(data: bytes) -> dict:
    b0, b1, seq, ts, ssrc = struct.unpack("!BBHII", data[:12])
    return {"version": b0 >> 6, "payload_type": b1 & 0x7F,
            "sequence": seq, "timestamp": ts, "ssrc": ssrc}

# Чиста функція → тестується БЕЗ моків, миттєво
@pytest.mark.parametrize("seq, pt", [(1234, 96), (0, 0), (65535, 127)])
def test_parse_rtp(seq, pt):
    packet = struct.pack("!BBHII", 0x80, pt, seq, 99000, 0xDEADBEEF)
    h = parse_rtp_header(packet)
    assert h["version"] == 2
    assert h["payload_type"] == pt
    assert h["sequence"] == seq

def test_parse_rtp_too_short():
    with pytest.raises(struct.error):
        parse_rtp_header(b"\x00\x01")        # замало байтів
```
**Урок:** розділивши **парсинг (чиста логіка)** від **прийому з сокета (I/O)**, тестуєш парсинг повністю без моків — швидко, надійно. А прийом з сокета мокаєш окремо. Це і є «mock at boundaries, test pure logic».

---

## ✅ Чеклист тестування (інтерв'ю)

**pytest:**
- [ ] assert, fixtures (scope, conftest), parametrize, pytest.raises.

**Mocking/patching (часто питають!):**
- [ ] Mock vs patch; `return_value` vs `side_effect`.
- [ ] **«patch where used, not defined»** — головне правило.
- [ ] `autospec` (безпечніше), `assert_called_with`.
- [ ] `AsyncMock` для async; `assert_awaited`.
- [ ] `monkeypatch` (pytest) vs `unittest.mock.patch`.
- [ ] **Що мокати — межі (мережа/час/залізо), не власну логіку.**

**Принципи:**
- [ ] AAA, FIRST, тестуй поведінку не реалізацію.
- [ ] Піраміда (багато unit), flaky-тести.
- [ ] Розділяти I/O від логіки → тестувати чисте без моків.

---

## 🔑 Топ-питання інтерв'ю
1. **«Mock vs patch?»** → mock = фейк-об'єкт; patch = тимчасова заміна.
2. **«Де патчити — джерело чи споживач?»** → **де використовується** (`from x import y` → патч y у споживачі).
3. **«Що мокати?»** → межі системи (мережа, час, залізо), не власну логіку.
4. **`return_value` vs `side_effect`?** → значення vs функція/виняток/послідовність.
5. **«Як тестувати async?»** → `pytest-asyncio` + `AsyncMock`.
6. **«Чому 100% coverage ≠ якість?»** → рядок виконано ≠ результат перевірено.
7. **«Як тестувати код із сокетом/камерою?»** → розділити логіку від I/O, мокати I/O, тестувати чисту логіку.

## 🔗 Зв'язки
- **Тестування базово (unit/integration, best practices):** [answers/01_general_cs_web.md](../answers/01_general_cs_web.md) п.17–20.
- **Що тестувати у відео-коді:** парсер (08/струк), ring buffer (Q9), producer-consumer (Q11), async (09).
- **EAFP/обробка помилок:** [answers/02_python.md](../answers/02_python.md) п.43.

> ⚠️ `pytest-asyncio` API (маркери, режими) та `AsyncMock` (3.8+) залежать від версій — звіряй з docs. `freezegun`/`pytest-mock` — сторонні пакети.
