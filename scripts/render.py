#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""课程海报生成主编排脚本（灵活架构版）。

用法：
  python render.py --input data.json --out poster.png [--template purple-tech]
                   [--topic ai] [--cutout]

流程：
  1. 解析输入（blocks / theme / topic / template / 扁平旧字段）
  2. 路径绝对化（图片 -> file:// 绝对路径）
  3. 主题解析：模板/类型 -> 基础主题 -> 输入 theme 覆盖；装饰 motif 同理
  4. blocks 解析：输入 blocks > 模板默认 > 扁平字段归一化
  5. 渲染 blocks + decor -> 填充 base.html -> 写出 HTML（保留）
  6. 截图 PNG（整张真实高度）+ 排版自检
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import jsonschema
from jinja2 import Environment, FileSystemLoader, select_autoescape

SKILL_DIR = Path(__file__).parent.parent
SCRIPTS = SKILL_DIR / "scripts"
SCHEMA = SKILL_DIR / "schemas" / "input.schema.json"
TPL_DIR = SKILL_DIR / "templates"
PRESETS = SKILL_DIR / "presets"
ASSETS_URL = ("file:///" + str(SKILL_DIR / "assets")).replace("\\", "/")

sys.path.insert(0, str(SCRIPTS))
import blocks as blocks_mod          # noqa: E402
import decor as decor_mod            # noqa: E402
from topic_styles import get as get_topic, DEFAULT_TOPIC  # noqa: E402

IMG_KEYS = {"avatar", "logo", "qr", "src", "avatar_path", "logo_path", "qrcode_path"}


def ensure_fonts():
    """字体以 Git Submodule 形式提供；本地缺失时自动拉取。失败不致命。"""
    fonts_css = SKILL_DIR / "assets" / "fonts" / "fonts.css"
    if fonts_css.exists():
        return
    print("提示：字体文件缺失，尝试自动拉取 Git 子模块（course-poster-fonts）...")
    try:
        r = subprocess.run(
            ["git", "submodule", "update", "--init", "--recursive"],
            cwd=str(SKILL_DIR), capture_output=True, text=True, timeout=300,
        )
        if r.returncode == 0 and fonts_css.exists():
            print("字体子模块已就绪。")
        else:
            print("自动拉取未成功（可手动执行：git submodule update --init --recursive）；"
                  "浏览器会回退系统字体。")
    except Exception as e:
        print("自动拉取字体失败：", e, "（可手动执行 git submodule update --init --recursive）")


def deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def resolve_images(obj, base_dir: Path):
    """递归把图片字段转为 file:// 绝对路径（基于输入 JSON 所在目录）。"""
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if k in IMG_KEYS and isinstance(v, str) and not v.startswith(("file://", "http://", "https://")):
                p = (base_dir / v).resolve()
                if p.exists():
                    obj[k] = "file:///" + str(p).replace("\\", "/")
                else:
                    obj[k] = ""  # 文件不存在 -> 交给块渲染器画占位
            else:
                resolve_images(v, base_dir)
    elif isinstance(obj, list):
        for it in obj:
            resolve_images(it, base_dir)


def normalize_flat(data: dict) -> list:
    """把旧的扁平字段（course_title/teacher/outline...）归一化为 blocks 数组。"""
    blocks = []
    if data.get("course_title") or data.get("subtitle"):
        hero = {"type": "hero", "title": data.get("course_title", ""), "subtitle": data.get("subtitle", "")}
        if data.get("tag"):
            hero["tag"] = data["tag"]
        blocks.append(hero)
    t = data.get("teacher")
    if t:
        blocks.append({
            "type": "teacher",
            "name": t.get("name", ""),
            "role": t.get("role", t.get("title", "")),
            "titles": t.get("titles", []),
            "avatar": t.get("avatar") or t.get("avatar_path", ""),
        })
    if data.get("pain_point"):
        blocks.append({"type": "text", "label": "课程痛点", "body": data["pain_point"]})
    if data.get("audience"):
        items = data["audience"] if isinstance(data["audience"], list) else [data["audience"]]
        blocks.append({"type": "chips", "label": "适合人群", "items": items})
    if data.get("outline"):
        phases = data["outline"] if isinstance(data["outline"], list) else []
        if phases and isinstance(phases[0], str):
            phases = [{"title": p, "desc": ""} for p in phases]
        blocks.append({"type": "outline", "label": "课程大纲", "phases": phases})
    if data.get("event") or data.get("cta"):
        cta = data.get("cta", {})
        ev = data.get("event", {})
        blocks.append({
            "type": "cta",
            "time": (ev or {}).get("time", data.get("time", "")),
            "place": (ev or {}).get("place", ""),
            "price": (ev or {}).get("price", ""),
            "button": (cta or {}).get("button", "立即报名"),
            "qr": (cta or {}).get("qr", (ev or {}).get("qr", "")),
        })
    return blocks


def resolve_theme(data: dict, template: str):
    preset = {}
    if template:
        pfile = PRESETS / f"{template}.json"
        if pfile.exists():
            preset = json.loads(pfile.read_text(encoding="utf-8"))
        else:
            print("警告：模板不存在", template, "，回退到 topic 解析")
            template = None

    topic = data.get("topic") or (preset.get("topic") if template else None) or DEFAULT_TOPIC
    theme = get_topic(topic)

    # 输入 theme 覆盖（深合并）
    theme = deep_merge(theme, data.get("theme") or {})
    # 预设额外 theme 覆盖
    if preset.get("theme"):
        theme = deep_merge(theme, preset["theme"])

    decor = (data.get("theme") or {}).get("decor") \
        or preset.get("decor") or theme.get("decor") or "dots"
    return theme, decor, topic


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--template")
    ap.add_argument("--topic")
    ap.add_argument("--cutout", action="store_true")
    args = ap.parse_args()

    ensure_fonts()  # 字体子模块按需拉取（缺失时）

    in_path = Path(args.input).resolve()
    base_dir = in_path.parent
    data = json.loads(in_path.read_text(encoding="utf-8"))
    if args.topic:
        data["topic"] = args.topic
    if args.template:
        data["template"] = args.template

    # 1. 校验（宽松）
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        print("输入校验警告:", e.message)
    except Exception:
        pass

    # 2. 图片路径绝对化
    resolve_images(data, base_dir)

    # 3. 抠图（可选，默认不抠；仅 cutout=true 才触发）
    if (args.cutout or data.get("cutout")) and data.get("teacher", {}).get("avatar"):
        av = data["teacher"]["avatar"]
        out_av = str(SKILL_DIR / "build" / "avatar_cutout.png")
        r = subprocess.run([sys.executable, str(SCRIPTS / "cutout.py"), "--src", av, "--out", out_av],
                           capture_output=True, text=True)
        if r.returncode == 0:
            data["teacher"]["avatar"] = "file:///" + out_av.replace("\\", "/")
        else:
            print("抠图失败，回退原图:", r.stderr[-200:])

    template = data.get("template")
    theme, decor, topic = resolve_theme(data, template)

    # 4. blocks 解析
    blocks = data.get("blocks")
    if not blocks and template:
        preset = json.loads((PRESETS / f"{template}.json").read_text(encoding="utf-8"))
        blocks = preset.get("blocks")
    if not blocks:
        blocks = normalize_flat(data)
    if not blocks:
        print("错误：未提供 blocks，且无可用内容字段（course_title/teacher/outline...）")
        sys.exit(1)

    # 5. 渲染
    blocks_html = blocks_mod.render_blocks(blocks)
    decor_html = decor_mod.render(decor, theme["colors"]["accent"], theme["colors"]["primary"])

    env = Environment(
        loader=FileSystemLoader(str(TPL_DIR)),
        autoescape=select_autoescape([]),  # 内容已自行转义，关闭自动转义
    )
    tpl = env.get_template("base.html")
    hero_title = ""
    for b in blocks:
        if b.get("type") == "hero":
            hero_title = b.get("title", "")
            break
    html_out = tpl.render(
        title=hero_title or data.get("course_title", "课程海报"),
        ASSETS=ASSETS_URL,
        theme=theme,
        decor_html=decor_html,
        blocks_html=blocks_html,
    )

    out_png = Path(args.out).resolve()
    out_html = out_png.with_suffix(".html")
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html_out, encoding="utf-8")
    print("HTML 已保留:", out_html)

    # 6. 截图 + 自检
    from screenshot import render as shoot
    issues, real_h = shoot(str(out_html), str(out_png), fix=True, rounds=5)
    report = {"passed": len(issues) == 0, "issues": issues, "width": 1080, "height": real_h,
              "topic": topic, "decor": decor}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["passed"] else 2)


if __name__ == "__main__":
    main()
