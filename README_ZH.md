<div align="center">

# GenLikeScientificSVG

### 让图像模型生成有科研结构的论文图，而不是猜出来的 PPT。

**科研论文图生成 · 网页领域绘图惯例 · 受控配色 · 拓扑优先的图像生成**

联网搜索领域共识 SVG 表达，结合 FigureBench 精选 RAG 和颜色审美，教会图像生成模型生成真实科研架构图。

[English](./README.md) · [工作流程](#工作流程) · [实跑记录](#实跑记录) · [研究说明](#研究说明)

</div>

将它作为 Skill 安装；安装器会让你选择 Codex、Claude Code 或其他受支持智能体。

```bash
npx skills@latest add LawrenceRiver/genlike-scientific-svg-skill
```

然后直接交给智能体一个 Figure Brief：想法、较长的方法原文、结果、论文片段、草图或参考图均可。内置的开场提示会明确启动一项**带完整文字的科研图像生成任务**。

## 工作流程

核心原则是**先规划、再图像生成**：可并行获取的证据同时进行，随后在图像模型出图前冻结唯一的拓扑合同与配色合同。

| 阶段 | 它做什么 |
| --- | --- |
| 领域视觉搜索 | 筛选至少 3–4 张高质量论文 HTML/SVG/PDF 图，判断构图、层级、构件惯例、留白、重点与科研感。它提供领域画法与创新证据，不提供最终配色。 |
| FigureBench 语义–结构 RAG | 返回方法语义、图类型、拓扑、分组、布局、文字密度与几何语法的少量摘要。它不是像素相似检索，也不把完整数据集送给模型。 |
| 拓扑与配色规划 | 把冗余方法文字压缩为模块、标签、箭头、层级和阅读顺序；每次仅冻结一组批准的颜色，来源是本地库或不相关领域的 SVG。 |
| 直接图像生成 | 将精确标签、关系、布局、参考摘要与 HEX 颜色角色写入 Image Generation Contract，图像模型直接生成最终光栅科研图，文字也必须直接生成。不会把渲染后的 SVG 当作生成前输入。 |
| 一次检查 | 只检查一次文字、碰撞、箭头、层级、密度和配色使用；只允许一次局部修补，不能推翻重画。 |

它故意结合**两种参考**：同领域高审美图教会模型“这个概念通常怎样画”，FigureBench 教会模型可复用的科研几何和结构；配色则独立隔离，绝不复制同领域论文的色组。

## 实跑记录

下面是仓库的真实测试输入，而不是复刻原论文图。每个案例以引用论文中的较长 Methodology 原文为输入，让 Skill 生成一张全新的解释性架构图；输出不得复制源论文图。

| 案例 | Methodology 输入 | 生成目标 |
| --- | --- | --- |
| Latent Diffusion · 视觉生成 | [Method §3](./README.md#latent-diffusion--visual-generation) | 清楚区分感知压缩、latent 去噪、条件控制和解码。 |
| MusiCoT · 音乐生成 | [Method §4](./README.md#musicot--music-generation) | 展示音频片段、CLAP thoughts、粗到细 RVQ 与双重采样。 |
| AlphaFold 3 · 生物分子结构 | [Network architecture and training](./README.md#alphafold-3--biomolecular-structure) | 展示 pair/single representation、Pairformer、坐标扩散与结构输出。 |

英文 README 保留了三段实际 Methodology 原文、来源、精确标签合同与最终结果位置，避免双份拷贝造成测试输入漂移。

## 研究说明

我是正在从事计算机视觉学习和研究的学生，目前关注科研论文图生成，也有数学建模竞赛和日常科研制图的实际经验。我的研究涉及 diffusion、VLM，以及它们究竟能在多大程度上理解并可控地呈现一个科研图需求。

我发现不少工作把重点放在生成中间 SVG 或结构描述；但中间结构本身并不会自动让图像生成模型真正理解这张图。图像模型本来擅长视觉规划，却常会改错文字、漂移颜色、生成不专业且不像科研矢量图的视觉语言，并让后续还原或可编辑化变得困难。

因此，这个 Skill 把关键控制前置：领域绘图惯例、语义–结构 FigureBench RAG、隔离的配色合同、精确文字和拓扑合同，然后才直接调用图像生成模型。目标不是泛化的“AI 图”，而是一张原创、可读、符合严肃科研论文视觉纪律的图。生成结果在作为科学证据使用前仍必须由作者独立核验。

## 鸣谢

项目的本地语义–结构检索受到 FigureBench 启发。运行时的网页参考阶段可以检查 Nature Portfolio、Science、Cell 及各领域公开论文图页，从中学习绘图惯例，或提取与当前主题无关的颜色组。仓库不再分发源论文图、临时裁图、FigureBench 原始图片或原始色卡；同领域参考图也绝不提供最终配色。

## 维护者说明

FigureBench 保留在本地。公开仓库只提供检索代码与小型 HEX/RGB 批准色库，不含源图片、原始本地路径或需要用户下载的多 GB 数据集。详见 [FigureBench RAG](./references/figurebench-rag.md) 与 [Palette RAG](./references/palette-rag.md)。
