# 每日看点推送网页

这是一个部署在 GitHub Pages 上的每日资讯站点。

## 当前模式

项目已经支持全自动更新：

- GitHub Actions 每天定时运行
- 脚本自动抓取 RSS / Atom 新闻源
- 自动生成 `data/daily-brief.js`
- 自动提交到仓库
- GitHub Pages 自动发布最新页面

默认定时为每天北京时间早上 `07:15` 左右更新。

## 文件说明

- `index.html`：页面结构
- `styles.css`：视觉样式与响应式布局
- `app.js`：前端渲染逻辑
- `data/daily-brief.js`：自动生成的每日内容
- `config/feed_sources.json`：各板块的抓取源配置
- `scripts/generate_daily_brief.py`：抓取并生成日报数据的脚本
- `.github/workflows/daily-brief.yml`：GitHub Actions 定时任务

## 如何调整自动抓取

如果想替换资讯来源，主要改 `config/feed_sources.json`：

- 每个板块都可以配置多个 RSS / Atom 源
- 脚本会自动抓取、去重、按时间排序
- 每个板块默认生成 `2` 条重点内容和 `4` 条其他看点

## 手动触发更新

如果不想等到定时任务，也可以在 GitHub 仓库的 Actions 页面手动运行 `Daily Brief Update`。

## 本地测试

可以在项目根目录运行：

```bash
python3 scripts/generate_daily_brief.py
```

生成完成后刷新页面即可查看。
