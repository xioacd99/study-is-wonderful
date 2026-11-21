#!/usr/bin/env python3
"""Generate the bilingual map from course-title links and additional sources.

Course titles are the primary source links; no duplicate Course/back links needed.
"""
import re,json,pathlib,argparse,base64,html,math,hashlib
from urllib.parse import urlsplit
ROOT=pathlib.Path(__file__).resolve().parents[1]
def host_source_names():
    manifest=json.loads((ROOT/'icons/sources.json').read_text())
    mapping={}
    for r in manifest['sources']:
        for host in r.get('hosts',[]):
            mapping[host]=r['name']
    return mapping

def courses(text):
    host_names=host_source_names()
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
                    host=urlsplit(url).hostname or ''
                    unique.append(dict(label=label,url=url,source=host_names.get(host,host)));seen.add(url)
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
            links=[dict(label=join(x['label'],y['label']),url=x['url'],source=x['source']) for x,y in zip(a['links'],b['links'])],
            description=join(a['description'],b['description'],'\n'),
            locales={'zh':{k:v for k,v in a.items() if k!='id'},
                     'en':{k:v for k,v in b.items() if k!='id'}}))
    return result

BODY_START='<a id="数学-math">'
RESOURCE_HEADING=re.compile(r'^- (?:<a id="course-[^"]+"></a>\s*)?\[')
RESOURCE_LINK=re.compile(r'\[([^\]]+)\]\((https?://[^\s)]+)\)')

def resource_sources(text):
    """Classify every catalog link; require explicit review of new source hosts."""
    body=text[text.index(BODY_START):]
    manifest=json.loads((ROOT/'icons/sources.json').read_text())
    by_id={r['id']:r for r in manifest['sources']}
    by_path={r['path']:r['id'] for r in manifest['sources'] if 'path' in r}
    by_host={}
    for r in manifest['sources']:
        for host in r.get('hosts',[]):
            if host in by_host: raise ValueError('Duplicate source host in manifest: '+host)
            by_host[host]=r['id']
    credits={}
    for r in manifest['sources']:
        for credit in r.get('course_credits',[]):
            if urlsplit(credit['evidence']).scheme!='https':
                raise ValueError('Missing reference for course attribution: '+credit['course'])
            credits.setdefault(credit['course'],[]).append((r['id'],credit['resource_url']))
    unregistered=set()
    present=set()
    for line in body.splitlines():
        if not RESOURCE_HEADING.match(line): continue
        line_sources=set()
        urls=[url for _,url in RESOURCE_LINK.findall(line)]
        anchor=re.match(r'^- <a id="(course-[^"]+)"></a>',line)
        if anchor:
            for sid,credited_url in credits.get(anchor[1],[]):
                if credited_url not in urls:
                    raise ValueError('Review source attribution after link change: '+anchor[1])
                line_sources.add(sid)
        for url in urls:
            link=urlsplit(url)
            if link.hostname not in by_host:
                unregistered.add(url)
                continue
            line_sources.add(by_host[link.hostname])
            for r in manifest['sources']:
                if any(link.hostname==p['host'] and link.path.startswith(p['prefix']) for p in r.get('credited_paths',[])):
                    line_sources.add(r['id'])
        icons=set(re.findall(r'<img src="([^"]+)"',line))
        unknown=icons-by_path.keys()
        if unknown: raise ValueError('Register new source icons in icons/sources.json: '+', '.join(sorted(unknown)))
        bad={by_path[path] for path in icons}-line_sources
        if bad and not unregistered:
            raise ValueError('Source icon has no matching link on its resource row: '+', '.join(sorted(bad))+' in '+line)
        present.update(line_sources)
    if unregistered: raise ValueError('Classify new catalog source URLs in icons/sources.json: '+', '.join(sorted(unregistered)))
    return manifest,[by_id[sid] for sid in present]

def source_records(text):
    """Derive sources from resource links, not whether a logo is available."""
    manifest,records=resource_sources(text)
    organization_names=manifest['organization_names']
    return sorted(records,key=lambda r:(organization_names[r['organization']].casefold(),r['name'].casefold(),r['id']))

# Order intentionally puts colleges and universities first in both languages.
SOURCE_CARDS = {
    'university': {
        'file': 'source-wall-universities.svg',
        'zh': '大学',
        'en': 'Universities',
        'palette': ('#f2f7ff', '#c7d6ee', '#426b9e', '#334965'),
    },
    'project': {
        'file': 'source-wall-projects.svg',
        'zh': '项目与平台',
        'en': 'Projects & Platforms',
        'palette': ('#f4f2fb', '#d9cdeb', '#7d5ba4', '#4f3b64'),
    },
    'company': {
        'file': 'source-wall-companies.svg',
        'zh': '公司',
        'en': 'Companies',
        'palette': ('#f2f8f6', '#c4ded5', '#377c6b', '#2c5148'),
    },
}

def source_card_records(text):
    """Require each source to declare its card explicitly, including unused entries."""
    manifest=json.loads((ROOT/'icons/sources.json').read_text())
    bad=[r['id'] for r in manifest['sources'] if r.get('group') not in SOURCE_CARDS]
    if bad:
        raise ValueError('Assign source-wall groups in icons/sources.json: '+', '.join(sorted(bad)))
    cards={key:[] for key in SOURCE_CARDS}
    for r in source_records(text):
        cards[r['group']].append(r)
    return cards

def source_wall(records, group):
    """Render one self-contained six-column card without altering source artwork."""
    card=SOURCE_CARDS[group]
    background,border,accent,label_color=card['palette']
    cols=json.loads((ROOT/'icons/sources.json').read_text())['columns']
    cell_w,cell_h=116,72
    pad_x,pad_y=12,12
    width=cols*cell_w+2*pad_x
    height=math.ceil(len(records)/cols)*cell_h+2*pad_y
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">',
         '<title>'+html.escape(card['en'])+'</title>',
         '<desc>'+html.escape(', '.join(r['name'] for r in records))+'. Not sponsorships or endorsements.</desc>',
         f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="16" fill="{background}" stroke="{border}"/>',
         f'<rect x="{width/2-20:g}" y="7" width="40" height="2" rx="1" fill="{accent}"/>']
    mime={'.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp','.avif':'image/avif','.jpg':'image/jpeg'}
    for n,r in enumerate(records):
        x=pad_x+(n%cols)*cell_w;y=pad_y+(n//cols)*cell_h
        name=html.escape(r['name'])
        out.append(f'<g data-source="{r["id"]}"><title>{name}</title>')
        if not r.get('path') or not r.get('sha256'):
            raise ValueError('Register a verified source-wall logo for '+r['id'])
        path=ROOT/r['path'];raw=path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=r['sha256']:
            raise ValueError('Source icon changed; verify provenance: '+r['path'])
        w=r['header_width'];data=base64.b64encode(raw).decode('ascii')
        if r.get('light_backdrop'):
            # Local light backing keeps dark logos legible without changing artwork.
            out.append(f'<rect x="{x+(cell_w-w)/2-3:g}" y="{y+5}" width="{w+6}" height="44" rx="5" fill="#fff"/>')
        out.append(f'<image x="{x+(cell_w-w)/2:g}" y="{y+6}" width="{w}" height="42" preserveAspectRatio="xMidYMid meet" xlink:href="data:{mime[path.suffix]};base64,{data}"/>')
        out.append(f'<text x="{x+cell_w/2:g}" y="{y+62}" text-anchor="middle" font-family="Arial, sans-serif" font-size="9.5" fill="{label_color}">{name}</text></g>')
    return '\n'.join(out+['</svg>'])+'\n'

def refresh_header(text, language):
    """Keep source cards and small catalog counts derived from actual content."""
    body=text[text.index(BODY_START):]
    records=courses(text)
    label='资源来源 · 非赞助或背书' if language=='zh' else 'Resource sources · not sponsorships or endorsements'
    wall=[f'<p align="center"><strong>📚 {label}</strong></p>']
    for group,sources in source_card_records(text).items():
        if not sources:
            continue
        card=SOURCE_CARDS[group]
        names=html.escape(', '.join(r['name'] for r in sources),quote=True)
        title=html.escape(card[language])
        wall.append(f'<p align="center"><strong>{title}</strong><br>\n<img src="icons/{card["file"]}" alt="{title}: {names}" width="720">\n</p>')
    text=re.sub(r'<!-- SOURCES:START -->.*?<!-- SOURCES:END -->','<!-- SOURCES:START -->\n'+'\n'.join(wall)+'\n<!-- SOURCES:END -->',text,flags=re.S)
    counts=[(len(records),'门课程' if language=='zh' else 'courses'),(len(set(c['subject'] for c in records)),'个学科' if language=='zh' else 'subjects'),(len(re.findall(r'^- \[',body,flags=re.M)),'篇技术文章' if language=='zh' else 'articles')]
    for count,label in counts:text=re.sub(r'\[\d+ '+label+r'\]',f'[{count} {label}]',text)
    return text

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    for name,lang in [('README.md','zh'),('README-en.md','en')]:
        path=ROOT/name;text=path.read_text();updated=refresh_header(text,lang)
        if args.check: assert text==updated,'Synchronize header: '+name
        else: path.write_text(updated)
    zh=source_card_records((ROOT/'README.md').read_text())
    en=source_card_records((ROOT/'README-en.md').read_text())
    assert zh==en,'Source card language mismatch'
    for group,records in zh.items():
        wall=source_wall(records,group)
        wall_path=ROOT/'icons'/SOURCE_CARDS[group]['file']
        if args.check: assert wall_path.read_text()==wall,'Synchronize source card: '+group
        else: wall_path.write_text(wall)
    data=bilingual_courses((ROOT/'README.md').read_text(), (ROOT/'README-en.md').read_text())
    out=(ROOT/'resource-map/template.html').read_text().replace('/*__COURSES__*/',json.dumps(data,ensure_ascii=False).replace('</','<\\/'))
    target=ROOT/'resource-map/index.html'
    if args.check:
        assert target.read_text()==out,'Run python tools/build_resource_map.py to synchronize the map'
    else: target.write_text(out)
    print(f'Validated {len(data)} courses in {len(set(x["subject"] for x in data))} subjects')
