# Linux та Docker — deep-dive для відео-інженера (24/7 production)

> Що реально знадобиться на роботі. **Linux — більша частина** (з акцентом на операційку, troubleshooting і відео-специфіку), потім Docker.
> Базу (SSH, пакети, env) заклали в [answers/05](../answers/05_middle_architecture.md) п.63 та [answers/07](../answers/07_db_devops_ds.md) п.92 — тут фокус на **операційне використання під стрімінг**.

---

# ЧАСТИНА A — LINUX ⭐

## A0. Чому Linux критичний для цієї ролі
Відео-сервіси **живуть на Linux** (сервери, контейнери, студійне залізо). У 24/7 production, коли стрім падає о 3 ночі, ти **по SSH** заходиш на сервер і **командами** діагностуєш: процеси, логи, мережу, ресурси. Linux CLI — це твій **головний інструмент troubleshooting**. Тому «особливо Linux».

---

## A1. Процеси й сигнали (graceful shutdown стрімів) ⭐
```bash
ps aux | grep python              # знайти процес стрімінг-сервісу
ps aux | grep gst                 # GStreamer-процеси
htop                              # інтерактивний монітор (CPU/RAM/процеси)
top -p <PID>                      # стежити за конкретним процесом

# Сигнали — критично для коректної зупинки стріму
kill -TERM <PID>                  # SIGTERM (15) — ЧЕМНА зупинка (дай прибратись)
kill -KILL <PID>                  # SIGKILL (9) — ПРИМУСОВО (останній засіб)
kill -HUP <PID>                   # SIGHUP (1) — часто reload конфігу
```
**Чому це важливо для відео:** стрімінг-сервіс при зупинці має **коректно закрити** pipeline/сокети/з'єднання (graceful shutdown — зв'язок з GStreamer `set_state(NULL)` і asyncio cleanup). `SIGTERM` дає шанс прибратись; `SIGKILL` рве на місці (можливі биті дані/витоки). Тому в проді — `systemctl restart` (шле TERM, чекає, потім KILL), не `kill -9` навмання.

## A2. Логи — перше, куди дивишся при інциденті ⭐
```bash
# systemd-сервіси (більшість продакшн-сервісів)
journalctl -u stream-encoder -f          # стежити в реальному часі (-f = follow)
journalctl -u stream-encoder --since "10 min ago"   # за останні 10 хв
journalctl -u stream-encoder -p err      # лише помилки
journalctl -u stream-encoder -n 100      # останні 100 рядків

# Файлові логи
tail -f /var/log/app.log                 # стежити
tail -n 200 /var/log/app.log             # останні 200
grep -i error /var/log/app.log | tail    # помилки
grep "stream-42" /var/log/app.log        # за конкретним стрімом

# GStreamer debug (зв'язок з 07)
GST_DEBUG=3 ./encoder_service            # рівень логування pipeline
```
**Практика:** при інциденті **спершу логи** (`journalctl -f` під час відтворення проблеми) — часто причина прямо там (помилка pipeline, втрата з'єднання, OOM).

## A3. Мережа — серце відео-troubleshooting ⭐⭐
Найважливіша зона для стрімінгу (зв'язок з [UDP deep-dive 06](06_deep_dive_udp.md)):
```bash
# Які порти/сокети відкриті (UDP-стрімінг!)
ss -ulnp                          # UDP-сокети, що слухають (+ процес)
ss -tlnp                          # TCP-сокети
ss -u                             # активні UDP-з'єднання

# UDP-статистика — ДРОПИ через малий буфер (часта причина "втрат"!)
netstat -su | grep -i error       # "receive buffer errors" = ядро дропає пакети
cat /proc/net/udp                 # черги сокетів (Drops колонка)

# Тюнінг UDP-буфера (зв'язок з 06, розділ 13)
sysctl net.core.rmem_max          # макс. розмір приймального буфера
sysctl -w net.core.rmem_max=26214400   # підняти до 25MB (для high-bitrate)

# Захоплення RTP/UDP трафіку → Wireshark
tcpdump -i eth0 udp port 5004 -w capture.pcap    # записати
tcpdump -i any udp port 5004 -c 100              # 100 пакетів у консоль

# Якість шляху (packet loss, jitter, latency)
ping 10.0.0.5                     # базова доступність + RTT
mtr 10.0.0.5                      # traceroute + loss на кожному хопі (живий)

# Пропускна здатність у реальному часі
iftop -i eth0                     # хто скільки трафіку їсть
nload eth0                        # графік вхід/вихід

# Статистика інтерфейсу — ДРОПИ на рівні NIC
ip -s link show eth0              # RX/TX dropped/errors
ethtool -S eth0 | grep -i drop    # детальні дропи мережевої карти
ethtool -g eth0                   # розмір ring buffer NIC
```
**Це твій арсенал, коли «стрім сипле»:** `mtr` (втрати на шляху) → `netstat -su` (дропи буфера) → `ip -s link`/`ethtool` (дропи NIC) → `tcpdump` (захопити й глянути в Wireshark). Більшість «втрат» = малий UDP-буфер або повільне читання, **не мережа** (зв'язок з 06).

## A4. Ресурси системи (CPU/пам'ять/диск) ⭐
Енкодинг — CPU/пам'ять-важкий; 24/7 → витоки за дні:
```bash
top / htop                        # CPU, RAM, load average, процеси
free -h                           # пам'ять (used/free/available)
df -h                             # диск (заповнення — логи/записи можуть забити!)
du -sh /var/log/*                 # що займає місце
iostat -x 2                       # дискове I/O (для запису стрімів)
vmstat 2                          # система загалом (swap, io, cpu)
uptime                            # load average (1/5/15 хв)
```
**Load average vs ядра:** load average 8 на 4-ядерній машині = перевантаження (черга на CPU). Для енкодинг-сервісу стежиш, щоб CPU не впирався в 100% (→ dropped frames).

**Пам'ять для 24/7:** стежиш за `RSS` процесу в часі (`top`, `ps`) — **росте без причини = memory leak** (зв'язок з [Q5 GC/leaks](04_python_answers_q1_q8.md)). Диск: записи/логи можуть **забити диск** → сервіс падає.

## A5. Performance debugging живого процесу ⭐ (золото для прода)
Профілювати/діагностувати **без перезапуску** (прод не можна рестартити навмання):
```bash
# py-spy — профілювати ЖИВИЙ Python-процес (не змінюючи код!)
py-spy top --pid <PID>            # що зараз їсть CPU (live)
py-spy dump --pid <PID>           # стек усіх потоків зараз (де завис?)
py-spy record -o prof.svg --pid <PID> --duration 30   # flame graph

# strace — які системні виклики робить (завис на чому?)
strace -p <PID>                   # live syscalls
strace -p <PID> -e trace=network  # лише мережеві

# lsof — відкриті файли/сокети (ВИТІК дескрипторів!)
lsof -p <PID>                     # усе, що тримає процес
lsof -p <PID> | grep -c sock      # скільки сокетів (росте = витік)
lsof -i :5004                     # хто слухає порт

# perf — CPU-профілювання на рівні системи
perf top                          # гарячі функції зараз
```
**Чому критично:** «сервіс гальмує/завис у проді» → `py-spy dump` покаже, **де** саме застряг код (без рестарту); `lsof` покаже витік дескрипторів; `strace` — на якому syscall висить. Це відрізняє інженера, що **знаходить** причину, від того, хто «перезапускає й молиться».

## A6. Текст і пайпи — аналіз логів ⭐
Unix-філософія: маленькі інструменти через `|` (зв'язок з [answers/05](../answers/05_middle_architecture.md) п.63):
```bash
# Скільки помилок за останню годину
journalctl --since "1 hour ago" | grep -ci error

# Топ-10 IP за кількістю запитів у логу
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head

# Знайти всі дропи кадрів і порахувати
grep "dropped frame" app.log | wc -l

# Витягти латентність і подивитись хвіст
grep "latency=" app.log | grep -oP 'latency=\K[0-9]+' | sort -n | tail

# Стежити за логом і фільтрувати на льоту
tail -f app.log | grep --line-buffered ERROR
```
`grep` (пошук), `awk` (колонки/обчислення), `sed` (заміна), `sort`/`uniq` (групування), `wc` (підрахунок), `cut` (поля), `xargs` (передати далі). Це щоденний інструмент розслідування.

## A7. SSH + tmux (віддалені сервери, on-call) ⭐
```bash
# Підключення (зв'язок з answers/07 п.92)
ssh deploy@stream-server-1
ssh -i ~/.ssh/key.pem user@host

# ~/.ssh/config — зручні аліаси
# Host prod
#     HostName 10.0.0.5
#     User deploy
ssh prod                          # → коротко

# Копіювання
scp file.py prod:/app/            # один файл
rsync -avz ./dir/ prod:/app/      # синхронізація

# tmux — сесія, що ПЕРЕЖИВЕ розрив SSH (критично для on-call!)
tmux new -s debug                 # нова сесія
# Ctrl+b d — від'єднатись (процеси працюють далі)
tmux attach -t debug              # повернутись
# Запустив довгий tcpdump/моніторинг → tmux → закрив ноут → процес живий
```
**Чому tmux:** на чергуванні запускаєш довгий моніторинг/захоплення → розрив SSH **не вб'є** його. Без tmux — SSH впав, твій `tcpdump`/процес помер.

## A8. Відео/стрімінг-специфічний Linux ⭐
Те, чого нема в загальних гайдах, але знадобиться:
```bash
# Відео-пристрої захоплення (камери/карти)
ls /dev/video*                    # відеопристрої
v4l2-ctl --list-devices           # деталі (v4l-utils)
v4l2-ctl -d /dev/video0 --list-formats-ext   # підтримувані формати/роздільності

# HW-енкодинг (зв'язок з GStreamer 07)
nvidia-smi                        # GPU-завантаження (для NVENC) — у реальному часі
nvidia-smi dmon                   # моніторинг GPU
vainfo                            # можливості VAAPI (Intel HW-енкодинг)

# Multicast (студія/IPTV, зв'язок з 06)
ip maddr show                     # multicast-групи на інтерфейсах
netstat -ng                       # підписки на групи

# Перевірити, чи стрім реально йде по порту
tcpdump -i any udp port 5004 -c 5 -X    # 5 пакетів з hex-дампом
ffprobe udp://239.1.1.1:5004      # подивитись, що в UDP-стрімі (кодек/бітрейт)
```
**Сценарій:** «камера не дає сигнал» → `v4l2-ctl --list-devices` (чи бачить ОС пристрій?) → `ffprobe`/`tcpdump` (чи йдуть дані?). «HW-енкодер перевантажений» → `nvidia-smi` (GPU 100%?).

---

# ЧАСТИНА B — DOCKER

## B1. Що таке Docker і навіщо тут
**Аналогія — стандартний контейнер для перевезень.** Пакуєш сервіс із усіма залежностями (Python, GStreamer, бібліотеки) в **образ** → працює однаково всюди (твій ноут, staging, прод). «Works on my machine» зникає.

**Контейнер ≠ VM (зв'язок з [answers/07](../answers/07_db_devops_ds.md) п.90):** контейнер шарить ядро хоста, ізоляція через **namespaces + cgroups** Linux → легкий (мс старт, MB), на відміну від VM (повна ОС, секунди, GB).

## B2. Ключові концепції
| Термін | Простими словами |
|---|---|
| **Image (образ)** | шаблон-«знімок» (код + залежності + ОС-шар) |
| **Container** | запущений екземпляр образу |
| **Dockerfile** | рецепт побудови образу |
| **Registry** | сховище образів (Docker Hub, приватний) |
| **Layer (шар)** | образ = шари (кешуються при перебудові) |
| **Volume** | постійне сховище (поза контейнером) |

## B3. Dockerfile (приклад для Python-сервісу)
```dockerfile
FROM python:3.12-slim                    # базовий образ
WORKDIR /app
COPY pyproject.toml uv.lock ./           # спершу залежності (кеш шару!)
RUN pip install uv && uv sync --frozen
COPY . .                                 # потім код
CMD ["uv", "run", "python", "service.py"]
```
**Gotcha:** копіюй **залежності окремо й раніше** за код → Docker кешує шар залежностей, перебудова при зміні коду швидка (не переставляє все).

## B4. Команди, що використовуватимеш щодня ⭐
```bash
docker ps                         # запущені контейнери
docker ps -a                      # усі (включно зупинені)
docker logs <container> -f        # логи контейнера (стежити)
docker logs <container> --tail 100
docker exec -it <container> bash  # ЗАЙТИ ВСЕРЕДИНУ (дебаг!)
docker stats                      # CPU/RAM контейнерів у реальному часі
docker inspect <container>        # повна інфа (мережа, volumes, env)
docker build -t myservice:1.0 .   # зібрати образ
docker run -d --name enc myservice:1.0   # запустити (-d = фоном)
docker stop / start / restart <container>
docker rm <container>             # видалити
docker images                     # список образів
```
**`docker exec -it <c> bash`** — найважливіша для дебагу: **заходиш усередину** працюючого контейнера й діагностуєш тими ж Linux-командами (частина A!).

## B5. Дебаг контейнерів (для прода)
```bash
docker logs <c> -f                # що пише сервіс
docker exec -it <c> bash          # зайти й глянути зсередини
docker exec <c> ps aux            # процеси в контейнері
docker stats <c>                  # ресурси (CPU/RAM/мережа)
docker inspect <c> | grep -i ip   # IP контейнера
docker exec <c> ss -ulnp          # сокети в контейнері (UDP-стрім!)
```
Усередині контейнера — ті самі Linux-інструменти (A1-A8), якщо встановлені (slim-образи часто без них → інколи треба `apt install` для дебагу).

## B6. Docker для відео-специфіки ⭐
Стрімінг-контейнери мають нюанси:
```bash
# Прокинути відеопристрій (камеру) в контейнер
docker run --device=/dev/video0 myservice

# Прокинути GPU для HW-енкодингу (NVENC)
docker run --gpus all myservice           # NVIDIA Container Toolkit

# Мережа для UDP/multicast (host mode — без NAT)
docker run --network host myservice       # прямий доступ до мережі хоста
# (важливо для multicast і low-latency UDP — bridge-мережа додає overhead/проблеми)

# Прокинути порти (для unicast)
docker run -p 5004:5004/udp myservice     # UDP-порт!

# Ліміти ресурсів (cgroups)
docker run --cpus=2 --memory=2g myservice
```
**Чому `--network host` для стрімінгу:** дефолтна bridge-мережа NAT'ить трафік → проблеми з multicast, зайвий overhead, складність із UDP. `host` дає контейнеру прямий доступ до мережі хоста (ціна — менша ізоляція).

## B7. docker-compose (кілька сервісів)
```yaml
# docker-compose.yml
services:
  encoder:
    build: .
    network_mode: host
    devices: ["/dev/video0:/dev/video0"]
    restart: unless-stopped          # авто-рестарт при падінні
  db:
    image: postgres:16
    volumes: ["pgdata:/var/lib/postgresql/data"]
volumes:
  pgdata:
```
```bash
docker compose up -d              # підняти все
docker compose logs -f encoder    # логи сервісу
docker compose down               # зупинити
```

## B8. Best practices
- **Малі образи** — `slim`/`alpine` базові, multi-stage build (збірка окремо від рантайму).
- **Не root** — `USER appuser` (безпека).
- **`.dockerignore`** — не копіювати `.git`, `__pycache__`, `node_modules`.
- **Immutable** — той самий образ dev→staging→prod (конфіг через env).
- **`restart: unless-stopped`** — авто-відновлення в проді.
- **Healthcheck** — щоб оркестратор знав, чи сервіс живий.

---

# ЧАСТИНА C — реалістичний інцидент (Linux+Docker разом)

> «Стрім-сервіс у контейнері почав сипати артефактами»:
```bash
# 1. Контейнер живий? ресурси?
docker ps                                    # працює?
docker stats encoder                         # CPU 100%? RAM росте?

# 2. Логи — що каже сервіс?
docker logs encoder --tail 200 | grep -i -E "error|drop|warn"

# 3. Зайти всередину, глянути мережу (UDP-дропи?)
docker exec -it encoder bash
  netstat -su | grep -i error                # receive buffer errors?
  ss -ulnp                                    # сокет слухає?
  exit

# 4. Профілювати живий процес (CPU bottleneck?)
py-spy top --pid $(docker inspect -f '{{.State.Pid}}' encoder)

# 5. Мережа на хості (втрати на шляху?)
mtr 10.0.0.5                                  # loss до джерела?
ip -s link show eth0                          # дропи NIC?

# 6. GPU (якщо HW-енкодинг)
nvidia-smi                                    # GPU перевантажений?
```
**Методика (зв'язок з [Q6 troubleshooting](02_answers_q6_q10.md)):** контейнер → логи → мережа (дропи буфера/NIC/шляху) → процес (py-spy) → залізо (GPU). Шар за шаром, від простого до глибокого, **дані перед змінами**.

---

## ✅ Чеклист «Linux+Docker під роль»

**Linux (must):**
- [ ] Процеси/сигнали (SIGTERM vs SIGKILL, graceful shutdown).
- [ ] Логи (`journalctl -f`, `tail -f`, `grep`).
- [ ] Мережа (`ss`, `netstat -su`, `tcpdump`, `mtr`, `ip -s link`).
- [ ] Ресурси (`top/htop`, `free`, `df`, load average).
- [ ] **py-spy/lsof/strace на живому процесі** (дебаг без рестарту).
- [ ] Пайпи + grep/awk для логів.
- [ ] SSH + tmux (on-call).
- [ ] Відео-специфіка (`v4l2-ctl`, `nvidia-smi`, `ffprobe udp://`).

**Docker:**
- [ ] Образ vs контейнер vs Dockerfile; контейнер ≠ VM.
- [ ] `ps/logs/exec/stats/inspect` (особливо **`exec -it bash`**).
- [ ] Dockerfile (кеш шарів залежностей).
- [ ] Відео-специфіка (`--device`, `--gpus`, `--network host`, UDP-порти).
- [ ] docker-compose, restart-політики.

## 🔑 Головна думка
Linux для цієї ролі — це **інструмент troubleshooting у проді**. Коли стрім падає, ти по SSH діагностуєш командами: логи → мережа → ресурси → живий процес. Docker — як це все запаковано й запущено. Найцінніше: **дебаг живого процесу без рестарту** (`py-spy`, `lsof`, `strace`) + **мережева діагностика** (`netstat -su`, `tcpdump`, `mtr`) — саме це відрізняє інженера, що знаходить причину.

## 🔗 Зв'язки
- SSH/пакети/env база: [answers/07](../answers/07_db_devops_ds.md) п.92, [answers/05](../answers/05_middle_architecture.md) п.63.
- Docker/K8s концепції: [answers/07](../answers/07_db_devops_ds.md) п.90.
- UDP-буфери/tcpdump: [06_deep_dive_udp.md](06_deep_dive_udp.md).
- Troubleshooting-методологія: [02_answers_q6_q10.md](02_answers_q6_q10.md) Q6.
- Memory leaks (RSS у часі): [04_python_answers_q1_q8.md](04_python_answers_q1_q8.md) Q5.

> ⚠️ Деякі команди потребують пакетів (`v4l2-ctl` ← v4l-utils, `mtr`, `iftop`, `py-spy`, `nvidia-smi` ← драйвери) і прав (sudo). Поведінка/прапори різняться між дистрибутивами. Звіряй на цільовій системі.
