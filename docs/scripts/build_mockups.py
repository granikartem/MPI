# -*- coding: utf-8 -*-
"""Генератор макетов экранов ИС «Караваны» (docs/mockups/uc-NN-slug.html).

Зачем генератор, а не руками свёрстанные файлы:

1. Макеты обязаны соответствовать реализованному интерфейсу. Поэтому
   docs/mockups/assets/karavany.css — дословная копия frontend/src/index.css
   плюс небольшой слой, нужный только макету (подпись под картинкой).
   Никаких собственных классов у макетов нет: используется тот же словарь
   классов, что и в коде (.app, .card, .registry-head, .summary-tile, .chip,
   .modal-overlay, .admin-console, .tier-card и т. д.).
2. Один экран — один прецедент и 1-2 карточки. Раньше каждый макет рисовал
   трёхколоночную «консоль» с навигацией и боковой сводкой, которой в коде нет
   вообще — отсюда и замечание «интерфейсы перегружены».

Две оболочки, обе взяты из кода:
  app   — терминал диспетчера/полевого пользователя: .app > header > main
          со стопкой .card (pages/Console.tsx);
  admin — консоль суперпользователя: .admin-console > .admin-header >
          .admin-grid (pages/Organizations.tsx). Только UC-32..34.

Запуск:  python docs/scripts/build_mockups.py
Рендер:  python <scratchpad>/uc/render.py docs/mockups/uc-*.html
"""
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT_DIR = os.path.join(ROOT, 'docs', 'mockups')
APP_CSS = os.path.join(ROOT, 'frontend', 'src', 'index.css')
NL = chr(10)

# ----------------------------------------------------------------------------
# таблица стилей макетов = дословный index.css приложения + слой макета
# ----------------------------------------------------------------------------

CSS_LAYER = '''
/* ======================================================================
   Слой макета. Всё выше — дословная копия frontend/src/index.css, чтобы
   макеты и реализованный интерфейс нельзя было развести по оформлению.
   Ниже — только то, чего в приложении нет: подпись под макетом и
   имитация состояний, которые в живом интерфейсе даёт сам браузер.
   Файл собирается docs/scripts/build_mockups.py, править руками не нужно.
   ====================================================================== */

/* подпись под макетом; полоса непрозрачна и лежит выше модального
   оверлея (z-index 100), иначе на макетах с модальным окном подпись
   оказывается под затемнением */
.mock-caption-bar {
  position: relative;
  z-index: 200;
  max-width: 1100px;
  margin: 8px auto 0;
  background: var(--bg);
  border-top: 1px solid var(--border);
}
.mock-caption {
  padding: 14px 16px 22px;
  color: var(--dim);
  font-size: 12px;
  line-height: 1.6;
}
.mock-caption b {
  color: var(--fg);
}
/* в приложении консоль тянется на весь экран (min-height: 100vh);
   в макете это выталкивает подпись за нижний край снимка */
.admin-console,
.admin-console .admin-nav,
.admin-console .admin-summary {
  min-height: 0;
}
.admin-console + .mock-caption-bar {
  max-width: none;
  margin: 8px 0 0;
  background: var(--admin-bg, #111);
  border-top-color: #6d4a00;
}
.admin-console + .mock-caption-bar .mock-caption {
  color: #8a5e00;
  padding: 12px;
}

/* модальное окно: в приложении оно накрывает экран (position: fixed)
   и потому вырезано из потока. На статичном макете это мешает: окно встаёт
   посередине экрана и накрывает подпись, а длинное окно ещё и обрезается
   по max-height: 88vh. В макете показываем его в потоке — под содержимым
   экрана и над подписью; затемнение фона остаётся и читается как
   полоса за окном */
.modal-overlay {
  position: static;
  padding: 24px 16px;
}
.modal-overlay .modal {
  max-height: none;
}

/* фокус в поле ввода: в живом интерфейсе его рисует браузер */
.mock-focus {
  border-color: var(--fg);
}

/* ряд кнопок внизу карточки: в приложении кнопки стоят в потоке формы,
   в макете их нужно показать вместе */
.mock-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-top: 4px;
}
'''


def build_css():
    src = io.open(APP_CSS, encoding='utf-8').read().replace(chr(13), '')
    path = os.path.join(OUT_DIR, 'assets', 'karavany.css')
    io.open(path, 'w', encoding='utf-8', newline=NL).write(src + CSS_LAYER)
    return path

# ----------------------------------------------------------------------------
# примитивы разметки
# ----------------------------------------------------------------------------


def e(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def at(t):
    return e(t).replace('"', '&quot;')


def tag(name, inner='', cls=None, extra=''):
    c = ' class="%s"' % at(cls) if cls else ''
    return '<%s%s%s>%s</%s>' % (name, c, extra, inner, name)


def card(title, *parts, **kw):
    cls = kw.get('cls', 'card')
    head = '<h2>%s</h2>' % e(title) if title else ''
    return '<div class="%s">%s%s</div>' % (cls, head, ''.join(parts))


def form(title, *parts):
    return '<form class="card"><h2>%s</h2>%s</form>' % (e(title), ''.join(parts))


def inp(label, value='', ph='', kind='text', disabled=False, focus=False):
    a = ''
    if value != '':
        a += ' value="%s"' % at(value)
    if ph:
        a += ' placeholder="%s"' % at(ph)
    if disabled:
        a += ' disabled'
    if focus:
        a += ' class="mock-focus"'
    return '<label>%s<input type="%s"%s></label>' % (e(label), kind, a)


def sel(label, chosen, *rest):
    opts = '<option selected>%s</option>' % e(chosen)
    opts += ''.join('<option>%s</option>' % e(o) for o in rest)
    return '<label>%s<select>%s</select></label>' % (e(label), opts)


def area(label, value='', ph=''):
    a = ' placeholder="%s"' % at(ph) if ph else ''
    return '<label>%s<textarea%s>%s</textarea></label>' % (e(label), a, e(value))


def check(label, checked=True, cls='check-row'):
    c = ' checked' if checked else ''
    return '<label class="%s"><input type="checkbox"%s> %s</label>' % (cls, c, e(label))


def btn(text, cls=None, extra=''):
    c = ' class="%s"' % at(cls) if cls else ''
    return '<button%s%s>%s</button>' % (c, extra, e(text))


def link(text):
    return btn(text, 'link')


def actions(*parts):
    return '<div class="mock-actions">%s</div>' % ''.join(parts)


def muted(text, small=True, cls=''):
    c = 'muted small' if small else 'muted'
    if cls:
        c += ' ' + cls
    return '<div class="%s">%s</div>' % (c, e(text))


def err(text):
    return '<div class="error">%s</div>' % e(text)


def row2(label, value):
    return '<div class="sum-row"><span>%s</span><b>%s</b></div>' % (e(label), e(value))


def table(headers, rows, cls=None, wrap=False):
    """rows: список списков с готовым HTML ячеек; элемент может быть
    кортежем (css-класс строки, [ячейки])."""
    c = ' class="%s"' % at(cls) if cls else ''
    out = ['<table%s><thead><tr>' % c]
    out += ['<th>%s</th>' % e(h) for h in headers]
    out.append('</tr></thead><tbody>')
    for r in rows:
        rc = ''
        if isinstance(r, tuple):
            rc, r = ' class="%s"' % at(r[0]), r[1]
        out.append('<tr%s>%s</tr>' % (rc, ''.join('<td>%s</td>' % c2 for c2 in r)))
    out.append('</tbody></table>')
    html = ''.join(out)
    return '<div class="registry-table">%s</div>' % html if wrap else html


STATUS = {
    'DRAFT': ('Черновик', '#7aa888'),
    'READY': ('Готов к отправке', '#ffd633'),
    'EN_ROUTE': ('В пути', '#33ccff'),
    'DELAYED': ('Задержка', '#ff9800'),
    'DELIVERED': ('Доставлен', '#33ff66'),
    'CLOSED': ('Закрыт', '#55aa77'),
    'CANCELLED': ('Отменён', '#ff4444'),
}

RISK = {
    'UNKNOWN': ('Н/Д', '#888'),
    'LOW': ('Низкий', '#33ff66'),
    'MEDIUM': ('Средний', '#ffd633'),
    'HIGH': ('Высокий', '#ff9800'),
    'CRITICAL': ('Критический', '#ff4444'),
}


def sbadge(code, prefix=''):
    label, color = STATUS[code]
    return ('<span class="status-badge" style="border-color:%s;color:%s">%s%s</span>'
            % (color, color, e(prefix), e(label)))


def rbadge(score, level, info=True):
    color = RISK[level][1] if level == 'UNKNOWN' else (
        '#ff4444' if score >= 80 else '#ff9800' if score >= 60 else
        '#ffd633' if score >= 30 else '#33ff66')
    text = 'risk %s' % score if score != '' else 'risk —'
    if info:
        text += ' ⓘ'
    return ('<button class="risk-badge" style="border-color:%s;color:%s">%s</button>'
            % (color, color, e(text)))


def tile(head, value=None, marks=None, note=None):
    out = ['<div class="summary-tile"><div class="tile-head">%s</div>' % e(head)]
    if value is not None:
        out.append('<div class="tile-value">%s</div>' % e(value))
    if marks:
        out.append('<div class="tile-marks">%s</div>' % ''.join(
            '<span class="summary-mark"%s>%s</span>'
            % (' style="border-color:%s;color:%s"' % (c, c) if c else '', e(t))
            for t, c in marks))
    if note:
        out.append('<div class="muted small">%s</div>' % e(note))
    out.append('</div>')
    return ''.join(out)


def tiles(*items):
    return '<div class="summary-tiles">%s</div>' % ''.join(items)


def chips(title, items):
    cs = ''.join('<button class="chip%s"%s>%s</button>'
                 % (' active' if a else '',
                    ' style="border-color:%s;color:%s"' % (c, c) if c else '', e(t))
                 for t, c, a in items)
    return ('<div class="filter-group"><div class="filter-title">%s</div>'
            '<div class="chips">%s</div></div>' % (e(title), cs))


def fgroup(title, inner):
    t = '<div class="filter-title">%s</div>' % e(title) if title else ''
    return '<div class="filter-group">%s%s</div>' % (t, inner)


def filterbar(*groups):
    return '<div class="filter-bar">%s</div>' % ''.join(groups)


def scopetabs(a_label, b_label, active=0):
    return ('<div class="scope-tabs"><button class="%s">%s</button>'
            '<button class="%s">%s</button></div>'
            % ('active' if active == 0 else '', e(a_label),
               'active' if active == 1 else '', e(b_label)))


def modetoggle(a_label, b_label, active=0):
    return ('<div class="mode-toggle"><button class="%s">%s</button>'
            '<button class="%s">%s</button></div>'
            % ('active' if active == 0 else '', e(a_label),
               'active' if active == 1 else '', e(b_label)))


def state(*parts):
    return '<div class="registry-state">%s</div>' % ''.join(parts)


def derivation(head, steps, total=None):
    out = ['<div class="derivation">']
    if head:
        out.append('<div class="muted small">%s</div>' % e(head))
    for name, value in steps:
        out.append('<div class="step"><span>%s</span><b>%s</b></div>' % (e(name), e(value)))
    if total:
        out.append('<div class="step total"><span>%s</span><b>%s</b></div>'
                   % (e(total[0]), e(total[1])))
    out.append('</div>')
    return ''.join(out)


def seg_row(a, b, hours):
    return ('<div class="segment-row"><select><option selected>%s</option></select>'
            '<span>&rarr;</span><select><option selected>%s</option></select>'
            '<input type="number" value="%s">%s</div>'
            % (e(a), e(b), e(hours), link('✕')))


def rhead(title, meta_parts):
    return ('<div class="registry-head"><h2>%s</h2><div class="registry-meta">%s</div></div>'
            % (e(title), ''.join(meta_parts)))


# ----------------------------------------------------------------------------
# оболочки страниц
# ----------------------------------------------------------------------------

HEAD = '''<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>{title}</title>
<!-- render: {size} -->
<!-- Шрифт Share Tech Mono (как в frontend/index.html) намеренно не подключается
     ссылкой на Google Fonts: макеты должны открываться и рендериться без сети.
     Семейство в CSS то же самое, при отсутствии шрифта работает запасной
     моноширинный стек. -->
<link rel="stylesheet" href="assets/karavany.css">
</head>
<body>
'''

TAIL = NL + '</body>' + NL + '</html>' + NL

ORG_BANNER = (card(None,
                   link('← все организации'),
                   '<h2>Рейсы · Crimson Caravan Company</h2>',
                   muted('STANDARD · tenant crimson'),
                   cls='card org-banner'))

TRIP_BANNER = (card(None,
                    link('← все рейсы'),
                    '<h2>Рейс R-1043 · Goodsprings &rarr; New Vegas</h2>',
                    muted('Караван-мастер Кэсседи · отправление 2287-10-21 · этап 3 из 5'),
                    cls='card org-banner'))


def app_shell(h1, main_html, header_links, modal=None):
    links = ''.join(link(t) for t in header_links)
    out = ['<div class="app">',
           '<header><div class="header-top"><h1>%s</h1>' % e(h1),
           '<div class="header-actions">%s</div></div>' % links,
           '<div class="health"><span class="dot ok"></span> сервер: ok · PG: ok · Mongo: ok</div>',
           '</header>',
           '<main>%s</main>' % main_html,
           '</div>']
    if modal:
        out.append(modal)
    return NL.join(out)


ADMIN_NAV_ITEMS = ['ORGANIZATIONS', 'SUBSCRIPTIONS', 'AUDIT LOG', 'DISPATCH']


def admin_shell(mode, panels, summary, nav_active='ORGANIZATIONS'):
    nav = ''
    for n in ADMIN_NAV_ITEMS:
        active = (n == nav_active)
        nav += ('<button class="nav-item%s">[%s] %s</button>'
                % (' active' if active else '', '>' if active else ' ', e(n)))
    return NL.join([
        '<div class="admin-console">',
        '<header class="admin-header">',
        '<div><h1>ROBCO PLATFORM // SUPERUSER CONSOLE</h1>'
        '<div class="admin-sub">PLATFORM v4.21.07 · TENANT OPS</div></div>',
        '<div class="admin-mode">%s</div>' % e(mode),
        '<div class="admin-user">ROLE :: PLATFORM OPERATOR<br>API :: ONLINE</div>',
        '</header>',
        '<div class="admin-grid">',
        '<aside class="admin-nav"><div class="nav-title">-- PLATFORM --</div>',
        nav,
        '<div class="nav-foot">TENANTS :: 7<br>ACTIVE USERS :: 41<br>STATUS :: NOMINAL</div></aside>',
        '<main class="admin-main">%s</main>' % ''.join(panels),
        '<aside class="admin-summary">%s</aside>' % summary,
        '</div>',
        '</div>',
    ])


def admin_panel(title, right, *parts):
    return ('<section class="admin-panel"><div class="admin-panel-title">'
            '<span>%s</span><span>%s</span></div>%s</section>'
            % (e(title), e(right), ''.join(parts)))


def admin_form(title, right, *parts):
    return ('<form class="admin-panel"><div class="admin-panel-title">'
            '<span>%s</span><span>%s</span></div>%s</form>'
            % (e(title), e(right), ''.join(parts)))


def admin_block(title, *parts, **kw):
    t = '<h2>%s</h2>' % e(title) if title else ''
    return '<section class="admin-block">%s%s</section>' % (t, ''.join(parts))


def admin_inp(label, value='', ph='', full=False, disabled=False):
    cls = ' class="full"' if full else ''
    a = ' value="%s"' % at(value) if value else ''
    if ph:
        a += ' placeholder="%s"' % at(ph)
    if disabled:
        a += ' disabled'
    return '<label%s>%s<input type="text"%s></label>' % (cls, e(label), a)


def admin_area(label, value='', full=True):
    cls = ' class="full"' if full else ''
    return '<label%s>%s<textarea>%s</textarea></label>' % (cls, e(label), e(value))


def tier_card(code, price, feats, selected=False):
    body = '<b>%s</b><span>%s</span>' % (e(code), e(price))
    body += ''.join('<small>%s</small>' % e(f) for f in feats)
    return '<button class="tier-card%s">%s</button>' % (' selected' if selected else '', body)


TIERS = [
    ('BASIC', '200 caps / мес.', ['до 3 диспетчеров', 'до 50 рейсов / мес', 'Intel: базовый']),
    ('STANDARD', '600 caps / мес.', ['до 10 диспетчеров', 'до 300 рейсов / мес', 'Intel: расширенный']),
    ('PRO', '1 500 caps / мес.', ['без лимита', 'SLA 99.5%', 'Intel: live-feed + API']),
]


def tier_grid(selected):
    return ('<div class="field-title">SUBSCRIPTION TIER · УРОВЕНЬ ПОДПИСКИ</div>'
            '<div class="tier-grid">%s</div>'
            % ''.join(tier_card(c, p, f, c == selected) for c, p, f in TIERS))


def admin_sum(*secs):
    return '<h2>SUMMARY</h2>' + ''.join(secs)


def sum_sec(head, rows):
    return ('<div class="sum-sec"><div class="sum-head">%s</div>%s</div>'
            % (e(head), ''.join(row2(k, v) for k, v in rows)))


def sum_effect(head, lines):
    return ('<div class="sum-effect"><b>%s</b>%s</div>'
            % (e(head), ''.join('<span>%s</span>' % e(l) for l in lines)))


# ----------------------------------------------------------------------------
# общие данные демонстрационного набора
# ----------------------------------------------------------------------------

SEGMENTS = [('Goodsprings', 'Primm', '8'), ('Primm', 'Nipton', '7'),
            ('Nipton', 'Novac', '12'), ('Novac', 'New Vegas', '9')]

THREATS = [('Goodsprings → Primm', 'Рейдеры', '3'),
           ('Primm → Nipton', 'Когти смерти', '4'),
           ('Nipton → Novac', 'Гули', '2'),
           ('Novac → New Vegas', 'Чисто', '0')]

REG_ROWS = [
    ['<span class="route-code">R-1043</span> Южный объезд', 'Goodsprings &rarr; New Vegas',
     '2287-10-21', 'Медикаменты<div class="muted small">5 000 крышек</div>', '1 д 12 ч',
     rbadge(74, 'HIGH') + '<div class="muted small">Высокий</div>', sbadge('EN_ROUTE')],
    ['<span class="route-code">R-1041</span> Прямой тракт', 'Goodsprings &rarr; Novac',
     '2287-10-20', 'Патроны<div class="muted small">12 400 крышек</div>', '9 ч',
     rbadge(86, 'CRITICAL') + '<div class="muted small">Критический</div>', sbadge('DELAYED')],
    ['<span class="route-code">R-1038</span> Северный обход', 'Primm &rarr; New Vegas',
     '2287-10-18', 'Вода<div class="muted small">800 крышек</div>', '14 ч',
     rbadge(28, 'LOW') + '<div class="muted small">Низкий</div>', sbadge('READY')],
    ['<span class="route-code">R-1035</span> Южный объезд', 'Goodsprings &rarr; New Vegas',
     '2287-10-16', 'Оружие<div class="muted small">21 000 крышек</div>', '1 д 11 ч',
     rbadge(62, 'HIGH') + '<div class="muted small">Высокий</div>', sbadge('DELIVERED')],
]

REG_HEADERS = ['Маршрут (id · название)', 'Откуда → Куда', 'Отправка', 'Груз',
               'ETA', 'risk_score', 'Статус']


# ----------------------------------------------------------------------------
# экраны
# ----------------------------------------------------------------------------

SCREENS = []


def screen(n, slug, title, body, caption, size='1180x1200', shell='app',
           h1='CARAVAN // DISPATCH TERMINAL',
           header_links=('консоль организаций', '← на главную'),
           modal=None, banner=ORG_BANNER, admin=None):
    SCREENS.append(dict(n=n, slug=slug, title=title, body=body, caption=caption,
                        size=size, shell=shell, h1=h1, header_links=list(header_links),
                        modal=modal, banner=banner, admin=admin))


FIELD = dict(h1='CARAVAN // FIELD TERMINAL',
             header_links=('← к списку рейсов',),
             banner=TRIP_BANNER)

# --- UC-1 -------------------------------------------------------------------
screen(1, 'create-request', 'Создать заявку на перевозку',
       form('Новая заявка на перевозку',
            inp('Пункт отправления', 'Goodsprings'),
            inp('Пункт назначения', 'New Vegas'),
            inp('Дата отправки', '2287-10-21', kind='date'),
            modetoggle('Шаблон маршрута', 'Ручной маршрут', 0),
            sel('Маршрут', 'RT-07 · Южный объезд через Primm',
                'RT-02 · Прямой тракт', 'RT-11 · Северный обход'),
            area('Описание груза', 'Медикаменты, 4 ящика',
                 'Медикаменты, патроны...'),
            inp('Ценность груза (крышек)', '5000', kind='number'),
            actions(btn('Создать заявку'))),
       'Основная форма прецедента UC-1 — один экран, одна карточка. '
       'Переключатель «Шаблон маршрута / Ручной маршрут» — шаг 3 сценария (UC-1.3, см. UC-5). '
       'ETA и risk_score на форме не показываются: они считаются системой после создания '
       'заявки (UC-6, UC-7) и появляются в реестре.',
       size='1180x1050')

# --- UC-2 -------------------------------------------------------------------
screen(2, 'request-status', 'Управлять статусами заявки',
       card(None,
            rhead('Реестр рейсов',
                  [muted('данные на 2287-10-21 14:20 · показано 3 · в срезе 3'),
                   link('Обновить')]),
            table(['Маршрут', 'Откуда → Куда', 'Статус', 'Изменение статуса', ''],
                  [['<span class="route-code">R-1043</span> Южный объезд',
                    'Goodsprings &rarr; New Vegas', sbadge('EN_ROUTE'),
                    '<div class="small">2287-10-21 09:40</div>'
                    '<div class="muted small">Джед Мастерсон</div>', link('Статус')],
                   ['<span class="route-code">R-1041</span> Прямой тракт',
                    'Goodsprings &rarr; Novac', sbadge('DELAYED'),
                    '<div class="small">2287-10-21 11:05</div>'
                    '<div class="muted small">Кэсседи</div>', link('Статус')],
                   ['<span class="route-code">R-1038</span> Северный обход',
                    'Primm &rarr; New Vegas', sbadge('READY'),
                    '<div class="small">2287-10-20 18:12</div>'
                    '<div class="muted small">Джед Мастерсон</div>', link('Статус')]],
                  wrap=True)),
       'Переход статуса выполняется в модальном окне поверх реестра — так же, как в коде '
       '(components/StatusModal.tsx). Видны только разрешённые статусной моделью переходы, '
       'причина обязательна при фиксации задержки, журнал переходов — внизу окна (FR-3).',
       size='1180x1350',
       modal=('<div class="modal-overlay"><div class="modal">'
              '<div class="modal-head"><h3>Статус рейса</h3>%s</div>'
              '%s%s%s%s%s%s%s'
              '</div></div>'
              % (link('✕'),
                 muted('Goodsprings → New Vegas · Южный объезд через Primm'),
                 '<div class="status-current"><span class="muted">Текущий статус:</span>%s</div>'
                 % sbadge('EN_ROUTE'),
                 '<div class="actor-row">%s%s</div>'
                 % (sel('Роль актора', 'Диспетчер караванов', 'Караван-мастер'),
                    inp('ФИО (для журнала)', 'Джед Мастерсон', 'Например, Кэсседи')),
                 area('Причина перехода', '', 'Обязательна при фиксации задержки'),
                 '<div class="transitions">'
                 '<div class="transition"><div class="transition-head">%s%s</div></div>'
                 '<div class="transition"><div class="transition-head">%s%s</div>%s</div>'
                 '<div class="transition"><div class="transition-head">%s%s</div></div>'
                 '</div>'
                 % (btn('Зафиксировать задержку'), sbadge('DELAYED', '→ '),
                    btn('Отметить доставку'), sbadge('DELIVERED', '→ '),
                    muted('доступно после отметки последнего этапа рейса'),
                    btn('Отменить рейс'), sbadge('CANCELLED', '→ ')),
                 derivation('История изменений статуса (FR-3)', []),
                 table(['Когда', 'Переход', 'Кто', 'Причина'],
                       [['2287-10-21 09:40', 'READY &rarr; EN_ROUTE', 'Джед Мастерсон', '—'],
                        ['2287-10-20 17:02', 'DRAFT &rarr; READY', 'Джед Мастерсон',
                         'манифест и охрана подтверждены']], cls='inner'))))

# --- UC-3 -------------------------------------------------------------------
screen(3, 'registry', 'Просмотреть реестр рейсов',
       card(None,
            rhead('Реестр рейсов',
                  [muted('данные на 2287-10-21 14:20 · показано 4 · в срезе 4'),
                   link('Обновить')]),
            scopetabs('Активные (3)', 'Архив (1)', 0),
            tiles(tile('Срез «Активные»', '3', note='рейсов в срезе'),
                  tile('По статусам', marks=[('В пути 1', '#33ccff'),
                                             ('Задержка 1', '#ff9800'),
                                             ('Готов к отправке 1', '#ffd633')]),
                  tile('По уровню риска', marks=[('Критический 1', '#ff4444'),
                                                 ('Высокий 1', '#ff9800'),
                                                 ('Низкий 1', '#33ff66')]),
                  tile('Требуют внимания', '1',
                       marks=[('Задержка', None)])),
            muted('Сводка считается по срезу и не зависит от применённых фильтров '
                  'и ограничения выборки.', cls='registry-hint'),
            table(REG_HEADERS + ['Внимание'],
                  [REG_ROWS[0] + ['—'],
                   ('row-attention', REG_ROWS[1] +
                    ['<div class="attention-marks">'
                     '<span class="attention-mark">Задержка</span></div>']),
                   REG_ROWS[2] + ['—'],
                   REG_ROWS[3] + ['—']],
                  wrap=True)),
       'Реестр: вкладки среза, сводка по срезу, таблица рейсов. Отбор, сортировка и поиск '
       'вынесены на макет UC-4, чтобы экран читался. Строка с отметкой внимания выделяется '
       'рамкой слева — как в components/RequestList.tsx.',
       size='1400x1150')

# --- UC-4 -------------------------------------------------------------------
screen(4, 'archive-search', 'Поиск и фильтрация завершённых рейсов',
       card(None,
            rhead('Реестр рейсов',
                  [muted('данные на 2287-10-21 14:20 · показано 2 · в срезе 9'),
                   link('Обновить')]),
            scopetabs('Активные (3)', 'Архив (9)', 1),
            filterbar(
                fgroup('Поиск по архиву',
                       '<input type="text" value="Primm" '
                       'placeholder="id рейса, маршрут, пункт, груз" class="mock-focus">'),
                chips('Статус', [('Доставлен', '#33ff66', True),
                                 ('Закрыт', '#55aa77', True),
                                 ('Отменён', '#ff4444', False)]),
                chips('Уровень риска', [('Низкий', '#33ff66', False),
                                        ('Средний', '#ffd633', False),
                                        ('Высокий', '#ff9800', True),
                                        ('Критический', '#ff4444', True)]),
                fgroup(None, check('только требующие внимания', False)),
                '<label class="sort-select">Порядок<select>'
                '<option selected>По дате отправки</option>'
                '<option>Сначала новые</option><option>По risk_score</option>'
                '<option>По последнему изменению статуса</option></select></label>',
                fgroup(None, btn('Сбросить фильтры')) .replace(
                    'class="filter-group"', 'class="filter-group filter-actions"')),
            muted('Найдено 2 рейса из 9 в архивном срезе · запрос «Primm», '
                  'статусы: Доставлен, Закрыт · риск: Высокий, Критический'),
            table(REG_HEADERS,
                  [REG_ROWS[3],
                   ['<span class="route-code">R-1012</span> Южный объезд',
                    'Primm &rarr; New Vegas', '2287-09-30',
                    'Инструменты<div class="muted small">6 300 крышек</div>', '11 ч',
                    rbadge(81, 'CRITICAL') + '<div class="muted small">Критический</div>',
                    sbadge('CLOSED')]],
                  wrap=True)),
       'Поиск и фильтрация — разные шаги прецедента и разные элементы экрана: поле запроса '
       '(UC-4.2) задаёт, что ищем, а чипы статуса/риска и порядок (UC-4.3) сужают уже '
       'отобранный архивный срез. Поле поиска — проектное расширение: в текущей реализации '
       '(components/RegistryFilters.tsx) есть только чипы и сортировка.',
       size='1400x1000')

# --- UC-5 -------------------------------------------------------------------
screen(5, 'route-plan', 'Выбрать/спланировать маршрут',
       form('Маршрут рейса',
            modetoggle('Шаблон маршрута', 'Ручной маршрут', 1),
            '<div class="segments">%s%s%s%s</div>'
            % (inp('Название маршрута', 'Южный объезд через Primm',
                   'Напр. Южный объезд через Primm'),
               muted('Участки маршрута (по порядку)'),
               ''.join(seg_row(a, b, h) for a, b, h in SEGMENTS),
               link('+ участок')),
            muted('Итого 4 участка · расчётное время в пути 36 ч (ETA считается '
                  'системой после сохранения — UC-6)'),
            actions(btn('Сохранить маршрут'), link('Сохранить как шаблон'))),
       'Ручной режим планирования: участки задаются по порядку, каждый — «откуда → куда» '
       'и время в часах. Шаблонный режим (вторая вкладка переключателя) сводится к одному '
       'выпадающему списку, он показан на макете UC-1.',
       size='1180x900')

# --- UC-6 -------------------------------------------------------------------
screen(6, 'eta', 'Рассчитать ETA',
       card('Расчёт ETA · рейс R-1043',
            muted('Goodsprings → New Vegas · Южный объезд через Primm'),
            table(['Участок', 'Расстояние', 'Скорость каравана', 'Время'],
                  [['Goodsprings &rarr; Primm', '32 км', '4 км/ч', '8 ч'],
                   ['Primm &rarr; Nipton', '28 км', '4 км/ч', '7 ч'],
                   ['Nipton &rarr; Novac', '48 км', '4 км/ч', '12 ч'],
                   ['Novac &rarr; New Vegas', '36 км', '4 км/ч', '9 ч']], cls='inner'),
            derivation(None,
                       [('Сумма по участкам', '36 ч'),
                        ('Отправление', '2287-10-21 06:00')],
                       ('ETA прибытия', '2287-10-22 18:00 (1 д 12 ч)')),
            muted('Пересчитывается автоматически при изменении маршрута. '
                  'Кнопки «рассчитать» нет: расчёт инициирует система.')),
       'UC-6 выполняет система внутри UC-1 и UC-5, у прецедента нет актора-человека — '
       'поэтому на экране нет ни одной кнопки запуска расчёта, только его результат '
       'и раскрытие, из чего ETA получена.',
       size='1180x800')

# --- UC-7 -------------------------------------------------------------------
screen(7, 'risk-score', 'Рассчитать risk_score',
       card(None,
            rhead('Реестр рейсов',
                  [muted('данные на 2287-10-21 14:20 · показано 2 · в срезе 3'),
                   link('Обновить')]),
            table(REG_HEADERS + [''],
                  [REG_ROWS[0] + [link('Пересчитать риск')],
                   REG_ROWS[1] + [link('Пересчитать риск')]], wrap=True)),
       'risk_score раскрывается тем же модальным окном, что и в коде '
       '(components/RiskModal.tsx): источник данных и их возраст, вклад каждого участка, '
       'арифметика оценки и вытекающая из неё рекомендация (UC-8).',
       size='1400x1150',
       modal=('<div class="modal-overlay"><div class="modal">'
              '<div class="modal-head"><h3>Как получен risk_score</h3>%s</div>'
              '%s%s%s%s%s%s'
              '</div></div>'
              % (link('✕'),
                 muted('R-1043 · Goodsprings → New Vegas · Южный объезд через Primm'),
                 '<div class="muted small modal-asof">Источник: Wasteland Intel, '
                 'данные на 2287-10-21 13:50</div>',
                 table(['Участок', 'Угроза', 'Уровень'],
                       [[a, b, c] for a, b, c in THREATS], cls='inner'),
                 derivation(None,
                            [('Сумма уровней угроз', '9'),
                             ('База = сумма × 6 (макс. 100)', '54'),
                             ('Ценность груза 5 000 крышек (5 000–19 999 → +20)', '+20')],
                            ('Итог = min(100, база + коэф. груза)', '74')),
                 '<div class="rec modal-rec">Рекомендуется охрана 3 чел. и '
                 'запас воды на 2 суток.</div>',
                 '<div class="modal-actions">%s%s</div>'
                 % (btn('Удалить оценку', 'danger'),
                    muted('после удаления нажмите «Пересчитать риск» в реестре — '
                          'оценка появится заново')))))

# --- UC-8 -------------------------------------------------------------------
screen(8, 'recommendation', 'Получить рекомендацию по охране и припасам',
       card('Рекомендация по рейсу R-1043',
            muted('Получатель: диспетчер караванов (автор заявки). '
                  'Рекомендация показывается в карточке рейса и в окне risk_score.'),
            derivation(None,
                       [('risk_score', '74 · Высокий'),
                        ('Длительность рейса', '1 д 12 ч'),
                        ('Ценность груза', '5 000 крышек')]),
            table(['Что рекомендовано', 'Норма', 'Основание'],
                  [['Охрана', '3 чел.', 'risk 60–79 → 3 охранника'],
                   ['Вода', '2 сут.', '36 ч в пути + запас 12 ч'],
                   ['Стимуляторы', '2 шт.', 'угроза «Когти смерти» на участке Primm → Nipton']],
                  cls='inner'),
            '<div class="rec">Рекомендуется охрана 3 чел. и запас воды на 2 суток.</div>',
            actions(btn('Перейти к назначению ролей'), link('Зарезервировать припасы'))),
       'Экран отвечает на вопрос «кому система формирует рекомендацию»: адресат назван '
       'первой же строкой — это диспетчер, создавший заявку. Две кнопки внизу ведут '
       'в прецеденты, которые рекомендацию потребляют: UC-9 и UC-13.',
       size='1180x900')

# --- UC-9 -------------------------------------------------------------------
screen(9, 'assign-staff', 'Назначить сотрудников на роли рейса',
       card('Роли рейса R-1043',
            muted('Рекомендация по рейсу: охрана 3 чел. (UC-8)'),
            '<div class="actor-row">%s%s</div>'
            % (sel('Роль', 'Охранник', 'Караван-мастер', 'Полевой медик', 'Кладовщик'),
               sel('Сотрудник', 'Маркус · свободен с 2287-10-21',
                   'Рауль · свободен с 2287-10-23',
                   'Бун · свободен с 2287-10-21')),
            actions(btn('Назначить')),
            table(['Роль', 'Сотрудник', 'Ставка', 'Статус назначения', ''],
                  [['Караван-мастер', 'Кэсседи', '120 крышек/сут', 'подтверждено', link('Снять')],
                   ['Охранник', 'Бун', '90 крышек/сут', 'подтверждено', link('Снять')],
                   ['Охранник', 'Маркус', '90 крышек/сут', 'ожидает подтверждения', link('Снять')],
                   ['Полевой медик', 'док Усанаги', '110 крышек/сут', 'подтверждено', link('Снять')]]),
            muted('Назначено 2 охранника из 3 рекомендованных.')),
       'Назначение ролей: одна строка выбора «роль + сотрудник» и таблица уже назначенных. '
       'Доступность сотрудника видна прямо в списке; полный список с занятостью — '
       'отдельный прецедент UC-10.',
       size='1180x950')

# --- UC-10 ------------------------------------------------------------------
screen(10, 'staff-available', 'Просмотреть доступных сотрудников',
       card(None,
            rhead('Сотрудники организации',
                  [muted('на 2287-10-21 · свободных 4 из 7'), link('Обновить')]),
            filterbar(
                chips('Роль', [('Караван-мастер', None, False), ('Охранник', None, True),
                               ('Медик', None, False), ('Кладовщик', None, False)]),
                fgroup(None, check('только свободные', True))),
            table(['Сотрудник', 'Роль', 'Ставка', 'Доступен с', 'Текущий рейс'],
                  [['Бун', 'Охранник', '90 крышек/сут', '2287-10-21', '—'],
                   ['Маркус', 'Охранник', '90 крышек/сут', '2287-10-21', '—'],
                   ['Рауль', 'Охранник', '85 крышек/сут', '2287-10-23',
                    '<span class="route-code">R-1041</span> в пути'],
                   ['Вероника', 'Охранник', '95 крышек/сут', '2287-10-22',
                    '<span class="route-code">R-1038</span> готов к отправке']])),
       'Список сотрудников с занятостью. Фильтр по роли и переключатель «только свободные» — '
       'тот же набор элементов, что и в отборе реестра, другой словарь значений.',
       size='1180x800')

# --- UC-11 ------------------------------------------------------------------
screen(11, 'manifest', 'Создать груз-манифест',
       form('Груз-манифест рейса R-1043',
            '<div class="segments">%s%s%s</div>'
            % (muted('Позиции манифеста'),
               ''.join('<div class="segment-row">'
                       '<select><option selected>%s</option></select>'
                       '<input type="number" value="%s">'
                       '<select><option selected>%s</option></select>%s</div>'
                       % (e(name), e(qty), e(unit), link('✕'))
                       for name, qty, unit in
                       [('Стимуляторы', '40', 'шт'), ('Антирадин', '25', 'шт'),
                        ('Бинты', '60', 'шт'), ('Чистая вода', '12', 'ящик')]),
               link('+ позиция')),
            inp('Общая масса (кг)', '186', kind='number'),
            area('Примечание к приёмке', '', 'Особые условия хранения, хрупкость...'),
            actions(btn('Сохранить манифест'), link('Печать на голотейп'))),
       'Манифест набирается позициями «наименование + количество + единица» — '
       'той же строкой, что и участки маршрута на UC-5. Ценность груза задаётся '
       'отдельным прецедентом UC-12, на этом экране её нет.',
       size='1180x900')

# --- UC-12 ------------------------------------------------------------------
screen(12, 'cargo-value', 'Указать ценность груза',
       form('Ценность груза · рейс R-1043',
            inp('Ценность груза (крышек)', '5000', kind='number', focus=True),
            muted('Диапазон 5 000–19 999 добавляет +20 к risk_score. '
                  'После сохранения оценка риска пересчитывается автоматически (UC-7).'),
            actions(btn('Сохранить'), link('Отмена'))),
       'Прецедент простой — экран тоже: одно поле, одна подсказка о последствии ввода '
       'и две кнопки. Ничего, кроме ввода ценности, на этом шаге не требуется.',
       size='1180x620')

# --- UC-13 ------------------------------------------------------------------
screen(13, 'supplies-reserve', 'Зарезервировать припасы',
       form('Резерв припасов · рейс R-1043',
            muted('Рекомендация по рейсу: вода на 2 суток, стимуляторы 2 шт (UC-8)'),
            table(['Припас', 'Нужно', 'На складе', 'Резервируем'],
                  [['Чистая вода', '24 л', '180 л',
                    '<input type="number" value="24">'],
                   ['Стимуляторы', '2 шт', '14 шт', '<input type="number" value="2">'],
                   ['Патроны 5.56', '120 шт', '90 шт',
                    '<input type="number" value="90" class="input-error">']]),
            err('Патронов на складе меньше запрошенного: 90 из 120. '
                'Резерв будет создан на доступное количество.'),
            actions(btn('Зарезервировать'), link('Отмена'))),
       'Резервирование припасов под рекомендацию UC-8. Нехватка на складе показана '
       'сообщением об ошибке и подсветкой поля — это альтернативный поток прецедента, '
       'а не отдельный экран.',
       size='1180x800')

# --- UC-14 ------------------------------------------------------------------
screen(14, 'delivery-confirm', 'Подтвердить доставку груза (с пломбой)',
       form('Подтверждение доставки',
            inp('Номер пломбы', 'SL-88214', focus=True),
            check('Пломба цела, следов вскрытия нет', True),
            inp('ФИО принимающего', 'Рейчел'),
            area('Примечание', '', 'Заполняется при повреждении пломбы'),
            actions(btn('Подтвердить доставку'), link('Пломба нарушена'))),
       'Полевой экран караван-мастера: минимум полей, крупные элементы. Нарушенная пломба '
       'уводит в альтернативный поток — фиксацию инцидента (UC-19), поэтому это вторая '
       'ссылка, а не обязательное поле формы.',
       size='1180x800', **FIELD)

# --- UC-15 ------------------------------------------------------------------
screen(15, 'manifest-check', 'Выполнить сверку манифеста при приёмке',
       form('Сверка манифеста · рейс R-1043',
            table(['Позиция', 'По манифесту', 'Принято', 'Расхождение'],
                  [['Стимуляторы', '40 шт', '<input type="number" value="40">', '—'],
                   ['Антирадин', '25 шт', '<input type="number" value="25">', '—'],
                   ['Бинты', '60 шт',
                    '<input type="number" value="54" class="input-error">',
                    '<span class="attention-mark">−6 шт</span>'],
                   ['Чистая вода', '12 ящ', '<input type="number" value="12">', '—']]),
            area('Причина расхождения', '',
                 'Обязательна, если расхождение не нулевое'),
            actions(btn('Завершить приёмку'), link('Оформить расхождение актом'))),
       'Сверка выполняется исполнителем приёмки — на диаграмме это одна обобщённая роль '
       'для кладовщика и караван-мастера. Расхождение помечается прямо в строке; '
       'причина обязательна только при ненулевом расхождении.',
       size='1180x800', **FIELD)

# --- UC-16 ------------------------------------------------------------------
screen(16, 'stage-log', 'Зафиксировать прохождение этапа рейса',
       card('Этапы рейса R-1043',
            '<div class="status-current"><span class="muted">Текущий статус:</span>%s</div>'
            % sbadge('EN_ROUTE'),
            table(['Этап', 'Пункт', 'План', 'Факт', ''],
                  [['1', 'Goodsprings → Primm', '2287-10-21 14:00',
                    '2287-10-21 13:40', '<span class="muted">пройден</span>'],
                   ['2', 'Primm → Nipton', '2287-10-21 21:00',
                    '2287-10-21 21:25', '<span class="muted">пройден</span>'],
                   ['3', 'Nipton → Novac', '2287-10-22 09:00', '—',
                    btn('Отметить прохождение')],
                   ['4', 'Novac → New Vegas', '2287-10-22 18:00', '—',
                    '<span class="muted">недоступен</span>']]),
            muted('Этапы отмечаются по порядку: следующий становится доступен после '
                  'предыдущего. Отставание от плана переводит рейс в статус «Задержка».')),
       'Журнал этапов рейса: пройденные — фактом и временем, текущий — единственной '
       'активной кнопкой. Такой порядок снимает вопрос «какой этап отмечать» и делает '
       'экран пригодным для работы на ходу.',
       size='1180x800', **FIELD)

# --- UC-17 ------------------------------------------------------------------
screen(17, 'checkpoint', 'Отметить прохождение контрольной точки',
       form('Контрольная точка',
            sel('Точка', 'Nipton · перекрёсток у вышки',
                'Novac · мотель Dino Dee-lite', 'Primm · мост'),
            inp('Время прохождения', '2287-10-22 09:15', focus=True),
            area('Отметка', '', 'Необязательно'),
            actions(btn('Отметить'))),
       'Самый короткий полевой экран: что прошли, когда и необязательная отметка. '
       'Контрольная точка — часть этапа (UC-16), поэтому ни статуса, ни списка '
       'этапов здесь не дублируется.',
       size='1180x700', **FIELD)

# --- UC-18 ------------------------------------------------------------------
screen(18, 'ncr-gate', 'Отметить прохождение КПП (с пошлиной)',
       form('Прохождение КПП',
            sel('КПП', 'NCR · Mojave Outpost', 'NCR · Camp Searchlight',
                'NCR · Hoover Dam'),
            inp('Пошлина (крышек)', '240', kind='number'),
            muted('Ставка получена из NCR Checkpoint & Tax Terminal, '
                  'данные на 2287-10-22 08:30 (UC-24): 4% от ценности груза.'),
            inp('Номер квитанции', 'NCR-TX-55102'),
            inp('Время прохождения', '2287-10-22 10:05'),
            actions(btn('Отметить прохождение'), link('Пошлина оспорена'))),
       'Сумма пошлины приходит из интеграции и подставляется в поле, но остаётся '
       'редактируемой — на случай расхождения с квитанцией. Источник и возраст данных '
       'подписаны под полем, как и в окне risk_score.',
       size='1180x850', **FIELD)

# --- UC-19 ------------------------------------------------------------------
screen(19, 'incident', 'Сообщить об инциденте в рейсе',
       form('Инцидент в рейсе R-1043',
            sel('Тип инцидента', 'Нападение', 'Поломка', 'Потеря груза',
                'Травма сотрудника', 'Погодные условия'),
            chips('Серьёзность', [('Низкая', '#33ff66', False),
                                  ('Средняя', '#ffd633', False),
                                  ('Высокая', '#ff9800', True),
                                  ('Критическая', '#ff4444', False)]),
            inp('Место', 'Участок Nipton → Novac, 12 км от Nipton'),
            area('Описание', 'Нападение рейдеров, двое охранников ранены, груз цел.',
                 'Что произошло, последствия для груза и людей'),
            actions(btn('Отправить сообщение'), link('Запросить эвакуацию'))),
       'Карточка инцидента. Сообщение уходит диспетчеру рейса — он и есть получатель '
       'уведомления на диаграмме прецедента. Критическая серьёзность предлагает сразу '
       'перейти к запросу эвакуации (UC-20).',
       size='1180x900', **FIELD)

# --- UC-20 ------------------------------------------------------------------
screen(20, 'recovery-request', 'Инициировать RecoveryRequest',
       form('Запрос на эвакуацию · R-1043',
            muted('Основание: инцидент INC-204 «Нападение», серьёзность высокая (UC-19)'),
            sel('Причина', 'Потеря хода каравана', 'Угроза жизни сотрудников',
                'Утрата груза', 'Блокировка маршрута'),
            '<div class="filter-group"><div class="filter-title">Что требуется</div>%s%s%s</div>'
            % (check('медицинская помощь', True),
               check('вооружённое сопровождение', True),
               check('транспорт для груза', False)),
            inp('Координаты', '12 км к северу от Nipton, у разрушенной заправки'),
            area('Комментарий', '', 'Что критично для эвакуационной группы'),
            actions(btn('Отправить RecoveryRequest'), link('Отмена'))),
       'Запрос на эвакуацию заводится из инцидента, поэтому его основание подставлено '
       'и показано первой строкой. Набор требуемой помощи — флажки, а не отдельные экраны.',
       size='1180x950', **FIELD)

# --- UC-21 ------------------------------------------------------------------
screen(21, 'financial-report', 'Сформировать финансовый отчёт по рейсу',
       card(None,
            rhead('Отчёты по рейсам',
                  [muted('завершённых рейсов 9'), link('Обновить')]),
            filterbar(
                fgroup('Поиск рейса',
                       '<input type="text" value="R-10" '
                       'placeholder="id рейса, маршрут, пункт" class="mock-focus">'),
                fgroup('Период', '<select><option selected>Октябрь 2287</option>'
                                 '<option>Сентябрь 2287</option>'
                                 '<option>Весь архив</option></select>'),
                chips('Статус', [('Доставлен', '#33ff66', True),
                                 ('Закрыт', '#55aa77', True)])),
            table(['Рейс', 'Маршрут', 'Завершён', 'Статус отчёта', ''],
                  [['<span class="route-code">R-1035</span>',
                    'Goodsprings &rarr; New Vegas', '2287-10-18', 'сформирован',
                    link('Открыть')],
                   ['<span class="route-code">R-1029</span>',
                    'Primm &rarr; Novac', '2287-10-12', 'не сформирован',
                    btn('Сформировать')],
                   ['<span class="route-code">R-1012</span>',
                    'Primm &rarr; New Vegas', '2287-09-30', 'сформирован',
                    link('Открыть')]])) +
       card('Финансовый отчёт · рейс R-1035',
            muted('Goodsprings → New Vegas · завершён 2287-10-18 · '
                  'сформирован 2287-10-21 14:05'),
            derivation(None,
                       [('Оплата за перевозку', '3 200 крышек'),
                        ('Оплата сотрудников (4 чел. × 2 сут.)', '−820 крышек'),
                        ('Пошлины КПП', '−240 крышек'),
                        ('Припасы и расходники', '−310 крышек'),
                        ('Списание по расхождению манифеста', '−60 крышек')],
                       ('Итог по рейсу', '1 770 крышек')),
            actions(btn('Экспортировать на голотейп'), link('Пересчитать'))),
       'Замечание «непонятно, как найти нужный отчёт» закрыто первой карточкой: поиск '
       'по рейсу, период и статус отчёта, а в строке — действие «Сформировать» или '
       '«Открыть». Вторая карточка — сам отчёт с раскрытой арифметикой.',
       size='1180x1250')

# --- UC-22 ------------------------------------------------------------------
screen(22, 'export-holotape', 'Экспортировать отчёт на голотейп',
       form('Экспорт отчёта · рейс R-1035',
            sel('Формат', 'Голотейп (.holo)', 'Печать на терминале', 'Текстовый дамп'),
            check('включить журнал изменений статусов', True),
            check('включить акт расхождения манифеста', False),
            actions(btn('Экспортировать'), link('Отмена')),
            '<div class="registry-state">%s%s</div>'
            % ('<div class="muted">Готово: R-1035-report.holo · 24 КБ</div>',
               '<div class="registry-state-actions">%s%s</div>'
               % (link('Записать на голотейп'), link('Сохранить копию')))),
       'Экспорт — продолжение UC-21, поэтому отчёт не выбирается заново: он уже открыт. '
       'Форма сведена к формату и двум необязательным вложениям; результат показан '
       'тем же блоком состояния, что и в реестре.',
       size='1180x800')

# --- UC-23 ------------------------------------------------------------------
screen(23, 'intel-threats', 'Получить данные об угрозах',
       card('Wasteland Intel · данные об угрозах',
            muted('Последнее обновление: 2287-10-21 13:50 · следующее по '
                  'расписанию: 14:50 · данные актуальны'),
            table(['Участок', 'Угроза', 'Уровень', 'Обновлено'],
                  [[a, b, c, '2287-10-21 13:50'] for a, b, c in THREATS], cls='inner'),
            muted('Если Intel недоступен более 24 часов, рейсы помечаются отметкой '
                  '«risk_score по устаревшим данным», а при полном отсутствии ответа — '
                  'risk_score не рассчитывается (Н/Д).'),
            actions(link('Обновить сейчас'))),
       'Интеграционный прецедент: инициатор — система, человек видит только кэш '
       'и его возраст. Ручное обновление оставлено ссылкой, а не кнопкой действия, '
       'потому что штатно данные тянутся по расписанию.',
       size='1180x800')

# --- UC-24 ------------------------------------------------------------------
screen(24, 'ncr-tariffs', 'Получить данные о КПП и пошлинах',
       card('NCR Checkpoint & Tax Terminal · КПП и ставки',
            muted('Последнее обновление: 2287-10-22 08:30 · данные актуальны'),
            table(['КПП', 'Положение', 'Ставка', 'Обновлено'],
                  [['Mojave Outpost', 'Goodsprings → Primm', '4% от ценности груза',
                    '2287-10-22 08:30'],
                   ['Camp Searchlight', 'Nipton → Novac', '120 крышек фикс.',
                    '2287-10-22 08:30'],
                   ['Hoover Dam', 'Novac → New Vegas', '6% от ценности груза',
                    '2287-10-21 20:10']], cls='inner'),
            muted('При недоступности терминала пошлина вводится вручную по квитанции '
                  '(альтернативный поток UC-18).'),
            actions(link('Обновить сейчас'))),
       'Второй интеграционный прецедент, построен так же, как UC-23: кэш ставок, '
       'возраст данных и правило на случай недоступности внешней системы.',
       size='1180x800')

# --- UC-25 ------------------------------------------------------------------
screen(25, 'login', 'Аутентификация',
       form('Вход в систему',
            inp('Логин', 'j.masterson', focus=True),
            inp('Пароль', '', kind='password'),
            err('Неверный логин или пароль. Осталось попыток: 4.'),
            actions(btn('Войти'), link('Забыли пароль?'))),
       'Вход одинаков для всех ролей, поэтому и на диаграмме прецедента вместо шести '
       'акторов один — «Пользователь системы». Роль определяется после входа, на экране '
       'её не выбирают.',
       size='1180x700', banner=None,
       h1='CARAVAN // ACCESS TERMINAL', header_links=())

# --- UC-26 ------------------------------------------------------------------
screen(26, 'user-create', 'Создать учётную запись пользователя',
       form('Новая учётная запись',
            inp('ФИО', 'Вероника Санторо'),
            inp('Логин', 'v.santoro'),
            sel('Роль', 'Капитан охраны', 'Диспетчер караванов', 'Караван-мастер',
                'Кладовщик', 'Полевой медик'),
            inp('Email / холофон', 'v.santoro@crimson.caravan'),
            inp('Временный пароль', 'Tx7-mojave-41'),
            check('потребовать смену пароля при первом входе', True),
            actions(btn('Создать учётную запись'), link('Отмена'))),
       'Создание учётной записи доступно и диспетчеру в своей организации, и '
       'суперпользователю — на диаграмме это одна обобщённая роль «Администратор '
       'учётных записей», поэтому экран один.',
       size='1180x950', banner=None)

# --- UC-27 ------------------------------------------------------------------
screen(27, 'user-role', 'Изменить роль пользователя',
       form('Учётная запись · Вероника Санторо',
            '<div class="status-current"><span class="muted">Текущая роль:</span>'
            '<span class="status-badge">Капитан охраны</span></div>',
            sel('Новая роль', 'Караван-мастер', 'Диспетчер караванов',
                'Кладовщик', 'Полевой медик'),
            area('Основание', '', 'Фиксируется в журнале изменений'),
            muted('Права пересчитываются при следующем входе пользователя.'),
            actions(btn('Изменить роль'), link('Отмена'))),
       'Смена роли: текущее значение показано бейджем, новое выбирается списком, '
       'основание уходит в журнал. Никаких матриц прав на экране нет — права '
       'определяются ролью.',
       size='1180x800', banner=None)

# --- UC-28 ------------------------------------------------------------------
screen(28, 'user-deactivate', 'Деактивировать учётную запись',
       form('Деактивация · Рауль Техада',
            '<div class="status-current"><span class="muted">Статус:</span>'
            '<span class="status-badge" style="border-color:#33ff66;color:#33ff66">'
            'Активна</span></div>',
            area('Причина деактивации', '', 'Фиксируется в журнале изменений'),
            err('У пользователя есть активное назначение на рейс R-1041. '
                'Снимите назначение или дождитесь завершения рейса.'),
            actions(btn('Деактивировать', 'danger'), link('Отмена'))),
       'Деактивация — необратимое для пользователя действие, поэтому кнопка выделена '
       'красным, а блокирующая проверка (активное назначение) показана до нажатия, '
       'а не после.',
       size='1180x780', banner=None)

# --- UC-29 ------------------------------------------------------------------
screen(29, 'profile-edit', 'Редактировать свои учётные данные',
       form('Мои данные',
            inp('ФИО', 'Джед Мастерсон'),
            inp('Email / холофон', 'j.masterson@crimson.caravan'),
            muted('Логин и роль меняет администратор учётных записей (UC-27).'),
            inp('Текущий пароль', '', kind='password'),
            inp('Новый пароль', '', kind='password'),
            inp('Повторите новый пароль', '', kind='password'),
            actions(btn('Сохранить'), link('Отмена'))),
       'Свой профиль правит любой вошедший пользователь независимо от роли — на '
       'диаграмме это один актор «Аутентифицированный пользователь». Поля, которые '
       'пользователь менять не вправе, не выведены вовсе.',
       size='1180x1000', banner=None)

# --- UC-30 ------------------------------------------------------------------
screen(30, 'credentials-reset', 'Сбросить учётные данные пользователя',
       form('Сброс учётных данных',
            sel('Пользователь', 'Кэсседи · c.cassidy · Караван-мастер',
                'Рейчел · r.wells · Кладовщик',
                'Маркус · m.stone · Капитан охраны'),
            inp('Временный пароль', 'Qm4-novac-77'),
            check('потребовать смену пароля при первом входе', True),
            check('завершить все активные сессии пользователя', True),
            actions(btn('Сбросить'), link('Отмена')),
            '<div class="registry-state">%s%s</div>'
            % ('<div class="muted">Пароль сброшен. Временный пароль передан '
               'пользователю по холофону.</div>',
               '<div class="registry-state-actions">%s</div>' % link('Скопировать'))),
       'Сброс выполняет администратор учётных записей — та же обобщённая роль, что '
       'и в UC-26. Экран повторяет форму создания записи, поэтому отдельного словаря '
       'элементов для него не понадобилось.',
       size='1180x950', banner=None)

# --- UC-31 ------------------------------------------------------------------
screen(31, 'employee-rate', 'Назначить/изменить ставку сотрудника',
       form('Ставка сотрудника',
            sel('Сотрудник', 'Бун · Охранник', 'Маркус · Охранник',
                'Кэсседи · Караван-мастер'),
            inp('Текущая ставка (крышек/сут)', '90', disabled=True),
            inp('Новая ставка (крышек/сут)', '105', kind='number', focus=True),
            inp('Действует с', '2287-11-01', kind='date'),
            muted('Ставка применяется к рейсам, начатым после указанной даты. '
                  'Уже сформированные отчёты не пересчитываются.'),
            actions(btn('Сохранить ставку'), link('Отмена'))),
       'Ставка влияет на финансовый отчёт (UC-21), поэтому на экране явно сказано, '
       'с какого момента она действует и что прошлые отчёты не меняются.',
       size='1180x900')

# --- UC-32 ------------------------------------------------------------------
screen(32, 'org-create', 'Создать организацию', '',
       'Консоль суперпользователя — единственное место, где трёхколоночная раскладка '
       'действительно реализована (pages/Organizations.tsx). Шаг 1 мастера: реквизиты '
       'организации и уровень подписки; правая колонка показывает, что будет создано.',
       size='1500x1150', shell='admin',
       admin=dict(
           mode='SUPERUSER MODE', nav='ORGANIZATIONS',
           panels=[admin_form(
               'CREATE ORGANIZATION', 'WIZARD · STEP 1 / 2',
               '<div class="admin-info">Организация создаётся вместе с изолированным '
               'tenant-пространством. Уровень подписки определяет лимиты и объём '
               'данных Wasteland Intel.</div>',
               '<div class="admin-stepper">'
               '<div class="admin-step active">[1] ORGANIZATION</div>'
               '<div class="admin-step">[2] FIRST DISPATCHER</div></div>',
               admin_block('STEP 1 · ORGANIZATION',
                           admin_inp('NAME', 'Gun Runners'),
                           admin_inp('REGION', 'Mojave · New Vegas'),
                           '<div class="full">%s</div>' % tier_grid('STANDARD'),
                           admin_area('LEGAL ADDRESS',
                                      'Freeside, северные ворота, склад 2'),
                           admin_inp('PRIMARY CONTACT', 'Изабелла Санторо'),
                           admin_inp('HOLOPHONE / EMAIL', 'ops@gunrunners.mojave')),
               '<div class="admin-actions">%s%s</div>'
               % (btn('BACK'), btn('NEXT · FIRST DISPATCHER', 'create-button')))],
           summary=admin_sum(
               sum_sec('-- ORGANIZATION --',
                       [('Name', 'Gun Runners'), ('Tier', 'STANDARD'),
                        ('Billing', '600 caps / мес.'), ('Region', 'Mojave · New Vegas')]),
               sum_sec('-- FIRST DISPATCHER --',
                       [('Status', 'шаг 2'), ('Login', '—'), ('Access', '—')]),
               sum_effect('БУДЕТ СОЗДАНО',
                          ['+ TENANT scope', '+ ORG catalog row', '+ AUDIT event']))))

# --- UC-33 ------------------------------------------------------------------
screen(33, 'first-dispatcher', 'Назначить первого диспетчера организации', '',
       'Шаг 2 того же мастера. Флажок «SKIP» оставляет организацию без диспетчера — '
       'альтернативный поток прецедента; остальные поля при этом гаснут, а не '
       'исчезают, чтобы состав формы не прыгал.',
       size='1500x1150', shell='admin',
       admin=dict(
           mode='SUPERUSER MODE', nav='ORGANIZATIONS',
           panels=[admin_form(
               'CREATE ORGANIZATION', 'WIZARD · STEP 2 / 2',
               '<div class="admin-info">Первый диспетчер получает права администратора '
               'учётных записей внутри своей организации.</div>',
               '<div class="admin-stepper">'
               '<div class="admin-step">[1] ORGANIZATION</div>'
               '<div class="admin-step active">[2] FIRST DISPATCHER</div></div>',
               admin_block('STEP 2 · FIRST DISPATCHER',
                           '<label class="check-row full"><input type="checkbox"> '
                           'SKIP · создать организацию без диспетчера</label>',
                           admin_inp('FULL NAME', 'Изабелла Санторо'),
                           admin_inp('LOGIN', 'i.santoro'),
                           admin_inp('INITIAL PASSWORD', 'Gr7-freeside-02'),
                           admin_inp('EMAIL / HOLOPHONE', 'i.santoro@gunrunners.mojave')),
               '<div class="admin-success">Проверка пройдена: логин i.santoro свободен.</div>',
               '<div class="admin-actions">%s%s</div>'
               % (btn('BACK'), btn('CREATE ORGANIZATION', 'create-button')))],
           summary=admin_sum(
               sum_sec('-- ORGANIZATION --',
                       [('Name', 'Gun Runners'), ('Tier', 'STANDARD'),
                        ('Billing', '600 caps / мес.'), ('Region', 'Mojave · New Vegas')]),
               sum_sec('-- FIRST DISPATCHER --',
                       [('Status', 'будет создан'), ('Login', 'i.santoro'),
                        ('Access', 'ORG ADMIN')]),
               sum_effect('БУДЕТ СОЗДАНО',
                          ['+ TENANT scope', '+ ORG catalog row', '+ USER account',
                           '+ AUDIT event']))))

# --- UC-34 ------------------------------------------------------------------
screen(34, 'subscription', 'Управлять подписками', '',
       'Раздел SUBSCRIPTIONS той же консоли. Истечение подписки — отдельная часть '
       'прецедента, которую выполняет система без участия человека, поэтому на экране '
       'она присутствует только предупреждением о сроке, без кнопки.',
       size='1500x1150', shell='admin',
       admin=dict(
           mode='SUPERUSER MODE', nav='SUBSCRIPTIONS',
           panels=[admin_form(
               'SUBSCRIPTION', 'TENANT :: crimson',
               '<div class="admin-info">Смена уровня применяется со следующего '
               'расчётного периода. Понижение уровня блокируется, если текущие '
               'показатели организации превышают лимиты нового уровня.</div>',
               admin_block('CURRENT PLAN',
                           admin_inp('ORGANIZATION', 'Crimson Caravan Company',
                                     disabled=True),
                           admin_inp('TIER', 'STANDARD', disabled=True),
                           admin_inp('PAID UNTIL', '2287-11-30', disabled=True),
                           admin_inp('USAGE', '7 диспетчеров · 214 рейсов / мес',
                                     disabled=True)),
               admin_block('CHANGE TIER',
                           '<div class="full">%s</div>' % tier_grid('PRO'),
                           '<label class="check-row full"><input type="checkbox" checked> '
                           'перенести остаток оплаченного периода</label>'),
               '<div class="admin-info">Подписка истекает через 9 дней. По истечении '
               'система переводит организацию в режим «только чтение» автоматически.</div>',
               '<div class="admin-actions">%s%s</div>'
               % (btn('CANCEL'), btn('APPLY CHANGE', 'create-button'))),
               admin_panel('SUBSCRIPTION REGISTRY', '7 TENANTS',
                           '<div class="org-list">%s</div>'
                           % table(['Tenant', 'Организация', 'Подписка', 'Оплачено до',
                                    'Статус'],
                                   [['crimson', 'Crimson Caravan Company', 'STANDARD',
                                     '2287-11-30', 'активна'],
                                    ['gunrun', 'Gun Runners', 'STANDARD', '2287-12-15',
                                     'активна'],
                                    ['vanm', 'Van Graffs', 'BASIC', '2287-10-31',
                                     'истекает'],
                                    ['cwater', 'Crimson Water', 'BASIC', '2287-10-14',
                                     'только чтение']]))],
           summary=admin_sum(
               sum_sec('-- CURRENT --',
                       [('Tier', 'STANDARD'), ('Billing', '600 caps / мес.'),
                        ('Paid until', '2287-11-30')]),
               sum_sec('-- AFTER CHANGE --',
                       [('Tier', 'PRO'), ('Billing', '1 500 caps / мес.'),
                        ('Effective', '2287-12-01')]),
               sum_effect('БУДЕТ ПРИМЕНЕНО',
                          ['+ лимиты PRO', '+ Intel live-feed + API',
                           '+ AUDIT event']))))


# ----------------------------------------------------------------------------
# сборка
# ----------------------------------------------------------------------------

def page_html(s):
    title = 'UC-%d · %s — макет экрана' % (s['n'], s['title'])
    caption = ('<div class="mock-caption-bar"><div class="mock-caption">'
               '<b>UC-%d. %s</b><br>%s</div></div>'
               % (s['n'], e(s['title']), e(s['caption'])))
    if s['shell'] == 'admin':
        a = s['admin']
        body = admin_shell(a['mode'], a['panels'], a['summary'], a['nav']) + NL + caption
    else:
        main = (s['banner'] or '') + s['body']
        body = app_shell(s['h1'], main, s['header_links'], s['modal']) + NL + caption
    return HEAD.format(title=at(title), size=s['size']) + body + TAIL


def main():
    print('таблица стилей: %s' % os.path.basename(build_css()))
    written = []
    for s in SCREENS:
        name = 'uc-%02d-%s.html' % (s['n'], s['slug'])
        path = os.path.join(OUT_DIR, name)
        io.open(path, 'w', encoding='utf-8', newline=NL).write(page_html(s))
        written.append(name)
    print('макетов записано: %d' % len(written))
    nums = sorted(x['n'] for x in SCREENS)
    missing = [n for n in range(1, 35) if n not in nums]
    if missing:
        print('ПРОПУЩЕНЫ прецеденты: %s' % missing)
    for name in written:
        print('  ' + name)


if __name__ == '__main__':
    main()
