# SQLAlchemy — повний deep-dive

> Усе про SQLAlchemy: Core + ORM, сучасний **2.0-стиль**, Session, relationships, N+1, async, пули з'єднань, транзакції, Alembic.
> Сучасний стек: SQLAlchemy 2.0+, Python 3.10+. Код перевірений запуском (sqlite).
> Де у відео-сервісі: метадані стримів, розклад, журнал подій обладнання, каталог записів.

---

## 1. Що таке SQLAlchemy

### L1 — суть
**Аналогія — перекладач між двома світами.** Python мислить **об'єктами**, БД — **таблицями**. SQLAlchemy перекладає між ними: працюєш з Python-об'єктами, а воно генерує SQL і мапить рядки назад в об'єкти.

**SQLAlchemy = «Python SQL toolkit + ORM»** — має **два рівні**:
- **Core** — будівник SQL (SQL Expression Language): пишеш SQL Python-об'єктами, без рядків.
- **ORM** — об'єкти ↔ рядки таблиць (Object-Relational Mapper).

### L2 — два рівні (вибір)
```
┌─────────────────────────────────────┐
│ ORM (моделі, Session, relationships) │  ← високий рівень, об'єкти
├─────────────────────────────────────┤
│ Core (Table, select(), Engine)       │  ← будівник SQL, типобезпечно
├─────────────────────────────────────┤
│ DBAPI (psycopg, asyncpg, sqlite3)    │  ← драйвер
└─────────────────────────────────────┘
```
ORM **побудований поверх** Core. Можна спускатись із ORM у Core там, де потрібен тонкий контроль.

**Важливо: SQLAlchemy 2.0** змінив API (типізований `Mapped`, `select()` всюди, async). Старий 1.x-стиль (`query()`, `Column` без типів) — legacy. Цей файл — **2.0**.

---

## 2. Engine та Connection (фундамент)

**Engine** — фабрика з'єднань + пул. Створюється раз на застосунок.
```python
from sqlalchemy import create_engine

# URL: dialect+driver://user:pass@host:port/dbname
engine = create_engine("postgresql+psycopg://user:pass@localhost:5432/mydb",
                       echo=True,           # логувати SQL (для дебагу)
                       pool_size=10,        # пул з'єднань (розділ 11)
                       pool_pre_ping=True)  # перевіряти живість з'єднання

# sqlite (для тестів/прототипів)
engine = create_engine("sqlite:///:memory:")    # у пам'яті
engine = create_engine("sqlite:///app.db")      # файл
```

**Connection** — одне з'єднання з БД (береться з пулу):
```python
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})
    for row in result:
        print(row)
    conn.commit()                # 2.0: явний commit (немає autocommit за замовч.)
```
**Gotcha:** у 2.0 `engine.connect()` **не в autocommit** — треба явний `conn.commit()` (або `engine.begin()` — авто-commit/rollback).

---

## 3. Core — SQL Expression Language

Пишеш SQL **Python-об'єктами** (без рядків, типобезпечно):
```python
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, select, insert

metadata = MetaData()
users = Table("users", metadata,
              Column("id", Integer, primary_key=True),
              Column("name", String(50)),
              Column("email", String))
metadata.create_all(engine)      # CREATE TABLE

with engine.begin() as conn:     # begin() — авто commit/rollback
    # INSERT
    conn.execute(insert(users).values(name="Іван", email="ivan@ex.com"))

    # SELECT — будуємо запит об'єктами
    stmt = select(users).where(users.c.name == "Іван").order_by(users.c.id)
    for row in conn.execute(stmt):
        print(row.name, row.email)
```
**Core доречний:** складні/аналітичні запити, bulk-операції, коли ORM зайвий, максимум контролю над SQL без рядкових конкатенацій.

---

## 4. ORM — декларативні моделі (2.0-стиль) ⭐

```python
from sqlalchemy import String, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

class Base(DeclarativeBase):     # базовий клас для всіх моделей
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str | None]                       # nullable (Optional)
    # зв'язок один-до-багатьох:
    orders: Mapped[list["Order"]] = relationship(back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[float]
    user: Mapped["User"] = relationship(back_populates="orders")

engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)                    # CREATE усіх таблиць
```
**2.0-фішки:**
- **`Mapped[type]`** — типізована анотація (mypy бачить типи).
- **`mapped_column()`** — конфіг колонки.
- `Mapped[int]` → NOT NULL; `Mapped[int | None]` → nullable.

---

## 5. Session — серце ORM ⭐

**Session** — «робоча зона»: відстежує об'єкти, накопичує зміни, виконує їх однією транзакцією.
```python
with Session(engine) as session:
    # CREATE
    user = User(name="Іван", email="ivan@ex.com")
    session.add(user)
    session.commit()                 # INSERT + транзакція

    # READ — get за PK (O(1) через identity map)
    u = session.get(User, 1)

    # READ — select() (2.0-стиль)
    from sqlalchemy import select
    stmt = select(User).where(User.name == "Іван")
    users = session.scalars(stmt).all()       # list[User]
    one = session.scalars(stmt).first()       # User | None

    # UPDATE — просто змінюємо об'єкт, Session відстежує
    u.name = "Іван Новий"
    session.commit()                 # авто UPDATE (dirty tracking)

    # DELETE
    session.delete(u)
    session.commit()
```

**`scalars` vs `execute`:** `session.scalars(select(User))` повертає **об'єкти User**; `session.execute(select(User))` повертає **Row** (кортежі). Для повних об'єктів — `scalars`.

**Gotcha:** `session.commit()` за замовчуванням **expire** усі об'єкти (наступний доступ перечитає з БД). Тому доступ до атрибутів **після commit поза session** → помилка (detached, розділ 12).

---

## 6. Session lifecycle — Unit of Work + Identity Map ⭐

ORM реалізує три патерни:
- **Unit of Work** — Session **накопичує** зміни (add/dirty/delete) і виконує **разом** на `commit()` (одна транзакція, оптимальний порядок INSERT/UPDATE/DELETE).
- **Identity Map** — один рядок БД = **один** Python-об'єкт у межах session (`session.get(User,1)` двічі → той самий об'єкт). Запобігає неузгодженості.
- **Dirty tracking** — Session помічає зміни атрибутів → авто UPDATE.

```python
with Session(engine) as session:
    u1 = session.get(User, 1)
    u2 = session.get(User, 1)
    assert u1 is u2              # identity map — ТОЙ САМИЙ об'єкт!

    u1.name = "змінено"         # dirty
    session.flush()             # відправити SQL у БД (без commit)
    session.commit()            # зафіксувати транзакцію
    # session.rollback()        # відкотити
```

**flush vs commit:**
- **`flush()`** — відправляє накопичений SQL у БД (у межах транзакції), але **не комітить** (можна відкотити).
- **`commit()`** — flush + зафіксувати транзакцію.

**Стани об'єкта:** transient (новий, не в session) → pending (added, не flushed) → persistent (у БД) → detached (session закрита) → deleted.

---

## 7. Запити (select 2.0) — повний арсенал

```python
from sqlalchemy import select, func, and_, or_, desc

# WHERE, кілька умов
select(User).where(User.name == "Іван", User.email.isnot(None))
select(User).where(or_(User.id == 1, User.id == 2))
select(User).where(User.name.like("Ів%"))
select(User).where(User.id.in_([1, 2, 3]))

# ORDER BY, LIMIT, OFFSET
select(User).order_by(desc(User.id)).limit(10).offset(20)

# JOIN
select(User, Order).join(Order, User.id == Order.user_id)
select(User).join(User.orders)               # через relationship

# Агрегація (GROUP BY, HAVING)
select(Order.user_id, func.sum(Order.amount).label("total")) \
    .group_by(Order.user_id) \
    .having(func.sum(Order.amount) > 1000)

# COUNT
session.scalar(select(func.count()).select_from(User))

# Виконання
session.scalars(stmt).all()      # усі об'єкти
session.scalars(stmt).first()    # перший або None
session.scalar(stmt)             # одне скалярне значення
```

---

## 8. Relationships (зв'язки) ⭐

### One-to-Many (один користувач — багато замовлень)
```python
class User(Base):
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
class Order(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="orders")

# Використання:
user.orders                      # list[Order] — пов'язані замовлення
order.user                       # User — власник
user.orders.append(Order(amount=100))   # додати через relationship
```

### Many-to-Many (через association table)
```python
from sqlalchemy import Table, Column, ForeignKey
stream_tags = Table("stream_tags", Base.metadata,
    Column("stream_id", ForeignKey("streams.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True))

class Stream(Base):
    tags: Mapped[list["Tag"]] = relationship(secondary=stream_tags, back_populates="streams")
class Tag(Base):
    streams: Mapped[list["Stream"]] = relationship(secondary=stream_tags, back_populates="tags")
```

**`back_populates`** — двосторонній зв'язок: зміна одного боку синхронізує інший.

### Cascade — що робити з дітьми при видаленні батька ⭐
```python
class User(Base):
    orders: Mapped[list["Order"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan")    # видалити orders разом з user
```
**Gotcha (перевірено на практиці):** **без cascade** видалення `User` намагається **занулити** `user_id` його замовлень (orphan) → якщо FK `NOT NULL` → `IntegrityError`. Варіанти:
- `cascade="all, delete-orphan"` — видалити дітей разом із батьком (типово для «володіння»).
- Залишити дітей, занулити FK — лише якщо FK nullable.
- `ON DELETE CASCADE` на рівні БД (`ForeignKey(..., ondelete="CASCADE")`) + `passive_deletes=True`.
Завжди свідомо обирай поведінку cascade для one-to-many.

---

## 9. N+1 problem та eager loading ⭐⭐ (найважливіше!)

**Найчастіша пастка ORM (і питання на інтерв'ю).** Lazy loading: доступ до `user.orders` тригерить **окремий** SQL-запит.
```python
# ❌ N+1: 1 запит на users + ПО ЗАПИТУ на orders кожного user
users = session.scalars(select(User)).all()        # 1 запит
for user in users:
    print(user.orders)                              # N запитів (по 1 на кожного!)
# 100 users → 101 запит → катастрофа продуктивності
```

**Рішення — eager loading:**
```python
from sqlalchemy.orm import selectinload, joinedload

# selectinload — 2 запити (users + усі orders одним IN-запитом). Рекомендовано.
stmt = select(User).options(selectinload(User.orders))
users = session.scalars(stmt).all()
for user in users:
    print(user.orders)               # БЕЗ додаткових запитів!

# joinedload — 1 запит з JOIN (добре для one-to-one / малих to-many)
stmt = select(User).options(joinedload(User.orders))
```

| Стратегія | Запитів | Коли |
|---|---|---|
| `lazy` (дефолт) | 1 + N | один об'єкт, рідкісний доступ |
| **`selectinload`** | 2 (IN-запит) | **колекції (one-to-many)** — дефолт-вибір |
| `joinedload` | 1 (JOIN) | one-to-one, малі to-many |

**Gotcha:** N+1 «непомітний» у коді (просто `for user in users: user.orders`), але вбиває продуктивність. **Завжди** думай про loading strategy при ітерації з relationships. У логах (echo=True) видно «зливу» запитів.

---

## 10. Транзакції

```python
# Контекстний менеджер — авто commit/rollback
with Session(engine) as session:
    with session.begin():            # транзакція
        session.add(user1)
        session.add(user2)
        # commit при виході; rollback при винятку

# Ручне керування
with Session(engine) as session:
    try:
        session.add(user)
        session.commit()
    except Exception:
        session.rollback()           # відкат при помилці
        raise

# Savepoint (вкладена транзакція)
with session.begin_nested():         # SAVEPOINT
    session.add(risky)               # відкотиться лише цей блок при помилці
```
*(Рівні ізоляції, MVCC — у [answers/03_databases.md](../answers/03_databases.md) / [answers/07](../answers/07_db_devops_ds.md).)* Рівень ізоляції задається на engine: `create_engine(..., isolation_level="SERIALIZABLE")`.

---

## 11. Async SQLAlchemy ⭐ (для async-сервісу)

Для asyncio-застосунку (FastAPI, відео-роздача) — async-движок + `asyncpg`:
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_users():
    async with async_session() as session:
        result = await session.scalars(select(User))   # await!
        return result.all()

    # CRUD з await:
    async with async_session() as session:
        user = User(name="Іван")
        session.add(user)
        await session.commit()
```
**Gotcha (важливо):** в async **lazy loading НЕ працює прозоро** — не можна тригерити I/O на доступі до атрибута поза await. Тому **eager loading (`selectinload`) стає обов'язковим**, не опційним. `expire_on_commit=False` — щоб об'єкти лишались доступні після commit.

---

## 12. Connection pooling (для прода/high-load)

Відкриття з'єднання до БД дороге (TCP+TLS+auth). Пул **перевикористовує** з'єднання:
```python
engine = create_engine(
    "postgresql+psycopg://...",
    pool_size=10,            # постійних з'єднань
    max_overflow=20,         # тимчасових понад pool_size при сплеску
    pool_timeout=30,         # чекати вільне з'єднання (сек)
    pool_pre_ping=True,      # перевіряти живість перед видачею (захист від «мертвих»)
    pool_recycle=3600,       # переробляти з'єднання старші за годину
)
```
- **`pool_pre_ping=True`** — критично для прода: перевіряє, чи з'єднання живе (БД могла розірвати) → уникаєш «server closed connection» помилок.
- **`pool_recycle`** — БД/firewall закривають довгі з'єднання → переробляти заздалегідь.
- **PgBouncer** — зовнішній пул перед Postgres (для багатьох інстансів).

---

## 13. Міграції — Alembic

SQLAlchemy описує схему в коді, **Alembic** керує її змінами в БД (версіонування схеми):
```bash
alembic init alembic                          # ініціалізація
alembic revision --autogenerate -m "add streams table"   # згенерувати міграцію
alembic upgrade head                          # застосувати
alembic downgrade -1                          # відкотити одну
```
- **`--autogenerate`** — Alembic порівнює моделі з БД і генерує diff-міграцію.
- Міграції — у `alembic/versions/`, версіоновані, оборотні (`upgrade`/`downgrade`).
- **Gotcha:** завжди **переглядай** автозгенеровану міграцію (autogenerate не ловить усе — перейменування, дані, складні зміни).

---

## 14. Core vs ORM — коли що (трейдофи) ⭐

| | Core | ORM |
|---|---|---|
| Рівень | SQL-вирази | об'єкти |
| Швидкість | максимум | overhead (трекінг) |
| Контроль над SQL | повний | обмежений |
| Продуктивність розробки | нижча | вища |
| N+1 ризик | немає (ти пишеш SQL) | є (lazy loading) |
| Складні/аналітичні запити | природно | інколи незручно |

**Senior-стратегія:** **ORM для CRUD** (швидкість розробки, безпека), **Core/raw для гарячих/складних запитів** (аналітика, bulk, оптимізовані JOIN). SQLAlchemy унікальна тим, що дає **обидва в одній бібліотеці** — спускайся в Core там, де ORM незручний.

---

## 15. Типові пастки (gotchas)

| Пастка | Проблема | Рішення |
|---|---|---|
| **N+1** | lazy loading у циклі | `selectinload`/`joinedload` |
| **DetachedInstanceError** | доступ до атрибута після закриття session | `expire_on_commit=False` / eager load / тримати session |
| **Lazy load у async** | I/O на доступі поза await | eager loading обов'язково |
| Забув commit | зміни не збереглись | явний `commit()` (2.0 не autocommit) |
| Session на весь застосунок | стан тече, не thread-safe | **session per request/operation** |
| Bulk insert по одному | повільно (N INSERT) | `session.execute(insert(), [list])` / `bulk_insert_mappings` |
| **Видалення батька → IntegrityError** | діти осиротіли (FK NOT NULL) | `cascade="all, delete-orphan"` / `ondelete="CASCADE"` (розділ 8) |

**Session per request (важливо):** Session **не thread-safe** і не призначена бути глобальною/довгоживучою. Патерн: **одна session на запит/операцію** (у FastAPI — dependency, що відкриває/закриває session на запит).

---

## 16. SQLModel (SQLAlchemy + Pydantic)

**SQLModel** (автор FastAPI) поєднує SQLAlchemy ORM + Pydantic-валідацію в одній моделі:
```python
from sqlmodel import SQLModel, Field

class Stream(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    bitrate: int
# одна модель = таблиця БД (SQLAlchemy) + валідація/серіалізація (Pydantic)
```
**Трейдоф:** менше дублювання (одна модель замість SQLAlchemy-модель + Pydantic-схема), чудово для FastAPI ↔ молодша, менш гнучка за чисту SQLAlchemy для складних випадків. Під капотом — та сама SQLAlchemy.

---

## ✅ Чеклист SQLAlchemy (інтерв'ю)

**Базово:**
- [ ] Core vs ORM — два рівні, коли що.
- [ ] Engine / Connection / Session — ролі.
- [ ] Декларативні моделі 2.0 (`Mapped`, `mapped_column`).
- [ ] CRUD через Session (add/get/select/commit).

**Середній:**
- [ ] Unit of Work + Identity Map + dirty tracking.
- [ ] flush vs commit.
- [ ] Relationships (one-to-many, many-to-many, back_populates).
- [ ] **N+1 + eager loading (selectinload/joinedload)** — must!

**Senior:**
- [ ] Async SQLAlchemy (чому eager loading обов'язковий).
- [ ] Connection pooling (pool_pre_ping, pool_recycle).
- [ ] Транзакції, savepoints, ізоляція.
- [ ] Alembic (autogenerate + ревью).
- [ ] Core vs ORM трейдофи (ORM для CRUD, Core для гарячого).
- [ ] Session per request; DetachedInstanceError.

## 🔑 Топ-питання інтерв'ю
1. **«Core vs ORM?»** → SQL-вирази vs об'єкти; ORM поверх Core.
2. **«Що таке N+1 і як лікувати?»** → lazy loading у циклі → `selectinload`/`joinedload`.
3. **«flush vs commit?»** → SQL у БД (можна відкотити) vs зафіксувати транзакцію.
4. **«Identity Map / Unit of Work?»** → один об'єкт на рядок / накопичення змін у транзакцію.
5. **«Чому в async eager loading обов'язковий?»** → lazy = I/O на доступі, неможливе поза await.
6. **«Як керувати session?»** → одна на запит/операцію, не глобальна.

> ⚠️ SQLAlchemy 2.0 суттєво відрізняється від 1.x (типізований `Mapped`, `select()` замість `query()`, async). Звіряй із docs **версії 2.0**. Async-частина (`asyncpg`, lazy loading нюанси) — особливо уважно.
