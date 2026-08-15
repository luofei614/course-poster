#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 Chromium 渲染填充后的 HTML，注入 check.js 做排版自检，输出高清 PNG。

流程：打开页面 -> 注入 check.js -> 循环自检/自动修复（最多 rounds 轮）
      -> 量出海报真实高度 -> 整张截图（DPR=2 高清，按真实高度，不再写死 1920）
      -> 缩放为 1080 x 真实高度 -> 打印自检报告 JSON。

注意：海报高度由内容决定（min-height:1920，内容多则更高），截图必须按真实高度
截取，否则底部会被切掉。
"""
import argparse
import io
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright
from PIL import Image

SCRIPT_DIR = Path(__file__).parent
CHECK_JS = (SCRIPT_DIR / "check.js").read_text(encoding="utf-8")

VIEW_W = 1080          # 海报固定宽度
VIEW_H = 1920          # 初始视口高度（仅用于布局计算，不代表截取高度）
OUT_W = 1080           # 输出固定宽度


def render(html_path: str, out_path: str, fix: bool = True, rounds: int = 5):
    html_path = Path(html_path).resolve()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--font-render-hinting=none"])
        page = browser.new_page(
            viewport={"width": VIEW_W, "height": VIEW_H}, device_scale_factor=2
        )
        page.goto("file://" + str(html_path))
        # 关键修复：等待本地 @font-face 字体全部加载完成再截图。
        # 否则 font-display:swap 会在字体就绪前用 fallback 渲染中文，
        # 无头环境里中文可能显示不出来（表现为"大标题掉字"）。
        try:
            page.evaluate("document.fonts.ready")
        except Exception:
            pass
        page.wait_for_timeout(300)
        page.evaluate(CHECK_JS)

        issues = []
        for _ in range(rounds):
            issues = page.evaluate("window.__audit()")
            if not issues:
                break
            if fix:
                page.evaluate("window.__fix()")
            else:
                break
        # 末轮再确认一次
        issues = page.evaluate("window.__audit()")

        # 量出海报真实高度（.poster-canvas 的 min-height=1920，内容多则更高）
        real_h = page.evaluate(
            "Math.ceil("
            "((document.querySelector('.poster-canvas')||document.body)"
            ".getBoundingClientRect().height))"
        ) or VIEW_H
        # 取整，且不低于视口高度，避免极小值
        real_h = max(int(real_h), VIEW_H)

        # 整张截图：full_page 按内容真实高度捕获，避免底部被切（取字节流，不落盘临时文件）
        png_bytes = page.screenshot(full_page=True)
        browser.close()

    # 高清源（DPR=2）-> 目标尺寸：宽固定 1080，高取真实内容高度
    with Image.open(io.BytesIO(png_bytes)) as im:
        im = im.resize((OUT_W, real_h), Image.LANCZOS)
        im.save(out_path, "PNG")
    return issues, real_h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--no-fix", action="store_true", help="关闭自动修复，仅检测")
    ap.add_argument("--rounds", type=int, default=5)
    args = ap.parse_args()

    issues, real_h = render(args.html, args.out, fix=not args.no_fix, rounds=args.rounds)
    report = {"passed": len(issues) == 0, "issues": issues, "width": OUT_W, "height": real_h}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["passed"] else 2)


if __name__ == "__main__":
    main()
