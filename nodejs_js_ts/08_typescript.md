# Блок 8. TypeScript — 20 питань з відповідями

> Формат — **Принцип Сходів**: L1 Junior → L2 Middle → L3 Senior.
> TypeScript 5+. Дотичне до JS-блоку (03) — тут фокус на системі типів.

---

## 1. Що таке TypeScript і навіщо?

### L1 — Junior
**Аналогія — етикетки на коробках.** TypeScript — це **JavaScript + типи**: ти підписуєш, що в кожній «коробці» (змінній, функції), і компілятор ловить помилки **до запуску**.

```typescript
function greet(name: string): string {   // приймає string, повертає string
  return `Привіт, ${name}`;
}
greet(42);   // ❌ помилка ще ДО запуску (number ≠ string)
```

### L2 — Middle
TypeScript — **типізована надбудова** над JavaScript, що **компілюється в JS** (браузер/Node виконують JS, не TS). Дає:
- Відлов помилок типів **на етапі компіляції** (не в рантаймі).
- Автодоповнення/рефакторинг в IDE.
- Самодокументований код (сигнатури).
- Безпечніший рефакторинг великих кодбаз.

### L3 — Senior
TS — **gradual typing**: типи **опціональні й поступові**, можна додавати в існуючий JS частинами. Ключове: типи **стираються при компіляції** (type erasure, питання 20) — у рантаймі їх немає, лишається чистий JS. Тому TS дає **статичну** безпеку (до запуску), а **не** рантайм-гарантії. Трейдоф: безпека/масштабованість великих проєктів + інструменти ↔ overhead написання типів + крок компіляції. Для команд/великих кодбаз — must; для дрібних скриптів — інколи зайве.

---

## 2. Базові типи

### L1 — Junior
```typescript
let s: string = "текст";
let n: number = 42;
let b: boolean = true;
let arr: number[] = [1, 2, 3];
let tuple: [string, number] = ["вік", 30];   // фіксована структура
let nothing: null = null;
let u: undefined = undefined;
```

### L2 — Middle
```typescript
let anything: any;            // вимикає перевірку (уникати!)
let safe: unknown;            // типобезпечний any (питання 5)
let arr2: Array<number>;      // = number[]
let obj: { name: string; age: number };   // об'єкт
let fn: (x: number) => string;            // функція
let optional: string | undefined;         // union
let union: string | number;               // або те, або те
function fail(): never { throw new Error(); }  // ніколи не повертає
```

### L3 — Senior
- **`object`** vs `{}` vs `Object` — нюанси: `{}` — майже будь-що (крім null/undefined), `object` — не примітив, `Object` — обгортка (уникати).
- **`void`** — функція без значущого повернення (≠ undefined, питання у JS-блоці п.30).
- **`bigint`, `symbol`** — повні примітивні типи.
- TS розрізняє `null` і `undefined` (зі `strictNullChecks`, питання 14) — `string` **не** включає null, треба `string | null` явно. Це прибирає цілий клас «cannot read property of null».

---

## 3. `interface` vs `type` ⭐

### L1 — Junior
Обидва описують **форму об'єкта**:
```typescript
interface User { name: string; age: number; }
type User2 = { name: string; age: number; };
```
Для об'єктів майже взаємозамінні. Різниця — у можливостях.

### L2 — Middle
| | `interface` | `type` |
|---|---|---|
| Об'єкти | ✅ | ✅ |
| Union/intersection | ❌ | ✅ (`A \| B`, `A & B`) |
| Примітиви/tuple | ❌ | ✅ (`type ID = string`) |
| Declaration merging | ✅ (можна «доповнити») | ❌ |
| Extends | `extends` | `&` (intersection) |

```typescript
type ID = string | number;          // лише type (union)
interface Animal { name: string; }
interface Animal { age: number; }   // МЕРЖИТЬСЯ → Animal має name + age
```

### L3 — Senior
**Коли що (конвенція):**
- **`interface`** — для **об'єктів і публічних API** (класи, бібліотеки): підтримує declaration merging (розширення сторонніх типів), кращі повідомлення про помилки, `implements` у класах.
- **`type`** — для **union, intersection, tuple, примітивів, складних/обчислюваних** типів (mapped/conditional, питання 18).

**Declaration merging** — потужно для augmentation (доповнити типи бібліотеки, напр. `Express.Request` додати `user`). Трейдоф: interface гнучкіший для розширення, type — для composition. Багато styleguide: interface за замовчуванням для об'єктів, type — де interface не може.

---

## 4. Union та Intersection типи ⭐

### L1 — Junior
- **Union (`|`)** — «**або** те, **або** те»: `string | number`.
- **Intersection (`&`)** — «**і** те, **і** те разом»: об'єднати поля.

```typescript
type Status = "active" | "inactive";   // union (лише ці значення)
type Admin = User & { role: string };  // intersection (User + role)
```

### L2 — Middle
```typescript
function format(value: string | number): string {
  // треба ЗВУЗИТИ тип перед використанням (питання 7)
  if (typeof value === "string") return value.toUpperCase();
  return value.toFixed(2);   // тут TS знає, що number
}

type A = { a: number };
type B = { b: number };
type AB = A & B;             // { a: number; b: number } — має ОБА
```

### L3 — Senior
**Union — основа моделювання станів:** замість «boolean + nullable» — точний union (`"loading" | "success" | "error"`). У поєднанні з **discriminated unions** (питання 19) дає exhaustive-перевірку. **Intersection** — для композиції (mixins, розширення). 

**Gotcha:** intersection примітивів дає `never` (`string & number` — неможливо). Union робить тип **ширшим** (більше варіантів), intersection — **вужчим** (більше обмежень). Це двоїстість: `|` розширює множину значень, `&` звужує.

---

## 5. `any` vs `unknown` vs `never` ⭐

### L1 — Junior
- **`any`** — «будь-що, не перевіряй» (вимикає типи — **уникати**).
- **`unknown`** — «не знаю тип, але **безпечно**» (треба звузити перед використанням).
- **`never`** — «**ніколи** не буває значення» (функція кидає/не повертає).

### L2 — Middle
```typescript
let a: any = 5;
a.foo.bar;              // ✅ компілюється (небезпечно! — впаде в рантаймі)

let u: unknown = 5;
u.foo;                  // ❌ помилка — треба спершу звузити
if (typeof u === "object" && u !== null) { /* тепер можна */ }

function fail(): never { throw new Error(); }   // ніколи не повертає
```

### L3 — Senior
| | any | unknown | never |
|---|---|---|---|
| Безпека | ❌ (вимикає перевірку) | ✅ (треба звузити) | — (порожній тип) |
| Присвоїти йому | будь-що | будь-що | нічого (крім never) |
| Присвоїти з нього | будь-куди | лише після звуження | будь-куди |

- **`any`** — escape hatch, «отрута»: поширюється (any.x = any) і вимикає перевірку всюди, куди тече. Використовуй мінімально (інтеграція з нетипізованим JS).
- **`unknown`** — type-safe заміна any: приймає будь-що, але **змушує звузити** перед використанням → безпека. Для зовнішніх даних (JSON.parse, API) — `unknown`, не `any`.
- **`never`** — для exhaustiveness checking (питання 19), функцій що кидають/зациклюються, неможливих гілок. `never` — підтип усіх типів (порожня множина значень).

---

## 6. Generics (узагальнення) ⭐

### L1 — Junior
**Generics** — типи-«параметри»: функція/клас працює з **будь-яким** типом, зберігаючи його.
```typescript
function identity<T>(x: T): T {   // T — «змінна типу»
  return x;
}
identity<string>("hi");   // T = string
identity(42);             // T = number (виведено)
```

### L2 — Middle
```typescript
// Generic-функція з обмеженням
function first<T>(arr: T[]): T | undefined {
  return arr[0];
}

// Constraint — T має мати .length
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}

// Generic-інтерфейс/клас
interface Box<T> { value: T; }
class Stack<T> {
  private items: T[] = [];
  push(item: T): void { this.items.push(item); }
  pop(): T | undefined { return this.items.pop(); }
}
```

### L3 — Senior
Generics дають **переиспользування без втрати типобезпеки** (на відміну від `any`, що губить тип). `Array<T>`, `Promise<T>`, `Map<K,V>` — усі generic. **Constraints (`extends`)** обмежують, що можна передати. **Defaults** (`<T = string>`). **Multiple params** (`<K, V>`).

**Трейдоф:** потужність і переиспользування ↔ складність (вкладені generics стають нечитабельними). Generics — основа utility types (питання 11), mapped/conditional types (питання 18). Senior використовує для бібліотек/переиспользуваних абстракцій, не ускладнює прості випадки.

---

## 7. Type narrowing та type guards ⭐

### L1 — Junior
**Звуження (narrowing)** — TS «розуміє» точніший тип усередині `if`. **Type guard** — перевірка, що звужує union.
```typescript
function f(x: string | number) {
  if (typeof x === "string") {
    x.toUpperCase();   // TS знає: тут x — string
  }
}
```

### L2 — Middle
**Способи звуження:**
```typescript
typeof x === "string"           // примітиви
x instanceof Date               // класи
"prop" in obj                   // наявність властивості
x === null / x !== undefined    // null-перевірки
Array.isArray(x)                // масиви

// Custom type guard (predicate "x is Type")
function isUser(x: unknown): x is User {
  return typeof x === "object" && x !== null && "name" in x;
}
if (isUser(data)) { data.name; }   // TS знає: data — User
```

### L3 — Senior
**Control flow analysis** — TS відстежує тип по гілках виконання (звужує після `if/return/throw`). **Custom type guards** (`x is Type`) — для складних перевірок (валідація зовнішніх даних). **Discriminated unions** (питання 19) — найпотужніше звуження через спільне «тег»-поле.

**Gotcha:** type guard `x is Type` — це **обіцянка** компілятору, не рантайм-гарантія: якщо предикат збрехав, TS повірить (як `as`). Тому пиши guard коректно. Для надійної рантайм-валідації зовнішніх даних — **zod** (питання 20).

---

## 8. Enums (і альтернативи) ⭐

### L1 — Junior
**Enum** — набір іменованих констант.
```typescript
enum Status { Active, Inactive, Banned }   // 0, 1, 2 (numeric)
enum Color { Red = "RED", Green = "GREEN" } // string enum
let s: Status = Status.Active;
```

### L2 — Middle
```typescript
// Numeric (за замовч.) — reverse mapping (Status[0] === "Active")
enum Status { Active, Inactive }

// String enum — читабельніше в логах/БД
enum Role { Admin = "admin", User = "user" }

// const enum — інлайниться (без рантайм-об'єкта)
const enum Direction { Up, Down }

// ✅ Альтернатива (часто краще) — union of literals + as const
const Status2 = { Active: "active", Inactive: "inactive" } as const;
type Status2 = typeof Status2[keyof typeof Status2];  // "active" | "inactive"
```

### L3 — Senior
**Enum — суперечлива фіча:** numeric enum створює **рантайм-об'єкт** (не tree-shakeable), має дивну поведінку (reverse mapping, можна присвоїти будь-яке число). **Багато команд уникають enum** на користь:
- **Union of string literals** (`type Status = "active" | "inactive"`) — нуль рантайм-коду, простіше.
- **`as const` об'єкт** — коли потрібні і значення, і тип.

**Трейдоф:** enum зручний синтаксично й групує константи ↔ рантайм-вага, не tree-shakeable, нюанси numeric. `const enum` інлайниться (нуль рантайму), але має проблеми з ізольованою компіляцією. Senior часто обирає **union літералів** як простіше й легше. Це часте питання «чому уникати enum».

---

## 9. `readonly`, `optional`, модифікатори

### L1 — Junior
```typescript
interface User {
  readonly id: number;     // не можна змінити після створення
  name: string;
  email?: string;          // опціональне (може бути undefined)
}
```

### L2 — Middle
```typescript
const arr: readonly number[] = [1, 2, 3];
arr.push(4);               // ❌ readonly

interface Config {
  readonly apiKey: string;
  timeout?: number;        // ?: означає `number | undefined`
}

// Параметри
function f(required: string, optional?: number, withDefault = 10) {}
```

### L3 — Senior
- **`readonly`** — лише **compile-time** (стирається в рантаймі, як `const` для прив'язки vs `Object.freeze` для значення). Запобігає випадковій мутації на рівні типів.
- **`?` (optional)** — додає `| undefined` до типу; зі `strictNullChecks` треба перевіряти.
- **`Readonly<T>`** (utility, питання 11) — зробити всі поля readonly.
- **`as const`** — глибокий readonly + literal-звуження (питання 13).

**Gotcha:** `readonly` не глибокий (`readonly obj` не робить вкладені поля readonly). І це лише типи — у рантаймі мутацію не зупинить (на відміну від `Object.freeze`).

---

## 10. Type assertions (`as`) — і чому небезпечно ⭐

### L1 — Junior
**`as`** каже компілятору «**довірся мені**, це тип X» — обходить перевірку.
```typescript
const el = document.getElementById("app") as HTMLInputElement;
const data = JSON.parse(raw) as User;
```

### L2 — Middle
```typescript
let x: unknown = "hello";
let len = (x as string).length;   // стверджуємо, що string

// Небезпечно — TS повірить, навіть якщо брехня:
const user = {} as User;          // ❌ порожній об'єкт «вдає» User
user.name.toUpperCase();          // компілюється, але впаде в рантаймі!
```

### L3 — Senior
**`as` — НЕ перетворення, а обіцянка компілятору** (нуль рантайм-перевірки). Якщо збрехав — TS повірить, помилка спливе в рантаймі (TS втрачає сенс). Тому:
- **Уникай `as`** де можна — використовуй narrowing/type guards (питання 7) для безпечного звуження.
- `as` доречний: DOM (`as HTMLInputElement`), звуження `unknown` після перевірки, інтеграція з нетипізованим.
- **`as const`** — інше: не assertion типу, а **звуження до літералів** (питання 13).
- **`as any`/подвійне `as unknown as X`** — найгірше (обхід усіх перевірок).

**Для зовнішніх даних** (JSON, API) `as User` **бреше** про валідність → використовуй рантайм-валідацію (**zod**), яка і перевіряє, і дає тип. `as` — остання інстанція, коли знаєш краще за компілятор.

---

## 11. Utility types ⭐

### L1 — Junior
Вбудовані «трансформери» типів:
```typescript
Partial<User>     // усі поля опціональні
Required<User>    // усі обов'язкові
Readonly<User>    // усі readonly
Pick<User, "id">  // лише обрані поля
Omit<User, "id">  // усі КРІМ обраних
```

### L2 — Middle
```typescript
interface User { id: number; name: string; email: string; }

type UserUpdate = Partial<User>;          // { id?, name?, email? }
type UserPreview = Pick<User, "id" | "name">;   // { id, name }
type UserNoId = Omit<User, "id">;         // { name, email }
type Users = Record<string, User>;        // { [key: string]: User }

// З функцій
type Fn = (x: number) => string;
type R = ReturnType<Fn>;                  // string
type P = Parameters<Fn>;                  // [number]
type A = Awaited<Promise<User>>;          // User (розгортає Promise)
```

### L3 — Senior
**Найкорисніші:** `Partial`, `Required`, `Readonly`, `Pick`, `Omit`, `Record`, `ReturnType`, `Parameters`, `Awaited`, `NonNullable`, `Exclude`, `Extract`, `ReturnType`.

Це **mapped/conditional types** (питання 18) у stdlib. Дозволяють **похідні** типи без дублювання: `UserUpdate = Partial<User>` автоматично оновлюється при зміні `User` (DRY для типів). Senior комбінує: `Omit<User, "id"> & { id?: string }`, власні utility через mapped types. Розуміння, що Pick/Omit/Partial — це **обчислення над типами**, відкриває метапрограмування типів.

---

## 12. Function overloads (перевантаження)

### L1 — Junior
Кілька сигнатур для однієї функції (різні входи → різні виходи):
```typescript
function parse(x: string): string[];
function parse(x: number): number[];
function parse(x: any): any[] {           // реалізація
  return typeof x === "string" ? x.split("") : [x];
}
```

### L2 — Middle
```typescript
function getValue(key: "name"): string;
function getValue(key: "age"): number;
function getValue(key: string): string | number {
  // одна реалізація, кілька публічних сигнатур
  return key === "age" ? 30 : "Іван";
}
const name = getValue("name");   // тип: string (точно!)
const age = getValue("age");     // тип: number
```

### L3 — Senior
Overloads дають **точніший** тип повернення залежно від входу, ніж union. Але часто **generics або conditional types кращі** (менше дублювання). 

**Трейдоф:** overloads читабельні для дискретних випадків ↔ дублювання сигнатур, реалізація має покривати всі (тип реалізації не видно ззовні). Сучасний підхід — `function f<T>(x: T): Result<T>` через conditional types замість багатьох overload. Overloads лишаються для API, де входи дискретні й непов'язані.

---

## 13. Literal types та `as const` ⭐

### L1 — Junior
**Literal type** — конкретне значення як тип:
```typescript
let dir: "up" | "down";     // лише ці два рядки
dir = "left";               // ❌ помилка
```

### L2 — Middle
```typescript
// Без as const — тип розширюється до загального
const config = { mode: "dark" };        // mode: string (розширено!)
config.mode = "anything";               // ✅ (не те, що хотіли)

// З as const — звужується до літералів + readonly
const config2 = { mode: "dark" } as const;   // mode: "dark" (literal, readonly)
config2.mode = "light";                 // ❌ readonly + не "dark"

const arr = [1, 2, 3] as const;         // readonly [1, 2, 3] (tuple)
```

### L3 — Senior
**`as const` (const assertion)** — потужний інструмент:
- Звужує до **найвужчого** літерального типу (`"dark"`, не `string`).
- Робить **глибоко readonly** (об'єкти, масиви → tuple).
- Дозволяє **виводити union** з об'єкта (`typeof obj[keyof typeof obj]` — питання 8, альтернатива enum).

**Чому важливо:** TS за замовчуванням **розширює** літерали (`const x = "a"` → тип `"a"`, але `let x = "a"` → `string`; в об'єктах — завжди розширює). `as const` зберігає точність. Основа типобезпечних конфігів, заміни enum, discriminated unions. Senior використовує для constant-об'єктів, route-конфігів, redux actions.

---

## 14. tsconfig та strict mode ⭐

### L1 — Junior
**`tsconfig.json`** — налаштування компілятора TS. **`strict: true`** — вмикає всі суворі перевірки (рекомендовано).
```json
{ "compilerOptions": { "strict": true, "target": "ES2022" } }
```

### L2 — Middle
```json
{
  "compilerOptions": {
    "strict": true,                    // усі суворі перевірки
    "target": "ES2022",                // в яку версію JS компілювати
    "module": "ESNext",                // система модулів
    "moduleResolution": "bundler",
    "outDir": "./dist",
    "esModuleInterop": true,           // сумісність CJS/ESM
    "skipLibCheck": true,
    "noUncheckedIndexedAccess": true   // arr[i] → T | undefined (безпечніше)
  }
}
```
**`strict` вмикає:** `strictNullChecks`, `noImplicitAny`, `strictFunctionTypes`, `strictBindCallApply`, `alwaysStrict` та ін.

### L3 — Senior
**`strictNullChecks`** — найважливіше: `null`/`undefined` **не** входять у типи автоматично → треба обробляти явно → прибирає «cannot read property of null» (мільярдна помилка). **`noImplicitAny`** — забороняє неявний any. 

**Додаткові суворі прапори (senior):** `noUncheckedIndexedAccess` (`arr[i]` стає `T | undefined` — ловить out-of-bounds), `exactOptionalPropertyTypes`, `noImplicitReturns`, `noFallthroughCasesInSwitch`. **`target`/`module`** — у що компілювати. **Завжди вмикай `strict`** у новому коді — без нього TS втрачає половину користі (тихо допускає any/null). Поступова міграція legacy: вмикати прапори по одному.

---

## 15. Structural typing (структурна типізація) ⭐

### L1 — Junior
TS порівнює типи **за формою (структурою)**, а не за іменем («duck typing»): якщо об'єкт має потрібні поля — він підходить.
```typescript
interface Point { x: number; y: number; }
const p = { x: 1, y: 2, z: 3 };   // має x, y (+ зайве z)
const pt: Point = p;              // ✅ підходить за структурою
```

### L2 — Middle
```typescript
interface Named { name: string; }
class Dog { constructor(public name: string) {} }
const n: Named = new Dog("Рекс");   // ✅ Dog має name → сумісний з Named
                                     // (не треба implements Named)
```
На відміну від **nominal** типізації (Java/C#), де потрібне явне успадкування/реалізація.

### L3 — Senior
**Структурна типізація = типи сумісні за формою, не за іменем** (статичний duck typing — паралель з Python `Protocol`). Плюс: гнучкість, менше бойлерплейту (не треба `implements`), легка інтеграція. Мінус: **випадкова сумісність** (два різні концепти з однаковою формою вважаються однаковими).

**Excess property checks** — TS усе ж лає на **літерали** із зайвими полями (`const p: Point = { x, y, z }` — помилка), але не на змінні (приклад L1). **Branded/nominal types** — трюк для штучної номінальності (`type UserId = string & { __brand: "UserId" }`), коли структурної замало (не сплутати UserId з OrderId). Senior знає, коли структурної достатньо, а коли потрібен branding.

---

## 16. Type inference (виведення типів)

### L1 — Junior
TS **сам виводить** типи, де може — не завжди треба писати явно.
```typescript
let x = 42;              // TS виводить number (не треба : number)
const arr = [1, 2, 3];   // number[]
function double(n: number) { return n * 2; }   // повернення виведено: number
```

### L2 — Middle
```typescript
// Виводиться з ініціалізації, повернення, контексту
const user = { name: "Іван", age: 30 };   // { name: string; age: number }
const doubled = [1, 2].map(n => n * 2);   // number[] (n виведено як number)

// Best common type
const mixed = [1, "two"];                  // (string | number)[]
```
**Best practice:** не дублюй очевидне (`const x: number = 42` — зайве `: number`). Пиши типи на **межах** (параметри функцій, публічні API, складні структури), решту — виводь.

### L3 — Senior
**Contextual typing** — TS виводить тип з контексту: `arr.map(n => ...)` знає, що `n` — елемент масиву; `button.onclick = (e) => ...` знає, що `e` — MouseEvent. **Return type inference** — зазвичай не пишуть явно (виводиться), але для **публічного API** інколи пишуть явно (стабільність контракту, кращі помилки).

**Трейдоф inference vs явні типи:** менше коду + DRY (тип оновлюється з реалізацією) ↔ явні типи документують намір і ловлять помилки на межі (якщо реалізація поверне не те, явний тип повернення це впіймає). Senior: виводити локальне, явно типізувати **межі** (параметри, експортовані функції) — це і документація, і захист контракту.

---

## 17. `keyof`, `typeof`, indexed access ⭐

### L1 — Junior
- **`keyof T`** — union ключів типу.
- **`typeof x`** — тип значення.
- **`T[K]`** — тип властивості за ключем.
```typescript
interface User { id: number; name: string; }
type Keys = keyof User;        // "id" | "name"
type IdType = User["id"];      // number
```

### L2 — Middle
```typescript
const config = { host: "localhost", port: 5432 };
type Config = typeof config;          // { host: string; port: number }
type ConfigKey = keyof typeof config; // "host" | "port"

// Типобезпечний доступ за ключем (generic)
function getProp<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
getProp(user, "name");   // тип: string (точно!)
```

### L3 — Senior
Ці оператори — **міст між значеннями й типами** (типи з рантайм-структур):
- **`typeof`** — взяти тип з реального значення (конфіг, константа) → не дублювати.
- **`keyof`** — отримати ключі → типобезпечні «get property», ітерація.
- **`T[K]` (indexed access)** — витягти тип частини.

Разом — основа **mapped types** (питання 18) і type-safe API: `getProp<T, K extends keyof T>(o: T, k: K): T[K]` гарантує, що ключ існує й тип повернення точний. Senior комбінує `typeof obj[keyof typeof obj]` для виведення union значень (альтернатива enum, питання 8).

---

## 18. Mapped та Conditional types ⭐

### L1 — Junior
- **Mapped type** — «пройтись по ключах» і трансформувати: `{ [K in keyof T]: ... }`.
- **Conditional type** — «якщо тип X, то A, інакше B»: `T extends U ? X : Y`.

### L2 — Middle
```typescript
// Mapped — зробити всі поля опціональними (так працює Partial!)
type MyPartial<T> = { [K in keyof T]?: T[K] };

// Mapped з модифікаторами
type ReadonlyT<T> = { readonly [K in keyof T]: T[K] };

// Conditional
type IsString<T> = T extends string ? "yes" : "no";
type A = IsString<string>;   // "yes"
type B = IsString<number>;   // "no"

// Conditional + infer (витягти тип)
type ElementType<T> = T extends (infer U)[] ? U : never;
type E = ElementType<number[]>;   // number
```

### L3 — Senior
Це **метапрограмування типів** — обчислення над типами. Utility types (питання 11) реалізовані саме так (`Partial`, `Pick`, `ReturnType`). 
- **Mapped types** — трансформація форми (зробити readonly/optional, перейменувати ключі через `as`, фільтрувати).
- **Conditional types** — розгалуження + **`infer`** (витягти тип-частину: елемент масиву, аргумент Promise, повернення функції).
- **Distributive conditional** — union розподіляється: `T extends U ? ...` для `A | B` дає `(A extends U ?...) | (B extends U ?...)`.

**Трейдоф:** надзвичайна потужність (типобезпечні бібліотеки, точні типи) ↔ складність (вкладені mapped/conditional стають нечитабельними «type gymnastics»). Senior використовує для **бібліотек/переиспользуваних абстракцій**, не ускладнює прикладний код. Розуміння `infer` + distributive — рівень, що відрізняє senior TS.

---

## 19. Discriminated unions ⭐

### L1 — Junior
Union об'єктів зі спільним **«тег»-полем**, за яким TS точно звужує:
```typescript
type Shape =
  | { kind: "circle"; radius: number }
  | { kind: "square"; side: number };

function area(s: Shape): number {
  if (s.kind === "circle") return Math.PI * s.radius ** 2;  // TS знає: circle
  return s.side ** 2;                                        // square
}
```

### L2 — Middle
```typescript
// Класичний приклад — стани (loading/success/error)
type State =
  | { status: "loading" }
  | { status: "success"; data: User }
  | { status: "error"; error: string };

function render(state: State) {
  switch (state.status) {
    case "loading": return "Завантаження...";
    case "success": return state.data.name;    // data доступне лише тут
    case "error": return state.error;          // error лише тут
  }
}
```

### L3 — Senior
**Discriminated (tagged) union** — найпотужніший патерн моделювання станів у TS. **Exhaustiveness checking** через `never`:
```typescript
function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return ...;
    case "square": return ...;
    default:
      const _exhaustive: never = s;   // ❌ якщо додали новий kind і забули — помилка!
      return _exhaustive;
  }
}
```
Якщо додаси новий варіант у union і забудеш обробити — `never`-присвоєння **зламає компіляцію** (compile-time гарантія повноти). Це робить unions **безпечнішими за enum + if**. Замінює багато OOP-поліморфізму типобезпечно. Senior моделює домен через discriminated unions + exhaustive switch — улюблений патерн функціонального TS.

---

## 20. Type erasure — як TS працює в рантаймі ⭐

### L1 — Junior
**Типи зникають при компіляції.** TS компілюється в JS, **типи стираються** — у рантаймі їх **немає**. Браузер/Node виконують чистий JS.
```typescript
// TS:
function greet(name: string): string { return `Hi ${name}`; }
// Скомпільований JS (типи зникли):
function greet(name) { return `Hi ${name}`; }
```

### L2 — Middle
**Наслідок — типи не перевіряються в рантаймі:**
```typescript
function process(user: User) {
  // user.name — TS вірить, що є, але в РАНТАЙМІ може не бути
  // (якщо дані прийшли ззовні неперевірені)
}
const data = JSON.parse(raw) as User;   // ❌ as БРЕШЕ — рантайм-перевірки немає
```
Не можна `if (x instanceof MyInterface)` — інтерфейсів у рантаймі немає (лише класи).

### L3 — Senior
**Type erasure — фундаментальна властивість:** TS дає **статичні** (compile-time) гарантії, **не рантайм**. Для **зовнішніх даних** (API, JSON, форми, БД) типи TS **нічого не гарантують** — потрібна **рантайм-валідація**:
```typescript
import { z } from "zod";
const UserSchema = z.object({ name: z.string(), age: z.number() });
const user = UserSchema.parse(jsonData);   // ✅ перевіряє в РАНТАЙМІ + дає тип
type User = z.infer<typeof UserSchema>;    // тип ВИВОДИТЬСЯ зі схеми
```
**zod/io-ts/valibot** — валідують у рантаймі **і** генерують TS-тип (single source of truth). Це закриває розрив між compile-time типами й рантайм-реальністю.

**Senior-висновок:** TS-типи — для **свого** коду (compile-time безпека), на **межах системи** (API, файли, user input) — рантайм-валідація (zod). Плутати їх («`as User` гарантує валідність») — класична помилка. Type erasure = чому TS не сповільнює рантайм (нуль overhead), але й не захищає від брудних зовнішніх даних.

---

## ✅ Чеклист TypeScript (інтерв'ю)

**Базово:** типи, interface vs type, union/intersection, generics, optional/readonly.
**Середній:** any/unknown/never, narrowing/type guards, utility types, enums (+ чому уникати), literal/as const, tsconfig strict.
**Senior:** structural typing (+ branding), keyof/typeof/indexed, mapped/conditional types + infer, discriminated unions + exhaustiveness, **type erasure + рантайм-валідація (zod)**.

## 🔑 Топ-питання
1. **interface vs type?** → type для union/primitives, interface для об'єктів + merging.
2. **any vs unknown?** → any вимикає перевірку; unknown безпечний (треба звузити).
3. **Чому уникати enum?** → рантайм-вага, не tree-shakeable → union літералів.
4. **Чому `as` небезпечний?** → обіцянка без рантайм-перевірки → bug.
5. **Типи в рантаймі?** → стираються; для зовнішніх даних → zod.
6. **Discriminated union + exhaustiveness?** → tag-поле + `never` для повноти.

> ⚠️ TS швидко розвивається (нові utility types, satisfies-оператор, const type params). Звіряй з docs версії. `satisfies` (5.0+) — варто додати в арсенал (перевіряє відповідність без розширення типу).
