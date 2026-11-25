# Диаграммы прецедентов ИС «Караваны»

Каталог содержит все диаграммы прецедентов проекта. Исходники — PlantUML (`*.puml`),
отрисованные картинки — в [`../out/`](../out/).

Полные текстовые сценарии прецедентов — в [CoreUseCases.md](../../CoreUseCases.md),
краткий перечень — в [UseCases.md](../../UseCases.md).

## Общая диаграмма

| Диаграмма | Файл | Исходник | Картинка |
|---|---|---|---|
| Полная диаграмма прецедентов ИС «Караваны» — UC-1…UC-34 | UC_0_General | [PlantUML](UC_0_General.puml) | [PNG](../out/UC_0_General.png) |

## Тематические диаграммы

Группируют прецеденты по предметным областям — удобны для обзора,
детализация каждого прецедента вынесена в отдельные диаграммы ниже.

| Диаграмма | Файл | Исходник | Картинка |
|---|---|---|---|
| Управление заявкой и рейсом | UC_1_Request | [PlantUML](UC_1_Request.puml) | [PNG](../out/UC_1_Request.png) |
| Планирование маршрута и оценка рисков | UC_2_Route | [PlantUML](UC_2_Route.puml) | [PNG](../out/UC_2_Route.png) |
| Формирование команды | UC_3_Team | [PlantUML](UC_3_Team.puml) | [PNG](../out/UC_3_Team.png) |
| Груз и манифест | UC_4_Cargo | [PlantUML](UC_4_Cargo.puml) | [PNG](../out/UC_4_Cargo.png) |
| Полевые операции | UC_5_Field | [PlantUML](UC_5_Field.puml) | [PNG](../out/UC_5_Field.png) |
| Финансы и интеграции | UC_6_Finance | [PlantUML](UC_6_Finance.puml) | [PNG](../out/UC_6_Finance.png) |
| Управление пользователями | UC_7_Users | [PlantUML](UC_7_Users.puml) | [PNG](../out/UC_7_Users.png) |
| Управление организациями | UC_8_Orgs | [PlantUML](UC_8_Orgs.puml) | [PNG](../out/UC_8_Orgs.png) |

## Подробные диаграммы прецедентов (UC-1…UC-34)

Для каждого прецедента: основной и альтернативные потоки, связи
`«include»`/`«extend»`, границы системы и внешние интеграции.
Эти диаграммы встроены в [CoreUseCases.md](../../CoreUseCases.md).

| Диаграмма | Файл | Исходник | Картинка |
|---|---|---|---|
| UC-1. Создать заявку на перевозку | UC_1_Detail | [PlantUML](UC_1_Detail.puml) | [PNG](../out/UC_1_Detail.png) |
| UC-2. Управлять статусами заявки | UC_2_Detail | [PlantUML](UC_2_Detail.puml) | [PNG](../out/UC_2_Detail.png) |
| UC-3. Просмотреть реестр рейсов | UC_3_Detail | [PlantUML](UC_3_Detail.puml) | [PNG](../out/UC_3_Detail.png) |
| UC-4. Поиск и фильтрация завершённых рейсов | UC_4_Detail | [PlantUML](UC_4_Detail.puml) | [PNG](../out/UC_4_Detail.png) |
| UC-5. Выбрать/спланировать маршрут | UC_5_Detail | [PlantUML](UC_5_Detail.puml) | [PNG](../out/UC_5_Detail.png) |
| UC-6. Рассчитать ETA | UC_6_Detail | [PlantUML](UC_6_Detail.puml) | [PNG](../out/UC_6_Detail.png) |
| UC-7. Рассчитать risk_score | UC_7_Detail | [PlantUML](UC_7_Detail.puml) | [PNG](../out/UC_7_Detail.png) |
| UC-8. Получить рекомендацию по охране и припасам | UC_8_Detail | [PlantUML](UC_8_Detail.puml) | [PNG](../out/UC_8_Detail.png) |
| UC-9. Назначить сотрудников на роли рейса | UC_9_Detail | [PlantUML](UC_9_Detail.puml) | [PNG](../out/UC_9_Detail.png) |
| UC-10. Просмотреть доступных сотрудников | UC_10_Detail | [PlantUML](UC_10_Detail.puml) | [PNG](../out/UC_10_Detail.png) |
| UC-11. Создать груз-манифест | UC_11_Detail | [PlantUML](UC_11_Detail.puml) | [PNG](../out/UC_11_Detail.png) |
| UC-12. Указать ценность груза | UC_12_Detail | [PlantUML](UC_12_Detail.puml) | [PNG](../out/UC_12_Detail.png) |
| UC-13. Зарезервировать припасы | UC_13_Detail | [PlantUML](UC_13_Detail.puml) | [PNG](../out/UC_13_Detail.png) |
| UC-14. Подтвердить доставку груза (с пломбой) | UC_14_Detail | [PlantUML](UC_14_Detail.puml) | [PNG](../out/UC_14_Detail.png) |
| UC-15. Выполнить сверку манифеста при приёмке | UC_15_Detail | [PlantUML](UC_15_Detail.puml) | [PNG](../out/UC_15_Detail.png) |
| UC-16. Зафиксировать прохождение этапа рейса | UC_16_Detail | [PlantUML](UC_16_Detail.puml) | [PNG](../out/UC_16_Detail.png) |
| UC-17. Отметить прохождение контрольной точки | UC_17_Detail | [PlantUML](UC_17_Detail.puml) | [PNG](../out/UC_17_Detail.png) |
| UC-18. Отметить прохождение КПП (с пошлиной) | UC_18_Detail | [PlantUML](UC_18_Detail.puml) | [PNG](../out/UC_18_Detail.png) |
| UC-19. Сообщить об инциденте в рейсе | UC_19_Detail | [PlantUML](UC_19_Detail.puml) | [PNG](../out/UC_19_Detail.png) |
| UC-20. Инициировать RecoveryRequest | UC_20_Detail | [PlantUML](UC_20_Detail.puml) | [PNG](../out/UC_20_Detail.png) |
| UC-21. Сформировать финансовый отчёт по рейсу | UC_21_Detail | [PlantUML](UC_21_Detail.puml) | [PNG](../out/UC_21_Detail.png) |
| UC-22. Экспортировать отчёт на голотейп | UC_22_Detail | [PlantUML](UC_22_Detail.puml) | [PNG](../out/UC_22_Detail.png) |
| UC-23. Получить данные об угрозах | UC_23_Detail | [PlantUML](UC_23_Detail.puml) | [PNG](../out/UC_23_Detail.png) |
| UC-24. Получить данные о КПП и пошлинах | UC_24_Detail | [PlantUML](UC_24_Detail.puml) | [PNG](../out/UC_24_Detail.png) |
| UC-25. Аутентификация | UC_25_Detail | [PlantUML](UC_25_Detail.puml) | [PNG](../out/UC_25_Detail.png) |
| UC-26. Создать учётную запись пользователя | UC_26_Detail | [PlantUML](UC_26_Detail.puml) | [PNG](../out/UC_26_Detail.png) |
| UC-27. Изменить роль пользователя | UC_27_Detail | [PlantUML](UC_27_Detail.puml) | [PNG](../out/UC_27_Detail.png) |
| UC-28. Деактивировать учётную запись | UC_28_Detail | [PlantUML](UC_28_Detail.puml) | [PNG](../out/UC_28_Detail.png) |
| UC-29. Редактировать свои учётные данные | UC_29_Detail | [PlantUML](UC_29_Detail.puml) | [PNG](../out/UC_29_Detail.png) |
| UC-30. Сбросить учётные данные пользователя | UC_30_Detail | [PlantUML](UC_30_Detail.puml) | [PNG](../out/UC_30_Detail.png) |
| UC-31. Назначить/изменить ставку сотрудника | UC_31_Detail | [PlantUML](UC_31_Detail.puml) | [PNG](../out/UC_31_Detail.png) |
| UC-32. Создать организацию | UC_32_Detail | [PlantUML](UC_32_Detail.puml) | [PNG](../out/UC_32_Detail.png) |
| UC-33. Назначить первого диспетчера организации | UC_33_Detail | [PlantUML](UC_33_Detail.puml) | [PNG](../out/UC_33_Detail.png) |
| UC-34. Управлять подписками | UC_34_Detail | [PlantUML](UC_34_Detail.puml) | [PNG](../out/UC_34_Detail.png) |

## Диаграммы деятельности

Пошаговые потоки тех же прецедентов. В основной документ не встраиваются,
хранятся как рабочий материал.

| Диаграмма | Файл | Исходник | Картинка |
|---|---|---|---|
| UC-1. Создать заявку на перевозку | UC_1_Activity | [PlantUML](UC_1_Activity.puml) | [PNG](../out/UC_1_Activity.png) |
| UC-2. Управлять статусами заявки | UC_2_Activity | [PlantUML](UC_2_Activity.puml) | [PNG](../out/UC_2_Activity.png) |
| UC-3. Просмотреть реестр рейсов | UC_3_Activity | [PlantUML](UC_3_Activity.puml) | [PNG](../out/UC_3_Activity.png) |
| UC-4. Поиск и фильтрация завершённых рейсов | UC_4_Activity | [PlantUML](UC_4_Activity.puml) | [PNG](../out/UC_4_Activity.png) |
| UC-5. Выбрать/спланировать маршрут | UC_5_Activity | [PlantUML](UC_5_Activity.puml) | [PNG](../out/UC_5_Activity.png) |
| UC-6. Рассчитать ETA | UC_6_Activity | [PlantUML](UC_6_Activity.puml) | [PNG](../out/UC_6_Activity.png) |
| UC-7. Рассчитать risk_score | UC_7_Activity | [PlantUML](UC_7_Activity.puml) | [PNG](../out/UC_7_Activity.png) |
| UC-8. Получить рекомендацию по охране и припасам | UC_8_Activity | [PlantUML](UC_8_Activity.puml) | [PNG](../out/UC_8_Activity.png) |
| UC-9. Назначить сотрудников на роли рейса | UC_9_Activity | [PlantUML](UC_9_Activity.puml) | [PNG](../out/UC_9_Activity.png) |
| UC-10. Просмотреть доступных сотрудников | UC_10_Activity | [PlantUML](UC_10_Activity.puml) | [PNG](../out/UC_10_Activity.png) |
| UC-11. Создать груз-манифест | UC_11_Activity | [PlantUML](UC_11_Activity.puml) | [PNG](../out/UC_11_Activity.png) |
| UC-12. Указать ценность груза | UC_12_Activity | [PlantUML](UC_12_Activity.puml) | [PNG](../out/UC_12_Activity.png) |
| UC-13. Зарезервировать припасы | UC_13_Activity | [PlantUML](UC_13_Activity.puml) | [PNG](../out/UC_13_Activity.png) |
| UC-14. Подтвердить доставку груза (с пломбой) | UC_14_Activity | [PlantUML](UC_14_Activity.puml) | [PNG](../out/UC_14_Activity.png) |
| UC-15. Выполнить сверку манифеста при приёмке | UC_15_Activity | [PlantUML](UC_15_Activity.puml) | [PNG](../out/UC_15_Activity.png) |
| UC-16. Зафиксировать прохождение этапа рейса | UC_16_Activity | [PlantUML](UC_16_Activity.puml) | [PNG](../out/UC_16_Activity.png) |
| UC-17. Отметить прохождение контрольной точки | UC_17_Activity | [PlantUML](UC_17_Activity.puml) | [PNG](../out/UC_17_Activity.png) |
| UC-18. Отметить прохождение КПП (с пошлиной) | UC_18_Activity | [PlantUML](UC_18_Activity.puml) | [PNG](../out/UC_18_Activity.png) |
| UC-19. Сообщить об инциденте в рейсе | UC_19_Activity | [PlantUML](UC_19_Activity.puml) | [PNG](../out/UC_19_Activity.png) |
| UC-20. Инициировать RecoveryRequest | UC_20_Activity | [PlantUML](UC_20_Activity.puml) | [PNG](../out/UC_20_Activity.png) |
| UC-21. Сформировать финансовый отчёт по рейсу | UC_21_Activity | [PlantUML](UC_21_Activity.puml) | [PNG](../out/UC_21_Activity.png) |
| UC-22. Экспортировать отчёт на голотейп | UC_22_Activity | [PlantUML](UC_22_Activity.puml) | [PNG](../out/UC_22_Activity.png) |
| UC-23. Получить данные об угрозах | UC_23_Activity | [PlantUML](UC_23_Activity.puml) | [PNG](../out/UC_23_Activity.png) |
| UC-24. Получить данные о КПП и пошлинах | UC_24_Activity | [PlantUML](UC_24_Activity.puml) | [PNG](../out/UC_24_Activity.png) |
| UC-25. Аутентификация | UC_25_Activity | [PlantUML](UC_25_Activity.puml) | [PNG](../out/UC_25_Activity.png) |
| UC-26. Создать учётную запись пользователя | UC_26_Activity | [PlantUML](UC_26_Activity.puml) | [PNG](../out/UC_26_Activity.png) |
| UC-27. Изменить роль пользователя | UC_27_Activity | [PlantUML](UC_27_Activity.puml) | [PNG](../out/UC_27_Activity.png) |
| UC-28. Деактивировать учётную запись | UC_28_Activity | [PlantUML](UC_28_Activity.puml) | [PNG](../out/UC_28_Activity.png) |
| UC-29. Редактировать свои учётные данные | UC_29_Activity | [PlantUML](UC_29_Activity.puml) | [PNG](../out/UC_29_Activity.png) |
| UC-30. Сбросить учётные данные пользователя | UC_30_Activity | [PlantUML](UC_30_Activity.puml) | [PNG](../out/UC_30_Activity.png) |
| UC-31. Назначить/изменить ставку сотрудника | UC_31_Activity | [PlantUML](UC_31_Activity.puml) | [PNG](../out/UC_31_Activity.png) |
| UC-32. Создать организацию | UC_32_Activity | [PlantUML](UC_32_Activity.puml) | [PNG](../out/UC_32_Activity.png) |
| UC-33. Назначить первого диспетчера организации | UC_33_Activity | [PlantUML](UC_33_Activity.puml) | [PNG](../out/UC_33_Activity.png) |
| UC-34. Управлять подписками | UC_34_Activity | [PlantUML](UC_34_Activity.puml) | [PNG](../out/UC_34_Activity.png) |

## Прочее

| Диаграмма | Файл | Исходник | Картинка |
|---|---|---|---|
| UC-2. Статусная модель заявки на перевозку | UC_2_Status | [PlantUML](UC_2_Status.puml) | [PNG](../out/UC_2_Status.png) |
| UC-3. Просмотреть реестр рейсов | UC_3_Registry | [PlantUML](UC_3_Registry.puml) | [PNG](../out/UC_3_Registry.png) |
