# -*- coding: utf-8 -*-
"""课程类型 -> 视觉处理映射（内容感知风格库）。

渲染时：读课程内容推断 topic（或用户用 input.topic 覆盖），自动选取
background 情绪 / 配色 accent / 装饰 motif / 字体。这就是“AI 课自动加 AI 元素”的实现。
"""
from typing import Dict, Any

SANS = '"Microsoft YaHei", "Source Han Sans SC", "Noto Sans CJK SC", sans-serif'
SERIF = '"FZYanSJW", "Source Han Sans SC", "Microsoft YaHei", serif'

TOPIC_STYLES: Dict[str, Dict[str, Any]] = {
    "ai": {
        "background": "linear-gradient(160deg, #0B1026 0%, #1B1B6E 55%, #0A0E2E 100%)",
        "colors": {"primary": "#6D5BFF", "accent": "#22D3EE", "text": "#EAF2FF", "muted": "#9FB3D1"},
        "decor": "starfield",
        "font": {"body": SANS, "title": SANS},
    },
    "finance": {
        "background": "linear-gradient(160deg, #0F1B3D 0%, #13294B 100%)",
        "colors": {"primary": "#D4AF37", "accent": "#E8C766", "text": "#F5EFE0", "muted": "#B9C2D0"},
        "decor": "gold_lines",
        "font": {"body": SANS, "title": SERIF},
    },
    "ecommerce": {
        "background": "linear-gradient(160deg, #0B1B3A 0%, #122046 100%)",
        "colors": {"primary": "#FF5A36", "accent": "#FF8A3D", "text": "#FFFFFF", "muted": "#C9D2E0"},
        "decor": "dots",
        "font": {"body": SANS, "title": SANS},
    },
    "management": {
        "background": "linear-gradient(160deg, #0E5A2E 0%, #1B7A3F 100%)",
        "colors": {"primary": "#1FA15A", "accent": "#8FE3A8", "text": "#F3F8EF", "muted": "#CFE3C7"},
        "decor": "waves",
        "font": {"body": SANS, "title": SERIF},
    },
    "education": {
        "background": "linear-gradient(160deg, #0E6E6E 0%, #149E8E 100%)",
        "colors": {"primary": "#14B8A6", "accent": "#7CE0C9", "text": "#EAFBF7", "muted": "#BFE9DF"},
        "decor": "waves",
        "font": {"body": SANS, "title": SERIF},
    },
    "business": {
        "background": "linear-gradient(160deg, #16306B 0%, #1E3A8A 100%)",
        "colors": {"primary": "#2D6CDF", "accent": "#FF8A3D", "text": "#F2F6FF", "muted": "#C2CFE3"},
        "decor": "dots",
        "font": {"body": SANS, "title": SANS},
    },
}

DEFAULT_TOPIC = "business"


def get(topic: str) -> Dict[str, Any]:
    return TOPIC_STYLES.get(topic) or TOPIC_STYLES[DEFAULT_TOPIC]


def list_topics() -> list:
    return list(TOPIC_STYLES.keys())
