create table request_status_history (
    id          uuid          primary key default gen_random_uuid(),
    request_id  uuid          not null references caravan_request (id),
    from_status varchar(32),
    to_status   varchar(32)   not null,
    actor_role  varchar(32)   not null,
    actor_name  varchar(255),
    reason      varchar(1000),
    occurred_at timestamptz   not null default now()
);

create index ix_request_status_history_request on request_status_history (request_id, occurred_at);

-- Заявки, созданные до UC-2, получают стартовую запись истории на момент создания.
insert into request_status_history (request_id, from_status, to_status, actor_role, actor_name, reason, occurred_at)
select id, null, status, 'DISPATCHER', null, 'Заявка создана (запись восстановлена при внедрении UC-2)', created_at
from caravan_request;

-- Статус заявки ограничен статусной моделью из глоссария.
alter table caravan_request
    add constraint ck_caravan_request_status
    check (status in ('DRAFT', 'READY', 'EN_ROUTE', 'DELAYED', 'DELIVERED', 'CLOSED', 'CANCELLED'));
