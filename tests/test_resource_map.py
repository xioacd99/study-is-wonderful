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
 def test_single_language_payload(self):
  for key,text in [('zh',self.text),('en',self.english)]:
   raw={c['id']:c for c in builder.courses(text)}
   for c in self.c:
    self.assertEqual(c['locales'][key],{k:v for k,v in raw[c['id']].items() if k!='id'})
 def test_generated_html(self):
  import json
  expected=(ROOT/'resource-map/template.html').read_text().replace('/*__COURSES__*/',json.dumps(self.c,ensure_ascii=False).replace('</','<\\/'))
  self.assertEqual(expected,(ROOT/'resource-map/index.html').read_text())
if __name__=='__main__':unittest.main()
