-- UC-3: реестр рейсов читается запросом «заявки организации, сначала новые»
-- (Vision 9.3: загрузка реестра ≤ 500 мс). Индексов по caravan_request до UC-3 не было.
create index ix_caravan_request_org_created on caravan_request (organization_id, created_at desc);
