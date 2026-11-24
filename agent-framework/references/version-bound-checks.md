# 检查与文件版本 / Checks and artifact versions

只有完成实际检查后才记录凭据；凭据将任务范围、检查方法、证据文件和所依赖的输入输出绑定到 SHA-256。
Record a receipt after performing a check; it binds task scope, method, evidence and the dependent inputs and outputs to SHA-256 fingerprints.

`project/checks.json` 保存凭据，`task.json` 的通过项通过 `receipt_id` 引用，视觉、引用和跨文件核查记录引用对应检查的凭据。
`project/checks.json` stores receipts, passed task checks reference them through `receipt_id`, and visual, citation and alignment records reference the corresponding receipt.

```python
from task_integrity import make_receipt
receipt = make_receipt(root, task, "R-01", "cross_artifact_alignment",
    "review.md", ["manuscript.txt", "booklet.txt"], [],
    "Selected paragraphs and their captions", "same-context source comparison")
```

文件内容改变只使依赖该文件的检查失效；任务编号、范围、授权或其他执行条件改变会使该任务范围内的旧凭据失效。
A content change invalidates checks that depend on that file; a changed task ID, scope, authorization or other execution conditions invalidate receipts for that task context.

新增检查结果、过程注释、成本记录和历史不会让凭据因自身写入而失效；这些字段不能用于隐藏范围或输入的改变。
Adding check results, notes, metrics and history does not make a receipt invalidate itself; these fields must not conceal changes to scope or inputs.

```bash
python3 agent-framework/scripts/task_guard.py status
python3 agent-framework/scripts/check_framework.py
```

读取 `effective_status` 判断当前可用性，不能在检查已经失效时沿用原先声明的 `pass`；只重新检查受影响的环节。
Use `effective_status` for current validity rather than retaining a declared `pass` after it has become stale; recheck only affected stages.

远程资料先通过连接来源重新读取并固定版本，再保存本轮所用摘录；凭据验证本地摘录内容，不自动轮询远程文件是否更新。
Refresh remote material through its connected source, pin the version and save the excerpts actually used; receipts validate local excerpts and do not automatically poll remote updates.

记录远程来源编号、版本、返回文件编号、实际页序和读取范围；没有原始文件字节时，不声称获得整份 PDF 的校验值或完成版式检查。
Record the remote source ID, version, returned file ID, actual page indices and reading scope; without original file bytes, do not claim a whole-PDF digest or layout inspection.

凭据不能证明检查者诚实、资料真实或解释正确；它防止已声明检查被无提示地用于另一版本或另一范围。
A receipt cannot prove reviewer honesty, source truth or interpretive validity; it prevents a declared check from silently applying to another version or scope.

迁移旧记录时保留原报告，把没有版本凭据的旧通过项改为 `not_run` 或有明确缺口的 `partial`，不补造检查证据。
When migrating older records, retain their reports and mark unbound old passes `not_run` or explicitly `partial` rather than inventing evidence.
