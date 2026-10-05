# -*- coding: utf-8 -*-
"""Сборка проекта Visual Paradigm (project.xml) для импорта утилитой ImportXML.

Формат и ограничения описаны в docs/VisualParadigm.md. Библиотека закрывает те места,
где ошибиться легче всего:

  * идентификаторы ровно 16 символов и их уникальность;
  * обязательный <Caption> — без него фигура рисуется пустой;
  * порядок дочерних элементов, заданный схемой;
  * разделение модели и представления: в <Model> связи ссылаются на модели,
    в <Connector> — на фигуры.

Многострочный текст передаётся обычным "\n": ElementTree сам закодирует его в &#10;.
"""
import re
import xml.etree.ElementTree as ET

NS = 'http://www.visual-paradigm.com/product/vpuml/modelexporter'
ET.register_namespace('', NS)

# Палитра, повторяющая цвета исходных .puml
FILL_GREY = 'Cr:245,245,245,255'      # #F5F5F5 — обычный узел
FILL_PINK = 'Cr:255,228,225,255'      # #MistyRose — альт. поток «источник недоступен»
FILL_SAND = 'Cr:253,245,230,255'      # #OldLace — альт. поток «устаревшие данные»
FILL_LILAC = 'Cr:237,231,246,255'     # #EDE7F6 — внешняя система
FILL_CREAM = 'Cr:255,242,204,255'     # #FFF2CC — проектируемый элемент
FILL_MINT = 'Cr:232,245,233,255'      # #E8F5E9
FILL_NOTE = 'Cr:254,255,221,255'      # заметка, как в PlantUML
FILL_WHITE = 'Cr:253,253,253,255'     # #FDFDFD — фон пакета


def _q(tag):
    return '{%s}%s' % (NS, tag)


class Ids:
    """Идентификаторы ровно по 16 символов [A-Za-z0-9_.], уникальные в проекте.

    Только ASCII: проверку id Visual Paradigm делает java-регекспом, где класс \\w
    кириллицу не пропускает, и VP молча перевыпускает такой id. Ссылки на него
    (verticalPartitionId, compartmentIds и прочие) перестают совпадать, и часть
    фигур пропадает с картинки.
    """

    def __init__(self):
        self._used = set()
        self._n = 0

    def __call__(self, hint):
        base = re.sub(r'[^A-Za-z0-9_.]', '_', hint)[:16]
        cand = (base + '0' * 16)[:16]
        while cand in self._used:
            self._n += 1
            suf = 'x%d' % self._n
            cand = (base[:16 - len(suf)] + suf)
            cand = (cand + '0' * 16)[:16]
        assert re.fullmatch(r'[A-Za-z0-9_.]{16}', cand), cand
        self._used.add(cand)
        return cand


class M:
    """Элемент модели."""

    def __init__(self, el, mid, props):
        self.el, self.id, self.props = el, mid, props
        self.kids = None


class S:
    """Фигура на холсте."""

    def __init__(self, el, sid, dep, fill):
        self.el, self.id, self.dep = el, sid, dep
        self.fill = fill
        self.children = None


class Project:
    def __init__(self, name):
        self.ids = Ids()
        self.root = ET.Element(_q('Project'), {
            'name': name, 'umlVersion': '2.x', 'exporterVersion': '18.1'})
        self.models = ET.SubElement(self.root, _q('Models'))
        self.diagrams = ET.SubElement(self.root, _q('Diagrams'))

    # ---- модель -----------------------------------------------------
    def model(self, model_type, name=None, hint=None, props=None, parent=None):
        mid = self.ids(hint or model_type)
        attrs = {'id': mid, 'modelType': model_type}
        if name is not None:
            attrs['name'] = name
        host = parent if parent is not None else self.models
        el = ET.SubElement(host, _q('Model'), attrs)
        mp = ET.SubElement(el, _q('ModelProperties'))
        if name is not None:
            ET.SubElement(mp, _q('StringProperty'), {'name': 'name', 'value': name})
        for k, v in (props or {}).items():
            ET.SubElement(mp, _q('StringProperty'), {'name': k, 'value': v})
        return M(el, mid, mp)

    def ref_prop(self, m, prop_name, target_id):
        rp = ET.SubElement(m.props, _q('ModelRefProperty'), {'name': prop_name})
        ET.SubElement(rp, _q('ModelRef'), {'id': target_id})

    def note(self, text, hint='note'):
        """Заметка: текст живёт только в documentation."""
        m = self.model('NOTE', hint=hint)
        ET.SubElement(m.props, _q('HTMLProperty'),
                      {'name': 'documentation', 'plainTextValue': text})
        return m

    def flow(self, model_type, src, dst, name=None, guard=None, hint='flow'):
        """Модель связи: from/to ссылаются на МОДЕЛИ."""
        m = self.model(model_type, name=name, hint=hint)
        if guard:
            ET.SubElement(m.props, _q('StringProperty'), {'name': 'guard', 'value': guard})
        self.ref_prop(m, 'from', src.id)
        self.ref_prop(m, 'to', dst.id)
        return m

    # ---- диаграмма классов -------------------------------------------
    def stereotype(self, name, base='Class'):
        """Стереотип, по одной модели на имя (повторные вызовы возвращают ту же)."""
        if not hasattr(self, '_stereo'):
            self._stereo = {}
        if name not in self._stereo:
            self._stereo[name] = self.model('Stereotype', name=name, hint='ST' + name,
                                            props={'baseType': base})
        return self._stereo[name]

    def children(self, m):
        """Контейнер <ChildModels> модели, создаётся по требованию."""
        if m.kids is None:
            m.kids = ET.SubElement(m.el, _q('ChildModels'))
        return m.kids

    def _text_type(self, m, prop_name, value):
        tp = ET.SubElement(m.props, _q('TextModelProperty'), {'name': prop_name})
        ET.SubElement(tp, _q('StringValue'), {'value': value})

    def _stereo_ref(self, m, names):
        if not names:
            return
        rp = ET.SubElement(m.props, _q('ModelRefsProperty'), {'name': 'stereotypes'})
        for n in names:
            ET.SubElement(rp, _q('ModelRef'), {'id': self.stereotype(n).id})

    def cls(self, name, stereotype=None, hint=None, abstract=False, visibility='public'):
        """Класс. Интерфейс и enum — тот же Class со стереотипом (см. VisualParadigm.md)."""
        m = self.model('Class', name=name, hint=hint or ('CL' + name))
        if visibility:
            ET.SubElement(m.props, _q('StringProperty'),
                          {'name': 'visibility', 'value': visibility})
        if abstract:
            ET.SubElement(m.props, _q('BooleanProperty'), {'name': 'abstract', 'value': 'true'})
        if stereotype:
            self._stereo_ref(m, [stereotype] if isinstance(stereotype, str) else stereotype)
        return m

    def attr(self, owner, name, type=None, visibility='public', static=False,
             multiplicity=None, hint=None):
        """Поле класса. visibility='Unspecified' — без значка видимости."""
        m = self.model('Attribute', name=name, hint=hint or 'AT',
                       parent=self.children(owner))
        if visibility:
            ET.SubElement(m.props, _q('StringProperty'),
                          {'name': 'visibility', 'value': visibility})
        if static:
            ET.SubElement(m.props, _q('StringProperty'),
                          {'name': 'scope', 'value': 'classifier'})
        if multiplicity:
            ET.SubElement(m.props, _q('StringProperty'),
                          {'name': 'multiplicity', 'value': multiplicity})
        if type:
            self._text_type(m, 'type', type)
        return m

    def oper(self, owner, name, params=(), ret=None, visibility='public', static=False,
             abstract=False, hint=None):
        """Операция. params — последовательность (имя, тип) либо (имя, None)."""
        m = self.model('Operation', name=name, hint=hint or 'OP',
                       parent=self.children(owner))
        if visibility:
            ET.SubElement(m.props, _q('StringProperty'),
                          {'name': 'visibility', 'value': visibility})
        if static:
            ET.SubElement(m.props, _q('StringProperty'),
                          {'name': 'scope', 'value': 'classifier'})
        if abstract:
            ET.SubElement(m.props, _q('BooleanProperty'), {'name': 'abstract', 'value': 'true'})
        if ret:
            self._text_type(m, 'returnType', ret)
        for pname, ptype in params:
            pm = self.model('Parameter', name=pname, hint='PA', parent=self.children(m))
            if ptype:
                self._text_type(pm, 'type', ptype)
        return m

    def lit(self, owner, name, hint=None):
        """Литерал перечисления."""
        return self.model('EnumerationLiteral', name=name, hint=hint or 'EL',
                          parent=self.children(owner))

    def assoc(self, src, dst, name=None, a_mult=None, b_mult=None, a_role=None, b_role=None,
              a_agg='None', b_agg='None', a_nav=None, b_nav=None,
              hint='assoc'):
        """Ассоциация. Композиция и агрегация — это она же с aggregationKind у конца.

        Стрелку направленной ассоциации («-->» в PlantUML) даёт не коннектор,
        а свойство navigable у конца, и оно логическое: 'true' / 'false'
        (любая другая строка читается как 'true'). Стрелка рисуется, только
        когда навигируем ровно ОДИН конец: у связи с двумя навигируемыми
        концами Visual Paradigm рисует голую линию. None — свойство
        не выводится вовсе, поведение как раньше.
        """
        m = self.model('Association', name=name or '', hint=hint)
        self.ref_prop(m, 'endRelationshipFromMetaModelElement', src.id)
        self.ref_prop(m, 'endRelationshipToMetaModelElement', dst.id)
        for tag, end, role, mult, agg, nav in (
                ('FromEnd', src, a_role, a_mult, a_agg, a_nav),
                ('ToEnd', dst, b_role, b_mult, b_agg, b_nav)):
            host = ET.SubElement(m.el, _q(tag))
            em = ET.SubElement(host, _q('Model'), {
                'composite': 'true', 'modelType': 'AssociationEnd',
                'id': self.ids(hint + tag[:4]), 'name': role or ''})
            ep = ET.SubElement(em, _q('ModelProperties'))
            ET.SubElement(ep, _q('StringProperty'), {'name': 'name', 'value': role or ''})
            rp = ET.SubElement(ep, _q('ModelRefProperty'), {'name': 'EndModelElement'})
            ET.SubElement(rp, _q('ModelRef'), {'id': end.id})
            if mult:
                ET.SubElement(ep, _q('StringProperty'), {'name': 'multiplicity', 'value': mult})
            ET.SubElement(ep, _q('StringProperty'),
                          {'name': 'aggregationKind', 'value': agg})
            if nav is not None:
                ET.SubElement(ep, _q('StringProperty'),
                              {'name': 'navigable', 'value': nav})
        return m

    # ---- диаграмма --------------------------------------------------
    def diagram(self, name, diagram_type):
        el = ET.SubElement(self.diagrams, _q('Diagram'), {
            'id': self.ids('D_' + name), 'name': name, 'diagramType': diagram_type})
        return Diagram(self, el)

    def write(self, path):
        ET.ElementTree(self.root).write(path, encoding='utf-8', xml_declaration=True)
        return path


class Diagram:
    def __init__(self, project, el):
        self.p = project
        self.el = el
        self.shapes = ET.SubElement(el, _q('Shapes'))
        self.connectors = ET.SubElement(el, _q('Connectors'))
        self._z = 0

    def _next_z(self):
        self._z += 1
        return self._z

    def shape(self, shape_type, model, x, y, w, h, name=None, fill=None,
              caption=True, parent=None, hint=None, zorder=None):
        """Фигура на холсте. Координаты абсолютные, в том числе у вложенных."""
        sid = self.p.ids(hint or ('S_' + shape_type))
        attrs = {'id': sid, 'shapeType': shape_type,
                 'x': str(x), 'y': str(y), 'width': str(w), 'height': str(h),
                 'zorder': str(zorder if zorder is not None else self._next_z())}
        if model is not None:
            attrs['model'] = model.id
        if name is not None:
            attrs['name'] = name
        host = parent.children if isinstance(parent, S) else (parent if parent is not None
                                                              else self.shapes)
        el = ET.SubElement(host, _q('Shape'), attrs)
        # порядок детей задан схемой: DiagramElementProperties → Caption → ChildShapes → FillColor
        dep = ET.SubElement(el, _q('DiagramElementProperties'))
        ET.SubElement(dep, _q('BooleanProperty'),
                      {'name': 'requestResetCaption', 'value': 'true'})
        ET.SubElement(dep, _q('BooleanProperty'),
                      {'name': 'requestResetCaptionSize', 'value': 'true'})
        if caption and name is not None:
            ET.SubElement(el, _q('Caption'), {
                'visible': 'true', 'side': 'Center',
                'x': '0', 'y': '0', 'width': str(w), 'height': str(h)})
        return S(el, sid, dep, fill)

    def child_shapes(self, s):
        if s.children is None:
            s.children = ET.SubElement(s.el, _q('ChildShapes'))
        return s.children

    def finish_fill(self, s):
        """FillColor обязан идти последним ребёнком фигуры."""
        if s.fill:
            ET.SubElement(s.el, _q('FillColor'), {
                'type': '1', 'color': s.fill, 'transparency': '0', 'style': '0'})
            s.fill = None

    def connector(self, shape_type, model, src, dst,
                  caption_xy=None, caption_wh=(200, 34), points=None,
                  style='Rectlinear', hint=None):
        """Связь. from/to ссылаются на ФИГУРЫ, model — на модель связи."""
        attrs = {'id': self.p.ids(hint or ('C_' + shape_type)),
                 'shapeType': shape_type, 'model': model.id,
                 'from': src.id, 'to': dst.id}
        if style:
            attrs['connectorStyle'] = style
        el = ET.SubElement(self.connectors, _q('Connector'), attrs)
        if caption_xy:
            ET.SubElement(el, _q('Caption'), {
                'visible': 'true', 'side': 'None',
                'x': str(caption_xy[0]), 'y': str(caption_xy[1]),
                'width': str(caption_wh[0]), 'height': str(caption_wh[1])})
        if points:
            pts = ET.SubElement(el, _q('Points'))
            for px, py in points:
                ET.SubElement(pts, _q('Point'), {'x': str(px), 'y': str(py)})
        return el


class Swimlanes:
    """Вертикальные дорожки диаграммы активности.

    Контейнер ActivitySwimlane2 с парой «заголовок + отсек» на каждую дорожку.
    В verticalPartitionIds лежат id ФИГУР-заголовков, а не моделей партиций.
    Узлы внутрь отсеков НЕ кладутся — принадлежность дорожке определяют координаты.
    """

    HEADER_H = 46

    def __init__(self, diag, lanes, x=40, y=40, body_h=900, header_h=None):
        self.d = diag
        self.x, self.y = x, y
        self.header_h = header_h or self.HEADER_H
        self.body_h = body_h
        self.lane_x = []
        self.headers = []
        self.compartments = []
        # допускается третий элемент кортежа — цвет заливки дорожки
        lanes = [(l[0], l[1], l[2] if len(l) > 2 else None) for l in lanes]

        swm = diag.p.model('ActivitySwimlane2', name='Swimlane', hint='M_swimlane')
        parts = ET.SubElement(swm.props, _q('ModelsProperty'), {'name': 'verticalPartitions'})
        part_models = [diag.p.model('ActivityPartition', name=t,
                                    hint='M_part_%02d' % i, parent=parts)
                       for i, (t, _w, _f) in enumerate(lanes)]

        total_w = sum(w for _t, w, _f in lanes)
        self.container = diag.shape('ActivitySwimlane2', swm, x, y,
                                    total_w, self.header_h + body_h,
                                    caption=False, hint='S_swimlane')
        diag.child_shapes(self.container)

        hdr_ids, cmp_ids = [], []
        cx = x
        for i, ((title, w, lane_fill), pm) in enumerate(zip(lanes, part_models)):
            tag = '%02d' % i          # только ASCII: кириллица в id ломает импорт
            hdr = diag.shape('ActivityPartitionHeader', pm, cx, y, w, self.header_h,
                             name=title, fill=lane_fill, parent=self.container,
                             hint='S_hdr_' + tag)
            ET.SubElement(hdr.dep, _q('BooleanProperty'),
                          {'name': 'horizontal', 'value': 'false'})
            cmp_ = diag.shape('ActivitySwimlane2Compartment', None,
                              cx, y + self.header_h, w, body_h,
                              caption=False, fill=lane_fill, parent=self.container,
                              hint='S_cmp_' + tag)
            ET.SubElement(cmp_.dep, _q('StringProperty'),
                          {'name': 'verticalPartitionId', 'value': hdr.id})
            hdr_ids.append(hdr.id)
            cmp_ids.append(cmp_.id)
            self.headers.append(hdr)
            self.compartments.append(cmp_)
            self.lane_x.append((cx, w))
            cx += w

        for prop, vals in (('verticalPartitionIds', hdr_ids), ('compartmentIds', cmp_ids)):
            sap = ET.SubElement(self.container.dep, _q('StringArrayProperty'), {'name': prop})
            vs = ET.SubElement(sap, _q('Values'))
            for v in vals:
                ET.SubElement(vs, _q('Value'), {'value': v})

    def center(self, lane, w):
        """X левого края фигуры шириной w, отцентрованной в дорожке lane."""
        lx, lw = self.lane_x[lane]
        return lx + (lw - w) // 2

    @property
    def top(self):
        return self.y + self.header_h
