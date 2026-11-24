# 迁移与成本 / Portability and cost

在另一项目中先运行环境检查；真实工具缺失时明确缩小当前产物范围，不能把成功导出当作已检查，或伪称具备原生软件编辑能力。
Run the environment check in another project; missing tools require an explicit change of deliverable scope, not treating export success as inspection or inventing native editing capabilities.

```bash
python3 agent-framework/scripts/task_guard.py environment
python3 agent-framework/scripts/restore_framework.py framework.md /path/to/new-project
```

默认迁移清空项目资料、检查结论和私有试用摘录，保留已有 `AGENTS.md` 原文；任何不同内容的框架文件冲突都会在写入前中止。
Default restoration resets project material, check conclusions and private pilot excerpts while retaining existing `AGENTS.md` bytes; conflicting framework files stop restoration before writes begin.

完整快照使用 `--mode snapshot`，其中旧检查必须重新运行；快照不是新项目已完成验证的证明。
Use `--mode snapshot` for an exact recorded snapshot and rerun its checks; a snapshot does not establish validation of a new project.

给朋友分享前使用 `bundle_framework.py --mode template --output shareable-framework.md`，让共享文件本身也排除当前论文摘录与私有项目记录。
Before sharing with a friend, use `bundle_framework.py --mode template --output shareable-framework.md` so the shared file itself excludes current manuscript excerpts and private project records.

迁移脚本先检查路径、重复文件和摘要，再写文件；它不声称具备多进程锁或断电时的整目录事务恢复能力。
The restorer checks paths, duplicates and digests before writing; it does not claim multi-process locking or whole-directory transactional recovery after power loss.

按快速、标准、深入三种深度选择记录和覆盖，不通过减少必要事实条件来换取速度，也不强制规定文献数量。
Choose quick, standard or deep coverage and records without sacrificing necessary factual conditions or imposing source quotas.

只记录实际可获得的耗时、工具调用、token 和金额；无法取得的数据保留为 `null` 并说明原因，不估造提速比例或运行成本。
Record only observable time, tool calls, tokens and monetary costs; unavailable values remain `null` with a reason rather than invented savings or costs.
