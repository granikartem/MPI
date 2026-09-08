# План реализации — UC-1 и UC-7

Рабочий план реализации программной части. Без методологической обвязки — цель быстро получить работающий каркас и довести до рабочего состояния два прецедента: **UC-1 (Создать заявку)** и **UC-7 (Рассчитать risk_score)**. Эти два UC берёт на себя **Артём**. Остальные UC и их распределение — вне этого документа.

## 1. Решения

- Всё в Docker Compose: PostgreSQL 16, MongoDB 7, backend, frontend, mock внешних систем.
- Внешние интеграции (Wasteland Intel) — заглушка (WireMock), не реальный сервис.
- Обе БД поднимаем реально (Postgres — оперативные данные, Mongo — события/аудит).
- Стек по [SRS 3.5](SRS.md): Java 21 + Spring Boot, React 18 + Vite, без лишних абстракций.
- Сначала каркас (поднимается и пингует обе БД), затем на нём UC-1 и UC-7.

## 2. Стек

**Backend:** Spring Boot 3.x, Spring Web, Spring Data JPA (Postgres), Spring Data MongoDB, Flyway, Gradle, Java 21.
**Frontend:** Vite + React 18 + TypeScript, Axios. Без тяжёлой UI-обвязки на старте.
**Инфра:** docker-compose (postgres, mongo, backend, frontend, mock-intel через WireMock).

## 3. Структура репозитория

```
backend/    Spring Boot (Gradle), сборка внутри Docker
frontend/   Vite + React
docker-compose.yml
docs/       документация (этот файл здесь)
```

Backend по слоям внутри модулей: `web` (Controller/DTO) → `service` → `repository` → `domain`.

## 4. Каркас (делаем первым)

Минимум, который должен подняться и работать до фич:

- `docker-compose.yml`: postgres + mongo + backend + frontend + mock-intel.
- Backend стартует, Flyway применяет миграции, эндпоинт `GET /api/health` пингует Postgres и Mongo.
- Frontend поднимается, ходит на `/api/health` через proxy и показывает статус.

Когда это работает — каркас готов, дальше фичи.

## 5. UC-1 — Создать заявку на перевозку (Артём)

Полное описание потока — [CoreUseCases UC-1](CoreUseCases.md).

**Данные (Postgres):**
- `caravan_request` — заявка (origin, destination, departure_date, cargo_description, cargo_value_caps, route_id, eta, risk_score, recommendation, status, created_at).
- `route` / `route_segment` — маршрут (шаблон или ручной) и его участки.
- `checkpoint` — справочник точек (seed).

**Backend:**
- Создание заявки в статусе `Draft` (FR-1), выбор шаблона маршрута или ручной ввод (альт. 3а).
- Расчёт ETA (FR-5).
- Вызов расчёта risk_score (UC-7) и рекомендации (FR-8, FR-13).
- Fallback при недоступности Wasteland Intel (альт. 4а): заявка без risk_score, пометка «требует пересчёта».
- `POST /api/requests`, `GET /api/requests` (реестр).

**Frontend:**
- Форма создания заявки (макет: [mockups/caravan_dispatch.png](mockups/caravan_dispatch.png)).
- Реестр заявок со статусом и risk_score.

## 6. UC-7 — Рассчитать risk_score (Артём)

Полное описание — [CoreUseCases UC-7](CoreUseCases.md).

**Интеграция (mock):**
- WireMock-стаб Wasteland Intel: `GET /threats?segments=...` → угрозы по участкам + дата актуальности. Конфигурируется для сценариев: норма / устаревшие данные / недоступен.

**Backend:**
- Клиент Wasteland Intel с timeout/fallback.
- Расчёт: агрегация угроз → базовый risk_score → корректировка ценностью груза (FR-7, FR-14).
- Рекомендация по охране/припасам (FR-8).
- Состояния: успех / данные устарели (>24 ч) / источник недоступен (`risk_score = "Н/Д"`, флаг пересчёта).
- `POST /api/requests/{id}/risk-score`.

**Frontend:**
- Виджет risk_score в карточке заявки (макеты: [норма](mockups/risk_assessment_1.png), [ошибки](mockups/risk_assessment_2.png)).
- Три состояния виджета.

## 7. Порядок работ

1. Каркас (Docker + health) — общий, без него ничего не работает.
2. UC-7 (расчёт risk_score + mock Wasteland Intel) — нужен для UC-1.
3. UC-1 (создание заявки, использует UC-7).

## 8. Статус реализации

Реализовано и проверено end-to-end в Docker (`docker compose up -d --build`, фронт на :5173).

### Каркас
- PostgreSQL 16 + MongoDB 7 + backend + frontend + mock-intel в одном compose.
- `GET /api/health` пингует обе БД. Flyway применяет миграции (`V1__init`, `V2__seed_routes`).
- Фронт: лендинг на `/`, терминал диспетчера на `/requests`.

### UC-7 — risk_score
- Клиент Wasteland Intel (WireMock) с timeout/fallback.
- **Формула:** `score = min(100, base + cargoFactor)`, где `base = min(100, сумма_уровней_угроз × 6)`; коэффициент груза: `≥20000 → +30`, `≥5000 → +20`, `≥1000 → +10`, иначе `0`.
- Рекомендация по охране/припасам по диапазону score.
- Состояния: `OK` / `STALE` (данные >24 ч) / `NA` (источник недоступен).
- Снимок оценки сохраняется в MongoDB (коллекция `risk_assessment`) с разбивкой по участкам и слагаемыми расчёта.
- Виджет на фронте: клик по бейджу → модалка с derivation (угрозы по участкам → сумма → база → +груз → итог), кнопка «Удалить оценку».

### UC-1 — создание заявки
- Создание в статусе `DRAFT`, ETA = длина_маршрута / 4 км/ч (FR-5).
- Маршрут из шаблона **или ручной** (последовательность участков, альт. поток 3а).
- Автоматический вызов UC-7; при недоступности Intel заявка создаётся без risk_score (`NA`).
- Реестр заявок с индикацией статуса и risk_score.

### Известные пробелы
- **STALE** не демонстрируется: mock отдаёт фиксированный `asOf` (2287 → «вечно свежий»). Логика в коде есть.
- **Журнал аудита** (FR-35) для события создания заявки не реализован: UC-1 пишет стартовую запись
  в историю статусов, но отдельного audit-события `REQUEST_CREATED` в MongoDB нет.
- Статусная модель в объёме UC-1/UC-7 — только `DRAFT`. Полная статусная модель реализована
  отдельно в UC-2, см. [UC-2.md](UC-2.md); автоматические переходы из полевых событий — UC-16/UC-19.
- Реестр рейсов в объёме UC-1 — плоская таблица без срезов, сводки, фильтров и сортировки,
  серверный отбор только по организации. Срезы, сводка, фильтры и сортировка реализованы
  в UC-3, см. [UC-3.md](UC-3.md); поиск и фильтрация по архиву завершённых рейсов — UC-4.
- **Изоляция организаций (FR-24) в `GET /api/requests` не обеспечена:** без параметра
  `organizationId` эндпоинт UC-1 возвращает заявки всех организаций. Реестр UC-3
  (`GET /api/requests/registry`) организацию требует и без неё отвечает `400`; правка контракта
  UC-1 отложена до UC-25/UC-26, когда организация будет приходить из сессии, а не с клиента.

Эндпоинты — см. [README](../README.md).
