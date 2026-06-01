-- Схема для UC-1 (заявка, маршрут) и UC-7 (risk_score хранится в заявке).

create table checkpoint (
    id   uuid         primary key,
    code varchar(64)  not null unique,
    name varchar(255) not null
);

create table route (
    id          uuid         primary key,
    name        varchar(255) not null,
    is_template boolean      not null default true
);

create table route_segment (
    id                 uuid             primary key,
    route_id           uuid             not null references route (id),
    ord                int              not null,
    from_checkpoint_id uuid             not null references checkpoint (id),
    to_checkpoint_id   uuid             not null references checkpoint (id),
    distance_km        double precision not null
);

create table caravan_request (
    id                uuid             primary key default gen_random_uuid(),
    origin            varchar(255)     not null,
    destination       varchar(255)     not null,
    departure_date    date             not null,
    cargo_description varchar(2000),
    cargo_value_caps  integer          not null default 0,
    route_id          uuid             references route (id),
    eta_hours         double precision,
    risk_score        integer,
    risk_status       varchar(16)      not null default 'NA',
    recommendation    varchar(2000),
    status            varchar(32)      not null default 'DRAFT',
    created_at        timestamptz      not null default now()
);
