# Диаграммы для SAD

Комплект диаграмм к документу **Software Architecture Document** — [SAD.md](SAD.md); матрица
типов диаграмм по точкам зрения приведена в его разделе 2 («Architectural Representation»).
Тип диаграммы строится в тех точках зрения, где матрица ставит «+»: для State Machine, Sequence,
Cooperative, Class и Activity это все три — Use-Case View, Logical View, Implementation View;
для Use Case Diagram — только Use-Case View, для Package Diagram — только Logical View, для
Data Base Diagram — только Implementation View, для Deployment Diagram — только Deployment View,
для Timeline Diagram — только Process View.

Сноска матрицы относит к прецедентам четыре типа диаграмм: Activity, Sequence, Cooperative и
State Machine. Каждый из них построен в трёх точках зрения на трёх разных прецедентах; для State
Machine, Sequence и Cooperative прецеденты UC-1, UC-2 и UC-32 распределены так, что у каждого типа и
в каждой точке зрения прецедент свой. Остальные типы в сноску не входят и построены на систему
целиком.

## Распределение прецедентов по типам диаграмм

| Тип диаграммы | Прецедент | Почему выбран |
|---|---|---|
| State Machine Diagram | **UC-2** (Use-Case View), **UC-1** (Logical View), **UC-32** (Implementation View) | UC-2: статусная модель заявки; UC-1: заявка проходит состояния формирования (маршрут, ETA, оценка риска) до «Черновика»; UC-32: создание организации — цепочка состояний внутри одной транзакции `OrganizationService.create(...)` |
| Sequence Diagram | **UC-1** (Use-Case View), **UC-32** (Logical View), **UC-2** (Implementation View) | UC-1: обмен актора, системы и Wasteland Intel; UC-32: вызовы между слоями при создании организации; UC-2: полный HTTP-путь перехода статуса, включая асинхронную перезагрузку данных на клиенте |
| Cooperative (Communication) Diagram | **UC-32** (Use-Case View), **UC-2** (Logical View), **UC-1** (Implementation View) | UC-32: аналитические объекты boundary / control / entity; UC-2: кооперация компонентов слоёв при смене статуса; UC-1: самый широкий набор объектов реализации — клиент, сервисы, репозитории, хранилища и внешняя система |
| Activity Diagram | **UC-7 «Рассчитать risk_score»** (Use-Case View), **UC-1 «Создать заявку на перевозку»** (Logical View), **UC-32 «Создать организацию»** (Implementation View) | Один тип диаграмм покрывает разные прецеденты в разных точках зрения. Взяты все три реализованных коровых прецедента: UC-7 даёт ветвление по внешним данным, UC-1 — самый длинный поток через все логические компоненты, UC-32 — провижининг с двумя хранилищами и аудитом |
| Use Case Diagram | — (система целиком) | Сноской не ограничена: показывает акторов, границу системы и архитектурно значимые прецеденты |
| Class Diagram | — (система целиком) | Сноской не ограничена: три точки зрения — это три уровня детализации одной модели (сущности → классы по слоям → полные классы), а не три прецедента |
| Package Diagram | — (система целиком) | Сноской не ограничена: задаёт слои, на которые опираются Logical View остальных диаграмм |
| Data Base Diagram | — (система целиком) | Сноской не ограничена: модель данных системы. Матрица требует её только в Implementation View и в двух частях — полная ER-модель и её даталогическая модель, поэтому это две диаграммы |
| Deployment Diagram | — (система целиком) | Сноской не ограничена: размещение всех компонентов по машинам |
| Timeline Diagram | — (процессы системы) | Сноска ** матрицы: в системе есть процессы, привязанные ко времени, — сроки подписки, устаревание данных угроз, хранение аудита, полевая синхронизация, таймауты интеграции. Процессы разного масштаба времени разнесены по трём диаграммам, так как у диаграммы одна ось времени |

Прецеденты UC-16 «Зафиксировать прохождение этапа рейса» и UC-19 «Сообщить об инциденте в рейсе»
под диаграммы, привязанные к одному прецеденту, не брались: в коде они не реализованы, поэтому
Implementation View для них был бы проектным. Их сущности показаны как проектируемые на
диаграмме классов (Use-Case View) и в модели базы данных; черновые диаграммы по ним есть в
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
| 5. Logical View | Package, система целиком | [PKG_LogicalView.puml](diagrams/sad/PKG_LogicalView.puml) | [png](diagrams/out/PKG_LogicalView.png) |
| 5. Logical View | Class, система целиком | [CLS_LogicalView.puml](diagrams/sad/CLS_LogicalView.puml) | [png](diagrams/out/CLS_LogicalView.png) |
| 5. Logical View | Activity, UC-1 | [ACT_UC1_LogicalView.puml](diagrams/sad/ACT_UC1_LogicalView.puml) | [png](diagrams/out/ACT_UC1_LogicalView.png) |
| 5. Logical View | State Machine, UC-1 | [SM_UC1_LogicalView.puml](diagrams/sad/SM_UC1_LogicalView.puml) | [png](diagrams/out/SM_UC1_LogicalView.png) |
| 5. Logical View | Sequence, UC-32 | [SEQ_UC32_LogicalView.puml](diagrams/sad/SEQ_UC32_LogicalView.puml) | [png](diagrams/out/SEQ_UC32_LogicalView.png) |
| 5. Logical View | Cooperative, UC-2 | [COL_UC2_LogicalView.puml](diagrams/sad/COL_UC2_LogicalView.puml) | [png](diagrams/out/COL_UC2_LogicalView.png) |
| 6. Process View | Timeline, календарные процессы | [TL_Calendar_ProcessView.puml](diagrams/sad/TL_Calendar_ProcessView.puml) | [png](diagrams/out/TL_Calendar_ProcessView.png) |
| 6. Process View | Timeline, полевая синхронизация | [TL_Field_ProcessView.puml](diagrams/sad/TL_Field_ProcessView.puml) | [png](diagrams/out/TL_Field_ProcessView.png) |
| 6. Process View | Timeline, UC-1 | [TL_UC1_ProcessView.puml](diagrams/sad/TL_UC1_ProcessView.puml) | [png](diagrams/out/TL_UC1_ProcessView.png) |
| 7. Deployment View | Deployment, система целиком | [DEP_DeploymentView.puml](diagrams/sad/DEP_DeploymentView.puml) | [png](diagrams/out/DEP_DeploymentView.png) |
| 8. Implementation View | Class, система целиком | [CLS_ImplementationView.puml](diagrams/sad/CLS_ImplementationView.puml) | [png](diagrams/out/CLS_ImplementationView.png) |
| 8. Implementation View | Activity, UC-32 | [ACT_UC32_ImplementationView.puml](diagrams/sad/ACT_UC32_ImplementationView.puml) | [png](diagrams/out/ACT_UC32_ImplementationView.png) |
| 8. Implementation View | State Machine, UC-32 | [SM_UC32_ImplementationView.puml](diagrams/sad/SM_UC32_ImplementationView.puml) | [png](diagrams/out/SM_UC32_ImplementationView.png) |
| 8. Implementation View | Sequence, UC-2 | [SEQ_UC2_ImplementationView.puml](diagrams/sad/SEQ_UC2_ImplementationView.puml) | [png](diagrams/out/SEQ_UC2_ImplementationView.png) |
| 8. Implementation View | Cooperative, UC-1 | [COL_UC1_ImplementationView.puml](diagrams/sad/COL_UC1_ImplementationView.puml) | [png](diagrams/out/COL_UC1_ImplementationView.png) |
| 8. Implementation View | Data Base, часть 1: ER-модель | [DB_ER_ImplementationView.puml](diagrams/sad/DB_ER_ImplementationView.puml) | [png](diagrams/out/DB_ER_ImplementationView.png) |
| 8. Implementation View | Data Base, часть 2: даталогическая модель | [DB_Datalogical_ImplementationView.puml](diagrams/sad/DB_Datalogical_ImplementationView.puml) | [png](diagrams/out/DB_Datalogical_ImplementationView.png) |

Итого 23 диаграммы: Use Case, Package и Deployment — по одной, Data Base — две (ER-модель и
даталогическая модель), Timeline — три, Class, Activity, State Machine, Sequence и Cooperative — по три.

## Уровень детализации по точкам зрения

Шаблон задаёт три уровня; в комплекте они выдержаны так:

- **Use-Case View — абстрактное описание.** Только предметная область: акторы, система как единое
  целое, внешние системы, бизнес-состояния и бизнес-сообщения. Ни классов, ни методов, ни HTTP.
- **Logical View — описание по слоям.** Логические компоненты и правила их взаимодействия.
  На диаграммах State Machine, Sequence и Cooperative уровни взаимодействия совпадают со слоями
  [диаграммы пакетов](diagrams/sad/PKG_LogicalView.puml): `presentation` → `application` → `domain`,
  `application` → `infrastructure` (`<<access>>`), внешние системы — через адаптеры `infrastructure`.
  Участники названы по ответственности («Создание заявки», «Оценка риска», «Заявка», «Хранение
  данных»), а не по техническим ролям классов: сервисы, репозитории и контроллеры появляются только
  в Implementation View. Диаграмма классов в Logical View пока использует имена
  фактических пакетов кода (`backend.web` / `backend.service` / `backend.repository`);
  диаграмма активности Logical View построена на тех же логических
  компонентах, что Sequence, Cooperative и State Machine.
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

### Package Diagram — система целиком

- **Logical View.** Слои `presentation` (web-клиент React, полевой клиент Pip-Boy, REST API),
  `application` (сценарии по прецедентам), `domain` (заявка, реестр, маршрут, риск, организация,
  учётная запись, событие аудита), `infrastructure` (хранение в PostgreSQL и MongoDB, адаптеры
  внешних систем, безопасность) и внешние системы Wasteland Intel и NCR Checkpoint & Tax Terminal.
  Компоненты названы так же, как участники Logical View диаграмм последовательности, кооперации и
  состояний. Зависимости идут только сверху вниз; красной
  связью показано фактическое отступление от DC-6 — контроллеры справочников читают репозитории
  напрямую. Заметка сопоставляет пакеты с фактической структурой кода.

### Activity Diagram — три прецедента

Один тип диаграмм разнесён по разным прецедентам, формат у всех трёх один: дорожки идут слева
направо от актора к инфраструктуре и внешним системам.

- **Use-Case View — UC-7 «Рассчитать risk_score».** Шаги основного потока в дорожках
  «Диспетчер караванов», «ИС «Караваны»» и «Wasteland Intel»: запрос угроз по участкам маршрута,
  агрегация, корректировка ценностью груза, сохранение и формирование рекомендации. Показаны
  альтернативные потоки 2а (источник недоступен → `risk_score` = «Н/Д», пометка «требует
  пересчёта») и 2б (данные актуальности старше 24 часов → пометка «на основе устаревших данных»).
- **Logical View — UC-1 «Создать заявку на перевозку».** Дорожки — логические компоненты
  диаграммы пакетов: «Интерфейс заявок» (`presentation`), «Создание заявки», «Расчёт ETA»,
  «Оценка риска» (`application`), «Маршрут, Заявка» (`domain`), «Хранение данных» и
  «Адаптер Wasteland Intel» (`infrastructure`). Порядок шагов — по
  [CoreUseCases](CoreUseCases.md): маршрут из шаблона или вручную (альт. 3а), расчёт risk_score
  и ETA, ценность груза, подтверждение диспетчера (альт. 8а — отмена), сохранение в статусе
  «Черновик». Недоступность Wasteland Intel показана как альт. поток 4а.
- **Implementation View — UC-32 «Создать организацию».** Те же дорожки логических компонентов,
  в узлах — фактические классы и методы: `POST /api/organizations` →
  `OrganizationController.create()` → `OrganizationService.create(CreateOrganizationCommand)` →
  `organizationRepository.findByNameIgnoreCase()` → `save(new Organization(tenantKey, …))` →
  `userRepository.save(new AppUser(…))` → `AuditEvent.organizationCreated()` → коллекция
  `audit_event`. Показаны альт. поток 4а (название занято → HTTP 400), альт. поток 6а
  (диспетчер не назначается), `tenantKey = "tnt_" + 8 символов UUID` как основа
  мультитенантности (FR-23, FR-24) и хеш пароля `"sha256:" + hex(SHA-256("karavany:" + пароль))`.

### Data Base Diagram — система целиком

- **Implementation View, часть 1 — ER-модель.** Все сущности данных системы с атрибутами,
  первичными и внешними ключами и связями с кратностями UML (`1..1`, `0..1`, `0..*`, `1..*`),
  сгруппированные по областям: организации и доступ (организация, подписка, терминал, роль,
  пользователь, ставка), заявка и маршрут (заявка, история статусов, план охраны и припасов, маршрут,
  участок, контрольная точка, снимок оценки риска), команда, груз и припасы (участник команды рейса,
  груз-манифест, позиция, пломба, сверка, расхождение, резерв припасов), полевые операции, финансы и
  аудит (этап рейса, отметка КТ/КПП, инцидент, RecoveryRequest, финансовый отчёт перевозки, событие
  аудита).
- **Implementation View, часть 2 — даталогическая модель.** Таблицы PostgreSQL 16 с типами колонок,
  `NOT NULL`, значениями по умолчанию и разделом ограничений у каждой таблицы: `PRIMARY KEY`,
  `FOREIGN KEY … REFERENCES`, `UNIQUE`, `CHECK`, индексы. Коллекции MongoDB 7 со структурой документов
  и индексами, включая TTL-индекс журнала аудита для RL-5. Связи подписаны кратностями UML и именем
  колонки внешнего ключа; пунктиром показаны ссылки по значению идентификатора между PostgreSQL и
  MongoDB. Роли — справочник `role`, команда рейса — `trip_crew_member`, финансовый отчёт — одна
  таблица `financial_report` с расходами по статьям.

### State Machine Diagram

- **Use-Case View, UC-2 «Управлять статусами заявки».** Семь состояний заявки (Черновик, Готов к
  отправке, В пути, Задержка, Доставлен, Закрыт, Отменён) и переходы между ними; на каждом переходе
  указано действие и актор, который его инициирует. Показано, что «Закрыт» и «Отменён» — финальные,
  а отмена возможна только до выхода каравана на маршрут.
- **Logical View, UC-1 «Создать заявку на перевозку».** Заявка от открытия формы до «Черновика»:
  «Заполняется» → композитное состояние «Формируется» (организация подтверждена → маршрут определён
  из шаблона или по участкам → ETA рассчитано → риск оценён либо требует пересчёта) → «Черновик».
  Альтернативы — отмена (8а) и возврат к заполнению, если не найдены организация, шаблон маршрута
  или контрольная точка. Эффекты переходов подписаны логическими компонентами диаграммы пакетов:
  «Интерфейс заявок», «Создание заявки», «Расчёт ETA», «Оценка риска», «Заявка», «Маршрут»,
  «Хранение данных», «Адаптер Wasteland Intel».
- **Implementation View, UC-32 «Создать организацию».** Состояния внутри одной транзакции
  `OrganizationService.create(...)`: команда принята → данные проверены (`findByNameIgnoreCase`,
  `validateDispatcher`) → организация `ACTIVE` (`organizationRepository.save`) → диспетчер назначен
  (`userRepository.save`; при альт. 6а пропускается) → событие `ORGANIZATION_CREATED` записано →
  HTTP 201. Отклонение — `IllegalArgumentException` или `DataIntegrityViolationException`, откат
  транзакции, HTTP 400.

### Sequence Diagram

Синхронный вызов — сплошная линия с закрашенной стрелкой, результат вызова указан в подписи
(«результат = операция(...)»); асинхронный — сплошная линия с открытой стрелкой. Ответные сообщения
(по UML 2.5 — пунктир) не рисуются.

- **Use-Case View, UC-1 «Создать заявку на перевозку».** Обмен между диспетчером, системой и
  Wasteland Intel по шагам основного потока; альтернативы показаны фрагментами `alt`: ручной маршрут
  (3а), недоступность внешней системы (4а), отмена создания (8а). Сообщения системы актору —
  асинхронные.
- **Logical View, UC-32 «Создать организацию».** Участники — логические компоненты слоёв диаграммы
  пакетов: «Интерфейс управления организациями» (`presentation`), «Создание организации»
  (`application`), «Организация», «Учётная запись», «Событие аудита» (`domain`), «Хранение данных»,
  «Журнал аудита» (`infrastructure`). Проверки названия и логина — фрагменты `break` (альт. 4а),
  назначение первого диспетчера — фрагмент `alt` (альт. 6а).
- **Implementation View, UC-2 «Управлять статусами заявки».** `StatusModal.apply()` →
  `api.changeStatus()` → `POST /api/requests/{id}/status` → `RequestStatusController` →
  `RequestService.getById()` → `RequestStatusService.changeStatus()` → `RequestStatusMachine.find()`,
  `RequestReadinessGuard.blockerFor()` → сохранение заявки, записи истории и события аудита. Отказы
  HTTP 400 / 409 — фрагменты `break`. После ответа клиент асинхронно перезагружает реестр
  (`getRegistry`), статус и историю переходов (`getStatusInfo`, `getStatusHistory`).

### Cooperative (Communication) Diagram

- **Use-Case View, UC-32 «Создать организацию».** Аналитические объекты прецедента (`<<boundary>>`,
  `<<control>>`, `<<entity>>`) и пронумерованные сообщения между ними; альтернативные потоки 4а
  (неуникальное название) и 6а (диспетчер не назначается) описаны заметкой.
- **Logical View, UC-2 «Управлять статусами заявки».** Компоненты слоёв диаграммы пакетов:
  «Интерфейс заявок» (`presentation`), «Управление статусами» (`application`), «Заявка», «Статусная
  модель заявки», «Запись истории статусов», «Событие аудита» (`domain`), «Хранение данных»,
  «Журнал аудита» (`infrastructure`). Иерархическая нумерация сообщений 1 → 1.1 → 1.1.1…1.1.9 и
  сторожевое условие `[переход допустим]`.
- **Implementation View, UC-1 «Создать заявку на перевозку».** Объекты — экземпляры классов
  (`form:RequestForm.tsx`, `c:RequestController`, `s:RequestService`, `eta:EtaService`,
  `risk:RiskService`, `intel:WastelandIntelClient`, репозитории заявок, организаций, маршрутов,
  контрольных точек и оценки риска), сообщения — вызовы методов с сигнатурами и запросы к
  PostgreSQL, MongoDB и Wasteland Intel. Шаблонный и ручной маршрут различаются сторожевыми
  условиями, перезагрузка реестра после создания — асинхронное сообщение.

### Timeline Diagram — процессы системы

- **Process View, календарные процессы** (ось — сутки). Подписка организации: оплаченный период
  30 суток → grace-период 30 суток с доступом только на чтение → блокировка (Vision 4.5, UC-34).
  Признак `risk_status`: через 24 часа после `asOf` данные устаревают, признак `STALE` выставляется
  при пересчёте risk_score. Журнал аудита: запись хранится не менее 3 месяцев (RL-5) и удаляется
  TTL-индексом.
- **Process View, полевая синхронизация** (ось — секунды). Инцидент фиксируется на Pip-Boy
  без связи и лежит в локальной очереди; после появления связи передаётся на сервер не позднее
  60 секунд (RL-3), при высокой тяжести статус рейса автоматически становится «Задержка» (актор
  SYSTEM), диспетчер получает уведомление не позднее 5 минут.
- **Process View, UC-1** (ось — миллисекунды). Поток обработки `POST /api/requests`
  при ответе Wasteland Intel и при его молчании: таймауты соединения и чтения по 2000 мс дают ответ
  примерно через 4,3 с, что расходится с PF-4 (отклик не более 1 секунды).

### Deployment Diagram — система целиком

- **Deployment View.** Центральный сервер (Intel Xeon E5-2643, 16 ядер, 128 ГБ, 26 ТБ, 10 Гбит/с)
  под FreeBSD 14.3-STABLE. Все компоненты установлены в ОС из пакетов и работают как службы rc.d:
  nginx 1.30 (`www/nginx`: web-клиент и PWA, TLS, прокси `/api/*`), OpenJDK 21 (`java/openjdk21`:
  `karavany-0.1.0.jar`), PostgreSQL 16 (`databases/postgresql16-server`) и MongoDB 7.0
  (`databases/mongodb70`) на отдельных ZFS-датасетах. Резервные копии (`pg_dump`, `mongodump`,
  ZFS-снапшоты) записываются на голотейп. Клиенты — офисный терминал (2 ядра, 8 ГБ, браузер; до 50)
  и Pip-Boy 3000 (ARM, 1 ГБ, 64 ГБ, Wi-Fi; PWA с IndexedDB; до 150). На связях указаны протоколы и
  порты: HTTPS :443 от клиентов к nginx, HTTP 127.0.0.1:8080 от nginx к backend, JDBC 127.0.0.1:5432,
  MongoDB Wire Protocol 127.0.0.1:27017, REST / HTTPS к Wasteland Intel и NCR Checkpoint. Заметка
  описывает изоляцию служб, фильтр pf, поставку артефактов и проверку порта MongoDB.

## Что показано как предполагаемая реализация

Диаграммы построены по фактическому коду. Элементы, которых в коде пока нет, помечены на самих
диаграммах заметками и в тексте ниже:

- **Проверка готовности рейса перед выходом на маршрут (FR-10).** `RequestReadinessGuard.blockerFor(...)`
  сейчас возвращает `null` для всех переходов; сама проверка появится вместе с моделью команды рейса
  (UC-9). На диаграмме последовательности UC-2 (Implementation View) это вызов
  `RequestReadinessGuard.blockerFor(...)`; в модели базы
  данных правило обязательности ролей задано полями `role.crew_required` и
  `role.crew_required_from_risk_score`.
- **Источник роли актора.** Роль приходит в теле запроса (`actorRole`), а не из сессии — до
  реализации аутентификации (UC-25).
- **Предусловия, связанные с организацией и аутентификацией.** UC-2: принадлежность актора
  организации заявки не проверяется — статус может сменить любой клиент, знающий `id` заявки.
  UC-1: существование организации проверяет только backend (`loadOrganization` → HTTP 400), форма
  отображается и при неизвестном `?org=`. UC-32: аутентификация суперпользователя не проверяется,
  актор `SUPERUSER` в audit-событии задан константой.
- **Автоматический переход `EN_ROUTE → DELAYED` ролью `SYSTEM`** разрешён статусной моделью, но
  вызывающий его код (UC-19) ещё не реализован.
- **Audit-событие `REQUEST_CREATED`** для UC-1 в MongoDB не пишется (известный пробел,
  см. [ImplementationPlan](ImplementationPlan.md)).
- **Ветка `STALE`** в расчёте risk_score реализована, но не воспроизводится на WireMock-заглушке,
  отдающей фиксированную дату актуальности; признак вычисляется только в момент расчёта, фоновой
  переоценки нет (Timeline, календарные процессы).
- **Сущности UC-16 и UC-19** (этап рейса, журнал контрольных точек, инцидент, его участники,
  RecoveryRequest) в коде отсутствуют: на диаграмме классов (Use-Case View) они помечены как
  «проект» и построены по [CoreUseCases](CoreUseCases.md), [SRS](SRS.md) и
  [глоссарию](Glossary_Karavany_FNV.md). В модели базы данных для них выбрано хранилище по DC-5:
  полевые события (`checkpoint_log`, `incident`) — коллекции MongoDB, этапы рейса и RecoveryRequest —
  таблицы PostgreSQL.
- **Аудит изменений данных заявки** требуется требованием **RL-4** ([SRS](SRS.md): «журнал аудита
  должен фиксировать все операции изменения данных: создание, обновление и удаление заявок,
  манифестов, пользователей, организаций»). Событий создания заявки и пересчёта `risk_score` в
  `audit_event` нет. Требование FR-35
  относится только к операциям по управлению пользователями и к данным заявки не применяется.
- **Диаграмма пакетов** описывает логическое разделение на слои (`presentation`, `application`,
  `domain`, `infrastructure`). Фактическая структура кода — пакеты по предметным модулям
  (`com.karavany.request`, `.organization`, `.route`, `.risk`, `.audit`). Слои
  `web` / `service` / `domain` / `repository` выделены вложенными пакетами только в `request`
  и `organization`: в `route` слоя `service` нет, а `risk` и `audit` подпакетов не имеют
  вовсе — там слой класса виден по стереотипу; соответствие приведено заметкой на диаграмме.
  Компоненты команды рейса, груза, полевых событий, финансов, пользователей, подписок, адаптер NCR
  и слой безопасности — проект.
- **Модель базы данных** описывает целевую схему. Фактически миграциями `V1`–`V6` созданы таблицы
  `caravan_request`, `route`, `route_segment`, `checkpoint`, `organization`, `app_user`,
  `request_status_history` и коллекции `risk_assessment`, `audit_event`. Отличия этих таблиц от модели
  (справочник ролей вместо текстовых полей, `eta_hours` вместо `estimated_delivery_hours`,
  дополнительные `CHECK`) закрываются следующей миграцией;
  таблицы подписок, терминалов, ставок, команды рейса, груз-манифеста, припасов, этапов, RecoveryRequest
  и финансового отчёта, а также коллекции `checkpoint_log` и `incident` относятся к нереализованным
  прецедентам.
- **Timeline Diagram.** Реализованы только таймауты Wasteland Intel (UC-1) и проверка 24 часов при
  расчёте risk_score. Сроки подписки, TTL журнала аудита, полевая синхронизация и уведомления — проект.
- **Deployment Diagram.** Артефакты `karavany-0.1.0.jar` и сборка web-клиента уже собираются проектом,
  пакеты nginx, OpenJDK 21, PostgreSQL 16 и MongoDB 7.0 есть в FreeBSD 14. Конфигурация nginx с TLS,
  скрипты служб rc.d, правила pf, PWA полевого клиента и резервное копирование на голотейп — проект.

## Рендеринг

Из каталога `docs` (нужна Java 11+; Graphviz не требуется — диаграммы прецедентов, классов,
пакетов, баз данных, развёртывания, состояний и кооперации используют встроенный движок
`!pragma layout smetana`, а диаграммы активности, последовательности и Timeline обходятся штатной
раскладкой PlantUML):

```bash
python scripts/render_puml.py --jar tools/plantuml/plantuml.jar --src diagrams/sad --out diagrams/out --fmt png
```
