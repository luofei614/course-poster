---
name: 课程海报生成器
description: 用「先建 HTML 网页 → HTML 转 PNG」的方式生成竖版课程宣传海报。灵活架构：模板=预设JSON，海报=主题(背景/配色/字体/装饰)+内容块数组+内容感知风格库。支持 AI/金融/电商/管理/教育等多主题自动匹配视觉元素。触发词：课程海报、讲师海报、培训宣传图、课程招生图、知识付费海报、讲座海报、讲师宣传图。
version: 2.3.0
---

# 课程海报生成器

先建 HTML 网页，再用 Chromium 渲染成高清竖版 PNG（1080×内容高度）。核心特性：**灵活**——海报由可增删排序的「内容块」+ 参数化「主题」组成；**内容感知**——根据课程类型自动匹配背景情绪与装饰元素。

## 两步工作流（强制）

**第一步（只出文字方案，不出图）**：读课程内容 → 推断 `topic` → 给出：
1. 排版设计：用哪些 blocks、顺序、每块布局选项；
2. 元素想法：背景情绪、装饰 motif、配色、字体；
3. 设计思路：为什么这么搭、呼应什么。
**等用户确认后，再执行第二步。**

**第二步（确认后）**：构造输入 JSON → 运行 `render.py` 出 HTML + PNG，并**保留 HTML**（用户会反复要求改内容，直接改 HTML 局部重渲即可）。

## 输入（JSON）

顶层字段（全部可选，按需组合）：
- `topic`：课程类型，`ai/finance/ecommerce/management/education/business`，驱动内容感知风格（见下）。
- `template`：模板预设名（= `presets/*.json`）：`purple-tech`(AI) / `blue-business`(商务) / `midnight-ecom`(电商) / `gold-wealth`(金融) / `green-classic`(管理)。选模板=套用它的主题+装饰。
- `theme`：主题覆盖（深合并），可改 `background`(渐变/纯色) / `decor` / `colors` / `font`。
- `blocks`：内容块数组（见下）。给出则优先；否则用模板默认；再否则由扁平旧字段归一化。
- 扁平旧字段兼容：`course_title` `subtitle` `teacher{name,role,titles,avatar}` `audience[]` `outline[]` `pain_point` `event{time,place,price}` `cta{qr,button}` `cutout`。

图片字段（`avatar`/`logo`/`qr`/`src` 等）填相对路径即可，脚本自动转 `file://` 绝对路径；缺图自动画虚线占位，**绝不报错**。

## 内容块（blocks，`type` + `data`）

可增、删、排序、重复、空缺——不写某块，海报就没有该区（而非留空框）。

| type | 数据 | 说明 |
|---|---|---|
| `logo_bar` | `brand`,`logo` | 顶部品牌条 |
| `hero` | `title`,`subtitle`,`tag` | 主标题/副标/标签 |
| `teacher` | `name`,`role`,`titles[]`,`avatar`,`layout`(left/top，头像默认 240px) | 讲师卡（左图右文 / 置顶居中） |
| `text` | `label`,`body` | 痛点/引言段落 |
| `chips` | `label`,`items[]` | 适用人群标签 |
| `outline` | `label`,`phases[{title,desc}]`,`variant`(list/card) | 课程大纲 |
| `list` | `label`,`items[]` | 条目列表 |
| `image` | `src`,`caption` | 宣传图 |
| `cta` | `time`,`place`,`price`,`button`,`qr` | 报名区+二维码 |
| `divider` | `text` | 分隔 |
| `spacer` | `height` | 留白 |
| `stats` | `label`,`items[{value,label}]` | 数字卡 |
| `testimonial` | `quote`,`author` | 证言 |
| `timeline` | `label`,`items[{time,title,desc}]` | 时间轴 |
| `compare` | `left{title,items[]}`,`right{title,items[]}` | 双列对比 |

## 内容感知风格库（主题 → 视觉）

| topic | 背景情绪 | 装饰 motif | accent |
|---|---|---|---|
| `ai` | 深空紫蓝 | starfield 星轨/神经节点 | 荧光青 #22D3EE |
| `finance` | 深蓝 | gold_lines 金线角标 | 金 #D4AF37 |
| `ecommerce` | 午夜蓝 | dots 点阵 | 橙红 #FF5A36 |
| `management` | 草绿 | waves 波纹 | 草绿 #8FE3A8 |
| `education` | 清新蓝绿 | waves 波纹 | 蓝绿 #7CE0C9 |
| `business` | 宝蓝 | dots 点阵 | 橙 #FF8A3D |

`topic` 由课程内容推断，用户也可用 `topic`/`theme` 字段覆盖。装饰 motif 列表：`starfield` `circuit` `gradient_mesh` `gold_lines` `dots` `waves` `none`，以低透明度铺在背景，文字始终可读。**不支持上传背景图**（按用户要求，背景用渐变+小元素/粒子特效表达）。

## 字体（Git Submodule，按需拉取）

字体（86M）独立存放在**子模块** `assets/fonts/`，**主仓库不含字体文件**——克隆后按需拉取，避免仓库臃肿、推送缓慢。

- 字体内容：微软雅黑（正文）、方正颜宋简体（标题书法感）、思源黑体简体（SourceHanSansCN）。
- 主题通过 `--font-body`/`--font-title` 引用，缺字体自动回退。
- 子模块仓库：`git@github.com:luofei614/course-poster-fonts.git`

### 克隆 / 拉取字体

克隆主仓库时**一并拉取字体**：
```bash
git clone --recurse-submodules <主仓库URL>
```
已克隆主仓库后，再初始化字体子模块：
```bash
git submodule update --init --recursive
```
> 渲染脚本 `render.py` 会在字体缺失时**自动执行上述初始化**，无需手动操作；若环境无 git 或拉取失败，浏览器会回退系统字体，不报错。

字号阶梯（v2.4 仅小字端再放大，其余不变）：主标题 72px / 副标 40px / 区块标题 40px / 讲师名 40px / 正文 30px / 说明 26px / 小字·标签 30px / 占位提示 28px(二维码占位26) / CTA 按钮 22px / 数字卡 56px。行业参考：标题 72–96px、副标/卖点 36–44px、正文/说明 28–32px、CTA 40–48px、辅助 24–28px；行距标题 1.1–1.2、正文 1.4–1.55。最小字不低于 24px。如需微调，全部集中在 `assets/blocks.css`。

## 调优经验与用户偏好（已验证）

> 本轮多轮迭代沉淀的硬规则，后续做海报直接遵循，无需再追问。

- **字号铁律**：小字端要够大（最小 **≥24px**），但**大标题保持 72px、CTA 按钮保持 22px，禁止过度放大**。飞哥原话反馈：88px 标题 / 44px 按钮"太大了"。完整阶梯见本节上方「字体」（v2.3）。
- **讲师头像默认 240px**：飞哥连续要求放大（156→200→240）。左侧 `layout:"left"` 下再大（>240）会挤占右侧姓名/职衔空间；想让头像更突出，改用 `layout:"top"` 头像置顶居中、文字在下方居中。
- **两步 SOP 强制**：先出**文字版布局方案**（排版设计 + 元素想法 + 设计思路）等用户确认，再出 HTML+PNG（见顶部「两步工作流」）。飞哥曾指出"没先出文字方案就出图"——务必先方案后出图。
- **布局走纵向流**：内容块纵向排列，每块自带布局选项（如 teacher 的 left/top）；二维码等元素**不二维自由摆放**。
- **不支持上传背景图**：背景用渐变 + 装饰 motif（starfield/dots/waves…）表达。
- **竖版 1080 海报行业字号参考**：标题 72–96 / 副标·卖点 36–44 / 正文·说明 28–32 / CTA 40–48 / 辅助 24–28；行距标题 1.1–1.2、正文 1.4–1.55。

## 自检机制（防掉字/越界）

每个文本容器带 `data-expected` 属性，渲染时注入 `check.js` 检测横向/纵向溢出与越界：L1 自动缩放字号(×0.92，最多5轮)+放开高度；L2 仍失败输出问题报告 JSON。`screenshot.py` 按海报**真实高度**整张截取（不再写死 1920，避免底部被切），输出宽固定 1080。

## 渲染

```
python scripts/render.py --input data.json --out out.png [--template purple-tech] [--topic ai] [--cutout]
```
产物：`out.png`（社群成品）+ `out.html`（保留，供反复微调重渲）。

## 目录

```
templates/base.html      # 主题变量 + loop 渲染 blocks 的壳
assets/blocks.css        # 所有块样式（集中）
assets/fonts/            # 内置字体（Git 子模块，按需拉取；见「字体」节）
scripts/blocks.py        # 块渲染器注册表
scripts/decor.py         # 装饰 motif 库
scripts/topic_styles.py  # 类型→视觉映射
scripts/render.py        # 主编排
scripts/screenshot.py    # 渲染+自检+截图
scripts/check.js         # 浏览器内几何自检
presets/*.json           # 模板预设（主题+装饰）
schemas/input.schema.json
```
