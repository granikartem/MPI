# Software Architecture Document — ИС «Караваны»

Описание архитектуры. Структура разделов — по шаблону дисциплины. Рабочий индекс исходников
диаграмм с краткими описаниями каждой — [SAD_Diagrams.md](SAD_Diagrams.md).

## 1. Introduction (Введение)

### 1.1 Purpose (Назначение)

_Не заполнено._

### 1.2 Scope (Область применения)

_Не заполнено._

### 1.3 Definitions, Acronyms and Abbreviations (Определения и аббревиатуры)

_Не заполнено._

### 1.4 References (Ссылки)

_Не заполнено._

### 1.5 Overview (Обзор документа)

_Не заполнено._

## 2. Architectural Representation (Представление архитектуры)

Типы диаграмм по точкам зрения:

| Diagram \ View | Use Case View | Logical View | Implementation view | Process view** | Deployment View |
|---|---|---|---|---|---|
| Use Case Diagram | + | − | − | | − |
| Class Diagram | + (Взаимодействие сущностей) | + (Описание основных классов и интерфейсов их взаимодействия) | + (Полное описание классов с указанием их методов/полей, указать типы связей между классами) | | − |
| Activity Diagram | + (Абстрактное описание) | + (Более подробное описание, уровни взаимодействия должны совпадать с диаграммой пакетов) | + (Полное описание прецедента с указанием вызываемых методов, используемых классов и объектов) | | − |
| State Machine Diagram | + (Абстрактное описание) | + (Более подробное описание, уровни взаимодействия должны совпадать с диаграммой пакетов) | + (Полное описание прецедента с указанием вызываемых методов, используемых классов и объектов) | | − |
| Sequence Diagram | + (Абстрактное описание) | + (Более подробное описание, уровни взаимодействия должны совпадать с диаграммой пакетов) | + (Полное описание прецедента с указанием вызываемых методов, используемых классов и объектов) | | − |
| Cooperative Diagram | + (Абстрактное описание) | + (Более подробное описание, уровни взаимодействия должны совпадать с диаграммой пакетов) | + (Полное описание прецедента с указанием вызываемых методов, используемых классов и объектов) | | − |
| Package Diagram | − | + | − | | − |
| Data Base Diagram | − | − | + (Полная ER модель базы данных + её даталогическая модель) | | − |
| Deployment Diagram | − | − | − | | + (Подробная диаграмма развертывания с указанием характеристик машин и интерфейсов взаимодействия) |
| Timeline diagramm | | | | + | |

\* Activity, Sequence, Cooperative и State Machine диаграммы составляются на основе одного
прецедента (каждый тип диаграмм — на основе своего).

\*\* Всё представление описывается только в случае, если в системе есть процессы, жёстко привязанные
к определённым моментам времени (пример — наступление нового месяца, времени суток и т.д.).

Прецеденты, выбранные под типы диаграмм, привязанные к одному прецеденту:

| Тип диаграммы | Прецедент |
|---|---|
| State Machine Diagram | UC-2 «Управлять статусами заявки» |
| Sequence Diagram | UC-1 «Создать заявку на перевозку» |
| Cooperative (Communication) Diagram | UC-32 «Создать организацию» |
| Activity Diagram | UC-7 «Рассчитать risk_score» |

Use Case Diagram и Class Diagram сноской не ограничены и построены на систему целиком.

## 3. Architectural Goals and Constraints (Цели и ограничения архитектуры)

_Не заполнено._

## 4. Use-Case View

| Диаграмма | Что показывает | Исходник | Изображение |
|---|---|---|---|
| Use Case, система целиком | Акторы, граница системы и архитектурно значимые прецеденты | [UCD_UseCaseView.puml](diagrams/sad/UCD_UseCaseView.puml) | [png](diagrams/out/UCD_UseCaseView.png) |
| Class, система целиком | Сущности предметной области и связи между ними, без методов и слоёв | [CLS_UseCaseView.puml](diagrams/sad/CLS_UseCaseView.puml) | [png](diagrams/out/CLS_UseCaseView.png) |
| Activity, UC-7 | Шаги предметной области; дорожки — актор, система как единое целое и внешняя система | [ACT_UC7_UseCaseView.puml](diagrams/sad/ACT_UC7_UseCaseView.puml) | [png](diagrams/out/ACT_UC7_UseCaseView.png) |
| State Machine, UC-2 | Состояния заявки и действия акторов | [SM_UC2_UseCaseView.puml](diagrams/sad/SM_UC2_UseCaseView.puml) | [png](diagrams/out/SM_UC2_UseCaseView.png) |
| Sequence, UC-1 | Обмен между актором, системой и внешней системой | [SEQ_UC1_UseCaseView.puml](diagrams/sad/SEQ_UC1_UseCaseView.puml) | [png](diagrams/out/SEQ_UC1_UseCaseView.png) |
| Cooperative, UC-32 | Аналитические объекты прецедента и порядок сообщений | [COL_UC32_UseCaseView.puml](diagrams/sad/COL_UC32_UseCaseView.puml) | [png](diagrams/out/COL_UC32_UseCaseView.png) |

Краткие описания всех диаграмм этого раздела — [SAD_Diagrams.md](SAD_Diagrams.md).

## 5. Logical View

Уровни взаимодействия (на диаграммах классов и активности имена приведены дословно как имена
пакетов; на диаграммах последовательности и кооперации — как стереотипы участников и вложенные
пакеты; на диаграмме состояний пакетов нет, имена уровней перечислены в заметке к диаграмме):
`frontend.pages` / `frontend.components` / `frontend.api` → `backend.web` → `backend.service` →
`backend.domain` / `backend.repository` → инфраструктура (PostgreSQL, MongoDB, Wasteland Intel).

| Диаграмма | Что показывает | Исходник | Изображение |
|---|---|---|---|
| Package, система целиком | Логические пакеты слоёв, их компоненты, внешние системы и зависимости; соответствие пакетам кода | [PKG_LogicalView.puml](diagrams/sad/PKG_LogicalView.puml) | [png](diagrams/out/PKG_LogicalView.png) |
| Class, система целиком | Основные классы и интерфейсы их взаимодействия по слоям | [CLS_LogicalView.puml](diagrams/sad/CLS_LogicalView.puml) | [png](diagrams/out/CLS_LogicalView.png) |
| Activity, UC-7 | Те же шаги в дорожках слоёв приложения | [ACT_UC7_LogicalView.puml](diagrams/sad/ACT_UC7_LogicalView.puml) | [png](diagrams/out/ACT_UC7_LogicalView.png) |
| State Machine, UC-2 | Состояния, сторожевые условия и эффекты переходов в разрезе слоёв | [SM_UC2_LogicalView.puml](diagrams/sad/SM_UC2_LogicalView.puml) | [png](diagrams/out/SM_UC2_LogicalView.png) |
| Sequence, UC-1 | Взаимодействие компонентов по слоям | [SEQ_UC1_LogicalView.puml](diagrams/sad/SEQ_UC1_LogicalView.puml) | [png](diagrams/out/SEQ_UC1_LogicalView.png) |
| Cooperative, UC-32 | Объекты по слоям приложения | [COL_UC32_LogicalView.puml](diagrams/sad/COL_UC32_LogicalView.puml) | [png](diagrams/out/COL_UC32_LogicalView.png) |

Диаграмма пакетов делит систему на слои `presentation` → `application` → `domain`,
`application` → `infrastructure` (`<<access>>`), `infrastructure` → `domain`, и показывает внешние
системы Wasteland Intel и NCR Checkpoint & Tax Terminal. Логические компоненты внутри пакетов названы
так же, как участники диаграмм последовательности, кооперации и состояний («Интерфейс заявок»,
«Создание заявки», «Оценка риска», «Хранение данных», «Адаптер Wasteland Intel» и т.д.). Фактическая
структура кода — пакеты по предметным модулям (`com.karavany.request`, `.organization`, `.route`,
`.risk`, `.audit`) со слоями `web` / `service` / `domain` / `repository` внутри; соответствие приведено
заметкой на диаграмме.

Краткие описания всех диаграмм этого раздела — [SAD_Diagrams.md](SAD_Diagrams.md).

## 6. Process View

Процессы, жёстко привязанные к моментам времени, в системе есть, поэтому представление описывается:

- **календарные** — окончание оплаченного периода подписки и 30-дневный grace-период
  ([Vision](Vision.md) 4.5, UC-34), устаревание данных Wasteland Intel через 24 часа (UC-7, альт. 2б),
  срок хранения журнала аудита не менее 3 месяцев (RL-5);
- **полевые** — передача событий с Pip-Boy на сервер не позднее 60 секунд после появления связи
  (RL-3) и уведомление диспетчера о критическом событии не позднее 5 минут;
- **обработка запроса UC-1** — таймауты обращения к Wasteland Intel (2000 мс на соединение и 2000 мс
  на чтение) против требования PF-4 «отклик не более 1 секунды».

| Диаграмма | Что показывает | Исходник | Изображение |
|---|---|---|---|
| Timeline, календарные процессы | Подписка и grace-период, признак устаревания risk_score, срок хранения аудита; ось — сутки | [TL_Calendar_ProcessView.puml](diagrams/sad/TL_Calendar_ProcessView.puml) | [png](diagrams/out/TL_Calendar_ProcessView.png) |
| Timeline, полевая синхронизация | Инцидент без связи, синхронизация Pip-Boy, автопереход статуса, уведомление; ось — секунды | [TL_Field_ProcessView.puml](diagrams/sad/TL_Field_ProcessView.puml) | [png](diagrams/out/TL_Field_ProcessView.png) |
| Timeline, UC-1 | Поток обработки создания заявки при ответе и молчании Wasteland Intel; ось — миллисекунды | [TL_UC1_ProcessView.puml](diagrams/sad/TL_UC1_ProcessView.puml) | [png](diagrams/out/TL_UC1_ProcessView.png) |

В коде реализованы только таймауты Wasteland Intel и проверка 24 часов в момент расчёта risk_score;
подписки, TTL журнала аудита и полевая синхронизация показаны как проект.

## 7. Deployment View

| Диаграмма | Что показывает | Исходник | Изображение |
|---|---|---|---|
| Deployment, система целиком | Узлы и среды выполнения, размещение служб и артефактов, характеристики машин, протоколы и порты | [DEP_DeploymentView.puml](diagrams/sad/DEP_DeploymentView.puml) | [png](diagrams/out/DEP_DeploymentView.png) |

Центральный сервер (Intel Xeon E5-2643, 16 ядер, 128 ГБ RAM, 26 ТБ, Ethernet 10 Гбит/с) работает под
FreeBSD 14.3-STABLE ([Vision](Vision.md) 9.2). Все серверные компоненты установлены непосредственно в
FreeBSD из пакетов и запускаются как службы rc.d: nginx 1.30 раздаёт web-клиент и PWA и принимает HTTPS
на :443, проксируя `/api/*` на backend; OpenJDK 21 исполняет `karavany-0.1.0.jar` (Spring Boot, миграции
Flyway); PostgreSQL 16 и MongoDB 7.0 хранят данные на отдельных ZFS-датасетах. Backend и базы данных
слушают только `127.0.0.1`, извне сетевой фильтр pf пропускает только TCP 443. Резервные копии
(`pg_dump`, `mongodump`, ZFS-снапшоты) записываются на голотейп. Клиенты — до 50 офисных терминалов
(браузер) и до 150 устройств Pip-Boy (PWA с локальной очередью событий). Внешние системы вызываются по
REST через HTTPS.

Краткое описание диаграммы — [SAD_Diagrams.md](SAD_Diagrams.md).

## 8. Implementation View

| Диаграмма | Что показывает | Исходник | Изображение |
|---|---|---|---|
| Class, система целиком | Поля, сигнатуры методов, аннотации JPA и MongoDB, таблицы PostgreSQL и коллекции MongoDB | [CLS_ImplementationView.puml](diagrams/sad/CLS_ImplementationView.puml) | [png](diagrams/out/CLS_ImplementationView.png) |
| Activity, UC-7 | Фактические методы, эндпоинты, формула, пороги и ветвления реализации | [ACT_UC7_ImplementationView.puml](diagrams/sad/ACT_UC7_ImplementationView.puml) | [png](diagrams/out/ACT_UC7_ImplementationView.png) |
| State Machine, UC-2 | Значения `RequestStatus`, реальные вызовы методов и HTTP-контракт | [SM_UC2_ImplementationView.puml](diagrams/sad/SM_UC2_ImplementationView.puml) | [png](diagrams/out/SM_UC2_ImplementationView.png) |
| Sequence, UC-1 | Реальные классы, методы и HTTP-контракт реализации | [SEQ_UC1_ImplementationView.puml](diagrams/sad/SEQ_UC1_ImplementationView.puml) | [png](diagrams/out/SEQ_UC1_ImplementationView.png) |
| Cooperative, UC-32 | Объекты реализации: классы, вызываемые методы и хранилища | [COL_UC32_ImplementationView.puml](diagrams/sad/COL_UC32_ImplementationView.puml) | [png](diagrams/out/COL_UC32_ImplementationView.png) |
| Data Base, часть 1: ER-модель | Все сущности данных, атрибуты, ключи и связи с кратностями (нотация «воронья лапка») | [DB_ER_ImplementationView.puml](diagrams/sad/DB_ER_ImplementationView.puml) | [png](diagrams/out/DB_ER_ImplementationView.png) |
| Data Base, часть 2: даталогическая модель | Таблицы PostgreSQL 16 и коллекции MongoDB 7: типы, PK / FK, UNIQUE, CHECK, индексы | [DB_Datalogical_ImplementationView.puml](diagrams/sad/DB_Datalogical_ImplementationView.puml) | [png](diagrams/out/DB_Datalogical_ImplementationView.png) |

Модель базы данных описывает целевую схему и шире фактической: миграциями `V1`–`V6` пока созданы
`caravan_request`, `route`, `route_segment`, `checkpoint`, `organization`, `app_user`,
`request_status_history` в PostgreSQL и коллекции `risk_assessment`, `audit_event` в MongoDB; остальные
таблицы и коллекции помечены как проект. Изменения существующих таблиц помечены `[V7]`:

- роли вынесены в справочник `role` и используются по id — вместо текстовых `app_user.role` и
  `request_status_history.actor_role`;
- караван-мастер, капитан охраны и полевой медик рейса — строки `trip_crew_member`
  (заявка, роль, сотрудник), а не колонки `master_id` / `medic_id`; обязательность ролей для FR-10
  задаётся в `role`;
- `caravan_request.eta_hours` переименовывается в `estimated_delivery_hours` — расчётное время
  доставки в часах: в колонке хранится длительность пути, а не момент прибытия, как понимает ETA глоссарий.

Краткие описания всех диаграмм этого раздела — [SAD_Diagrams.md](SAD_Diagrams.md).

## 9. Size and Performance (Производительность)

_Не заполнено._

## 10. Quality (Качество)

_Не заполнено._
