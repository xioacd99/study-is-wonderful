# 交互课程图 / Interactive course map

`index.html` 是独立、无外部脚本依赖的课程思维导图。下载该文件后用现代浏览器打开即可使用；GitHub 的 blob 文件页只展示源码，不执行 HTML。已发布：[打开交互课程图](https://xioacd99.github.io/study-is-wonderful/resource-map/)。

`index.html` is a standalone course mind map with no external script dependencies. Download and open it in a modern browser. GitHub blob pages show source, not a running app. Published: [open the interactive course map](https://xioacd99.github.io/study-is-wonderful/resource-map/).

功能 / Features:
- 思维导图 / 分层列表双视图，手机也可切换真正连线图；学科 → 相关主题 → 全部课程分别展开和收起 / Switch between a connected mind map and a nested list, including on mobile; expand or collapse subjects and topics.
- 课程搜索、缩放、恢复全景 / Search, zoom, and return to overview.
- 真正中英文切换，界面、课程和简介随语言切换 / Switch the UI, course titles, descriptions, and source labels between Chinese and English.
- 课程详情内一键返回原图位置；外部课程在新标签打开，原图保留 / Return from details to the same map position; external sources open in a new tab.
- 键盘可访问按钮和搜索，详情支持 Escape；窄屏使用分层列表，无需横向拖动 / Keyboard controls, Escape to close details, and swipeable connected map or nested list on narrow screens.

## 更新 / Updating

中文 `README.md` 与英文 `README-en.md` 是成对的课程数据来源。按现有稳定 `course-*` 锚点解析每个课程列表条目，一级学科取 `##` 标题、主题取 `###` 标题。请保留稳定锚点；修改课程内容、来源、分组或顺序后运行：

The Chinese `README.md` and English `README-en.md` are paired course-data sources. The builder reads course list entries with stable `course-*` anchors, `##` subjects and `###` topics. Preserve anchors and regenerate after changing courses, sources, groups, or order:

```sh
python tools/build_resource_map.py
python tools/build_resource_map.py --check
python -m unittest discover -s tests -v
```

编辑 `template.html` 修改交互和样式，再生成 `index.html`。不要手动修改生成的数据副本。提交前测试展开/收起、搜索、课程链接、详情返回与缩放，核对全部课程覆盖。保留外链交互图入口和普通目录，不再生成原生折叠导航；每主题按英文名排序。

Edit `template.html` for UI changes and regenerate `index.html`; do not manually edit generated data. Test expansion, search, links, return, zoom, and complete coverage before committing. Preserve the external map entry and normal TOC without duplicate collapsible navigation. Sort each topic by English title.

## 发布 / Publishing

经维护者授权，GitHub Pages 已从 `dev` 分支根目录公开发布，后续 `dev` 提交自动部署，HTTPS 已启用。`index.html` 将主页引导至 `resource-map/`。这不改变 `main`，也不表示可自动合并。

With the owner's authorization, GitHub Pages publishes the root of `dev` publicly and deploys subsequent `dev` commits automatically over HTTPS. The root `index.html` routes visitors to `resource-map/`. This does not change `main` or authorize automatic merges.

当前在线地址 / Live URL: https://xioacd99.github.io/study-is-wonderful/resource-map/

每次修改后确认 Pages 构建完成，并在真实公开页面测试代表交互；本地预览通过不等于远程部署成功。

After changes, verify the Pages build and representative interactions on the live site; a passing local preview is not proof of deployment.

## 视觉与预览 / Visual assets

项目图标 `icon.png` 由 GPT image 生成。`preview-zh.jpg` 和 `preview-en.jpg` 为实际页面的浏览器截图，不是示意图；界面变化后重新截图并同步 README 入口。

The project icon is generated with GPT image. README previews are real browser screenshots of the rendered application; recapture both languages after visual changes.

全景按左右对称学科分支展示，点击学科聚焦主题树；学科筛选与适应画布按钮帮助探索大型树。保留全展开、搜索、缩放、列表替代及中英切换。

The overview uses balanced subject branches. Select a subject to focus its topic tree, or use the subject filter and fit-to-view control. Expand-all, search, zoom, list view and both languages remain available.


桌面采用学科侧栏、顶部搜索、主画布和浮动工具栏；手机改为紧凑筛选与双列全景，不把桌面长横图强塞到窄屏。渐变项目图标与柔和紫色设计保持一致。

Desktop uses a subject sidebar, top search and floating canvas tools. Mobile has compact filtering and a two-column overview, with bilingual labels and the same course data.


最新视觉：恢复青绿与金色，采用重新生成的三片折叠丝带图标。桌面全景为上下两排学科连接中心节点，手机保留独立双列树；主题层仍可聚焦展开。

Current visual: teal and gold with a newly generated three-ribbon symbol. Desktop overview places subjects above and below the central hub; mobile retains its own two-column tree. Topic focus remains available.
