-- Привязка существующих рейсов к организации + читаемый код маршрута.

-- 1. Legacy-организация для уже созданных рейсов (до мультиарендности).
insert into organization (id, tenant_key, name, subscription_tier, status)
values ('dddddddd-0000-0000-0000-000000000001', 'tnt_legacy',
        'Архив (до мультиарендности)', 'BASIC', 'ACTIVE');

-- 2. Все существующие заявки без организации — в legacy; дальше organization_id обязателен.
update caravan_request
set organization_id = 'dddddddd-0000-0000-0000-000000000001'
where organization_id is null;

alter table caravan_request alter column organization_id set not null;

-- 3. Читаемый код маршрута RT-N.
alter table route add column code varchar(32);

with numbered as (
    select id, row_number() over (order by is_template desc, name) as rn
    from route
)
update route r set code = 'RT-' || n.rn
from numbered n
where r.id = n.id;

alter table route alter column code set not null;
create unique index uq_route_code on route (code);

-- 4. Существующие ручные (не-шаблонные) маршруты — к legacy-организации.
update route
set organization_id = 'dddddddd-0000-0000-0000-000000000001'
where organization_id is null and is_template = false;
