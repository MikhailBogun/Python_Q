# Вакансія: Python Live Video Streaming Engineer

Підготовка до співбесіди — аналіз вакансії та прогноз питань.

| Файл | Зміст |
|------|-------|
| [00_analysis_and_questions.md](00_analysis_and_questions.md) | Аналіз вакансії + перші 10 найімовірніших питань |
| [01_answers_q1_q5.md](01_answers_q1_q5.md) | Відповіді 1–5: Python/GIL, codecs, протоколи, GStreamer, I/P/B-кадри |
| [02_answers_q6_q10.md](02_answers_q6_q10.md) | Відповіді 6–10: troubleshooting, performance, WebRTC, плеєр, UDP/TCP |
| [03_python_questions.md](03_python_questions.md) | Прогноз 13 Python-питань під роль (🔗 є відповіді / 🆕 нові) |
| [04_python_answers_q1_q8.md](04_python_answers_q1_q8.md) | Python-відповіді 1–8: GIL, async, генератори, пам'ять, **memoryview**, **struct** |
| [05_python_answers_q9_q13.md](05_python_answers_q9_q13.md) | Python-відповіді 9–13: **ring buffer**, складність, **producer-consumer**, context managers, помилки |
| [06_deep_dive_udp.md](06_deep_dive_udp.md) | 🌊 **UDP deep-dive**: заголовок, механіка, RTP/SRT/WebRTC, MTU, multicast, сокети, тюнінг, troubleshooting |
| [07_deep_dive_gstreamer.md](07_deep_dive_gstreamer.md) | 🎬 **GStreamer deep-dive** (Strong Junior): концепції, елементи, Python (appsrc/appsink), caps, дебаг, архітектура сервісу |
| [08_deep_dive_codecs_containers.md](08_deep_dive_codecs_containers.md) | 🎞️ **Кодеки та контейнери deep-dive**: стиснення, H.264/265/AV1, MP4/TS/fMP4, remux vs transcode, мапінг протоколів |
| [09_deep_dive_asyncio.md](09_deep_dive_asyncio.md) | ⚡ **asyncio deep-dive**: event loop під капотом, корутини/Task/Future, не блокувати loop, патерни, відео-сервіс |
| [10_deep_dive_testing.md](10_deep_dive_testing.md) | 🧪 **Тестування deep-dive**: pytest, **mocking/patching**, fixtures, async-тести, що мокати (межі), best practices |
| [11_deep_dive_sqlalchemy.md](11_deep_dive_sqlalchemy.md) | 🗄️ **SQLAlchemy deep-dive**: Core+ORM (2.0), Session, relationships, **N+1/eager**, async, пули, Alembic |
| [12_role_overview_glossary_practices.md](12_role_overview_glossary_practices.md) | 🗺️ **Карта професії**: signal flow, що робитимеш день-за-днем, глосарій термінів, практики |
| [13_deep_dive_linux_docker.md](13_deep_dive_linux_docker.md) | 🐧 **Linux + Docker deep-dive**: процеси/логи/мережа, py-spy на живому процесі, відео-команди, дебаг контейнерів |

## Перші 10 питань (прогноз)
1. Python concurrency для стримінгу (GIL: threading/multiprocessing/asyncio)
2. Codec vs Container (H.264/H.265, MP4/TS/fMP4)
3. Протоколи стримінгу (RTMP/HLS/DASH/WebRTC, latency)
4. GStreamer pipeline (elements/pads/caps/bins)
5. I/P/B-кадри та GOP
6. ⭐ Troubleshooting-сценарій (24/7 production)
7. Performance optimization обробки кадрів
8. WebRTC (signaling/STUN/TURN/ICE/SDP)
9. Web player + MSE (hls.js/dash.js, ABR)
10. UDP vs TCP для live-відео (jitter, packet loss)

## Статус
- [x] Аналіз вакансії
- [x] Перші 10 питань (прогноз)
- [x] Повні відповіді за Принципом Сходів (усі 10)
- [ ] Додаткові питання (system design, event handlers, Linux/Docker, алгоритми)
- [ ] Mock-інтерв'ю
