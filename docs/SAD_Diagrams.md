# Диаграммы для SAD

Комплект диаграмм к документу **Software Architecture Document** — [SAD.md](SAD.md); матрица
типов диаграмм по точкам зрения приведена в его разделе 2 («Architectural Representation»).
Тип диаграммы строится в тех точках зрения, где матрица ставит «+»: для State Machine, Sequence,
Cooperative, Class и Activity это все три — Use-Case View, Logical View, Implementation View, —
а для Use Case Diagram только Use-Case View.

Сноска матрицы требует строить **на основе одного прецедента** четыре типа диаграмм: Activity,
Sequence, Cooperative и State Machine. Use Case Diagram и Class Diagram в эту сноску не входят,
поэтому построены на систему целиком.

## Распределение прецедентов по типам диаграмм

| Тип диаграммы | Прецедент | Почему выбран |
|---|---|---|
| State Machine Diagram | **UC-2 «Управлять статусами заявки»** | Единственный прецедент с явной статусной моделью; реализован полностью (`RequestStatusMachine`, история статусов, audit) |
| Sequence Diagram | **UC-1 «Создать заявку на перевозку»** | Самый длинный обмен сообщениями: клиент → REST → сервисы → внешняя система Wasteland Intel → две БД; включает UC-5, UC-6, UC-7, UC-8 |
| Cooperative (Communication) Diagram | **UC-32 «Создать организацию»** | Мультитенантность и провижининг: наглядная кооперация объектов разных слоёв, не пересекается с UC-1 и UC-2 |
| Activity Diagram | **UC-7 «Рассчитать risk_score»** | Единственный оставшийся свободным реализованный прецедент: ветвление основного потока (внешние данные получены / источник недоступен / данные устарели) даёт содержательную диаграмму активности, а Implementation View опирается на фактический код, а не на проект |
| Use Case Diagram | — (система целиком) | Сноской не ограничена: показывает акторов, границу системы и архитектурно значимые прецеденты |
| Class Diagram | — (система целиком) | Сноской не ограничена: три точки зрения — это три уровня детализации одной модели (сущности → классы по слоям → полные классы), а не три прецедента |
| Package Diagram | — (система целиком) | Сноской не ограничена: делит приложение на слои и показывает зависимости между ними; матрица требует её только в Logical View |
| Data Base Diagram | — (система целиком) | Сноской не ограничена: модель данных системы. Матрица требует её в Implementation View; логический вид добавлен дополнительно, чтобы отделить сущности данных от даталогической модели |
| Deployment Diagram | — (система целиком) | Сноской не ограничена: узлы развёртывания и каналы взаимодействия; матрица требует её только в Deployment View |

Прецеденты UC-16 «Зафиксировать прохождение этапа рейса» и UC-19 «Сообщить об инциденте в рейсе»
под диаграммы, привязанные к одному прецеденту, не брались: в коде они не реализованы, поэтому
Implementation View для них был бы проектным. Их сущности показаны как проектируемые на
диаграмме классов (Use-Case View); черновые диаграммы по ним есть в
[diagrams/usecases](diagrams/usecases).

## Состав комплекта

Исходники — `diagrams/sad/*.puml`, отрендеренные изображения — `diagrams/out/*.png`.

| Раздел SAD | Диаграмма | Исходник | Изображение |
|---|---|---|---|
| 4. Use-Case View | Use Case, система целиком | [UCD_UseCaseView.puml](diagrams/sad/UCD_UseCaseView.puml) | [png](diagrams/out/UCD_UseCaseView.png) |
| 4. Use-Case View | Class, система целиком | [CLS_UseCaseView.puml](diagrams/sad/CLS_UseCaseView.puml) | [png](diagrams/out/CLS_UseCaseView.png) |
| 4. Use-Case View | Activity, UC-7 | [ACT_UC7_UseCaseView.puml](diagrams/sad/ACT_UC7_UseCaseView.puml) | [png](diagrams/out/ACT_UC7_UseCaseView.png) |
| 4. Use-Case View | State Machine, UC-2 | [SM_UC2_UseCaseView.puml](diagrams/sad/SM_UC2_UseCaseView.puml) | [png](diagrams/out/SM_UC2_UseCaseView.png) |
| 4. Use-Case View | Sequence, UC-1 | [SEQ_UC1_UseCaseView.puml](diagrams/sad/SEQ_UC1_UseCaseView.puml) | [png](diagrams/out/SEQ_UC1_UseCaseView.png) |
| 4. Use-Case View | Cooperative, UC-32 | [COL_UC32_UseCaseView.puml](diagrams/sad/COL_UC32_UseCaseView.puml) | [png](diagrams/out/COL_UC32_UseCaseView.png) |
| 5. Logical View | Class, система целиком | [CLS_LogicalView.puml](diagrams/sad/CLS_LogicalView.puml) | [png](diagrams/out/CLS_LogicalView.png) |
| 5. Logical View | Activity, UC-7 | [ACT_UC7_LogicalView.puml](diagrams/sad/ACT_UC7_LogicalView.puml) | [png](diagrams/out/ACT_UC7_LogicalView.png) |
| 5. Logical View | State Machine, UC-2 | [SM_UC2_LogicalView.puml](diagrams/sad/SM_UC2_LogicalView.puml) | [png](diagrams/out/SM_UC2_LogicalView.png) |
| 5. Logical View | Sequence, UC-1 | [SEQ_UC1_LogicalView.puml](diagrams/sad/SEQ_UC1_LogicalView.puml) | [png](diagrams/out/SEQ_UC1_LogicalView.png) |
| 5. Logical View | Cooperative, UC-32 | [COL_UC32_LogicalView.puml](diagrams/sad/COL_UC32_LogicalView.puml) | [png](diagrams/out/COL_UC32_LogicalView.png) |
| 5. Logical View | Package, система целиком | [PKG_LogicalView.puml](diagrams/sad/PKG_LogicalView.puml) | [png](diagrams/out/PKG_LogicalView.png) |
| 5. Logical View | Data Base, система целиком | [DB_LogicalView.puml](diagrams/sad/DB_LogicalView.puml) | [png](diagrams/out/DB_LogicalView.png) |
| 7. Deployment View | Deployment, система целиком | [DEP_DeploymentView.puml](diagrams/sad/DEP_DeploymentView.puml) | [png](diagrams/out/DEP_DeploymentView.png) |
| 8. Implementation View | Class, система целиком | [CLS_ImplementationView.puml](diagrams/sad/CLS_ImplementationView.puml) | [png](diagrams/out/CLS_ImplementationView.png) |
| 8. Implementation View | Activity, UC-7 | [ACT_UC7_ImplementationView.puml](diagrams/sad/ACT_UC7_ImplementationView.puml) | [png](diagrams/out/ACT_UC7_ImplementationView.png) |
| 8. Implementation View | State Machine, UC-2 | [SM_UC2_ImplementationView.puml](diagrams/sad/SM_UC2_ImplementationView.puml) | [png](diagrams/out/SM_UC2_ImplementationView.png) |
| 8. Implementation View | Sequence, UC-1 | [SEQ_UC1_ImplementationView.puml](diagrams/sad/SEQ_UC1_ImplementationView.puml) | [png](diagrams/out/SEQ_UC1_ImplementationView.png) |
| 8. Implementation View | Cooperative, UC-32 | [COL_UC32_ImplementationView.puml](diagrams/sad/COL_UC32_ImplementationView.puml) | [png](diagrams/out/COL_UC32_ImplementationView.png) |
| 8. Implementation View | Data Base, система целиком | [DB_ImplementationView.puml](diagrams/sad/DB_ImplementationView.puml) | [png](diagrams/out/DB_ImplementationView.png) |

Итого 20 диаграмм: Use Case, Package и Deployment — по одной, Data Base — две (логический и
реализационный виды), Class, Activity, State Machine, Sequence и Cooperative — по три.

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

### Use Case Diagram — система целиком

- **Use-Case View.** Акторы из [UseCases.md](UseCases.md), включая абстрактного «Полевого
  пользователя», от которого наследуются Караван-мастер, Капитан охраны и Полевой медик, и внешние
  системы Wasteland Intel и NCR Checkpoint & Tax Terminal. Внутри границы «ИС «Караваны»» раскрыты
  архитектурно значимые и реализованные прецеденты (UC-1, UC-2, UC-3, UC-5, UC-6, UC-7, UC-8,
  UC-12, UC-32) и связи `<<include>>` между ними; UC-16 и UC-19 показаны как нереализованные.
  Остальные 23 прецедента собраны в одну группу с пунктирной рамкой, полный перечень — в
  [UseCases.md](UseCases.md) и на [UC_0_General.png](diagrams/out/UC_0_General.png).

### Class Diagram — система целиком

- **Use-Case View.** Сущности предметной области и связи между ними, без методов и слоёв:
  организация и пользователи, заявка со статусом и историей переходов, маршрут с участками и
  контрольными точками, снимок оценки риска и событие аудита. Проектируемые сущности UC-16 и UC-19
  (этап рейса, журнал контрольных точек, инцидент, участники, RecoveryRequest) помечены как
  «проект» — классов в коде нет, хранилище для них ещё не выбрано.
- **Logical View.** Основные классы и интерфейсы их взаимодействия, разложенные по пакетам слоёв
  (`frontend.pages` / `frontend.components` / `frontend.api` → `backend.web` → `backend.service` →
  `backend.domain` / `backend.repository` → инфраструктура). Ключевые методы приведены без полных
  сигнатур. Отдельной заметкой перечислены фактические отступления от правила DC-6 «web → service →
  repository»: транзакция открывается в слое web (`@Transactional` на методах контроллеров),
  контроллеры справочников обращаются к репозиториям напрямую, слой web вызывает доменные правила
  при сборке DTO и разборе параметров.
- **Implementation View.** Фактические поля и сигнатуры методов, аннотации JPA и MongoDB, таблицы
  PostgreSQL и коллекции MongoDB, типы связей. Контур ограничен реализованными прецедентами
  UC-1, UC-2, UC-3, UC-7, UC-32; что именно осталось за контуром, перечислено в заметке
  «Контур диаграммы» на самой диаграмме.

### Activity Diagram — UC-7 «Рассчитать risk_score»

- **Use-Case View.** Шаги основного потока в дорожках «Диспетчер», «ИС «Караваны»» и «Wasteland
  Intel»: запрос угроз по участкам маршрута, агрегация, корректировка ценностью груза, сохранение и
  формирование рекомендации. Показаны альтернативные потоки 2а (источник недоступен → `risk_score`
  = «Н/Д», пометка «требует пересчёта») и 2б (данные актуальности старше 24 часов → пометка «на
  основе устаревших данных»).
- **Logical View.** Те же шаги, разложенные по дорожкам слоёв — `backend.web`, `backend.service`,
  `backend.domain`, `backend.repository`, `frontend.components` / `frontend.api` и инфраструктура
  (Wasteland Intel, PostgreSQL, MongoDB).
- **Implementation View.** Фактический след вызовов:
  `POST /api/requests/{id}/risk-score` → `RequestController.recalculateRisk()` →
  `RequestService.recalculateRisk()` → `RiskService.calculate(route, cargoValueCaps)` →
  `WastelandIntelClient.fetchThreats()` → `GET /threats?segments=…`. Приведены формула
  `base = min(100, сумма уровней угроз × 6)`, коэффициент ценности груза (`≥20000` → +30,
  `≥5000` → +20, `≥1000` → +10, иначе 0), итог `score = min(100, base + cargoFactor)`, пороги
  рекомендаций 80 / 60 / 30, ветка `RiskResult.unavailable()`, проверка `asOf` на 24 часа и
  сохранение снимка в коллекцию `risk_assessment` вместе с полями `risk_score`, `risk_status` и
  `recommendation` в таблице `caravan_request`.

### Package Diagram — система целиком

- **Logical View.** Приложение разделено на пакеты `presentation` (контроллеры, DTO, валидация,
  обработчики исключений), `application` (сервисы, сценарии, DTO слоя приложения),
  `domain` (сущности, интерфейсы репозиториев, объекты-значения, доменные исключения),
  `infrastructure` (реализации репозиториев, адаптеры внешних систем, безопасность, аудит,
  конфигурация, Kafka, специфика СУБД) и `common` (утилиты, константы, общие исключения). Показаны
  зависимости `presentation → application → domain`, обращение `infrastructure → domain`,
  доступ `application → infrastructure` и связи `infrastructure` с внешними системами
  Wasteland Intel и NCR Checkpoint. Имена пакетов здесь отражают целевое разделение по слоям и не
  совпадают с именами фактических пакетов кода, перечисленными в разделе «Уровень детализации».

### Data Base Diagram — система целиком

- **Logical View.** Сущности данных с атрибутами и связями с кратностями, без привязки к СУБД:
  заявка на перевозку и её статус, маршрут с контрольными точками, груз-манифест с позициями,
  команда рейса и пользователи с ролями, организация, инцидент со типом и тяжестью,
  RecoveryRequest, журнал контрольных точек, финансовый отчёт и резерв припасов.
- **Implementation View.** Даталогическая модель: таблицы PostgreSQL с типами колонок, первичными
  и внешними ключами, индексами и уникальными ограничениями, и коллекции MongoDB для событий и
  аудита (`incidents`, `recovery_requests`, `checkpoint_logs`, `audit_log`), а также внешние ключи
  между таблицами.

### Deployment Diagram — система целиком

- **Deployment View.** Узел «Сервер караванной конторы» с backend на Spring Boot (Java 21, REST
  API), PostgreSQL для оперативных данных, MongoDB для событий и аудита, Kafka для очередей
  сообщений и центральным терминалом управления; клиентские узлы — стационарный терминал офиса
  (веб-клиент на React) и полевое устройство Pip-Boy (PWA-клиент с локальным хранилищем для работы
  офлайн); внешние узлы Wasteland Intel и NCR Checkpoint. На связях указаны протоколы: HTTPS от
  клиентов, REST/HTTPS до внешних систем, JDBC и MongoDB Driver до хранилищ, Producer/Consumer до
  Kafka, а также резервное копирование на голотейп.

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
- **Сущности UC-16 и UC-19** (этап рейса, журнал контрольных точек, инцидент, его участники,
  RecoveryRequest) в коде отсутствуют: на диаграмме классов (Use-Case View) они помечены как
  «проект» и построены по [CoreUseCases](CoreUseCases.md), [SRS](SRS.md) и
  [глоссарию](Glossary_Karavany_FNV.md). Хранилище для них не выбрано, поэтому в Logical и
  Implementation View они не показаны.
- **Аудит изменений данных заявки** требуется требованием **RL-4** ([SRS](SRS.md): «журнал аудита
  должен фиксировать все операции изменения данных: создание, обновление и удаление заявок,
  манифестов, пользователей, организаций»). Событий создания заявки и пересчёта `risk_score` в
  `audit_event` нет — на диаграмме активности UC-7 это отмечено заметкой. Требование FR-35
  относится только к операциям по управлению пользователями и к данным заявки не применяется.
- **Диаграмма пакетов** описывает целевое разделение на слои (`presentation`, `application`,
  `domain`, `infrastructure`, `common`). Фактическая структура кода другая — пакеты по предметным
  модулям (`com.karavany.request`, `.organization`, `.route`, `.risk`, `.audit`), внутри каждого
  слои `web` / `service` / `domain` / `repository`; именно эти имена перечислены в разделе
  «Уровень детализации» и использованы на диаграммах классов и активности. Kafka на диаграмме
  пакетов и на диаграмме развёртывания заявлена как целевой компонент — в `docker-compose.yml`
  её нет.
- **Диаграмма баз данных** описывает целевую схему хранения. Фактически миграциями `V1`–`V6`
  созданы таблицы `caravan_request`, `route`, `route_segment`, `checkpoint`, `organization`,
  `app_user`, `request_status_history` и коллекции `risk_assessment`, `audit_event`. Таблиц команды
  рейса, груз-манифеста, припасов и финансового отчёта, а также коллекций инцидентов,
  RecoveryRequest и журнала контрольных точек в базе пока нет — они относятся к прецедентам
  UC-9…UC-22, которые не реализованы.
- **Timeline Diagram (раздел 6, Process View)** не построена: матрица требует её только при наличии
  процессов, жёстко привязанных к моментам времени.

## Рендеринг

Из каталога `docs` (нужна Java 11+; Graphviz не требуется — диаграммы прецедентов, классов,
состояний и кооперации используют встроенный движок `!pragma layout smetana`, а диаграммы
активности и последовательности обходятся штатной раскладкой PlantUML):

```bash
python scripts/render_puml.py --jar tools/plantuml/plantuml.jar --src diagrams/sad --out diagrams/out --fmt png
```
