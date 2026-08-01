#!/usr/bin/env python3
"""打印样式自检：验证 CLAUDE.md 要求的「打印时强制浅色主题、隐藏切换按钮、展开全部 quiz 答案」。

    python3 reference/check_print.py

需要 playwright（未安装时直接跳过，不算失败）：
    pip install playwright && playwright install chromium

为什么需要单独一个脚本：打印样式无法用静态检查覆盖，而它出过一次真实的 bug——
@media print 里的 `html` 选择器特异度 (0,0,1) 压不过系统深色块的
`html:not([data-theme="light"])` (0,1,1)，而 prefers-color-scheme 在打印时依然生效，
导致「系统深色 + 从未手动切换」这一默认状态下打印出白纸配浅灰字。
本脚本正是以那个场景作为主用例。
"""
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

PAGES = [
    "chapters/1-2-kv-cache.html",
    "chapters/2-4-capacity-planning.html",
    "chapters/6-5-degradation-fallback.html",
    "index.html",
    "glossary.html",
    "appendix-a-tooling.html",
]

PROBE = """() => ({
  ink: getComputedStyle(document.body).color,
  bg: getComputedStyle(document.body).backgroundColor,
  toggle: getComputedStyle(document.querySelector('.theme-toggle')).display,
  total: document.querySelectorAll('.quiz details').length,
  open: document.querySelectorAll('.quiz details[open]').length,
})"""

LIGHT_INK = "rgb(27, 39, 51)"     # --ink 浅色值 #1B2733
WHITE = "rgb(255, 255, 255)"


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("跳过：未安装 playwright（pip install playwright && playwright install chromium）")
        return 0

    errors = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for rel in PAGES:
            path = ROOT / rel
            if not path.exists():
                errors.append("{}: 文件不存在".format(rel))
                continue
            page = browser.new_page()
            # 关键场景：打印 + 系统深色 + 用户从未手动切换
            page.emulate_media(media="print", color_scheme="dark")
            page.goto(path.as_uri())
            page.wait_for_timeout(500)
            page.evaluate("() => window.dispatchEvent(new Event('beforeprint'))")
            page.wait_for_timeout(200)
            r = page.evaluate(PROBE)
            page.close()

            if r["ink"] != LIGHT_INK:
                errors.append("{}: 打印时正文色应为浅色主题的 {}，实际 {}"
                              .format(rel, LIGHT_INK, r["ink"]))
            if r["bg"] != WHITE:
                errors.append("{}: 打印时背景应为白色，实际 {}".format(rel, r["bg"]))
            if r["toggle"] != "none":
                errors.append("{}: 打印时主题切换按钮未隐藏".format(rel))
            if r["total"] and r["open"] != r["total"]:
                errors.append("{}: 打印时 quiz 答案未全部展开（{}/{}）"
                              .format(rel, r["open"], r["total"]))
            print("  {:44s} ink={} bg={} toggle={} quiz={}/{}".format(
                rel, r["ink"], r["bg"], r["toggle"], r["open"], r["total"]))
        browser.close()

    for e in errors:
        print("  ✗ " + e)
    print("\n{} 个错误".format(len(errors)))
    return 1 if errors else 0


if __name__ == "__main__":
    os.chdir(ROOT)
    sys.exit(main())
