# 引用核验与能力分级 / Citation checks and capability levels

## Two separate questions

1. Does the work exist, and do title, authors, date and identifiers match an authoritative record?
2. Does the material actually read support the sentence using it?

A real reference can be misused. Metadata can establish bibliographic identity and broad topic, not an unseen mechanism, precise result, quotation or detailed limitation. Read a relevant excerpt, full text or data for the stronger claim and record a concrete location.

## Actual verification method

- `fresh_context_retrieval`: an authorized fresh-context verifier checks cited prose and references through retrieval, without the writer's preferred verdict or reasoning.
- `same_context_retrieval`: the current agent re-derives entries from actual retrieval and checks claim support; do not call it independent.
- `supplied_sources_only`: check against the supplied accessible material and add no unsupported external entries; do not claim external verification.
- `not_run`: no citation check was performed.

Source and claim standards stay the same when capabilities are missing. The mechanism and coverage change, and any consequential limitation is reported briefly. A different role label in one context is not a fresh independent check. Availability of subagents does not itself grant authorization to launch them.

## Source verdicts

Record citation checks in `project/reviews.json` with citation ID, claim IDs, method, result, checked locator and resolution.

| Result | Meaning | Action |
|---|---|---|
| `verified` | Identity matches and the cited statement fits material read | Keep within that scope |
| `metadata_mismatch` | A work exists but the reference fields differ | Correct from reliable records; preserve unresolved conflicts |
| `overclaim` | The source exists but does not support this strength or detail | Read the needed material or revise the affected sentence |
| `not_found` | Normal completed searches with meaningfully different query forms found no matching work | Investigate, replace or remove from factual final prose; do not label a known valid work nonexistent from one failure |
| `inconclusive` | Retrieval, access or identification could not be completed | Neither pass nor assert nonexistence; record what remains unresolved |

`not_found` requires actual completed searches, not a fixed ritual count. Distinguish infrastructure failure from negative evidence. A paywall limits what can be checked; it does not prove an entry false.

## When to run

Review every cited material factual claim in a final manuscript, multi-section draft, literature synthesis or requested citation audit. Scale the pass to short fragments. For no-citation creative prose, do not force a bibliography, but check externally testable statements that the prose actually makes.

Repair only affected entries, sentences and dependencies, then repeat the affected check. Unresolved material citation problems block calling that citation layer fully verified. They do not require abandoning all independent useful work or erasing a valid artistic proposition.

These checks establish bibliographic and support relationships at the stated scope. They do not establish that a published source's underlying claim is true, that fieldwork occurred, or that an interpretation is universally correct.
