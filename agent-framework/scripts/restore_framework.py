"""Restore an ACHE guide without replacing existing user instructions or conflicts.

Default template mode resets project records and omits private pilot material.
Snapshot mode restores the recorded state, whose receipts require checking again.
"""
import argparse
import base64
import hashlib
import json
import tempfile
from pathlib import Path, PurePosixPath

START = "<!-- ACHE_BUNDLE_START -->\n```json\n"
END = "\n```\n<!-- ACHE_BUNDLE_END -->"
OPEN = "<!-- ACHE_PROJECT_FRAMEWORK_START -->"
CLOSE = "<!-- ACHE_PROJECT_FRAMEWORK_END -->"


def unpack(guide):
    text = Path(guide).read_text(encoding="utf-8")
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("Missing or ambiguous ACHE bundle")
    payload = json.loads(text.split(START, 1)[1].split(END, 1)[0])
    if payload.get("format") not in {"ache-art-design-project-framework-v2", "ache-art-design-project-framework-v3"}:
        raise ValueError("Unknown ACHE bundle format")
    files = {}
    for item in payload["files"]:
        name = item["path"]
        path = PurePosixPath(name)
        if (not name or "\\" in name or path.is_absolute() or ".." in path.parts or ":" in name
                or str(path) != name or (name != "AGENTS.md" and not name.startswith("agent-framework/")) or name in files):
            raise ValueError("Unsafe or duplicate bundle path")
        encoding = item.get("encoding", "UTF-8")
        if encoding not in {"UTF-8", "base64"}:
            raise ValueError("Unknown bundle encoding")
        data = base64.b64decode(item["content"], validate=True) if encoding == "base64" else item["content"].encode("utf-8")
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError("Bundle digest mismatch: " + name)
        files[name] = data
    if "AGENTS.md" not in files or "agent-framework/registry.json" not in files:
        raise ValueError("Incomplete framework bundle")
    return files


def template_records(files):
    files = {k: v for k, v in files.items() if not k.startswith("agent-framework/project/")}
    def add(name, value):
        files["agent-framework/project/" + name] = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    add("brief.json", {"project_type": "mixed", "title": "New ACHE project", "unknowns": ["Read current user material before selecting a workflow."]})
    add("task.json", {"id": "ACHE-new-project", "workflow_id": "framework-maintenance", "operation": "configure", "depth": "quick", "scope": "template_setup", "required_checks": [], "check_exemptions": {k: "Template restored; no task or verified outputs claimed." for k in ["source_grounding", "configuration_integrity", "policy_integrity", "delivery_integrity"]}, "checks": {}, "verification_method": "not_run", "independent_verification": False, "edit_authorized": False, "edits_made": False, "protected_paths": [], "protected_content": []})
    add("status.json", {"status": "partial", "scope": "template_setup", "next_action": "Read the current request, choose a workflow and run applicable checks."})
    for name, key in [("sources.json", "sources"), ("claims.json", "claims"), ("assets.json", "assets"), ("checks.json", "receipts")]:
        add(name, {key: []})
    add("reviews.json", {"visual_inspections": [], "citation_checks": [], "alignment_checks": []})
    files["agent-framework/project/decisions.md"] = b"# Project decisions\n\nNo project decisions recorded yet.\n"
    return files


def restore(guide, destination, mode="template"):
    files = unpack(guide)
    if mode == "template":
        files = template_records(files)
    elif mode != "snapshot":
        raise ValueError("Unknown restore mode")
    root = Path(destination).resolve()
    writes = {}
    for name, data in files.items():
        target = root / name
        try:
            target.resolve().relative_to(root)
        except ValueError:
            raise ValueError("Restore target escapes project")
        if target.is_symlink() or any(p.is_symlink() for p in target.parents if p != root.parent):
            raise ValueError("Restore target uses a symlink")
        if target.exists():
            if not target.is_file():
                raise ValueError("Restore target is not a file")
            existing = target.read_bytes()
            if existing == data:
                continue
            if name != "AGENTS.md":
                raise ValueError("Existing file conflict; nothing written: " + name)
            section = (OPEN + "\n").encode() + data + ("\n" + CLOSE + "\n").encode()
            if section in existing:
                continue
            if OPEN.encode() in existing or CLOSE.encode() in existing:
                raise ValueError("Existing ACHE instructions differ; merge explicitly")
            # Keep all existing bytes in order, then append a delimited entry.
            data = existing + b"\n\n" + section
        writes[name] = data
    # Preflight every collision before touching the destination.
    root.mkdir(parents=True, exist_ok=True)
    for name, data in writes.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=target.parent, delete=False) as stream:
            stream.write(data)
            temporary = Path(stream.name)
        temporary.replace(target)
    return {"mode": mode, "written_files": len(writes), "existing_instructions_preserved": True,
            "inherited_checks_passed": False, "private_pilot_material_included": mode == "snapshot"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guide", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("--mode", choices=["template", "snapshot"], default="template")
    args = parser.parse_args()
    print(json.dumps(restore(args.guide, args.destination, args.mode), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
