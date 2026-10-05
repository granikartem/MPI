# -*- coding: utf-8 -*-
"""ACT_UC32_ImplementationView: UC-32 «Создать организацию», Activity Diagram (Implementation View).

Содержание перенесено из docs/diagrams/sad/ACT_UC32_ImplementationView.puml.
Раскладка задаётся здесь: колонка — дорожка, строка — шаг потока.

Две находки, не описанные в docs/VisualParadigm.md:

  * явные изломы <Points> VP учитывает только при ОТСУТСТВИИ connectorStyle и только если
    список точек содержит и концы маршрута — первой точкой центр фигуры-источника, последней
    центр фигуры-приёмника. Список одних изломов игнорируется молча: с "Rectlinear" рисуется
    автотрасса (она не обходит препятствия), без connectorStyle — прямая наклонная линия;
  * DecisionNode размером 40x40 своей подписи не показывает, но при размере примерно от 300x60
    текст рисуется ВНУТРИ ромба — как в PlantUML. Поэтому вопросы развилок стоят в самих
    ромбах, а на связях остаются только охранные условия [да]/[нет].
"""
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpgen import Project, Swimlanes, FILL_GREY, FILL_PINK, FILL_NOTE, _q  # noqa: E402

NAME = 'ACT_UC32_ImplementationView'

p = Project(NAME)
d = p.diagram(NAME, 'ActivityDiagram')

# ─── дорожки ─────────────────────────────────────────────────────────
LANES = [('Супер-\nпользователь', 280),
         ('presentation\nOrganizations.tsx\n→ api.ts', 300),
         ('presentation\nOrganizationController', 380),
         ('application\nOrganizationService', 1260),
         ('domain\nOrganization,\nAppUser', 820),
         ('domain\nAuditEvent', 360),
         ('infrastructure\nХранение данных\n(PostgreSQL)', 460),
         ('infrastructure\nЖурнал аудита\n(MongoDB)', 360)]
sw = Swimlanes(d, LANES, x=40, y=40, body_h=3130, header_h=64)

# skinparam swimlaneTitleFontStyle bold из .puml: ElementFont ставится вторым ребёнком фигуры
# (порядок схемы DiagramElementProperties → ElementFont → Line → Caption).
for _hdr in sw.headers:
    _hdr.el.insert(1, ET.Element(_q('ElementFont'), {
        'name': 'Dialog', 'color': 'Cr:0,0,0,255', 'size': '11', 'style': '1'}))

# опорные колонки внутри дорожек
SPINE_X, SPINE_W, SPINE_C = 1020, 400, 1220      # основной столбец дорожки OrganizationService
ALT_X, ALT_W, ALT_C = 1450, 400, 1650            # ветки ошибок (розовые), та же дорожка
ALT2_X, ALT2_W, ALT2_C = 1870, 380, 2060         # альт. поток 6а, та же дорожка
L4A_X, L4A_W, L4A_C = 2280, 370, 2465            # domain, ветка «да»
L4B_X, L4B_W, L4B_C = 2680, 370, 2865            # domain, ветка «нет»

U_C = 180      # центр дорожки «Супер-пользователь»
FE_C = 470     # центр дорожки Organizations.tsx
CT_C = 810     # центр дорожки OrganizationController
AU_C = 3260    # центр дорожки AuditEvent
PG_X, PG_W, PG_C = 3455, 430, 3670               # дорожка PostgreSQL
MG_X, MG_W, MG_C = 3910, 340, 4080               # дорожка MongoDB

nodes = {}
centers = {}


def act(key, text, x, y, w, h, fill=FILL_GREY):
    m = p.model('ActivityAction', name=text, hint='M_' + key)
    s = d.shape('ActivityAction', m, x, y, w, h, name=text, fill=fill, hint='S_' + key)
    nodes[key] = (m, s)
    centers[key] = (x + w // 2, y + h // 2)
    return s


def dec(key, text, cx, y, w, h):
    """Развилка с вопросом ВНУТРИ ромба (при 40x40 подпись не рисуется вовсе)."""
    m = p.model('DecisionNode', name=text, hint='M_' + key)
    s = d.shape('DecisionNode', m, cx - w // 2, y, w, h, name=text, fill=FILL_GREY,
                hint='S_' + key)
    nodes[key] = (m, s)
    centers[key] = (cx, y + h // 2)
    return s


def plain(key, model_type, shape_type, x, y, w, h):
    m = p.model(model_type, hint='M_' + key)
    s = d.shape(shape_type, m, x, y, w, h, caption=False, hint='S_' + key)
    nodes[key] = (m, s)
    centers[key] = (x + w // 2, y + h // 2)
    return s


def ctrl(key, a, b, guard=None, name=None, cap=None, cap_wh=(300, 34), pts=None):
    """Связь. Маршрут достраивается концами из centers — без них VP изломы игнорирует."""
    ma, sa = nodes[a]
    mb, sb = nodes[b]
    fm = p.flow('ControlFlow', ma, mb, name=name, guard=guard, hint='F_' + key)
    route = ([centers[a]] + list(pts) + [centers[b]]) if pts else None
    d.connector('ControlFlow', fm, sa, sb, points=route,
                style=None if route else 'Rectlinear',
                caption_xy=cap, caption_wh=cap_wh, hint='C_' + key)


# ─── узлы ────────────────────────────────────────────────────────────
plain('start', 'InitialNode', 'InitialNode', U_C - 15, 110, 30, 30)
act('a1', 'Заполнить форму организации\nи подтвердить создание', 50, 180, 260, 60)

act('a2', 'createOrganization(body)\nPOST /api/organizations', 330, 290, 280, 60)
act('a3', 'create(CreateOrganization body)\n<<@PostMapping>> @Transactional, 201', 630, 400, 360, 60)

act('a4', 'create(CreateOrganizationCommand)\n<<@Service>> @Transactional', SPINE_X, 510, SPINE_W, 60)
act('a5', 'required(name),\nnormalizeTier(tier) из {BASIC, STANDARD, PRO}', SPINE_X, 600, SPINE_W, 60)

act('a6', 'organizationRepository\n    .findByNameIgnoreCase(name)', PG_X, 710, PG_W, 60)

# --- развилка 1: название свободно? ---
dec('d1', 'название свободно?', SPINE_C, 820, 300, 60)
act('a7', 'generateTenantKey() =\n"tnt_" + 8 символов UUID', SPINE_X, 930, SPINE_W, 60)
act('a8', 'throw new IllegalArgumentException\n«Организация с таким названием уже существует»',
    ALT_X, 930, ALT_W, 60, fill=FILL_PINK)
act('a9', '@ExceptionHandler(IllegalArgumentException)\n→ HTTP 400 ErrorResponse(message)',
    630, 1040, 360, 60, fill=FILL_PINK)
plain('stop1', 'ActivityFinalNode', 'ActivityFinalNode', CT_C - 15, 1140, 30, 30)

# --- развилка 2: назначается ли диспетчер ---
dec('d2', 'command.firstDispatcher() != null?', SPINE_C, 1060, 420, 64)
act('a10', 'userRepository\n    .findByLoginIgnoreCase(login)', PG_X, 1180, PG_W, 60)
act('a14', 'проверять нечего —\nдиспетчер не назначается', ALT2_X, 1190, ALT2_W, 60)

# --- развилка 3: логин уже занят? ---
dec('d3', 'логин уже занят?', SPINE_C, 1310, 300, 60)
act('a13', 'required(fullName), required(login),\nrequired(initialPassword)\n'
           '— validateDispatcher пройдена', SPINE_X, 1420, SPINE_W, 76)
act('a11', 'throw new IllegalArgumentException\n«Пользователь с таким логином уже существует»',
    ALT_X, 1420, ALT_W, 60, fill=FILL_PINK)
act('a12', '@ExceptionHandler(IllegalArgumentException)\n→ HTTP 400 ErrorResponse(message)',
    630, 1546, 360, 60, fill=FILL_PINK)
plain('stop2', 'ActivityFinalNode', 'ActivityFinalNode', CT_C - 15, 1646, 30, 30)

plain('m2', 'MergeNode', 'MergeNode', SPINE_C - 20, 1570, 40, 40)

act('a15', 'organizationRepository.save(new Organization(\n    tenantKey, name, tier, …))\n'
           '→ таблица organization', PG_X, 1690, PG_W, 76)
act('a16', 'Проставить tenantKey — изолированное\nпространство данных: сущности организации\n'
           'ссылаются на organization_id (FR-23, FR-24)', 2390, 1830, 560, 84)

# --- развилка 4: создавать ли учётную запись первого диспетчера ---
dec('d4', 'command.firstDispatcher() != null?', SPINE_C, 1980, 420, 64)
act('a17', 'Вычислить passwordHash = "sha256:" + hex(\n    SHA-256("karavany:" + пароль))',
    L4A_X, 2090, L4A_W, 64)
act('a19', 'Организация создана без учётных записей,\nuserCount = 0 — диспетчера назначит UC-33',
    L4B_X, 2090, L4B_W, 64)
act('a18', 'userRepository.save(new AppUser(organization,\n    fullName, login, passwordHash,\n'
           '    "DISPATCHER", contactChannel))\n→ таблица app_user', PG_X, 2230, PG_W, 90)

plain('m4', 'MergeNode', 'MergeNode', L4B_C - 20, 2370, 40, 40)

act('a20', 'AuditEvent.organizationCreated(orgId,\n    dispatcherId, name, tier, login)',
    3090, 2480, 340, 64)
act('a21', 'auditEventRepository.save(event)\n→ коллекция audit_event   (RL-4)',
    MG_X, 2610, MG_W, 64)
act('a22', 'return new OrganizationProvisioning(\n    organization, dispatcher, userCount)',
    SPINE_X, 2740, SPINE_W, 64)
act('a23', 'OrganizationResponse.from(created)\n→ HTTP 201', 630, 2860, 360, 60)
act('a24', 'Перезагрузить список организаций', 330, 2975, 280, 50)
act('a25', 'Увидеть организацию и учётную запись\nпервого диспетчера', 50, 3080, 260, 64)
plain('stop3', 'ActivityFinalNode', 'ActivityFinalNode', U_C - 15, 3175, 30, 30)

# ─── потоки ──────────────────────────────────────────────────────────
ctrl('f1', 'start', 'a1', pts=[(U_C, 160)])
ctrl('f2', 'a1', 'a2', pts=[(U_C, 270), (FE_C, 270)])
ctrl('f3', 'a2', 'a3', pts=[(FE_C, 380), (CT_C, 380)])
ctrl('f4', 'a3', 'a4', pts=[(CT_C, 490), (SPINE_C, 490)])
ctrl('f5', 'a4', 'a5', pts=[(SPINE_C, 585)])
ctrl('f6', 'a5', 'a6', pts=[(SPINE_C, 685), (PG_C, 685)])
ctrl('f7', 'a6', 'd1', pts=[(PG_C, 800), (SPINE_C, 800)])

ctrl('f8', 'd1', 'a7', guard='да', cap=(1000, 886), cap_wh=(200, 34),
     pts=[(SPINE_C, 905)])
ctrl('f9', 'd1', 'a8', guard='нет — альт. поток 4а', cap=(1370, 810), cap_wh=(300, 34),
     pts=[(1370, 850), (ALT_C, 850)])
ctrl('f10', 'a8', 'a9', pts=[(ALT_C, 1020), (CT_C, 1020)])
ctrl('f11', 'a9', 'stop1', pts=[(CT_C, 1120)])

ctrl('f12', 'a7', 'd2', pts=[(SPINE_C, 1025)])
ctrl('f13', 'd2', 'a10', guard='да — проверить диспетчера', cap=(1450, 1052), cap_wh=(340, 34),
     pts=[(1430, 1092), (PG_C, 1092)])
ctrl('f14', 'd2', 'a14', guard='нет — альт. поток 6а', cap=(1700, 1120), cap_wh=(300, 34),
     pts=[(SPINE_C, 1158), (ALT2_C, 1158)])
ctrl('f15', 'a10', 'd3', pts=[(PG_C, 1280), (SPINE_C, 1280)])

ctrl('f16', 'd3', 'a13', guard='нет', cap=(1000, 1376), cap_wh=(200, 34),
     pts=[(SPINE_C, 1395)])
ctrl('f17', 'd3', 'a11', guard='да', cap=(1400, 1300), cap_wh=(200, 34),
     pts=[(1370, 1340), (ALT_C, 1340)])
ctrl('f18', 'a11', 'a12', pts=[(ALT_C, 1526), (CT_C, 1526)])
ctrl('f19', 'a12', 'stop2', pts=[(CT_C, 1626)])

ctrl('f20', 'a13', 'm2', pts=[(SPINE_C, 1540)])
ctrl('f21', 'a14', 'm2', pts=[(ALT2_C, 1590), (SPINE_C + 20, 1590)])
ctrl('f22', 'm2', 'a15', pts=[(SPINE_C, 1650), (PG_C, 1650)])
ctrl('f23', 'a15', 'a16', pts=[(PG_C, 1800), (2670, 1800)])
ctrl('f24', 'a16', 'd4', pts=[(2670, 1950), (SPINE_C, 1950)])

ctrl('f25', 'd4', 'a17', guard='да — основной поток', cap=(1500, 2020), cap_wh=(300, 34),
     pts=[(SPINE_C, 2060), (L4A_C, 2060)])
ctrl('f26', 'd4', 'a19', guard='нет — альт. поток 6а', cap=(2550, 1970), cap_wh=(300, 34),
     pts=[(1430, 2012), (L4B_C, 2012)])
ctrl('f27', 'a17', 'a18', pts=[(L4A_C, 2190), (PG_C, 2190)])
ctrl('f28', 'a19', 'm4', pts=[(L4B_C, 2260)])
ctrl('f29', 'a18', 'm4', pts=[(PG_C, 2390), (L4B_C + 20, 2390)])

ctrl('f30', 'm4', 'a20', pts=[(L4B_C, 2450), (AU_C, 2450)])
ctrl('f31', 'a20', 'a21', pts=[(AU_C, 2580), (MG_C, 2580)])
ctrl('f32', 'a21', 'a22', pts=[(MG_C, 2710), (SPINE_C, 2710)])
ctrl('f33', 'a22', 'a23', pts=[(SPINE_C, 2830), (CT_C, 2830)])
ctrl('f34', 'a23', 'a24', pts=[(CT_C, 2945), (FE_C, 2945)])
ctrl('f35', 'a24', 'a25', pts=[(FE_C, 3050), (U_C, 3050)])
ctrl('f36', 'a25', 'stop3', pts=[(U_C, 3160)])

# ─── заметки ─────────────────────────────────────────────────────────
NOTE_X = 4330
NOTE_W = 430


def note(key, text, y, h, anchor_to=None):
    m = p.note(text, hint='M_' + key)
    s = d.shape('NOTE', m, NOTE_X, y, NOTE_W, h, caption=False, fill=FILL_NOTE, hint='S_' + key)
    nodes[key] = (m, s)
    if anchor_to:
        am, asx = nodes[anchor_to]
        an = p.flow('Anchor', m, am, hint='A_' + key)
        d.connector('Anchor', an, s, asx, style=None, hint='CA_' + key)


# floating note из .puml — без привязки, как в оригинале
note('idx', 'Уникальность названия и логина продублирована\n'
            'индексами uq_organization_name_ci\n'
            'и uq_app_user_login_ci: их нарушение даёт\n'
            'DataIntegrityViolationException → HTTP 400.',
     300, 92)

note('legend', 'Обозначения\n'
               '• дорожки — те же слои и компоненты, что в Logical View\n'
               '  (PKG_LogicalView); в заголовках указаны реализующие\n'
               '  их классы и хранилища\n'
               '• розовым выделены альт. поток 4а и обработка ошибок\n'
               '\n'
               'Требования (docs/SRS.md)\n'
               '• FR-23, FR-24, FR-25, RL-4\n'
               '• DC-4 (PostgreSQL), DC-5 (MongoDB), DC-6 (слои)',
     452, 168)

# заливка — последним ребёнком каждой фигуры
for _m, _s in nodes.values():
    d.finish_fill(_s)
d.finish_fill(sw.container)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', NAME + '.xml')
os.makedirs(os.path.dirname(out), exist_ok=True)
p.write(out)
print(out)
