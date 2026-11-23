> Active workflow: SVG-only references, dedicated complete other-track SVG palette, full Creative Director colour/layout decisions, and simple routes. See [SKILL.md](SKILL.md). Fixed-library and regular-rectangle examples below are historical, not new-run mandates.

<div align="center">

# FigFox-Gen-skill · V3

### 从 Methodology 和真实证据出发，生成一张科研图。

**同类图需求锚点 · 按需配图 · 有范围的风格借鉴 · SVG 来源配色 · 最终 PNG1**

[English](./README.md) · [安装](#安装) · [工作流程](#工作流程) · [案例](#案例) · [版本说明](references/versions.md)

</div>

## V3 · SVG-reference workflow / SVG 参考流程

<img src="examples/v3.1/architecture/editable/final.svg" alt="FigFox-Gen V3: Methodology and SVG evidence feed Creative Director decisions, preflight, one generation and pixel inspection" width="100%" />

[Editable SVG / 可编辑 SVG](examples/v3.1/architecture/editable/final.svg) · [PNG preview / PNG 预览](examples/v3.1/architecture/editable/final.png) · [Reconstruction & run illustrations / 重建与运行记录插图](examples/v3.1/architecture/editable/README.md)

[Full V3 Methodology / 完整方法正文](examples/v3.1/architecture/input/methodology.md) · [Generated with our own skill / 自己的 skill 生成记录](examples/v3.1/architecture/README.md) · [Prompt / 提示词](examples/v3.1/architecture/prompt-1/prompt.md)

Current version: **V3 (`v3.1.0`)**. / 当前版本：**V3 (`v3.1.0`)**。

- Inspect genuine vector SVG references and retain source provenance; report missing references rather than substitute raster images.
- Derive colours and their spatial relationships from one complete SVG; the Creative Director decides the final palette, composition and scientific detail.
- Place frames and plan straight or single smooth-curve routes together. Preserve genuine internal topology and keep text inside its parent region.
- Generate one PNG1 and inspect the actual image. Deterministic validation does not certify scientific or visual correctness.

真实 SVG 参考与来源记录 → 方法内容与叙事 → 完整 SVG 配色关系 → 创意师统筹配色、布局与真实内部拓扑 → 简单连线 → 单次 PNG1 → 实际图像检查。

See [the active workflow and schemas](references/svg-reference-workflow.md) and [SKILL.md](SKILL.md). New runs use `svg-reference-v1`.

## From generated figure to editable SVG / 从生成图到可编辑 SVG

After choosing a generated PNG, use the separate [FigFox skill](https://github.com/LawrenceRiver/FigFox#use-as-a-skill--作为-skill-使用) to reconstruct it as an editable SVG. Text, shapes and connectors remain native, while photos can be independently movable image elements.

生成 PNG 后，可调用独立的 [FigFox skill](https://github.com/LawrenceRiver/FigFox/tree/main/skills/figfox)，还原为可编辑 SVG：文字、图形、箭头保持原生元素，照片可独立移动与替换。

```bash
npx skills@latest add LawrenceRiver/FigFox --skill figfox
```

Use `$FigFox-Gen-skill` to create the figure, then `$figfox` to reconstruct the selected image; conversion is explicitly invoked rather than an automatic generation/repair loop.

先用 `$FigFox-Gen-skill` 生成，再用 `$figfox` 还原选定图片；两步分别调用，不自动进入重建或修图循环。

[Installation & workflow / 安装与流程](https://github.com/LawrenceRiver/FigFox/blob/main/docs/skill.md) · [Our editable V3 overview / 本仓库 V3 可编辑总览](examples/v3.1/architecture/editable/README.md)

## Examples · V3 / V3 新案例

Complete updated Methodology inputs and recorded checks are linked below. / 以下包含更新后的完整 Methodology 与实际检查记录。

### Qwen-Music

<img src="examples/v3.1/qwen-music/png1.png" alt="Qwen-Music generated with FigFox-Gen V3" width="100%" />

[Full Methodology / 完整方法正文](examples/v3.1/qwen-music/input/methodology.md) · [Prompt, sources & inspection / 提示词、来源与检查](examples/v3.1/qwen-music/README.md)

Known deviations: external connector prose and incomplete internal melody continuation. / 已记录：连线说明出框，旋律到语义输出连接仍不完整。

### AlphaGenome

<img src="examples/v3.1/alphagenome/png1.png" alt="AlphaGenome generated with FigFox-Gen V3" width="100%" />

[Full Methodology / 完整方法正文](examples/v3.1/alphagenome/input/methodology.md) · [Prompt, sources & inspection / 提示词、来源与检查](examples/v3.1/alphagenome/README.md)

Known deviation: some connector labels remain outside frames. Readouts are schematic. / 已记录：少量连线标签出框；读出均为示意。

### World Models · MDN-RNN

<img src="examples/v3.1/world-models/png1.png" alt="World Models · MDN-RNN generated with FigFox-Gen V3" width="100%" />

[Full Methodology / 完整方法正文](examples/v3.1/world-models/input/methodology.md) · [Prompt, sources & inspection / 提示词、来源与检查](examples/v3.1/world-models/README.md)

Known deviation: mild shading/gradients. / 已记录：局部有轻微渐变。

[All V3 run packages / 全部 V3 运行记录](examples/v3.1/README.md)

### 可选科研海报支线

[PosFox Gen](skills/posfox-gen/SKILL.md) 已作为附加 Skill 收进本仓库。**只有用户明确要求制作科研海报或学术海报时才进入这条支线**；论文 PDF、大幅面参考、提及或否定海报都不构成触发条件。其余仍按科研论文图、方法图或架构图处理。

也可以只安装海报生成附加包：

```bash
npx skills@latest add LawrenceRiver/FigFox-Gen-skill --full-depth --skill posfox-gen
```

明确要求 `$posfox-gen` 制作科研海报，并提供论文 PDF 与可选参考。它在生成 PNG 后结束，不自动进入 HTML/SVG 重建，也不需要旧的独立生成仓库。

## 安装

[skills CLI](https://github.com/vercel-labs/skills) 需要 Node.js 22.20 或以上。
安装默认版本，并在提示中选择 Codex：

```bash
npx skills@latest add LawrenceRiver/FigFox-Gen-skill --skill FigFox-Gen-skill
```

默认安装到当前项目；加 `-g` 可用于所有项目，加 `-a codex` 可直接选择 Codex。
已经安装的副本需要主动更新：

```bash
npx skills@latest check
npx skills@latest update FigFox-Gen-skill
```

远端仓库更新需要主动更新本地安装；更新前先保存本地自定义修改。在已安装的 Skill 目录检查文件完整性：

```bash
python scripts/check_installation.py
```

使用时提供 Methodology，可选附上 SVG 参考图。一般请求默认使用当前 V3 工作流。

## Choose a workflow / 选择工作流

```mermaid
flowchart LR
  subgraph V1["V1 · Original / 初版"]
    a["Contexts 1–3<br/>FigureBench + palette"]
  end
  subgraph V2["V2 · Visual planning / 视觉规划"]
    b["Needs → drawing correspondence<br/>Grid + route preflight"]
  end
  subgraph V3["V3 · Current / 当前"]
    c["Genuine SVG evidence<br/>Director-owned colour + simple routes"]
  end
  a --> b --> c
```

| Workflow / 工作流 | Install source / 安装来源 | Call / 调用 |
|---|---|---|
| V1 | [v1.0.0](https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v1.0.0) | `$figfox-gen-v1` |
| V2 | [v2.1.0](https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v2.1.0) | `$FigFox-Gen-skill` after installing V2 / 安装 V2 后调用 |
| V3 | [main](https://github.com/LawrenceRiver/FigFox-Gen-skill) | `$FigFox-Gen-skill` (default / 默认) |

<details>
<summary>Install a specific workflow / 安装指定工作流</summary>

```bash
# V1
npx skills@latest add https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v1.0.0 --skill figfox-gen-v1

# V2
npx skills@latest add https://github.com/LawrenceRiver/FigFox-Gen-skill/tree/v2.1.0 --skill FigFox-Gen-skill

# V3 (current)
npx skills@latest add LawrenceRiver/FigFox-Gen-skill --skill FigFox-Gen-skill
```

V2 and V3 share the same skill name: install the selected version before calling it. / V2 与 V3 使用同一 skill 名称，先安装所选版本，再调用；不通过名称同时区分两个版本。

</details>

## 工作流程

```text
Methodology + 用户要求
  → 真实 SVG 证据 + 已确定的科学内容与叙事
  → 创意师：配色与留白 → 框架与简单连线 → 准确文字与局部构造
  → 来源/科学关系/几何/符号预检 → 紧凑图像提示词
  → 一次图像调用 → PNG1 → 实际像素检查 + 偏差记录
```

1. **先确定科学内容。** Methodology 决定模块、依赖关系与贡献。优先检查真实 SVG 论文图，只保留有用构造，记录参考缺口及需求—观察画法—本图表达的对应关系。
2. **收集完整风格与配色证据。** 从另一赛道的一张完整 SVG 中记录真实色值、相邻和分离关系、强调与留白。新流程不从固定色板库选配色；本地 PNG 只作为原 SVG 的显示或传输衍生图。
3. **创意师统筹决策。** 创意师结合方法内容与完整参考，先决定来源配色及衍生色，再共同安排内容大小合适的框架与简单走线，最后填入准确文字、符号和局部构造。保留真实内部拓扑；普通框通常一个输入和一个输出，必要多端口须有科学依据。
4. **编译与预检。** 检查 SVG 与哈希、来源配色决策、科学关系、符号及几何。路径只用直线或必要的单条简单曲线；复杂绕线通过移动或重组框架解决。将科学不变量、构造要求和实际参考附件编译为紧凑提示词。
5. **单次生成与实际检查。** 调用一次图像模型，交付 PNG1，检查真实图像，保留方法正文、来源、创意决策、计划、提示词与已知偏差。产物校验不能证明视觉或科学正确，不自动修图或还原可编辑 SVG。

[完整 V3 Methodology](examples/v3.1/architecture/input/methodology.md) · [当前 skill](SKILL.md) · [SVG 合同](references/svg-reference-workflow.md) · [紧凑交付](references/compact-generation.md)

## 内置参考包

安装包内有恰好 30 张完整、已索引且有署名的 FigureBench 开发集图片，以及
**14 组命名配色**。普通用户无需下载 FigureBench；不使用官方测试集图片。
FigureBench 提供几何与布局证据，不提供实际配色；FigFoxBench 是另一个独立来源。
署名信息见 [图片索引](assets/figurebench-references/index.json)。来源可访问或属于
某数据集并不等于允许重新分发；用户图片和权限未确定的素材留在本地。

## 维护者

`scripts/curate_figurebench_reference_pack.py` 用于维护参考包，
`scripts/figure_workflow.py` 用于运行产物和验证。

```bash
python scripts/check_installation.py
python -m unittest discover -s tests -v
```

检查通过不能替代像素目检。固定安装、迁移与旧版保留策略见
[版本说明](references/versions.md)。
