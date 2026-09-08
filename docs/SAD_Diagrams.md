# Диаграммы для SAD — State Machine, Sequence, Cooperative

Комплект диаграмм к документу **Software Architecture Document** (шаблон `SAD_template.doc`).
Согласно таблице из раздела 2 шаблона («Architectural Representation») каждый тип диаграммы
строится **в трёх точках зрения** — Use-Case View, Logical View, Implementation View, — а сноска
шаблона требует, чтобы каждый тип диаграмм строился **на основе своего прецедента**.

## Распределение прецедентов по типам диаграмм

| Тип диаграммы | Прецедент | Почему выбран |
|---|---|---|
| State Machine Diagram | **UC-2 «Управлять статусами заявки»** | Единственный прецедент с явной статусной моделью; реализован полностью (`RequestStatusMachine`, история статусов, audit) |
| Sequence Diagram | **UC-1 «Создать заявку на перевозку»** | Самый длинный обмен сообщениями: клиент → REST → сервисы → внешняя система Wasteland Intel → две БД; включает UC-5, UC-6, UC-7, UC-8 |
| Cooperative (Communication) Diagram | **UC-32 «Создать организацию»** | Мультитенантность и провижининг: наглядная кооперация объектов разных слоёв, не пересекается с UC-1 и UC-2 |

Диаграмма активности (Activity) в комплект не входит — под неё остаются свободными UC-7 и UC-16,
для которых уже есть черновые activity-диаграммы в [diagrams/usecases](diagrams/usecases).

## Состав комплекта

Исходники — `diagrams/sad/*.puml`, отрендеренные изображения — `diagrams/out/*.png`.

| Раздел SAD | Диаграмма | Исходник | Изображение |
|---|---|---|---|
| 4. Use-Case View | State Machine, UC-2 | [SM_UC2_UseCaseView.puml](diagrams/sad/SM_UC2_UseCaseView.puml) | [png](diagrams/out/SM_UC2_UseCaseView.png) |
| 4. Use-Case View | Sequence, UC-1 | [SEQ_UC1_UseCaseView.puml](diagrams/sad/SEQ_UC1_UseCaseView.puml) | [png](diagrams/out/SEQ_UC1_UseCaseView.png) |
| 4. Use-Case View | Cooperative, UC-32 | [COL_UC32_UseCaseView.puml](diagrams/sad/COL_UC32_UseCaseView.puml) | [png](diagrams/out/COL_UC32_UseCaseView.png) |
| 5. Logical View | State Machine, UC-2 | [SM_UC2_LogicalView.puml](diagrams/sad/SM_UC2_LogicalView.puml) | [png](diagrams/out/SM_UC2_LogicalView.png) |
| 5. Logical View | Sequence, UC-1 | [SEQ_UC1_LogicalView.puml](diagrams/sad/SEQ_UC1_LogicalView.puml) | [png](diagrams/out/SEQ_UC1_LogicalView.png) |
| 5. Logical View | Cooperative, UC-32 | [COL_UC32_LogicalView.puml](diagrams/sad/COL_UC32_LogicalView.puml) | [png](diagrams/out/COL_UC32_LogicalView.png) |
| 8. Implementation View | State Machine, UC-2 | [SM_UC2_ImplementationView.puml](diagrams/sad/SM_UC2_ImplementationView.puml) | [png](diagrams/out/SM_UC2_ImplementationView.png) |
| 8. Implementation View | Sequence, UC-1 | [SEQ_UC1_ImplementationView.puml](diagrams/sad/SEQ_UC1_ImplementationView.puml) | [png](diagrams/out/SEQ_UC1_ImplementationView.png) |
| 8. Implementation View | Cooperative, UC-32 | [COL_UC32_ImplementationView.puml](diagrams/sad/COL_UC32_ImplementationView.puml) | [png](diagrams/out/COL_UC32_ImplementationView.png) |

## Уровень детализации по точкам зрения

Шаблон задаёт три уровня; в комплекте они выдержаны так:

- **Use-Case View — абстрактное описание.** Только предметная область: акторы, система как единое
  целое, внешние системы, бизнес-состояния и бизнес-сообщения. Ни классов, ни методов, ни HTTP.
- **Logical View — описание по слоям.** Компоненты слоёв и правила их взаимодействия. Уровни
  взаимодействия совпадают с пакетами: `frontend.pages` / `frontend.components` / `frontend.api` →
  `backend.web` → `backend.service` → `backend.domain` / `backend.repository` → инфраструктура
  (PostgreSQL, MongoDB, Wasteland Intel). Эти же имена пакетов нужно использовать в диаграмме
  пакетов раздела 5 SAD.
- **Implementation View — полное описание.** Фактические классы и методы реализации, сигнатуры,
  эндпоинты, тела запросов, коды ответов, таблицы PostgreSQL и коллекции MongoDB.

## Краткое описание диаграмм (для текста SAD)

### State Machine Diagram — UC-2 «Управлять статусами заявки»

- **Use-Case View.** Семь состояний заявки (Черновик, Готов к отправке, В пути, Задержка,
  Доставлен, Закрыт, Отменён) и переходы между ними; на каждом переходе указано действие и актор,
  который его инициирует. Показано, что «Закрыт» и «Отменён» — финальные, а отмена возможна только
  до выхода каравана на маршрут.
- **Logical View.** Те же состояния с добавлением сторожевых условий (роль актора, обязательная
  причина, проверка готовности рейса) и общего эффекта «записать переход». Состояния «В пути» и
  «Задержка» объединены в композитное состояние «Рейс на маршруте». Отдельной заметкой описано
  распределение ответственности по пакетам и поведение при отклонении перехода.
- **Implementation View.** Состояния — константы `RequestStatus`; переходы подписаны реальными
  элементами таблицы `RequestStatusMachine.TRANSITIONS`, телом запроса
  `POST /api/requests/{id}/status` и порядком проверок в `RequestStatusService.changeStatus(...)`.
  Отдельно показан эффект успешного перехода (запись в `caravan_request`,
  `request_status_history`, `audit_event`) и коды ответов 200 / 400 / 409.

### Sequence Diagram — UC-1 «Создать заявку на перевозку»

- **Use-Case View.** Обмен между диспетчером, системой и Wasteland Intel по шагам основного потока;
  альтернативы показаны фрагментами `alt`: ручной маршрут (3а), недоступность внешней системы (4а),
  отмена создания (8а).
- **Logical View.** Те же шаги, но участники — компоненты слоёв: форма и клиент REST API на
  frontend, контроллер, сервисы заявок / ETA / оценки риска, клиент внешней разведки и репозитории
  на backend, PostgreSQL, MongoDB и Wasteland Intel в инфраструктуре.
- **Implementation View.** Полный след вызовов: `RequestForm.submit()` → `api.createRequest()` →
  `POST /api/requests` → `RequestController.create()` → `RequestService.create()` /
  `createWithManualRoute()` → `EtaService.computeHours()` → `RiskService.calculate()` →
  `WastelandIntelClient.fetchThreats()` → `GET /threats?segments=…` → сохранение заявки, снимка
  оценки риска и стартовой записи истории статусов, ответ `HTTP 201`. Показана формула risk_score
  и ветка `RiskResult.unavailable()`.

### Cooperative (Communication) Diagram — UC-32 «Создать организацию»

- **Use-Case View.** Аналитические объекты прецедента (`<<boundary>>`, `<<control>>`, `<<entity>>`)
  и пронумерованные сообщения между ними; альтернативные потоки 4а (неуникальное название) и 6а
  (диспетчер не назначается) описаны заметкой.
- **Logical View.** Те же кооперирующиеся объекты, разложенные по пакетам слоёв, с иерархической
  нумерацией сообщений (1, 1.1, 1.1.1, …), которая показывает вложенность вызовов между слоями.
- **Implementation View.** Объекты — экземпляры реальных классов (`page:Organizations.tsx`,
  `c:OrganizationController`, `s:OrganizationService`, `oRepo:OrganizationRepository`,
  `aRepo:AuditEventRepository`, …), сообщения — вызовы методов с сигнатурами и SQL/Mongo-операции;
  отдельно описана обработка ошибок (`IllegalArgumentException`, `DataIntegrityViolationException`
  → HTTP 400).

## Что показано как предполагаемая реализация

Диаграммы построены по фактическому коду. Элементы, которых в коде пока нет, помечены на самих
диаграммах заметками и в тексте ниже:

- **Проверка готовности рейса перед выходом на маршрут (FR-10).** `RequestReadinessGuard.blockerFor(...)`
  сейчас возвращает `null` для всех переходов; сама проверка появится вместе с моделью команды рейса
  (UC-9). На диаграммах показана как сторожевое условие перехода `READY → EN_ROUTE`.
- **Источник роли актора.** Роль приходит в теле запроса (`actorRole`), а не из сессии — до
  реализации аутентификации (UC-25).
- **Автоматический переход `EN_ROUTE → DELAYED` ролью `SYSTEM`** разрешён статусной моделью, но
  вызывающий его код (UC-19) ещё не реализован.
- **Audit-событие `REQUEST_CREATED`** для UC-1 в MongoDB не пишется (известный пробел,
  см. [ImplementationPlan](ImplementationPlan.md)); на диаграмме последовательности отмечено заметкой.
- **Ветка `STALE`** в расчёте risk_score реализована, но не воспроизводится на WireMock-заглушке,
  отдающей фиксированную дату актуальности.

## Рендеринг

Из каталога `docs` (нужна Java 11+; Graphviz не требуется — диаграммы состояний и кооперации
используют встроенный движок `!pragma layout smetana`):

```bash
python scripts/render_puml.py --jar tools/plantuml/plantuml.jar --src diagrams/sad --out diagrams/out --fmt png
```
