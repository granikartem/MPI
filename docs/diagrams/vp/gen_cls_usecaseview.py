# -*- coding: utf-8 -*-
"""CLS_UseCaseView: диаграмма классов концептуального уровня (Use-Case View).

Содержание перенесено из docs/diagrams/sad/CLS_UseCaseView.puml: понятия предметной
области со свойствами без типов, перечисления, внешняя система, ассоциации с
кратностями, композиции, агрегации, зависимости, три заметки и легенда.

Раскладка задаётся здесь, маршруты связей — явными точками излома.

Важная особенность формата: кратности и роли рисуются только при
requestResetCaption=true у коннектора, а при нём Visual Paradigm расставляет
подпись связи сам — в середине ломаной, игнорируя заданные координаты Caption.
Поэтому положение подписи задаётся не координатами, а геометрией маршрута;
`python gen_cls_usecaseview.py --check` считает середины ломаных и проверяет,
что подписи не налезают на фигуры и друг на друга.
"""
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpgen import Project, NS, FILL_GREY, FILL_LILAC, FILL_NOTE  # noqa: E402

NAME = 'CLS_UseCaseView'
CH = 6.5        # ширина знака подписи связи, px (замерено по экспорту)
LH = 16         # высота строки подписи связи, px
LY = 12         # сдвиг подписи вниз от середины ломаной, px (замер по PNG)


def Q(tag):
    return '{%s}%s' % (NS, tag)


p = Project(NAME)
d = p.diagram(NAME, 'ClassDiagram')

nodes = {}       # key -> (модель, фигура)
boxes = {}       # key -> (x, y, w, h)        — для проверки раскладки
labels = []      # (текст, x, y, w, h)        — подписи связей, середина ломаной


# ─── примитивы ───────────────────────────────────────────────────────
def box(key, name, attrs, x, y, w, h, fill=FILL_GREY, stereo=None):
    """Понятие предметной области: класс со свойствами БЕЗ ТИПОВ."""
    m = p.cls(name, stereotype=stereo, hint='CL_' + key)
    for a in attrs:
        p.attr(m, a, visibility='Unspecified', hint='AT_' + key)
    s = d.shape('Class', m, x, y, w, h, name=name, fill=fill, caption=False,
                hint='SH_' + key)
    nodes[key] = (m, s)
    boxes[key] = (x, y, w, h)
    return s


def enum(key, name, literals, x, y, w, h, fill=FILL_GREY):
    """Перечисление: Class со стереотипом enumeration и детьми EnumerationLiteral."""
    m = p.cls(name, stereotype='enumeration', hint='EN_' + key)
    for lit in literals:
        p.lit(m, lit, hint='EL_' + key)
    s = d.shape('Class', m, x, y, w, h, name=name, fill=fill, caption=False,
                hint='SH_' + key)
    nodes[key] = (m, s)
    boxes[key] = (x, y, w, h)
    return s


def _reset(el):
    """requestResetCaption у коннектора — без него не рисуются роли и кратности."""
    dep = ET.Element(Q('DiagramElementProperties'))
    for n in ('requestResetCaption', 'requestResetCaptionSize'):
        ET.SubElement(dep, Q('BooleanProperty'), {'name': n, 'value': 'true'})
    el.insert(0, dep)
    return el


def _label_rect(text, pts):
    """Прямоугольник подписи связи в системе координат диаграммы.

    Visual Paradigm привязывает подпись к середине ломаной и рисует её НИЖЕ
    линии: замеры по экспортированным PNG дают сдвиг около +12 px по y
    (поэтому LY), по x подпись центрируется с точностью до пары символов.
    """
    segs, total = [], 0.0
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        ln = abs(x2 - x1) + abs(y2 - y1)
        segs.append(((x1, y1), (x2, y2), ln))
        total += ln
    half, acc = total / 2.0, 0.0
    cx, cy = pts[0]
    for (x1, y1), (x2, y2), ln in segs:
        if acc + ln >= half:
            t = (half - acc) / ln if ln else 0
            cx, cy = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
            break
        acc += ln
    lines = text.split('\n')
    w = max(len(ln) for ln in lines) * CH
    h = len(lines) * LH
    return (int(cx - w / 2), int(cy + LY), int(w), int(h))


def link(key, a, b, label=None, am=None, bm=None, agg=None, nav=False, pts=None):
    """Ассоциация: agg — 'Aggregation' / 'Composited' у конца A."""
    ma, sa = nodes[a]
    mb, sb = nodes[b]
    m = p.assoc(ma, mb, name=label, a_mult=am, b_mult=bm,
                a_agg=agg or 'None', hint='AS_' + key)
    if nav:
        # Стрелка «-->» рисуется, только когда навигабелен ровно один конец.
        # Свойство navigable читается ТОЛЬКО как StringProperty со значением
        # 'true'/'false'; IntegerProperty (0/1/2 из IAssociationEnd.NAVIGABLE_*)
        # молча игнорируется — проверено отрисовкой матрицы из десяти вариантов.
        # Побочный эффект 'false': VP ставит на ближнем конце крестик
        # «non-navigable». Режима «стрелка без крестика» нет: при любом
        # showNavigationArrows (0..3) и любом другом значении navigable
        # получается либо две стрелки, либо ни одной.
        for end, val in (('FromEnd', 'false'), ('ToEnd', 'true')):
            props = m.el.find(Q(end) + '/' + Q('Model') + '/' + Q('ModelProperties'))
            ET.SubElement(props, Q('StringProperty'),
                          {'name': 'navigable', 'value': val})
    cn = _reset(d.connector('Association', m, sa, sb, points=pts, hint='CN_' + key))
    if nav:
        # 3 — SHOW_NAVIGATION_ARROWS_HIDE_ARROWS_WITH_TWO_WAY_NAVIGABILITY
        ET.SubElement(cn.find(Q('DiagramElementProperties')), Q('IntegerProperty'),
                      {'name': 'showNavigationArrows', 'value': '3'})
    if label:
        labels.append((label, ) + _label_rect(label, pts))


def dep(key, a, b, label=None, pts=None):
    """Зависимость ..> — кратности на ней не показываются."""
    ma, sa = nodes[a]
    mb, sb = nodes[b]
    m = p.flow('Dependency', ma, mb, name=label, hint='DP_' + key)
    _reset(d.connector('Dependency', m, sa, sb, points=pts, hint='CN_' + key))
    if label:
        labels.append((label, ) + _label_rect(label, pts))


def note(key, text, x, y, w, h, anchor=None, pts=None):
    m = p.note(text, hint='NO_' + key)
    s = d.shape('NOTE', m, x, y, w, h, caption=False, fill=FILL_NOTE, hint='SH_' + key)
    nodes[key] = (m, s)
    boxes[key] = (x, y, w, h)
    if anchor:
        am, asx = nodes[anchor]
        fm = p.flow('Anchor', m, am, hint='AN_' + key)
        _reset(d.connector('Anchor', fm, s, asx, style=None, points=pts,
                           hint='CN_' + key))


# ═══ узлы ════════════════════════════════════════════════════════════
# — кто работает в системе —
box('USER', 'Сотрудник',
    ['имя', 'роль в организации', 'канал связи'], 60, 210, 250, 90)
enum('ROLE', 'Роль участника',
     ['Диспетчер караванов', 'Караван-мастер', 'Система'], 60, 430, 240, 105)
box('ORG', 'Организация',
    ['название', 'уровень подписки', 'состояние'], 520, 40, 240, 90)

# — рейс и его статусная модель —
box('REQ', 'Заявка на перевозку',
    ['пункт отправления', 'пункт назначения', 'желаемая дата отправки',
     'описание груза', 'оценочная ценность груза', 'расчётное время в пути',
     'текущий статус'], 960, 195, 300, 145)
box('HIST', 'Запись истории рейса',
    ['предыдущий статус', 'новый статус', 'кто инициировал переход', 'причина',
     'когда произошло'], 580, 430, 260, 115)
enum('STATUS', 'Статус рейса',
     ['Черновик', 'Готов к отправке', 'В пути', 'Задержка', 'Доставлен',
      'Закрыт', 'Отменён'], 980, 430, 230, 160)
box('AUDIT', 'Событие аудита',
    ['что произошло', 'кто инициировал', 'когда произошло'], 520, 210, 230, 90)

# — маршрут —
box('ROUTE', 'Маршрут',
    ['название', 'готовый шаблон или задан вручную'], 1420, 430, 290, 75)
box('SEG', 'Участок маршрута',
    ['порядок в маршруте', 'протяжённость'], 1430, 670, 240, 75)
box('CP', 'Контрольная точка', ['название'], 1440, 860, 210, 60)

# — оценка риска —
box('RISK', 'Оценка риска',
    ['значение риска', 'актуальность оценки', 'рекомендация по охране и припасам',
     'когда получена'], 1820, 210, 320, 100)
enum('LEVEL', 'Уровень риска',
     ['Н/Д', 'Низкий', 'Средний', 'Высокий', 'Критический'], 1820, 430, 210, 128)

# — внешняя система разведки —
box('WI', 'Wasteland Intel', [], 2400, 40, 240, 60,
    fill=FILL_LILAC, stereo='внешняя система')
box('REPORT', 'Отчёт об угрозах',
    ['дата актуальности сведений'], 2400, 210, 250, 60, fill=FILL_LILAC)
box('THREAT', 'Угроза участка',
    ['участок маршрута', 'уровень опасности', 'виды угроз'], 2400, 400, 240, 90,
    fill=FILL_LILAC)

# — полевые события рейса —
box('INC', 'Инцидент',
    ['вид инцидента', 'тяжесть', 'время и место', 'описание произошедшего'],
    520, 670, 260, 100)
box('STAGE', 'Этап рейса',
    ['порядок этапа', 'вид этапа', 'плановое время', 'подтверждён'],
    980, 670, 240, 100)
box('PART', 'Участник инцидента',
    ['роль в инциденте', 'пострадал', 'состояние и оказанная помощь'],
    60, 860, 280, 90)
box('RECOVERY', 'Запрос на реагирование',
    ['что требуется', 'состояние обработки'], 520, 860, 250, 75)
box('LOG', 'Отметка прохождения',
    ['фактическое время', 'место', 'результат', 'причина задержки'],
    980, 860, 240, 100)

# ═══ связи ═══════════════════════════════════════════════════════════
# организация и её люди
link('org_user', 'ORG', 'USER', 'сотрудники организации', '1', '0..*',
     agg='Aggregation',
     pts=[(520, 85), (390, 85), (390, 265), (310, 265)])
link('org_req', 'ORG', 'REQ', 'рейсы организации (FR-23, FR-24)', '1', '0..*',
     agg='Aggregation',
     pts=[(760, 85), (880, 85), (880, 250), (960, 250)])
link('org_audit', 'ORG', 'AUDIT', 'события организации (RL-4)', '1', '0..*',
     agg='Aggregation', pts=[(640, 130), (640, 210)])
dep('user_role', 'USER', 'ROLE', 'роль сотрудника',
    pts=[(130, 300), (130, 430)])

# статусная модель
link('req_hist', 'REQ', 'HIST', 'история переходов (FR-3)', '1', '1..*',
     agg='Composited',
     pts=[(960, 300), (870, 300), (870, 470), (840, 470)])
dep('req_status', 'REQ', 'STATUS', 'текущий статус (FR-2)',
    pts=[(1060, 340), (1060, 430)])
dep('hist_status', 'HIST', 'STATUS', 'из какого в какой',
    pts=[(840, 490), (980, 490)])
dep('hist_role', 'HIST', 'ROLE', 'кто инициировал',
    pts=[(580, 520), (300, 520)])
link('hist_audit', 'HIST', 'AUDIT', 'переход статуса попадает в журнал',
     '0..1', '0..1', pts=[(600, 430), (600, 300)])

# рейс и маршрут
link('req_route', 'REQ', 'ROUTE', 'выполняется по маршруту (FR-4)', '0..*', '0..1',
     nav=True, pts=[(1260, 300), (1500, 300), (1500, 430)])
link('route_seg', 'ROUTE', 'SEG', 'участки в порядке следования', '1', '1..*',
     agg='Composited', pts=[(1550, 505), (1550, 670)])
link('seg_cp1', 'SEG', 'CP', 'начало участка', '0..*', '1', nav=True,
     pts=[(1480, 745), (1480, 860)])
link('seg_cp2', 'SEG', 'CP', 'конец участка', '0..*', '1', nav=True,
     pts=[(1620, 745), (1620, 860)])

# оценка риска
link('req_risk', 'REQ', 'RISK',
     'оценки риска рейса; учитывают\nценность груза (FR-7, FR-13, FR-14)',
     '1', '0..*', agg='Aggregation', pts=[(1260, 240), (1820, 240)])
dep('risk_level', 'RISK', 'LEVEL', 'уровень риска для диспетчера (FR-8)',
    pts=[(1880, 310), (1880, 430)])
dep('risk_report', 'RISK', 'REPORT', 'рассчитана по сведениям об угрозах',
    pts=[(2140, 260), (2400, 260)])
link('wi_report', 'WI', 'REPORT', 'поставляет сведения об угрозах (FR-6)',
     '1', '0..*', nav=True, pts=[(2520, 100), (2520, 210)])
link('report_threat', 'REPORT', 'THREAT', 'угрозы по участкам маршрута',
     '1', '1..*', agg='Aggregation', pts=[(2460, 270), (2460, 400)])
# маршрут идёт по свободной полосе между заметкой о риске и легендой
dep('threat_seg', 'THREAT', 'SEG', 'относится к участку',
    pts=[(2520, 490), (2520, 705), (1670, 705)])

# полевые события рейса
link('req_stage', 'REQ', 'STAGE', 'план этапов рейса (FR-18)', '1', '0..*',
     agg='Composited',
     pts=[(1260, 320), (1340, 320), (1340, 630), (1100, 630), (1100, 670)])
link('stage_log', 'STAGE', 'LOG', 'отметка о прохождении', '1', '0..1',
     agg='Composited', pts=[(1050, 770), (1050, 860)])
link('stage_cp', 'STAGE', 'CP', 'плановая контрольная точка', '0..*', '0..1',
     nav=True, pts=[(1220, 730), (1330, 730), (1330, 890), (1440, 890)])
link('req_inc', 'REQ', 'INC', 'инциденты рейса (FR-19)', '1', '0..*',
     agg='Composited',
     pts=[(960, 335), (930, 335), (930, 640), (620, 640), (620, 670)])
link('inc_part', 'INC', 'PART', 'участники инцидента (FR-20)', '1', '0..*',
     agg='Composited',
     pts=[(560, 770), (560, 810), (180, 810), (180, 860)])
link('inc_rec', 'INC', 'RECOVERY', 'основание для реагирования (FR-21)',
     '1', '0..*', agg='Aggregation', pts=[(700, 770), (700, 860)])
link('inc_user', 'INC', 'USER', 'кто сообщил об инциденте', '0..*', '1', nav=True,
     pts=[(520, 720), (360, 720), (360, 290), (310, 290)])

# ═══ заметки ═════════════════════════════════════════════════════════
note('n_req',
     'Рейс — центральное понятие\n'
     'Диспетчер создаёт заявку (UC-1), система подбирает маршрут (UC-5),\n'
     'считает время в пути (UC-6) и риск (UC-7), даёт рекомендацию\n'
     'по охране и припасам (UC-8). Дальше рейс живёт статусной моделью\n'
     '(UC-2) и виден в реестре (UC-3).',
     1380, 40, 490, 105, anchor='REQ', pts=[(1380, 110), (1260, 230)])

note('n_risk',
     'Оценка риска обновляется каждым расчётом\n'
     'Если внешняя система недоступна, оценка получает значение «Н/Д»\n'
     'и пометку «требует пересчёта»; если сведения старше суток —\n'
     'пометку «на основе устаревших данных».',
     1820, 600, 470, 90, anchor='RISK', pts=[(2100, 600), (2100, 310)])

note('n_inc',
     'Полевые события рейса\n'
     'Отметки прохождения этапов и карточки инцидентов создаются\n'
     'на полевом устройстве и попадают в систему при появлении связи (RL-1).',
     60, 980, 510, 75, anchor='INC',
     pts=[(420, 980), (420, 745), (520, 745)])

note('legend',
     'Обозначения\n'
     '• серый — понятие реализовано в системе\n'
     '• сиреневый — «внешняя система» и данные, которые она поставляет\n'
     '\n'
     'Уровень описания. Только предметная область: понятия, их деловые\n'
     'свойства и связи. Ни классов реализации, ни методов, ни типов данных,\n'
     'ни слоёв, ни хранилищ — это уровни Logical и Implementation View.\n'
     'Свойства перечислены деловыми именами, без типов: тип и формат\n'
     'появляются на CLS_LogicalView, фактическое объявление —\n'
     'на CLS_ImplementationView.\n'
     'Перечисления показаны там, где набор значений сам является\n'
     'понятием модели и обсуждается с заказчиком.\n'
     'Типы связей: *-- композиция (часть не существует без целого),\n'
     'o-- агрегация, --> ассоциация, ..> зависимость\n'
     '(на зависимостях кратности не указываются).\n'
     'Трассировка: FR-2 и FR-3 (статусы и история), FR-4 (маршрут),\n'
     'FR-6 (Wasteland Intel), FR-7 (risk_score), FR-8 (рекомендация),\n'
     'FR-13 и FR-14 (ценность груза), FR-18 (этапы рейса),\n'
     'FR-19 — FR-21 (инциденты и реагирование), FR-23 и FR-24\n'
     '(организация и изоляция её данных), RL-1 (офлайн-фиксация),\n'
     'RL-4 (журнал аудита). Перечень прецедентов — docs/UseCases.md.',
     1800, 760, 520, 355)

# заливка — последним ребёнком каждой фигуры
for _m, _s in nodes.values():
    d.finish_fill(_s)


# ═══ проверка раскладки ══════════════════════════════════════════════
def _ov(a, b):
    dx = min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0])
    dy = min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1])
    return dx, dy


def check():
    bad = 0
    for text, x, y, w, h in labels:
        for key, r in boxes.items():
            dx, dy = _ov((x, y, w, h), r)
            if dx > 0 and dy > 0:
                print('ПОДПИСЬ НА ФИГУРЕ: "%s" (%d,%d %dx%d) x [%s] %dx%d'
                      % (text.replace('\n', ' / '), x, y, w, h, key, dx, dy))
                bad += 1
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            t1, *r1 = labels[i]
            t2, *r2 = labels[j]
            dx, dy = _ov(r1, r2)
            if dx > 0 and dy > 0:
                print('ПОДПИСИ ВНАХЛЁСТ: "%s" x "%s" %dx%d'
                      % (t1.replace('\n', ' / '), t2.replace('\n', ' / '), dx, dy))
                bad += 1
    keys = list(boxes)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            dx, dy = _ov(boxes[keys[i]], boxes[keys[j]])
            if dx > 0 and dy > 0:
                print('ФИГУРЫ ВНАХЛЁСТ: [%s] x [%s] %dx%d'
                      % (keys[i], keys[j], dx, dy))
                bad += 1
    xs = [r[0] for r in boxes.values()] + [r[0] + r[2] for r in boxes.values()]
    ys = [r[1] for r in boxes.values()] + [r[1] + r[3] for r in boxes.values()]
    print('габариты: x %d..%d, y %d..%d; замечаний: %d'
          % (min(xs), max(xs), min(ys), max(ys), bad))
    return bad


if '--check' in sys.argv:
    sys.exit(1 if check() else 0)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', NAME + '.xml')
os.makedirs(os.path.dirname(out), exist_ok=True)
p.write(out)
print(out)
