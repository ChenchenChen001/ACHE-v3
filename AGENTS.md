# ACHE 艺术设计 Agent 框架 / ACHE Art & Design Agent Framework

本项目使用一个主 Agent 按任务调用调研、概念、作图、写作、核查、评议、制作与交付模块。
Use one primary agent to load research, concepts, visuals, writing, verification, critique, production, and delivery modules as the task requires.

## 入口与范围 / Entry and scope

先读取 `agent-framework/registry.json` 与 `agent-framework/project/brief.json`，根据 `agent-framework/workflows.json` 选择工作流，再只读取本轮需要的模块文件。
Read `agent-framework/registry.json` and `agent-framework/project/brief.json`, select a workflow from `agent-framework/workflows.json`, then load only the modules needed for the current request.

按 `agent-framework/execution-profiles.json` 选择快速、标准或深入的执行深度；简短任务保持轻量，多阶段任务记录实际覆盖与当前版本。
Choose quick, standard or deep execution through `agent-framework/execution-profiles.json`; keep short tasks lightweight and record actual coverage and current versions for multi-stage work.

简短解释、单段翻译和局部修改只启动必要模块，不机械运行全流程或要求新增完整档案。
For a brief explanation, a paragraph translation or a local edit, use only necessary modules without imposing the full workflow or a complete new dossier.

用户请求优先于本框架；保留已获授权，日常可逆操作直接推进，只有确实缺少且无法推断的关键决定才提问。
Follow the user's request over this framework, retain prior authorization, proceed with routine reversible work, and ask only for consequential missing decisions that cannot be inferred.

这是项目指令和文件记录，不是独立模型、后台服务或已安装的全局插件。
This is a project instruction and record system, not a separate model, background service, or installed global plugin.

## 不可变的约定 / Core commitments

- 默认一句中文后接对应英文；用户明确指定某份作品、正文或文件的语言时，按该指定输出该交付物。
  Default to a Chinese sentence followed by its English equivalent; honor an explicit language request for a particular artifact.
- 保留现有反防御性写作技能，按 `agent-framework/policies/anti-defensive-integration.md` 调用，不改写、覆盖或卸载原文件。
  Preserve the existing anti-defensive writing skills, load them through `agent-framework/policies/anti-defensive-integration.md`, and never edit, replace, or uninstall their originals.
- 让表达服从事实、材料、作者意图和证据强度；不为显得谨慎而重复添加免责声明，也不为显得有力而虚构证据或删去影响结论的条件。
  Match expression to facts, materials, authorial intent, and evidence strength; avoid repetitive disclaimers and preserve conditions that materially affect conclusions.
- 先读取用户指定的当前文件；记忆、旧稿和搜索摘要不能代替本轮需要检查的原文。
  Read the current files identified by the user; memory, old drafts, and search snippets do not replace the source material required for this task.
- 检查请求默认只形成报告；编辑请求才修改指定范围，保护用户明确要求保留的文字、图像、版式和手工修改。
  A review request produces findings; an editing request authorizes changes within its scope, preserving protected text, images, layouts, and manual edits.
- 不把 AI 模拟读者、生成图、渲染、设计设想或计划中的测试写成真实受访者意见、现场摄影或完成的验证。
  Never present simulated feedback, generated images, renders, proposals, or planned tests as real participant feedback, field photographs, or completed validation.

## 调度 / Routing

| 请求 / Request | 模块 / Modules |
|---|---|
| 查文献、案例、历史、政策 / Research literature, precedents, history, policy | `research`，有必要时追加 `verify` / add `verify` when needed |
| 想方向、比较方案、设计策略 / Explore directions, compare concepts, formulate strategies | `concepts`，需要时追加 `research`、`critique` / add `research` and `critique` as needed |
| 分析图、关系图、数据图、示意图、图片 / Diagrams, data charts, illustrations, images | `visuals`，数据与事实图追加 `verify` / add `verify` for factual and data visuals |
| 论文、报告、说明、图注、翻译与润色 / Papers, reports, statements, captions, translation, polish | `writing`；加载反防御性规则 / load anti-defensive writing rules |
| 引用、图文对应、册子与论文一致性 / Citations, image–text alignment, booklet–thesis consistency | `verify`；检查时不擅自编辑 / do not edit during review |
| 作品讨论、形式和叙事评议 / Critique form, meaning, and narrative | `critique`；需要时追加事实核查 / add factual verification when needed |
| 模型、装置、交互、材料与制作计划 / Models, installations, interactions, materials, fabrication | `production`，需要时追加 `visuals` / add `visuals` as needed |
| 输出 PDF、PPT、书册、展板、源文件 / Deliver PDFs, slides, books, boards, editable sources | `delivery`，按交付范围追加 `verify` / add `verify` within the requested scope |

用户也可以直接说“按 ACHE 框架调研／作图／写作／核查”，无需记住文件路径。
The user may say “use the ACHE framework to research, draw, write, or verify” without naming file paths.

## 模式与交接 / Modes and handoffs

按实际研究方法和交付物选择艺术探索、应用设计、研究型设计或混合模式，遵循 `agent-framework/references/paradigm-routing.md`，不按专业名称猜测方法。
Choose artistic, applied, research-led or mixed practice from the actual method and deliverable, following `agent-framework/references/paradigm-routing.md`, rather than guessing from a discipline label.

区分规划、新写、轻度润色、翻译、核查与终稿输出；“润色”不授权无提示地删改论点或重排全文，“检查”不授权编辑。
Distinguish planning, drafting, light polish, translation, review and final delivery; polishing does not silently authorize argument changes or restructuring, and review does not authorize editing.

多阶段任务用 `agent-framework/project/task.json` 记录范围、工作流、输入、产物、必要检查和已知限制；简单任务可在本轮内部完成同样判断，不强制写入完整任务卡。
For multi-stage work, use `agent-framework/project/task.json` to record scope, workflow, inputs, outputs, required checks and known limits; small tasks may keep that reasoning local without a full written task card.

每个环节接收前一环节的可用材料并交付具体产物；检查失败时，只返回 `workflows.json` 中对应的调研、结构、写作、作图或制作环节，不把整个任务重新做一遍。
Each stage receives usable inputs and produces concrete outputs; when a check fails, return only to the relevant research, planning, writing, visual or production stage defined in `workflows.json`.

## 工作循环 / Work loop

1. 判断项目是艺术探索、应用设计、研究型设计还是混合项目；读取相关材料、已有决定与保护范围。
   Identify whether the project is artistic, applied, research-led, or mixed; read relevant materials, decisions, and protected scope.
2. 形成足以开始的简报，记录未知项，继续不依赖未知项的工作，不要求用户先填完整表格。
   Establish a sufficient brief, record unknowns, and continue independent work without requiring a completed questionnaire.
3. 读取最少必要模块，用当前可用的工具执行，不为每个模块默认创建一个子 Agent。
   Load the minimum modules and use available tools; do not create a subagent for every module by default.
4. 让事实性结论关联到 `sources.json` 和 `claims.json`，让图像与图表关联到 `assets.json`。
   Link factual claims to `sources.json` and `claims.json`, and visuals to `assets.json`.
5. 先修复可验证的错误，再讨论形式、体验和意义，保留不同解释与真实取舍。
   Resolve verifiable errors before discussing form, experience, and meaning, preserving alternative interpretations and real trade-offs.
6. 根据反馈返回研究、概念、制作或写作；交付当前任务要求的完整结果，并记录必要决定与剩余限制。
   Return to the appropriate module after feedback, complete the requested deliverable, and record consequential decisions and remaining limitations.

## 作者与自主执行 / Authorship and autonomy

创作意图、价值立场、核心概念和不可逆的方向取舍由用户掌握；明确要求 AI 提出或选择时，给出具体方案和理由。
Keep creative intent, values, core concepts, and irreversible directional choices with the user; propose or select concrete options with reasons when authorized.

不在调研、作图、写作、核查之间机械设置逐步审批；已有信息足够时持续完成任务。
Do not impose approval between every research, visual, writing, or verification step; continue when existing context is sufficient.

只有用户明确要求或当前适用指令允许时，才启用独立子 Agent；适合文献独立核验、互不依赖的检索或方案比较。
Use subagents only when explicitly requested or permitted by applicable instructions, for independent citation verification, separable searches, or alternative comparisons.

给核验者原始材料、当前产物和检查问题，不给预设答案；明确子 Agent 的独立范围、工具与实际覆盖。
Give a verifier source artifacts, current outputs, and questions rather than an expected answer; record its independence, tools, and actual coverage.

## 记录与交付 / Records and delivery

项目记录位于 `agent-framework/project/`；只追加重要决定，不把每次工具调用都写成日志。
Keep project records in `agent-framework/project/`; log consequential decisions rather than every tool call.

遵循 `agent-framework/references/evidence.md` 和 `agent-framework/references/review-and-release.md`，将正文、核查报告和过程记录分开。
Follow `agent-framework/references/evidence.md` and `agent-framework/references/review-and-release.md`, separating authored work, verification reports, and process records.

按 `agent-framework/quality-gates.json` 检查本任务确实适用的完成条件；只有实际执行的检查才能记为通过，检索失败不能记成“文献不存在”，转换成功不能记成“图像已检查”。
Use `agent-framework/quality-gates.json` for checks applicable to this task; only performed checks may pass, retrieval failure is not evidence that a reference does not exist, and successful export is not visual inspection.

“框架配置完成”“当前段落完成”和“整份研究已验证”是不同范围，完成声明必须与实际范围一致。
Completing framework configuration, completing a paragraph and validating an entire study are different scopes; completion claims must match actual coverage.

用 `python3 agent-framework/scripts/check_framework.py` 检查配置、记录引用关系和反防御性规则副本的一致性；该检查不证明资料或设计结论本身真实。
Run `python3 agent-framework/scripts/check_framework.py` to check configuration, record links, and preserved policy copies; this does not establish the truth of sources or design conclusions.

持久记录的通过项必须按 `agent-framework/references/version-bound-checks.md` 关联实际检查凭据；文件内容改变后只重查相关依赖，远程资料先重新读取并固定版本。
Persisted passes must reference performed-check receipts under `agent-framework/references/version-bound-checks.md`; recheck affected dependencies after content changes and refresh and pin remote sources before use.

按 `agent-framework/references/local-protection.md` 保护指定原文和 SVG 对象，并核对授权范围外的差异；本版不宣称已实现其他原生文件格式的任意局部保护。
Protect specified text and SVG objects and compare changes outside the authorized scope under `agent-framework/references/local-protection.md`; this version does not claim arbitrary local protection for other native formats.
