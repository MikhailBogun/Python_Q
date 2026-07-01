# Блок 10. JavaScript / Node.js — Advanced (20 питань)

> Формат — **Принцип Сходів**: L1 Junior → L2 Middle → L3 Senior.
> Доповнює блоки 01/03/06/07 — тут глибокі й підступні теми (замикання, прототипи, currying, generators, Proxy, coercion, Buffer). ES2022+. Код перевірений запуском.

---

## 1. Замикання (closures) ⭐

### L1 — Junior
**Аналогія — рюкзак функції.** **Замикання** — функція «пам'ятає» змінні з місця, де її **створили**, навіть коли викликається деінде. Вона носить із собою «рюкзак» зовнішніх змінних.

```javascript
function counter() {
  let count = 0;              // "у рюкзаку"
  return () => ++count;      // внутрішня функція бачить count
}
const inc = counter();
inc(); // 1
inc(); // 2  — count живе між викликами!
```

### L2 — Middle
Замикання = функція + її **лексичне оточення** (зовнішні змінні). Застосування:
```javascript
// 1. Приватний стан (інкапсуляція)
function createBank(balance) {
  return {
    deposit: (n) => balance += n,
    getBalance: () => balance,   // balance недоступний ззовні напряму
  };
}

// 2. Фабрики функцій
const multiply = (x) => (y) => x * y;
const double = multiply(2);   // double(5) → 10
```

**Gotcha — замикання в циклі з `var`:**
```javascript
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i)); // 3,3,3
for (let i = 0; i < 3; i++) setTimeout(() => console.log(i)); // 0,1,2
```

### L3 — Senior
Замикання можливе, бо JS має **лексичну область видимості** й функції — first-class. Внутрішня функція тримає **посилання** на змінні (не копію) → бачить актуальне значення. `let` створює **нову прив'язку на ітерацію** (тому 0,1,2), `var` — одну спільну.

**Трейдоф:** замикання дають приватність, стан без класів, каррінг ↔ **витік пам'яті** — замкнена змінна живе, поки жива функція (тримає великий об'єкт → не звільниться). Основа: модульного патерну, hooks (React), мемоізації, debounce/throttle. Кожен callback у JS — потенційне замикання.

---

## 2. Прототипне наслідування (prototype chain) ⭐

### L1 — Junior
**Аналогія — питай батьків, якщо сам не знаєш.** Кожен об'єкт має **прототип** — інший об'єкт, куди JS іде шукати властивість/метод, якщо не знайшов у самому об'єкті. Це **ланцюг прототипів**.

```javascript
const animal = { eats: true };
const dog = Object.create(animal);   // dog.__proto__ === animal
dog.barks = true;
dog.eats;   // true — знайдено в прототипі!
```

### L2 — Middle
```javascript
// Ланцюг: instance → Constructor.prototype → Object.prototype → null
function Dog(name) { this.name = name; }
Dog.prototype.bark = () => "Гав";   // метод на прототипі (спільний)

const rex = new Dog("Рекс");
rex.bark();                          // "Гав" (знайдено в Dog.prototype)
Object.getPrototypeOf(rex) === Dog.prototype;  // true
rex.hasOwnProperty("name");          // true (власна)
rex.hasOwnProperty("bark");          // false (у прототипі)
```
**`class` — синтаксичний цукор** над прототипами: `class Dog { bark(){} }` кладе `bark` у `Dog.prototype`.

### L3 — Senior
**`__proto__` vs `prototype` (плутають):**
- **`prototype`** — властивість **функції-конструктора**; об'єкт, що стане прототипом екземплярів.
- **`__proto__`** (= `Object.getPrototypeOf`) — посилання **екземпляра** на його прототип.
- `rex.__proto__ === Dog.prototype`.

**Чому методи на прототипі:** якби метод оголошувався в конструкторі (`this.bark = ...`), кожен екземпляр мав би **свою копію** (пам'ять). На прототипі — **один спільний** метод для всіх.

**Трейдоф:** прототипне наслідування гнучкіше за класичне (динамічне, делегування), але заплутане (`__proto__` vs `prototype`, мутація прототипу впливає на всіх). Пошук по ланцюгу — `O(глибина)`; глибокі ланцюги повільніші. `Object.create(null)` — об'єкт **без** прототипу (чистий словник, без `toString` тощо).

---

## 3. Оператор `new` і функції-конструктори

### L1 — Junior
**`new`** створює новий об'єкт із функції-конструктора.
```javascript
function User(name) { this.name = name; }
const u = new User("Іван");   // { name: "Іван" }
```

### L2 — Middle
**Що робить `new` (4 кроки):**
```javascript
function User(name) {
  // 1. створюється порожній об'єкт {}
  // 2. його __proto__ = User.prototype
  // 3. this = цей об'єкт
  this.name = name;
  // 4. повертається this (якщо не return об'єкт явно)
}
```
**Gotcha:** забув `new` → `this` = `undefined` (strict) / global → баг. Тому класи (`class`) кидають помилку без `new`.

### L3 — Senior
`new Fn(args)` ≈:
```javascript
function myNew(Fn, ...args) {
  const obj = Object.create(Fn.prototype);   // кроки 1-2
  const result = Fn.apply(obj, args);        // крок 3: this=obj
  return result instanceof Object ? result : obj;  // крок 4
}
```
**Нюанс:** якщо конструктор **повертає об'єкт** — повертається він (не `this`); повертає примітив — ігнорується, повертається `this`. Це використовують для синглтонів/фабрик. `new.target` — детектує виклик через `new`. Сучасно — `class` (чіткіше, кидає без `new`, приватні поля `#`).

---

## 4. Debounce vs Throttle ⭐

### L1 — Junior
Обидва **обмежують частоту** виклику функції (для scroll, resize, input):
- **Debounce** — виконати **після паузи** (перестав друкувати → шукаємо). Останній виграє.
- **Throttle** — виконати **не частіше ніж раз на N мс** (регулярно, не частіше).

### L2 — Middle
```javascript
// DEBOUNCE — чекає тишу (пошук при введенні)
function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

// THROTTLE — максимум раз на interval (scroll, resize)
function throttle(fn, interval) {
  let last = 0;
  return (...args) => {
    const now = Date.now();
    if (now - last >= interval) {
      last = now;
      fn(...args);
    }
  };
}
```
| | Debounce | Throttle |
|---|---|---|
| Коли | після паузи | регулярно, не частіше N |
| Для | пошук, автозбереження, валідація | scroll, resize, mousemove |

### L3 — Senior
Обидва — **замикання** (п.1) з таймером у «рюкзаку». Debounce «скидає» таймер на кожен виклик → виконає лише коли настане тиша (ризик — на постійному потоці **ніколи** не виконає, тому інколи додають `maxWait`). Throttle гарантує регулярність.

**Трейдоф/варіанти:** debounce з `leading`/`trailing` (виконати на початку і/або в кінці); throttle через таймер vs timestamp (різна поведінка на межах). У проді — `lodash.debounce/throttle` (edge cases, cancel, flush). Це фундамент оптимізації подій у UI (менше ререндерів, менше запитів).

---

## 5. Currying та partial application

### L1 — Junior
**Currying** — перетворити функцію багатьох аргументів на **ланцюг функцій по одному аргументу**.
```javascript
const add = (a) => (b) => (c) => a + b + c;
add(1)(2)(3);   // 6
```
**Partial application** — зафіксувати частину аргументів наперед.

### L2 — Middle
```javascript
// Currying — конфігурація частинами
const log = (level) => (message) => console.log(`[${level}] ${message}`);
const error = log("ERROR");
error("щось впало");   // [ERROR] щось впало

// Partial application через bind
function multiply(a, b) { return a * b; }
const double = multiply.bind(null, 2);   // a=2 зафіксовано
double(5);   // 10
```
**Навіщо:** переиспользування (створити спеціалізовані функції), композиція, конфігурація.

### L3 — Senior
Currying тримається на **замиканнях** (кожна функція пам'ятає попередні аргументи). Різниця:
- **Curry:** `f(a)(b)(c)` — строго по одному.
- **Partial:** `f(a, b)` частково → чекає решту.

**Універсальний curry:**
```javascript
const curry = (fn) => {
  const curried = (...args) =>
    args.length >= fn.length ? fn(...args) : (...more) => curried(...args, ...more);
  return curried;
};
const add3 = curry((a, b, c) => a + b + c);
add3(1)(2)(3); add3(1, 2)(3); add3(1)(2, 3);   // усі → 6
```
**Трейдоф:** каррінг дає елегантну композицію й переиспользування у **функціональному** стилі (point-free, pipe) ↔ читабельність для незвичних, overhead замикань. Основа функціональних бібліотек (Ramda). У JS рідше за Haskell, але корисно для конфігурованих утиліт/middleware.

---

## 6. Memoization (мемоізація)

### L1 — Junior
**Аналогія — записник результатів.** Мемоізація **кешує** результати функції: той самий вхід → повертаємо збережене, не рахуємо знову.
```javascript
const cache = {};
function fib(n) {
  if (n in cache) return cache[n];
  return cache[n] = n < 2 ? n : fib(n-1) + fib(n-2);
}
```

### L2 — Middle
```javascript
// Універсальний мемоізатор
function memoize(fn) {
  const cache = new Map();
  return (...args) => {
    const key = JSON.stringify(args);   // ключ із аргументів
    if (cache.has(key)) return cache.get(key);
    const result = fn(...args);
    cache.set(key, result);
    return result;
  };
}
const slowSquare = memoize((n) => { /* важке */ return n * n; });
```
**Коли:** дорогі **чисті** функції (той самий вхід → той самий вихід), повторювані виклики.

### L3 — Senior
Мемоізація — класичний **обмін пам'яті на час** (як DP): наївний рекурсивний Фібоначчі `O(2ⁿ)` → з кешем `O(n)`.

**Нюанси (senior):**
- **Лише для чистих функцій** — з побічними ефектами/залежністю від часу зламається.
- **Ключ:** `JSON.stringify` для складних аргументів (повільно, не всі типи), або WeakMap для об'єктів-ключів.
- **Витік пам'яті:** необмежений кеш росте вічно → LRU з лімітом.
- У React — `useMemo`/`useCallback` (блок 09). У проді — `lodash.memoize`.

**Трейдоф:** швидкість ↔ пам'ять + складність (інвалідація кешу — одна з двох складних речей). Мемоізуй **гарячі** дорогі чисті функції, не все підряд.

---

## 7. Generators та iterators ⭐

### L1 — Junior
**Generator** — функція, що може **призупинятись** і віддавати значення по одному через `yield`.
```javascript
function* count() {
  yield 1;
  yield 2;
  yield 3;
}
for (const n of count()) console.log(n);   // 1, 2, 3
```

### L2 — Middle
```javascript
function* idGenerator() {
  let id = 1;
  while (true) yield id++;   // нескінченний, але лінивий!
}
const gen = idGenerator();
gen.next();   // { value: 1, done: false }
gen.next();   // { value: 2, done: false }

// Iterator protocol — об'єкт з next()
const range = {
  from: 1, to: 3,
  [Symbol.iterator]() {
    let cur = this.from, last = this.to;
    return { next: () => cur <= last ? {value: cur++, done: false} : {value: undefined, done: true} };
  }
};
[...range];   // [1, 2, 3]
```

### L3 — Senior
Generator повертає **iterator**, що зберігає **стан** між `yield` (заморожений frame) → лінива генерація, `O(1)` пам'яті для нескінченних послідовностей. `yield` двонаправлений: `gen.next(value)` передає значення назад у `yield`.

**Застосування:**
- **Ліниві/нескінченні** послідовності (без матеріалізації).
- **Async iteration** (`for await...of` над async-generator — стрімінг даних).
- Історично — основа корутин/co (до async/await).
- Кастомні ітеровані структури (`Symbol.iterator`).

**Трейдоф:** лінива обробка великих/нескінченних даних + елегантні ітератори ↔ складніший дебаг (застиглий стан), одноразовість. Прямий аналог Python-генераторів. `Symbol.iterator` робить об'єкт сумісним з `for...of`, spread, destructuring.

---

## 8. Symbols

### L1 — Junior
**Symbol** — унікальний примітивний тип. Кожен `Symbol()` **завжди унікальний**, навіть з однаковим описом.
```javascript
const a = Symbol("id");
const b = Symbol("id");
a === b;   // false — унікальні!
```

### L2 — Middle
**Застосування:**
```javascript
// 1. Унікальні ключі об'єкта (без колізій)
const id = Symbol("id");
const user = { name: "Іван", [id]: 42 };
user[id];   // 42; не з'явиться в for...in, Object.keys (прихований)

// 2. Well-known symbols — гачки в поведінку мови
const obj = { [Symbol.iterator]() { /* ... */ } };   // робить ітерованим
```
**Well-known:** `Symbol.iterator`, `Symbol.asyncIterator`, `Symbol.toPrimitive`, `Symbol.hasInstance`.

### L3 — Senior
Symbols вирішують дві задачі:
1. **Колізії ключів** — symbol-ключ гарантовано унікальний → бібліотеки додають метадані в чужі об'єкти без ризику затерти. «Приховані» від звичайної ітерації (`Object.keys`, `JSON.stringify`), доступні через `Object.getOwnPropertySymbols`.
2. **Кастомізація поведінки мови** — well-known symbols дають гачки: `Symbol.iterator` (робить ітерованим, п.7), `Symbol.toPrimitive` (як об'єкт приводиться до примітиву, п.10), `Symbol.hasInstance` (`instanceof`).

**`Symbol.for(key)`** — глобальний реєстр (спільні symbols між частинами коду/realms). **Трейдоф:** приховані/унікальні ключі й розширення мови ↔ не серіалізуються (JSON їх ігнорує), менш очевидні. Нішевий, але потужний для бібліотек/протоколів.

---

## 9. Proxy та Reflect

### L1 — Junior
**Proxy** — «обгортка» навколо об'єкта, що **перехоплює** операції (читання, запис) і дає виконати свій код.
```javascript
const user = { name: "Іван" };
const proxy = new Proxy(user, {
  get(target, prop) { console.log(`читаю ${prop}`); return target[prop]; }
});
proxy.name;   // логує "читаю name" → "Іван"
```

### L2 — Middle
```javascript
// Валідація при записі
const validated = new Proxy({}, {
  set(target, prop, value) {
    if (prop === "age" && typeof value !== "number") throw new TypeError("age має бути числом");
    target[prop] = value;
    return true;
  }
});
validated.age = 30;      // ок
validated.age = "тридцять";   // TypeError

// Reflect — «правильний» спосіб виконати операцію в trap
const p = new Proxy(obj, {
  get(t, prop, receiver) { return Reflect.get(t, prop, receiver); }
});
```
**Traps:** `get`, `set`, `has`, `deleteProperty`, `apply`, `construct` тощо.

### L3 — Senior
Proxy — метапрограмування: перехоплення **фундаментальних операцій** над об'єктом. **Reflect** — набір методів, що виконують ці операції «за замовчуванням» (дефолтна поведінка trap), із коректним `receiver` (важливо для гетерів/прототипів).

**Застосування:** реактивність (**Vue 3** на Proxy — відстежує зміни), валідація, логування/аудит, віртуальні/lazy об'єкти, негативні індекси масивів, immutable-обгортки, API-mock.

**Трейдоф:** потужна прозора інтерцепція ↔ **overhead** (кожна операція через trap — повільніше за прямий доступ), складність дебагу («магія»), не всі операції перехоплюються ідеально. Не для гарячих шляхів; для фреймворків/бібліотек (реактивність, ORM) — незамінно. Reflect **завжди** в парі з Proxy для коректності.

---

## 10. `==` vs `===` та type coercion ⭐

### L1 — Junior
- **`===`** (strict) — рівність **без приведення типів** (тип + значення).
- **`==`** (loose) — **приводить типи** перед порівнянням.
```javascript
1 === "1";   // false (різні типи)
1 == "1";    // true (рядок → число)
```
**Правило: завжди `===`** (передбачувано).

### L2 — Middle
**Класичні пастки coercion:**
```javascript
0 == "";        // true   (обидва → 0? насправді "" → 0)
0 == "0";       // true
"" == "0";      // false  (обидва рядки, не рівні!)
null == undefined;  // true
null == 0;      // false  (null рівний ЛИШЕ undefined)
NaN == NaN;     // false  (NaN нерівний нічому)
[] == false;    // true   (моторошно)
[] == ![];      // true   (!!! [] → "" → 0, ![] → false → 0)
```
**Falsy значення:** `false, 0, -0, "", null, undefined, NaN`. Решта — truthy (включно з `[]`, `{}`, `"0"`, `"false"`!).

### L3 — Senior
`==` запускає **abstract equality algorithm** з приведенням: рядок↔число → до числа; boolean → до числа; об'єкт↔примітив → об'єкт через `Symbol.toPrimitive`/`valueOf`/`toString`. Звідси `[] == ![]`: `![]` → `false` → `0`; `[]` → `""` → `0`; `0 == 0` → `true`.

**`null`/`undefined` — особливі:** `==` рівні лише один одному й собі (не приводяться до 0). `null == undefined` → `true`; `null == 0` → `false`.

**Правила Senior:**
- **Завжди `===`** (крім однієї легітимної ідіоми: `x == null` для перевірки «null **або** undefined» одразу).
- `NaN` — через `Number.isNaN` (блок 03, п.33).
- Truthy-перевірки обережно: `if (arr.length)` ок, але `if (value)` спіткнеться на `0`/`""` (використовуй `??`, блок 03 п.39).

---

## 11. Shallow vs deep copy

### L1 — Junior
- **Shallow (поверхнева)** — копіює верхній рівень; вкладені об'єкти **спільні** (за посиланням).
- **Deep (глибока)** — копіює **все рекурсивно** (незалежна копія).
```javascript
const orig = { a: 1, nested: { b: 2 } };
const shallow = { ...orig };
shallow.nested.b = 99;   // змінить і orig.nested.b! (спільний)
```

### L2 — Middle
```javascript
// SHALLOW
const s1 = { ...obj };
const s2 = Object.assign({}, obj);
const arr2 = [...arr];

// DEEP
const deep = structuredClone(obj);   // ✅ сучасно (Node 17+, браузери)
const jsonDeep = JSON.parse(JSON.stringify(obj));  // хак (обмежений)
```
**Gotcha:** `{...obj}` / `[...arr]` — **лише верхній рівень**. Вкладене — спільне (класична причина багів «змінив копію, а оригінал теж змінився»).

### L3 — Senior
**`structuredClone` vs JSON-хак:**
| | `structuredClone` | `JSON.parse(JSON.stringify)` |
|---|---|---|
| Date, Map, Set, RegExp | ✅ зберігає | ❌ ламає (Date → рядок, Map → {}) |
| функції | ❌ (кидає) | ❌ (пропускає) |
| циклічні посилання | ✅ | ❌ (падає) |
| undefined | ✅ | ❌ (пропускає) |
| швидкість | нативно, швидко | повільно (серіалізація) |

**structuredClone** (structured clone algorithm) — правильний нативний deep copy. JSON-хак — legacy, ламає типи, падає на циклах, але простий для plain-JSON.

**Трейдоф immutable-стилю (React/Redux):** deep copy дорога для великих структур → **structural sharing** (Immer, Immutable.js) — копіювати лише змінений шлях. Знати різницю shallow/deep — критично для незмінності стану (зміна вкладеного без deep copy = мутація спільного = баги change detection).

---

## 12. Event delegation, bubbling, capturing

### L1 — Junior
**Event bubbling** — подія «спливає» від елемента до батьків. **Event delegation** — повісити один слухач на **батька** замість багатьох на дітей.
```javascript
// Замість слухача на кожен <li> — один на <ul>
list.addEventListener("click", (e) => {
  if (e.target.matches("li")) handle(e.target);
});
```

### L2 — Middle
**Дві фази поширення:**
```
Capturing (вниз):  document → ... → target
Target:            сам елемент
Bubbling (вгору):  target → ... → document   (за замовчуванням тут слухаємо)
```
```javascript
el.addEventListener("click", fn);              // bubbling (default)
el.addEventListener("click", fn, true);        // capturing
e.stopPropagation();                           // зупинити поширення
e.preventDefault();                            // скасувати дефолт (submit, link)
```

### L3 — Senior
**Чому delegation потужна:**
- **Перформанс** — один слухач замість тисяч (менше пам'яті/обробників).
- **Динамічні елементи** — працює для елементів, доданих **після** навішування (новий `<li>` уже «під наглядом» батька).

**Механізм:** подія на `<li>` спливає до `<ul>`, слухач `<ul>` дивиться `e.target` (де реально клікнули). `e.currentTarget` — де слухач; `e.target` — де подія виникла.

**Трейдоф:** delegation — масштабованість і робота з динамікою ↔ треба фільтрувати `e.target` (не всі кліки цікаві), деякі події не спливають (`focus`, `blur` — використовуй `focusin`/`focusout`). Основа обробки подій у списках/таблицях/SPA. `stopPropagation` — обережно (ламає інші delegation-слухачі вище).

---

## 13. Immutability (Object.freeze, незмінність)

### L1 — Junior
**Immutability** — не змінювати дані на місці, а створювати нові. `const` захищає **прив'язку**, `Object.freeze` — **вміст**.
```javascript
const obj = Object.freeze({ a: 1 });
obj.a = 2;   // тихо ігнорується (strict — TypeError)
```

### L2 — Middle
```javascript
const frozen = Object.freeze({ a: 1, nested: { b: 2 } });
frozen.a = 9;            // ❌ не змінюється
frozen.nested.b = 9;     // ✅ ЗМІНЮЄТЬСЯ! freeze поверхневий

// Immutable-оновлення (замість мутації)
const updated = { ...state, count: state.count + 1 };
const newArr = [...arr, item];          // не push
const without = arr.filter(x => x !== item);   // не splice
```
`Object.freeze` — **поверхневий** (deep freeze — рекурсивно вручну).

### L3 — Senior
**Навіщо immutability:**
- **Передбачуваність** — дані не міняються під ногами (немає «хто це змінив?»).
- **Change detection** — React/Redux порівнюють за посиланням (`prev === next`); мутація не змінює посилання → UI не оновиться. Immutable оновлення = нове посилання = коректна реакція.
- **Thread-safety / concurrency** — незмінне безпечно шарити.

**Трейдоф:** передбачуваність + reactive-дружність ↔ алокація нових об'єктів (overhead для великих структур). Рішення для великих — **structural sharing** (Immer дає «мутабельний» синтаксис, продукує immutable результат через Proxy, п.9). `Object.freeze` — рантайм-захист (є вартість); `readonly` у TS — compile-time (безкоштовно, блок 08). Senior: immutable оновлення стану (spread/filter/map), `Object.freeze` для констант/захисту, Immer для складного стану.

---

## 14. `map` / `filter` / `reduce` + чейнінг

### L1 — Junior
Функціональні методи масиву (не мутують, повертають нове):
```javascript
[1,2,3].map(x => x*2);           // [2,4,6]  — трансформація
[1,2,3,4].filter(x => x%2===0);  // [2,4]    — вибірка
[1,2,3,4].reduce((s,x) => s+x, 0); // 10     — згортка в одне
```

### L2 — Middle
```javascript
// reduce — найпотужніший (можна виразити map/filter через нього)
const orders = [{amount: 100}, {amount: 250}, {amount: 50}];
const total = orders.reduce((sum, o) => sum + o.amount, 0);   // 400

// Групування через reduce
const byType = items.reduce((acc, it) => {
  (acc[it.type] ??= []).push(it);
  return acc;
}, {});

// Чейнінг
const result = data
  .filter(x => x.active)
  .map(x => x.value)
  .reduce((a, b) => a + b, 0);
```
**Gotcha:** `reduce` без **початкового значення** на порожньому масиві → **TypeError**. Завжди давай initial (`, 0`).

### L3 — Senior
`reduce` — універсальна згортка (fold): map, filter, group, flatten, count — усе виражається через неї. Але **читабельність** важливіша: явний `map/filter` зрозуміліший за хитрий `reduce`.

**Трейдоф чейнінг vs цикл:**
- Чейнінг — декларативно, immutable, композиційно ↔ **кожен метод — окремий прохід + проміжний масив** (`filter().map().reduce()` = 2 тимчасові масиви + 3 проходи).
- Для **дуже великих** даних — один `for...of` (один прохід, без алокацій) або **generators**/lazy (п.7).

**Нюанси:** `map` для трансформації (не для побічних ефектів — там `forEach`/`for`); `flatMap` (map + flatten); `reduce` для акумуляції. Функціональні методи не мутують (на відміну від `sort`/`splice`, п.15). Senior: читабельність за замовчуванням, ручний цикл — для гарячих шляхів.

---

## 15. Array: мутуючі vs немутуючі + пастка `sort()`

### L1 — Junior
Частина методів масиву **мутують** оригінал, частина — **повертають новий**.
```javascript
arr.push(4);      // МУТУЄ (додає в оригінал)
arr.map(...);     // НОВИЙ (не чіпає оригінал)
```

### L2 — Middle
| Мутуючі (міняють оригінал) | Немутуючі (новий масив) |
|---|---|
| `push`, `pop`, `shift`, `unshift` | `map`, `filter`, `slice`, `concat` |
| `splice`, `sort`, `reverse`, `fill` | `flatMap`, spread `[...]` |

**Головна пастка — `sort()`:**
```javascript
[1, 2, 10, 3].sort();          // [1, 10, 2, 3] ❌ (лексикографічно!)
[1, 2, 10, 3].sort((a,b)=>a-b); // [1, 2, 3, 10] ✅
```
`sort()` за замовчуванням перетворює на **рядки** й порівнює лексикографічно (`"10" < "2"`). І **мутує** оригінал!

### L3 — Senior
**Пастки:**
- **`sort` мутує + лексикографічний** за замовчуванням → завжди передавай comparator для чисел, і `[...arr].sort(...)` якщо треба зберегти оригінал.
- **`splice` vs `slice`** — splice мутує (вирізає), slice копіює (не мутує). Легко сплутати.
- Немутуючі копії ES2023: `toSorted`, `toReversed`, `toSpliced`, `with` — повертають **новий** масив (immutable-дружні).

**Чому це важливо:** мутація спільного масиву — джерело багів (особливо з immutable-стилем React/Redux, п.13). `[...arr].sort()` — безпечно; `arr.sort()` — тихо змінить оригінал, який хтось ще використовує.

**Трейдоф:** мутуючі — ефективні за пам'яттю (на місці) ↔ побічні ефекти; немутуючі — передбачувані ↔ алокація. Senior: immutable за замовчуванням (spread + немутуючі/`toSorted`), мутуючі — свідомо на локальних масивах.

---

## 16. Обробка помилок (error handling)

### L1 — Junior
```javascript
try {
  риск();
} catch (err) {
  console.error(err.message);
} finally {
  cleanup();   // завжди
}
```

### L2 — Middle
```javascript
// Кастомні класи помилок (ієрархія)
class ValidationError extends Error {
  constructor(message, field) {
    super(message);
    this.name = "ValidationError";
    this.field = field;
  }
}
try { validate(); }
catch (err) {
  if (err instanceof ValidationError) handleValidation(err);
  else throw err;   // не наше — пробросити
}

// Async помилки
async function fetchData() {
  try { return await fetch(url).then(r => r.json()); }
  catch (err) { handle(err); }
}
```
**Gotcha:** відхилений Promise **без** `.catch`/`try` → `unhandledRejection` (у Node може покласти процес).

### L3 — Senior
**Операційні vs програмні помилки** (блок 06, п.71): очікувані (мережа, валідація) — обробляй gracefully; баги — fail fast + рестарт.

**Патерни (senior):**
- **Кастомні класи** з `instanceof`, кодами, контекстом → структурована обробка.
- **Не глуши німо** (`catch {}`) — мінімум лог.
- **Async:** `try/catch` навколо `await`; `Promise.allSettled` для «обробити всі, не падати на першому» (блок 03, п.36).
- **Глобальні гачки:** `process.on("unhandledRejection")`, `uncaughtException` — остання лінія; після — коректно завершити (стан невідомий).
- **Error cause:** `new Error("msg", { cause: original })` — ланцюг причин.

**Трейдоф:** детальна обробка (стійкість, діагностика) ↔ шум/складність. Fail fast для програмних; graceful degradation для операційних. Один поганий вхід не має валити весь сервіс (блок 07, п.94 — стрими).

---

## 17. Spread / rest + destructuring (advanced)

### L1 — Junior
```javascript
const { name, age } = user;           // destructuring об'єкта
const [first, second] = arr;          // destructuring масиву
const merged = { ...a, ...b };        // spread
function f(...args) {}                // rest (збір)
```

### L2 — Middle
```javascript
// Дефолти + перейменування + вкладене
const { name = "Гість", address: { city } = {} } = user;

// Rest у destructuring
const { id, ...rest } = obj;          // rest = усе крім id
const [head, ...tail] = [1,2,3];      // head=1, tail=[2,3]

// Обмін без temp
[a, b] = [b, a];

// Spread — копія + злиття (порядок важливий!)
const config = { ...defaults, ...overrides };   // overrides перекриває
```

### L3 — Senior
**Нюанси:**
- **Spread — shallow** (п.11): `{...obj}` копіює верхній рівень, вкладене спільне.
- **Порядок у злитті:** пізніший перекриває (`{...a, ...b}` — `b` виграє на конфліктах).
- **Rest ≠ spread:** rest **збирає** (у визначенні), spread **розгортає** (у виклику/літералі).
- **Destructuring дефолт** — лише на `undefined` (не `null`/`0`), як `??` (блок 03, п.39).
- **Перформанс:** spread у циклі (`acc = [...acc, x]`) — `O(n²)` (копіює щоразу); краще `push` або `reduce`.

**Застосування:** immutable-оновлення (п.13), витяг props, дефолти функцій, злиття конфігів, видалення поля (`const {remove, ...rest} = obj`). Основа сучасного JS/React. Трейдоф: лаконічність/immutability ↔ shallow-пастки + O(n²) при зловживанні у циклах.

---

## 18. Buffer та бінарні дані (Node)

### L1 — Junior
**Buffer** — спосіб Node працювати з **сирими байтами** (файли, мережа, шифрування) — те, що не є текстом.
```javascript
const buf = Buffer.from("Привіт", "utf8");
buf.length;          // байти (не символи!)
buf.toString("utf8"); // назад у рядок
```

### L2 — Middle
```javascript
Buffer.from("hello");                    // з рядка
Buffer.from([1, 2, 3]);                   // з масиву байтів
Buffer.alloc(10);                         // 10 нульових байтів
Buffer.allocUnsafe(10);                   // швидше, але «сміття» (треба заповнити)

buf.toString("hex");                      // hex-представлення
buf.toString("base64");                   // base64
Buffer.concat([buf1, buf2]);              // склеїти
```
Buffer — підклас `Uint8Array` (типізований масив). Стрими (блок 07) віддають дані Buffer'ами.

### L3 — Senior
Buffer — це **пам'ять поза V8-heap** (`external` у `process.memoryUsage`), для ефективної роботи з бінарними даними без overhead JS-об'єктів. Основа файлового/мережевого I/O, crypto, стиснення.

**Нюанси (senior):**
- **Байти ≠ символи:** `"Привіт".length` (6 симв.) ≠ `Buffer.byteLength("Привіт")` (12 байт у UTF-8) — важливо для лімітів/протоколів.
- **`allocUnsafe`** — швидше (не обнуляє), але може містити **стару пам'ять** (витік даних!) → лише якщо одразу повністю заповнюєш.
- **Encodings:** utf8, hex, base64, latin1 — конвертація.
- **Zero-copy:** `buf.subarray()` — view без копії (як memoryview у Python); `slice` (deprecated поведінка) копіювала.

**Трейдоф:** ефективна робота з байтами ↔ ручне керування encodings/розмірами, ризик `allocUnsafe`. Для парсингу бінарних протоколів — Buffer + читання за offset (`readUInt32BE` тощо), аналог Python `struct`. Основа для відео/файлів/мережі.

---

## 19. `process.nextTick` vs `setImmediate` vs `setTimeout` (Node)

### L1 — Junior
Три способи «відкласти» виконання, з **різним пріоритетом**:
```javascript
setTimeout(() => console.log("timeout"), 0);
setImmediate(() => console.log("immediate"));
process.nextTick(() => console.log("nextTick"));
Promise.resolve().then(() => console.log("promise"));
console.log("sync");
```

### L2 — Middle
**Порядок виконання:**
```
1. sync         (синхронний код)
2. nextTick     (process.nextTick — найвищий пріоритет)
3. promise      (Promise microtasks)
4. timeout / immediate  (macrotasks — залежить від контексту)
```
- **`process.nextTick`** — окрема черга, виконується **перед** Promise microtasks і будь-якими macrotasks.
- **`setImmediate`** — фаза `check` event loop (після I/O).
- **`setTimeout(0)`** — фаза `timers`.

### L3 — Senior
*(Зв'язок з блоком 06/07 — event loop, microtasks.)* Ієрархія черг (Node):
```
[синхронний код] → [process.nextTick queue] → [Promise microtask queue]
→ [наступна фаза event loop: timers / poll / check ...]
```
- **`nextTick`** спорожнюється **повністю** перед мікрозадачами й будь-якою фазою → **найвищий** пріоритет.
- **`setImmediate` vs `setTimeout(0)`:** усередині **I/O-callback** `setImmediate` **завжди** перший (фаза check іде після poll); у головному модулі — **недетерміновано** (залежить від таймінгу старту).

**Небезпека — голодування (starvation):** рекурсивний `process.nextTick` (або нескінченний ланцюг мікрозадач) **ніколи** не віддасть керування event loop → I/O/таймери не виконаються, сервер «зависне» при зайнятому CPU. Тому важку роботу через `nextTick` — антипатерн.

**Коли що:** `setImmediate` — «виконати після поточної I/O-операції» (безпечніше за nextTick); `nextTick` — «до всього іншого, але обережно»; `setTimeout` — реальна затримка.

**⚠️ Пастка ESM top-level:** правило «nextTick → promise» діє в **нормальному** контексті (CommonJS, всередині callback). У **top-level ES-модуля** (`.mjs`) порядок **інвертується** (`promise` перед `nextTick`) — сам модуль виконується всередині microtask-контексту завантажувача. Перевірено на Node 22: у CJS та I/O-callback → `sync, nextTick, promise, immediate, timeout`; у `.mjs` top-level → `sync, promise, nextTick`. У реальному коді (обробники запитів завжди в callback) — контекст нормальний, тому покладайся на «nextTick першим».

> ⚠️ Точний порядок timer/immediate залежить від контексту (top-level ESM vs callback) й версії Node — звіряй з docs event loop.

---

## 20. Витоки пам'яті в JS/Node — причини й діагностика

### L1 — Junior
**Memory leak** — пам'ять, що більше не потрібна, але **не звільняється** (десь лишилось посилання). Процес росте → OOM. Критично для довгоживучих сервісів.

### L2 — Middle
**Типові причини:**
```javascript
// 1. Не прибрані слухачі подій
emitter.on("data", handler);       // накопичуються → removeListener

// 2. Не очищені таймери
setInterval(work, 1000);           // тримає замикання вічно → clearInterval

// 3. Необмежені кеші/масиви
const cache = {};                  // росте вічно → LRU/ліміт/TTL

// 4. Замикання, що тримають великі об'єкти
// 5. Глобальні змінні, що накопичують
```
*(Зв'язок з блоком 06, п.76-77.)*

### L3 — Senior
**Механізм:** V8 GC (generational, mark-sweep — блок 06 п.76) звільняє **недосяжне**. Витік = об'єкт **досяжний**, хоч непотрібний (є посилання): listener у EventEmitter, callback таймера, ключ у Map, замикання.

**Діагностика (senior):**
```javascript
process.memoryUsage();   // { rss, heapUsed, heapTotal, external }
// heapUsed монотонно росте під стабільним навантаженням = витік
```
- **Heap snapshots** (`--inspect` → Chrome DevTools → Memory) — 2 знімки до/після → comparison → що накопичилось + **retainers** (хто тримає).
- `--max-old-space-size` (тимчасово підняти ліміт для діагностики, не лікування).
- `clinic.js`, `py-spy`-аналоги, `heapdump`.

**Запобігання:**
- **Прибирати listeners/timers** у cleanup; `once` для одноразових; стежити за `MaxListenersExceededWarning`.
- **Bounded кеші** (lru-cache з maxSize/TTL).
- **WeakMap/WeakRef** — слабкі посилання, що **не заважають** GC (кеші/метадані, що не тримають об'єкти).
- Уникати глобальних акумуляторів.

**Трейдоф:** автоматичний GC прибирає use-after-free ↔ витоки через випадкову досяжність. У 24/7-сервісі навіть повільний витік за дні = OOM → моніторинг RSS/heap у часі + heap snapshots для кореня. Це прямий зв'язок з відео-роллю (блок про leaks) і Python GC (crossmapping refcount vs tracing).

---

## ✅ Чеклист (advanced JS)
Замикання (приватність/пам'ять) · прототипи (`__proto__` vs `prototype`) · `new` (4 кроки) · debounce/throttle · currying · memoization · generators/iterators · Symbols · Proxy/Reflect · coercion (`[] == ![]`) · shallow/deep (`structuredClone`) · event delegation · immutability · map/filter/reduce · sort()-пастка + мутуючі методи · error handling · spread/rest/destructuring · Buffer · nextTick/immediate/timeout · memory leaks.

## 🔑 Топ-питання
1. **Що таке замикання + приклад витоку?** → функція+оточення; тримає велику змінну живою.
2. **`__proto__` vs `prototype`?** → посилання екземпляра vs властивість конструктора.
3. **`[] == ![]` чому true?** → `![]`→false→0; `[]`→""→0; 0==0.
4. **Shallow vs deep + `structuredClone`?** → spread поверхневий; structuredClone deep (Date/Map/цикли).
5. **`sort()` пастка?** → лексикографічний + мутує; треба comparator + `[...arr]`.
6. **debounce vs throttle?** → після паузи vs не частіше N.
7. **nextTick vs setImmediate?** → nextTick найвищий пріоритет (перед microtasks); immediate — фаза check.
8. **Причини витоку пам'яті?** → listeners/timers/кеші/замикання → cleanup + WeakMap + моніторинг.

> ⚠️ Порядок timer/immediate і деталі GC — специфіка версії Node/V8; звіряй з docs.
