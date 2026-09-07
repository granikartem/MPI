# ИС «Караваны»

Информационная система управления караванными перевозками в сеттинге Fallout: New Vegas. Учебный проект в рамках дисциплины МПИ.

## Структура репозитория

```
docs/             — проектная документация (Vision, SRS, SDP, UseCases, BusinessCase, RiskList, Glossary)
  diagrams/       — диаграммы (PlantUML-исходники + отрендеренные PNG)
  mockups/        — HTML-макеты и скриншоты интерфейсов
  scripts/        — служебные скрипты (рендер диаграмм и графиков)
  tools/          — внешние инструменты (plantuml.jar)
backend/          — серверная часть (Java 21, Spring Boot, PostgreSQL + MongoDB)
frontend/         — веб-клиент (React 18 + Vite + TypeScript)
mock-integrations/— WireMock-заглушка внешней системы Wasteland Intel
docker-compose.yml
```

Подробный план реализации и статус — [docs/ImplementationPlan.md](docs/ImplementationPlan.md).

## Запуск

Требуется Docker + Docker Compose. Поднимает всё (PostgreSQL 16, MongoDB 7, backend, frontend, mock Wasteland Intel):

```bash
docker compose up -d --build
```

Затем открыть **http://localhost:5173**:
- «Открыть терминал диспетчера» — UC-1/UC-2/UC-7.
- «Открыть консоль организаций» — UC-32.

| Сервис | Порт | Назначение |
|--------|------|-----------|
| frontend | 5173 | веб-клиент диспетчера |
| backend | 8080 | REST API |
| postgres | 5432 | оперативные данные (заявки, маршруты, организации, пользователи) |
| mongo | 27017 | снимки оценки риска, audit-события |
| mock-intel | 8089 | заглушка Wasteland Intel (`GET /threats`) |

### Реализовано

Прецеденты **UC-1 (создание заявки)** и **UC-7 (расчёт risk_score)** — см. [docs/ImplementationPlan.md](docs/ImplementationPlan.md).
Прецедент **UC-32 (создать организацию)** — см. [docs/UC-32.md](docs/UC-32.md).
Прецедент **UC-2 (управлять статусами заявки)** — см. [docs/UC-2.md](docs/UC-2.md).

Ключевые эндпоинты:

| Метод | Путь | Назначение |
|-------|------|-----------|
| GET | `/api/health` | доступность PostgreSQL и MongoDB |
| GET | `/api/routes` | шаблоны маршрутов |
| GET | `/api/checkpoints` | контрольные точки (для ручного маршрута) |
| GET/POST | `/api/requests` | реестр / создание заявки (шаблон или ручной маршрут) |
| POST | `/api/requests/{id}/risk-score` | пересчитать risk_score |
| GET | `/api/requests/{id}/risk` | снимок оценки риска с разбивкой по участкам |
| DELETE | `/api/requests/{id}/risk` | сбросить оценку риска |
| GET | `/api/requests/{id}/status` | текущий статус заявки и доступные переходы (UC-2) |
| POST | `/api/requests/{id}/status` | перевод заявки в новый статус (UC-2) |
| GET | `/api/requests/{id}/status-history` | история изменений статуса (FR-3) |
| GET/POST | `/api/organizations` | реестр / создание организации с опциональным первым диспетчером |

## Документация

Точка входа — [docs/Vision.md](docs/Vision.md) (концепция) и [docs/SRS.md](docs/SRS.md) (требования). Архитектурно значимые прецеденты с диаграммами и макетами — [docs/CoreUseCases.md](docs/CoreUseCases.md).

## Генерация диаграмм из PUML

Требования: установленная Java (JRE/JDK 11+).

Рендер диаграмм из `docs/diagrams/usecases/` в `docs/diagrams/out/`:

```bash
cd docs
python scripts/render_puml.py --jar tools/plantuml/plantuml.jar --fmt png
```

Генерация графика окупаемости (требуется Python + matplotlib):

```bash
cd docs
python scripts/render_payback.py
```
