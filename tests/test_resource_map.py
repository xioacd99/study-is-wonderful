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
   self.assertIn('](#'+c['id']+')',self.text)
   self.assertTrue(c['subject'] and c['group'] and c['title'] and c['description'])
   self.assertTrue(c['links'])
   self.assertTrue(all(x['url'].startswith(('https://','http://')) for x in c['links']))
 def test_generated_html(self):
  import json
  expected=(ROOT/'resource-map/template.html').read_text().replace('/*__COURSES__*/',json.dumps(self.c,ensure_ascii=False).replace('</','<\\/'))
  self.assertEqual(expected,(ROOT/'resource-map/index.html').read_text())
if __name__=='__main__':unittest.main()
