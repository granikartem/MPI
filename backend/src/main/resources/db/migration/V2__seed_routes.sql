-- Справочник контрольных точек Мохаве и шаблоны маршрутов.

insert into checkpoint (id, code, name) values
('aaaaaaaa-0000-0000-0000-000000000001', 'GOODSPRINGS', 'Goodsprings'),
('aaaaaaaa-0000-0000-0000-000000000002', 'PRIMM',       'Primm'),
('aaaaaaaa-0000-0000-0000-000000000003', 'NIPTON',      'Nipton'),
('aaaaaaaa-0000-0000-0000-000000000004', 'NOVAC',       'Novac'),
('aaaaaaaa-0000-0000-0000-000000000005', 'NEW_VEGAS',   'New Vegas');

insert into route (id, name, is_template) values
('bbbbbbbb-0000-0000-0000-000000000001', 'Goodsprings -> New Vegas (через I-15)', true),
('bbbbbbbb-0000-0000-0000-000000000002', 'Primm -> Novac', true);

-- Маршрут 1: Goodsprings -> Primm -> Nipton -> Novac -> New Vegas
insert into route_segment (id, route_id, ord, from_checkpoint_id, to_checkpoint_id, distance_km) values
('cccccccc-0000-0000-0000-000000000001', 'bbbbbbbb-0000-0000-0000-000000000001', 1, 'aaaaaaaa-0000-0000-0000-000000000001', 'aaaaaaaa-0000-0000-0000-000000000002', 35),
('cccccccc-0000-0000-0000-000000000002', 'bbbbbbbb-0000-0000-0000-000000000001', 2, 'aaaaaaaa-0000-0000-0000-000000000002', 'aaaaaaaa-0000-0000-0000-000000000003', 40),
('cccccccc-0000-0000-0000-000000000003', 'bbbbbbbb-0000-0000-0000-000000000001', 3, 'aaaaaaaa-0000-0000-0000-000000000003', 'aaaaaaaa-0000-0000-0000-000000000004', 55),
('cccccccc-0000-0000-0000-000000000004', 'bbbbbbbb-0000-0000-0000-000000000001', 4, 'aaaaaaaa-0000-0000-0000-000000000004', 'aaaaaaaa-0000-0000-0000-000000000005', 60);

-- Маршрут 2: Primm -> Nipton -> Novac
insert into route_segment (id, route_id, ord, from_checkpoint_id, to_checkpoint_id, distance_km) values
('cccccccc-0000-0000-0000-000000000005', 'bbbbbbbb-0000-0000-0000-000000000002', 1, 'aaaaaaaa-0000-0000-0000-000000000002', 'aaaaaaaa-0000-0000-0000-000000000003', 40),
('cccccccc-0000-0000-0000-000000000006', 'bbbbbbbb-0000-0000-0000-000000000002', 2, 'aaaaaaaa-0000-0000-0000-000000000003', 'aaaaaaaa-0000-0000-0000-000000000004', 55);
