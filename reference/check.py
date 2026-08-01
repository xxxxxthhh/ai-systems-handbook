#!/usr/bin/env python3
"""构建自检：验证每章满足 CLAUDE.md 的格式约定。

  python3 reference/check.py            # 检查全部已完稿章节
  python3 reference/check.py 1 2        # 只检查 Part 1、Part 2

reference/ 目录不发布，本脚本仅供构建期使用。
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS = os.path.join(ROOT, "chapters")
SECTION_IDS = ["concept", "case", "tools", "quiz"]

errors = []
warnings = []
stubs = []


def err(f, msg):
    errors.append("{}: {}".format(f, msg))


def check_chapter(path, name):
    html = open(path, encoding="utf-8").read()

    if "Draft 待撰写" in html:
        stubs.append(name)
        return

    # Part 0 是导读而非正式章节，不适用四要素与锚点约定
    guide = name.startswith("0-")

    # 章节四要素
    if "<figure" not in html:
        err(name, "缺少 <figure> 原创图表")
    if 'class="quiz"' not in html:
        if not guide:
            err(name, "缺少 quiz 区块")
    else:
        n_q = html.count("<details>")
        if n_q < 3:
            warnings.append("{}: quiz 只有 {} 题".format(name, n_q))
        if html.count("<summary>") != html.count('class="qtype"'):
            err(name, "有 quiz 题目缺少题型标签 .qtype")
        if html.count("<details>") != html.count('class="answer"'):
            err(name, "有 quiz 题目缺少参考答案")
    if 'class="case"' not in html:
        if not guide:
            err(name, "缺少真实案例区块 .case")
    elif 'class="src"' not in html:
        err(name, "案例缺少来源标注 .src")

    # 锚点 id（glossary 的首次出现链接依赖它们）
    if not guide:
        for sid in SECTION_IDS:
            if 'id="{}"'.format(sid) not in html:
                err(name, '缺少锚点 id="{}"'.format(sid))

    # 工具层必须有截至日期
    n_tool = html.count('class="toolbox"')
    n_date = html.count('class="date"')
    if n_tool != n_date:
        err(name, "工具层区块 {} 个但日期戳 {} 个".format(n_tool, n_date))
    if n_tool == 0 and not guide:
        warnings.append("{}: 没有工具层侧栏".format(name))

    # 共享资源引用
    if "assets/handbook.css" not in html:
        err(name, "未引用共享样式 handbook.css")
    if "assets/theme.js" not in html:
        err(name, "未引用 theme.js（dark mode）")
    if "theme-toggle" not in html:
        err(name, "缺少主题切换按钮")

    # SVG 内不能用 HTML 内联标签：会被解析成未知 SVG 元素，文字直接不显示
    for svg in re.findall(r"<svg\b.*?</svg>", html, flags=re.S):
        bad_tags = re.findall(r"</?(b|i|em|strong|br|code|span)\b", svg)
        if bad_tags:
            err(name, "SVG 内出现 HTML 标签（文字将无法渲染）: {}".format(sorted(set(bad_tags))))

    # 禁止写死色值（@media print 的强制浅色块是唯一例外，章节页不含该块）
    body = re.sub(r"@media\s+print\s*\{.*?\n\s*\}\s*\n", "", html, flags=re.S)
    hard = re.findall(r'(?:fill|stroke|color|background)\s*[:=]\s*"?#[0-9a-fA-F]{3,8}', body)
    if hard:
        err(name, "SVG/组件中写死色值: {}".format(hard[:4]))


def check_links():
    pages = {}
    for d in [ROOT, CHAPTERS]:
        for f in os.listdir(d):
            if f.endswith(".html"):
                pages[os.path.join(d, f)] = None
    for path in pages:
        base = os.path.dirname(path)
        name = os.path.relpath(path, ROOT)
        for href in re.findall(r'href="([^"]+)"', open(path, encoding="utf-8").read()):
            if href.startswith(("http", "#", "mailto:")):
                continue
            target = href.split("#")[0]
            if not target:
                continue
            if not os.path.exists(os.path.normpath(os.path.join(base, target))):
                err(name, "死链: {}".format(href))


def main():
    only = sys.argv[1:]
    names = sorted(f for f in os.listdir(CHAPTERS) if f.endswith(".html"))
    for f in names:
        if only and f.split("-")[0] not in only:
            continue
        check_chapter(os.path.join(CHAPTERS, f), f)
    check_links()

    done = len(names) - len(stubs)
    print("章节 {}/{} 已完稿".format(done, len(names)))
    if stubs:
        print("待撰写 ({}): {}".format(len(stubs), ", ".join(s[:-5] for s in stubs)))
    for w in warnings:
        print("  ⚠ " + w)
    for e in errors:
        print("  ✗ " + e)
    print("\n{} 个错误 / {} 个警告".format(len(errors), len(warnings)))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
