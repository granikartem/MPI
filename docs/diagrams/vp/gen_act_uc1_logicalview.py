# -*- coding: utf-8 -*-
"""ACT_UC1_LogicalView: UC-1 «Создать заявку на перевозку», Activity Diagram (Logical View).

Содержание перенесено из docs/diagrams/sad/ACT_UC1_LogicalView.puml.
Девять вертикальных дорожек — логические компоненты диаграммы пакетов.
Раскладка задаётся здесь: колонка — дорожка, строка — шаг потока.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vpgen import (Project, Swimlanes, FILL_GREY, FILL_PINK, FILL_LILAC,  # noqa: E402
                   FILL_NOTE)

NAME = 'ACT_UC1_LogicalView'

p = Project(NAME)
d = p.diagram(NAME, 'ActivityDiagram')

# ─── дорожки ─────────────────────────────────────────────────────────
LANES = [('Диспетчер\nкараванов', 340),
         ('presentation\nИнтерфейс заявок', 340),
         ('application\nСоздание заявки', 620),
         ('application\nРасчёт ETA', 370),
         ('application\nОценка риска', 560),
         ('domain\nМаршрут, Заявка', 360),
         ('infrastructure\nХранение данных', 340),
         ('infrastructure\nАдаптер\nWasteland Intel', 320),
         ('«внешняя система»\nWasteland Intel', 300, FILL_LILAC)]
sw = Swimlanes(d, LANES, x=40, y=40, body_h=3210, header_h=70)
L_ACT, L_PRES, L_APP_REQ, L_APP_ETA, L_APP_RISK, L_DOM, L_INFRA, L_ADP, L_EXT = range(9)

# опорные колонки (абсолютные X, посчитаны от границ дорожек)
APP_REQ_X, APP_REQ_W = 750, 300        # основной столбец «Создание заявки»
APP_REQ_C = APP_REQ_X + APP_REQ_W // 2         # 900
REJ_X, REJ_W = 1070, 250               # отказ «организация не найдена»
REJ_C = REJ_X + REJ_W // 2                     # 1195

RISK_X, RISK_W = 1840, 300             # основной столбец «Оценка риска»
RISK_C = 1990
OK_X, OK_W = 1713, 274                 # ветка «да» развилки по угрозам
OK_C = OK_X + OK_W // 2                        # 1850 — ровно левая вершина ромба
ND_X, ND_W = 2020, 240                 # ветка «нет — альт. поток 4а»
ND_C = ND_X + ND_W // 2                        # 2140

DOM_X, DOM_W = 2280, 340
DOM_C = 2450
INF_X, INF_W = 2650, 300
INF_C = 2800
ADP_X, ADP_W = 2985, 290
ADP_C = 3130
EXT_X, EXT_W = 3310, 260
EXT_C = 3440
ACT_X, ACT_W = 60, 300
ACT_C = 210
PRES_X, PRES_W = 400, 300
PRES_C = 550
ETA_X, ETA_W = 1375, 300
ETA_C = 1525

DEC_W, DEC_H = 280, 54                 # ромб развилки: текст вопроса внутри

nodes = {}


def act(key, text, x, y, w, h, fill=FILL_GREY, parent=None):
    m = p.model('ActivityAction', name=text, hint='M_' + key)
    s = d.shape('ActivityAction', m, x, y, w, h, name=text, fill=fill, hint='S_' + key,
                parent=parent)
    nodes[key] = (m, s)
    return s


def plain(key, model_type, shape_type, x, y, w, h, fill=None):
    m = p.model(model_type, hint='M_' + key)
    s = d.shape(shape_type, m, x, y, w, h, caption=False, fill=fill, hint='S_' + key)
    nodes[key] = (m, s)
    return s


def dec(key, text, cx, y, w=DEC_W, h=DEC_H):
    """Развилка с вопросом внутри ромба — как в PlantUML (if (вопрос?))."""
    m = p.model('DecisionNode', name=text, hint='M_' + key)
    s = d.shape('DecisionNode', m, cx - w // 2, y, w, h, name=text,
                fill=FILL_GREY, hint='S_' + key)
    nodes[key] = (m, s)
    return s


def ctrl(key, a, b, guard=None, name=None, cap=None, cap_w=240, pts=None):
    ma, sa = nodes[a]
    mb, sb = nodes[b]
    fm = p.flow('ControlFlow', ma, mb, name=name, guard=guard, hint='F_' + key)
    d.connector('ControlFlow', fm, sa, sb, points=pts,
                caption_xy=cap, caption_wh=(cap_w, 34), hint='C_' + key)


# ─── узлы: основной поток ────────────────────────────────────────────
plain('start', 'InitialNode', 'InitialNode', ACT_C - 15, 160, 30, 30)
act('a1', 'Открыть форму создания заявки', ACT_X, 230, ACT_W, 46)
act('a2', 'Заполнить пункт отправления и назначения,\nдату отправки и описание груза',
    ACT_X, 320, ACT_W, 60)
act('a3', 'Передать данные заявки\nи выбранный способ задания маршрута',
    PRES_X, 420, PRES_W, 60)
act('a4', 'Определить организацию заявки', APP_REQ_X, 520, APP_REQ_W, 46)
act('a5', 'Выдать организацию\nили сообщить, что её нет', INF_X, 610, INF_W, 60)

dec('d1', 'организация существует?', APP_REQ_C, 700)
act('a6', 'Привязать заявку к организации:\nвсе её данные живут в изолированном\n'
          'пространстве организации (FR-24)', APP_REQ_X, 820, APP_REQ_W, 78)
act('a7', 'Отказать: организация не найдена', REJ_X, 820, REJ_W, 50, fill=FILL_PINK)
plain('stop1', 'ActivityFinalNode', 'ActivityFinalNode', REJ_C - 15, 920, 30, 30)

dec('d2', 'способ задания маршрута', APP_REQ_C, 950)
act('a8', 'Выдать шаблон маршрута\nс участками и контрольными точками',
    INF_X, 1070, INF_W, 60)
act('a9', 'Задать контрольные точки маршрута вручную', ACT_X, 1070, ACT_W, 46)
act('a10', 'Сформировать новый маршрут по участкам (UC-5)', 740, 1160, 320, 46)
act('a11', 'Сохранить маршрут, участки\nи новые контрольные точки', INF_X, 1250, INF_W, 60)
plain('m1', 'MergeNode', 'MergeNode', DOM_C - 20, 1360, 40, 40, fill=FILL_GREY)

act('a12', 'Маршрут: выдать участки в порядке следования\nи ключи участков «откуда — куда»',
    DOM_X, 1440, DOM_W, 60)
act('a13', 'Запросить данные об угрозах\nпо участкам маршрута (UC-7)',
    RISK_X, 1540, RISK_W, 60)
act('a14', 'Обратиться к внешней системе разведки', ADP_X, 1640, ADP_W, 46)
# Узел в залитой дорожке обязан быть дочерней фигурой её отсека: иначе заливка
# отсека закрывает его и на картинке остаётся пустое место (см. VisualParadigm.md).
d.child_shapes(sw.compartments[L_EXT])
act('a15', 'Вернуть угрозы по участкам\nи дату актуальности\nлибо не ответить',
    EXT_X, 1730, EXT_W, 78, parent=sw.compartments[L_EXT])

dec('d3', 'данные об угрозах получены?', RISK_C, 1840)
act('a16', 'Вычислить базовый risk_score маршрута\nпо уровням угроз участков',
    OK_X, 1965, OK_W, 60)
act('a17', 'Установить risk_score «Н/Д»\nи пометку «требует пересчёта»',
    ND_X, 1965, ND_W, 60, fill=FILL_PINK)
plain('m2', 'MergeNode', 'MergeNode', RISK_C - 20, 2090, 40, 40, fill=FILL_GREY)

act('a18', 'Сложить длины участков маршрута', ETA_X, 2170, ETA_W, 46)
act('a19', 'Разделить на среднюю скорость каравана\nи получить расчётное время в пути (UC-6)',
    1355, 2230, 340, 60)
act('a20', 'Указать оценочную ценность груза\nв крышках (UC-12)', ACT_X, 2330, ACT_W, 60)
act('a21', 'Пересчитать risk_score с учётом ценности груза\nи сформировать рекомендацию по '
           'составу\nохраны и объёму припасов (UC-8)', 1815, 2430, 350, 78)
act('a22', 'Показать сводку заявки: маршрут, ETA,\nrisk_score и рекомендацию',
    PRES_X, 2540, PRES_W, 60)

dec('d4', 'создание подтверждено?', ACT_C, 2630)
act('a23', 'Подтвердить создание заявки', ACT_X, 2750, ACT_W, 46)
act('a24', 'Закрыть форму, заявка не сохранена', PRES_X, 2750, PRES_W, 46, fill=FILL_PINK)
plain('stop2', 'ActivityFinalNode', 'ActivityFinalNode', PRES_C - 15, 2830, 30, 30)

act('a25', 'Заявка: собрать заявку в статусе «Черновик»\n'
           'с маршрутом, ETA, risk_score и рекомендацией', DOM_X, 2910, DOM_W, 60)
act('a26', 'Сохранить заявку и стартовую запись\nистории статусов', INF_X, 3000, INF_W, 60)
act('a27', 'Показать созданную заявку в реестре', PRES_X, 3090, PRES_W, 46)
act('a28', 'Увидеть заявку со статусом «Черновик»', ACT_X, 3170, ACT_W, 46)
plain('stop3', 'ActivityFinalNode', 'ActivityFinalNode', ACT_C - 15, 3250, 30, 30)

# ─── потоки ──────────────────────────────────────────────────────────
ctrl('f1', 'start', 'a1')
ctrl('f2', 'a1', 'a2')
ctrl('f3', 'a2', 'a3')
ctrl('f4', 'a3', 'a4')
ctrl('f5', 'a4', 'a5')
# вход в развилку — сверху: иначе он ложится на ту же горизонталь,
# по которой уходит ветка «нет», и две линии сливаются в одну
ctrl('f6', 'a5', 'd1', pts=[(INF_C, 670), (INF_C, 685), (APP_REQ_C, 685),
                            (APP_REQ_C, 700)])

ctrl('f7', 'd1', 'a6', guard='да', cap=(818, 768), cap_w=70)
ctrl('f8', 'd1', 'a7', guard='нет', cap=(1080, 690), cap_w=80,
     pts=[(APP_REQ_C + DEC_W // 2, 727), (REJ_C, 727), (REJ_C, 820)])
ctrl('f9', 'a7', 'stop1')
ctrl('f10', 'a6', 'd2')

# подписи ветвей — по центру свободных дорожек: иначе их режет граница дорожки
# (слева) или перекрывает финальный узел ветки отказа (справа)
ctrl('f11', 'd2', 'a8', name='[шаблон] основной поток', cap=(ETA_C - 120, 938),
     pts=[(APP_REQ_C + DEC_W // 2, 977), (INF_C, 977), (INF_C, 1070)])
ctrl('f12', 'd2', 'a9', name='[вручную] альт. поток 3а', cap=(PRES_C - 120, 938),
     pts=[(APP_REQ_C - DEC_W // 2, 977), (ACT_C, 977), (ACT_C, 1070)])
ctrl('f13', 'a9', 'a10')
ctrl('f14', 'a10', 'a11')
ctrl('f15', 'a8', 'm1', pts=[(INF_X, 1100), (DOM_C, 1100), (DOM_C, 1360)])
ctrl('f16', 'a11', 'm1', pts=[(INF_C, 1310), (INF_C, 1335), (DOM_C, 1335), (DOM_C, 1360)])

ctrl('f17', 'm1', 'a12')
ctrl('f18', 'a12', 'a13')
ctrl('f19', 'a13', 'a14')
ctrl('f20', 'a14', 'a15')
ctrl('f21', 'a15', 'd3', pts=[(EXT_C, 1808), (EXT_C, 1823), (RISK_C, 1823),
                              (RISK_C, 1840)])

# обе ветви уходят из боковых вершин ромба: подпись «нет» умещается между ними
# и не вылезает в соседнюю дорожку
ctrl('f22', 'd3', 'a16', guard='да', cap=(1760, 1918), cap_w=70,
     pts=[(RISK_C, 1894), (RISK_C, 1914), (OK_C, 1914), (OK_C, 1965)])
ctrl('f23', 'd3', 'a17', guard='нет — альт. поток 4а', cap=(1900, 1922),
     pts=[(RISK_C + DEC_W // 2, 1867), (ND_C, 1867), (ND_C, 1965)])
ctrl('f24', 'a16', 'm2', pts=[(OK_C, 2025), (OK_C, 2060), (RISK_C, 2060), (RISK_C, 2090)])
ctrl('f25', 'a17', 'm2', pts=[(ND_C, 2025), (ND_C, 2060), (RISK_C, 2060), (RISK_C, 2090)])

ctrl('f26', 'm2', 'a18')
ctrl('f27', 'a18', 'a19')
ctrl('f28', 'a19', 'a20')
ctrl('f29', 'a20', 'a21')
ctrl('f30', 'a21', 'a22')
ctrl('f31', 'a22', 'd4', pts=[(PRES_C, 2600), (PRES_C, 2615), (ACT_C, 2615),
                              (ACT_C, 2630)])

ctrl('f32', 'd4', 'a23', guard='да', cap=(128, 2700), cap_w=70)
ctrl('f33', 'd4', 'a24', guard='нет — альт. поток 8а', cap=(395, 2698), cap_w=220,
     pts=[(ACT_C + DEC_W // 2, 2657), (650, 2657), (650, 2750)])
ctrl('f34', 'a24', 'stop2')

ctrl('f35', 'a23', 'a25', pts=[(ACT_C, 2796), (ACT_C, 2885), (DOM_C, 2885), (DOM_C, 2910)])
ctrl('f36', 'a25', 'a26')
ctrl('f37', 'a26', 'a27')
ctrl('f38', 'a27', 'a28')
ctrl('f39', 'a28', 'stop3')

# ─── легенда ─────────────────────────────────────────────────────────
legend = p.note('Обозначения\n'
                '• дорожки — логические компоненты диаграммы пакетов\n'
                '  PKG_LogicalView; имена совпадают с участниками\n'
                '  Sequence, Cooperative и State Machine (Logical View)\n'
                '• розовым выделены альт. потоки 4а и 8а и отказы,\n'
                '  сиреневым — дорожка внешней системы\n'
                '\n'
                'Требования (docs/SRS.md)\n'
                '• FR-1, FR-5, FR-6, FR-7, FR-8, FR-14, FR-24\n'
                '• DC-6 (слои)', hint='M_legend')
legend_s = d.shape('NOTE', legend, 3650, 1500, 430, 170,
                   caption=False, fill=FILL_NOTE, hint='S_legend')

# заливка — последним ребёнком каждой фигуры
for _m, _s in nodes.values():
    d.finish_fill(_s)
d.finish_fill(legend_s)
for _s in sw.headers + sw.compartments:
    d.finish_fill(_s)
d.finish_fill(sw.container)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', NAME + '.xml')
os.makedirs(os.path.dirname(out), exist_ok=True)
p.write(out)
print(out)
