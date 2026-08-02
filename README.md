# AI 系统工程手册 · AI Systems Engineering Handbook

双语 HTML 电子书（中文为主，英文术语原文标注），面向应用层 AI 工程师。
每章 = 核心概念 + 真实案例 + 原创图表 + 章末自测。纯静态 HTML/CSS/JS，无框架依赖。

**状态**：全书已完稿——6 个 Part、30 个章节页、3 篇附录。术语与自测题数量由附录生成器按当前章节自动汇总。

本地预览直接用浏览器打开 `index.html` 即可（无需构建步骤）。

## 目录结构

```
├── index.html                     # 全书目录
├── chapters/                      # 30 个章节页（part-章-slug.html）
├── appendix-a-tooling.html        # 附录 A 工具层速查
├── glossary.html                  # 附录 B 术语表　　（自动生成）
├── appendix-c-interview-index.html# 附录 C 面试题索引（自动生成）
├── assets/
│   ├── handbook.css               # 共享样式：浅/深两套 CSS 变量 + 全部组件 + 打印样式
│   ├── theme.js                   # dark mode 切换（localStorage 持久化，head 内同步加载）
│   └── quiz.js                    # quiz「展开全部/收起全部」控件
└── reference/                     # 构建期资源，不发布
    ├── chapter-1-2-kv-cache-sample.html  # 人工审定样章（格式基准，已转为 1.2 章页）
    ├── sources.md                 # 引用溯源台账（写作红线的核对依据）
    ├── check.py                   # 构建自检
    └── gen_appendix.py            # 附录 B/C 生成器
```

## 维护命令

```bash
python3 reference/check.py
```

构建自检：逐章验证章节四要素（图表 / 案例含来源 / quiz 含题型与答案 / 工具层带日期戳）、
五个锚点 id、共享资源引用、SVG 内是否误用 HTML 标签、是否写死色值，以及全站死链。
可加 Part 号只检查部分章节，如 `python3 reference/check.py 3 4`。

```bash
python3 reference/check_print.py
```

打印样式自检（需 playwright，未安装时自动跳过）：在「打印媒体 + 系统深色 + 用户从未手动切换」
这一最容易出问题的场景下，验证强制浅色、隐藏切换按钮、quiz 答案全部展开。
**打印样式无法被静态检查覆盖，而它出过一次真实 bug**，因此单独成一项。

```bash
python3 reference/gen_appendix.py
```

从 `chapters/` 重新生成附录 B 与附录 C。术语的「首次出现章节」与面试题题面均从章节 HTML
提取，**改动章节后重跑本命令即可保持附录同步**；术语的中文释义维护在该脚本的 `GLOSS` 字典中
（新增术语但未写释义时脚本会报错并列出缺失项）。

## 约定速查

| 文件 | 作用 |
|------|------|
| `CLAUDE.md` | 项目约定（必读）：语言规则、章节四要素、原理/工具分层、dark mode、写作红线 |
| `SKELETON.md` | 全书章节级骨架（已定稿） |
| `reference/sources.md` | 每一处论文/公开报告引用的条件与核验状态 |

三条最容易违反的约定：

1. **知识分层**——会过期的内容（工具名、参数、价格）只能进虚线侧栏或附录 A，且必须带
   「截至 YYYY-MM」日期戳；正文只写 18 个月后依然成立的原理层内容，且**正文不依赖侧栏**。
2. **写作红线**——不虚构论文数据。引用数字必须可溯源，且**连同实验条件一起写出**
   （哪个模型、什么基线、什么负载）；自行推导的估算须写明假设；案例只用公开可查信息或匿名化实践。
3. **颜色一律走 CSS 变量**——包括 SVG 内部的填充与文字（实心块上的文字用 `var(--on-fill)`）。
   唯一例外是 `handbook.css` 中 `@media print` 强制浅色的那一组值。`check.py` 会检查这一点。

## 部署

纯静态站点，直接部署到 GitHub Pages / Cloudflare Pages 即可，无需构建步骤。
页面支持打印导出 PDF（打印时强制浅色主题、隐藏交互按钮、自动展开全部 quiz 答案）。
