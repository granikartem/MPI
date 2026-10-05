# -*- coding: utf-8 -*-
"""CLS_ImplementationView: диаграмма классов уровня реализации.

Содержание целиком берётся из docs/diagrams/sad/CLS_ImplementationView.puml —
классы, члены, стереотипы, цвета и связи разбираются из исходника, поэтому при
переносе ничего не теряется. Здесь задаётся то, чего в PlantUML нет: раскладка
по колонкам, маршруты линий и положение подписей.

    колонка 1  frontend/src, заметки и легенда
    колонка 2  com.karavany.request (web → service → domain → repository)
    колонка 3  com.karavany.risk, внешние системы
    колонка 4  com.karavany.organization, com.karavany.audit

Главная тонкость формата. Список <Points> у коннектора действует только тогда,
когда ПЕРВАЯ точка лежит на границе источника, а ПОСЛЕДНЯЯ — на границе
приёмника. Если задать одни лишь изломы, Visual Paradigm молча выбрасывает их
и прокладывает маршрут сам: вертикаль по оси источника до уровня центра
приёмника, затем горизонталь — прямо сквозь всё, что попадётся.

Поэтому каждая связь, которой тесно, получает явный маршрут по коридору:
у пакета слева оставлено поле с дорожками, между колонками — зазор, сверху —
полоса y = Y_TOP. Модуль сам проверяет геометрию: route_report() печатает
связи, чьи отрезки пересекают чужие фигуры, и подписи, налезающие на фигуры.
"""
import io
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xml.etree.ElementTree as ET  # noqa: E402
from PIL import ImageFont  # noqa: E402
from vpgen import (Project, FILL_GREY, FILL_LILAC, FILL_NOTE, FILL_WHITE, _q)  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
PUML = os.path.normpath(os.path.join(HERE, '..', 'sad', 'CLS_ImplementationView.puml'))
NAME = 'CLS_ImplementationView'

# ═══════════════════════════════════════════════════════════════════════
# 1. Разбор PlantUML
# ═══════════════════════════════════════════════════════════════════════

VIS = {'+': 'public', '-': 'private', '#': 'protected', '~': 'package'}


class Cls(object):
    __slots__ = ('alias', 'title', 'stereo', 'fill', 'members', 'model', 'shape',
                 'w', 'h', 'x', 'y')

    def __init__(self, alias, title, stereo, fill):
        self.alias, self.title, self.stereo, self.fill = alias, title, stereo, fill
        self.members = []
        self.model = self.shape = None
        self.w = self.h = self.x = self.y = 0


def _split_op(line):
    """('имя', [(параметр, тип)], 'возврат') либо None, если строка не сигнатура."""
    i = line.find('(')
    if i < 0:
        return None
    head = line[:i].strip()
    if not re.fullmatch(r'[A-Za-zА-Яа-яЁё_][\w]*', head):
        return None
    depth, j = 0, i
    while j < len(line):
        if line[j] == '(':
            depth += 1
        elif line[j] == ')':
            depth -= 1
            if depth == 0:
                break
        j += 1
    if depth != 0:
        return None
    args, rest = line[i + 1:j].strip(), line[j + 1:].strip()
    if rest and not rest.startswith(':'):
        return None
    ret = rest[1:].strip() if rest.startswith(':') else None
    params = []
    for a in (x.strip() for x in args.split(',')) if args else ():
        if ' : ' in a:
            pn, pt = a.split(' : ', 1)
            params.append((pn.strip(), pt.strip()))
        else:
            params.append((a, None))
    return head, params, ret


def parse_member(raw):
    line = raw.strip()
    if (line.startswith('..') and line.endswith('..')) or \
       (line.startswith('--') and line.endswith('--')):
        return ('attr', 'Unspecified', line, None, False)
    if line[:1] not in VIS:
        # литерал перечисления: поле без значка видимости — так сохраняется
        # порядок строк исходника (отсек литералов VP рисует после методов)
        return ('attr', 'Unspecified', line, None, False)
    vis, line = VIS[line[0]], line[1:].strip()
    static = False
    if line.startswith('{static}'):
        static, line = True, line[8:].strip()
    op = _split_op(line)
    if op:
        return ('op', vis, op[0], op[1], op[2], static)
    if ' : ' in line:
        n, t = line.split(' : ', 1)
        return ('attr', vis, n.strip(), t.strip(), static)
    return ('attr', vis, line, None, static)


RE_PKG = re.compile(r'^package\s+(?:"([^"]+)"|(\S+))(?:\s+as\s+\w+)?\s*(#\w+)?\s*\{')
RE_CLS = re.compile(r'^(class|enum|interface)\s+(?:"([^"]+)"\s+as\s+(\w+)|(\w+))'
                    r'(?:\s+<<([^>]+)>>)?\s*(#\w+)?\s*\{')
RE_REL = re.compile(r'^(?:"([^"]+)"|(\w+))\s*(?:"([^"]*)"\s*)?'
                    r'(-->|\.\.>|\.\.|o--|\*--|\+--)'
                    r'\s*(?:"([^"]*)"\s*)?(?:"([^"]+)"|(\w+))\s*(?::\s*(.*))?$')

COLORS = {'#F5F5F5': FILL_GREY, '#EDE7F6': FILL_LILAC, '#FDFDFD': FILL_WHITE}

classes, order, rels = {}, [], []
with io.open(PUML, encoding='utf-8') as fh:
    lines = fh.read().split('\n')

cur, i = None, 0
while i < len(lines):
    line = lines[i].strip()
    i += 1
    if not line or line.startswith("'") or line.startswith('@'):
        continue
    if cur is not None:
        if line == '}':
            cur = None
        else:
            cur.members.append(parse_member(line))
        continue
    if line.startswith('note ') or line.startswith('legend'):
        stop = 'end note' if line.startswith('note ') else 'endlegend'
        while i < len(lines) and lines[i].strip() != stop:
            i += 1
        i += 1
        continue
    m = RE_CLS.match(line)
    if m:
        alias = m.group(3) or m.group(4)
        cur = Cls(alias, m.group(2) or m.group(4), m.group(5),
                  COLORS.get((m.group(6) or '').upper(), FILL_GREY))
        classes[alias] = cur
        order.append(alias)
        continue
    if RE_PKG.match(line) or line == '}' or '[hidden]' in line:
        continue
    m = RE_REL.match(line)
    if m:
        a, b = m.group(1) or m.group(2), m.group(6) or m.group(7)
        if a in classes or b in classes:
            rels.append((a, m.group(3), m.group(4), m.group(5), b, m.group(8)))

assert len(classes) == 68, len(classes)
assert len(rels) == 78, len(rels)

# ═══════════════════════════════════════════════════════════════════════
# 2. Габариты фигур (шрифт VP ≈ Arial 11, шаг строки 15 px)
# ═══════════════════════════════════════════════════════════════════════

F_PLAIN = ImageFont.truetype('arial.ttf', 11)
F_BOLD = ImageFont.truetype('arialbd.ttf', 11)
LINE_H, HDR_NAME, HDR_STEREO, PAD_COMP = 15, 21, 15, 9
VIS_CH = {'public': '+', 'private': '-', 'protected': '#', 'package': '~', 'Unspecified': ''}


def tw(text, bold=False):
    return int(max((F_BOLD if bold else F_PLAIN).getlength(s)
                   for s in str(text).split('\n')) * 1.06)


def member_text(m):
    if m[0] == 'attr':
        _k, vis, name, typ, _st = m
        return VIS_CH[vis] + name + (' : ' + typ if typ else '')
    _k, vis, name, params, ret, _st = m
    args = ', '.join(pn + (' : ' + pt if pt else '') for pn, pt in params)
    return VIS_CH[vis] + name + '(' + args + ')' + (' : ' + ret if ret else '')


# Visual Paradigm всегда рисует отсек атрибутов целиком, а следом — отсек
# операций, и порядок строк исходника ломается у классов, где за сигнатурой
# снова идёт строка-пояснение («.. плюс геттеры всех полей ..» у сущностей,
# чередование у api.ts). Такие классы собираются «плоско»: каждая строка —
# член-атрибут с готовым текстом, поэтому порядок .puml сохраняется дословно.
FLAT = set()
for _a, _c in classes.items():
    _k = [m[0] for m in _c.members]
    if any(_k[i] == 'attr' and 'op' in _k[:i] for i in range(len(_k))):
        FLAT.add(_a)


def flat_name(m):
    """Строка .puml без значка видимости — его VP подставит сам."""
    txt = member_text(m)
    ch = VIS_CH[m[1]]
    return txt[len(ch):] if ch else txt


for c in classes.values():
    if c.alias in FLAT:
        attrs, ops = c.members, []
    else:
        attrs = [m for m in c.members if m[0] == 'attr']
        ops = [m for m in c.members if m[0] == 'op']
    w = tw(c.title, bold=True)
    if c.stereo:
        w = max(w, tw('<<%s>>' % c.stereo))
    for m in c.members:
        w = max(w, tw(member_text(m)))
    h = HDR_NAME + (HDR_STEREO if c.stereo else 0)
    h += (LINE_H * len(attrs) + PAD_COMP) if attrs else 0
    h += (LINE_H * len(ops) + PAD_COMP) if ops else 0
    h += 0 if (attrs or ops) else 24
    c.w, c.h = w + 20, h + 6

# ═══════════════════════════════════════════════════════════════════════
# 3. Раскладка
# ═══════════════════════════════════════════════════════════════════════

PKG_PAD, PKG_HDR, GAP_V, GAP_H = 16, 46, 44, 46
PKGPOS, PKGORDER, NOTE_BOX = {}, [], {}


def C(alias, dx=0, dy=0):
    return ('cls', classes[alias], dx, dy)


def Col(*kids, **kw):
    return ('col', list(kids), kw.get('gap', GAP_V), kw.get('align', 'center'))


def Row(*kids, **kw):
    return ('row', list(kids), kw.get('gap', GAP_H), kw.get('align', 'top'))


def Pkg(name, kid, lpad=PKG_PAD, rpad=PKG_PAD):
    return ('pkg', name, kid, lpad, rpad)


def size(n):
    t = n[0]
    if t == 'cls':
        return n[1].w, n[1].h
    if t in ('col', 'row'):
        sz = [size(k) for k in n[1]]
        gap = n[2] * (len(sz) - 1)
        if t == 'col':
            return max(s[0] for s in sz), sum(s[1] for s in sz) + gap
        return sum(s[0] for s in sz) + gap, max(s[1] for s in sz)
    w, h = size(n[2])
    return w + n[3] + n[4], h + PKG_HDR + PKG_PAD


def place(n, x, y):
    w, h = size(n)
    t = n[0]
    if t == 'cls':
        c = n[1]
        c.x, c.y = x + n[2], y + n[3]
        return
    if t == 'col':
        ty = y
        for k in n[1]:
            kw, kh = size(k)
            place(k, x + (0 if n[3] == 'left' else (w - kw) // 2), ty)
            ty += kh + n[2]
        return
    if t == 'row':
        tx = x
        for k in n[1]:
            kw, kh = size(k)
            place(k, tx, y + (0 if n[3] == 'top' else (h - kh) // 2))
            tx += kw + n[2]
        return
    PKGPOS[id(n)] = (x, y, w, h)
    PKGORDER.append(n[1])
    place(n[2], x + n[3], y + PKG_HDR)


def geo(a):
    if a in classes:
        c = classes[a]
        return (c.x, c.y, c.w, c.h)
    return NOTE_BOX[a]


def cx(a):
    x, _y, w, _h = geo(a)
    return x + w // 2


def cy(a):
    _x, y, _w, h = geo(a)
    return y + h // 2


FL_LPAD, REQ_LPAD, ORG_LPAD = 180, 300, 110

FRONT = Pkg('frontend/src', Col(
    Pkg('корневые модули', Col(C('MAIN'), Row(C('APP'), C('ROUTER')))),
    Pkg('pages', Row(C('LANDING'), C('CONSOLE'), C('ORGPAGE'))),
    Pkg('components', Col(
        Row(C('FORM'), C('REG')),
        Row(C('FILTERS'), C('SUMMARY'), C('LIST')),
        Row(C('SMODAL'), C('SBADGE'), C('RBADGE'), C('RMODAL')), gap=78)),
    Pkg('api', C('API'))), lpad=FL_LPAD, rpad=96)

REQUEST = Pkg('com.karavany.request', Col(
    Pkg('web', Row(
        Col(C('RequestController'), C('RequestStatusController'),
            C('RequestRegistryController')),
        Col(C('CreateRequest'), C('SegmentInput'), C('ChangeStatusRequest')))),
    Pkg('service', Row(
        Col(C('RequestService'), C('RequestStatusService'), C('RequestRegistryService')),
        Col(C('SegmentSpec'), C('AvailableTransition'), C('RegistryView'),
            C('EtaService'), C('RequestReadinessGuard'), C('StatusTransitionException')))),
    Pkg('domain', Row(
        Col(C('RequestStatus'), C('ActorRole'), C('RequestStatusMachine'),
            C('RequestRegistry')),
        Col(C('Transition'), C('Summary'), C('RegistryScope'), C('RegistrySort'),
            C('AttentionFlag')),
        Col(C('CaravanRequest'), C('RequestStatusHistory'), C('RegistryEntry')))),
    Pkg('repository', Row(C('CaravanRequestRepository'),
                          C('RequestStatusHistoryRepository')))), lpad=REQ_LPAD)

RISK = Pkg('com.karavany.risk', Col(
    Row(Col(C('RiskService'), C('RiskAssessment'), C('WastelandIntelClient'), C('RiskLevel')),
        Col(C('RiskResult'), C('SegmentRisk'), C('AssessmentSegment'), C('ThreatReport'),
            C('SegmentThreat'), C('RiskAssessmentRepository')))), lpad=70)

EXT = Pkg('внешние системы', C('WI'), lpad=70)

ORG = Pkg('com.karavany.organization', Col(
    Pkg('web', Row(C('OrganizationController'), C('CreateOrganization'))),
    Pkg('service', Row(C('OrganizationService'),
                       Col(C('CreateOrgCmd'), C('FirstDispCmd'), C('Provisioning')))),
    Pkg('domain', Row(C('Organization'), C('AppUser'))),
    Pkg('repository', Row(C('OrganizationRepository'), C('AppUserRepository')))),
    lpad=ORG_LPAD)

AUDIT = Pkg('com.karavany.audit', Row(C('AuditEvent'), C('AuditEventRepository')),
            lpad=ORG_LPAD)

Y_TOP = 28
X0, Y0 = 60, 182
GAP_COL = 150
LEG_W, MACH_W = 530, 436

place(FRONT, X0, Y0)
FR_W, FR_H = size(FRONT)
COL1_W = max(FR_W, LEG_W + 40 + MACH_W)

X1 = X0 + COL1_W + GAP_COL
place(REQUEST, X1, Y0)
RQ_W, RQ_H = size(REQUEST)

X2 = X1 + RQ_W + GAP_COL
place(RISK, X2, Y0)
RK_W, RK_H = size(RISK)
RISK_NOTE_Y = Y0 + RK_H + 56
EXT_Y = RISK_NOTE_Y + 200
place(EXT, X2, EXT_Y)
EX_W, EX_H = size(EXT)
ORG_Y = EXT_Y + EX_H + 86
place(ORG, X2, ORG_Y)
OR_W, OR_H = size(ORG)
AUD_Y = ORG_Y + OR_H + 86
place(AUDIT, X2, AUD_Y)
AU_W, AU_H = size(AUDIT)
X3 = X2 + max(RK_W, EX_W, OR_W, AU_W)

NY = Y0 + FR_H + 56
# заголовка у диаграммы в VP нет (VisualParadigm.md, §6) —
# текст title из .puml перенесён заметкой в левом верхнем углу
# заметки занимают колонку целиком: их правый край совпадает с правым краем
# пакета frontend/src, иначе под пакетом остаётся пустая полоса в 380 px
NOTE_W = FR_W
MACH_Y = cy('RequestStatusMachine') - 62
NOTE_BOX['title'] = (X0, 88, 760, 74)
NOTE_BOX['scope'] = (X0, NY, NOTE_W, 178)
NOTE_BOX['limits'] = (X0, NY + 206, NOTE_W, 184)
NOTE_BOX['dto'] = (X0, NY + 418, NOTE_W, 330)
# заметка про RequestStatusMachine стоит на уровне своего класса,
# легенда — под ней, поэтому её место в стопке не фиксировано
NOTE_BOX['machine'] = (X0 + NOTE_W - MACH_W, MACH_Y, MACH_W, 124)
NOTE_BOX['legend'] = (X0, MACH_Y + 152, NOTE_W, 730)
NOTE_BOX['risk'] = (X2 + 40, RISK_NOTE_Y, 452, 150)

CANVAS_W = X3
CANVAS_H = max(Y0 + RQ_H, AUD_Y + AU_H, MACH_Y + 882)

# ═══════════════════════════════════════════════════════════════════════
# 4. Маршруты
# ═══════════════════════════════════════════════════════════════════════

STEP = 11


def lane_fl(i):                       # frontend/src, слева
    return X0 + 16 + STEP * i


def lane_fr(i):                       # frontend/src, справа
    return X0 + FR_W - 18 - STEP * i


def lane_req(i):                      # com.karavany.request, слева
    return X1 + 16 + STEP * i


def lane_org(i):                      # com.karavany.organization, слева
    return X2 + 16 + STEP * i


def lane_g12(i):
    return X1 - 34 - STEP * i


def lane_g23(i):
    return X2 - 30 - STEP * i


# правая кромка полосы подписей коридора: подписи выравниваются по ней вправо,
# так они не налезают ни на дорожки слева, ни на фигуры справа
LBL_FL = X0 + FL_LPAD - 12
LBL_REQ = X1 + REQ_LPAD - 12

ROUTE, ENTRY, LBL = {}, {}, {}
LBL_PLACED = []


def edge(a, side, v):
    ax, ay, aw, ah = geo(a)
    if side == 'l':
        return (ax, v)
    if side == 'r':
        return (ax + aw, v)
    if side == 't':
        return (v, ay)
    return (v, ay + ah)


def side_route(a, b, lane, k=None, asid='l', bsid='l', ya=None, band=None):
    """Выход вбок, вертикальный перегон по дорожке, вход вбок на строке k."""
    ya = cy(a) if ya is None else ya
    yb = (geo(b)[1] + 28 + 20 * k) if k is not None else cy(b)
    ROUTE[(a, b)] = [edge(a, asid, ya), (lane, ya), (lane, yb), edge(b, bsid, yb)]
    ENTRY[(a, b)] = yb
    LBL[(a, b)] = band


def band_route(a, b, ymid, asid='b', bsid='t', xa=None, xb=None):
    """U-образный обход через свободную полосу между рядами."""
    xa = cx(a) if xa is None else xa
    xb = cx(b) if xb is None else xb
    ROUTE[(a, b)] = [edge(a, asid, xa), (xa, ymid), (xb, ymid), edge(b, bsid, xb)]


def down_lane_route(a, b, ymid, lane, k=None, bsid='l', xa=None, asid='b'):
    """Выход вниз (вверх), полоса между рядами, дорожка, вход вбок."""
    xa = cx(a) if xa is None else xa
    yb = (geo(b)[1] + 28 + 20 * k) if k is not None else cy(b)
    ROUTE[(a, b)] = [edge(a, asid, xa), (xa, ymid), (lane, ymid), (lane, yb),
                     edge(b, bsid, yb)]
    ENTRY[(a, b)] = yb


def gap_between(left, right):
    """X середины зазора между двумя колонками классов."""
    lx = max(classes[a].x + classes[a].w for a in left)
    rx = min(classes[a].x for a in right)
    return (lx + rx) // 2


def row_gap(upper, lower):
    """Y середины полосы между двумя рядами классов."""
    ub = max(classes[a].y + classes[a].h for a in upper)
    lt = min(classes[a].y for a in lower)
    return (ub + lt) // 2


def top_route(a, b, lane1, lane2, ytop, k=None, asid='l', bsid='t'):
    """Выход вбок, подъём в верхнюю полосу, перенос, спуск в приёмник сверху."""
    ya = cy(a)
    xb = cx(b) if bsid == 't' else None
    if bsid == 't':
        ROUTE[(a, b)] = [edge(a, asid, ya), (lane1, ya), (lane1, ytop),
                         (xb, ytop), edge(b, 't', xb)]
    else:
        yb = (geo(b)[1] + 28 + 20 * k) if k is not None else cy(b)
        ROUTE[(a, b)] = [edge(a, asid, ya), (lane1, ya), (lane1, ytop),
                         (lane2, ytop), (lane2, yb), edge(b, bsid, yb)]
        ENTRY[(a, b)] = yb


# ─── frontend ────────────────────────────────────────────────────────
PAGES_ROW = ['LANDING', 'CONSOLE', 'ORGPAGE']
ROW1 = ['FORM', 'REG']
ROW2 = ['FILTERS', 'SUMMARY', 'LIST']
ROW3 = ['SMODAL', 'SBADGE', 'RBADGE', 'RMODAL']

G_ROOT_PAGES = row_gap(['MAIN', 'APP', 'ROUTER'], PAGES_ROW)
G_PAGES_COMP = row_gap(PAGES_ROW, ROW1)
G_ROW12 = row_gap(ROW1, ROW2)
G_ROW23 = row_gap(ROW2, ROW3)

band_route('APP', 'ORGPAGE', G_ROOT_PAGES)
band_route('LANDING', 'ROUTER', G_ROOT_PAGES, asid='t', bsid='b')
band_route('CONSOLE', 'ROUTER', G_ROOT_PAGES - 14, asid='t', bsid='b',
           xa=cx('CONSOLE') - 26, xb=cx('ROUTER') - 26)
band_route('ORGPAGE', 'ROUTER', G_ROOT_PAGES - 28, asid='t', bsid='b',
           xa=cx('ORGPAGE') + 26, xb=cx('ROUTER') + 26)

band_route('REG', 'FILTERS', G_ROW12 - 24)
band_route('REG', 'LIST', G_ROW12 - 8)
band_route('FILTERS', 'SBADGE', G_ROW23 - 24)
band_route('LIST', 'SMODAL', G_ROW23 - 8)
band_route('LIST', 'SBADGE', G_ROW23 + 8)
band_route('LIST', 'RBADGE', G_ROW23 + 24)

for n, a in enumerate(ROW1):
    down_lane_route(a, 'API', G_ROW12 + 10 + 11 * n, lane_fl(n), k=n)
    LBL[(a, 'API')] = LBL_FL
for n, a in enumerate(ROW2):
    down_lane_route(a, 'API', G_ROW23 + 10 + 11 * n, lane_fl(n + 2), k=n + 2)
    LBL[(a, 'API')] = LBL_FL
down_lane_route('CONSOLE', 'API', G_PAGES_COMP, lane_fr(0), k=5, bsid='r')
down_lane_route('ORGPAGE', 'API', G_PAGES_COMP - 14, lane_fr(1), k=6, bsid='r')

# ─── frontend → web ──────────────────────────────────────────────────
for n, b in enumerate(['RequestController', 'RequestStatusController',
                       'RequestRegistryController']):
    side_route('API', b, lane_g12(n), k=0, asid='r', band=LBL_REQ)
top_route('API', 'OrganizationController', lane_fr(2), lane_g23(7), Y_TOP + 46,
          k=0, asid='r', bsid='l')

# ─── com.karavany.request ────────────────────────────────────────────
REQ_LANES = [('RequestController', 'RequestService', 0),
             ('RequestStatusController', 'RequestService', 1),
             ('RequestStatusController', 'RequestStatusService', 0),
             ('RequestRegistryController', 'RequestRegistryService', 0),
             ('RequestStatusController', 'RequestStatus', 0),
             ('RequestStatusController', 'ActorRole', 0),
             ('RequestStatusController', 'RequestStatusMachine', 0),
             ('RequestRegistryController', 'RequestStatusMachine', 1),
             ('RequestRegistryController', 'RequestRegistry', 0),
             ('RequestStatusService', 'RequestStatusMachine', 2),
             ('RequestRegistryService', 'RequestRegistry', 1)]
for n, (a, b, k) in enumerate(REQ_LANES):
    side_route(a, b, lane_req(n), k=k, band=LBL_REQ)

WEB_GAP = gap_between(['RequestController', 'RequestStatusController',
                       'RequestRegistryController'],
                      ['CreateRequest', 'SegmentInput', 'ChangeStatusRequest'])
side_route('RequestController', 'SegmentInput', WEB_GAP, asid='r')

SRV_COL1 = ['RequestService', 'RequestStatusService', 'RequestRegistryService']
SRV_COL2 = ['SegmentSpec', 'AvailableTransition', 'RegistryView', 'EtaService',
            'RequestReadinessGuard', 'StatusTransitionException']
SRV_GAP = gap_between(SRV_COL1, SRV_COL2)
side_route('RequestService', 'EtaService', SRV_GAP - 16, asid='r')
side_route('RequestStatusService', 'AvailableTransition', SRV_GAP - 8, asid='r')
side_route('RequestRegistryService', 'RegistryView', SRV_GAP, asid='r')
side_route('RequestStatusService', 'RequestReadinessGuard', SRV_GAP + 8, asid='r')
side_route('RequestStatusService', 'StatusTransitionException', SRV_GAP + 16, asid='r')

DOM_COL1 = ['RequestStatus', 'ActorRole', 'RequestStatusMachine', 'RequestRegistry']
DOM_COL2 = ['Transition', 'Summary', 'RegistryScope', 'RegistrySort', 'AttentionFlag']
DOM_GAP = gap_between(DOM_COL1, DOM_COL2)
side_route('RequestStatusMachine', 'Transition', DOM_GAP - 8, asid='r')
side_route('RequestRegistry', 'Summary', DOM_GAP + 8, asid='r')

top_route('RequestService', 'RiskService', lane_req(12), lane_g23(3), Y_TOP, k=0, bsid='l')
top_route('RequestRegistryService', 'RiskLevel', lane_req(13), lane_g23(4), Y_TOP + 22,
          k=0, bsid='l')

# ─── com.karavany.risk ───────────────────────────────────────────────
side_route('RiskService', 'WastelandIntelClient', lane_g23(0), k=0)
side_route('WastelandIntelClient', 'WI', lane_g23(1), k=0)
RISK_GAP = gap_between(['RiskService', 'RiskAssessment', 'WastelandIntelClient', 'RiskLevel'],
                       ['RiskResult', 'SegmentRisk', 'AssessmentSegment', 'ThreatReport',
                        'SegmentThreat', 'RiskAssessmentRepository'])
side_route('WastelandIntelClient', 'SegmentThreat', RISK_GAP, asid='r')

# ─── межпакетные ─────────────────────────────────────────────────────
side_route('CaravanRequest', 'RiskAssessment', lane_g23(5), k=2, asid='r')
side_route('CaravanRequest', 'Organization', lane_g23(8), k=1, asid='r')
side_route('Organization', 'AuditEvent', lane_org(0), k=1)

# ═══════════════════════════════════════════════════════════════════════
# 5. Проверка геометрии
# ═══════════════════════════════════════════════════════════════════════


def auto_segments(a, b):
    """Маршрут, который VP строит сам, когда явных точек нет."""
    ax, ay, aw, ah = geo(a)
    bx, by, bw, bh = geo(b)
    axc, byc = ax + aw // 2, by + bh // 2
    segs = []
    if byc > ay + ah:
        segs.append(('v', axc, ay + ah, byc))
        sx = axc
    elif byc < ay:
        segs.append(('v', axc, byc, ay))
        sx = axc
    else:
        sx = ax + aw if bx > ax else ax
    if sx < bx:
        segs.append(('h', byc, sx, bx))
    elif sx > bx + bw:
        segs.append(('h', byc, bx + bw, sx))
    return segs


def pts_segments(pts):
    segs = []
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if x1 == x2:
            segs.append(('v', x1, min(y1, y2), max(y1, y2)))
        elif y1 == y2:
            segs.append(('h', y1, min(x1, x2), max(x1, x2)))
        else:
            segs.append(('d', x1, y1, x2, y2))
    return segs


def all_boxes(skip=()):
    out = [(al,) + geo(al) for al in classes if al not in skip]
    out += [(k,) + v for k, v in NOTE_BOX.items() if k not in skip]
    return out


def seg_hits(seg, skip=(), m=4):
    hit = []
    for nm, x, y, w, h in all_boxes(skip):
        if seg[0] == 'v':
            _k, sx, y1, y2 = seg
            if x + m < sx < x + w - m and y1 < y + h - m and y2 > y + m:
                hit.append(nm)
        elif seg[0] == 'h':
            _k, sy, x1, x2 = seg
            if y + m < sy < y + h - m and x1 < x + w - m and x2 > x + m:
                hit.append(nm)
    return hit


def rect_hits(x, y, w, h, skip=()):
    return [nm for nm, bx, by, bw, bh in all_boxes(skip)
            if x < bx + bw and x + w > bx and y < by + bh and y + h > by]


def label_report():
    bad = []
    for a, b, x, y, w, h in LBL_PLACED:
        hit = rect_hits(x, y, w, h)
        if hit:
            bad.append((a, b, sorted(set(hit))))
    return bad


def route_report():
    bad = []
    for a, _am, _k, _bm, b, _lab in rels:
        pts = ROUTE.get((a, b))
        segs = pts_segments(pts) if pts else auto_segments(a, b)
        names = []
        for s in segs:
            if s[0] == 'd':
                names.append('ДИАГОНАЛЬ')
            else:
                names += seg_hits(s, skip=(a, b))
        if names:
            bad.append((a, b, sorted(set(names))))
    return bad


if os.environ.get('CHECK'):
    bad = route_report()
    print('полотно %dx%d, пересечений %d из %d' % (CANVAS_W, CANVAS_H, len(bad), len(rels)))
    for a, b, names in bad:
        print('  %-28s -> %-28s %s' % (a, b, ', '.join(names)))
    sys.exit(0)


# ═══════════════════════════════════════════════════════════════════════
# 6. Подписи связей: кандидаты перебираются, берётся первое свободное место
# ═══════════════════════════════════════════════════════════════════════

CAP_BOX = []            # занятые прямоугольники подписей


def free_spot(cands, w, h, skip=()):
    for x, y in cands:
        if rect_hits(x, y, w, h, skip):
            continue
        if any(x < bx + bw and x + w > bx and y < by + bh and y + h > by
               for bx, by, bw, bh in CAP_BOX):
            continue
        CAP_BOX.append((x, y, w, h))
        return x, y
    x, y = cands[-1]
    CAP_BOX.append((x, y, w, h))
    return x, y


def auto_ends(a, b):
    """Точки, в которых автомаршрут VP касается границ источника и приёмника."""
    ax, ay, aw, ah = geo(a)
    bx, by, bw, bh = geo(b)
    axc, byc = ax + aw // 2, by + bh // 2
    down, up = byc > ay + ah, byc < ay
    if down:
        ps = (axc, ay + ah)
    elif up:
        ps = (axc, ay)
    else:
        ps = (ax + aw, cy(a)) if bx > ax else (ax, cy(a))
    sx = ps[0]
    if sx < bx:
        pt = (bx, byc)
    elif sx > bx + bw:
        pt = (bx + bw, byc)
    elif down:
        pt = (sx, by)
    elif up:
        pt = (sx, by + bh)
    else:
        pt = (bx, byc) if bx > ax else (bx + bw, byc)
    return ps, pt


def vis_segments(a, b):
    """Видимая часть линии: автомаршрут, обрезанный границами обеих фигур."""
    pts = ROUTE.get((a, b))
    if pts:
        return pts_segments(pts)
    ps, pt = auto_ends(a, b)
    segs = []
    if ps[1] != pt[1]:
        segs.append(('v', ps[0], min(ps[1], pt[1]), max(ps[1], pt[1])))
    if ps[0] != pt[0]:
        segs.append(('h', pt[1], min(ps[0], pt[0]), max(ps[0], pt[0])))
    return segs


def long_segs(a, b):
    segs = vis_segments(a, b)
    hs = sorted((s for s in segs if s[0] == 'h'), key=lambda s: s[3] - s[2], reverse=True)
    vs = sorted((s for s in segs if s[0] == 'v'), key=lambda s: s[3] - s[2], reverse=True)
    return hs, vs


def caption_spot(a, b, text, lines=1):
    w, h = tw(text) + 14, 17 * lines
    bx, by, bw, bh = geo(b)
    yb = ENTRY.get((a, b), cy(b))
    hs, vs = long_segs(a, b)
    cands = []
    band = LBL.get((a, b))
    if band:
        cands.append((band - w, yb - h - 1))
        cands.append((band - w, yb + 3))
    # «сбоку от приёмника» годится, только если линия и правда входит в него
    # сбоку: иначе подпись отрывается от связи и висит в пустоте
    side = [(bx - w - 10, yb - h - 1), (bx + bw + 10, yb - h - 1)]
    pts_all = vis_segments(a, b)
    last = pts_all[-1] if pts_all else None
    if last and last[0] == 'h':
        if last[2] >= bx + bw - 2:      # линия подходит справа — и подпись справа
            side.reverse()
        cands.append(side[0])
        if last[3] - last[2] < w + 24:
            # отрезок короче подписи: вдоль линии её не поставить — кладём
            # под зазором или над ним, лишь бы она осталась при своей связи
            _ax, ay, _aw, ah = geo(a)
            mid = (last[2] + last[3]) // 2
            cands.append((mid - w // 2, max(ay + ah, by + bh) + 26))
            cands.append((mid - w // 2, min(ay, by) - h - 6))
        cands.append(side[1])
        side = []
    for s in hs:
        mid = (s[2] + s[3]) // 2
        cands.append((mid - w // 2, s[1] - h - 2))
        cands.append((mid - w // 2, s[1] + 3))
    for s in vs:
        mid = (s[2] + s[3]) // 2
        cands.append((s[1] + 8, mid - h // 2))
        cands.append((s[1] - w - 8, mid - h // 2))
    cands += side
    cands.append(((cx(a) + cx(b)) // 2 - w // 2, (cy(a) + cy(b)) // 2 - h // 2))
    # подпись связи не должна залезать ни на одну фигуру, включая свои концы
    spot = free_spot(cands, w, h)
    LBL_PLACED.append((a, b, spot[0], spot[1], w, h))
    return spot


def mult_spot(a, b, at_source):
    pts = ROUTE.get((a, b))
    if pts:
        px, py = pts[0] if at_source else pts[-1]
        nx, ny = pts[1] if at_source else pts[-2]
    else:
        ps, pt = auto_ends(a, b)
        (px, py), (nx, ny) = (ps, pt) if at_source else (pt, ps)
    dx = 6 if nx >= px else -52
    dy = 4 if ny >= py else -20
    if nx == px:
        cands = [(px + 8, py + dy), (px - 54, py + dy)]
    else:
        cands = [(px + (6 if dx > 0 else -52), py - 20), (px + (6 if dx > 0 else -52), py + 4)]
    cands += [(px + 8, py + 4), (px - 54, py - 20)]
    return free_spot(cands, 46, 16, skip=(a, b))


# ═══════════════════════════════════════════════════════════════════════
# 7. Текст заметок и легенды
# ═══════════════════════════════════════════════════════════════════════

N_SCOPE = (
    'Контур диаграммы\n'
    '• показаны классы реализованных прецедентов\n'
    '  UC-1, UC-2, UC-3, UC-7 и UC-32;\n'
    '• вне контура, чтобы диаграмма читалась по ширине\n'
    '  страницы: пакет com.karavany.route целиком,\n'
    '  HealthController и KaravanyApplication;\n'
    '• схема хранения — таблицы, колонки, индексы\n'
    '  и коллекции — на диаграммах базы данных\n'
    '  (DB_ER_ImplementationView\n'
    '  и DB_Datalogical_ImplementationView).')

N_DTO = (
    'Вложенные record-DTO контроллеров\n'
    'Отдельными классами показаны те, что участвуют\n'
    'в связях: CreateRequest, SegmentInput,\n'
    'ChangeStatusRequest, CreateOrganization.\n'
    'Остальные — представления ответов:\n'
    '• RequestController: RequestResponse (16 полей\n'
    '  представления заявки), RiskAssessmentResponse\n'
    '  и SegmentRiskResponse (разбор оценки риска),\n'
    '  ErrorResponse(message : String)\n'
    '• RequestStatusController: StatusInfoResponse\n'
    '  и TransitionResponse (доступные переходы),\n'
    '  StatusHistoryResponse (запись истории)\n'
    '• RequestRegistryController: RegistryResponse (срез,\n'
    '  сортировка, limit, shown, truncated, generatedAt),\n'
    '  RegistryRowResponse (24 поля строки реестра),\n'
    '  SummaryResponse и AttentionResponse\n'
    '  (сводка и пометки)\n'
    '• OrganizationController: FirstDispatcher (часть тела\n'
    '  запроса), OrganizationResponse и UserResponse,\n'
    '  ErrorResponse')

N_RISK = (
    'RiskService.calculate(route, cargoValueCaps)\n'
    'base = min(100, сумма threatLevel * 6)\n'
    'score = min(100, base + cargoFactor),\n'
    'cargoFactor из {0, 10, 20, 30}\n'
    'пороги recommendation: 80 / 60 / 30\n'
    'isStale(asOf): при пустом или неразборном asOf\n'
    'возвращает false — оценка считается актуальной.\n'
    'Предметные шаги расчёта — на ACT_UC7_UseCaseView.')

N_MACHINE = (
    'RequestStatusMachine.TRANSITIONS — 8 переходов\n'
    'Состав переходов с ролями и признаком обязательной\n'
    'причины показан на диаграмме состояний SM_UC2.\n'
    'Здесь существенно: isTerminal(CLOSED) и\n'
    'isTerminal(CANCELLED) истинны — из этих статусов\n'
    'переходов нет.')

N_LIMITS = (
    'Особенности реализации\n'
    '• транзакция открывается в слое web: @Transactional\n'
    '  стоит на методах контроллеров, кроме\n'
    '  RequestRegistryController, — отступление от DC-6;\n'
    '  на CLS_LogicalView границы транзакции показаны\n'
    '  зоной ответственности контракта API;\n'
    '• RequestStatusService.changeStatus() выполняет\n'
    '  проверки в порядке: current == target → find() →\n'
    '  roles().contains() → reasonRequired → blockerFor();\n'
    '  любой отказ — StatusTransitionException → HTTP 409.')

LEGEND = (
    'Обозначения\n'
    '\n'
    'Цвет заливки\n'
    '• светло-серый — класс, интерфейс или enum реализации\n'
    '• сиреневый — record-DTO и внешняя система\n'
    '\n'
    'Стереотип, а не цвет, несёт смысл: «@RestController», «@Service»,\n'
    '«@Component», «@Entity» (хранится в PostgreSQL, DC-4), «@Document»\n'
    '(хранится в MongoDB, DC-5), «JpaRepository», «MongoRepository»,\n'
    '«перечисление», «утилита», «исключение», «не хранится», «pages»,\n'
    '«components», «api», «внешняя система».\n'
    '\n'
    'Хранилища на диаграмме не показаны: принадлежность класса\n'
    'к PostgreSQL или MongoDB видна по аннотации, а сама схема —\n'
    'на диаграммах базы данных Implementation View.\n'
    '\n'
    'Нотация: «-» private, «+» public, подчёркивание — статический член;\n'
    '«имя : Тип» для полей, «имя(параметр : Тип) : Возврат» для методов;\n'
    '«..текст..» — разделитель-пояснение (аннотации класса, вид\n'
    'объявления, контракт внешней системы, сноска), а не член класса;\n'
    '«-- текст --» — заголовок следующего отсека.\n'
    'У методов с пятью и более параметрами показаны только имена\n'
    'параметров — их типы совпадают с полями соответствующего record-DTO.\n'
    'В фигурных скобках — аннотации и пояснения.\n'
    '\n'
    'Типы связей\n'
    '• сплошная линия со стрелкой и кратностями на обоих концах —\n'
    '  направленная ассоциация, фактическое JPA-отображение;\n'
    '  крестик на дальнем конце — обратной навигации нет: у @ManyToOne\n'
    '  обратной ссылки в коде не объявлено;\n'
    '• линия с кружком-плюсом у владельца — вложенный тип\n'
    '  (объявление, а не ассоциация);\n'
    '• линия с полым ромбом у владельца — агрегация;\n'
    '• линия с подписью «по значению …» — связь по значению поля,\n'
    '  внешнего ключа нет;\n'
    '• пунктир со стрелкой — зависимость: вызов или обращение\n'
    '  к хранилищу; кратности на зависимостях и на вложенности\n'
    '  не указываются.\n'
    '\n'
    'Внедрённые зависимости показаны полями класса\n'
    '(«- requestRepository : CaravanRequestRepository» и т. п.).')

N_TITLE = (
    'ИС «Караваны» — Class Diagram (Implementation View)\n'
    'Фактические классы реализации: пакеты, поля, сигнатуры методов\n'
    'и аннотации; схема хранения — на диаграммах базы данных')

NOTES = [('title', N_TITLE, None), ('scope', N_SCOPE, None),
         ('limits', N_LIMITS, None), ('dto', N_DTO, None),
         ('legend', LEGEND, None), ('risk', N_RISK, 'RiskService'),
         ('machine', N_MACHINE, 'RequestStatusMachine')]

# ═══════════════════════════════════════════════════════════════════════
# 8. Построение project.xml
# ═══════════════════════════════════════════════════════════════════════

p = Project(NAME)
d = p.diagram(NAME, 'ClassDiagram')

# Тип поля и тип возврата Visual Paradigm разбирает как ПОЛНОЕ ИМЯ и рисует
# только часть после последней точки: «double = 4.0» превращается в «0»,
# «String {альт. поток 3а}» — в « поток 3а}». В именах (класса, поля, операции)
# точка безопасна, портятся только значения type/returnType. Поэтому в них
# точка заменяется на неразличимый на глаз U+2024 ONE DOT LEADER.
DOT = u'․'


def no_dot(t):
    return t.replace('.', DOT) if t and '.' in t else t


for alias in order:
    c = classes[alias]
    c.model = p.cls(c.title, stereotype=c.stereo, hint='C' + alias)
    for m in c.members:
        if alias in FLAT:
            p.attr(c.model, flat_name(m), visibility=m[1], static=m[-1],
                   hint='A' + alias)
        elif m[0] == 'attr':
            _k, vis, nm, typ, st = m
            p.attr(c.model, nm, type=no_dot(typ), visibility=vis, static=st,
                   hint='A' + alias)
        else:
            _k, vis, nm, params, ret, st = m
            p.oper(c.model, nm, [(pn, no_dot(pt)) for pn, pt in params],
                   ret=no_dot(ret), visibility=vis, static=st, hint='O' + alias)

# фигуры: пакеты в порядке обхода, классы — внутрь своего пакета
pkg_shape, pkg_model, pkg_parent, pkg_shapes = {}, {}, {}, []
stack = []


def build_shapes(n, parent=None, pmodel=None):
    t = n[0]
    if t == 'cls':
        c = n[1]
        c.shape = d.shape('Class', c.model, c.x, c.y, c.w, c.h, name=c.title,
                          fill=c.fill, parent=parent, hint='S' + c.alias)
        return
    if t in ('col', 'row'):
        for k in n[1]:
            build_shapes(k, parent, pmodel)
        return
    name = n[1]
    x, y, w, h = PKGPOS[id(n)]
    tag = re.sub(r'\W', '', name)[:12]
    host = p.children(pmodel) if pmodel is not None else None
    pm = p.model('Package', name=name, hint='PK' + tag, parent=host)
    ps = d.shape('Package', pm, x, y, w, h, name=name, fill=FILL_WHITE,
                 parent=parent, hint='SP' + tag)
    d.child_shapes(ps)
    pkg_shapes.append(ps)
    build_shapes(n[2], ps, pm)


for tree in (FRONT, REQUEST, RISK, EXT, ORG, AUDIT):
    build_shapes(tree)

note_shapes = {}
for key, text, anchor in NOTES:
    x, y, w, h = NOTE_BOX[key]
    m = p.note(text, hint='N' + key)
    s = d.shape('NOTE', m, x, y, w, h, caption=False, fill=FILL_NOTE, hint='SN' + key)
    note_shapes[key] = (m, s, anchor)

# ─── связи ───────────────────────────────────────────────────────────
AGG = {'o--': 'Aggregation', '*--': 'Composited'}

for a, am, kind, bm, b, label in rels:
    ca, cb = classes[a], classes[b]
    label = (label or '').replace('\\n', '\n').strip() or None
    hint = 'R%d_%d' % (order.index(a), order.index(b))
    if kind == '..>':
        fm = p.flow('Dependency', ca.model, cb.model, name=label, hint='M' + hint)
        cn = d.connector('Dependency', fm, ca.shape, cb.shape, hint='C' + hint)
    elif kind == '+--':
        fm = p.flow('Dependency', ca.model, cb.model, hint='M' + hint)
        cn = d.connector('Containment', fm, ca.shape, cb.shape, hint='C' + hint)
    else:
        # «-->» в PlantUML — направленная ассоциация: стрелка у приёмника
        fm = p.assoc(ca.model, cb.model, name=label, a_mult=am, b_mult=bm,
                     a_agg=AGG.get(kind, 'None'),
                     a_nav='false' if kind == '-->' else None,
                     b_nav='true' if kind == '-->' else None,
                     hint='M' + hint)
        cn = d.connector('Association', fm, ca.shape, cb.shape, hint='C' + hint)
    # порядок детей задан схемой: Caption → RoleA → RoleB → Points
    if label:
        nl = label.count('\n') + 1
        x, y = caption_spot(a, b, label, nl)
        ET.SubElement(cn, _q('Caption'), {
            'visible': 'true', 'side': 'None', 'x': str(x), 'y': str(y),
            'width': str(tw(label) + 14), 'height': str(17 * nl)})
    if am or bm:
        pa = mult_spot(a, b, True)
        pb = mult_spot(a, b, False)
        ra = ET.SubElement(cn, _q('RoleA'))
        ET.SubElement(ra, _q('MultiplicityCaption'),
                      {'x': str(pa[0]), 'y': str(pa[1]), 'width': '46', 'height': '16'})
        rb = ET.SubElement(cn, _q('RoleB'))
        ET.SubElement(rb, _q('MultiplicityCaption'),
                      {'x': str(pb[0]), 'y': str(pb[1]), 'width': '46', 'height': '16'})
    pts = ROUTE.get((a, b))
    if pts:
        el = ET.SubElement(cn, _q('Points'))
        for px, py in pts:
            ET.SubElement(el, _q('Point'), {'x': str(px), 'y': str(py)})

# ─── привязки заметок ────────────────────────────────────────────────
ANCHOR_PTS = {
    'risk': lambda s: [edge('risk', 't', cx('risk')), (cx('risk'), RISK_NOTE_Y - 26),
                       (lane_g23(6), RISK_NOTE_Y - 26), (lane_g23(6), cy('RiskService')),
                       edge('RiskService', 'l', cy('RiskService'))],
    'machine': lambda s: [edge('machine', 'r', cy('machine')),
                          (X1 - 92, cy('machine')),
                          (X1 - 92, cy('RequestStatusMachine') + 40),
                          edge('RequestStatusMachine', 'l',
                               cy('RequestStatusMachine') + 40)],
}
for key, (m, s, anchor) in note_shapes.items():
    if not anchor:
        continue
    c = classes[anchor]
    am = p.flow('Anchor', m, c.model, hint='NA' + key)
    cn = d.connector('Anchor', am, s, c.shape, style='Rectlinear', hint='NC' + key)
    el = ET.SubElement(cn, _q('Points'))
    for px, py in ANCHOR_PTS[key](s):
        ET.SubElement(el, _q('Point'), {'x': str(px), 'y': str(py)})

for c in classes.values():
    d.finish_fill(c.shape)
for s in pkg_shapes:
    d.finish_fill(s)
for _m, s, _a in note_shapes.values():
    d.finish_fill(s)

out = os.path.join(HERE, 'out', NAME + '.xml')
os.makedirs(os.path.dirname(out), exist_ok=True)
p.write(out)
print(out)
print('классов %d, связей %d, пересечений %d' % (len(classes), len(rels), len(route_report())))
_lb = label_report()
print('подписей поверх фигур: %d' % len(_lb))
for _a, _b, _n in _lb:
    print('  %-28s -> %-28s %s' % (_a, _b, ', '.join(_n)))
print('полотно ~ %dx%d' % (CANVAS_W, CANVAS_H))
