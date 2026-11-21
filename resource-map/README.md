# 学习星图 / Learning Star Map

`index.html` 是独立、无外部脚本依赖的交互式学习星图，汇总目录中的全部跨学科课程与前沿技术博客。下载该文件后用现代浏览器打开即可使用；已发布：[打开学习星图](https://xioacd99.github.io/study-is-wonderful/resource-map/)。

`index.html` is a standalone interactive Learning Star Map with no external script dependencies, covering both catalog courses and technical blogs. Published: [open the Learning Star Map](https://xioacd99.github.io/study-is-wonderful/resource-map/).

## 功能 / Features

- **课程与技术博客双模式**：侧栏支持在「课程」与「技术博客」之间一键切换，并在搜索时提示另一标签页中的匹配数量 / **Courses & Tech Blogs tabs** with cross-tab search match hints.
- **知识图谱 / 分层列表双视图**：桌面端默认知识图谱，移动端（`<=760px`）默认更易读的分层列表，均可一键切换 / **Knowledge graph & Hierarchy list**: graph by default on desktop, list by default on mobile (`<=760px`), switchable anytime.
- **三级语义缩放与流畅手势**：布局与缩放解耦，支持鼠标滚轮以光标为中心缩放、触控双指捏合及拖拽平移；全景展示学科分布、中景/聚焦单学科时直接显示全部主题名称、近景展示条目与平台徽标 / **3-level semantic zoom (LOD)** with cursor-anchored wheel/pinch zoom and immediate topic labels on subject focus.
- **悬停聚光灯与右侧详情抽屉**：悬停节点高亮关联分支并展示即时预览提示；点击条目打开右侧抽屉，展示面包屑、明确来源平台入口、目录定位链接以及同主题其他课程/文章推荐 / **Hover spotlight, tooltip, and right-side detail drawer** with explicit platform names and sibling navigation.
- **完整中英文双语切换**：界面、标题、简介与分类标签随语言实时切换 / **Full bilingual switching** for UI, titles, descriptions, and categories.

## 更新 / Updating

中文 `README.md` 与英文 `README-en.md` 是成对数据源。生成器解析带稳定 `course-*` 锚点的全部课程（`/*__COURSES__*/`）以及 `## 技术博客` / `## Technical blogs` 下的全部文章（`/*__BLOGS__*/`），同时自动同步 README 的快捷目录与浅/深色来源图标墙。编辑 `template.html` 或更新目录后运行：

```sh
python3 tools/build_resource_map.py
python3 tools/build_resource_map.py --check
python3 -m unittest discover -s tests -v
```

## 发布与预览 / Publishing & Previews

GitHub Pages 从 `dev` 分支根目录自动部署（`index.html` 引导至 `resource-map/`）。视觉或数据变更后，须在真实无头浏览器（光标移出界面、数量与正文完全一致）重新截取 `preview-zh.jpg` 与 `preview-en.jpg`，并在桌面端与移动端验证交互与零控制台报错。
