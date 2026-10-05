# -*- coding: utf-8 -*-
"""ACT_UC7_UseCaseView: UC-7 «Рассчитать risk_score», Activity Diagram (Use-Case View).

Содержание перенесено из docs/diagrams/sad/ACT_UC7_UseCaseView.puml.
Раскладка задаётся здесь: колонка — дорожка, строка — шаг потока.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpgen import Project, Swimlanes, FILL_GREY, FILL_PINK, FILL_SAND, FILL_NOTE  # noqa: E402

NAME = 'ACT_UC7_UseCaseView'

p = Project(NAME)
d = p.diagram(NAME, 'ActivityDiagram')

# ─── дорожки ─────────────────────────────────────────────────────────
LANES = [('Диспетчер караванов', 340),
         ('ИС «Караваны»', 900),
         ('«внешняя система»\nWasteland Intel', 340)]
sw = Swimlanes(d, LANES, x=40, y=40, body_h=1900)
L0, L1, L2 = 0, 1, 2

# опорные колонки внутри дорожки «ИС «Караваны»»
SPINE_X, SPINE_W = 490, 420      # основной столбец
COL_A_X, COL_A_W = 455, 280      # вложенная ветка «да»
COL_B_X, COL_B_W = 760, 280      # вложенная ветка «нет — альт. поток 2б»
COL_C_X, COL_C_W = 1000, 265     # альт. поток 2а

nodes = {}


def act(key, text, x, y, w, h, fill=FILL_GREY):
    m = p.model('ActivityAction', name=text, hint='M_' + key)
    s = d.shape('ActivityAction', m, x, y, w, h, name=text, fill=fill, hint='S_' + key)
    nodes[key] = (m, s)
    return s


def ctrl(key, a, b, guard=None, name=None, cap=None, pts=None):
    ma, sa = nodes[a]
    mb, sb = nodes[b]
    fm = p.flow('ControlFlow', ma, mb, name=name, guard=guard, hint='F_' + key)
    d.connector('ControlFlow', fm, sa, sb, points=pts,
                caption_xy=cap, caption_wh=(230, 34), hint='C_' + key)


def dec(key, text, cx, y, w=300, h=54):
    """Развилка: вопрос рисуется внутри ромба, как if (вопрос?) в PlantUML."""
    m = p.model('DecisionNode', name=text, hint='M_' + key)
    s = d.shape('DecisionNode', m, cx - w // 2, y, w, h, name=text, fill=FILL_GREY,
                hint='S_' + key)
    nodes[key] = (m, s)
    return s


def plain(key, model_type, shape_type, x, y, w, h, fill=None):
    m = p.model(model_type, hint='M_' + key)
    s = d.shape(shape_type, m, x, y, w, h, caption=False, fill=fill, hint='S_' + key)
    nodes[key] = (m, s)
    return s


# ─── узлы ────────────────────────────────────────────────────────────
plain('start', 'InitialNode', 'InitialNode', sw.center(L0, 30), 110, 30, 30)
act('ask', 'Запросить оценку риска маршрута', sw.center(L0, 300), 175, 300, 50)

act('take', 'Взять маршрут заявки\nи оценочную ценность груза', SPINE_X, 260, SPINE_W, 60)
act('req', 'Сформировать запрос об угрозах,\nперечислив контрольные точки маршрута', SPINE_X, 350,
    SPINE_W, 60)
act('ext', 'Обработать запрос об угрозах\nпо участкам маршрута', sw.center(L2, 300), 445, 300, 60)

dec('d1', 'данные об угрозах получены?', 700, 545)

act('accept', 'Принять угрозы по каждому участку\n(тип угрозы, уровень опасности)\nи дату '
              'актуальности данных', SPINE_X, 690, SPINE_W, 78)
act('aggr', 'Агрегировать угрозы участков\nи вычислить базовый risk_score маршрута', SPINE_X, 800,
    SPINE_W, 60)
act('cargo', 'Применить корректирующий коэффициент\nценности груза: чем дороже груз,\nтем выше '
             'итоговый risk_score', SPINE_X, 890, SPINE_W, 78)

dec('d2', 'дата актуальности\nсвежее 24 часов?', 700, 1000)
act('fresh', 'Признать оценку полученной\nна актуальных данных', COL_A_X, 1145, COL_A_W, 60)
act('stale1', 'Пометить оценку\n«На основе устаревших данных»', COL_B_X, 1145, COL_B_W, 60,
    fill=FILL_SAND)
act('stale2', 'Предупредить диспетчера\nоб устаревших данных', COL_B_X, 1235, COL_B_W, 60,
    fill=FILL_SAND)
plain('m2', 'MergeNode', 'MergeNode', SPINE_X + SPINE_W // 2 - 20, 1335, 40, 40, fill=FILL_GREY)

act('save', 'Сохранить итоговый risk_score\nв заявке и отобразить его диспетчеру', SPINE_X, 1415,
    SPINE_W, 60)
act('reco', 'Сформировать рекомендацию по минимальному\nсоставу охраны и объёму припасов (UC-8)',
    SPINE_X, 1505, SPINE_W, 60)

act('na', 'Установить risk_score = «Н/Д»', COL_C_X, 690, COL_C_W, 52, fill=FILL_PINK)
act('mark', 'Пометить заявку\n«risk_score требует пересчёта»', COL_C_X, 780, COL_C_W, 60,
    fill=FILL_PINK)
act('notify', 'Уведомить диспетчера о недоступности\nвнешней системы разведки', COL_C_X, 870,
    COL_C_W, 60, fill=FILL_PINK)

plain('m1', 'MergeNode', 'MergeNode', SPINE_X + SPINE_W // 2 - 20, 1605, 40, 40, fill=FILL_GREY)
act('explain', 'Сохранить разбор оценки\nдля показа диспетчеру', SPINE_X, 1685, SPINE_W, 60)

act('see', 'Увидеть в карточке заявки risk_score\nили «Н/Д», уровень риска, пометки\nи рекомендацию '
           '(если оценка получена)', sw.center(L0, 320), 1775, 320, 78)
plain('stop', 'ActivityFinalNode', 'ActivityFinalNode', sw.center(L0, 30), 1890, 30, 30)

# ─── потоки ──────────────────────────────────────────────────────────
ctrl('f1', 'start', 'ask')
ctrl('f2', 'ask', 'take')
ctrl('f3', 'take', 'req')
ctrl('f4', 'req', 'ext')
ctrl('f5', 'ext', 'd1')
ctrl('f6', 'd1', 'accept', guard='да', cap=(545, 630))
ctrl('f7', 'accept', 'aggr')
ctrl('f8', 'aggr', 'cargo')
ctrl('f9', 'cargo', 'd2')
ctrl('f10', 'd2', 'fresh', guard='да', cap=(470, 1055))
ctrl('f11', 'd2', 'stale1', guard='нет — альт. поток 2б', cap=(755, 1055),
     pts=[(850, 1027), (900, 1027), (900, 1145)])
ctrl('f12', 'stale1', 'stale2')
ctrl('f13', 'fresh', 'm2')
ctrl('f14', 'stale2', 'm2')
ctrl('f15', 'm2', 'save')
ctrl('f16', 'save', 'reco')
ctrl('f17', 'd1', 'na', guard='нет — альт. поток 2а', cap=(905, 598),
     pts=[(850, 572), (1132, 572), (1132, 690)])
ctrl('f18', 'na', 'mark')
ctrl('f19', 'mark', 'notify')
ctrl('f20', 'reco', 'm1')
ctrl('f21', 'notify', 'm1', pts=[(1132, 930), (1132, 1580), (700, 1580), (700, 1605)])
ctrl('f22', 'm1', 'explain')
ctrl('f23', 'explain', 'see')
ctrl('f24', 'see', 'stop')

# ─── заметки ─────────────────────────────────────────────────────────
NOTE_X = 1660


def note(key, text, y, h, anchor_to=None):
    m = p.note(text, hint='M_' + key)
    s = d.shape('NOTE', m, NOTE_X, y, 400, h, caption=False, fill=FILL_NOTE, hint='S_' + key)
    nodes[key] = (m, s)
    if anchor_to:
        am, asx = nodes[anchor_to]
        an = p.flow('Anchor', m, am, hint='A_' + key)
        d.connector('Anchor', an, s, asx, style=None, hint='CA_' + key)


note('pre', 'Предусловия прецедента\n'
            '• для заявки выбран или сформирован маршрут (UC-5)\n'
            '• указана оценочная ценность груза или её значение по умолчанию',
     250, 110, anchor_to='take')
note('post', 'Постусловия\n'
             '• основной поток и 2б: заявка содержит risk_score и рекомендацию\n'
             '• альт. поток 2а: расчёт можно повторить позднее',
     1685, 110, anchor_to='explain')
note('legend', 'Обозначения\n'
               '• дорожки: инициатор расчёта, система как единое целое,\n'
               '  внешняя система-поставщик данных об угрозах\n'
               '• сиреневым выделена дорожка внешней системы\n'
               '• розовым выделен альт. поток 2а (источник недоступен),\n'
               '  песочным — альт. поток 2б (данные старше 24 часов)\n'
               '\n'
               'Требования (docs/SRS.md)\n'
               '• FR-6 — интеграция с Wasteland Intel\n'
               '• FR-7 — автоматический расчёт risk_score\n'
               '• FR-8 — рекомендация по охране и припасам\n'
               '• FR-14 — учёт ценности груза',
     700, 230)

# заливка — последним ребёнком каждой фигуры
for _m, _s in nodes.values():
    d.finish_fill(_s)
d.finish_fill(sw.container)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', NAME + '.xml')
os.makedirs(os.path.dirname(out), exist_ok=True)
p.write(out)
print(out)
