# ACHE v3 — Art & Design Agent Framework

一个主 Agent 按任务调用调研、概念、作图、写作、核查、评议、制作与交付八个模块。
One primary agent loads research, concepts, visuals, writing, verification, critique, production and delivery modules as needed.

保留中英文反防御性写作规则，围绕材料支持的核心贡献组织表达，并保留影响结论的事实条件。
Preserves Chinese and English anti-defensive writing, foregrounding supported contributions and retaining material factual conditions.

## 使用 / Use

在支持项目指令的宿主中打开本仓库，先读取 `AGENTS.md`，再直接描述要完成的工作。
Open this repository in a host that supports project instructions, read `AGENTS.md`, then describe the task directly.

复制到已有项目时，使用完整指南的恢复脚本，保留已有用户指令；默认建立空白项目记录。
For an existing project, use the guide restorer to preserve its user instructions and create fresh project records by default.

```bash
python3 agent-framework/scripts/restore_framework.py docs/ACHE_v3_Framework.md /path/to/project
python3 agent-framework/scripts/check_framework.py
python3 -m unittest discover -s agent-framework/tests -v
```

## 包含内容 / Included

- 八个按需模块、十一条工作流和快速／标准／深入三档执行深度。
  Eight on-demand modules, eleven workflows and quick/standard/deep execution profiles.
- 将实际检查绑定到任务范围及输入输出版本，相关文件改变后旧通过项失效。
  Binds performed checks to task scope and artifact versions, invalidating passes after relevant changes.
- 文本片段、段落范围、SVG 对象及图像顺序保护，以及授权范围外的差异检查。
  Protects text fragments, sections, SVG objects and image order, with checks for changes outside authorized scope.
- 中英文反防御性写作的完整副本和原许可，无法读取个人安装时使用内置副本。
  Complete Chinese/English anti-defensive writing copies and their original notice, with bundled fallback.
- 完整可恢复指南、配置检查器、回归测试和不会覆盖文件冲突的迁移脚本。
  A restorable guide, configuration validator, regression tests and collision-aware restoration.

本仓库分发通用模板，不包含个人论文摘录、场地试用档案、账户文件编号或个人电脑路径。
This repository distributes a reusable template without personal thesis excerpts, fieldwork pilots, account file IDs or personal computer paths.

本框架使用宿主已有模型与工具；它不是独立模型、后台服务或已安装的全局插件。
The framework uses host models and tools; it is not a separate model, background service or installed global plugin.

局部保护直接支持 UTF-8 文本与稳定 ID 的 SVG，自动检查不证明资料真实性或艺术质量。
Local protection directly supports UTF-8 text and SVG with stable IDs; automated checks do not establish source truth or artistic quality.

## 来源与许可 / Sources and licensing

方法学习自 [HKUSTDial/Supervisor-Skills](https://github.com/HKUSTDial/Supervisor-Skills)，固定提交与改编说明见 `agent-framework/upstream.lock.json` 和 `agent-framework/references/supervisor-adaptation.md`。
Methods are adapted from [HKUSTDial/Supervisor-Skills](https://github.com/HKUSTDial/Supervisor-Skills); the pinned revision and adaptation notes are included in the framework.

改编方法保留 CC BY-NC-SA 4.0 许可，中英文反防御性写作保留其 MIT 许可；相关原文随仓库保留。
Adapted methodology retains CC BY-NC-SA 4.0 terms, while anti-defensive writing retains its MIT notice; original notices are included.
