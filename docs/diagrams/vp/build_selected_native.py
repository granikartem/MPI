#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Direct native Visual Paradigm XML assembly of the nine reviewed SAD diagrams.

The JSON specifications are explicit, editable diagram definitions: model elements,
compartments, nesting, exact coordinates, message kinds, and connector routes.
This builder does not invoke puml2vp, PlantUML, Graphviz, or SVG conversion.
Run: python3 docs/diagrams/vp/build_selected_native.py [diagram names ...]
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from vpgen import Project, _q

HERE = Path(__file__).resolve().parent
SPECS = HERE / 'specs'
OUT = HERE / 'out'
BLACK = 'Cr:51,51,51,255'
OUTLINE = 'Cr:0,0,0,255'
GREY = 'Cr:245,245,245,255'


def prop(host, kind, name, value):
    old = next((e for e in host if e.get('name') == name), None)
    if old is not None:
        host.remove(old)
    if isinstance(value, bool):
        value = str(value).lower()
    return ET.SubElement(host, _q(kind + 'Property'), {'name': name, 'value': str(value)})


def font(element, size=13, bold=False):
    f = ET.Element(_q('ElementFont'), {'name': 'Arial', 'size': str(size),
                                      'style': '1' if bold else '0', 'color': BLACK})
    # Schema order: properties, font, line, caption, children, fill.
    element.insert(1 if element.find(_q('DiagramElementProperties')) is not None else 0, f)


def rich(text, size=13, align='left', bold=False):
    lines = []
    for line in text.split('\n'):
        chunks = line.split('**')
        line = ''.join(('<b>' + html.escape(c) + '</b>') if i % 2 else html.escape(c)
                       for i, c in enumerate(chunks))
        line = re.sub(r'&lt;&lt;([^<>]*?)&gt;&gt;', r'«\1»', line)
        if bold:
            line = '<b>' + line + '</b>'
        lines.append(line or '&nbsp;')
    result='<br>'.join(lines)
    if any(line.startswith('|') for line in text.split('\n')):
        table=[];before=[];after=[];in_table=False
        for raw,line in zip(text.split('\n'),lines):
            if raw.startswith('|'):
                in_table=True;cells=[]
                for cell in raw.strip('|').split('|'):
                    header=cell.strip().startswith('=');cell=cell.strip().lstrip('= ').strip()
                    color=re.search(r'<#([A-Fa-f0-9]{6})>',cell)
                    cell=re.sub(r'<#[A-Fa-f0-9]{6}>','',cell)
                    cell=html.escape(cell).replace('**','')
                    tag='th' if header else 'td'
                    cells.append('<%s%s>%s</%s>'%(tag,' bgcolor="#'+color.group(1)+'"' if color else '',cell or '&nbsp;',tag))
                table.append('<tr>'+''.join(cells)+'</tr>')
            elif in_table:after.append(line)
            else:before.append(line)
        result='<br>'.join(before)+'<table border="1" cellspacing="0" cellpadding="1">'+''.join(table)+'</table>'+'<br>'.join(after)
    return ('<html><body><p align="%s" style="margin-top:0;margin-bottom:0;'
            'font-family:Arial;font-size:%dpx;font-weight:normal">%s</p></body></html>') % (align, size, result)


class NativeDiagram:
    def __init__(self, spec):
        self.spec = spec
        self.p = Project(spec['name'])
        # Stable, diagram-scoped IDs allow importing all nine into one project.
        ids = self.p.ids
        prefix = hashlib.sha256(spec['name'].encode()).hexdigest()[:5]
        self.p.ids = lambda hint: ids(prefix + '_' + hint)
        self.d = self.p.diagram(spec['name'], spec['type'])
        dp = ET.Element(_q('DiagramProperties'))
        self.d.el.insert(0, dp)
        for name, value in [('showSequenceNumbers', False), ('autoFitShapesSize', False),
                            ('alignToGrid', False), ('gridVisible', False),
                            ('paintConnectorThroughLabel', True)]:
            prop(dp, 'Boolean', name, value)
        if spec['type']=='InteractionDiagram':
            prop(dp,'Boolean','autoExtendActivations',False)
            prop(dp,'Boolean','showActivations',False)
            prop(dp,'Boolean','showMessageName',False)
            prop(dp,'Integer','displayLifeLinesAsRobustnessAnalysisIcon',1)
        self.models = {}
        self.shapes = {}
        self.n = 0

    def hint(self, value):
        self.n += 1
        return '%s%03d' % (value, self.n)

    def shape(self, kind, model, rect, name=None, fill=None, parent=None, caption=True):
        s = self.d.shape(kind, model, *[round(x) for x in rect], name=name,
                         fill=fill, parent=self.d.child_shapes(parent) if parent else None,
                         caption=caption, hint=self.hint('S'))
        prop(s.dep, 'Boolean', 'requestResetCaption', bool(name))
        prop(s.dep, 'Boolean', 'requestResetCaptionSize', False)
        prop(s.dep, 'Boolean', 'requestFitSize', False)
        font(s.el)
        if kind == 'TextBox':
            # The default TextBox outline is a presentation aid, absent in the PNG.
            s.el.insert(2, ET.Element(_q('Line'), {'cap':'0','color':BLACK,'weight':'1','transparency':'0'}))
        elif kind=='Rectangle':
            # Line transparency is a percentage: 100 makes the outline invisible.
            # Activation bars, package frames, and participant footers need an
            # explicit opaque stroke, independently of their white/grey fill.
            s.el.insert(2,ET.Element(_q('Line'),{'cap':'0','color':OUTLINE,'weight':'1','transparency':'0'}))
            if rect[2]>2 and rect[3]>2:
                self.rectangle_outline(s,rect)
        return s

    def rectangle_outline(self,owner,rect):
        """Paint a guaranteed black contour for VP's generic rectangle renderer.

        VP 16.1 stores Line.color correctly but paints some Rectangle outlines
        using the fill color. An opaque black vector contour gives each one a
        visible border, so white bars and pale frames retain a visible
        outline. Keeping it as a child also preserves group movement.
        """
        x,y,w,h=rect
        self.vector_path(owner,rect,[[0,0],[w-1,0],[w-1,h-1],[0,h-1],[0,0]],'BORDER')

    def vector_path(self,owner,rect,vertices,hint,color=OUTLINE,dashed=False):
        model=self.p.model('Freehand',name='',hint=self.hint(hint))
        # Freehand paints only its segments, but VP takes their color from its
        # fill setting as well. An opaque black fill does not fill the polygon.
        contour=self.shape('Freehand',model,rect,caption=False,fill=color,parent=owner)
        prop(contour.dep,'Color','foreground',color)
        points=ET.Element(_q('FreehandPoints'));contour.el.insert(1,points)
        for px,py in vertices:
            point=ET.SubElement(points,_q('Point'))
            props=ET.SubElement(point,_q('DiagramElementProperties'))
            prop(props,'Point','value','Pt:%.1f,%.1f'%(px,py))
        line=ET.Element(_q('Line'),{'cap':'0','color':color,'weight':'1','transparency':'0'})
        if dashed:
            dashes=ET.SubElement(ET.SubElement(line,_q('Stroke')),_q('Dashes'))
            for length in [4,4]:ET.SubElement(dashes,_q('Dash'),{'value':str(length)})
        contour.el.insert(3,line)
        return contour

    def lifeline(self,item,owner):
        """Keep the time axis visible inside combined fragments as well.

        VP's sequence renderer omits lifeline sections covered by fragments and
        presents InteractionActor bodies as solid execution bars. An explicit
        dashed vector supplements the native participant without those gaps.
        """
        x,y,w,h=item['rect'];centre=x+w//2
        # One dashed presentation avoids overlapping VP's segmented black line
        # with our complete grey time axis. Participant names remain native.
        owner.el.insert(2,ET.Element(_q('Line'),{'cap':'0','color':OUTLINE,'weight':'1','transparency':'100'}))
        if item['kind']=='InteractionActor':
            # Hide the native full-height actor bar and supply a normal actor
            # header. Messages still connect to the native InteractionActor.
            owner.fill='Cr:255,255,255,0'
            owner.el.find(_q('Caption')).set('visible','false')
            actor=self.p.model('Actor',name=item['name'],hint=self.hint('ACTOR'))
            self.p.ref_prop(self.models[item['key']],'referencedActor',actor.id)
            self.shape('Actor',actor,[centre-15,y,30,60],caption=False,fill=GREY,parent=owner)
            height=len(item['name'].split('\n'))*16+6
            self.text(item['name'],[x,y+65,w,height],13,'center',parent=owner)
            start=y+65+height
        else:
            self.rectangle_outline(owner,[x,y,w,36])
            start=y+36
        end=self.spec['tail_y']
        graphic=self.vector_path(owner,[centre,start,2,end-start+1],
                                 [[0,0],[0,end-start]],'LIFE','Cr:120,120,120,255',True)
        prop(graphic.dep,'Boolean','lifelineGraphic',True)

    def text(self, text, rect, size=13, align='left', bold=False, parent=None):
        s = self.shape('TextBox', None, rect, caption=False, parent=parent)
        # TextBox HTML is presentation text; the owning UML model retains its name/body.
        prop(s.dep, 'String', 'plainText', re.sub(r'\*\*', '', text))
        prop(s.dep, 'String', 'htmlText', rich(text, size, align, bold))
        prop(s.dep, 'Integer', 'modelElementNameAlignment', 1)
        ef=s.el.find(_q('ElementFont'));ef.set('size',str(size));ef.set('style','1' if bold else '0')
        return s

    def separator(self, owner, x, y, w):
        # Editable graphics, not a raster image; native UML remains the owner.
        # Degenerate one-pixel rectangles are skipped by the VP renderer.
        self.vector_path(owner,[x,y,w,2],[[0,0],[w-1,0]],'DIV','Cr:160,160,160,255')

    def frame(self, item):
        m = self.p.model('Package', name=item['name'], hint=self.hint('MP'))
        # Native package presented as a rectangle, as in the reference PNG.
        s = self.shape('Rectangle', m, item['rect'], name=item['name'], fill=item['fill'])
        prop(s.dep, 'Integer', 'presentationOption', 3)
        prop(s.dep, 'Integer', 'primitiveShapeType', 1)
        s.el.find(_q('Caption')).set('visible', 'false')
        x, y, w, h = item['rect']
        self.text(item['name'], [x + 4, y + 3, w - 8, 36], 13, 'center', True, s)
        self.models[item['key']] = m
        self.shapes[item['key']] = s

    def node(self, item):
        key, kind, name = item['key'], item['kind'], item['name']
        parent = self.shapes.get(item.get('parent'))
        owner = self.models.get(item.get('parent'))
        model_kind = 'InteractionLifeLine' if kind == 'CommunicationLifeLine' else kind
        m = self.p.model(model_kind, name=name or None, hint=self.hint('MN'),
                         parent=self.p.children(owner) if owner else None)
        body = '\n'.join(item.get('body', []))
        if body:
            ET.SubElement(m.props, _q('HTMLProperty'), {'name': 'documentation',
                          'plainTextValue': body, 'value': rich(body, 12)})
        if body.startswith('entry / '):
            entry=self.p.model('Activity',name=body[8:],hint=self.hint('ENTRY'))
            self.p.ref_prop(m,'entry',entry.id)
        if item.get('stereotype'):
            st = self.p.stereotype(item['stereotype'], base=model_kind)
            refs = ET.SubElement(m.props, _q('ModelRefsProperty'), {'name': 'stereotypes'})
            ET.SubElement(refs, _q('ModelRef'), {'id': st.id})
        x, y, w, h = item['rect']
        fill=BLACK if kind in ['InitialPseudoState','FinalState2'] else item.get('fill',GREY)
        s = self.shape(kind, m, item['rect'], name=name or None, fill=fill, parent=parent)
        self.models[key], self.shapes[key] = m, s
        if kind == 'State2':
            prop(s.dep,'Boolean','0SwIta',False)
            prop(s.dep,'Boolean','1SwItt',False)
            # State body has its own editable compartment and separator, rather than
            # being appended to the state's UML name. Includes composite entry action.
            title_h = 25 if '\n' not in name else 41
            cap = s.el.find(_q('Caption'))
            cap.set('visible', 'false')
            prop(s.dep,'Boolean','requestResetCaption',False)
            self.text(name,[x+3,y+3,w-6,title_h-2],14,'center',parent=s)
            if body or item.get('composite'):
                self.separator(s, x, y + title_h, w)
                if body:
                    self.text(body, [x + 5, y + title_h + 4, w - 10, len(body.split('\n')) * 15 + 10],
                              11, parent=s)
                    if item.get('composite'):
                        self.separator(s, x, y + title_h + 23, w)
            else:
                self.separator(s, x, y + h - 10, w)
        elif kind == 'CommunicationLifeLine':
            # Rectangular object header, stereotype, and attributes as in PNG.
            cap = s.el.find(_q('Caption'))
            cap.set('visible', 'false')
            st = item.get('stereotype')
            header = ('«%s»\n' % st if st else '') + name
            header_h = len(header.split('\n')) * 16 + 5
            self.text(header, [x + 3, y + 2, w - 6, header_h], 13, 'center', parent=s)
            self.separator(s, x, y + header_h, w)
            if body:
                self.text(body, [x + 5, y + header_h + 4, w - 10, h - header_h - 4], 13, parent=s)
        elif kind in ['InteractionLifeLine', 'InteractionActor']:
            cap = s.el.find(_q('Caption'))
            cap.set('height', str(35 if '\n' in name else 27))
            # In the sequence diagram a lifeline's height includes the whole execution.
            if item.get('created'):
                prop(s.dep, 'Integer', 'requestSetSizeOption', 0)
            self.lifeline(item,s)
        return m, s

    def fragment(self, item):
        parent_key=item.get('parent')
        if parent_key:parent_key += '_operand'+str(item.get('parent_operand',0))
        owner = self.models.get(parent_key)
        parent = self.shapes.get(parent_key)
        m = self.p.model('CombinedFragment', name=item['name'], hint=self.hint('MF'),
                         parent=self.p.children(owner) if owner else None)
        # group is represented by a UML critical fragment with the full transaction name.
        op = 'critical' if item['operator'] == 'group' else item['operator']
        prop(m.props, 'String', 'interactionOperator', op)
        s = self.shape('CombinedFragment', m, item['rect'], caption=False, parent=parent)
        self.models[item['key']], self.shapes[item['key']] = m, s
        x, y, w, h = item['rect']
        ys = item['operand_ys']
        for i, guard in enumerate(item['guards']):
            start = ys[i]
            end = ys[i + 1] if i + 1 < len(ys) else y + h
            om = self.p.model('InteractionOperand', name=guard, hint=self.hint('MO'),
                              parent=self.p.children(m))
            prop(om.props, 'String', 'guard', guard)
            os = self.shape('InteractionOperand', om, [x, start, w, end-start], caption=False, parent=s)
            self.text(('[' + guard + ']') if item['operator'] != 'group' else guard,
                      [x + (110 if i == 0 and item['operator'] != 'group' else 6),
                       start + 4, w - 116 if i == 0 else w - 12,
                       max(20, len(guard.split('\n')) * 15)],
                      11 if self.spec['name'].startswith('SEQ_UC2') else 12, bold=True, parent=os)
            self.models[item['key'] + '_operand' + str(i)] = om
            self.shapes[item['key'] + '_operand' + str(i)] = os
        return m, s

    def edge(self, item):
        a, b = item['from'], item['to']
        ma, mb = self.models[a], self.models[b]
        sa, sb = self.shapes[a], self.shapes[b]
        label = item['label']
        kind = item['kind']
        points = [list(point) for point in item.get('points', [])]
        if kind in ['Message','SequenceSelfMessage'] and points:
            points = self.message_points(item, points)
        if kind in ['Message', 'SequenceSelfMessage']:
            mm = self.p.flow('Message', ma, mb, name=label, hint=self.hint('MM'))
            self.ends(mm,ma,mb,'MessageEnd')
            prop(mm.props, 'Boolean', 'asynchronous', item.get('asynchronous', False))
            prop(mm.props, 'Integer', 'type', 2 if item.get('create') else 3 if a == b else 0)
            if points:
                py=points[0][1]
                candidates=[f for f in self.spec.get('fragments',[]) if f['rect'][1]<=py<f['rect'][1]+f['rect'][3]]
                if candidates:
                    fragment=min(candidates,key=lambda f:f['rect'][2]*f['rect'][3])
                    index=max(i for i,start in enumerate(fragment['operand_ys']) if start<=py)
                    self.p.models.remove(mm.el)
                    self.p.children(self.models[fragment['key']+'_operand'+str(index)]).append(mm.el)
            visual = 'SequenceSelfMessage' if a == b else 'Message'
        elif kind == 'InteractionLifeLineLink':
            mm = self.p.flow('InteractionLifeLineLink', ma, mb, name=label, hint=self.hint('ML'))
            self.ends(mm,ma,mb,'InteractionLifeLineLinkEnd')
            # Messages are actual UML Message children, individually numbered.
            # The PNG intentionally groups several messages in one displayed label.
            chunks = re.split(r'(?m)(?=^\d[\d.]*\s*(?:[:→←]|\[))', label)
            for chunk in filter(str.strip, chunks):
                child = self.p.model('Message', name=chunk.strip(), hint=self.hint('MC'), parent=self.p.children(mm))
                reverse=bool(re.match(r'^\d[\d.]*\s*←',chunk.strip()))
                self.ends(child,mb if reverse else ma,ma if reverse else mb,'MessageEnd')
                num = re.match(r'[\d.]+', chunk)
                if num:
                    prop(child.props, 'String', 'sequenceNumber', num.group())
            visual = 'InteractionLifeLineLink'
        else:
            mm = self.p.flow(kind, ma, mb, name=label or None, hint=self.hint('ME'))
            visual = kind
        cap = item.get('caption')
        # Fix previously truncated multiline/self-message captions.
        if cap:
            cap = list(cap)
            cap[2] = max(cap[2], max(len(line) for line in label.split('\n')) * 6.5 + 12)
            cap[3] = max(cap[3], len(label.split('\n')) * 16 + 2)
        cn = self.d.connector(visual, mm, sa, sb, caption_xy=None,
                              caption_wh=[round(t) for t in cap[2:]] if cap else (0, 0),
                              points=[tuple(round(t) for t in p) for p in points] or None,
                              style='Curve' if len(points) > 2 and a != b else 'Oblique', hint=self.hint('C'))
        dep = ET.Element(_q('DiagramElementProperties'))
        cn.insert(0, dep)
        prop(dep, 'Boolean', 'requestRebuild', False)
        prop(dep, 'Boolean', 'requestRebuildFromEnd', False)
        prop(dep, 'Boolean', 'requestRebuildToEnd', False)
        prop(dep, 'Boolean', 'paintThroughLabel', True)
        font(cn)
        ET.SubElement(cn,_q('Caption'),{'visible':'false','side':'None','x':'0','y':'0','width':'0','height':'0'})
        # Caption precedes Points in the schema.
        cap_el=cn[-1];cn.remove(cap_el);cn.insert(2,cap_el)
        if label and cap:
            self.text(label, cap, 12 if self.spec['type']=='InteractionDiagram' else 13,
                      'left' if self.spec['type']=='InteractionDiagram' else 'center')
        elif label:
            if points:
                cx=(points[0][0]+points[-1][0])/2
                cy=(points[0][1]+points[-1][1])/2
                width=max(len(t) for t in label.split('\n'))*7+12
                self.text(label,[cx-width/2,cy-18,width,len(label.split('\n'))*16+4],13,'center')
        if item.get('color'):
            prop(dep,'Color','foreground',item['color'])
            line = ET.Element(_q('Line'), {'cap':'0','color':item['color'], 'weight':'1', 'transparency':'100'})
            if item.get('dashed'):
                stroke = ET.SubElement(line, _q('Stroke'))
                dash = ET.SubElement(stroke, _q('Dashes'))
                for v in [7, 5]:ET.SubElement(dash, _q('Dash'), {'value':str(v)})
            cn.insert(2, line)
        if kind == 'InteractionLifeLineLink' and 'COL_UC32' not in self.spec['name']:
            # The displayed arrow is an editable generic connector; its UML link and
            # individual messages above retain their proper model types.
            gm = self.p.flow('GenericConnector', ma, mb, hint=self.hint('GA'))
            gc = self.d.connector('GenericConnector', gm, sa, sb,
                                  points=[tuple(round(t) for t in p) for p in points],
                                  style='Curve' if len(points)>2 else 'Oblique', hint=self.hint('AC'))
            gp=ET.Element(_q('DiagramElementProperties'));gc.insert(0,gp)
            prop(gp,'String','toHeadname','Arrow1')
            ah=ET.Element(_q('EndArrowHead'));gc.insert(1,ah)
            ap=ET.SubElement(ah,_q('DiagramElementProperties'))
            prop(ap,'String','name','Arrow1');prop(ap,'Integer','size',1)
        if kind in ['Message','SequenceSelfMessage'] and a==b:
            # VP snaps native and generic self-message arrowheads to the lifeline
            # centre, under the white activation. Keep the native Message and
            # supply an editable vector loop ending on the visible bar border.
            tip=points[-1]
            vertices=points+[[tip[0]+5,tip[1]-3],tip,[tip[0]+5,tip[1]+3]]
            left=min(p[0] for p in vertices);top=min(p[1] for p in vertices)
            right=max(p[0] for p in vertices);bottom=max(p[1] for p in vertices)
            self.vector_path(sa,[left,top,right-left+1,bottom-top+1],
                             [[px-left,py-top] for px,py in vertices],'SELF')
        if kind=='Dependency' and item.get('color'):
            # VP ignores custom colors on a native Dependency renderer; retain the
            # dependency model and overlay its editable, colored visual connector.
            gm=self.p.flow('GenericConnector',ma,mb,hint=self.hint('BLUE'))
            gc=self.d.connector('GenericConnector',gm,sa,sb,
                                points=[tuple(round(t) for t in p) for p in points],
                                style='Oblique',hint=self.hint('BC'))
            gp=ET.Element(_q('DiagramElementProperties'));gc.insert(0,gp)
            prop(gp,'Color','foreground',item['color'])
            ah=ET.Element(_q('EndArrowHead'));gc.insert(1,ah)
            ap=ET.SubElement(ah,_q('DiagramElementProperties'))
            prop(ap,'String','name','Arrow1');prop(ap,'Integer','size',1)
            line=ET.Element(_q('Line'),{'cap':'0','color':item['color'],'weight':'1','transparency':'0'})
            stroke=ET.SubElement(line,_q('Stroke'));dash=ET.SubElement(stroke,_q('Dashes'))
            for v in [7,5]:ET.SubElement(dash,_q('Dash'),{'value':str(v)})
            gc.insert(2,line)
        return mm

    def message_points(self, item, points):
        """Attach visible arrows to the edge of the active execution rectangle.

        Ending at the lifeline centre puts the arrowhead underneath the white
        activation fill. The endpoint must be on the bar's facing border.
        """
        def active(owner,y):
            return next((a['rect'] for a in self.spec.get('activations',[])
                         if a['owner']==owner and a['rect'][1]<=y<=a['rect'][1]+a['rect'][3]),None)
        if item['from']==item['to']:
            for index in [0,len(points)-1]:
                rect=active(item['from'],points[index][1])
                if rect:points[index][0]=rect[0]+rect[2]
        else:
            right=points[-1][0]>points[0][0]
            rect=active(item['from'],points[0][1])
            if rect:points[0][0]=rect[0]+rect[2] if right else rect[0]
            rect=active(item['to'],points[-1][1])
            if rect:points[-1][0]=rect[0] if right else rect[0]+rect[2]
        return points

    def ends(self, relation, src, dst, end_kind):
        """End relationships reference relationship ends, not nodes through from/to.

        Without this structure VP draws connectors but silently drops Message and
        InteractionLifeLineLink models on ExportXML. Round-trip verification catches it.
        """
        for e in list(relation.props):
            if e.get('name') in ['from','to']:relation.props.remove(e)
        self.p.ref_prop(relation,'endRelationshipFromMetaModelElement',src.id)
        self.p.ref_prop(relation,'endRelationshipToMetaModelElement',dst.id)
        for i,(tag,node) in enumerate([('FromEnd',src),('ToEnd',dst)]):
            host=ET.Element(_q(tag));relation.el.insert(1+i,host)
            end=self.p.model(end_kind,name='',hint=self.hint('END'),parent=host)
            end.el.set('composite','true')
            self.p.ref_prop(end,'EndModelElement',node.id)

    def note(self, item):
        text = item['text']
        m = self.p.note(re.sub(r'\*\*', '', text), hint=self.hint('NOTE'))
        hp = m.props.find(_q('HTMLProperty'))
        note_size = 10 if self.spec['name'].startswith(('COL_UC1', 'SEQ_UC2')) else 12
        hp.set('value', rich(text, note_size))
        legend = item['kind'] == 'legend'
        s = self.shape('NOTE', m, item['rect'], caption=False,
                       fill='Cr:221,221,221,255' if legend else 'Cr:254,255,221,255')
        s.el.find(_q('ElementFont')).set('size',str(note_size))
        if legend:
            # Legends have rounded rectangular borders in the reference.
            prop(s.dep, 'Integer', 'presentationOption', 3)
            prop(s.dep, 'Integer', 'primitiveShapeType', 2)
        if item.get('anchor'):
            target=item['anchor'];am=self.p.flow('Anchor',m,self.models[target],hint=self.hint('AN'))
            self.d.connector('Anchor',am,s,self.shapes[target],style='Oblique',hint=self.hint('NA'))
        return s

    def build(self):
        for item in self.spec['frames']:self.frame(item)
        # Outer composite states precede their contained states.
        for item in self.spec['nodes']:self.node(item)
        for item in self.spec.get('fragments', []):self.fragment(item)
        for item in self.spec.get('activations', []):
            owner=item['owner'];m=self.p.model('Activation',hint=self.hint('MA'),parent=self.p.children(self.models[owner]))
            # Rectangle presentation keeps the specified activation extent while
            # disabling VP's implicit full-length activation on each lifeline.
            activation=self.shape('Rectangle',m,item['rect'],caption=False,fill='Cr:255,255,255,255',parent=self.shapes[owner])
            for shape in activation.el.iter(_q('Shape')):
                prop(shape.find(_q('DiagramElementProperties')),'Boolean','activationGraphic',True)
        for item in self.spec['edges']:self.edge(item)
        for item in self.spec['notes']:self.note(item)
        if 'tail_y' in self.spec:
            for item in self.spec['nodes']:
                x,y,w,h=item['rect'];name=item['name'];tail_y=self.spec['tail_y']
                if item['kind']=='InteractionActor':
                    m=self.p.model('Actor',name=name,hint=self.hint('AT'))
                    self.shape('Actor',m,[x,tail_y,w,100],name=name,fill=GREY)
                else:
                    self.shape('Rectangle',self.models[item['key']],[x,tail_y,w,50 if '\n' in name else 31],
                               name=name,fill=GREY)
        self.text(self.spec['title'],[5,10,self.spec['canvas'][0]-10,40],14,'center',True)
        # Larger zorder is farther back in VP. Notes must cover lifelines and
        # activations even when a note has a larger area than a narrow bar.
        all_shapes=list(self.d.el.iter(_q('Shape')))
        def paint_order(shape):
            kind=shape.get('shapeType')
            dep=shape.find(_q('DiagramElementProperties'))
            flags={p.get('name') for p in dep if p.get('value')=='true'}
            front=4 if kind=='TextBox' else 3 if kind=='NOTE' else 2 if 'activationGraphic' in flags else 1 if 'lifelineGraphic' in flags else 0
            return (front,-int(shape.get('width'))*int(shape.get('height')))
        ordered=sorted(all_shapes,key=paint_order)
        for i,s in enumerate(ordered):s.set('zorder',str(len(ordered)-i))
        # Every connector needs at least one child to satisfy project.xsd.
        for cn in self.d.connectors:
            if not len(cn):
                dep=ET.SubElement(cn,_q('DiagramElementProperties'))
                prop(dep,'Boolean','requestRebuild',False)
                font(cn)
                ET.SubElement(cn,_q('Caption'),{'visible':'false','side':'None','x':'0','y':'0','width':'0','height':'0'})
                src=self.d.el.find(".//"+_q('Shape')+"[@id='"+cn.get('from')+"']")
                dst=self.d.el.find(".//"+_q('Shape')+"[@id='"+cn.get('to')+"']")
                pts=ET.SubElement(cn,_q('Points'))
                for sh in [src,dst]:
                    ET.SubElement(pts,_q('Point'),{'x':str(int(sh.get('x'))+int(sh.get('width'))//2),'y':str(int(sh.get('y'))+int(sh.get('height'))//2)})
        # Empty ModelProperties are not allowed by the native project schema.
        for mp in self.p.root.iter(_q('ModelProperties')):
            if not len(mp):prop(mp,'String','name','')
        return self.p


def build(spec):
    nd=NativeDiagram(spec)
    wrappers=[]
    original=nd.shape
    def remember(*args,**kwargs):
        s=original(*args,**kwargs);wrappers.append(s);return s
    nd.shape=remember
    p=nd.build()
    for s in wrappers:nd.d.finish_fill(s)
    return p


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('names',nargs='*')
    args=parser.parse_args()
    files=[SPECS/(n+'.json') for n in args.names] if args.names else sorted(SPECS.glob('*.json'))
    combined=Project('SAD_Selected_9')
    for path in files:
        spec=json.loads(path.read_text(encoding='utf-8'))
        p=build(spec)
        target=OUT/(spec['name']+'.xml')
        ET.indent(p.root,space='  ')
        p.write(str(target))
        combined.models.extend(list(p.models));combined.diagrams.extend(list(p.diagrams))
        print(target.relative_to(HERE))
    if not args.names:
        ET.indent(combined.root,space='  ')
        combined.write(str(OUT/'SAD_Selected_9.xml'))


if __name__=='__main__':main()
