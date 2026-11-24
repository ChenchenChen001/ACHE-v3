# 核查与交付规则 / Review and release rules

## 范围 / Scope

Read the exact current artifacts named by the user and record what was inspected. If multiple versions exist, resolve from current file metadata and contents; ask only when the actual target remains ambiguous. Do not use remembered wording as the authoritative latest draft. Respect protected passages, photos, geometry, page layouts and manual edits.

## 分类 / Findings

Use concrete locations and actionable fixes. Separate `factual`, `methodological`, `cross_artifact`, `technical`, and `interpretive` findings. Label severity `critical`, `major`, or `minor` only for the consequence supported by the material. A font, dash or personal aesthetic preference is not automatically a critical research flaw.

- Critical: changes the truth or usability of the central claim, a fabricated source, misrepresented real-world evidence, a material numerical error, or unusable required output.
- Major: a consequential missing link, contradictory figure/text, missing provenance, illegible argument-bearing figure, or deliverable requirement not met.
- Minor: a local clarity, consistency or presentation improvement.

For comparison of a thesis, booklet, appendix, caption and diagram, build a map from the source claim and location to each derivative artifact. Track print page numbers separately from PDF page indices. Check omitted qualifiers, added claims, reversed relationships and figure references. Review requests produce a report, not an unsolicited revision.

## 两种评议 / Two review functions

Factual verification resolves testable questions using sources and measurements. Studio critique gives reasoned interpretations of intent, form, context and experience. Record disagreement and authorial trade-offs without pretending aesthetic value is an objective universal score. Simulated audience feedback is a hypothesis, not participant research.

## 完成与覆盖 / Completion and coverage

Use `complete`, `partial`, `blocked`, or `not_applicable` in `project/status.json`. Record current task, inspected scope, produced paths, relevant checks, open issues and the next justified action. Completed configuration checks are not semantic validation. Export success is not visual inspection. Independent verification requires an actual separate check, not a different role label in the same conversation.

Before final delivery, confirm requested formats, file opening, required pages or outputs, image/font legibility, figure/caption/reference correspondence and editable sources where requested. Use only checks material to the task. Do not add a broad new audit after the requested checks pass without a reason.

Keep the final answer self-contained, Chinese followed by English by default, and concise: outcome, usable deliverable, material limits if any. Save durable artifacts through the available supported workflow and return working links. Do not claim installation, publication, file saving, whole-document review, real testing or global activation unless observed.

## Applicable checks and targeted repair

Select checks from `quality-gates.json` through the task's workflow, rather than running every possible audit. Record `pass`, `fail`, `partial`, `not_run`, `not_applicable`, or `inconclusive`, with the actual check evidence and scope. A not-applicable judgment needs a reason. A required check that is incomplete prevents saying that checked scope is fully verified; report partial coverage while continuing useful independent work.

Separate project-configuration completion from research validation. The structural checker verifies declared records and file integrity, not source truth or artistic quality. Its success cannot be used as evidence that a participant exists, a paper says what is claimed, or a generated image depicts a real site.

Follow the workflow's failure route: missing sources return to research, broken reasoning to planning/writing, visual defects to the affected graphic, and unperformed physical tests to production. Recheck affected outputs only. Review severity follows consequence, not a universal ban on a word, dash, photographic format or artistic ambiguity.

For independent checks, record the actual method and authorization. Same-context retrieval and supplied-source checks remain useful but must not be described as fresh independent verification. Do not launch extra agents merely to satisfy a label or inflate the cost of a small task.

Persisted passes in v3 require current receipts under `version-bound-checks.md`. Run `task_guard.py status` to identify stale dependencies without rewriting history. Use `local-protection.md` to check protected fragments and changes outside the authorized scope. Default portable restoration clears inherited passes and private project material as described in `portability-and-cost.md`.
