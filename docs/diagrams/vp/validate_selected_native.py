#!/usr/bin/env python3
"""Validate native XML references, completeness, and actual VP round-trip retention."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
NS='{http://www.visual-paradigm.com/product/vpuml/modelexporter}'


def validate(path, specs):
    root=ET.parse(path).getroot()
    elements=[e for e in root.iter() if e.tag in [NS+'Model',NS+'Shape',NS+'Connector',NS+'Diagram']]
    ids=[e.get('id') for e in elements]
    assert len(ids)==len(set(ids)), 'Duplicate model/diagram IDs'
    assert all(re.fullmatch(r'[A-Za-z0-9_.]{16}',i) for i in ids), 'Invalid VP ID'
    models={e.get('id'):e for e in root.iter(NS+'Model')}
    for ref in root.iter(NS+'ModelRef'):
        assert ref.get('id') in models, 'Dangling model reference '+str(ref.attrib)
    for d in root.iter(NS+'Diagram'):
        shapes={s.get('id') for s in d.iter(NS+'Shape')}
        for co in d.iter(NS+'Connector'):
            assert co.get('model') in models
            assert co.get('from') in shapes and co.get('to') in shapes
        # A stored Line.color is insufficient in VP's Rectangle renderer. Every
        # substantial rectangle must also contain an opaque black vector contour.
        for sh in d.iter(NS+'Shape'):
            if sh.get('shapeType')!='Rectangle':continue
            x,y,w,h=(int(sh.get(k)) for k in ['x','y','width','height'])
            if min(w,h)<=2:continue
            line=sh.find(NS+'Line')
            assert line is not None and line.get('transparency')=='0',(d.get('name'),'transparent rectangle outline')
            edges=sh.find(NS+'ChildShapes')
            found=False
            if edges is not None:
                for edge in edges:
                    if edge.get('shapeType')!='Freehand':continue
                    stroke=edge.find(NS+'Line')
                    fill=edge.find(NS+'FillColor')
                    points=edge.find(NS+'FreehandPoints')
                    if stroke is None or stroke.get('color')!='Cr:0,0,0,255' or stroke.get('transparency')!='0' or points is None:continue
                    if fill is None or fill.get('color')!='Cr:0,0,0,255' or fill.get('transparency')!='0':continue
                    actual=[p.find(NS+'DiagramElementProperties/'+NS+'PointProperty').get('value') for p in points]
                    expected=['Pt:%.1f,%.1f'%p for p in [(0,0),(w-1,0),(w-1,h-1),(0,h-1),(0,0)]]
                    found=actual==expected
                    if found:break
            assert found,(d.get('name'),sh.get('id'),'missing rectangle contour')
    types=Counter(m.get('modelType') for m in models.values())
    strings={v for e in root.iter() for k,v in e.attrib.items() if k in ['name','value','plainTextValue']}
    for spec in specs:
        if spec['name']=='COL_UC2_LogicalView':
            nodes={n['key']:n for n in spec['nodes']}
            for edge in spec['edges']:
                x,y,w,h=nodes[edge['to']]['rect'];ex,ey=edge['points'][-1]
                distance=max(x-ex,ex-x-w,y-ey,ey-y-h,0)
                assert distance<=6,(spec['name'],edge['label'],'route ends outside its target',edge['to'])
        for node in spec['nodes']:
            if node['name']:assert node['name'] in strings,(spec['name'],'Missing node',node['name'])
            body='\n'.join(node.get('body',[]))
            if body:assert body in strings,(spec['name'],'Missing compartment',body)
        for edge in spec['edges']:
            if edge['label']:assert edge['label'] in strings,(spec['name'],'Missing message/transition',edge['label'])
        for note in spec['notes']:
            assert note['text'].replace('**','') in strings,(spec['name'],'Missing note')
        for f in spec.get('fragments',[]):
            assert f['name'] in strings
            for guard in f['guards']:assert guard in strings
    return root,models,types


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--roundtrip',type=Path,help='project.xml exported by Visual Paradigm')
    parser.add_argument('--schema',type=Path,help='Visual Paradigm bundled/project.xsd')
    args=parser.parse_args()
    specs=[json.loads(p.read_text()) for p in sorted((HERE/'specs').glob('*.json'))]
    for s in specs:
        path=HERE/'out'/(s['name']+'.xml')
        validate(path,[s])
        if args.schema:subprocess.run(['xmllint','--noout','--schema',str(args.schema),str(path)],check=True)
    combined=HERE/'out/SAD_Selected_9.xml'
    root,models,counts=validate(combined,specs)
    assert len(list(root.iter(NS+'Diagram')))==9
    if args.schema:subprocess.run(['xmllint','--noout','--schema',str(args.schema),str(combined)],check=True)
    print('9 diagrams: XML references and every declared name, body, message, guard, and note OK')
    print('Native models:',', '.join('%s=%d'%(t,counts[t]) for t in ['State2','Choice','Transition2','InteractionLifeLine','InteractionActor','Message','InteractionLifeLineLink','CombinedFragment','InteractionOperand','Activation','NOTE']))
    if args.roundtrip:
        exported=ET.parse(args.roundtrip).getroot()
        exported_models={m.get('id'):m for m in exported.iter(NS+'Model')}
        exported_shapes={s.get('id') for s in exported.iter(NS+'Shape')}
        missing=[(i,m.get('modelType'),m.get('name')) for i,m in models.items() if i not in exported_models and m.get('modelType')!='Stereotype']
        assert not missing,'VP discarded models: '+str(missing)
        missing_shapes=[s.get('id') for s in root.iter(NS+'Shape') if s.get('id') not in exported_shapes]
        assert not missing_shapes,'VP discarded shapes: '+str(missing_shapes)
        for i,m in models.items():
            if m.get('modelType') in ['Message','InteractionLifeLineLink']:
                actual=exported_models[i]
                for end in ['FromEnd','ToEnd']:
                    ref=actual.find('.//'+NS+end+'//'+NS+'ModelRefProperty[@name="EndModelElement"]/'+NS+'ModelRef')
                    assert ref is not None and ref.get('id') in exported_models,(i,end,'lost endpoint')
        print('VP round-trip: every native model and shape retained; every message/link endpoint retained')


if __name__=='__main__':main()
