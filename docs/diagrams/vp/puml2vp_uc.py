# -*- coding: utf-8 -*-
"""Детальные диаграммы прецедентов: PlantUML -> XML Visual Paradigm.

Почему отдельный модуль, а не ещё один разборщик в puml2vp: там собраны
диаграммы SAD из docs/diagrams/sad, здесь — docs/diagrams/usecases, и набор
элементов другой: актор, граница системы, прецедент, include и extend,
обобщение ролей, легенда. Общим остаётся приём раскладки — место каждой
фигуры снимается с SVG, который рисует сам PlantUML, поэтому в Visual
Paradigm выходит та же картинка, что в .puml, а не разложенная заново.

Актор в SVG — не фигура с текстом, а палочный человечек: кружок головы
попадает в marks, туловище — в frames, имя — в свободный текст. Поэтому
габариты актора собираются из головы (центр по горизонтали и верх)
и подписи (низ), а не ищутся по тексту, как остальные фигуры.

Запуск:
    python puml2vp_uc.py UC_7_Detail [ещё имена...]
    python puml2vp_uc.py --all
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svgpos                                                   # noqa: E402
from puml2vp import Conv, HERE, ROOT                            # noqa: E402
from vpgen import _q, FILL_GREY, FILL_NOTE                      # noqa: E402

UC_DIR = os.path.join(ROOT, 'docs', 'diagrams', 'usecases')
UC_OUT = os.path.join(HERE, 'out', 'usecases')
UC_SVG = os.path.join(HERE, 'out', 'svg', 'usecases')

WHITE = 'Cr:255,255,255,255'
DARK = 'Cr:51,51,51,255'

# ======================================================================
#  Разбор .puml
# ======================================================================

RE_ACTOR = re.compile(r'^actor\s+"(?P<label>[^"]+)"\s+as\s+(?P<alias>\w+)'
                      r'(?:\s+<<(?P<st>[^>]+)>>)?\s*$')
RE_UC = re.compile(r'^usecase\s+"(?P<label>[^"]+)"\s+as\s+(?P<alias>\w+)\s*$')
RE_BOUND = re.compile(r'^rectangle\s+"(?P<label>[^"]+)"\s+as\s+(?P<alias>\w+)\s*\{\s*$')
RE_EDGE = re.compile(r'^(?P<a>\w+)\s*(?P<arrow>\.\.>|--\|>|-->)\s*(?P<b>\w+)'
                     r'\s*(?::\s*(?P<label>.+?))?\s*$')

SKIP = re.compile(r'^(@|!|\'|skinparam\b|title\b|}$|.* direction$)')


def parse_uc(src):
    """Акторы, граница системы, прецеденты, связи и легенда из исходника.

    Разбор намеренно строгий: неизвестная строка — это ошибка, а не повод
    молча потерять элемент. Файлы генерируются docs/scripts/build_uc_detail.py,
    так что любой новый оборот в них лучше увидеть сразу.
    """
    actors, ucs, edges, legend = [], [], [], []
    boundary = None
    in_legend = False
    for raw in src.split('\n'):
        line = raw.strip()
        if in_legend:
            if line == 'endlegend':
                in_legend = False
            else:
                legend.append(line)
            continue
        if line.startswith('legend'):
            in_legend = True
            continue
        if not line or SKIP.match(line):
            continue
        m = RE_ACTOR.match(line)
        if m:
            actors.append((m.group('alias'), m.group('label'), m.group('st')))
            continue
        m = RE_UC.match(line)
        if m:
            ucs.append((m.group('alias'), m.group('label')))
            continue
        m = RE_BOUND.match(line)
        if m:
            boundary = (m.group('alias'), m.group('label'))
            continue
        m = RE_EDGE.match(line)
        if m:
            edges.append((m.group('arrow'), m.group('a'), m.group('b'),
                          (m.group('label') or '').strip()))
            continue
        raise ValueError('не разобрана строка: %r' % line)
    return actors, boundary, ucs, edges, '\n'.join(legend).strip('\n')


# ======================================================================
#  Конвертация
# ======================================================================

class ConvUC(Conv):
    """Одна детальная диаграмма прецедентов."""

    def __init__(self, name):
        Conv.__init__(self, name, 'UseCaseDiagram',
                      puml_dir=UC_DIR, out_dir=UC_OUT, svg_dir=UC_SVG)
        self._diagram_props()
        self.actors, self.boundary, self.ucs, self.edges, self.legend = parse_uc(self.src)
        # модели собираются в пакет с именем диаграммы: 34 файла сливаются
        # в один проект Visual Paradigm, и без пакетов дерево моделей
        # превращается в кашу из трёх сотен одноимённых прецедентов
        self.pkg = self.p.model('Package', name=name, hint='PKG')
        self.warn = []
        self._build()

    # ---- служебное ---------------------------------------------------
    def _diagram_props(self):
        """Стереотипы акторов и связей должны быть видны, сетка — нет."""
        dp = ET.Element(_q('DiagramProperties'))
        for k, v in (('autoFitShapesSize', 'false'), ('alignToGrid', 'false'),
                     ('gridVisible', 'false'), ('showStereotypes', 'true')):
            ET.SubElement(dp, _q('BooleanProperty'), {'name': k, 'value': v})
        self.d.el.insert(0, dp)

    def _model(self, model_type, name=None, hint=None):
        return self.p.model(model_type, name=name, hint=hint,
                            parent=self.p.children(self.pkg))

    @staticmethod
    def _text(label):
        return label.replace('\\n', '\n').strip()

    @staticmethod
    def _keep_caption(sh):
        """Не пересчитывать подпись: у актора имя ставится под человечком.

        По умолчанию Visual Paradigm подпись сбрасывает и рисует её поверх
        фигуры — у актора это приходится ровно на плечи и руки.
        """
        for el in list(sh.dep):
            sh.dep.remove(el)
        for k in ('requestResetCaption', 'requestResetCaptionSize', 'requestFitSize'):
            ET.SubElement(sh.dep, _q('BooleanProperty'), {'name': k, 'value': 'false'})

    def _deco(self, el, at, dashed=False, bold=False):
        """Шрифт и линия. <Stroke/> обязателен: без него теряются подписи."""
        font = ET.Element(_q('ElementFont'), {'name': 'Arial', 'size': '11',
                                              'style': '1' if bold else '0',
                                              'color': DARK})
        line = ET.Element(_q('Line'), {'color': DARK, 'weight': '1.0',
                                       'transparency': '0', 'cap': '0'})
        stroke = ET.SubElement(line, _q('Stroke'))
        if dashed:
            dashes = ET.SubElement(stroke, _q('Dashes'))
            for v in ('6.0', '4.0'):
                ET.SubElement(dashes, _q('Dash'), {'value': v})
        el.insert(at, font)
        el.insert(at + 1, line)

    # ---- геометрия ---------------------------------------------------
    def _rects(self):
        return [f for f in self.L.frames if f.kind == 'rect']

    def _boundary_box(self, uc_boxes):
        """Рамка границы системы: наименьшая, накрывающая все прецеденты."""
        inside = [f for f in self._rects()
                  if all(f.contains(b.x + 2, b.y + 2)
                         and f.contains(b.x + b.w - 2, b.y + b.h - 2) for b in uc_boxes)]
        if inside:
            return min(inside, key=lambda f: f.area)
        self.warn.append('рамка границы системы не найдена, габариты по прецедентам')
        x0 = min(b.x for b in uc_boxes) - 20
        y0 = min(b.y for b in uc_boxes) - 36
        x1 = max(b.x + b.w for b in uc_boxes) + 20
        y1 = max(b.y + b.h for b in uc_boxes) + 20
        return svgpos.Box(x0, y0, x1 - x0, y1 - y0, 'rect', '')

    def _actor_box(self, label, name_box):
        """Человечек: верх — по кружку головы, низ — по имени под ним."""
        cx = name_box.x + name_box.w / 2.0
        heads = [m for m in self.L.marks
                 if m.kind == 'ellipse' and m.y + m.h < name_box.y
                 and abs((m.x + m.w / 2.0) - cx) < 60]
        if heads:
            head = min(heads, key=lambda m: name_box.y - m.y)
            cx = head.x + head.w / 2.0
            top = head.y
        else:
            self.warn.append('голова актора %r не найдена' % label[:24])
            top = name_box.y - 59
        return svgpos.Box(cx - 10, top, 20, max(name_box.y - 4 - top, 30), 'actor', '')

    def _legend_box(self, boundary):
        """Рамка легенды: прямоугольник с её первой строкой, но не граница."""
        lines = [x for x in self.legend.split('\n') if x.strip()]
        anchors = [b for b in (self.L.find_label(x) for x in (lines[0], lines[-1]))
                   if b is not None]
        rects = [f for f in self._rects() if f is not boundary]
        hit = [f for f in rects
               if anchors and all(f.contains(b.x + 2, b.y + 12) for b in anchors)]
        if hit:
            return min(hit, key=lambda f: f.area)
        if rects:
            self.warn.append('легенда опознана по размеру рамки, а не по тексту')
            return max(rects, key=lambda f: f.area)
        self.warn.append('рамка легенды не найдена, габариты по тексту')
        if not anchors:
            return None
        x0 = min(b.x for b in anchors) - 8
        y0 = min(b.y for b in anchors) - 8
        x1 = max(b.x + b.w for b in anchors) + 8
        y1 = max(b.y + b.h for b in anchors) + 8
        return svgpos.Box(x0, y0, x1 - x0, y1 - y0, 'rect', '')

    # ---- сборка ------------------------------------------------------
    def _build(self):
        boxes = {}
        for alias, label in self.ucs:
            boxes[alias] = self.L.find(self._text(label))
            self._used.add(id(boxes[alias]))

        # граница системы
        bframe = self._boundary_box(list(boxes.values()))
        bm = self._model('System', name=self._text(self.boundary[1]), hint='M_sys')
        x, y, w, h = self.rect(bframe)
        bs = self.d.shape('System', bm, x, y, w, h, name=self._text(self.boundary[1]),
                          fill=WHITE, hint='S_sys')
        self._deco(bs.el, 1)
        self.shapes[self.boundary[0]] = (bm, bs)
        self._fills.append(bs)

        # прецеденты — внутрь границы
        for alias, label in self.ucs:
            text = self._text(label)
            m = self._model('UseCase', name=text, hint='M_' + alias)
            x, y, w, h = self.rect(boxes[alias])
            s = self.d.shape('UseCase', m, x, y, w, h, name=text,
                             fill=FILL_GREY, hint='S_' + alias)
            self._deco(s.el, 1)
            self.nest(s, bs)
            self.shapes[alias] = (m, s)
            self._fills.append(s)

        # акторы
        for alias, label, stereo in self.actors:
            text = self._text(label)
            nb = self.L.find_label(label)
            if nb is None:
                raise KeyError('в SVG нет имени актора %r' % text)
            ab = self._actor_box(text, nb)
            m = self._model('Actor', name=text, hint='M_' + alias)
            if stereo == 'abstract':
                # обобщённая роль: в PlantUML это <<abstract>>, в Visual Paradigm —
                # свойство модели, оно же наклонное начертание имени
                ET.SubElement(m.props, _q('BooleanProperty'),
                              {'name': 'abstract', 'value': 'true'})
            if stereo:
                # базовый тип задаётся при первом создании стереотипа,
                # а _stereo_ref создаёт его с базовым типом Class
                self.p.stereotype(stereo, 'Actor')
                self.p._stereo_ref(m, [stereo])
            x, y, w, h = self.rect(ab)
            w, h = 30, 60
            x = x + (self.rect(ab)[2] - w) // 2
            s = self.d.shape('Actor', m, x, y, w, h, name=text, caption=False,
                             hint='S_' + alias)
            self._keep_caption(s)
            self._deco(s.el, 1)
            cx, cy, cw, ch = self.rect(nb, min_w=120)
            lines = len(text.split('\n'))
            s.el.insert(3, ET.Element(_q('Caption'), {
                'visible': 'true', 'side': 'None',
                'x': str(x + w // 2 - cw // 2), 'y': str(y + h),
                'width': str(cw), 'height': str(max(ch, 20 * lines))}))
            self.shapes[alias] = (m, s)

        self._links()

        # легенда
        if self.legend:
            lb = self._legend_box(bframe)
            if lb is not None:
                m = self.p.note(self.legend, hint='M_legend')
                self.p.children(self.pkg).append(m.el)
                self.p.models.remove(m.el)
                x, y, w, h = self.rect(lb, min_w=320, min_h=90)
                s = self.d.shape('NOTE', m, x, y, w, h, caption=False,
                                 fill=FILL_NOTE, hint='S_legend')
                self._deco(s.el, 1)
                self._fills.append(s)

    def _links(self):
        """Связи: include, extend, обобщение ролей и «актор — прецедент».

        Направление в Visual Paradigm задаёт не коннектор, а пара from/to
        у модели: наконечник рисуется на конце to у include и extend
        и на конце from у обобщения (полый треугольник смотрит на родителя).
        """
        for arrow, a, b, label in self.edges:
            if a not in self.shapes or b not in self.shapes:
                self.warn.append('связь %s %s %s: нет такой фигуры' % (a, arrow, b))
                continue
            if arrow == '..>':
                kind = 'Include' if 'include' in label else 'Extend'
                st = kind.lower()
                m = self._model(kind, name='', hint='M_%s_%s' % (a, b))
                self.p.ref_prop(m, 'from', self.shapes[a][0].id)
                self.p.ref_prop(m, 'to', self.shapes[b][0].id)
                self.p.stereotype(st, kind)
                self.p._stereo_ref(m, [st])
                el = self.d.connector(kind, m, self.shapes[a][1], self.shapes[b][1],
                                      style='Oblique', hint='C_%s_%s' % (a, b))
                dep = ET.Element(_q('DiagramElementProperties'))
                ET.SubElement(dep, _q('BooleanProperty'),
                              {'name': 'requestResetCaption', 'value': 'true'})
                el.insert(0, dep)
                self._deco(el, 1, dashed=True)
                ET.SubElement(el, _q('Caption'), {
                    'visible': 'true', 'side': 'None',
                    'x': '0', 'y': '0', 'width': '90', 'height': '18'})
            elif arrow == '--|>':
                # PlantUML: A --|> B, где A — наследник, B — родитель
                m = self._model('Generalization', hint='M_g_%s_%s' % (a, b))
                self.p.ref_prop(m, 'from', self.shapes[b][0].id)
                self.p.ref_prop(m, 'to', self.shapes[a][0].id)
                el = self.d.connector('Generalization', m,
                                      self.shapes[b][1], self.shapes[a][1],
                                      style='Oblique', hint='C_g_%s_%s' % (a, b))
                self._deco(el, 0)
            else:
                m = self.p.assoc(self.shapes[a][0], self.shapes[b][0],
                                 hint='M_a_%s_%s' % (a, b))
                self.p.children(self.pkg).append(m.el)
                self.p.models.remove(m.el)
                ET.SubElement(m.props, _q('StringProperty'),
                              {'name': 'direction', 'value': 'From-To'})
                el = self.d.connector('Association', m,
                                      self.shapes[a][1], self.shapes[b][1],
                                      style='Oblique', hint='C_a_%s_%s' % (a, b))
                self._deco(el, 0)


def convert(name):
    c = ConvUC(name)
    path = c.write()
    return path, c.warn


def all_names():
    names = [f[:-5] for f in os.listdir(UC_DIR) if f.endswith('_Detail.puml')]
    return sorted(names, key=lambda n: int(re.search(r'\d+', n).group()))


if __name__ == '__main__':
    args = sys.argv[1:]
    names = all_names() if (not args or args[0] == '--all') else args
    bad = 0
    for n in names:
        try:
            path, warn = convert(n)
        except Exception as e:                                   # noqa: BLE001
            bad += 1
            print('%-16s ОШИБКА %s: %s' % (n, type(e).__name__, e))
            continue
        print('%-16s -> %s%s' % (n, os.path.basename(path),
                                 ''.join('\n    ! ' + w for w in warn)))
    if bad:
        print('не собрано: %d из %d' % (bad, len(names)))
        sys.exit(1)
