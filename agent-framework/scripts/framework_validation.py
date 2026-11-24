"""Validate ACHE configuration and declared records; never certify source truth."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from task_integrity import local_path, lock_issues, receipt_issues

MODULES = {"research", "concepts", "visuals", "writing", "verify", "critique", "production", "delivery"}
SCOPES = {"full_text", "excerpt", "abstract", "metadata", "image", "data", "not_read"}
AUTHENTICITY = {"verified", "user_reported", "unresolved", "not_applicable"}
EVIDENCE_TYPES = {"documented_source", "observational_record", "measurement", "reported_account", "interpretive_source", "simulated_material", "proposal", "unknown"}
CLAIM_KINDS = {"fact", "observation", "reported_account", "interpretation", "proposal", "preference", "simulated_feedback"}
CLAIM_STATES = {"supported", "needs_check", "contested", "proposed", "not_applicable"}
LEVELS = {"metadata", "summary", "detailed", "empirical"}
ASSET_KINDS = {"field_photo", "reference_image", "data_chart", "analytical_diagram", "generated_image", "render", "mockup", "prototype_record", "layout"}
ASSET_STATES = {"draft", "needs_check", "reviewed", "final"}
CHECK_STATES = {"pass", "fail", "partial", "not_run", "not_applicable", "inconclusive"}
METHODS = {"fresh_context_retrieval", "same_context_retrieval", "supplied_sources_only", "not_run"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def oneof(value, allowed):
    return isinstance(value, str) and value in allowed


def check(root):
    root = Path(root).resolve()
    base = root / "agent-framework"
    errors, warnings = [], []

    def error(message):
        errors.append(message)

    def relative_file(value, label):
        if not nonempty(value) or Path(value).is_absolute():
            error(label + ": expected a relative framework path")
            return None
        path = (base / value).resolve()
        try:
            path.relative_to(base.resolve())
        except ValueError:
            error(label + ": reference escapes the framework")
            return None
        if not path.is_file():
            error(label + ": missing file " + value)
            return None
        return path

    def obj(relative):
        path = relative_file(relative, relative)
        if path is None:
            return {}
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            error(relative + ": unreadable or invalid JSON")
            return {}
        if not isinstance(value, dict):
            error(relative + ": expected a JSON object")
            return {}
        return value

    def sequence(value, label):
        if not isinstance(value, list):
            error(label + ": expected a list")
            return []
        return value

    def strings(value, label):
        values = sequence(value, label)
        if any(not nonempty(x) for x in values):
            error(label + ": expected nonempty strings")
        return [x for x in values if nonempty(x)]

    def rows(relative, key):
        values = sequence(obj(relative).get(key, []), relative + ":" + key)
        if any(not isinstance(x, dict) for x in values):
            error(relative + ": every record must be an object")
        return [x for x in values if isinstance(x, dict)]

    def indexed(values, label):
        found = {}
        for row in values:
            identifier = row.get("id")
            if not nonempty(identifier):
                error(label + ": missing id")
            elif identifier in found:
                error(label + ": duplicate id " + identifier)
            else:
                found[identifier] = row
        return found

    def links(row, key, index, label):
        identifiers = strings(row.get(key, []), label + ":" + key)
        for identifier in identifiers:
            if identifier not in index:
                error(label + ": unknown " + key + " id " + identifier)
        return identifiers

    if not (root / "AGENTS.md").is_file():
        error("Missing project entry AGENTS.md")
    registry = obj("registry.json")
    modules = registry.get("modules", {})
    if not isinstance(modules, dict):
        error("modules must be an object")
        modules = {}
    if set(modules) != MODULES:
        error("Expected the eight art/design modules")
    for name, definition in modules.items():
        if not isinstance(definition, dict):
            error("Invalid module " + name)
            continue
        relative_file(definition.get("file"), "module " + name)
        for key in ("input_contract", "output_contract", "checks"):
            strings(definition.get(key), "module " + name + ":" + key)
    for group in ("policies", "references", "project_records", "templates"):
        for path in strings(registry.get(group, []), group):
            relative_file(path, group)

    quality = obj(registry.get("quality_gates", "quality-gates.json"))
    gates = quality.get("gates", {})
    if not isinstance(gates, dict):
        error("quality gates must be an object")
        gates = {}
    for name, definition in modules.items():
        if isinstance(definition, dict):
            for gate in definition.get("checks", []) if isinstance(definition.get("checks"), list) else []:
                if isinstance(gate, str) and gate not in gates:
                    error("module " + name + ": unknown check " + gate)
    flow_doc = obj(registry.get("workflows", "workflows.json"))
    workflows = flow_doc.get("workflows", {})
    if not isinstance(workflows, dict):
        error("workflows must be an object")
        workflows = {}
    for identifier, flow in workflows.items():
        if not isinstance(flow, dict):
            error("Invalid workflow " + identifier)
            continue
        used = strings(flow.get("modules"), identifier + ":modules")
        for name in used:
            if name not in modules:
                error(identifier + ": unknown module " + name)
        required = strings(flow.get("required_checks"), identifier + ":required_checks")
        for gate in required:
            if gate not in gates:
                error(identifier + ": unknown check " + gate)
        routes = flow.get("failure_routes", {})
        if not isinstance(routes, dict):
            error(identifier + ": failure_routes must be an object")
        else:
            for gate, name in routes.items():
                if gate not in required or name not in used:
                    error(identifier + ": invalid repair route " + str(gate))

    upstream = obj(registry.get("upstream_lock", "upstream.lock.json"))
    if not re.fullmatch(r"[0-9a-f]{40}", str(upstream.get("commit", ""))):
        error("Upstream revision is not pinned to a commit")
    policies = []
    for policy in sequence(registry.get("preserved_policies"), "preserved_policies"):
        if not isinstance(policy, dict):
            error("Invalid preserved policy record")
            continue
        name, digest = policy.get("name"), policy.get("sha256")
        if not nonempty(name) or not re.fullmatch(r"[0-9a-f]{64}", str(digest or "")):
            error("Invalid preserved policy identity or digest")
            continue
        snapshot = relative_file(policy.get("snapshot"), "policy " + name)
        matches = snapshot is not None and hashlib.sha256(snapshot.read_bytes()).hexdigest() == digest
        if not matches:
            error("Preserved policy snapshot changed: " + name)
        original_matches = None
        original_path = policy.get("original_path")
        if nonempty(original_path) and Path(original_path).is_file():
            try:
                original_matches = hashlib.sha256(Path(original_path).read_bytes()).hexdigest() == digest
            except OSError:
                warnings.append("Original policy could not be read: " + name)
            if original_matches is False:
                warnings.append("Original policy changed after the preserved baseline: " + name)
        else:
            warnings.append("Original policy unavailable; use its preserved snapshot: " + name)
        policies.append({"name": name, "snapshot_matches": matches, "original_matches": original_matches})
    if len(policies) != 2 or {x["name"] for x in policies} != {"anti-defensive-writing", "anti-defensive-writing-en"}:
        error("Expected both original anti-defensive writing policies")

    brief = obj("project/brief.json")
    if not oneof(brief.get("project_type"), {"artistic", "applied", "research-led", "mixed"}):
        error("Unknown project_type")
    status = obj("project/status.json")
    if not oneof(status.get("status"), {"complete", "partial", "blocked", "not_applicable"}):
        error("Unknown completion status")
    task = obj("project/task.json")
    strict_receipts = registry.get("receipt_policy") == "version-bound"
    if strict_receipts:
        profiles = obj(registry.get("execution_profiles", "execution-profiles.json")).get("profiles", {})
        if not isinstance(profiles, dict) or set(profiles) != {"quick", "standard", "deep"}:
            error("Expected quick, standard and deep execution profiles")
        if not oneof(task.get("depth", "standard"), {"quick", "standard", "deep"}):
            error("Unknown task execution depth")
    receipt_records = indexed(rows("project/checks.json", "receipts"), "check receipts") if strict_receipts else {}

    def bound_receipt(record, gate, label):
        identifier = record.get("receipt_id")
        receipt = receipt_records.get(identifier) if nonempty(identifier) else None
        for issue in receipt_issues(root, task, receipt, gate):
            error(label + ": " + issue)
        return receipt or {}

    def bound_paths(receipt, paths, label, role=None):
        dependencies = receipt.get("dependencies", [])
        if not isinstance(dependencies, list):
            dependencies = []
        for name in paths:
            try:
                actual = local_path(root, name)
                matched = any(isinstance(x, dict) and (role is None or x.get("role") == role)
                              and local_path(root, x.get("path")) == actual for x in dependencies)
                if not matched:
                    error(label + ": checked path is not bound to the receipt: " + name)
            except (ValueError, TypeError):
                error(label + ": invalid checked project path")
    workflow_id = task.get("workflow_id")
    if not nonempty(workflow_id) or workflow_id not in workflows:
        error("Current task has no known workflow")
        workflow_id = None
    required = strings(task.get("required_checks", []), "task:required_checks")
    checks = task.get("checks", {})
    if not isinstance(checks, dict):
        error("Task checks must be an object")
        checks = {}
    exemptions = task.get("check_exemptions", {})
    if not isinstance(exemptions, dict):
        error("Task check exemptions must be an object")
        exemptions = {}
    selected = workflows.get(workflow_id, {})
    if isinstance(selected, dict):
        for gate in selected.get("required_checks", []):
            if gate not in required and not nonempty(exemptions.get(gate)):
                error("Applicable workflow check omitted without reason: " + gate)
    for gate in required:
        if gate not in gates:
            error("Unknown required task check " + gate)
    for gate, record in checks.items():
        if gate not in gates or not isinstance(record, dict) or not oneof(record.get("status"), CHECK_STATES):
            error("Invalid task check " + str(gate))
            continue
        if record["status"] == "pass" and not nonempty(record.get("evidence")):
            error(gate + ": pass has no check evidence")
        if strict_receipts and record["status"] == "pass":
            bound_receipt(record, gate, gate)
        if record["status"] == "not_applicable" and not nonempty(record.get("reason")):
            error(gate + ": not-applicable has no reason")
    if status.get("status") == "complete":
        for gate in required:
            record = checks.get(gate, {})
            if not isinstance(record, dict) or not oneof(record.get("status"), {"pass", "not_applicable"}):
                error("Task marked complete before required check: " + gate)
    method = task.get("verification_method", "not_run")
    if not oneof(method, METHODS):
        error("Unknown verification method")
    independent = task.get("independent_verification", False)
    if not isinstance(independent, bool):
        error("Independent verification must be true or false")
    if bool(independent) != (method == "fresh_context_retrieval"):
        error("Independent verification claim does not match the declared method")
    if workflow_id == "cross-artifact-review" and task.get("edits_made") and not task.get("edit_authorized"):
        error("Review-only task records unauthorized edits")
    for item in sequence(task.get("protected_paths", []), "protected_paths"):
        if not isinstance(item, dict) or not nonempty(item.get("path")) or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("sha256", ""))):
            error("Invalid protected-file record")
            continue
        protected = Path(item["path"])
        if not protected.is_absolute():
            protected = root / protected
        try:
            if hashlib.sha256(protected.read_bytes()).hexdigest() != item["sha256"]:
                error("Protected file changed: " + item["path"])
        except OSError:
            error("Protected file could not be verified: " + item["path"])

    lock_rows = sequence(task.get("protected_content", []), "protected_content")
    if any(not isinstance(x, dict) for x in lock_rows):
        error("Invalid content lock record")
    content_locks = indexed([x for x in lock_rows if isinstance(x, dict)], "content locks")
    for item in content_locks.values():
        for issue in lock_issues(root, item):
            error(issue)

    source_rows = rows("project/sources.json", "sources")
    claim_rows = rows("project/claims.json", "claims")
    asset_rows = rows("project/assets.json", "assets")
    sources = indexed(source_rows, "sources")
    claims = indexed(claim_rows, "claims")
    assets = indexed(asset_rows, "assets")
    for identifier, source in sources.items():
        if not oneof(source.get("read_scope"), SCOPES) or not oneof(source.get("authenticity"), AUTHENTICITY):
            error(identifier + ": invalid reading scope or authenticity")
        if not nonempty(source.get("locator")):
            error(identifier + ": missing source locator")
        if not oneof(source.get("evidence_type", "unknown"), EVIDENCE_TYPES):
            error(identifier + ": invalid evidence type")
    for identifier, claim in claims.items():
        ids = links(claim, "source_ids", sources, identifier)
        kind, state = claim.get("kind"), claim.get("status")
        if not oneof(kind, CLAIM_KINDS) or not oneof(state, CLAIM_STATES) or not nonempty(claim.get("text")):
            error(identifier + ": invalid claim kind, status or text")
        evidence = sequence(claim.get("evidence_links", []), identifier + ":evidence_links")
        supporting = []
        for link in evidence:
            if not isinstance(link, dict):
                error(identifier + ": evidence link must be an object")
                continue
            sid = link.get("source_id")
            if not isinstance(sid, str) or sid not in sources or sid not in ids:
                error(identifier + ": evidence link has an unknown or undeclared source")
                continue
            if not oneof(link.get("relation"), {"supports", "qualifies", "contradicts"}):
                error(identifier + ": invalid evidence relation")
            if not nonempty(link.get("location")) or not nonempty(link.get("note")):
                error(identifier + ": evidence link needs a location and support explanation")
            elif link.get("relation") == "supports":
                supporting.append(sources[sid])
        factual = oneof(kind, {"fact", "observation", "reported_account"})
        if factual and state == "supported":
            level = claim.get("assertion_level")
            if not oneof(level, LEVELS):
                error(identifier + ": supported factual claim needs assertion_level")
            if not supporting:
                error(identifier + ": supported claim has no specific supporting evidence link")
            if supporting and all(s.get("read_scope") == "not_read" for s in supporting):
                error(identifier + ": supported claim relies only on unread material")
            if level == "summary" and supporting and all(oneof(s.get("read_scope"), {"metadata", "not_read"}) for s in supporting):
                error(identifier + ": metadata alone cannot support a substantive summary")
            if oneof(level, {"detailed", "empirical"}) and supporting and all(not oneof(s.get("read_scope"), {"full_text", "excerpt", "image", "data"}) for s in supporting):
                error(identifier + ": detailed or empirical assertion exceeds reading scope")
            if oneof(kind, {"fact", "observation"}) and supporting and all(s.get("authenticity") == "unresolved" for s in supporting):
                error(identifier + ": unresolved accounts cannot silently become established observations")
            if (kind == "observation" or level == "empirical") and supporting and all(oneof(s.get("evidence_type"), {"simulated_material", "proposal"}) for s in supporting):
                error(identifier + ": simulated or proposed material cannot establish observed effects")
        if oneof(kind, {"proposal", "simulated_feedback"}) and state == "supported":
            warnings.append(identifier + ": supported rationale does not establish an observed result")

    review_doc = obj("project/reviews.json")
    visual_rows = sequence(review_doc.get("visual_inspections", []), "visual_inspections")
    visual_records = indexed([x for x in visual_rows if isinstance(x, dict)], "visual_inspections")
    if len(visual_records) != len(visual_rows):
        error("Invalid or duplicate visual inspection records")
    for identifier, review in visual_records.items():
        if not oneof(review.get("status"), CHECK_STATES):
            error(identifier + ": invalid inspection status")
        if review.get("status") == "pass" and (not nonempty(review.get("checked_locator")) or not nonempty(review.get("method"))):
            error(identifier + ": passed inspection has no actual output or method")
        if strict_receipts and review.get("status") == "pass":
            receipt = bound_receipt(review, "visual_inspection", identifier)
            bound_paths(receipt, [review.get("checked_locator")], identifier, "output")
    for identifier, asset in assets.items():
        ids = links(asset, "source_ids", sources, identifier)
        links(asset, "claim_ids", claims, identifier)
        if not oneof(asset.get("kind"), ASSET_KINDS) or not oneof(asset.get("status", "draft"), ASSET_STATES) or not nonempty(asset.get("path")):
            error(identifier + ": invalid asset kind, status or path")
        if asset.get("generated") and asset.get("kind") == "field_photo":
            error(identifier + ": generated image cannot be field photography")
        if asset.get("kind") == "data_chart" and asset.get("status") == "final" and not ids:
            error(identifier + ": final data chart has no source")
        if oneof(asset.get("status"), {"reviewed", "final"}) or asset.get("visually_checked"):
            inspection_id = asset.get("inspection_id")
            record = visual_records.get(inspection_id, {}) if nonempty(inspection_id) else {}
            if record.get("status") != "pass":
                error(identifier + ": reviewed/final visual lacks a completed inspection record")
            elif strict_receipts:
                receipt = receipt_records.get(record.get("receipt_id"), {})
                bound_paths(receipt, [asset.get("path")], identifier, "output")
                snapshots = [sources[sid]["snapshot_path"] for sid in ids if sid in sources and nonempty(sources[sid].get("snapshot_path"))]
                bound_paths(receipt, snapshots, identifier, "input")

    citation_rows = sequence(review_doc.get("citation_checks", []), "citation_checks")
    for record in citation_rows:
        if not isinstance(record, dict):
            error("Citation check must be an object")
            continue
        if not oneof(record.get("result"), {"verified", "metadata_mismatch", "overclaim", "not_found", "inconclusive"}):
            error("Unknown citation verdict")
        if not oneof(record.get("method"), METHODS):
            error("Unknown citation-check method")
        if record.get("result") == "not_found":
            queries = strings(record.get("query_forms", []), "citation query forms")
            if record.get("search_status") != "completed" or not record.get("normal_zero_hits") or len(set(queries)) < 2:
                error("Citation not-found verdict is not backed by completed varied searches")
        if record.get("result") == "verified" and not nonempty(record.get("checked_locator")):
            error("Verified citation has no checked locator")
        if strict_receipts and record.get("result") == "verified":
            bound_receipt(record, "citation_accuracy", "Verified citation")
    for record in sequence(review_doc.get("alignment_checks", []), "alignment_checks"):
        if not isinstance(record, dict):
            error("Alignment check must be an object")
            continue
        if strict_receipts and record.get("status") == "pass":
            receipt = bound_receipt(record, "cross_artifact_alignment", "Alignment check")
            paths = strings(record.get("compared_paths", []), "compared_paths")
            if len(set(paths)) < 2:
                error("Alignment check needs both compared artifacts")
            bound_paths(receipt, paths, "Alignment check")

    return {"check_type": "configuration-and-declared-record-integrity", "result": "pass" if not errors else "fail", "semantic_validation": False, "errors": errors, "warnings": warnings, "details": {"version": registry.get("version"), "modules": sorted(modules), "workflow_count": len(workflows), "source_count": len(source_rows), "claim_count": len(claim_rows), "asset_count": len(asset_rows), "task_scope": task.get("scope"), "verification_method": method, "preserved_policies": policies}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = check(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
