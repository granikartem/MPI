# ИС «Караваны»

Информационная система управления караванными перевозками в сеттинге Fallout: New Vegas. Учебный проект в рамках дисциплины МПИ.

## Структура репозитория

```
docs/        — проектная документация (Vision, SRS, SDP, UseCases, BusinessCase, RiskList, Glossary)
  diagrams/  — диаграммы (PlantUML-исходники + отрендеренные PNG)
  mockups/   — HTML-макеты и скриншоты интерфейсов
  scripts/   — служебные скрипты (рендер диаграмм и графиков)
  tools/     — внешние инструменты (plantuml.jar)
backend/     — серверная часть (Java 21, Spring Boot) — в разработке
frontend/    — веб-клиент (React 18) — в разработке
```

Подробный план реализации — [docs/ImplementationPlan.md](docs/ImplementationPlan.md).

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
