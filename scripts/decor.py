# -*- coding: utf-8 -*-
"""背景装饰库：返回铺在海报底层的 SVG 字符串（低透明度、不阻挡文字）。

motif 列表：starfield / circuit / gradient_mesh / gold_lines / dots / waves / none
颜色由主题 accent / primary 驱动，保证装饰与配色统一。
"""
import random


W, H = 1080, 2000


def _wrap(inner: str) -> str:
    return (
        f'<svg viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMin slice" '
        f'xmlns="http://www.w3.org/2000/svg">'
        f'<defs>'
        f'<radialGradient id="gm1" cx="50%" cy="35%" r="70%">'
        f'<stop offset="0%" stop-color="white" stop-opacity="0.5"/>'
        f'<stop offset="100%" stop-color="white" stop-opacity="0"/></radialGradient>'
        f'</defs>{inner}</svg>'
    )


def starfield(accent, primary):
    rnd = random.Random(2026)
    stars = []
    for _ in range(140):
        x = rnd.randint(0, W)
        y = rnd.randint(0, H)
        r = rnd.uniform(0.6, 2.4)
        op = rnd.uniform(0.3, 0.9)
        stars.append(f'<circle cx="{x}" cy="{y}" r="{r:.1f}" fill="#ffffff" opacity="{op:.2f}"/>')
    # 神经节点连线
    nodes = [(rnd.randint(60, W - 60), rnd.randint(60, H - 60)) for _ in range(14)]
    lines = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if ((nodes[i][0] - nodes[j][0]) ** 2 + (nodes[i][1] - nodes[j][1]) ** 2) ** 0.5 < 320:
                lines.append(
                    f'<line x1="{nodes[i][0]}" y1="{nodes[i][1]}" x2="{nodes[j][0]}" y2="{nodes[j][1]}" '
                    f'stroke="{accent}" stroke-width="0.8" opacity="0.28"/>'
                )
    dots = "".join(
        f'<circle cx="{x}" cy="{y}" r="3.2" fill="{accent}" opacity="0.55"/>' for (x, y) in nodes
    )
    return _wrap("".join(stars) + "".join(lines) + dots)


def circuit(accent, primary):
    rnd = random.Random(7)
    lines = []
    y = 120
    while y < H:
        x = 0
        seg = []
        while x < W:
            nx = x + rnd.choice([80, 140, 200])
            ny = y + rnd.choice([-40, 0, 40])
            seg.append(f'<path d="M{x} {y} L{nx} {ny}" stroke="{accent}" stroke-width="1" '
                       f'fill="none" opacity="0.18"/>')
            x, y = nx, ny
        lines.extend(seg)
        y += rnd.randint(160, 240)
    nodes = []
    rnd2 = random.Random(99)
    for _ in range(60):
        cx, cy = rnd2.randint(20, W - 20), rnd2.randint(20, H - 20)
        nodes.append(f'<rect x="{cx-3}" y="{cy-3}" width="6" height="6" fill="{accent}" opacity="0.4"/>')
    return _wrap("".join(lines) + "".join(nodes))


def gradient_mesh(accent, primary):
    blobs = []
    centers = [(200, 300), (900, 500), (500, 1100), (150, 1600), (950, 1750)]
    cols = [accent, primary, accent, primary, accent]
    for (cx, cy), c in zip(centers, cols):
        blobs.append(
            f'<circle cx="{cx}" cy="{cy}" r="420" fill="{c}" opacity="0.14"/>'
        )
    glow = '<rect x="0" y="0" width="1080" height="2000" fill="url(#gm1)" opacity="0.06"/>'
    return _wrap(glow + "".join(blobs))


def gold_lines(accent, primary):
    lines = []
    for i in range(5):
        y0 = 200 + i * 360
        lines.append(
            f'<line x1="0" y1="{y0}" x2="1080" y2="{y0 + 160}" stroke="{accent}" '
            f'stroke-width="1" opacity="0.22"/>'
        )
    # 角标
    bracket = (
        '<path d="M40 40 L40 110 M40 40 L110 40" stroke="{a}" stroke-width="3" fill="none" opacity="0.5"/>'
        '<path d="M1040 1960 L1040 1890 M1040 1960 L970 1960" stroke="{a}" stroke-width="3" fill="none" opacity="0.5"/>'
    ).format(a=accent)
    return _wrap("".join(lines) + bracket)


def dots(accent, primary):
    rnd = random.Random(42)
    out = []
    step = 46
    for y in range(80, H, step):
        for x in range(40, W, step):
            op = rnd.uniform(0.06, 0.16)
            out.append(f'<circle cx="{x}" cy="{y}" r="2.2" fill="#ffffff" opacity="{op:.2f}"/>')
    return _wrap("".join(out))


def waves(accent, primary):
    paths = []
    for k in range(3):
        y0 = 1500 + k * 130
        d = f"M0 {y0}"
        x = 0
        while x < W:
            d += f" Q {x+135} {y0-60} {x+270} {y0} T {x+540} {y0}"
            x += 540
        paths.append(f'<path d="{d}" stroke="{accent}" stroke-width="2" fill="none" opacity="{0.22 - k*0.04}"/>')
    return _wrap("".join(paths))


def none(accent, primary):
    return _wrap("")


REGISTRY = {
    "starfield": starfield,
    "circuit": circuit,
    "gradient_mesh": gradient_mesh,
    "gold_lines": gold_lines,
    "dots": dots,
    "waves": waves,
    "none": none,
}


def render(motif: str, accent: str, primary: str) -> str:
    fn = REGISTRY.get(motif, dots)
    return fn(accent, primary)
