# 学习星图验收 / Learning map acceptance

1. 在候选目录执行生成器、`--check` 和单元测试（见 [AGENTS.md](../AGENTS.md)）。不要用旧的已发布页面替代待发布版本。
2. 在支持 `sites-preview` 的托管 Linux 环境，用临时目录中的纯静态预览验证候选，不用部署或修改 GitHub Pages：

   ```sh
   stage="$(python3 tools/stage_resource_map_preview.py "$PWD")"
   sites-preview start "$stage"
   ```

   如检出目录的父目录不可写，可用 `--parent` 指定托管工作区内的可写目录。预览只包含原样复制的候选星图 HTML、图标和测试入口。打开命令返回的精确 URL，对照 `source-fingerprints.json` 与候选文件的 SHA-256。验收结束后执行 `sites-preview stop`。
3. 在真实浏览器中分别检查桌面和窄屏中文／英文：导航、图谱／列表、跨分类搜索、详情、资源链接和目录锚点；确认无控制台错误、无页面横向溢出。可使用预览入口的 390 × 844 iframe 检查响应式布局，记录 iframe 内部页面尺寸；不得把 iframe 检查称为触控验证。
4. 在同一候选的桌面未筛选状态分别截取两版，确认无鼠标指针、提示浮层或遮挡，且数量和语言与对应 README 一致。记录候选 Git SHA、生成的 HTML SHA-256 和验证结果。将实际检查过的 JPEG 保存为 `resource-map/preview-zh.jpg` 和 `resource-map/preview-en.jpg`；受支持的真实云浏览器和无头浏览器均可提供此证据。无法保存正确截图或未通过必要验收时，应暂缓推送。

The preview is for browser verification only; no publication or repository changes are performed by the helper. State whether narrow layout or physical touch was verified. Save screenshots with the browser runtime’s supported artifact path and compare the resulting JPEGs to the exact candidate.
