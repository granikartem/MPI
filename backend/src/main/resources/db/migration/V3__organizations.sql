create table organization (
    id                uuid          primary key default gen_random_uuid(),
    tenant_key        varchar(64)   not null unique,
    name              varchar(255)  not null,
    subscription_tier varchar(32)   not null,
    legal_address     varchar(1000),
    primary_contact   varchar(255),
    contact_channel   varchar(255),
    region            varchar(255),
    status            varchar(32)   not null default 'ACTIVE',
    created_at        timestamptz   not null default now()
);

create unique index uq_organization_name_ci on organization (lower(name));

create table app_user (
    id              uuid          primary key default gen_random_uuid(),
    organization_id uuid          not null references organization (id),
    full_name       varchar(255)  not null,
    login           varchar(128)  not null,
    password_hash   varchar(255)  not null,
    role            varchar(32)   not null,
    contact_channel varchar(255),
    active          boolean       not null default true,
    created_at      timestamptz   not null default now()
);

create unique index uq_app_user_login_ci on app_user (lower(login));

alter table route
    add column organization_id uuid references organization (id);

alter table caravan_request
    add column organization_id uuid references organization (id);
