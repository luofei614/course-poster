# 课程海报生成器（course-poster）

用「先建 HTML 网页 → Chromium 渲染成高清 PNG」的方式，一键生成**竖版课程宣传海报**（1080 × 内容高度）。

核心特性：

- **灵活架构**——海报由可增删、排序的「内容块（blocks）」+ 参数化「主题（theme）」组合而成，不写死模板。
- **内容感知**——根据课程类型（AI / 金融 / 电商 / 管理 / 教育 / 商务）自动匹配背景情绪与装饰元素。
- **离线字体**——内置字体（86M）以 **Git 子模块** 形式按需拉取，主仓库保持轻量。
- **自动自检**——渲染时检测文字溢出 / 越界，按真实高度整张截图，避免底部被切。

---

## 目录

- [快速开始](#快速开始)
- [两步工作流（强制）](#两步工作流强制)
- [输入格式（JSON）](#输入格式json)
- [内容块（blocks）](#内容块blocks)
- [内容感知风格库](#内容感知风格库)
- [字体（Git 子模块）](#字体git-子模块)
- [字号规范](#字号规范)
- [渲染命令](#渲染命令)
- [目录结构](#目录结构)
- [调优经验与偏好](#调优经验与偏好)

---

## 快速开始

### 1. 克隆（含字体子模块）

```bash
git clone --recurse-submodules git@github.com:luofei614/course-poster.git
cd course-poster
```

> 若已克隆主仓库但字体未拉取：
> ```bash
> git submodule update --init --recursive
> ```
> 渲染脚本 `render.py` 也会在字体缺失时**自动执行上述初始化**，无需手动操作。

### 2. 安装依赖（Python）

本项目使用 Playwright（Chromium）做渲染。建议使用隔离的虚拟环境：

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install playwright jinja2 jsonschema pillow
playwright install chromium
```

### 3. 生成一张海报

```bash
python scripts/render.py --input examples/demo-input.json --out out.png --template purple-tech
```

产物：

- `out.png` —— 社群成品图（1080 × 真实高度）
- `out.html` —— 保留的网页源（改文案后直接重渲，无需重新设计）

---

## 两步工作流（强制）

**第一步（只出文字方案，不出图）**：读课程内容 → 推断 `topic` → 给出：

1. **排版设计**：用哪些 blocks、顺序、每块布局选项；
2. **元素想法**：背景情绪、装饰 motif、配色、字体；
3. **设计思路**：为什么这么搭、呼应什么。

**等用户确认后，再执行第二步。**

**第二步（确认后）**：构造输入 JSON → 运行 `render.py` 出 HTML + PNG，并**保留 HTML**（用户会反复要求改内容，直接改 HTML 局部重渲即可）。

> ⚠️ 务必「先方案、后出图」。直接出图而没先给文字方案，是已知错误用法。

---

## 输入格式（JSON）

顶层字段（全部可选，按需组合）：

| 字段 | 说明 |
|---|---|
| `topic` | 课程类型：`ai` / `finance` / `ecommerce` / `management` / `education` / `business`，驱动内容感知风格。 |
| `template` | 模板预设名（`presets/*.json`）：`purple-tech`(AI) / `blue-business`(商务) / `midnight-ecom`(电商) / `gold-wealth`(金融) / `green-classic`(管理)。选模板=套用它的主题+装饰。 |
| `theme` | 主题覆盖（深合并），可改 `background` / `decor` / `colors` / `font`。 |
| `blocks` | 内容块数组（见下）。给出则优先；否则用模板默认；再否则由扁平旧字段归一化。 |
| 扁平旧字段 | 兼容：`course_title` `subtitle` `teacher{name,role,titles,avatar}` `audience[]` `outline[]` `pain_point` `event{time,place,price}` `cta{qr,button}` `cutout`。 |

图片字段（`avatar` / `logo` / `qr` / `src` 等）填相对路径即可，脚本自动转 `file://` 绝对路径；缺图自动画虚线占位，**绝不报错**。

---

## 内容块（blocks）

每块由 `type` + `data` 组成。可增、删、排序、重复、空缺——不写某块，海报就没有该区（而非留空框）。

| type | data | 说明 |
|---|---|---|
| `logo_bar` | `brand`, `logo` | 顶部品牌条 |
| `hero` | `title`, `subtitle`, `tag` | 主标题 / 副标 / 标签 |
| `teacher` | `name`, `role`, `titles[]`, `avatar`, `layout`(`left`/`top`，头像默认 240px) | 讲师卡 |
| `text` | `label`, `body` | 痛点 / 引言段落 |
| `chips` | `label`, `items[]` | 适用人群标签 |
| `outline` | `label`, `phases[{title,desc}]`, `variant`(`list`/`card`) | 课程大纲 |
| `list` | `label`, `items[]` | 条目列表 |
| `image` | `src`, `caption` | 宣传图 |
| `cta` | `time`, `place`, `price`, `button`, `qr` | 报名区 + 二维码 |
| `divider` | `text` | 分隔 |
| `spacer` | `height` | 留白 |
| `stats` | `label`, `items[{value,label}]` | 数字卡 |
| `testimonial` | `quote`, `author` | 证言 |
| `timeline` | `label`, `items[{time,title,desc}]` | 时间轴 |
| `compare` | `left{title,items[]}`, `right{title,items[]}` | 双列对比 |

---

## 内容感知风格库

| topic | 背景情绪 | 装饰 motif | accent |
|---|---|---|---|
| `ai` | 深空紫蓝 | starfield 星轨 | 荧光青 `#22D3EE` |
| `finance` | 深蓝 | gold_lines 金线角标 | 金 `#D4AF37` |
| `ecommerce` | 午夜蓝 | dots 点阵 | 橙红 `#FF5A36` |
| `management` | 草绿 | waves 波纹 | 草绿 `#8FE3A8` |
| `education` | 清新蓝绿 | waves 波纹 | 蓝绿 `#7CE0C9` |
| `business` | 宝蓝 | dots 点阵 | 橙 `#FF8A3D` |

`topic` 由课程内容推断，用户也可用 `topic` / `theme` 字段覆盖。

装饰 motif 列表：`starfield` `circuit` `gradient_mesh` `gold_lines` `dots` `waves` `none`，以低透明度铺在背景，文字始终可读。**不支持上传背景图**（背景用渐变 + 小元素 / 粒子特效表达）。

---

## 字体（Git 子模块）

字体（86M）独立存放在**子模块** `assets/fonts/`，**主仓库不含字体文件**——克隆后按需拉取，避免仓库臃肿、推送缓慢。

- **字体内容**：微软雅黑（正文）、方正颜宋简体（标题书法感）、思源黑体简体（SourceHanSansCN）。
- 主题通过 `--font-body` / `--font-title` 引用，缺字体自动回退。
- 子模块仓库：`git@github.com:luofei614/course-poster-fonts.git`

### 克隆 / 拉取字体

```bash
# 克隆主仓库时一并拉取字体
git clone --recurse-submodules <主仓库URL>

# 已克隆主仓库后，再初始化字体子模块
git submodule update --init --recursive
```

> 渲染脚本 `render.py` 会在字体缺失时**自动执行上述初始化**；若环境无 git 或拉取失败，浏览器会回退系统字体，不报错。

---

## 字号规范

竖版 1080 海报字号阶梯（行业参考：标题 72–96px、副标/卖点 36–44px、正文/说明 28–32px、CTA 40–48px、辅助 24–28px；行距标题 1.1–1.2、正文 1.4–1.55）：

| 元素 | 字号 |
|---|---|
| 主标题 | 72px |
| 副标 / 区块标题 / 讲师名 | 40px |
| 正文 | 30px |
| 说明 | 26px |
| 小字 · 标签 | 30px |
| 占位提示 | 28px（二维码占位 26px） |
| CTA 按钮 | 22px |
| 数字卡 | 56px |

最小字不低于 24px。如需微调，全部集中在 `assets/blocks.css`。

---

## 渲染命令

```bash
python scripts/render.py --input data.json --out out.png [--template purple-tech] [--topic ai] [--cutout]
```

- `--input`：输入 JSON 路径（必填）
- `--out`：输出 PNG 路径（必填）
- `--template`：套用预设（`purple-tech` / `blue-business` / `midnight-ecom` / `gold-wealth` / `green-classic`）
- `--topic`：指定内容感知风格（`ai` / `finance` / `ecommerce` / `management` / `education` / `business`）
- `--cutout`：可选，对人物图做抠图

产物：`out.png`（社群成品）+ `out.html`（保留，供反复微调重渲）。

---

## 目录结构

```
course-poster/
├── templates/base.html        # 主题变量 + 渲染 blocks 的壳
├── assets/
│   ├── blocks.css             # 所有块样式（集中，字号在此调）
│   └── fonts/                 # 内置字体（Git 子模块，按需拉取）
├── scripts/
│   ├── blocks.py              # 块渲染器注册表
│   ├── decor.py               # 装饰 motif 库
│   ├── topic_styles.py        # 类型 → 视觉映射
│   ├── render.py              # 主编排
│   ├── screenshot.py          # 渲染 + 自检 + 截图
│   └── check.js               # 浏览器内几何自检
├── presets/*.json             # 模板预设（主题 + 装饰）
├── schemas/input.schema.json  # 输入 JSON Schema
├── examples/                  # 示例输入与成品图
├── SKILL.md                   # 技能定义（WorkBuddy 调用入口）
└── README.md
```

---

## 调优经验与偏好

多轮迭代沉淀的硬规则，后续做海报直接遵循：

- **字号铁律**：小字端要够大（最小 ≥24px），但**大标题保持 72px、CTA 按钮保持 22px，禁止过度放大**。
- **讲师头像默认 240px**：左侧 `layout:"left"` 下再大（>240）会挤占右侧姓名 / 职衔空间；想让头像更突出，改用 `layout:"top"` 头像置顶居中。
- **两步 SOP 强制**：先出文字版布局方案等确认，再出 HTML+PNG。
- **布局走纵向流**：内容块纵向排列，二维码等元素不二维自由摆放。
- **不支持上传背景图**：背景用渐变 + 装饰 motif 表达。

---

## License

本仓库含内置字体（微软雅黑 / 方正颜宋 / 思源黑体），字体文件版权归各自厂商所有，仅随 skill 离线使用，请遵守对应字体授权。代码部分可自由用于课程海报生成。
