# Блок 2. Express.js — Middleware (Junior)

> Формат — **Принцип Сходів**: **L1 Junior** → **L2 Middle** → **L3 Senior**.
> Сучасний стек: Express 4/5, Node.js 20+, ES Modules.

> **Ключова ідея блоку:** Express — це, по суті, **конвеєр middleware**. Зрозумієш middleware — зрозумієш увесь Express.

---

## 17. Для чого використовують middleware?

### L1 — Junior
**Аналогія — контроль в аеропорту.** Перш ніж потрапити на літак (до обробника маршруту), пасажир (запит) проходить через **ланцюг пунктів**: реєстрація → перевірка паспорта → митниця → безпека. Кожен пункт щось робить (перевіряє, штампує) і пропускає далі. **Middleware** — це такий «пункт» між отриманням запиту й відповіддю.

**Middleware** — функція, що має доступ до `req` (запит), `res` (відповідь) і `next` (передати далі), і виконується **між** отриманням запиту й фінальною відповіддю.

```javascript
import express from "express";
const app = express();

// Найпростіший middleware — логує кожен запит
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next(); // ← передати керування наступному
});
```

### L2 — Middle
Middleware вирішує **наскрізні (cross-cutting) задачі** — те, що потрібно багатьом маршрутам, але не є їх бізнес-логікою:
| Задача | Приклад middleware |
|---|---|
| Логування | запис кожного запиту |
| Парсинг тіла | `express.json()` — JSON → `req.body` |
| Автентифікація | перевірити токен, покласти `req.user` |
| Авторизація | перевірити права |
| CORS | заголовки крос-доменних запитів |
| Валідація | перевірити вхідні дані |
| Rate limiting | обмежити кількість запитів |
| Обробка помилок | централізовано (питання 20) |

```javascript
app.use(express.json());        // вбудований: парсить JSON-тіло
app.use(cors());                // сторонній: CORS-заголовки
app.use(authMiddleware);        // власний: автентифікація

// Middleware лише для конкретного маршруту:
app.get("/admin", checkAdmin, (req, res) => res.send("Адмінка"));
```

**Три типи middleware:**
- **Application-level** — `app.use(...)` (на всі запити).
- **Router-level** — `router.use(...)` (на групу маршрутів).
- **Route-level** — `app.get("/x", mw, handler)` (на один маршрут).

**Gotcha:** middleware виконуються **в порядку реєстрації** (питання 19). `express.json()` має бути **до** обробників, що читають `req.body` — інакше `req.body` буде `undefined`.

### L3 — Senior
Middleware реалізує патерн **Chain of Responsibility (ланцюг відповідальності)**: кожна ланка або **обробляє** запит і завершує його (`res.send`), або **передає** далі (`next()`). Запит «тече» крізь ланцюг, поки хтось не відповість.

**Чому це потужна архітектура:**
- **Separation of concerns** — бізнес-логіка маршруту чиста, а auth/logging/validation винесені в перевикористовувані ланки.
- **Композиція** — складна поведінка збирається з простих незалежних функцій (як Unix-pipe чи функціональна композиція).
- **DRY** — один auth-middleware на сотні маршрутів замість дублювання.

**Трейдоф:** елегантне декларативне розділення наскрізних аспектів ↔ **неявність** (важко простежити, що саме виконається для запиту — порядок і умови розкидані по реєстраціях), складніший дебаг (глибокий стек `next()`), ризик «забутого» `next()` (запит зависає назавжди). Це той самий компроміс, що декоратори в Python: чистота ↔ прихований потік виконання.

**Сучасний контекст:** ця ж модель — у Koa (async middleware зі «цибулевою» моделлю, де `await next()` дозволяє код **до й після** наступної ланки), Fastify (hooks), NestJS (interceptors/guards). Express — найпростіша й найпоширеніша реалізація.

---

## 18. Як переходити з однієї middleware в іншу?

### L1 — Junior
**Через виклик `next()`.** Це «естафетна паличка»: викликаєш `next()` — передаєш керування наступному middleware в ланцюгу. **Не викличеш — запит зависне** (клієнт чекатиме вічно).

```javascript
app.use((req, res, next) => {
  console.log("middleware 1");
  next();                    // → передаємо далі
});
app.use((req, res, next) => {
  console.log("middleware 2"); // спрацює завдяки next() вище
  next();
});
```

### L2 — Middle
**Три варіанти, що може зробити middleware:**
```javascript
app.use((req, res, next) => {
  // Варіант 1: передати далі
  next();

  // Варіант 2: завершити запит (НЕ викликати next)
  res.status(401).send("Unauthorized"); // ланцюг зупиняється тут

  // Варіант 3: передати ПОМИЛКУ → перейти до error handler (питання 20)
  next(new Error("щось пішло не так"));
});
```

**Ключові правила:**
- `next()` — далі по ланцюгу.
- `next(err)` — **пропустити** всі звичайні middleware й перестрибнути одразу до **error-handler** (питання 20).
- `next("route")` — пропустити решту middleware **цього** маршруту, перейти до наступного відповідного маршруту.
- Завершив відповідь (`res.send/json/end`) → `next()` **не викликай** (інакше «headers already sent»).

**Gotcha — найчастіша помилка:** забув `next()` і не відправив відповідь → запит **висить**, клієнт таймаутиться. Або навпаки — і `res.send()`, і `next()` → помилка `ERR_HTTP_HEADERS_SENT` (намагаєшся відповісти двічі).

### L3 — Senior
**Як це працює під капотом:** Express тримає **масив (стек) middleware** і вказівник на поточну позицію. `next()` — це функція, яку Express **передає** в кожен middleware; її виклик інкрементує вказівник і викликає наступну функцію в масиві. Тобто `next()` — це **продовження (continuation)** ланцюга.

```javascript
// Спрощена ментальна модель механізму:
function dispatch(index) {
  const middleware = stack[index];
  if (!middleware) return; // кінець ланцюга
  middleware(req, res, () => dispatch(index + 1)); // next = виклик наступного
}
```

**Async-пастка (критично, Express 4):** у синхронному коді `next(err)` працює просто. Але в **async middleware** відхилений Promise **не** ловиться Express автоматично (у Express 4):
```javascript
// ❌ Express 4: якщо await кине — помилка ВТРАЧЕНА, запит зависне
app.get("/user", async (req, res) => {
  const user = await db.findUser(req.id); // якщо throw → unhandled rejection
  res.json(user);
});

// ✅ Express 4: лови вручну й передавай у next
app.get("/user", async (req, res, next) => {
  try {
    const user = await db.findUser(req.id);
    res.json(user);
  } catch (err) {
    next(err); // → error handler
  }
});
```
**Express 5** виправив це — відхилені Promise з async-обробників **автоматично** передаються в `next(err)`. У Express 4 використовують обгортку `express-async-handler` або `try/catch`.

**Трейдоф:** явний `next()` дає повний контроль над потоком (можна розгалужувати, переривати, передавати помилки) ↔ легко забути виклик (зависання) або викликати двічі (подвійна відповідь). Сучасні фреймворки (Koa/Fastify) роблять це безпечнішим через `async/await` (повернення з функції = автоматичне «next»).

---

## 19. Як пріоритизувати middleware?

### L1 — Junior
**Порядок = пріоритет. Middleware виконуються згори вниз, у порядку реєстрації.** Що зареєстрував раніше — спрацює раніше. Жодних «ваг» чи «номерів пріоритету» — лише **позиція в коді**.

```javascript
app.use(logger);      // 1-й — спрацює першим
app.use(authCheck);   // 2-й
app.use(routes);      // 3-й
// Помінявши рядки місцями — зміниш порядок виконання
```

### L2 — Middle
**Правильний порядок (типовий продакшн-конвеєр):**
```javascript
const app = express();

// 1. Безпека/інфраструктура — найперше
app.use(helmet());            // безпечні заголовки
app.use(cors());              // CORS

// 2. Парсинг — щоб req.body був готовий для всіх нижче
app.use(express.json());

// 3. Логування/спостереження
app.use(requestLogger);

// 4. Автентифікація → авторизація
app.use(authenticate);

// 5. Маршрути (бізнес-логіка)
app.use("/api/users", usersRouter);
app.use("/api/orders", ordersRouter);

// 6. 404 — після всіх маршрутів (нічого не співпало)
app.use((req, res) => res.status(404).send("Not Found"));

// 7. Error handler — НАЙОСТАННІШИЙ (питання 20)
app.use(errorHandler);
```

**Чому такий порядок (логіка пріоритетів):**
- `express.json()` **перед** маршрутами → інакше `req.body` порожній.
- `authenticate` **перед** маршрутами → щоб захистити їх.
- `404` **після** всіх маршрутів → інакше перехопить усе.
- `errorHandler` **останній** → ловить помилки з усього вище.

**Gotcha:** порядок критичний і часто є джерелом багів. Класика: `express.json()` зареєстрований **після** роутера → `req.body === undefined`. Або 404-handler **перед** маршрутами → усі запити отримують 404.

### L3 — Senior
**Path-specificity теж впливає на «пріоритет»:** Express зіставляє middleware за **шляхом** і **порядком**. Глобальний `app.use(mw)` (без шляху) спрацьовує на все; `app.use("/api", mw)` — лише на `/api/*`. Усередині — все одно порядок реєстрації.

```javascript
app.use(globalMw);              // на всі
app.use("/admin", adminOnly);   // лише /admin/*
app.get("/admin/users", routeMw, handler); // routeMw лише на цей маршрут
```

**Архітектурні принципи пріоритизації (senior-мислення):**
1. **Дешеве й відсіювальне — раніше:** rate limiting, auth відкидають погані запити **до** дорогої роботи (не парсити тіло запиту, який все одно відхилимо за rate limit).
2. **Безпека — на вході:** helmet, CORS, валідація — найперше (defense at the edge).
3. **Залежності даних:** middleware, що готує дані (`req.body`, `req.user`), — перед тими, хто їх споживає.
4. **Catch-all — в кінці:** 404 і error handler замикають конвеєр.

**Трейдоф «порядок = пріоритет»:** простота й передбачуваність (немає прихованої системи ваг — читаєш код згори вниз) ↔ крихкість (перестановка двох рядків мовчки ламає поведінку; немає декларативного «це має бути перед тим»). Великі застосунки виносять конфігурацію middleware в одне місце (`app.ts`) із коментарями про **чому** саме такий порядок — інакше це стає прихованою залежністю. Деякі фреймворки (NestJS, Fastify) дають декларативніший контроль (guards, hooks із явними фазами) замість суто позиційного.

---

## 20. Як організувати error handler?

### L1 — Junior
**Аналогія — служба порятунку, що чергує в кінці.** Будь-де щось пішло не так — виклик іде до **однієї централізованої служби** (error handler), яка вирішує, що відповісти клієнту. Не треба обробляти помилки в кожному маршруті окремо.

**Error-handling middleware — це middleware з ЧОТИРМА аргументами** (`err` першим):
```javascript
app.use((err, req, res, next) => {   // 4 аргументи = error handler!
  console.error(err.stack);
  res.status(500).json({ error: "Internal Server Error" });
});
```

### L2 — Middle
**Правила error handler:**
1. **Чотири аргументи** `(err, req, res, next)` — саме за кількістю аргументів Express розпізнає його як error handler.
2. **Реєструється ОСТАННІМ** — після всіх маршрутів і middleware.
3. Спрацьовує, коли хтось викликав **`next(err)`** (або кинув помилку в Express 5 / sync-коді).

```javascript
import express from "express";
const app = express();

app.use(express.json());

app.get("/user/:id", async (req, res, next) => {
  try {
    const user = await db.findUser(req.params.id);
    if (!user) {
      const err = new Error("User not found");
      err.status = 404;
      throw err;            // → перехопить catch → next(err)
    }
    res.json(user);
  } catch (err) {
    next(err);              // передаємо в централізований handler
  }
});

// 404 для неіснуючих маршрутів
app.use((req, res) => res.status(404).json({ error: "Not Found" }));

// ЦЕНТРАЛІЗОВАНИЙ error handler — ОСТАННІЙ
app.use((err, req, res, next) => {
  const status = err.status || 500;
  console.error(`[${status}]`, err.message);
  res.status(status).json({
    error: status === 500 ? "Internal Server Error" : err.message,
  });
});
```

**Best practices:**
- **Кастомні класи помилок** із `status` (`NotFoundError`, `ValidationError`).
- **Не віддавай стектрейс клієнту** в проді (витік внутрішньої інформації — безпека).
- Логуй повну помилку, але клієнту — безпечне повідомлення.

**Gotcha:** error handler **мусить мати рівно 4 параметри**, навіть якщо `next` не використовуєш — інакше Express вважатиме його звичайним middleware й помилки в нього не потраплять. Це найчастіша причина «error handler не спрацьовує».

### L3 — Senior
**Як Express розрізняє типи middleware:** за **arity** (кількістю параметрів функції). 3 аргументи `(req,res,next)` → звичайний; 4 аргументи `(err,req,res,next)` → error handler. Express тримає **окремий** прохід по error-handling middleware: коли викликано `next(err)`, він **пропускає всі звичайні** middleware й шукає наступний 4-аргументний. Тому помилка «перестрибує» бізнес-логіку прямо до обробника.

**Async-помилки — головна пастка (зв'язок із питанням 18):**
```javascript
// ❌ Express 4: async throw НЕ потрапляє в error handler автоматично
app.get("/x", async (req, res) => {
  await somethingThatThrows(); // unhandled rejection → handler не спрацює
});

// ✅ Рішення 1: обгортка (DRY для всіх async-маршрутів)
const asyncHandler = (fn) => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

app.get("/x", asyncHandler(async (req, res) => {
  await somethingThatThrows(); // → автоматично next(err) → error handler
  res.json(result);
}));

// ✅ Рішення 2: Express 5 робить це з коробки
```

**Архітектура обробки помилок (senior-рівень):**
- **Операційні vs програмні помилки:** операційні (user not found, validation) — очікувані, обробляються gracefully (4xx). Програмні (null reference, баг) — несподівані (5xx), логуються, можливо тригерять рестарт/алерт.
- **Централізація:** один error handler → консистентний формат відповідей, єдина точка логування/моніторингу (Sentry), легше міняти політику.
- **Безпека:** ніколи не віддавай клієнту стектрейс/SQL-помилки/внутрішні шляхи — це витік (defense in depth).
- **Process-level safety:** `process.on("uncaughtException")` і `unhandledRejection` — остання лінія оборони; за best-practice після них процес **завершують** (стан невідомий → краще рестарт під оркестратором, ніж робота в зіпсованому стані).

**Трейдоф:** централізований error handler дає консистентність, єдину точку контролю й чисті маршрути ↔ вимагає дисципліни (кожен async-маршрут має коректно прокидати помилку в `next`), і занадто загальний handler може приховати специфіку. Senior поєднує: типізовані класи помилок (несуть `status`/код) + централізований handler, що мапить їх на HTTP-відповіді + структуроване логування + моніторинг.

> ⚠️ Поведінка async-помилок відрізняється Express 4 vs 5. Деталі `uncaughtException`/graceful shutdown — звіряй з docs Node й Express для своєї версії.
