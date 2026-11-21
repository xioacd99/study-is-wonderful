#!/usr/bin/env python3
"""Generate the bilingual map, README TOC, and themed source walls."""
import argparse
import base64
import hashlib
import html
import json
import math
import pathlib
import re
from urllib.parse import urlsplit

ROOT = pathlib.Path(__file__).resolve().parents[1]
BODY_START = '<a id="数学-math">'
TOC_PATTERN = re.compile(r'<!-- TOC:START -->.*?<!-- TOC:END -->', re.S)
SOURCES_PATTERN = re.compile(r'<!-- SOURCES:START -->.*?<!-- SOURCES:END -->', re.S)
RESOURCE_HEADING = re.compile(r'^- (?:<a id="course-[^"]+"></a>\s*)?\[')
RESOURCE_LINK = re.compile(r'\[([^\]]+)\]\((https?://[^\s)]+)\)')


def catalog_body(text):
    start = text.index(BODY_START)
    end = text.find('<!-- SOURCES:START -->', start)
    return text[start:end] if end != -1 else text[start:]


def host_source_names():
    manifest = json.loads((ROOT / 'icons/sources.json').read_text())
    mapping = {}
    for r in manifest['sources']:
        for host in r.get('hosts', []):
            mapping[host] = r['name']
    return mapping


def courses(text):
    host_names = host_source_names()
    result = []
    section = ''
    group = ''
    current = None
    for line in catalog_body(text).splitlines():
        if line.startswith('## '):
            section = line[3:]
            current = None
        elif line.startswith('### '):
            group = line[4:]
            current = None
        m = re.match(r'- <a id="(course-[^"]+)"></a>', line)
        if m:
            links = re.findall(r'\[([^\]]+)\]\((https?://[^\s)]+)\)', line)
            if not links:
                raise ValueError('Missing source for ' + m[1])
            unique = []
            seen = set()
            for label, url in links:
                if url not in seen:
                    host = urlsplit(url).hostname or ''
                    unique.append(dict(label=label, url=url, source=host_names.get(host, host)))
                    seen.add(url)
            current = dict(
                id=m[1],
                subject=section,
                group=group,
                title=links[0][0],
                links=unique,
                description='',
            )
            result.append(current)
        elif current and line.startswith('  > '):
            current['description'] += ('\n' if current['description'] else '') + line[4:]
        elif line.startswith('- '):
            current = None
    if len({x['id'] for x in result}) != len(result) or not result:
        raise ValueError('Missing or duplicate course anchors')
    if any(not c['description'] for c in result):
        raise ValueError('Missing course description')
    return result


def bilingual_courses(chinese, english):
    zh = courses(chinese)
    en = courses(english)
    if [c['id'] for c in zh] != [c['id'] for c in en]:
        raise ValueError('README language versions differ in course coverage or order')
    result = []

    def join(a, b, separator=' / '):
        return a if a == b else a + separator + b

    for a, b in zip(zh, en):
        if [x['url'] for x in a['links']] != [x['url'] for x in b['links']]:
            raise ValueError('README source URLs differ for ' + a['id'])
        result.append(
            dict(
                id=a['id'],
                subject=join(a['subject'], b['subject']),
                group=join(a['group'], b['group']),
                title=join(a['title'], b['title']),
                links=[
                    dict(label=join(x['label'], y['label']), url=x['url'], source=x['source'])
                    for x, y in zip(a['links'], b['links'])
                ],
                description=join(a['description'], b['description'], '\n'),
                locales={
                    'zh': {k: v for k, v in a.items() if k != 'id'},
                    'en': {k: v for k, v in b.items() if k != 'id'},
                },
            )
        )
    return result


def blogs(text):
    host_names = host_source_names()
    result = []
    in_blogs = False
    group = ''
    current = None
    for line in catalog_body(text).splitlines():
        if line.startswith('## '):
            in_blogs = line[3:] in ('技术博客', 'Technical blogs')
            group = ''
            current = None
        elif in_blogs and line.startswith('### '):
            group = line[4:]
            current = None
        elif in_blogs and line.startswith('- ['):
            m = re.match(r'^- \[([^\]]+)\]\((https?://[^\s)]+)\)(.*)$', line)
            if not m:
                raise ValueError('Invalid blog row: ' + line)
            title, url, tail = m.group(1), m.group(2), m.group(3)
            pub = re.sub(r'<img[^>]+>', '', tail).replace('·', ' ').strip()
            host = urlsplit(url).hostname or ''
            source = pub or host_names.get(host, host)
            idx = len(result) + 1
            current = dict(
                id=f'blog-{idx:02d}',
                group=group,
                title=title,
                links=[dict(label=title, url=url, source=source)],
                description='',
            )
            result.append(current)
        elif current and line.startswith('  > '):
            current['description'] += ('\n' if current['description'] else '') + line[4:]
        elif line.startswith('- '):
            current = None
    if not result:
        raise ValueError('Missing technical blogs')
    if any(not b['description'] or not b['group'] for b in result):
        raise ValueError('Missing technical blog group or description')
    return result


def bilingual_blogs(chinese, english):
    zh = blogs(chinese)
    en = blogs(english)
    if len(zh) != len(en) or [x['links'][0]['url'] for x in zh] != [x['links'][0]['url'] for x in en]:
        raise ValueError('README language versions differ in blog coverage or order')
    result = []

    def join(a, b, separator=' / '):
        return a if a == b else a + separator + b

    for a, b in zip(zh, en):
        result.append(
            dict(
                id=a['id'],
                subject='技术博客 / Technical blogs',
                group=join(a['group'], b['group']),
                title=join(a['title'], b['title']),
                links=[
                    dict(label=join(a['title'], b['title']), url=a['links'][0]['url'], source=a['links'][0]['source'])
                ],
                description=join(a['description'], b['description'], '\n'),
                locales={
                    'zh': dict(subject='技术博客', **{k: v for k, v in a.items() if k != 'id'}),
                    'en': dict(subject='Technical blogs', **{k: v for k, v in b.items() if k != 'id'}),
                },
            )
        )
    return result


def resource_sources(text):
    """Classify every catalog link; require explicit review of new source hosts."""
    body = catalog_body(text)
    manifest = json.loads((ROOT / 'icons/sources.json').read_text())
    by_id = {r['id']: r for r in manifest['sources']}
    by_path = {r['path']: r['id'] for r in manifest['sources'] if 'path' in r}
    by_host = {}
    for r in manifest['sources']:
        for host in r.get('hosts', []):
            if host in by_host:
                raise ValueError('Duplicate source host in manifest: ' + host)
            by_host[host] = r['id']
    credits = {}
    for r in manifest['sources']:
        for credit in r.get('course_credits', []):
            if urlsplit(credit['evidence']).scheme != 'https':
                raise ValueError('Missing reference for course attribution: ' + credit['course'])
            credits.setdefault(credit['course'], []).append((r['id'], credit['resource_url']))
    unregistered = set()
    present = set()
    for line in body.splitlines():
        if not RESOURCE_HEADING.match(line):
            continue
        line_sources = set()
        urls = [url for _, url in RESOURCE_LINK.findall(line)]
        anchor = re.match(r'^- <a id="(course-[^"]+)"></a>', line)
        if anchor:
            for sid, credited_url in credits.get(anchor[1], []):
                if credited_url not in urls:
                    raise ValueError('Review source attribution after link change: ' + anchor[1])
                line_sources.add(sid)
        for url in urls:
            link = urlsplit(url)
            if link.hostname not in by_host:
                unregistered.add(url)
                continue
            line_sources.add(by_host[link.hostname])
            for r in manifest['sources']:
                if any(
                    link.hostname == p['host'] and link.path.startswith(p['prefix'])
                    for p in r.get('credited_paths', [])
                ):
                    line_sources.add(r['id'])
        icons = set(re.findall(r'<img src="([^"]+)"', line))
        unknown = icons - by_path.keys()
        if unknown:
            raise ValueError('Register new source icons in icons/sources.json: ' + ', '.join(sorted(unknown)))
        bad = {by_path[path] for path in icons} - line_sources
        if bad and not unregistered:
            raise ValueError('Source icon has no matching link on its resource row: ' + ', '.join(sorted(bad)) + ' in ' + line)
        present.update(line_sources)
    if unregistered:
        raise ValueError('Classify new catalog source URLs in icons/sources.json: ' + ', '.join(sorted(unregistered)))
    return manifest, [by_id[sid] for sid in present]


def source_records(text):
    """Derive sources from resource links, not whether a logo is available."""
    manifest, records = resource_sources(text)
    organization_names = manifest['organization_names']
    return sorted(records, key=lambda r: (organization_names[r['organization']].casefold(), r['name'].casefold(), r['id']))


# Unified Teal + Gold cards across light and dark GitHub themes.
SOURCE_CARDS = {
    'university': {
        'file': 'source-wall-universities.svg',
        'dark_file': 'source-wall-universities-dark.svg',
        'zh': '大学',
        'en': 'Universities',
        'themes': {
            'light': ('#f6f9f6', '#d8e4db', '#2d6a54', '#2b443b', '#ffffff', '#e3ece4'),
            'dark': ('#161b22', '#30363d', '#4ea885', '#c9d1d9', '#ffffff', '#30363d'),
        },
    },
    'project': {
        'file': 'source-wall-projects.svg',
        'dark_file': 'source-wall-projects-dark.svg',
        'zh': '项目与平台',
        'en': 'Projects & Platforms',
        'themes': {
            'light': ('#f6f9f6', '#d8e4db', '#bd9b49', '#2b443b', '#ffffff', '#e3ece4'),
            'dark': ('#161b22', '#30363d', '#d4b15e', '#c9d1d9', '#ffffff', '#30363d'),
        },
    },
    'company': {
        'file': 'source-wall-companies.svg',
        'dark_file': 'source-wall-companies-dark.svg',
        'zh': '公司',
        'en': 'Companies',
        'themes': {
            'light': ('#f6f9f6', '#d8e4db', '#3c7a67', '#2b443b', '#ffffff', '#e3ece4'),
            'dark': ('#161b22', '#30363d', '#59b399', '#c9d1d9', '#ffffff', '#30363d'),
        },
    },
}


def source_card_records(text):
    """Require each source to declare its card explicitly, including unused entries."""
    manifest = json.loads((ROOT / 'icons/sources.json').read_text())
    bad = [r['id'] for r in manifest['sources'] if r.get('group') not in SOURCE_CARDS]
    if bad:
        raise ValueError('Assign source-wall groups in icons/sources.json: ' + ', '.join(sorted(bad)))
    cards = {key: [] for key in SOURCE_CARDS}
    for r in source_records(text):
        cards[r['group']].append(r)
    return cards


def source_wall(records, group, theme='light'):
    """Render one self-contained six-column card with uniform tiles and centered orphan row."""
    card = SOURCE_CARDS[group]
    background, border, accent, label_color, tile_fill, tile_border = card['themes'][theme]
    cols = json.loads((ROOT / 'icons/sources.json').read_text())['columns']
    cell_w, cell_h = 116, 78
    pad_x, pad_y = 12, 14
    width = cols * cell_w + 2 * pad_x
    rows = max(1, math.ceil(len(records) / cols))
    height = rows * cell_h + 2 * pad_y
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img">',
        '<title>' + html.escape(card['en']) + '</title>',
        '<desc>' + html.escape(', '.join(r['name'] for r in records)) + '. Not sponsorships or endorsements.</desc>',
        f'<rect x=".5" y=".5" width="{width-1}" height="{height-1}" rx="16" fill="{background}" stroke="{border}"/>',
        f'<rect x="{width/2-22:g}" y="7" width="44" height="2.5" rx="1.25" fill="{accent}"/>',
    ]
    mime = {'.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp', '.avif': 'image/avif', '.jpg': 'image/jpeg'}
    for n, r in enumerate(records):
        row = n // cols
        col = n % cols
        row_len = min(cols, len(records) - row * cols)
        row_x0 = pad_x + (cols - row_len) * cell_w / 2
        x = row_x0 + col * cell_w
        y = pad_y + row * cell_h
        name = html.escape(r['name'])
        out.append(f'<g data-source="{r["id"]}"><title>{name}</title>')
        if not r.get('path') or not r.get('sha256'):
            raise ValueError('Register a verified source-wall logo for ' + r['id'])
        path = ROOT / r['path']
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != r['sha256']:
            raise ValueError('Source icon changed; verify provenance: ' + r['path'])
        w = min(r['header_width'], cell_w - 24)
        data = base64.b64encode(raw).decode('ascii')
        out.append(
            f'<rect x="{x+10:g}" y="{y+4}" width="{cell_w-20}" height="46" rx="10" fill="{tile_fill}" stroke="{tile_border}" stroke-width="0.75"/>'
        )
        out.append(
            f'<image x="{x+(cell_w-w)/2:g}" y="{y+7}" width="{w}" height="40" preserveAspectRatio="xMidYMid meet" xlink:href="data:{mime[path.suffix]};base64,{data}"/>'
        )
        out.append(
            f'<text x="{x+cell_w/2:g}" y="{y+64}" text-anchor="middle" font-family="Arial, sans-serif" font-size="9.5" fill="{label_color}">{name}</text></g>'
        )
    return '\n'.join(out + ['</svg>']) + '\n'


def build_toc_block(body, records, blog_count):
    anchors = re.findall(r'<a id="([^"]+)"></a>\s*\n\s*\n## ([^\n]+)', body)
    counts = {}
    for c in records:
        counts[c['subject']] = counts.get(c['subject'], 0) + 1
    items = []
    for anchor_id, heading in anchors:
        if heading in counts:
            items.append(f'<a href="#{anchor_id}">{html.escape(heading)} ({counts[heading]})</a>')
        elif heading in ('技术博客', 'Technical blogs'):
            items.append(f'<a href="#{anchor_id}">{html.escape(heading)} ({blog_count})</a>')
    mid = math.ceil(len(items) / 2)
    line1 = ' · '.join(items[:mid])
    line2 = ' · '.join(items[mid:])
    inner = line1 + ('<br>\n' + line2 if line2 else '')
    return f'<!-- TOC:START -->\n<p align="center">\n{inner}\n</p>\n<!-- TOC:END -->'


def refresh_header(text, language):
    """Keep subject TOC, source cards, and catalog counts derived from actual content."""
    body = catalog_body(text)
    records = courses(text)
    blog_count = len(re.findall(r'^- \[', body, flags=re.M))
    if TOC_PATTERN.search(text):
        text = TOC_PATTERN.sub(build_toc_block(body, records, blog_count), text)
    label = '资源来源 · 非赞助或背书' if language == 'zh' else 'Resource sources · not sponsorships or endorsements'
    wall = [f'<p align="center"><strong>📚 {label}</strong></p>']
    for group, sources in source_card_records(text).items():
        if not sources:
            continue
        card = SOURCE_CARDS[group]
        names = html.escape(', '.join(r['name'] for r in sources), quote=True)
        title = html.escape(card[language])
        wall.append(
            f'<p align="center"><strong>{title}</strong><br>\n'
            f'<picture>\n'
            f'  <source media="(prefers-color-scheme: dark)" srcset="icons/{card["dark_file"]}">\n'
            f'  <img src="icons/{card["file"]}" alt="{title}: {names}" width="720">\n'
            f'</picture>\n'
            f'</p>'
        )
    text = SOURCES_PATTERN.sub(
        '<!-- SOURCES:START -->\n' + '\n'.join(wall) + '\n<!-- SOURCES:END -->',
        text,
    )
    counts = [
        (len(records), '门课程' if language == 'zh' else 'courses'),
        (len(set(c['subject'] for c in records)), '个学科' if language == 'zh' else 'subjects'),
        (blog_count, '篇技术文章' if language == 'zh' else 'articles'),
    ]
    for count, unit in counts:
        text = re.sub(r'\[\d+ ' + unit + r'\]', f'[{count} {unit}]', text)
    return text


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    for name, lang in [('README.md', 'zh'), ('README-en.md', 'en')]:
        path = ROOT / name
        text = path.read_text()
        updated = refresh_header(text, lang)
        if args.check:
            assert text == updated, 'Synchronize header: ' + name
        else:
            path.write_text(updated)
    zh = source_card_records((ROOT / 'README.md').read_text())
    en = source_card_records((ROOT / 'README-en.md').read_text())
    assert zh == en, 'Source card language mismatch'
    for group, records in zh.items():
        for theme, key in [('light', 'file'), ('dark', 'dark_file')]:
            wall = source_wall(records, group, theme=theme)
            wall_path = ROOT / 'icons' / SOURCE_CARDS[group][key]
            if args.check:
                assert wall_path.read_text() == wall, f'Synchronize source card ({theme}): {group}'
            else:
                wall_path.write_text(wall)
    data = bilingual_courses((ROOT / 'README.md').read_text(), (ROOT / 'README-en.md').read_text())
    blog_data = bilingual_blogs((ROOT / 'README.md').read_text(), (ROOT / 'README-en.md').read_text())
    out = (
        (ROOT / 'resource-map/template.html')
        .read_text()
        .replace('/*__COURSES__*/', json.dumps(data, ensure_ascii=False).replace('</', '<\\/'))
        .replace('/*__BLOGS__*/', json.dumps(blog_data, ensure_ascii=False).replace('</', '<\\/'))
    )
    target = ROOT / 'resource-map/index.html'
    if args.check:
        assert target.read_text() == out, 'Run python tools/build_resource_map.py to synchronize the map'
    else:
        target.write_text(out)
    print(f'Validated {len(data)} courses in {len(set(x["subject"] for x in data))} subjects and {len(blog_data)} blogs')
