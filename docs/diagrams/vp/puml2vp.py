# -*- coding: utf-8 -*-
"""Сборка проекта Visual Paradigm по исходнику PlantUML.

Почему это вообще возможно одним инструментом. Раньше каждая диаграмма
собиралась вручную, и дороже всего обходилась раскладка: в `.puml` координат
нет, а Visual Paradigm требует x/y/width/height у каждой фигуры, поэтому
положение подбиралось на глаз за несколько прогонов. Теперь раскладку считает
сам PlantUML — мы берём её из его SVG (`svgpos`) и сопоставляем с элементами
исходника по тексту. Остаётся перевести смысл: тип фигуры, тип модели, связи.

Устройство: общая часть `Conv` (раскладка, заметки, легенда, запись файла) плюс
по разборщику на тип диаграммы. Разборщик решает только «что это за элемент»,
но не «где он лежит».

Запуск:

    python puml2vp.py SM_UC2_UseCaseView [ещё имена...]
    python puml2vp.py --all
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xml.etree.ElementTree as ET                              # noqa: E402
import svgpos                                                   # noqa: E402
from vpgen import Project, FILL_NOTE, _q                        # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
PUML_DIR = os.path.join(ROOT, 'docs', 'diagrams', 'sad')
OUT_DIR = os.path.join(HERE, 'out')
SVG_DIR = os.path.join(HERE, 'out', 'svg')
JAR = os.path.join(ROOT, 'docs', 'tools', 'plantuml', 'plantuml.jar')

# PlantUML верстает под свои метрики шрифта, Visual Paradigm — под свои и крупнее.
# Общий коэффициент разносит фигуры так, чтобы подписи не слипались.
SCALE = 1.45
PAD = 40

ARROW = re.compile(r'-{1,2}(?:up|down|left|right)?-{0,2}>{1,2}')


def clean_label(label):
    """Подпись без разметки PlantUML и стереотип отдельно.

    В Visual Paradigm нет ни полужирного внутри имени, ни записи `<<...>>`:
    оставь их в тексте — они так и нарисуются звёздочками и угловыми скобками.
    Стереотип становится настоящим стереотипом модели.
    """
    st = re.search(r'<<(.+?)>>', label)
    text = re.sub(r'<<.+?>>', '', label)
    text = re.sub(r'<size:\d+>|</size>|<[a-z/][^>]*>', '', text)
    text = text.replace('**', '')
    text = '\n'.join(' '.join(x.split()) for x in text.split('\n'))
    return text.strip('\n '), (st.group(1).strip() if st else None)


def fill_of(svg_color):
    """Цвет заливки из SVG (#RRGGBB) в формат Visual Paradigm."""
    if not svg_color or svg_color == 'none':
        return None
    s = svg_color.lstrip('#')
    if len(s) != 6:
        return None
    return 'Cr:%d,%d,%d,255' % (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


class Conv(object):
    """Общая часть конвертации: раскладка, проект, заметки, запись."""

    def __init__(self, name, diagram_type):
        self.name = name
        self.puml = os.path.join(PUML_DIR, name + '.puml')
        self.src = open(self.puml, encoding='utf-8').read()
        self.L = svgpos.layout_of(self.puml, SVG_DIR, JAR)
        self.p = Project(name)
        self.d = self.p.diagram(name, diagram_type)
        self.shapes = {}          # ключ -> (модель, фигура)
        self._used = set()        # какие фигуры SVG уже разобраны
        self._fills = []          # заливки доливаются в самом конце, см. write()
        self._n = 0
        self.top = PAD
        self.title = self._title()
        if self.title:
            self._put_title()

    def _title(self):
        m = re.search(r'^title[ \t]+(.+)$', self.src, re.M)
        return m.group(1).strip().replace('\\n', '\n') if m else ''

    def _put_title(self):
        """Заголовок: свойства заголовка в формате Visual Paradigm нет, ставим надписью.

        Фигура `TextBox` поверх модели `NOTE`, текст — атрибутом `name`. Модели
        с типом `TextBox` не существует, а текст из documentation эта фигура не
        показывает: проверено рендером, в обоих случаях выходит пустая рамка.

        Место берём там же, где его отвёл PlantUML, — сверху над диаграммой.
        """
        lines = self.title.split('\n')
        b = self.L.find_label(self.title)
        w = max(int(max(len(x) for x in lines) * 9.5), 400)
        x, y = (self.rect(b)[:2] if b is not None else (PAD, PAD))
        m = self.p.model('NOTE', name=self.title, hint='Mtitle')
        s = self.d.shape('TextBox', m, x, y, w, 26 * len(lines),
                         name=self.title, hint='Stitle')
        self.d.finish_fill(s)

    # ---- геометрия ---------------------------------------------------
    def box(self, text, required=True):
        """Габариты элемента по его тексту, уже в координатах Visual Paradigm."""
        b = self.L.find(text, required=required)
        if b is None:
            return None
        self._used.add(id(b))
        return self.rect(b)

    def rect(self, b, min_w=0, min_h=0):
        return (int(b.x * SCALE) + PAD, int(b.y * SCALE) + self.top,
                max(int(b.w * SCALE), min_w), max(int(b.h * SCALE), min_h))

    def label_xy(self, text):
        """Положение подписи связи; None — пусть Visual Paradigm ставит сам."""
        b = self.L.find_label(text)
        if b is None:
            return None, (200, 34)
        x, y, w, h = self.rect(b)
        return (x, y), (max(w, 60), max(h, 20))

    # ---- элементы ----------------------------------------------------
    def node(self, key, shape_type, model_type, text, geom, fill=None, caption=None,
             owner=None):
        x, y, w, h = geom
        m = self.p.model(model_type, name=text or None, hint='M%d' % self._bump(),
                         parent=self.p.children(owner) if owner is not None else None)
        s = self.d.shape(shape_type, m, x, y, w, h,
                         name=(text if caption is None else caption) or None,
                         fill=fill, hint='S%d' % self._n)
        self._fills.append(s)
        self.shapes[key] = (m, s)
        return m, s

    def nest(self, child, parent):
        """Переносит фигуру внутрь родительской."""
        self.d.shapes.remove(child.el)
        self.d.child_shapes(parent).append(child.el)

    def edge(self, shape_type, model_type, a, b, label=None, guard=None, style='Rectlinear'):
        ma, sa = self.shapes[a]
        mb, sb = self.shapes[b]
        fm = self.p.flow(model_type, ma, mb, name=label or None, guard=guard,
                         hint='F%d' % self._bump())
        xy, wh = self.label_xy(label) if label else (None, (200, 34))
        return self.d.connector(shape_type, fm, sa, sb, caption_xy=xy, caption_wh=wh,
                                style=style, hint='C%d' % self._n)

    def _bump(self):
        self._n += 1
        return self._n

    # ---- заметки и легенда -------------------------------------------
    def notes(self, anchors=None):
        """Заметки и легенда: текст из исходника, место — из раскладки.

        Текст берётся именно из `.puml`, а не из фигуры в SVG: заметка рисуется
        контуром со сложенным углом, и её габариты часто накрывают стоящие рядом
        подписи связей — в текст фигуры попадает чужое.

        Якорь к элементу ставится, если разборщик передал соответствие
        «первая строка заметки -> ключ элемента».
        """
        anchors = anchors or {}
        for text, target in source_notes(self.src):
            head = text.split('\n')[0]
            want = {svgpos.norm(l) for l in text.split('\n') if svgpos.norm(l)}
            # по одной первой строке не опознать: легенду-таблицу PlantUML
            # разбирает на ячейки, и её первая строка в SVG совсем другая
            cands = [x for x in self.L.nodes if id(x) not in self._used and x.lines
                     and (x.fill or '').upper() in ('#FEFFDD', '#DDDDDD')]
            b = max(cands, key=lambda x: len(want & {svgpos.norm(l) for l in x.lines}),
                    default=None)
            if b is None or not (want & {svgpos.norm(l) for l in b.lines}):
                print('  заметка %r не найдена в раскладке' % head[:40], file=sys.stderr)
                continue
            self._used.add(id(b))
            key = 'note%d' % self._bump()
            m = self.p.note(text, hint='M' + key)
            x, y, w, h = self.rect(b, min_w=180, min_h=60)
            s = self.d.shape('NOTE', m, x, y, w, h, caption=False,
                             fill=FILL_NOTE, hint='S' + key)
            self.d.finish_fill(s)
            target = target or anchors.get(b.lines[0].strip())
            if target and target in self.shapes:
                am = self.p.flow('Anchor', m, self.shapes[target][0], hint='A' + key)
                self.d.connector('Anchor', am, s, self.shapes[target][1],
                                 style=None, hint='CA' + key)

    def _restack(self):
        """Порядок по глубине: большая фигура — назад, мелкая — вперёд.

        В Visual Paradigm больший `zorder` означает «дальше от зрителя».
        Нумерация в порядке создания даёт контейнеру меньший номер, то есть
        выводит его поверх собственного содержимого, и вложенные узлы просто
        закрашиваются родителем — на картинке их нет, хотя в проекте они есть.
        """
        q = ET.ElementTree(self.d.el).iter(_q('Shape'))
        all_shapes = sorted(q, key=lambda e: -(int(e.get('width')) * int(e.get('height'))))
        for i, el in enumerate(all_shapes):
            el.set('zorder', str(len(all_shapes) - i))

    def write(self):
        # FillColor обязан быть последним ребёнком фигуры, а вложенные фигуры
        # добавляются уже после её создания: залив цвет сразу, мы ставим
        # ChildShapes после FillColor, и импорт молча теряет всё вложенное
        for s in self._fills:
            self.d.finish_fill(s)
        self._restack()
        os.makedirs(OUT_DIR, exist_ok=True)
        path = os.path.join(OUT_DIR, self.name + '.xml')
        self.p.write(path)
        return path


# ======================================================================
#  Диаграмма состояний
# ======================================================================

RE_STATE = re.compile(r'^state\s+"(?P<label>.+?)"\s+as\s+(?P<alias>\w+)'
                      r'(?P<tail>[^{]*)(?P<open>\{)?\s*$')
RE_DESCR = re.compile(r'^(?P<alias>\w+)\s*:\s*(?P<text>.+)$')
RE_TRANS = re.compile(r'^(?P<a>\[\*\]|\w+)\s*' + ARROW.pattern +
                      r'\s*(?P<b>\[\*\]|\w+)\s*(?::\s*(?P<label>.+))?$')


def parse_states(src):
    """Состояния и переходы с учётом вложенности `state ... { ... }`.

    Область важна не только для иерархии: у каждой области свой `[*]`, и без
    неё начальные псевдосостояния не развести по нужным машинам.
    """
    states, trans, stack = {}, [], []
    for raw in src.splitlines():
        line = raw.strip()
        if line == '}':
            if stack:
                stack.pop()
            continue
        m = RE_STATE.match(line)
        if m:
            tail = m.group('tail') or ''
            st = re.search(r'<<(.+?)>>', tail)
            col = re.search(r'(#\w+)', tail)
            states[m.group('alias')] = {
                'label': m.group('label').replace('\\n', '\n'),
                'parent': stack[-1] if stack else None,
                'stereo': st.group(1).strip() if st else None,
                'color': col.group(1) if col else None,
                'composite': bool(m.group('open')),
            }
            if m.group('open'):
                stack.append(m.group('alias'))
            continue
        m = RE_TRANS.match(line)
        if m:
            if m.group('a') == '[*]' and m.group('b') == '[*]':
                continue
            trans.append((m.group('a'), m.group('b'),
                          (m.group('label') or '').strip().replace('\\n', '\n'),
                          stack[-1] if stack else None))
            continue
        m = RE_DESCR.match(line)
        if m and m.group('alias') in states:
            states[m.group('alias')].setdefault('descr', []).append(
                m.group('text').replace('\\n', '\n'))
    return states, trans


def convert_state(name):
    """Диаграмма состояний: состояния, переходы, начальный и конечный узлы."""
    c = Conv(name, 'StateDiagram')
    states, trans = parse_states(c.src)

    # габариты: у составного состояния текст принадлежит полосе заголовка,
    # а границы задаёт незалитая рамка вокруг неё
    frames = {}
    for alias, st in states.items():
        b = c.L.find(st['label'], required=False)
        if b is None:
            raise SystemExit('%s: состояния %r нет в раскладке' % (name, st['label']))
        c._used.add(id(b))
        st['box'] = c.L.frame_of(b) if st['composite'] else b
        st['text'] = b.text if not st['composite'] else st['label']
        st['fill'] = fill_of(b.fill)
        if st['composite']:
            frames[alias] = st['box']

    # внешние состояния раньше вложенных: фигура-родитель должна уже существовать
    def depth(alias):
        d, cur = 0, states[alias]['parent']
        while cur:
            d, cur = d + 1, states[cur]['parent']
        return d

    for alias in sorted(states, key=depth):
        st = states[alias]
        parent = c.shapes[st['parent']][1] if st['parent'] else None
        m, s = c.node(alias, 'State2', 'State2', st['text'],
                      c.rect(st['box'], min_w=120, min_h=56),
                      fill=st['fill'])
        if parent is not None:
            c.nest(s, parent)
        if st['stereo']:
            c.p.ref_prop(m, 'stereotypes', c.p.stereotype(st['stereo'], base='State').id)

    # область кружка определяется самой внутренней рамкой, которая его накрывает:
    # так `[*]` каждой вложенной машины достаётся своей
    def scope_of(e):
        inner, best = None, None
        for alias, f in frames.items():
            if f.contains(e.x + e.w / 2, e.y + e.h / 2) and (best is None or f.area < best):
                inner, best = alias, f.area
        return inner

    rings = [e for e in c.L.marks if not e.fill or e.fill == 'none']
    in_ring = lambda e: any(r is not e and r.contains(e.x + e.w / 2, e.y + e.h / 2)
                            for r in rings)
    pseudo = {}                      # (область, вид) -> ключ фигуры
    for i, e in enumerate(sorted(rings, key=lambda b: (b.y, b.x))):
        key = 'final%d' % i
        c.node(key, 'FinalState2', 'FinalState2', '', c.rect(e, min_w=34, min_h=34))
        pseudo.setdefault((scope_of(e), 'out'), key)
    for i, e in enumerate(sorted((x for x in c.L.marks
                                  if x not in rings and not in_ring(x)),
                                 key=lambda b: (b.y, b.x))):
        key = 'init%d' % i
        c.node(key, 'InitialPseudoState', 'InitialPseudoState', '',
               c.rect(e, min_w=30, min_h=30))
        pseudo.setdefault((scope_of(e), 'in'), key)

    def endpoint(tok, scope, kind):
        if tok != '[*]':
            return tok if tok in c.shapes else None
        cur = scope
        while True:                  # своя область, затем объемлющие
            if (cur, kind) in pseudo:
                return pseudo[(cur, kind)]
            if cur is None:
                return None
            cur = states[cur]['parent']

    for a, b, label, scope in trans:
        ka = endpoint(a, scope, 'in')
        kb = endpoint(b, scope, 'out')
        if ka is None or kb is None:
            print('  пропущен переход %s -> %s (нет фигуры)' % (a, b), file=sys.stderr)
            continue
        c.edge('Transition2', 'Transition2', ka, kb, label=label or None, style=None)

    c.notes(anchors=note_anchors(c.src, states))
    return c.write()


def clean_note(text):
    """Текст заметки без разметки PlantUML.

    В отличие от подписи элемента стереотип здесь не вырезается: заметки и
    легенды сами объясняют, что означают `<<actor>>`, `<<boundary>>` и прочие,
    и без них остались бы пустые тире.
    """
    text = re.sub(r'<<([^<>]*)>>', r'«\1»', text)
    text = re.sub(r'<size:\d+>|</size>|<[a-z/][^>]*>', '', text)
    return text.replace('**', '').strip('\n ')


RE_NOTE = re.compile(r'^note\s+(?:(?:left|right|top|bottom|over)'
                     r'(?:\s+(?:of\s+)?(?P<alias>\w+))?)?\s*$', re.I)


def source_notes(src):
    """Заметки и легенда из исходника: [(текст, псевдоним элемента или None)]."""
    out, buf, target, mode = [], None, None, None
    for raw in src.splitlines():
        line = raw.rstrip()
        s = line.strip()
        if mode is None:
            m = RE_NOTE.match(s)
            if m:
                buf, target, mode = [], m.group('alias'), 'note'
            elif re.match(r'^legend\b', s, re.I):
                buf, target, mode = [], None, 'legend'
            continue
        if (mode == 'note' and s.lower() in ('end note', 'endnote')) \
                or (mode == 'legend' and s.lower() in ('endlegend', 'end legend')):
            text = clean_note('\n'.join(buf).strip('\n'))
            if text:
                out.append((text, target))
            buf, target, mode = None, None, None
            continue
        buf.append(line)
    return out


def note_anchors(src, labels):
    """Соответствие «первая строка заметки -> псевдоним элемента» из `note ... of X`."""
    out = {}
    lines = src.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r'^note\s+\w+\s+of\s+(\w+)\s*$', line.strip())
        if not m:
            continue
        for nxt in lines[i + 1:]:
            if nxt.strip():
                out[nxt.strip()] = m.group(1)
                break
    return out


# ======================================================================
#  Диаграммы из вложенных контейнеров: пакетов и узлов развёртывания
# ======================================================================

RE_DECL = re.compile(r'^(?P<kw>package|node|rectangle|artifact|database|component|cloud|folder)'
                     r'\s+"(?P<label>.+?)"\s+as\s+(?P<alias>\w+)'
                     r'(?P<tail>[^{]*)(?P<open>\{)?\s*$')
RE_LINK = re.compile(r'^(?P<a>\w+)\s*(?P<arrow>[-.][^\s]*>)\s*(?P<b>\w+)'
                     r'\s*(?::\s*(?P<label>.+))?$')

# как ложатся элементы PlantUML на типы Visual Paradigm
KINDS = {
    'package':   ('Package', 'Package', None),
    'folder':    ('Package', 'Package', None),
    'node':      ('Node', 'Node', None),
    'cloud':     ('Node', 'Node', 'cloud'),
    'artifact':  ('Artifact', 'Artifact', None),
    # отдельного типа «хранилище данных» в Visual Paradigm нет — узел со стереотипом
    'database':  ('Node', 'Node', 'database'),
    'component': ('Component', 'Component', None),
    'rectangle': ('Component', 'Component', None),
}


def parse_containers(src):
    """Объявления с учётом вложенности и связи между ними."""
    items, links, stack = {}, [], []
    for raw in src.splitlines():
        line = raw.strip()
        if line == '}':
            if stack:
                stack.pop()
            continue
        m = RE_DECL.match(line)
        if m:
            tail = m.group('tail') or ''
            col = re.search(r'(#\w+)', tail)
            items[m.group('alias')] = {
                'kw': m.group('kw'),
                'label': m.group('label').replace('\\n', '\n'),
                'parent': stack[-1] if stack else None,
                'color': col.group(1) if col else None,
                'container': bool(m.group('open')),
            }
            if m.group('open'):
                stack.append(m.group('alias'))
            continue
        m = RE_LINK.match(line)
        if m and 'hidden' not in m.group('arrow'):
            links.append((m.group('a'), m.group('b'), m.group('arrow'),
                          (m.group('label') or '').strip().replace('\\n', '\n')))
    return items, links


def convert_containers(name, diagram_type):
    """Диаграмма пакетов или развёртывания: вложенные контейнеры и связи."""
    c = Conv(name, diagram_type)
    items, links = parse_containers(c.src)

    def depth(alias):
        d, cur = 0, items[alias]['parent']
        while cur:
            d, cur = d + 1, items[cur]['parent']
        return d

    # снаружи внутрь: границы родителя нужны, чтобы различить одинаковые подписи
    for alias in sorted(items, key=depth):
        it = items[alias]
        head = it['label'].split('\n')[0]
        outer = items[it['parent']]['box'] if it['parent'] else None
        # сперва по полной подписи: первая строка бывает общей у нескольких
        # элементов («БД karavany»), и по ней они неразличимы
        b = (c.L.find(it['label'], required=False, within=outer)
             or c.L.find(head, required=False, within=outer))
        if b is None:
            # пакет-«папка» рисуется незалитым контуром, имя стоит в ярлычке
            lbl = c.L.find_label(head, within=outer)
            b = c.L.frame_at(lbl.x + 4, lbl.y + 14) if lbl is not None else None
        if b is None:
            raise SystemExit('%s: элемента %r нет в раскладке' % (name, head))
        c._used.add(id(b))
        it['box'] = b

    for alias in sorted(items, key=depth):
        it = items[alias]
        shape_type, model_type, kind_stereo = KINDS[it['kw']]
        text, stereo = clean_label(it['label'])
        owner, parent = (c.shapes[it['parent']] if it['parent'] else (None, None))
        m, s = c.node(alias, shape_type, model_type, text,
                      c.rect(it['box'], min_w=120, min_h=50), owner=owner,
                      # незалитый контейнер Visual Paradigm красит цветом по
                      # умолчанию, и вложенные пакеты сливаются с родителем
                      fill=(fill_of(svg_color(it['color'])) or fill_of(it['box'].fill)
                            or fill_of('#FFFFFF')))
        if parent is not None:
            c.nest(s, parent)
        for name in filter(None, (stereo, kind_stereo)):
            c.p.ref_prop(m, 'stereotypes', c.p.stereotype(name, base=model_type).id)

    for a, b, arrow, label in links:
        if a not in c.shapes or b not in c.shapes:
            print('  пропущена связь %s -> %s (нет фигуры)' % (a, b), file=sys.stderr)
            continue
        dashed = arrow.startswith('.') or '..' in arrow or '.[' in arrow
        kind = 'Dependency' if dashed else 'Association'
        c.edge(kind, kind, a, b, label=label or None)

    c.notes(anchors=note_anchors(c.src, items))
    return c.write()


# ======================================================================
#  Диаграмма последовательности
# ======================================================================

RE_PART = re.compile(r'^(?P<kw>actor|participant|boundary|control|entity|database|collections)'
                     r'\s+"(?P<label>.+?)"\s+as\s+(?P<alias>\w+)(?P<tail>.*)$')
RE_MSG = re.compile(r'^(?P<a>\w+)\s*(?P<arrow>-{1,2}>{1,2}|<-{1,2}|-{2}>{1,2})\s*'
                    r'(?P<b>\w+)\s*(?::\s*(?P<text>.+))?$')
RE_FRAG = re.compile(r'^(?P<kw>alt|opt|loop|par|group|critical|break)\b\s*(?P<label>.*)$')

# на диаграмме последовательности Visual Paradigm различает только два типа линии
SEQ_KINDS = {'actor': 'InteractionActor'}


def parse_sequence(src):
    """Участники, сообщения и комбинированные фрагменты по порядку."""
    parts, msgs, frags, stack = {}, [], [], []
    order = []
    for raw in src.splitlines():
        line = raw.strip()
        if not line or line.startswith("'") or line.startswith('skinparam'):
            continue
        m = RE_PART.match(line)
        if m:
            st = re.search(r'<<(.+?)>>', m.group('tail') or '')
            parts[m.group('alias')] = {'kw': m.group('kw'),
                                       'label': m.group('label').replace('\\n', '\n'),
                                       'stereo': st.group(1).strip() if st else None}
            order.append(m.group('alias'))
            continue
        m = RE_FRAG.match(line)
        if m:
            f = {'kw': m.group('kw'), 'operands': [m.group('label').strip()],
                 'index': len(frags)}
            frags.append(f)
            stack.append(f)
            continue
        if line.startswith('else'):
            if stack:
                stack[-1]['operands'].append(line[4:].strip())
            continue
        if line == 'end' or line == 'end group':
            if stack:
                stack.pop()
            continue
        m = RE_MSG.match(line)
        if m and m.group('a') in parts and m.group('b') in parts:
            msgs.append({'a': m.group('a'), 'b': m.group('b'),
                         'arrow': m.group('arrow'),
                         'text': (m.group('text') or '').strip().replace('\\n', '\n')})
    return parts, order, msgs, frags


def convert_sequence(name):
    """Диаграмма последовательности: линии жизни, сообщения, альтернативы."""
    c = Conv(name, 'InteractionDiagram')
    parts, order, msgs, frags = parse_sequence(c.src)

    # Visual Paradigm нумерует сообщения сам; у нас номера свои, смысловые
    _set_diagram_prop(c.d, 'showSequenceNumbers', 'false')

    # верх и низ линий жизни: PlantUML повторяет заголовки внизу, берём крайние
    tops, bottoms = [], []
    for alias in order:
        hits = (c.L.find_all(parts[alias]['label'])
                or [c.L.find_label(parts[alias]['label'])])
        hits = [h for h in hits if h is not None]
        if not hits:
            raise SystemExit('%s: участника %r нет в раскладке'
                             % (name, parts[alias]['label']))
        parts[alias]['box'] = hits[0]
        tops.append(hits[0].y)
        bottoms.append(hits[-1].y + hits[-1].h)
    top, bottom = min(tops), max(bottoms)

    for alias in order:
        it = parts[alias]
        b = it['box']
        c._used.add(id(b))
        shape_type = SEQ_KINDS.get(it['kw'], 'InteractionLifeLine')
        text, stereo = clean_label(it['label'])
        x = int(b.x * SCALE) + PAD
        m, s = c.node(alias, shape_type, shape_type, text,
                      (x, int(top * SCALE) + c.top, max(int(b.w * SCALE), 120),
                       int((bottom - top) * SCALE)),
                      # без явной заливки Visual Paradigm красит линию жизни
                      # актора своим синим по умолчанию
                      fill=fill_of(b.fill) or fill_of('#F5F5F5'))
        it['cx'] = x + max(int(b.w * SCALE), 120) // 2
        for nm in filter(None, (stereo or it['stereo'],)):
            c.p.ref_prop(m, 'stereotypes', c.p.stereotype(nm, base=shape_type).id)

    # фрагменты: ярлычок с оператором стоит у левого верхнего угла рамки
    for f in frags:
        # ярлычок с оператором PlantUML рисует отдельной залитой фигурой,
        # а не свободным текстом, и у каждой рамки он свой
        tab = next((t for t in c.L.find_all(f['kw']) if id(t) not in c._used), None)
        box = c.L.frame_at(tab.x + 2, tab.y + tab.h + 2) if tab is not None else None
        if box is None:
            print('  рамка %s не найдена в раскладке' % f['kw'], file=sys.stderr)
            continue
        c._used.add(id(tab))
        key = 'frag%d' % f['index']
        mf, sf = c.node(key, 'CombinedFragment', 'CombinedFragment', f['kw'],
                        c.rect(box, min_w=200, min_h=80))
        ET.SubElement(mf.props, _q('StringProperty'),
                      {'name': 'interactionOperator', 'value': f['kw']})
        # секции: от подписи сторожевого условия до следующей
        gy = []
        for g in f['operands']:
            lbl = c.L.find_label(g) if g else None
            gy.append(lbl.y if lbl is not None else None)
        x, y, w, h = c.rect(box, min_w=200, min_h=80)
        for i, g in enumerate(f['operands']):
            y0 = int(gy[i] * SCALE) + c.top if gy[i] is not None else y + i * (h // len(f['operands']))
            y1 = (int(gy[i + 1] * SCALE) + c.top
                  if i + 1 < len(gy) and gy[i + 1] is not None else y + h)
            mo = c.p.model('InteractionOperand', name=g or None, hint='Mo%d' % c._bump())
            so = c.d.shape('InteractionOperand', mo, x, max(y0, y), w,
                           max(y1 - max(y0, y), 30), name=g or None, hint='So%d' % c._n)
            c.nest(so, sf)
            c._fills.append(so)

    for i, msg in enumerate(msgs):
        a, b = parts[msg['a']], parts[msg['b']]
        lbl = c.L.find_label(msg['text']) if msg['text'] else None
        if lbl is None:
            print('  сообщение %r не найдено в раскладке' % msg['text'][:40],
                  file=sys.stderr)
            continue
        y = int((lbl.y + lbl.h) * SCALE) + c.top
        kind = 'Message'
        if msg['a'] == msg['b']:
            kind = 'SequenceSelfMessage'
        mm = c.p.flow(kind, c.shapes[msg['a']][0], c.shapes[msg['b']][0],
                      name=msg['text'], hint='Mm%d' % c._bump())
        cn = c.d.connector(kind, mm, c.shapes[msg['a']][1], c.shapes[msg['b']][1],
                           style=None, hint='Cm%d' % c._n,
                           caption_xy=(min(a['cx'], b['cx']) + 12, y - 24),
                           caption_wh=(max(abs(a['cx'] - b['cx']) - 24, 120), 22))
        pts = ET.SubElement(cn, _q('Points'))
        if kind == 'SequenceSelfMessage':
            # обращение к себе рисуется петлёй: двух точек на одной линии
            # жизни недостаточно, связь просто не появляется на картинке
            for px, py in ((a['cx'], y), (a['cx'] + 70, y),
                           (a['cx'] + 70, y + 28), (a['cx'], y + 28)):
                ET.SubElement(pts, _q('Point'), {'x': str(px), 'y': str(py)})
        else:
            ET.SubElement(pts, _q('Point'), {'x': str(a['cx']), 'y': str(y)})
            ET.SubElement(pts, _q('Point'), {'x': str(b['cx']), 'y': str(y)})

    c.notes()
    return c.write()


# ======================================================================
#  Кооперативная (коммуникационная) диаграмма
# ======================================================================

RE_OBJ = re.compile(r'^object\s+"(?P<label>.+?)"\s+as\s+(?P<alias>\w+)(?P<tail>.*)$')


def convert_communication(name):
    """Кооперативная диаграмма: аналитические объекты и нумерованные сообщения.

    Сообщение в Visual Paradigm живёт на связи между линиями жизни: отдельная
    фигура `CommunicationMessage` через `ImportXML` не проходит — импорт падает
    с ClassCastException. Поэтому на каждую пару идёт одна связь, а нумерованный
    текст становится её подписью; в исходнике на паре и так ровно одна стрелка.
    """
    c = Conv(name, 'CommunicationDiagram')
    objs, links = {}, []
    for raw in c.src.splitlines():
        line = raw.strip()
        m = RE_OBJ.match(line)
        if m:
            st = re.search(r'<<(.+?)>>', m.group('tail') or '')
            col = re.search(r'(#\w+)', re.sub(r'<<.+?>>', '', m.group('tail') or ''))
            objs[m.group('alias')] = {
                'label': m.group('label').replace('\\n', '\n'),
                'stereo': st.group(1).strip() if st else None,
                'color': col.group(1) if col else None}
            continue
        m = RE_LINK.match(line)
        if m and 'hidden' not in m.group('arrow') and m.group('a') in objs:
            links.append((m.group('a'), m.group('b'),
                          (m.group('label') or '').strip().replace('\\n', '\n')))

    for alias, it in objs.items():
        b = c.L.find(it['label'], required=False)
        if b is None:
            raise SystemExit('%s: объекта %r нет в раскладке' % (name, it['label']))
        c._used.add(id(b))
        actor = (it['stereo'] or '').lower() == 'actor'
        shape_type = 'CommunicationActor' if actor else 'CommunicationLifeLine'
        model_type = 'InteractionActor' if actor else 'InteractionLifeLine'
        text, _st = clean_label(it['label'])
        # стереотип пишем прямо в имени: у линии жизни Visual Paradigm его
        # не показывает, а вся кооперативная диаграмма на нём и держится —
        # «boundary», «control», «entity» объяснены в легенде
        if it['stereo'] and not actor:
            text = '«%s»\n%s' % (it['stereo'], text)
        c.node(alias, shape_type, model_type, text,
               c.rect(b, min_w=160, min_h=60),
               fill=fill_of(svg_color(it['color'])) or fill_of(b.fill))

    for i, (a, b, label) in enumerate(links):
        if a not in c.shapes or b not in c.shapes:
            continue
        lk = c.p.model('InteractionLifeLineLink', name=label or None,
                       hint='Ml%d' % c._bump())
        c.p.ref_prop(lk, 'from', c.shapes[a][0].id)
        c.p.ref_prop(lk, 'to', c.shapes[b][0].id)
        xy, wh = c.label_xy(label) if label else (None, (200, 34))
        c.d.connector('InteractionLifeLineLink', lk, c.shapes[a][1], c.shapes[b][1],
                      style=None, hint='Cl%d' % c._n, caption_xy=xy, caption_wh=wh)

    c.notes()
    return c.write()


# ======================================================================
#  Диаграммы базы данных: ER-модель и даталогическая
# ======================================================================

RE_TABLE = re.compile(r'^(?:entity\s+"(?P<elabel>.+?)"\s+as\s+(?P<ealias>\w+)'
                      r'|class\s+(?P<calias>\w+)(?P<ctail>[^{]*))\s*\{\s*$')
RE_REL = re.compile(r'^(?P<a>\w+)\s+"(?P<am>[^"]+)"\s+(?P<line>--|\.\.)\s+'
                    r'"(?P<bm>[^"]+)"\s+(?P<b>\w+)\s*(?::\s*(?P<label>.+))?$')
RE_COL = re.compile(r'^(?P<name>.+?)(?:\s*:\s*(?P<type>.+?))?\s*$')


def parse_tables(src):
    """Таблицы с колонками и связи между ними."""
    tables, rels, cur = {}, [], None
    for raw in src.splitlines():
        line = raw.strip()
        if cur is not None:
            if line == '}':
                cur = None
                continue
            tables[cur]['cols'].append(line)
            continue
        m = RE_TABLE.match(line)
        if m:
            alias = m.group('ealias') or m.group('calias')
            label = m.group('elabel') or alias
            tables[alias] = {'label': label, 'cols': []}
            cur = alias
            continue
        m = RE_REL.match(line)
        if m and not line.startswith("'"):
            rels.append((m.group('a'), m.group('b'), m.group('line'),
                         m.group('am'), m.group('bm'),
                         (m.group('label') or '').strip()))
    return tables, rels


def parse_column(line):
    """Строка описания колонки: имя, тип и признаки.

    Форма различается у двух диаграмм — концептуальной (`* название <<PK>>`)
    и физической (`{field} id : uuid NOT NULL <<PK>>`), поэтому разбираем обе.
    """
    s = line.replace('{field}', '').strip()
    pk = '<<PK>>' in s
    required = s.startswith('*') or 'NOT NULL' in s
    s = re.sub(r'<<[^<>]*>>', '', s).strip().lstrip('*').strip()
    s = re.sub(r'\s+NOT NULL\b', '', s).strip()
    m = RE_COL.match(s)
    name = (m.group('name') or s).strip()
    ctype = (m.group('type') or '').strip()
    return name, ctype, pk, required


def convert_er(name):
    """Диаграмма базы данных: таблицы с колонками и связи по ключам."""
    c = Conv(name, 'ERDiagram')
    tables, rels = parse_tables(c.src)

    # Столбец типов гасим всегда. У концептуальной ER-модели типов нет вовсе,
    # а физические типы PostgreSQL Visual Paradigm сверяет со своим справочником
    # и всё незнакомое — uuid, timestamptz, boolean — молча заменяет на `integer`.
    # Свободное поле `typeName` на показ не влияет (проверено отрисовкой), поэтому
    # тип пишется прямо в имя колонки: так текст совпадает с исходником, а в модели
    # не остаётся неверных значений.
    _set_diagram_prop(c.d, '_showColumnTypes', 'false')

    for alias, t in tables.items():
        b = c.L.find(t['label'], required=False) or c.L.find(alias, required=False)
        if b is None:
            raise SystemExit('%s: таблицы %r нет в раскладке' % (name, t['label']))
        c._used.add(id(b))
        m, _s = c.node(alias, 'DBTable', 'DBTable', t['label'],
                       c.rect(b, min_w=200, min_h=60), fill=fill_of(b.fill))
        kids = c.p.children(m)
        for i, raw in enumerate(t['cols']):
            if not raw or raw == '--':
                continue
            cname, ctype, pk, required = parse_column(raw)
            if not cname:
                continue
            title = '%s : %s' % (cname, ctype) if ctype else cname
            cm = c.p.model('DBColumn', name=title, hint='MC%d' % c._bump(), parent=kids)
            if pk:
                ET.SubElement(cm.props, _q('BooleanProperty'),
                              {'name': 'primaryKey', 'value': 'true'})
            if required:
                ET.SubElement(cm.props, _q('BooleanProperty'),
                              {'name': 'nullable', 'value': 'false'})

    for a, b, kind, am, bm, label in rels:
        if a not in c.shapes or b not in c.shapes:
            print('  пропущена связь %s -- %s (нет таблицы)' % (a, b), file=sys.stderr)
            continue
        c.edge('DBForeignKey', 'DBForeignKey', a, b, label=label or None, style=None)

    c.notes(anchors=note_anchors(c.src, tables))
    return c.write()


def _set_diagram_prop(d, name, value):
    """Логическое свойство диаграммы (настройки показа)."""
    props = d.el.find(_q('DiagramProperties'))
    if props is None:
        props = ET.Element(_q('DiagramProperties'))
        d.el.insert(0, props)
    ET.SubElement(props, _q('BooleanProperty'), {'name': name, 'value': value})


def svg_color(name_or_hex):
    """Цвет PlantUML (#RRGGBB или имя) в вид #RRGGBB; имена — только встречающиеся у нас."""
    named = {'#LightGreen': '#90EE90', '#MistyRose': '#FFE4E1', '#White': '#FFFFFF',
             '#OldLace': '#FDF5E6', '#LightBlue': '#ADD8E6'}
    v = named.get(name_or_hex, name_or_hex)
    return v if re.match(r'^#[0-9A-Fa-f]{6}$', v or '') else None


CONVERTERS = {
    'SM': convert_state,
    'SEQ': convert_sequence,
    'COL': convert_communication,
    'DB': convert_er,
    'PKG': lambda n: convert_containers(n, 'PackageDiagram'),
    'DEP': lambda n: convert_containers(n, 'DeploymentDiagram'),
}


def convert(name):
    kind = name.split('_', 1)[0]
    fn = CONVERTERS.get(kind)
    if fn is None:
        raise SystemExit('нет разборщика для %s (префикс %s)' % (name, kind))
    return fn(name)


if __name__ == '__main__':
    args = sys.argv[1:]
    if args == ['--all']:
        args = sorted(os.path.splitext(f)[0] for f in os.listdir(PUML_DIR)
                      if f.endswith('.puml') and f.split('_', 1)[0] in CONVERTERS)
    for n in args:
        print(convert(n))
