# -*- coding: utf-8 -*-
"""Извлечение раскладки из SVG, который отрисовал PlantUML.

Идея: в `.puml` координат нет, их считает движок раскладки при отрисовке.
Visual Paradigm требует явные x/y/width/height. Вместо того чтобы изобретать
раскладку заново, мы забираем уже посчитанную — из SVG-вывода PlantUML.

Что даёт модуль: список прямоугольников с текстом внутри и список «свободных»
подписей (метки связей, заголовки дорожек, легенда). Привязка к смыслу — по
тексту: в `.puml` у узла есть текст, в SVG у фигуры есть тот же текст.

Ограничение: маршруты связей отсюда НЕ берутся. Узлы встают туда же, куда их
поставил PlantUML, а линии между ними прокладывает сам Visual Paradigm.
"""
import re
import subprocess
import xml.etree.ElementTree as ET

SVG = '{http://www.w3.org/2000/svg}'


def render_svg(puml_path, out_dir, plantuml_jar, java='java'):
    """Отрисовывает .puml в SVG и возвращает путь к файлу."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run([java, '-Djava.awt.headless=true', '-jar', plantuml_jar,
                    '-tsvg', '-o', os.path.abspath(out_dir), puml_path],
                   check=True, capture_output=True)
    name = os.path.splitext(os.path.basename(puml_path))[0] + '.svg'
    return os.path.join(out_dir, name)


def _num(v, default=0.0):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


class Box:
    """Фигура на холсте PlantUML: габариты плюс текст внутри."""

    __slots__ = ('x', 'y', 'w', 'h', 'kind', 'fill', 'runs')

    def __init__(self, x, y, w, h, kind, fill):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.kind, self.fill = kind, fill
        self.runs = []            # (x, y, текст) — фрагменты как они лежат в SVG

    @property
    def lines(self):
        """Фрагменты, собранные в строки по общей базовой линии.

        Одна строка подписи распадается на несколько `<text>`, как только
        в ней меняется начертание: `**Жирно** обычный хвост` — это два
        фрагмента на одной высоте, а не две строки.
        """
        rows = {}
        for x, y, t in self.runs:
            rows.setdefault(round(y / 3.0), []).append((x, t))
        return [' '.join(t for _x, t in sorted(v)) for _k, v in sorted(rows.items())]

    @property
    def text(self):
        return '\n'.join(self.lines)

    @property
    def area(self):
        return self.w * self.h

    def contains(self, px, py):
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    def __repr__(self):
        return 'Box(%d,%d %dx%d %s %r)' % (self.x, self.y, self.w, self.h,
                                           self.kind, self.text[:30])


_CMD = re.compile(r'([MmLlHhVvCcSsQqTtAaZz])|(-?\d*\.?\d+(?:[eE][-+]?\d+)?)')

# сколько чисел забирает команда и какие из них — координаты конечной точки
_ARITY = {'M': (2, (0, 1)), 'L': (2, (0, 1)), 'H': (1, (0, None)), 'V': (1, (None, 0)),
          'C': (6, (4, 5)), 'S': (4, (2, 3)), 'Q': (4, (2, 3)), 'T': (2, (0, 1)),
          'A': (7, (5, 6)), 'Z': (0, (None, None))}


def _path_points(d):
    """Конечные точки сегментов пути.

    Разбирать обязательно по командам: у дуги `A rx ry rot flag flag x y`
    четыре первых числа — не координаты, и наивный поиск пар чисел
    превращает `A0,0 0 0 0` в точку (0,0), растягивая габариты до начала холста.
    """
    toks = [(m.group(1), m.group(2)) for m in _CMD.finditer(d or '')]
    pts, i, cx, cy, cmd = [], 0, 0.0, 0.0, None
    while i < len(toks):
        c, _n = toks[i]
        if c:
            cmd = c
            i += 1
            if cmd.upper() == 'Z':
                continue
        if cmd is None:
            i += 1
            continue
        up = cmd.upper()
        n, (xi, yi) = _ARITY[up]
        nums = []
        while len(nums) < n and i < len(toks) and toks[i][1] is not None:
            nums.append(float(toks[i][1]))
            i += 1
        if len(nums) < n:
            break
        rel = cmd.islower()
        nx = cx if xi is None else (nums[xi] + (cx if rel else 0))
        ny = cy if yi is None else (nums[yi] + (cy if rel else 0))
        cx, cy = nx, ny
        pts.append((cx, cy))
        if up == 'M':
            cmd = 'l' if rel else 'L'      # после M продолжение читается как L
    return pts


def _shapes(root):
    """Прямоугольники, эллипсы, ромбы и прочие фигуры с их габаритами."""
    out = []
    for el in root.iter():
        tag = el.tag.replace(SVG, '')
        fill = (el.get('fill') or '').strip()
        if tag == 'rect':
            out.append(Box(_num(el.get('x')), _num(el.get('y')),
                           _num(el.get('width')), _num(el.get('height')), 'rect', fill))
        elif tag == 'ellipse':
            cx, cy = _num(el.get('cx')), _num(el.get('cy'))
            rx, ry = _num(el.get('rx')), _num(el.get('ry'))
            out.append(Box(cx - rx, cy - ry, 2 * rx, 2 * ry, 'ellipse', fill))
        elif tag in ('polygon', 'path'):
            if tag == 'polygon':
                pts = [(float(a), float(b)) for a, b in
                       re.findall(r'(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)',
                                  el.get('points') or '')]
            else:
                pts = _path_points(el.get('d'))
            if len(pts) < 3:
                continue
            xs = [p[0] for p in pts]
            ys = [p[1] for p in pts]
            out.append(Box(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys),
                           tag, fill))
    return out


def _texts(root):
    """Текстовые фрагменты с координатами базовой линии."""
    out = []
    for el in root.iter(SVG + 'text'):
        s = ''.join(el.itertext()).strip()
        if not s:
            continue
        out.append((_num(el.get('x')), _num(el.get('y')), s))
    return out


def canvas(root):
    """Габариты холста: сначала viewBox, иначе width/height (там единицы — `px`)."""
    vb = (root.get('viewBox') or '').split()
    if len(vb) == 4:
        return _num(vb[2], 1.0), _num(vb[3], 1.0)
    strip = lambda v: _num(re.sub(r'[^0-9.]', '', v or ''), 1.0)
    return strip(root.get('width')), strip(root.get('height'))


def diagram_type(root):
    """Тип диаграммы, как его пометил PlantUML: ACTIVITY, CLASS, SEQUENCE, ..."""
    return root.get('data-diagram-type') or ''


def lanes(root):
    """Дорожки диаграммы активности: [(x0, x1, заголовок), ...].

    Границы берутся из вертикальных линий во всю высоту холста, заголовки —
    из текста в шапке над первой границей по вертикали.
    """
    _w, h = canvas(root)
    xs = sorted({_num(el.get('x1')) for el in root.iter(SVG + 'line')
                 if abs(_num(el.get('x1')) - _num(el.get('x2'))) < 0.5
                 and _num(el.get('y2')) - _num(el.get('y1')) > 0.75 * h})
    if len(xs) < 3:
        return []
    header = max((b for b in _shapes(root)
                  if b.kind == 'rect' and abs(b.x - xs[0]) < 2 and b.w > 0.8 * (xs[-1] - xs[0])),
                 key=lambda b: b.w, default=None)
    titles = [[] for _ in range(len(xs) - 1)]
    if header is not None:
        for tx, ty, s in _texts(root):
            if not (header.y <= ty - 4 <= header.y + header.h):
                continue
            for i in range(len(xs) - 1):
                if xs[i] <= tx <= xs[i + 1]:
                    titles[i].append(s)
                    break
    return [(xs[i], xs[i + 1], ' '.join(titles[i]))
            for i in range(len(xs) - 1)]


class Layout(object):
    """Раскладка одной диаграммы, снятая с её SVG."""

    def __init__(self, kind, width, height, nodes, marks, free, lanes, frames=()):
        self.kind = kind            # ACTIVITY, CLASS, SEQUENCE, STATE, ...
        self.width, self.height = width, height
        self.nodes = nodes          # фигуры с текстом
        self.marks = marks          # кружки начала/конца, маркеры без текста
        self.free = free            # (x, y, текст) вне фигур: заголовок, метки связей
        self.lanes = lanes          # [(x0, x1, заголовок)] для диаграмм активности
        self.frames = list(frames)  # незалитые рамки: границы составных состояний и пакетов
        self.by_text = index_by_text(nodes)
        self.by_head = index_by_text(nodes, head_only=True)

    def find(self, text, required=True, within=None):
        """Узел по тексту из .puml. Текст сверяется в нормализованном виде.

        Если точного совпадения нет, ищем по первой строке: у состояния с
        описанием (`Alias : текст`) описание рисуется в том же прямоугольнике,
        и полный текст фигуры шире того, что записано в объявлении.
        """
        key = norm(text)
        if within is not None:
            # одинаковые подписи встречаются в разных слоях («Заявка и рейс» есть
            # и в application, и в domain) — различить их можно только по тому,
            # внутри какого контейнера они лежат
            hit = [b for b in self.nodes
                   if within.contains(b.x + 2, b.y + 2)
                   and (norm(b.text) == key or (b.lines and norm(b.lines[0]) == key))]
            if hit:
                return min(hit, key=lambda b: b.area)
        b = self.by_text.get(key) or self.by_head.get(key)
        if b is None:
            # стереотип рисуется отдельной строкой над именем, поэтому имя
            # бывает не первой строкой прямоугольника
            hits = self.find_all(text)
            b = hits[0] if len(hits) == 1 else None
        if b is None and key:
            # у объекта или состояния под именем бывает описание — оно попадает
            # в тот же прямоугольник, и полный текст оказывается длиннее имени
            pre = [x for x in self.nodes
                   if norm(body(x)).startswith(key) or norm(x.text).startswith(key)]
            if pre:
                b = min(pre, key=lambda x: len(norm(body(x))))
        if b is None and required:
            raise KeyError('в SVG нет узла с текстом %r' % (text,))
        return b

    def starts(self):
        """Кружки без текста сверху вниз: начало потока, затем концы."""
        return sorted((m for m in self.marks if m.kind == 'ellipse'),
                      key=lambda b: (b.y, b.x))

    def find_label(self, text, required=False, within=None):
        """Габариты свободной подписи (метки связи) по её тексту из .puml.

        Кластеризовать текст по близости не нужно и ненадёжно: состав строк
        уже известен из исходника, поэтому ищем подряд идущие фрагменты,
        совпадающие с ними по содержанию.
        """
        want = [norm(x) for x in re.split(r'\\n|\n', text) if norm(x)]
        if not want:
            return None
        # строки соседних подписей чередуются по общей сортировке, поэтому
        # цепочка собирается по вертикальному соседству, а не по порядку в списке
        pool = [t for t in self.free
                if within is None or within.contains(t[0], t[1])]
        for first in (t for t in pool if norm(t[2]) == want[0]):
            chain, prev = [first], first
            for line in want[1:]:
                nxt = [t for t in pool
                       if norm(t[2]) == line and 8 < t[1] - prev[1] < 28
                       and abs(t[0] - prev[0]) < 260]
                if not nxt:
                    break
                prev = min(nxt, key=lambda t: abs(t[0] - prev[0]))
                chain.append(prev)
            if len(chain) != len(want):
                continue
            xs = [c[0] for c in chain]
            ys = [c[1] for c in chain]
            w = max(len(c[2]) for c in chain) * 7.0
            return Box(min(xs), min(ys) - 12, w, (max(ys) - min(ys)) + 16, 'label', '')
        if required:
            raise KeyError('в SVG нет подписи %r' % (text,))
        return None

    def find_all(self, text):
        """Все узлы с таким текстом, сверху вниз.

        На диаграмме последовательности PlantUML повторяет заголовки участников
        внизу, поэтому одного совпадения мало — нужен самый верхний.
        """
        key = norm(text)
        # стереотип PlantUML рисует отдельной строкой НАД именем, поэтому имя
        # может оказаться любой строкой прямоугольника или всем остальным
        # текстом, если само занимает несколько строк
        return sorted((b for b in self.nodes
                       if norm(b.text) == key or norm(body(b)) == key
                       or any(norm(l) == key for l in b.lines)),
                      key=lambda b: (b.y, b.x))

    def labels_all(self, text):
        """Все вхождения свободной подписи, сверху вниз."""
        key = norm(text)
        return sorted((t for t in self.free if norm(t[2]) == key),
                      key=lambda t: (t[1], t[0]))

    def frame_of(self, box):
        """Рамка составного элемента по его заголовку.

        Составное состояние рисуется незалитой рамкой с полосой заголовка наверху:
        текст достаётся полосе, а габариты нужны от рамки вокруг неё.
        """
        for f in self.frames:            # отсортированы по площади: ближайшая снаружи
            if f.contains(box.x + 2, box.y + 2) and f.w >= box.w - 2:
                return f
        return box

    def frame_at(self, x, y):
        """Самый внутренний контейнер, накрывающий точку.

        Имя пакета стоит в ярлычке у его верхней кромки, поэтому из всех
        вложенных друг в друга рамок нужна та, чей верхний край ниже всех.
        """
        hit = [f for f in self.frames if f.contains(x, y)]
        return max(hit, key=lambda f: (f.y, f.x)) if hit else None

    def lane_of(self, box):
        """Номер дорожки, в которую попадает центр фигуры."""
        cx = box.x + box.w / 2
        for i, (x0, x1, _t) in enumerate(self.lanes):
            if x0 <= cx <= x1:
                return i
        return -1


def parse(svg_path):
    """Разбирает SVG и возвращает раскладку.

    Фоны дорожек и шапка не считаются фигурами-хозяевами: они тянутся почти на
    весь холст и иначе проглатывали бы весь стоящий в них текст.
    """
    root = ET.parse(svg_path).getroot()
    w, h = canvas(root)
    lns = lanes(root)
    kind = diagram_type(root)
    # Фоны дорожек и рамки `box` вокруг участников тянутся во всю высоту: оставь
    # их — и они проглотят весь стоящий в них текст, включая подписи сообщений.
    # Вне этих двух случаев рослая фигура обычно составное состояние, узел
    # развёртывания или пакет, и отсекать её нельзя.
    if lns or kind == 'SEQUENCE':
        tall = lambda b: b.h > 0.7 * h
    else:
        tall = lambda b: b.w > 0.95 * w and b.h > 0.95 * h
    boxes = [b for b in _shapes(root) if b.w > 4 and b.h > 4 and not tall(b)]
    # незалитая фигура — это линия: дуга перехода, рамка контейнера, соединитель.
    # Её габариты случайно накрывают чужой текст, поэтому держать в ней текст нельзя.
    hosts = [b for b in boxes if b.fill and b.fill != 'none']
    # контейнеры рисуются незалитым контуром: прямоугольником у составного
    # состояния, «папкой» (path) у пакета и узла развёртывания
    frames = sorted((b for b in _shapes(root)
                     if (not b.fill or b.fill == 'none') and b.kind in ('rect', 'path')
                     and b.w > 40 and b.h > 40), key=lambda b: b.area)
    hosts.sort(key=lambda b: b.area)          # мелкие (вложенные) раньше крупных

    free = []
    for tx, ty, s in _texts(root):
        host = None
        for b in hosts:
            # базовая линия текста лежит у нижней кромки строки — берём чуть выше
            if b.contains(tx, ty - 4):
                host = b
                break
        if host is None:
            free.append((tx, ty, s))
        else:
            host.runs.append((tx, ty, s))

    return Layout(diagram_type(root), w, h,
                  [b for b in hosts if b.runs],
                  [b for b in boxes if b.kind == 'ellipse' and not b.runs],
                  free, lns, frames)


def layout_of(puml_path, out_dir, plantuml_jar, java='java'):
    """Отрисовывает .puml и сразу возвращает его раскладку."""
    return parse(render_svg(puml_path, out_dir, plantuml_jar, java))


def norm(s):
    """Нормализация текста для сопоставления .puml и SVG."""
    s = s.replace('\\n', ' ').replace('\n', ' ')
    s = re.sub(r'<<([^<>]*)>>', r'«\1»', s)         # стереотип — как его рисует PlantUML
    s = re.sub(r'<[^>]+>', '', s)                    # разметка PlantUML
    s = s.replace('**', '')                          # полужирное начертание
    s = s.replace('«', '"').replace('»', '"')
    s = re.sub(r'[\s ]+', ' ', s)
    return s.strip().lower()


def body(box):
    """Текст фигуры без строк-стереотипов."""
    return '\n'.join(l for l in box.lines
                     if not re.fullmatch(r'\s*«[^«»]*»\s*', l))


def index_by_text(nodes, head_only=False):
    """Словарь нормализованный текст -> узел (неоднозначные отбрасываются)."""
    seen = {}
    dup = set()
    for b in nodes:
        k = norm(b.lines[0] if head_only and b.lines else b.text)
        if k in seen:
            dup.add(k)
        seen[k] = b
    for k in dup:
        seen.pop(k, None)
    return seen
