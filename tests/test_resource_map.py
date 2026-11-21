import importlib.util,pathlib,unittest,re
ROOT=pathlib.Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('builder',ROOT/'tools/build_resource_map.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class MapTests(unittest.TestCase):
 def setUp(self):
  self.text=(ROOT/'README.md').read_text();self.english=(ROOT/'README-en.md').read_text();self.c=builder.bilingual_courses(self.text,self.english)
 def test_complete_unique_coverage(self):
  anchors=re.findall(r'<a id="(course-[^"]+)"',self.text)
  self.assertEqual(len(anchors),len(set(anchors)))
  self.assertEqual(set(anchors),{c['id'] for c in self.c})
 def test_language_switch_and_parity(self):
  self.assertIn('[English](README-en.md)',self.text)
  self.assertIn('[简体中文](README.md)',self.english)
  for text in [self.text,self.english]:
   self.assertEqual([c['id'] for c in builder.courses(text)],[c['id'] for c in self.c])
   ids=set(re.findall(r'<a id="([^"]+)"',text))
   for href in re.findall(r'\]\(#([^\)]+)\)',text): self.assertIn(href,ids)
 def test_blog_source_and_icon_parity(self):
  def blogs(text):
   return [(re.findall(r'\]\((https?://[^)]+)\)',line), re.findall(r'<img [^>]+>',line)) for line in text.splitlines() if line.startswith('- [') and '](' in line and '](#' not in line]
  self.assertEqual(blogs(self.text),blogs(self.english))
 def test_navigation_and_content(self):
  for c in self.c:
   self.assertIn('<a id="'+c['id']+'"></a>',self.text)
   self.assertTrue(c['subject'] and c['group'] and c['title'] and c['description'])
   self.assertTrue(c['links'])
   self.assertTrue(all(x['url'].startswith(('https://','http://')) for x in c['links']))
 def test_topic_title_sort_and_no_duplicate_navigation(self):
  for text in [self.text,self.english]:
   self.assertNotIn('<details>',text)
   self.assertNotIn('| <a id="course-',text)
   self.assertIn('https://xioacd99.github.io/study-is-wonderful/resource-map/',text)
  topics={}
  for c in builder.courses(self.english):
   topics.setdefault((c['subject'],c['group']),[]).append(c['title'].casefold())
  for titles in topics.values(): self.assertEqual(titles,sorted(titles))
 def test_compact_header_and_thumbnail(self):
  for lang,text in [('zh',self.text),('en',self.english)]:
   self.assertIn('resource-map/preview-'+lang+'.jpg',text)
   self.assertNotIn('<table>',text)
   self.assertNotIn('toc.jpg',text)
   self.assertNotIn('Smart TOC',text)
   ids=set(re.findall(r'<a id="([^"]+)"',text))
   for anchor in re.findall(r'href="#([^"]+)"',text): self.assertIn(anchor,ids)
 def test_no_redundant_course_tails(self):
  for text in [self.text,self.english]:
   for line in text.splitlines():
    if line.startswith('- <a id="course-'):
     self.assertNotIn('](#resource-map)',line)
     urls=re.findall(r'\]\((https?://[^)]+)\)',line)
     self.assertEqual(len(urls),len(set(urls)))
 def test_single_language_payload(self):
  for key,text in [('zh',self.text),('en',self.english)]:
   raw={c['id']:c for c in builder.courses(text)}
   for c in self.c:
    self.assertEqual(c['locales'][key],{k:v for k,v in raw[c['id']].items() if k!='id'})
 def test_brand_and_focus_controls(self):
  template=(ROOT/'resource-map/template.html').read_text()
  self.assertIn('id="subject-filter"',template)
  self.assertIn('id="fit"',template)
  self.assertIn('function focusSubject',template)
  self.assertIn('src="icon.png?v=teal-orbit-3"',template)
  self.assertEqual(len(self.c),154)
  for text in [self.text,self.english]:
   self.assertNotIn('# 📚',text)
   self.assertIn('resource-map/icon.png',text)
 def test_mobile_mind_map_mode(self):
  template=(ROOT/'resource-map/template.html').read_text()
  self.assertIn('id="map-view"',template)
  self.assertIn('id="list-view"',template)
  self.assertIn('touch-action:pan-x pan-y',template)
  self.assertIn('body[data-view=list] svg,body[data-view=list] .root{display:none}',template)
  self.assertIn('id="subject-nav"',template)
  self.assertIn('class="canvas-tools"',template)
 def test_knowledge_graph_membership(self):
  template=(ROOT/'resource-map/template.html').read_text()
  self.assertIn('function renderKnowledge(shown)',template)
  self.assertIn('el.dataset.parent=n.parent.id',template)
  self.assertIn('not prerequisites',template)
  self.assertIn('graph-overview',template)
  self.assertIn('setZoom(zoom*1.4)',template)
 def test_generated_html(self):
  import json
  expected=(ROOT/'resource-map/template.html').read_text().replace('/*__COURSES__*/',json.dumps(self.c,ensure_ascii=False).replace('</','<\\/'))
  self.assertEqual(expected,(ROOT/'resource-map/index.html').read_text())
 def test_source_wall_grid_and_families(self):
  import xml.etree.ElementTree as ET,json
  records=builder.source_records(self.text)
  self.assertEqual([r['id'] for r in records],[r['id'] for r in builder.source_records(self.english)])
  for org in {r['organization'] for r in records}:
   positions=[i for i,r in enumerate(records) if r['organization']==org]
   self.assertEqual(positions,list(range(min(positions),max(positions)+1)))
  ids=[r['id'] for r in records]
  google=[r['id'] for r in records if r['organization']=='google']
  self.assertEqual(google,['google','antigravity','google-cloud','deepmind','youtube'])
  manifest=json.loads((ROOT/'icons/sources.json').read_text())
  keys=[(manifest['organization_names'][r['organization']].casefold(),r['name'].casefold(),r['id']) for r in records]
  self.assertEqual(keys,sorted(keys))
  for key in ['stanford','mit','berkeley','stonybrook','cmu']:
   r=next(r for r in records if r['id']==key)
   self.assertTrue(r['path'].endswith('-seal.svg'))
  wall=builder.source_wall(self.text)
  self.assertEqual(wall,(ROOT/'icons/source-wall.svg').read_text())
  doc=ET.fromstring(wall);ns={'s':'http://www.w3.org/2000/svg'}
  images=doc.findall('.//s:image',ns)
  cells=doc.findall('./s:g',ns)
  self.assertEqual([cell.attrib['data-source'] for cell in cells],ids)
  self.assertEqual(len(images),len(records))
  self.assertTrue(all(cell.find('./s:image',ns) is not None for cell in cells))
  self.assertFalse(any(cell.find('./s:rect',ns) is not None for cell in cells))
  rows={}
  for n,cell in enumerate(cells):
   text=cell.findall('./s:text',ns)[-1]
   rows.setdefault(text.attrib['y'],[]).append(cell)
   self.assertEqual(float(text.attrib['x']),(n%6)*120+60)
  for image in images:
   self.assertEqual(image.attrib['preserveAspectRatio'],'xMidYMid meet')
   self.assertTrue(image.attrib['{http://www.w3.org/1999/xlink}href'].startswith('data:image/'))
  self.assertTrue(all(len(row)==6 for row in list(rows.values())[:-1]))
  self.assertLessEqual(len(list(rows.values())[-1]),6)
 def test_source_wall_covers_official_links_without_inline_logos(self):
  for text in (self.text,self.english):
   records={r['id']:r for r in builder.source_records(text)}
   self.assertTrue({'yale','eth-zurich','vllm','ggml','huggingface','princeton','caltech','harvard','cornell','zhejiang','ntu'} <= set(records))
   sample=builder.BODY_START+'\n- [Example](https://vllm.ai/blog/example)'
   self.assertEqual([r['id'] for r in builder.source_records(sample)],['vllm'])
   republished=builder.BODY_START+'\n- [Example](https://huggingface.co/blog/ggml-org/example)'
   self.assertEqual([r['id'] for r in builder.source_records(republished)],['ggml','huggingface'])
   with self.assertRaisesRegex(ValueError,'Classify new catalog source URLs'):
    builder.source_records(sample.replace('vllm.ai','unclassified.example'))
 def test_mirror_does_not_hide_verified_course_producer(self):
  line=next(l for l in self.english.splitlines() if 'id="course-cs-49"' in l)
  sample=builder.BODY_START+'\n'+line
  self.assertEqual([r['id'] for r in builder.source_records(sample)],['bilibili','princeton'])
  with self.assertRaisesRegex(ValueError,'Review source attribution after link change'):
   builder.source_records(sample.replace('BV1FL411K7vK','BV1Different'))
 def test_source_wall_rejects_text_placeholders(self):
  from unittest.mock import patch
  with patch.object(builder,'source_records',return_value=[{'id':'missing-logo','name':'Missing logo'}]):
   with self.assertRaisesRegex(ValueError,'Register a verified source-wall logo for missing-logo'):
    builder.source_wall(self.text)
 def test_source_wall_is_idempotent(self):
  for lang,text in [('zh',self.text),('en',self.english)]:
   self.assertEqual(builder.refresh_header(text,lang),text)
   self.assertIn('icons/source-wall.svg',text)
   self.assertIn('<strong>📚 ',text)
if __name__=='__main__':unittest.main()
