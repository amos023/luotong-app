# 落筒录入

桶装落筒录入与满卷时间计算工具。页面为单文件 HTML，Android 端由 WebView 容器承载，仓库同时保留 APK 产物与打包脚本。

## 在线地址

| 版本 | 链接 | 说明 |
| --- | --- | --- |
| 现版 | https://amos023.github.io/luotong-app/ | 对应根目录 `index.html`，随每次提交自动更新 |
| 初版存档 | https://amos023.github.io/luotong-app/branch/ | 对应 `branch/index.html`，固定为 v0.6 初版优化版「满卷时间计算表」页面 |

`branch/` 是历史存档，内容是 v0.6 初版优化版；除非手动覆盖 `branch/index.html`，该地址不会跟随现版更新。两个地址共用同一域名，`localStorage` 互通，初版页面本身不保存数据，互不干扰。

## 目录结构

- `index.html`：现版页面，站点根地址直接指向它
- `branch/index.html`：初版存档页，对应 `/branch/` 地址
- `app/`：历史安装包，命名 `落筒录入_v<版本号>.apk`
- `文档/`：使用说明，含 HTML 与 Markdown 两份
- `源码/`：Android 容器、图标生成与 APK 打包脚本

## 安装包

`app/` 内保留各版本 APK，签名密钥保持不变以支持覆盖升级。包名 `io.github.mcool.luotong`。

发布新页面只需替换根目录 `index.html`；替换前建议先把旧版本另存到 `文档/` 之外的历史目录留档，避免丢失可对照版本。
