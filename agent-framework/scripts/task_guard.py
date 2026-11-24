"""Inspect current check receipts and content locks without changing their statuses."""
import argparse
import importlib.util
import json
import shutil
from pathlib import Path
from task_integrity import lock_issues, receipt_issues


def environment():
    return {"python_standard_library": True,
            "pdf_render": shutil.which("pdftoppm"),
            "svg_preview_candidate": shutil.which("qlmanage"),
            "pdf_text": bool(importlib.util.find_spec("pypdf")),
            "docx_edit": bool(importlib.util.find_spec("docx")),
            "image_generation": "requires_host_tool_discovery",
            "indesign_edit": "requires_host_application_discovery",
            "remote_version_refresh": "requires_connected_source_read",
            "token_usage": None, "monetary_cost": None,
            "probe_note": "Discovery only; an installed command is not a successful export or inspection."}


def inspect(root):
    base = Path(root) / "agent-framework/project"
    task = json.loads((base / "task.json").read_text(encoding="utf-8"))
    receipts = {r["id"]: r for r in json.loads((base / "checks.json").read_text(encoding="utf-8")).get("receipts", [])}
    checks = {}
    for gate, record in task.get("checks", {}).items():
        if record.get("status") == "pass":
            issues = receipt_issues(root, task, receipts.get(record.get("receipt_id")), gate)
            checks[gate] = {"declared_status": "pass", "effective_status": "stale" if issues else "pass", "issues": issues}
        else:
            checks[gate] = {"declared_status": record.get("status"), "effective_status": record.get("status")}
    protections = [{"id": x.get("id"), "issues": lock_issues(root, x)} for x in task.get("protected_content", [])]
    return {"checks": checks, "protections": protections, "semantic_validation": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["status", "environment"])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    result = environment() if args.command == "environment" else inspect(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.command == "status":
        return int(any(x.get("effective_status") == "stale" for x in result["checks"].values()) or any(x["issues"] for x in result["protections"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
