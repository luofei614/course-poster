#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成演示用的占位图：讲师头像占位 + 二维码占位。"""
from pathlib import Path
from PIL import Image, ImageDraw
import random

SKILL = Path(__file__).resolve().parent.parent
OUT = SKILL / "assets" / "placeholders"
OUT.mkdir(parents=True, exist_ok=True)

# 讲师头像占位（浅色背景 + 人像剪影）
W, H = 600, 760
img = Image.new("RGB", (W, H), (214, 232, 244))
d = ImageDraw.Draw(img)
d.ellipse([110, 430, 490, 860], fill=(150, 182, 205))   # 肩
d.ellipse([195, 140, 405, 370], fill=(235, 205, 175))   # 头
img.save(OUT / "avatar_placeholder.png")

# 二维码占位（白底 + 随机黑块 + 三个定位角）
random.seed(7)
S, cell = 240, 12
q = Image.new("RGB", (S, S), "white")
qd = ImageDraw.Draw(q)
for y in range(0, S, cell):
    for x in range(0, S, cell):
        if random.random() > 0.5:
            qd.rectangle([x, y, x + cell, y + cell], fill="black")


def corner(ox, oy):
    qd.rectangle([ox, oy, ox + 3 * cell, oy + 3 * cell], fill="black")
    qd.rectangle([ox + cell, oy + cell, ox + 2 * cell, oy + 2 * cell], fill="white")
    qd.rectangle([ox + cell + 4, oy + cell + 4, ox + 2 * cell - 4, oy + 2 * cell - 4], fill="black")


corner(0, 0)
corner(S - 3 * cell, 0)
corner(0, S - 3 * cell)
q.save(OUT / "qr_placeholder.png")

print("placeholders generated:", OUT)
