> Active workflow: SVG-only references, dedicated complete other-track SVG palette, full Creative Director colour/layout decisions, and simple routes. See [SKILL.md](SKILL.md). Fixed-library and regular-rectangle examples below are historical, not new-run mandates.

<div align="center">

# FigFox-Gen-skill · V3

### 从 Methodology 和真实证据出发，生成一张科研图。

**同类图需求锚点 · 按需配图 · 有范围的风格借鉴 · SVG 来源配色 · 最终 PNG1**

[English](./README.md) · [安装](#安装) · [工作流程](#工作流程) · [案例](#案例) · [版本说明](references/versions.md)

</div>

## V3 · SVG-reference workflow / SVG 参考流程

Current version: **V3 (`v3.1.0`)**. / 当前版本：**V3 (`v3.1.0`)**。

- Inspect genuine vector SVG references and retain source provenance; report missing references rather than substitute raster images.
- Derive colours and their spatial relationships from one complete SVG; the Creative Director decides the final palette, composition and scientific detail.
- Place frames and plan straight or single smooth-curve routes together. Preserve genuine internal topology and keep text inside its parent region.
- Generate one PNG1 and inspect the actual image. Deterministic validation does not certify scientific or visual correctness.

真实 SVG 参考与来源记录 → 方法内容与叙事 → 完整 SVG 配色关系 → 创意师统筹配色、布局与真实内部拓扑 → 简单连线 → 单次 PNG1 → 实际图像检查。

See [the active workflow and schemas](references/svg-reference-workflow.md) and [SKILL.md](SKILL.md). Historical raster-library runs remain replayable; new runs use `svg-reference-v1`.

## Historical V2 architecture / 历史 V2 架构

The overview and V2 notes below document the previous workflow; they are retained for provenance and do not define V3 defaults. / 以下总览与 V2 说明保留历史来源，不代表 V3 默认流程。


Historical V2 workflow, generated with FigFox-Gen and reconstructed as editable SVG with FigFox. / 历史 V2 流程示例。

<img src="assets/generated-figures/figfox-gen-v2-architecture-editable.svg" alt="FigFox-Gen V2 architecture: evidence-grounded planning, single generation and author inspection / V2 架构总览" width="100%" />

[Methodology & generation record / 方法正文与生成记录](examples/v2-architecture/README.md)

[Editable SVG / 可编辑 SVG](assets/generated-figures/figfox-gen-v2-architecture-editable.svg) · [SVG preview / SVG 渲染预览](assets/generated-figures/figfox-gen-v2-architecture-editable.png) · [Source comparison & editability / 原图对照与可编辑性](examples/v2-architecture/editable/README.md)

此前 V2 的发布版本为 `v2.1.0`。它从科学 Methodology 出发，形成
有来源依据的绘图计划，交付一张栅格 PNG1。细节服务于方法的实际创新，辅助模块保持
一致层级；复用已核实的缓存，按视觉需求并行处理构件证据、参考特征与配色，再由
创意师确定完整矩形布局和精确连线几何。

默认视觉优先级为：完整矩形整体、规整分区、在框内尽可能单向传导。以白底、黑字和浅色为主；只对重要内容定向着色，普通支撑区域尽量留白。

V2 按所需粒度采用标准模型的经典结构画法，默认在普通背景上使用粗体标题，把
颜色重点留给科学内容；箭头采用统一的比例与风格，可使用粗杆、圆角或手绘线条。
按需选用且已获使用许可的内容插图，通过确定性贴入保留实际素材像素。只调用一次
图像模型生成布局；生成图或贴入素材后的合成图就是唯一最终 PNG1，由作者检查实际
像素后决定是否接受，不承诺可编辑 SVG。

查看 [此前的预览案例与检查记录](examples/v3-0-1/README.md)、此前的
[布局和连线对照](examples/regular-layout-trial/README.md)，以及
[直接视觉插图合同](references/direct-visual-insets.md)。旧的独立 V2 入口已移除，此前流程统一为默认 V2；V1 仍可通过 `$figfox-gen-v1` 明确调用。

## From generated figure to editable SVG / 从生成图到可编辑 SVG

After choosing a generated PNG, use the separate [FigFox skill](https://github.com/LawrenceRiver/FigFox#use-as-a-skill--作为-skill-使用) to reconstruct it as an editable SVG. Text, shapes and connectors remain native, while photos can be independently movable image elements.

生成 PNG 后，可调用独立的 [FigFox skill](https://github.com/LawrenceRiver/FigFox/tree/main/skills/figfox)，还原为可编辑 SVG：文字、图形、箭头保持原生元素，照片可独立移动与替换。

```bash
npx skills@latest add LawrenceRiver/FigFox --skill figfox
```

Use `$FigFox-Gen-skill` to create the figure, then `$figfox` to reconstruct the selected image; conversion is explicitly invoked rather than an automatic generation/repair loop.

先用 `$FigFox-Gen-skill` 生成，再用 `$figfox` 还原选定图片；两步分别调用，不自动进入重建或修图循环。

[Installation & workflow / 安装与流程](https://github.com/LawrenceRiver/FigFox/blob/main/docs/skill.md) · [Our editable V2 example / 本仓库 V2 可编辑示例](examples/v2-architecture/editable/README.md)

## V2 更新亮点

1. **不再出现过度配色的 Mermaid 式拓扑图。** 用主视觉参考统一图形、箭头和字体，让生成结果具有真正科研架构图的构造感。
2. **真正从简的逻辑布局。** 支持反 C、S 型和环形等排布，整体规整、饱满、对齐，尽可能单向传导，并逐条复查实际箭头的逻辑走向。
3. **反直觉的空间配色要求。** 相邻模块用相近浅色过渡，远处才拉开色彩差异，关键机制通常只保留一种强调色。
4. **图片插入开挂。** 音频波形、街景等外部图片可以按科学需要直接嵌入框架图，让具体内容进入方法表达。
5. **专家式文字压缩。** 默认靠近 100 词，删除重复解释和灰色微字，并参考同类论文的创新粒度决定自己的细节展开程度，框架创新讲框架、层级创新讲层级，用户可按需求调整。

## 案例

### Latent Diffusion

<img src="assets/generated-figures/v3-0-1/latent-diffusion.png" alt="Latent Diffusion generated figure / 科研图生成案例" width="100%" />

### MusiCoT

<img src="assets/generated-figures/v3-0-1/musicot.png" alt="MusiCoT generated figure / 科研图生成案例" width="100%" />

### AlphaFold 3

<img src="assets/generated-figures/v3-0-1/alphafold3.png" alt="AlphaFold 3 generated figure / 科研图生成案例" width="100%" />

[Source papers, Methodology and recorded checks / 原论文、方法正文与检查记录](examples/v3-0-1/README.md) · [Complete Methodology inputs / 完整方法输入](README.md#full-methodology-inputs)

These are preserved generated previews for author inspection. / 以上为保留的生成预览，需作者检查。

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

远端仓库更新不会自动改动本地安装。手动安装或固定在 V1 的副本，可用上面的 V2
安装命令切换来源；先保存本地自定义修改。固定版本与 V1/V2 共存方法见
[版本说明](references/versions.md)。在已安装的 Skill 目录检查文件完整性：

```bash
python scripts/check_installation.py
```

使用时提供 Methodology，可选附上参考图。一般请求默认使用 V2；保留的旧版名为
`figfox-gen-v1`，只在明确指定它时调用。

## 工作流程

```text
Methodology + 约两张实际查看过的同类论文图
  → 一次形成有来源依据的视觉需求锚点
  → 复用缓存，并行处理构件证据 / 有范围的风格特征 / 配色选择
  → 需求—画法对照表 + 科学关系图
  → 创意师：创新细节、完整画布网格、符号与走线
  → V2 确定性网格/路径预检 → 紧凑 Prompt 1
  → 一次布局图生成 → 按需确定性贴入内容素材 → 最终 PNG1 → 作者检查
```

1. **先确定需求。** 查看约两个同类论文案例，只保留 Methodology 确实需要的共同
   视觉惯例。准确保留科学模块、方向关系、原文支持的贡献和必要假设。
2. **按需并行。** 查找有效的构件画法、明确喜欢的参考图特征，并从 SVG 来源配色中
   选取适合本次任务的一组。参考图分别承担字体、线条或局部构造等明确角色，不能
   整体照搬构图、标签和颜色。每个已选视觉需求都有对应画法，不要求每个模块都搜图。
   复用已核实的缓存，只为明确未解决的需求补查；Methodology 中已命名的标准模型，
   在所选粒度使用有来源依据的经典结构画法，不凭空造符号，也不展开无关内部细节。
3. **先规划完整画布。** 创意师按创新点分配细节，在规则行列中安排所有内容与输出。
   标签使用简洁科学术语；索引采用真实上下标或经确认的符号别名，不允许可见下划线。
   输出也在同一矩形轮廓内，平级区域、边缘与间距保持对齐。标题默认是普通背景上的
   深色或主题色粗体字，不自动加彩色标题条；填色重点留给重要机制与科学内容。
   每次重新判断合适的配色，不把演示图的色相当成固定主题。
4. **先走线再生成。** 声明精确节点端口和路径点，由 V2 确定性预检检查计划几何。
   主线至多一个转弯，尽量消除交叉；不可避免的交叉必须明确使用连续跨线桥，或经
   批准且可区分的线色处理。先通过移动模块改善路径，再锁定计划；不能用文字遮住
   断裂线段。路径点规定的是中心线，不强制使用细黑线；整图及局部模型视图采用
   统一的箭头家族，保持杆身和箭头比例一致，并预留足够宽度。每条箭头都须从源边界
   连续到达目标箭头端，准确落到所指的过程子区域。
5. **只生成一次。** 将紧凑绘图清单交给图像模型，只生成一次布局图。无参考图模式下，
   清单为 `attachments: []`，图像生成调用省略 `referenced_image_paths` 和
   `num_last_images_to_include`。若选用了已检查且获准使用的直接内容素材，在预留插图
   区域确定性贴入实际文件，合成后为 PNG1；保留来源、裁剪、许可与放置记录。示意素材
   须保持示意身份，不能替代该方法的实验或结果证据。不使用插图时，生成图本身就是
   PNG1。常规流程交付这一张待检查的栅格 PNG1，不自动进入修图循环或增加模型调用。

文件、图关系、符号与几何验证检查的是声明的产物，**不能证明最终像素正确**。
实际输出的科学含义、符号、箭头端点、文字、布局与美观仍须逐项目检。
执行步骤见 [SKILL.md](SKILL.md)，产物和命令见
[紧凑生成合同](references/compact-generation.md)。旧版详细工作流保留在
[V1 标签文档](https://github.com/LawrenceRiver/FigFox-Gen-skill/blob/v1.0.0/README_ZH.md)。

## 历史 V1 案例

旧图与原路径保持不变，作为 V1 案例；历史配色预览展示的是旧版颜色库。

| V1 Methodology | 原 V1 结果 |
|---|---|
| Latent Diffusion | <img src="assets/generated-figures/02-latent-diffusion.png" alt="保留的 V1 Latent Diffusion 案例" width="620" /> |
| MusiCoT | <img src="assets/generated-figures/03-musicot.png" alt="保留的 V1 MusiCoT 案例" width="620" /> |
| AlphaFold 3 | <img src="assets/generated-figures/04-alphafold3.png" alt="保留的 V1 AlphaFold 3 案例" width="620" /> |

[V1 FigureBench/配色预览](assets/figurebench-palette-preview.png)

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
