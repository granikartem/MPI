# -*- coding: utf-8 -*-
"""UCD_UseCaseView: диаграмма прецедентов ИС «Караваны» (Use-Case View).

Содержание перенесено из docs/diagrams/sad/UCD_UseCaseView.puml.
Раскладка задаётся здесь: слева акторы, в центре граница системы с группами
прецедентов, справа внешние системы, заметки и легенда.
"""
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpgen import Project, _q, FILL_GREY, FILL_CREAM, FILL_NOTE  # noqa: E402

NAME = 'UCD_UseCaseView'
WHITE = 'Cr:255,255,255,255'

p = Project(NAME)
d = p.diagram(NAME, 'UseCaseDiagram')

# свойства диаграммы (стереотипы акторов должны быть видны)
dp = ET.Element(_q('DiagramProperties'))
ET.SubElement(dp, _q('BooleanProperty'), {'name': 'showStereotypes', 'value': 'true'})
ET.SubElement(dp, _q('IntegerProperty'), {'name': 'showConnectorName', 'value': '0'})
ET.SubElement(dp, _q('BooleanProperty'), {'name': 'showDiagramFrame', 'value': 'false'})
d.el.insert(0, dp)

shapes = []          # все фигуры в порядке создания — для finish_fill
nodes = {}


# ─── мелкие помощники поверх vpgen ───────────────────────────────────
def deco(s, bold=False, size=11, dashed=False):
    """ElementFont + Line (<Stroke/> обязателен, иначе теряются подписи)."""
    font = ET.Element(_q('ElementFont'), {'color': 'Cr:0,0,0,255', 'name': 'Dialog',
                                          'size': str(size), 'style': '1' if bold else '0'})
    line = ET.Element(_q('Line'), {'color': 'Cr:51,51,51,255', 'weight': '1.0',
                                   'transparency': '0', 'cap': '0'})
    stroke = ET.SubElement(line, _q('Stroke'))
    if dashed:
        dashes = ET.SubElement(stroke, _q('Dashes'))
        for v in ('6.0', '4.0'):
            ET.SubElement(dashes, _q('Dash'), {'value': v})
    s.el.insert(1, font)
    s.el.insert(2, line)
    shapes.append(s)
    return s


def put_caption(s, x, y, w, h, side='South'):
    """Явная подпись с абсолютными координатами (актор, внешняя система)."""
    s.el.insert(3, ET.Element(_q('Caption'), {
        'visible': 'true', 'side': side, 'x': str(x), 'y': str(y),
        'width': str(w), 'height': str(h)}))
    return s


def actor(key, text, x, y, cap_w=160, cap_h=36, stereo=None):
    m = p.model('Actor', name=text, hint='M_' + key)
    if stereo:
        p._stereo_ref(m, [stereo])
    s = d.shape('Actor', m, x, y, 30, 60, name=text, caption=False, hint='S_' + key)
    deco(s)
    put_caption(s, x + 15 - cap_w // 2, y + 60, cap_w, cap_h)
    nodes[key] = (m, s)
    return s


def group(key, text, x, y, w, h, parent, fill=WHITE):
    m = p.model('System', name=text, hint='M_' + key)
    d.child_shapes(parent[1])
    s = d.shape('System', m, x, y, w, h, name=text, fill=fill,
                parent=parent[1], hint='S_' + key)
    deco(s)
    nodes[key] = (m, s)
    return s


def uc(key, text, x, y, w, h, parent, fill=FILL_GREY, bold=False, dashed=False):
    m = p.model('UseCase', name=text, hint='M_' + key)
    d.child_shapes(parent[1])
    s = d.shape('UseCase', m, x, y, w, h, name=text, fill=fill,
                parent=parent[1], hint='S_' + key)
    deco(s, bold=bold, dashed=dashed)
    nodes[key] = (m, s)
    return s


def conn(shape_type, model, a, b, pts=None, cap_xy=None, hint='c'):
    """Связь на холсте: from/to — ФИГУРЫ.

    <Points> учитывается только как ПОЛНАЯ ломаная: первая точка на границе
    фигуры-источника, последняя — на границе приёмника, между ними изломы.
    Список из одних изломов VP молча игнорирует, как и Rectlinear-трассу
    и любой DiagramElementProperties (связь пересчитывается заново).
    """
    el = d.connector(shape_type, model, nodes[a][1], nodes[b][1],
                     points=pts, caption_xy=cap_xy, caption_wh=(90, 18),
                     style='Oblique', hint=hint)
    font = ET.Element(_q('ElementFont'), {'color': 'Cr:0,0,0,255', 'name': 'Dialog',
                                          'size': '11', 'style': '0'})
    line = ET.Element(_q('Line'), {'color': 'Cr:51,51,51,255', 'weight': '1.0',
                                   'transparency': '0', 'cap': '0'})
    ET.SubElement(line, _q('Stroke'))
    el.insert(0, font)
    el.insert(1, line)
    return el


def assoc(a, b, pts=None, hint='as'):
    """Ассоциация актор → прецедент, стрелка на конце to."""
    m = p.assoc(nodes[a][0], nodes[b][0], hint='M_' + hint)
    ET.SubElement(m.props, _q('StringProperty'), {'name': 'direction', 'value': 'From-To'})
    # стрелку направления ImportXML не рисует: ни navigable строкой, ни int-кодом
    # (IAssociationEnd.NAVIGABLE_*), ни direction — связь выходит ненаправленной
    conn('Association', m, a, b, pts=pts, hint='C_' + hint)


def include(a, b, cap_xy, pts=None, hint='in'):
    """Include: from — базовый прецедент, to — включаемый, стрелка на конце to."""
    m = p.model('Include', name='«include»', hint='M_' + hint)
    p._stereo_ref(m, ['include'])
    p.ref_prop(m, 'from', nodes[a][0].id)
    p.ref_prop(m, 'to', nodes[b][0].id)
    conn('Include', m, a, b, pts=pts, cap_xy=cap_xy, hint='C_' + hint)


def general(parent, child, pts=None, hint='gen'):
    """Generalization: from — родитель, полый треугольник на конце from."""
    m = p.model('Generalization', hint='M_' + hint)
    p.ref_prop(m, 'from', nodes[parent][0].id)
    p.ref_prop(m, 'to', nodes[child][0].id)
    conn('Generalization', m, parent, child, pts=pts, hint='C_' + hint)


def anchor(key, target, pts=None):
    am = p.model('Anchor', hint='M_A' + key)
    p.ref_prop(am, 'from', nodes[key][0].id)
    p.ref_prop(am, 'to', nodes[target][0].id)
    conn('Anchor', am, key, target, pts=pts, hint='C_A' + key)


def note(key, text, x, y, w, h, anchor_to=None, pts=None):
    m = p.note(text, hint='M_' + key)
    s = d.shape('NOTE', m, x, y, w, h, caption=False, fill=FILL_NOTE, hint='S_' + key)
    deco(s)
    nodes[key] = (m, s)
    if anchor_to:
        anchor(key, anchor_to, pts)
    return s


p.stereotype('include', 'Include')
ST_EXT = 'внешняя система'
ST_ABS = 'абстрактный'
p.stereotype(ST_EXT, 'Actor')
p.stereotype(ST_ABS, 'Actor')

# ─── заметки верхнего ряда ───────────────────────────────────────────
note('n1', 'UC-1 создаёт заявку\n'
           '• статус «Черновик»\n'
           '• маршрут, ETA, risk_score\n'
           '  и рекомендация по охране\n'
           '  и припасам\n'
           'Пробел реализации\n'
           '• событие создания заявки\n'
           '  в журнал аудита не пишется\n'
           '  (пробел по RL-4)', 30, 60, 330, 175)
note('n2', 'Переходы статуса\n'
           '• инициируют диспетчер\n'
           '  и караван-мастер\n'
           '• инцидент высокой или\n'
           '  критической тяжести (UC-19) —\n'
           '  актором фиксируется «Система»\n'
           '• фиксация этапа рейса (UC-16)\n'
           '  тоже меняет статус\n'
           'Пробел реализации\n'
           '• проверка готовности рейса\n'
           '  перед выходом на маршрут\n'
           '  (FR-10) не выполняется:\n'
           '  модель команды рейса (UC-9)\n'
           '  не реализована', 440, 60, 330, 245)
note('n3', 'UC-3 — точка входа диспетчера\n'
           '• пустой реестр ведёт к UC-1\n'
           '• карточка рейса — к UC-2 и UC-7\n'
           '• архивный срез — к UC-4\n'
           '• сам реестр данные только читает', 820, 60, 310, 115)

# ─── акторы ──────────────────────────────────────────────────────────
actor('disp', 'Диспетчер\nкараванов', 170, 500)
actor('cmst', 'Караван-\nмастер', 255, 880)
actor('secu', 'Капитан\nохраны', 255, 1010)
actor('medic', 'Полевой\nмедик', 255, 1140)
actor('field', 'Полевой\nпользователь', 255, 1270, cap_h=50, stereo=ST_ABS)
actor('super', 'Супер-\nпользователь', 170, 1450)
actor('store', 'Кладовщик', 170, 1650)

# ─── граница системы и группы прецедентов ────────────────────────────
sys_m = p.model('System', name='ИС «Караваны»', hint='M_sys')
sys_s = d.shape('System', sys_m, 460, 350, 680, 1535, name='ИС «Караваны»',
                fill=WHITE, hint='S_sys')
deco(sys_s)
nodes['sys'] = (sys_m, sys_s)

group('g1', 'Управление заявкой и рейсом', 490, 420, 560, 260, nodes['sys'])
uc('uc2', 'UC-2: Управлять\nстатусами заявки', 530, 465, 250, 80, nodes['g1'], bold=True)
uc('uc3', 'UC-3: Просмотреть\nреестр рейсов', 800, 465, 250, 75, nodes['g1'])
uc('uc1', 'UC-1: Создать заявку\nна перевозку', 530, 570, 250, 85, nodes['g1'], bold=True)

group('g3', 'Груз и манифест', 790, 720, 260, 140, nodes['sys'])
uc('uc12', 'UC-12: Указать\nценность груза', 805, 765, 230, 75, nodes['g3'])

group('g2', 'Планирование маршрута\nи оценка рисков', 490, 900, 560, 300, nodes['sys'])
uc('uc5', 'UC-5: Выбрать/\nспланировать маршрут', 520, 965, 230, 80, nodes['g2'])
uc('uc6', 'UC-6: Рассчитать ETA', 820, 965, 230, 75, nodes['g2'])
uc('uc8', 'UC-8: Получить\nрекомендацию по охране\nи припасам', 520, 1070, 230, 95, nodes['g2'])
uc('uc7', 'UC-7: Рассчитать\nrisk_score', 820, 1075, 230, 85, nodes['g2'], bold=True)

group('g4', 'Полевые операции', 490, 1240, 560, 160, nodes['sys'])
uc('uc19', 'UC-19: Сообщить\nоб инциденте в рейсе', 530, 1285, 250, 95, nodes['g4'],
   fill=FILL_CREAM, bold=True)
uc('uc16', 'UC-16: Зафиксировать\nпрохождение\nэтапа рейса', 800, 1285, 250, 95, nodes['g4'],
   fill=FILL_CREAM, bold=True)

group('g5', 'Управление организациями', 790, 1440, 260, 150, nodes['sys'])
uc('uc32', 'UC-32: Создать\nорганизацию', 805, 1485, 230, 85, nodes['g5'], bold=True)

group('g6', 'Остальные прецеденты —\nсостав на диаграмме не раскрыт',
      490, 1630, 560, 215, nodes['sys'])
uc('rest', '23 прецедента:\nUC-4, UC-9…UC-11, UC-13…UC-15,\nUC-17, UC-18, UC-20…UC-31,\n'
           'UC-33, UC-34', 530, 1690, 480, 140, nodes['g6'], fill=WHITE, dashed=True)

# ─── внешние системы ─────────────────────────────────────────────────
actor('wi', 'Wasteland\nIntel', 1220, 880, cap_w=180, cap_h=50, stereo=ST_EXT)
actor('ncr', 'NCR Checkpoint\n& Tax Terminal', 1220, 1690, cap_w=170, cap_h=50, stereo=ST_EXT)

# ─── обобщение полевых ролей ─────────────────────────────────────────
general('field', 'cmst', pts=[(255, 1290), (135, 1290), (135, 905), (255, 905)], hint='g1')
general('field', 'secu', pts=[(255, 1300), (155, 1300), (155, 1035), (255, 1035)], hint='g2')
general('field', 'medic', pts=[(255, 1312), (175, 1312), (175, 1165), (255, 1165)], hint='g3')

# ─── связи акторов с прецедентами ────────────────────────────────────
assoc('disp', 'uc2', hint='a1')
assoc('disp', 'uc1', hint='a2')
assoc('disp', 'uc3', pts=[(200, 515), (480, 515), (480, 400), (1010, 400), (1010, 465)],
      hint='a3')
assoc('disp', 'uc5', pts=[(200, 520), (470, 520), (470, 1005), (520, 1005)], hint='a4')
assoc('disp', 'uc7', pts=[(200, 540), (365, 540), (365, 1190), (935, 1190), (935, 1160)],
      hint='a5')
# в обход группы G1: вниз по коридору x=300, затем полосой между G1 и G3
assoc('disp', 'uc12',
      pts=[(200, 558), (300, 558), (300, 700), (760, 700), (760, 802), (805, 802)], hint='a6')
assoc('disp', 'rest', pts=[(200, 550), (385, 550), (385, 1745), (536, 1745)], hint='a7')

assoc('cmst', 'uc2', pts=[(285, 898), (435, 898), (435, 510), (531, 510)], hint='a8')
assoc('cmst', 'uc16', pts=[(285, 910), (410, 910), (410, 1225), (925, 1225), (925, 1285)],
      hint='a9')
assoc('cmst', 'rest', pts=[(285, 922), (450, 922), (450, 1760), (530, 1760)], hint='a10')

assoc('field', 'uc19', pts=[(285, 1300), (440, 1300), (440, 1332), (530, 1332)], hint='a11')
assoc('field', 'rest', pts=[(285, 1320), (430, 1320), (430, 1790), (553, 1790)], hint='a12')

assoc('store', 'rest', hint='a13')
assoc('super', 'uc32', hint='a14')
assoc('super', 'rest', hint='a15')

# к акторам-внешним системам подходим горизонтально в полосе самой фигуры:
# по диагонали снизу VP обрезает связь о рамку подписи, и линия повисает в воздухе
assoc('uc7', 'wi', pts=[(1050, 1117), (1105, 1117), (1105, 900), (1220, 900)], hint='a16')
assoc('rest', 'wi', pts=[(967, 1720), (1125, 1720), (1125, 925), (1220, 925)], hint='a17')
assoc('rest', 'ncr', pts=[(1000, 1740), (1120, 1740), (1220, 1740)], hint='a18')

# ─── включаемые прецеденты ───────────────────────────────────────────
include('uc1', 'uc5', (655, 790), pts=[(655, 655), (645, 810), (635, 965)], hint='i1')
include('uc1', 'uc6', (965, 698),
        pts=[(775, 600), (1065, 600), (1065, 1002), (1050, 1002)], hint='i2')
include('uc1', 'uc7', (995, 940),
        pts=[(774, 625), (1090, 625), (1090, 1117), (1050, 1117)], hint='i3')
include('uc1', 'uc8', (512, 866),
        pts=[(532, 620), (505, 620), (505, 1117), (520, 1117)], hint='i4')
include('uc1', 'uc12', (800, 700), hint='i5')
include('uc7', 'uc8', (740, 1085), hint='i6')

# ─── привязки заметок верхнего ряда ──────────────────────────────────
anchor('n1', 'uc1', pts=[(360, 150), (415, 150), (415, 612), (530, 612)])
anchor('n2', 'uc2')
anchor('n3', 'uc3')

# ─── заметки справа и легенда ────────────────────────────────────────
note('n7', 'Внешние данные (FR-6)\n'
           '• нет ответа Wasteland Intel →\n'
           '  risk_score «Н/Д», пометка\n'
           '  «требует пересчёта» (альт. 2а)\n'
           '• данные старше 24 часов →\n'
           '  пометка «на основе устаревших\n'
           '  данных» (альт. 2б)\n'
           'Автоматические прецеденты\n'
           '• UC-6 и UC-8 актор не вызывает:\n'
           '  выполняются автоматически\n'
           '  в составе UC-1 и UC-7',
     1340, 950, 420, 200, anchor_to='uc7')
note('n16', 'Спроектировано, но не реализовано\n'
            '• UC-16: этапы рейса, журнал контрольных\n'
            '  точек и офлайн-фиксация на полевом\n'
            '  устройстве в системе отсутствуют\n'
            '• UC-19: карточка инцидента, уведомление\n'
            '  диспетчера и автоперевод рейса\n'
            '  в «Задержку» в системе отсутствуют\n'
            'Точки расширения (CoreUseCases.md)\n'
            '• UC-16: EP-1 прибытие на КТ → UC-17;\n'
            '  EP-2 прохождение КПП → UC-18;\n'
            '  EP-3 подтверждение доставки → UC-14\n'
            '• UC-19: EP-1 критический инцидент →\n'
            '  UC-20 «Инициировать RecoveryRequest»',
     1340, 1260, 420, 235, anchor_to='uc16')
note('n32', 'Основание мультитенантности\n'
            '• прецедент выделяет организации изолированное\n'
            '  пространство данных (FR-23, FR-24) —\n'
            '  на него опираются UC-1 и UC-3\n'
            'Точки расширения (CoreUseCases.md)\n'
            '• EP-1 → UC-33 «Назначить первого диспетчера\n'
            '  организации»: выполняется в том же шаге —\n'
            '  учётная запись создаётся вместе\n'
            '  с организацией и необязательна (альт. 6а)\n'
            '• EP-2 → UC-34 «Управлять подписками»:\n'
            '  уровень подписки только сохраняется,\n'
            '  управление подписками не реализовано',
     1340, 1560, 470, 220, anchor_to='uc32')

note('legend', 'Обозначения\n'
               '• рамка ИС «Караваны» — граница системы; акторы вне рамки\n'
               '• жирный шрифт — архитектурно значимый прецедент (CoreUseCases.md)\n'
               '• светло-серый фон #F5F5F5 — прецедент реализован в системе\n'
               '• кремовый фон #FFF2CC — спроектирован по документам, но не реализован\n'
               '• белый фон + пунктирная рамка — группа прецедентов: номера\n'
               '  перечислены, статус реализации не показан; какие из них\n'
               '  вызывает каждый актор — видно только в docs/UseCases.md\n'
               '• «абстрактный» — актор-обобщение: «Полевой пользователь»\n'
               '  обобщает караван-мастера, капитана охраны и полевого медика\n'
               '• «внешняя система» — актор-система за границей ИС «Караваны»\n'
               '\n'
               'Полный перечень 34 прецедентов — docs/UseCases.md\n'
               'и общая диаграмма diagrams/out/UC_0_General.png;\n'
               'детальные диаграммы — diagrams/usecases/UC_*_Detail.puml.\n'
               '\n'
               'Трассировка на SRS: UC-1 → FR-1; UC-2 → FR-2, FR-3;\n'
               'UC-3 → FR-2, FR-3, FR-7, FR-8, FR-24 (по docs/UC-3.md; FR-23 —\n'
               'предусловие, а не покрываемое требование); UC-6 → FR-5;\n'
               'UC-7 → FR-6, FR-7; UC-8 → FR-8; UC-12 → FR-13, FR-14;\n'
               'UC-16 → FR-18; UC-19 → FR-19, FR-20; UC-32 → FR-23, FR-24, FR-25.\n'
               'UC-5 отдельного требования не имеет и входит в FR-1.\n'
               'Журнал аудита по операциям с данными — RL-4 и RL-5\n'
               '(FR-35 относится только к управлению пользователями).',
     1340, 300, 530, 420)

# ─── заливка последним ребёнком ──────────────────────────────────────
for _s in shapes:
    d.finish_fill(_s)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', NAME + '.xml')
os.makedirs(os.path.dirname(out), exist_ok=True)
p.write(out)
print(out)
