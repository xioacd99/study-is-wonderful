"""Stage only exact generated learning-map assets for the managed preview daemon."""
from argparse import ArgumentParser
from hashlib import sha256
from html import escape
from pathlib import Path
from tempfile import mkdtemp
import json

parser=ArgumentParser(description=__doc__)
parser.add_argument('checkout',type=Path)
parser.add_argument('--parent',type=Path,default=None,
                    help='Writable staging parent under /workspace (default: checkout parent)')
args=parser.parse_args()
source=args.checkout.resolve(strict=True)
parent=(args.parent or source.parent).resolve(strict=True)
if not (parent == Path('/workspace') or Path('/workspace') in parent.parents):
    parser.error('--parent must be underneath /workspace')
paths=('resource-map/index.html','resource-map/icon.png')
if any(not (source/p).is_file() for p in paths):
    parser.error('the built resource-map/index.html and icon.png are required')
stage=Path(mkdtemp(prefix='study-map-preview-',dir=parent))
dist=stage/'dist'
(dist/'resource-map').mkdir(parents=True)
(stage/'.openai').mkdir()
(stage/'.openai'/'hosting.json').write_text(json.dumps({"static":{"directory":"dist"}},indent=2)+'\n')
summary={}
for p in paths:
    data=(source/p).read_bytes()
    target=dist/p
    target.write_bytes(data)
    assert target.read_bytes()==data
    summary[p]={"bytes":len(data),"sha256":sha256(data).hexdigest()}
tag=summary['resource-map/index.html']['sha256'][:16]
(dist/'index.html').write_text(f'''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Learning map QA</title><main><h1>Learning map QA</h1>
<p>Candidate fingerprint: <code>{escape(tag)}</code></p>
<ul><li><a href="resource-map/index.html">Desktop learning map</a></li>
<li><a href="mobile.html">Mobile-width learning map (390 × 844)</a></li></ul></main></html>''',encoding='utf-8')
(dist/'mobile.html').write_text('''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Learning map · 390 × 844</title>
<style>html,body{margin:0;padding:0} iframe{display:block;border:0;width:390px;height:844px;max-width:none}</style>
<iframe title="Learning map at mobile viewport" src="resource-map/index.html" width="390" height="844"></iframe></html>''',encoding='utf-8')
(stage/'source-fingerprints.json').write_text(json.dumps(summary,indent=2)+'\n')
print(stage)
