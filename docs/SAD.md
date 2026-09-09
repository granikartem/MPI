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
| Class, система целиком | Основные классы и интерфейсы их взаимодействия по слоям | [CLS_LogicalView.puml](diagrams/sad/CLS_LogicalView.puml) | [png](diagrams/out/CLS_LogicalView.png) |
| Activity, UC-7 | Те же шаги в дорожках слоёв приложения | [ACT_UC7_LogicalView.puml](diagrams/sad/ACT_UC7_LogicalView.puml) | [png](diagrams/out/ACT_UC7_LogicalView.png) |
| State Machine, UC-2 | Состояния, сторожевые условия и эффекты переходов в разрезе слоёв | [SM_UC2_LogicalView.puml](diagrams/sad/SM_UC2_LogicalView.puml) | [png](diagrams/out/SM_UC2_LogicalView.png) |
| Sequence, UC-1 | Взаимодействие компонентов по слоям | [SEQ_UC1_LogicalView.puml](diagrams/sad/SEQ_UC1_LogicalView.puml) | [png](diagrams/out/SEQ_UC1_LogicalView.png) |
| Cooperative, UC-32 | Объекты по слоям приложения | [COL_UC32_LogicalView.puml](diagrams/sad/COL_UC32_LogicalView.puml) | [png](diagrams/out/COL_UC32_LogicalView.png) |

Package Diagram, которую матрица раздела 2 требует для этой точки зрения, не построена.

Краткие описания всех диаграмм этого раздела — [SAD_Diagrams.md](SAD_Diagrams.md).

## 6. Process View

_Не заполнено._

## 7. Deployment View

_Не заполнено._

## 8. Implementation View

| Диаграмма | Что показывает | Исходник | Изображение |
|---|---|---|---|
| Class, система целиком | Поля, сигнатуры методов, аннотации JPA и MongoDB, таблицы PostgreSQL и коллекции MongoDB | [CLS_ImplementationView.puml](diagrams/sad/CLS_ImplementationView.puml) | [png](diagrams/out/CLS_ImplementationView.png) |
| Activity, UC-7 | Фактические методы, эндпоинты, формула, пороги и ветвления реализации | [ACT_UC7_ImplementationView.puml](diagrams/sad/ACT_UC7_ImplementationView.puml) | [png](diagrams/out/ACT_UC7_ImplementationView.png) |
| State Machine, UC-2 | Значения `RequestStatus`, реальные вызовы методов и HTTP-контракт | [SM_UC2_ImplementationView.puml](diagrams/sad/SM_UC2_ImplementationView.puml) | [png](diagrams/out/SM_UC2_ImplementationView.png) |
| Sequence, UC-1 | Реальные классы, методы и HTTP-контракт реализации | [SEQ_UC1_ImplementationView.puml](diagrams/sad/SEQ_UC1_ImplementationView.puml) | [png](diagrams/out/SEQ_UC1_ImplementationView.png) |
| Cooperative, UC-32 | Объекты реализации: классы, вызываемые методы и хранилища | [COL_UC32_ImplementationView.puml](diagrams/sad/COL_UC32_ImplementationView.puml) | [png](diagrams/out/COL_UC32_ImplementationView.png) |

Data Base Diagram, которую матрица раздела 2 требует для этой точки зрения, не построена.

Краткие описания всех диаграмм этого раздела — [SAD_Diagrams.md](SAD_Diagrams.md).

## 9. Size and Performance (Производительность)

_Не заполнено._

## 10. Quality (Качество)

_Не заполнено._
