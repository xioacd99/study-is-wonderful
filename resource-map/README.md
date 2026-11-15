# 交互课程图 / Interactive course map

`index.html` 是独立、无外部脚本依赖的课程思维导图。下载该文件后用现代浏览器打开即可使用；GitHub 的 blob 文件页只展示源码，不执行 HTML。已发布：[打开交互课程图](https://xioacd99.github.io/study-is-wonderful/resource-map/)。

`index.html` is a standalone course mind map with no external script dependencies. Download and open it in a modern browser. GitHub blob pages show source, not a running app. Published: [open the interactive course map](https://xioacd99.github.io/study-is-wonderful/resource-map/).

功能 / Features:
- 学科 → 相关主题 → 全部课程，分别展开和收起 / Expand or collapse subjects and topics.
- 课程搜索、缩放、恢复全景 / Search, zoom, and return to overview.
- 中英文分行、原简介、所有课程来源链接 / Bilingual titles on separate lines, original descriptions, and source links.
- 课程详情内一键返回原图位置；外部课程在新标签打开，原图保留 / Return from details to the same map position; external sources open in a new tab.
- 键盘可访问按钮和搜索，详情支持 Escape；窄屏可横向滚动 / Keyboard controls, Escape to close details, and horizontal scrolling on narrow screens.

## 更新 / Updating

中文 `README.md` 与英文 `README-en.md` 是成对的课程数据来源。按现有稳定 `course-*` 锚点解析每个三列表格行，一级学科取 `##` 标题、主题取 `###` 标题。请保留稳定锚点；修改课程内容、来源、分组或顺序后运行：

The Chinese `README.md` and English `README-en.md` are paired course-data sources. The builder reads three-column course rows with stable `course-*` anchors, `##` subjects and `###` topics. Preserve anchors and regenerate after changing courses, sources, groups, or order:

```sh
python tools/build_resource_map.py
python tools/build_resource_map.py --check
python -m unittest discover -s tests -v
```

编辑 `template.html` 修改交互和样式，再生成 `index.html`。不要手动修改生成的数据副本。提交前测试展开/收起、搜索、课程链接、详情返回与缩放，核对全部课程覆盖。README 中现有导航保持可用。

Edit `template.html` for UI changes and regenerate `index.html`; do not manually edit generated data. Test expansion, search, links, return, zoom, and complete coverage before committing. Preserve the README navigation.

## 发布 / Publishing

经维护者授权，GitHub Pages 已从 `dev` 分支根目录公开发布，后续 `dev` 提交自动部署，HTTPS 已启用。`index.html` 将主页引导至 `resource-map/`。这不改变 `main`，也不表示可自动合并。

With the owner's authorization, GitHub Pages publishes the root of `dev` publicly and deploys subsequent `dev` commits automatically over HTTPS. The root `index.html` routes visitors to `resource-map/`. This does not change `main` or authorize automatic merges.

当前在线地址 / Live URL: https://xioacd99.github.io/study-is-wonderful/resource-map/

每次修改后确认 Pages 构建完成，并在真实公开页面测试代表交互；本地预览通过不等于远程部署成功。

After changes, verify the Pages build and representative interactions on the live site; a passing local preview is not proof of deployment.
