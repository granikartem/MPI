#!/usr/bin/env python3
"""Check VP-rendered SVG for borders, return arrows, lifelines, and COL routes.

This inspects the actual exported drawing, not just the input XML. Usage:
  python3 verify_selected_render.py --svg-dir .build/checked_svg
"""
import argparse
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
IDENTITY=(1,0,0,1,0,0)


def multiply(a,b):
    return (a[0]*b[0]+a[2]*b[1],a[1]*b[0]+a[3]*b[1],
            a[0]*b[2]+a[2]*b[3],a[1]*b[2]+a[3]*b[3],
            a[0]*b[4]+a[2]*b[5]+a[4],a[1]*b[4]+a[3]*b[5]+a[5])


def transform(text):
    matrix=IDENTITY
    for name,args in re.findall(r'(\w+)\(([^)]*)\)',text):
        values=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?',args)]
        if name=='translate':other=(1,0,0,1,values[0],values[1] if len(values)>1 else 0)
        elif name=='scale':other=(values[0],0,0,values[-1],0,0)
        elif name=='matrix':other=tuple(values)
        elif name=='rotate':
            angle=math.radians(values[0]);c=math.cos(angle);s=math.sin(angle)
            other=(c,s,-s,c,0,0)
            if len(values)==3:
                other=multiply(multiply((1,0,0,1,values[1],values[2]),other),(1,0,0,1,-values[1],-values[2]))
        else:raise ValueError('Unsupported SVG transform: '+name)
        matrix=multiply(matrix,other)
    return matrix


def point(matrix,p):
    return (matrix[0]*p[0]+matrix[2]*p[1]+matrix[4],matrix[1]*p[0]+matrix[3]*p[1]+matrix[5])


def dark(color):
    if color in ['black','#000000','#333333']:return True
    values=re.findall(r'\d+',color)
    return color.startswith('rgb(') and max(map(int,values))<80


def drawing(path):
    """Return visible black straight segments and closed rectangle outlines."""
    segments=[];rectangles=[]
    def visit(el,matrix,style):
        tag=el.tag.rsplit('}',1)[-1]
        if tag in ['defs','clipPath']:return
        matrix=multiply(matrix,transform(el.get('transform','')))
        style={**style,**{k:v for k,v in el.attrib.items() if k in ['stroke','stroke-opacity','opacity']}}
        visible=dark(style.get('stroke','none')) and float(style.get('stroke-opacity','1'))>0 and float(style.get('opacity','1'))>0
        vertices=[];closed=False
        if visible and tag=='line':
            vertices=[(float(el.get('x1')),float(el.get('y1'))),(float(el.get('x2')),float(el.get('y2')))]
        elif visible and tag=='rect':
            x,y,w,h=(float(el.get(k,'0')) for k in ['x','y','width','height'])
            vertices=[(x,y),(x+w,y),(x+w,y+h),(x,y+h)];closed=True
        elif visible and tag=='path' and re.fullmatch(r'[MLZmlz\d.eE ,+-]+',el.get('d','')):
            # Curved glyph outlines and text paths are intentionally excluded.
            d=el.get('d','');closed=d.upper().endswith('Z')
            numbers=[float(x) for x in re.findall(r'-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?',d)]
            vertices=list(zip(numbers[::2],numbers[1::2]))
        if vertices:
            vertices=[point(matrix,p) for p in vertices]
            segments.extend(zip(vertices,vertices[1:]))
            if closed:
                segments.append((vertices[-1],vertices[0]))
                if len(vertices) in [4,5]:
                    xs=[p[0] for p in vertices];ys=[p[1] for p in vertices]
                    if all(abs(a[0]-b[0])<0.1 or abs(a[1]-b[1])<0.1 for a,b in zip(vertices,vertices[1:]+vertices[:1])):
                        rectangles.append((min(xs),min(ys),max(xs)-min(xs),max(ys)-min(ys)))
        for child in el:visit(child,matrix,style)
    visit(ET.parse(path).getroot(),IDENTITY,{})
    return segments,rectangles


def near(a,b,tolerance=1.6):return math.dist(a,b)<=tolerance


def edge_drawn(segments,start,end):
    return any((near(a,start) and near(b,end)) or (near(a,end) and near(b,start)) for a,b in segments)


def outline(segments,rect,offset):
    x,y,w,h=rect;x+=offset[0];y+=offset[1]
    vertices=[(x,y),(x+w-1,y),(x+w-1,y+h-1),(x,y+h-1)]
    return all(edge_drawn(segments,a,b) for a,b in zip(vertices,vertices[1:]+vertices[:1]))


def verify_rectangles(name,path):
    ns='{http://www.visual-paradigm.com/product/vpuml/modelexporter}'
    root=ET.parse(HERE/'out'/(name+'.xml')).getroot()
    rectangles=[tuple(int(s.get(k)) for k in ['x','y','width','height'])
                for s in root.iter(ns+'Shape') if s.get('shapeType')=='Rectangle'
                and min(int(s.get('width')),int(s.get('height')))>2]
    if not rectangles:return 0,(0,0)
    segments,_=drawing(path)
    x,y,w,h=rectangles[0];offsets=[]
    for a,b in segments:
        # VP insets Freehand contours by one pixel when fitting their bounds.
        if abs(a[1]-b[1])<0.1 and abs(abs(b[0]-a[0])-(w-1))<=1:
            offset=(min(a[0],b[0])-x,a[1]-y)
            if abs(offset[0])<20 and abs(offset[1])<30 and outline(segments,rectangles[0],offset):
                offsets.append(offset)
    assert offsets,(name,'no visible rectangle contour')
    offset=min(offsets,key=lambda p:abs(p[0])+abs(p[1]))
    for rect in rectangles:
        assert outline(segments,rect,offset),(name,'rectangle border is incomplete',rect)
    return len(rectangles),offset


def verify_col_routes(spec,path,offset):
    """Every incoming message must have a visible arrowhead at its target box."""
    segments,_=drawing(path)
    short=[(a,b) for a,b in segments if 3<math.dist(a,b)<10]
    tips=[]
    for i,(a,b) in enumerate(short):
        for c,d in short[i+1:]:
            for tip,wing in [(a,b),(b,a)]:
                for other,second in [(c,d),(d,c)]:
                    if not near(tip,other,0.1):continue
                    u=(wing[0]-tip[0],wing[1]-tip[1])
                    v=(second[0]-tip[0],second[1]-tip[1])
                    cosine=(u[0]*v[0]+u[1]*v[1])/(math.hypot(*u)*math.hypot(*v))
                    # Two arrow wings meet at a sharp angle; adjacent segments
                    # of the VP curve approximation are nearly collinear.
                    if abs(cosine)<0.65 and not any(near(tip,p,0.5) for p in tips):
                        tips.append(tip)
    for node in spec['nodes']:
        x,y,w,h=node['rect'];x+=offset[0];y+=offset[1]
        expected=sum(edge['to']==node['key'] for edge in spec['edges'])
        hits=[p for p in tips if max(x-p[0],p[0]-x-w,y-p[1],p[1]-y-h,0)<=4]
        assert len(hits)==expected,(spec['name'],node['key'],'arrowheads land at the wrong block',expected,hits)
    return len(spec['edges'])


def dashed_lifelines(path):
    """Read actual SVG strokes, excluding invisible native lifeline fragments."""
    lines=[]
    def visit(el,matrix,style):
        tag=el.tag.rsplit('}',1)[-1]
        if tag in ['defs','clipPath']:return
        matrix=multiply(matrix,transform(el.get('transform','')))
        style={**style,**{k:v for k,v in el.attrib.items()
                        if k in ['stroke','stroke-dasharray','stroke-opacity','opacity']}}
        dash=style.get('stroke-dasharray','none')
        visible=style.get('stroke','none')!='none' and float(style.get('stroke-opacity','1'))>0 and float(style.get('opacity','1'))>0
        if tag=='line' and visible and dash!='none':
            a=point(matrix,(float(el.get('x1')),float(el.get('y1'))))
            b=point(matrix,(float(el.get('x2')),float(el.get('y2'))))
            if abs(a[0]-b[0])<0.1 and abs(a[1]-b[1])>20:
                lines.append((a,b,dash))
        for child in el:visit(child,matrix,style)
    visit(ET.parse(path).getroot(),IDENTITY,{})
    return lines


def verify_lifelines(spec,path):
    lines=dashed_lifelines(path);expected=[]
    for node in spec['nodes']:
        x,y,w,h=node['rect']
        start=y+65+len(node['name'].split('\n'))*16+6 if node['kind']=='InteractionActor' else y+36
        expected.append((node['key'],(x+w//2,start),(x+w//2,spec['tail_y'])))
    assert len(lines)==len(expected),(spec['name'],'missing or overlapping dashed time axes',len(lines),len(expected))
    _,start,end=expected[0]
    candidates=[(a[0]-start[0],a[1]-start[1]) for a,b,dash in lines
                if abs((b[1]-a[1])-(end[1]-start[1]))<=2
                and abs(a[0]-start[0])<20 and abs(a[1]-start[1])<30]
    assert candidates,(spec['name'],'first lifeline is interrupted')
    offset=min(candidates,key=lambda p:abs(p[0])+abs(p[1]))
    for key,start,end in expected:
        start=(start[0]+offset[0],start[1]+offset[1])
        end=(end[0]+offset[0],end[1]+offset[1])
        hits=[(a,b,dash) for a,b,dash in lines if near(a,start) and near(b,end)]
        assert len(hits)==1,(spec['name'],key,'lifeline does not span the full time axis',start,end)
        assert hits[0][2]=='4,4',(spec['name'],key,'lifeline is not consistently dashed')
    # A native actor bar has two long solid borders at +/-4 pixels. None should
    # remain after replacing it by an ordinary actor header and dotted time axis.
    solid,_=drawing(path)
    for node in spec['nodes']:
        if node['kind']!='InteractionActor':continue
        x,y,w,h=node['rect'];centre=x+w//2+offset[0]
        borders=[(a,b) for a,b in solid if abs(a[0]-b[0])<0.1
                 and abs(abs(a[0]-centre)-4)<1 and abs(a[1]-b[1])>h/2]
        assert not borders,(spec['name'],node['key'],'solid actor execution rectangle remains')
    return len(expected)


def verify(spec,path):
    segments,rectangles=drawing(path)
    offset=None
    # Match the actual top stroke of the execution bar, allowing the renderer's
    # one-pixel inset and export cropping. No bitmap thresholding or watermarks.
    for activation in spec.get('activations',[]):
        x,y,w,h=activation['rect']
        hits=[]
        for a,b in segments:
            if abs(a[1]-b[1])<0.1 and abs(abs(b[0]-a[0])-(w-1))<=1:
                start=(min(a[0],b[0]),a[1])
                candidate=(start[0]-x,start[1]-y)
                if abs(candidate[0])<15 and abs(candidate[1])<30 and outline(segments,activation['rect'],candidate):
                    hits.append(candidate)
        assert hits,(spec['name'],activation['owner'],'activation outline is not painted black')
        current=min(hits,key=lambda r:abs(r[0])+abs(r[1]))
        if offset is None:offset=current
        assert near(offset,current),(spec['name'],'inconsistent render position',offset,current)
    if offset is None:return 0,0
    loops=0
    for edge in spec['edges']:
        if edge['from']!=edge['to']:continue
        points=[list(p) for p in edge['points']]
        for index in [0,len(points)-1]:
            active=next((a['rect'] for a in spec['activations'] if a['owner']==edge['from'] and a['rect'][1]<=points[index][1]<=a['rect'][1]+a['rect'][3]),None)
            if active:points[index][0]=active[0]+active[2]
        points=[(p[0]+offset[0],p[1]+offset[1]) for p in points]
        for start,end in zip(points,points[1:]):
            assert edge_drawn(segments,start,end), (edge['label'],'return loop segment is not drawn',start,end)
        tip=points[-1]
        wings=[]
        for a,b in segments:
            other=b if near(a,tip) else a if near(b,tip) else None
            if other and other[0]>tip[0]+1.5 and 0.5<abs(other[1]-tip[1])<12:
                wings.append(other[1]-tip[1])
        assert any(y>0 for y in wings) and any(y<0 for y in wings),(edge['label'],'left-pointing return arrowhead is missing')
        loops+=1
    for frame in spec['frames']:
        assert outline(segments,frame['rect'],offset),(spec['name'],frame['name'],'frame outline is not drawn')
    return len(spec.get('activations',[])),loops


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--svg-dir',type=Path,required=True)
    args=parser.parse_args()
    count=loops=rectangles=lifelines=0
    for p in sorted((HERE/'specs').glob('*.json')):
        spec=json.loads(p.read_text())
        path=args.svg_dir/(spec['name']+'.svg')
        assert path.is_file(),('Missing rendered diagram',spec['name'])
        r,offset=verify_rectangles(spec['name'],path);rectangles+=r
        if r:print('%s: %d complete black rectangle outlines'%(spec['name'],r))
        if spec['name']=='COL_UC2_LogicalView':
            arrows=verify_col_routes(spec,path,offset)
            print('%s: %d arrowheads at the intended target blocks'%(spec['name'],arrows))
        if spec['type']=='InteractionDiagram':
            l=verify_lifelines(spec,path);lifelines+=l
            print('%s: %d full dashed lifelines; no solid actor bars'%(spec['name'],l))
        if not spec.get('activations'):continue
        a,l=verify(spec,path)
        count+=a;loops+=l
        print('%s: %d black activation outlines, %d full return arrows visible'%(spec['name'],a,l))
    assert count==8 and loops==8 and rectangles==42 and lifelines==21,(count,loops,rectangles,lifelines)


if __name__=='__main__':main()
