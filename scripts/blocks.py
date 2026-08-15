# -*- coding: utf-8 -*-
"""内容块渲染器：每个 type 一段函数，返回 HTML 片段（已转义、带 data-expected 自检属性）。

块类型（14+）：
  logo_bar / hero / teacher / text / chips / outline / list / image /
  cta / divider / spacer / stats / testimonial / timeline / compare

所有用户输入文本都经 esc() 转义；文本容器带 data-expected 供 check.js 几何防掉字检测。
"""
import html
from typing import Any, Dict, List


def esc(s: Any) -> str:
    """HTML 文本转义（用于标签内容）。"""
    return html.escape("" if s is None else str(s), quote=False)


def eattr(s: Any) -> str:
    """HTML 属性值转义（用于 data-expected="..." 等属性）。"""
    return html.escape("" if s is None else str(s), quote=True)


def _img(url: str, cls: str, ph_text: str, ph_cls: str = "ph") -> str:
    """有 url 用 <img>，否则用虚线占位 div。"""
    if url and (url.startswith("file://") or url.startswith("http://") or url.startswith("https://")):
        return f'<img class="{cls}" src="{esc(url)}" alt="">'
    return f'<div class="{cls} {ph_cls}">{esc(ph_text)}</div>'


# ---------------- 各块渲染器 ----------------

def b_logo_bar(d):
    brand = esc(d.get("brand", ""))
    img = _img(d.get("logo"), "logo-img" if d.get("logo") else "", "LOGO")
    # logo_bar 内 img 用 .b-logo img 样式，占位用 .ph
    if d.get("logo"):
        inner = f'<img src="{esc(d["logo"])}" alt="">'
    else:
        inner = '<div class="ph">LOGO</div>'
    return f'<div class="b-logo" data-expected="{eattr(brand or "logo_bar")}">' \
           f'{inner}<span class="brand">{brand}</span></div>'


def b_hero(d):
    title = esc(d.get("title", ""))
    sub = esc(d.get("subtitle", ""))
    tag = esc(d.get("tag", ""))
    out = f'<div class="b-hero">'
    if title:
        out += f'<h1 class="title" data-expected="{eattr(title)}">{title}</h1>'
    if sub:
        out += f'<div class="subtitle" data-expected="{eattr(sub)}">{sub}</div>'
    if tag:
        out += f'<div class="tag" data-expected="{eattr(tag)}">{tag}</div>'
    out += '</div>'
    return out


def b_teacher(d):
    name = esc(d.get("name", ""))
    role = esc(d.get("role", ""))
    layout = "avatar_top" if d.get("layout") == "top" else "avatar_left"
    titles = d.get("titles") or []
    titles_html = "<ul class=\"titles\">" + "".join(
        f"<li data-expected=\"{eattr(t)}\">{esc(t)}</li>" for t in titles) + "</ul>"
    if d.get("avatar"):
        av = f'<img class="avatar" src="{esc(d["avatar"])}" alt="">'
    else:
        av = '<div class="avatar ph">讲师\n头像</div>'
    name_html = f'<div class="name" data-expected="{eattr(name)}">{name}</div>' if name else ""
    role_html = f'<div class="role" data-expected="{eattr(role)}">{role}</div>' if role else ""
    return f'<div class="b-teacher {layout}">{av}' \
           f'<div>{name_html}{role_html}{titles_html}</div></div>'


def b_text(d):
    label = esc(d.get("label", ""))
    body = esc(d.get("body", ""))
    label_html = f'<div class="label" data-expected="{eattr(label)}">{label}</div>' if label else ""
    return f'<div class="b-text card">{label_html}' \
           f'<div class="body" data-expected="{eattr(body)}">{body}</div></div>'


def b_chips(d):
    label = esc(d.get("label", "适用人群"))
    items = d.get("items") or []
    chips = "".join(f'<span class="chip" data-expected="{eattr(i)}">{esc(i)}</span>' for i in items)
    return f'<div class="b-chips"><div class="sec-title" data-expected="{eattr(label)}">{label}</div>' \
           f'<div class="items">{chips}</div></div>'


def b_outline(d):
    label = esc(d.get("label", "课程大纲"))
    variant = d.get("variant", "list")  # list | card
    phases = d.get("phases") or []
    cls = "b-outline variant-card" if variant == "card" else "b-outline"
    rows = []
    for idx, ph in enumerate(phases, 1):
        pt = esc(ph.get("title", ""))
        pd = esc(ph.get("desc", ""))
        rows.append(
            f'<div class="phase"><div class="num">{idx}</div>'
            f'<div><div class="pt" data-expected="{eattr(pt)}">{pt}</div>'
            f'<div class="pd" data-expected="{eattr(pd)}">{pd}</div></div></div>'
        )
    return f'<div class="{cls}"><div class="sec-title" data-expected="{eattr(label)}">{label}</div>' \
           f'<div class="phases">{"".join(rows)}</div></div>'


def b_list(d):
    label = esc(d.get("label", ""))
    items = d.get("items") or []
    lis = "".join(f'<li data-expected="{eattr(i)}">{esc(i)}</li>' for i in items)
    label_html = f'<div class="sec-title" data-expected="{eattr(label)}">{label}</div>' if label else ""
    return f'<div class="b-list">{label_html}<ul>{lis}</ul></div>'


def b_image(d):
    cap = esc(d.get("caption", ""))
    if d.get("src"):
        inner = f'<img src="{esc(d["src"])}" alt="">'
    else:
        inner = '<div class="ph">宣传图</div>'
    cap_html = f'<div class="cap" data-expected="{eattr(cap)}">{cap}</div>' if cap else ""
    return f'<div class="b-image">{inner}{cap_html}</div>'


def b_cta(d):
    time = esc(d.get("time", ""))
    price = esc(d.get("price", ""))
    place = esc(d.get("place", ""))
    btn = esc(d.get("button", "立即报名"))
    qr = d.get("qr", "")
    info = '<div class="info">'
    if time:
        info += f'<div class="line">时间：<span class="hl" data-expected="{eattr(time)}">{time}</span></div>'
    if place:
        info += f'<div class="line">地点：<span class="hl" data-expected="{eattr(place)}">{place}</span></div>'
    if price:
        info += f'<div class="line">费用：<span class="hl" data-expected="{eattr(price)}">{price}</span></div>'
    info += f'<span class="btn" data-expected="{eattr(btn)}">{btn}</span></div>'
    if qr:
        qr_html = f'<img class="qr" src="{esc(qr)}" alt="">'
    else:
        qr_html = '<div class="qr ph">扫码\n报名</div>'
    return f'<div class="b-cta card">{info}{qr_html}</div>'


def b_divider(d):
    text = esc(d.get("text", ""))
    return f'<div class="b-divider" data-expected="{eattr(text or "·")}">' \
           f'<span class="ln"></span><span class="dot"></span>' \
           f'<span>{text}</span><span class="dot"></span><span class="ln"></span></div>'


def b_spacer(d):
    h = int(d.get("height", 30))
    return f'<div class="b-spacer" style="height:{h}px"></div>'


def b_stats(d):
    label = esc(d.get("label", ""))
    items = d.get("items") or []
    cards = []
    for it in items:
        v = esc(it.get("value", ""))
        l = esc(it.get("label", ""))
        cards.append(
            f'<div class="stat"><div class="v" data-expected="{eattr(v)}">{v}</div>'
            f'<div class="l" data-expected="{eattr(l)}">{l}</div></div>'
        )
    label_html = f'<div class="sec-title" data-expected="{eattr(label)}">{label}</div>' if label else ""
    return f'<div class="b-stats">{label_html}<div class="items">{"".join(cards)}</div></div>'


def b_testimonial(d):
    quote = esc(d.get("quote", ""))
    author = esc(d.get("author", ""))
    return f'<div class="b-testimonial card"><div class="quote" data-expected="{eattr(quote)}">{quote}</div>' \
           f'<div class="author" data-expected="{eattr(author)}">— {author}</div></div>'


def b_timeline(d):
    label = esc(d.get("label", "发展历程"))
    items = d.get("items") or []
    rows = []
    for it in items:
        t = esc(it.get("time", ""))
        h = esc(it.get("title", ""))
        dd = esc(it.get("desc", ""))
        rows.append(
            f'<div class="row"><div class="axis"><div class="node"></div><div class="bar"></div></div>'
            f'<div class="body"><div class="t" data-expected="{eattr(t)}">{t}</div>'
            f'<div class="h" data-expected="{eattr(h)}">{h}</div>'
            f'<div class="d" data-expected="{eattr(dd)}">{dd}</div></div></div>'
        )
    return f'<div class="b-timeline"><div class="sec-title" data-expected="{eattr(label)}">{label}</div>' \
           f'<div class="items">{"".join(rows)}</div></div>'


def b_compare(d):
    left = d.get("left", {})
    right = d.get("right", {})
    lt = esc(left.get("title", "A"))
    rt = esc(right.get("title", "B"))
    litems = "".join(f'<li data-expected="{eattr(i)}">{esc(i)}</li>' for i in (left.get("items") or []))
    ritems = "".join(f'<li data-expected="{eattr(i)}">{esc(i)}</li>' for i in (right.get("items") or []))
    return f'<div class="b-compare"><div class="cols">' \
           f'<div class="col left"><div class="ct" data-expected="{eattr(lt)}">{lt}</div><ul>{litems}</ul></div>' \
           f'<div class="col right"><div class="ct" data-expected="{eattr(rt)}">{rt}</div><ul>{ritems}</ul></div>' \
           f'</div></div>'


REGISTRY = {
    "logo_bar": b_logo_bar,
    "hero": b_hero,
    "teacher": b_teacher,
    "text": b_text,
    "chips": b_chips,
    "outline": b_outline,
    "list": b_list,
    "image": b_image,
    "cta": b_cta,
    "divider": b_divider,
    "spacer": b_spacer,
    "stats": b_stats,
    "testimonial": b_testimonial,
    "timeline": b_timeline,
    "compare": b_compare,
}


def render_block(b: Dict[str, Any]) -> str:
    t = b.get("type")
    fn = REGISTRY.get(t)
    if not fn:
        # 未知块：安全跳过，避免渲染崩溃
        return f'<!-- unknown block type: {esc(t)} -->'
    return fn(b)


def render_blocks(blocks: List[Dict[str, Any]]) -> str:
    return "\n".join(render_block(b) for b in (blocks or []))
