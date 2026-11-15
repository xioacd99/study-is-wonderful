#!/usr/bin/env python3
"""Generate the bilingual course map from the synchronized README pair."""
import re,json,pathlib,argparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
def courses(text):
    result=[]; section=''; group=''
    for line in text.splitlines():
        if line.startswith('## '): section=line[3:]
        if line.startswith('### '): group=line[4:]
        m=re.search(r'<a id="(course-[^"]+)"></a>',line)
        if not m: continue
        cells=line.strip().strip('|').split(' | ')
        if len(cells)!=3: raise ValueError('Expected three course cells: '+m[1])
        links=re.findall(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',cells[0]+' '+cells[2])
        if not links: raise ValueError(m[1])
        title=links[0][0].replace('<br>', ' / ')
        unique=[];seen=set()
        for label,url in links:
            if url not in seen: unique.append(dict(label=label.replace('<br>',' / '),url=url));seen.add(url)
        result.append(dict(id=m[1],subject=section,group=group,title=title,links=unique,description=cells[1].replace('<br>','\n')))
    if len({x['id'] for x in result})!=len(result) or not result: raise ValueError('Missing or duplicate course anchors')
    return result
def bilingual_courses(chinese, english):
    zh=courses(chinese);en=courses(english)
    if [c['id'] for c in zh]!=[c['id'] for c in en]:
        raise ValueError('README language versions differ in course coverage or order')
    result=[]
    def join(a,b,separator=' / '): return a if a==b else a+separator+b
    for a,b in zip(zh,en):
        if [x['url'] for x in a['links']]!=[x['url'] for x in b['links']]:
            raise ValueError('README source URLs differ for '+a['id'])
        result.append(dict(id=a['id'],subject=join(a['subject'],b['subject']),
            group=join(a['group'],b['group']),title=join(a['title'],b['title']),
            links=[dict(label=join(x['label'],y['label']),url=x['url']) for x,y in zip(a['links'],b['links'])],
            description=join(a['description'],b['description'],'\n')))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    data=bilingual_courses((ROOT/'README.md').read_text(), (ROOT/'README-en.md').read_text())
    out=(ROOT/'resource-map/template.html').read_text().replace('/*__COURSES__*/',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
    target=ROOT/'resource-map/index.html'
    if args.check:
        assert target.read_text()==out,'Run python tools/build_resource_map.py to synchronize the map'
    else: target.write_text(out)
    print(f'Validated {len(data)} courses in {len(set(x["subject"] for x in data))} subjects')
