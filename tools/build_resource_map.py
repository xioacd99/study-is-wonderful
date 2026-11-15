#!/usr/bin/env python3
"""Generate the bilingual map from course-title links and additional sources.

Course titles are the primary source links; no duplicate Course/back links needed.
"""
import re,json,pathlib,argparse
ROOT=pathlib.Path(__file__).resolve().parents[1]
def courses(text):
    result=[]; section=''; group='';current=None
    for line in text.splitlines():
        if line.startswith('## '): section=line[3:];current=None
        if line.startswith('### '): group=line[4:];current=None
        m=re.match(r'- <a id="(course-[^"]+)"></a>',line)
        if m:
            links=re.findall(r'\[([^\]]+)\]\((https?://[^\s)]+)\)',line)
            if not links: raise ValueError('Missing source for '+m[1])
            unique=[];seen=set()
            for label,url in links:
                if url not in seen:
                    unique.append(dict(label=label,url=url));seen.add(url)
            current=dict(id=m[1],subject=section,group=group,title=links[0][0],links=unique,description='')
            result.append(current)
        elif current and line.startswith('  > '):
            current['description']+=('\n' if current['description'] else '')+line[4:]
        elif line.startswith('- '):current=None
    if len({x['id'] for x in result})!=len(result) or not result:
        raise ValueError('Missing or duplicate course anchors')
    if any(not c['description'] for c in result): raise ValueError('Missing course description')
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
            description=join(a['description'],b['description'],'\n'),
            locales={'zh':{k:v for k,v in a.items() if k!='id'},
                     'en':{k:v for k,v in b.items() if k!='id'}}))
    return result

def refresh_header(text, language):
    """Keep source wall and small catalog counts derived from actual content."""
    body=text[text.index('<a id="数学-math">'):]
    records=courses(text);sources=[];seen=set()
    for src,alt in re.findall(r'<img src="([^"]+)" alt="([^"]+)"',body):
        if src in seen: continue
        seen.add(src);sources.append((src,alt.replace(' course website','').replace(' repost','')))
    label='资源来源 · 非赞助或背书' if language=='zh' else 'Resource sources · not sponsorships or endorsements'
    wall='<p align="center"><sub>'+label+'</sub><br>\n'+'\n'.join(f'<img src="{src}" alt="{alt}" title="{alt}" height="24"> &nbsp;' for src,alt in sources)+'\n</p>'
    text=re.sub(r'<!-- SOURCES:START -->.*?<!-- SOURCES:END -->','<!-- SOURCES:START -->\n'+wall+'\n<!-- SOURCES:END -->',text,flags=re.S)
    counts=[(len(records),'门课程' if language=='zh' else 'courses'),(len(set(c['subject'] for c in records)),'个学科' if language=='zh' else 'subjects'),(len(re.findall(r'^- \[',body,flags=re.M)),'篇技术文章' if language=='zh' else 'articles')]
    for count,label in counts:text=re.sub(r'\[\d+ '+label+r'\]',f'[{count} {label}]',text)
    return text

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,lang in [('README.md','zh'),('README-en.md','en')]:
        path=ROOT/name;text=path.read_text();updated=refresh_header(text,lang)
        if args.check: assert text==updated,'Synchronize header: '+name
        else: path.write_text(updated)
    data=bilingual_courses((ROOT/'README.md').read_text(), (ROOT/'README-en.md').read_text())
    out=(ROOT/'resource-map/template.html').read_text().replace('/*__COURSES__*/',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
    target=ROOT/'resource-map/index.html'
    if args.check:
        assert target.read_text()==out,'Run python tools/build_resource_map.py to synchronize the map'
    else: target.write_text(out)
    print(f'Validated {len(data)} courses in {len(set(x["subject"] for x in data))} subjects')
