#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按需 AI 抠图（rembg）。仅当用户明确要求抠图时才被调用。

首次运行会自动 pip 安装 rembg + onnxruntime 并下载模型（约 170MB），
之后复用本地缓存。输出带 alpha 通道的透明背景 PNG。
"""
import argparse
import subprocess
import sys
from pathlib import Path

from PIL import Image


def ensure_rembg():
    try:
        from rembg import remove  # noqa: F401
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--quiet", "rembg", "onnxruntime"]
        )
    from rembg import remove

    return remove


def cutout(src, out):
    remove = ensure_rembg()
    img = Image.open(src).convert("RGBA")
    res = remove(img)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    res.save(out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    print(cutout(args.src, args.out))


if __name__ == "__main__":
    main()
