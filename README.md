# 每日看点推送网页

这是一个纯静态网页项目，适合做每日资讯首页。

## 文件说明

- `index.html`：页面结构
- `styles.css`：视觉样式与响应式布局
- `app.js`：根据数据生成栏目与资讯卡片
- `data/daily-brief.js`：每日内容数据

## 如何更新内容

每日只需要修改 `data/daily-brief.js`：

- 更新 `publishDate`
- 修改 `highlights`
- 修改各个 `sections` 下的 `items`
- 每条资讯都可以配置：
  - `priority`
  - `time`
  - `title`
  - `summary`
  - `impact`
  - `source`
  - `url`

## 本地打开

直接双击 `index.html` 即可查看，或者在当前目录启动一个静态服务。
