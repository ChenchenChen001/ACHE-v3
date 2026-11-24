"""Build a self-contained Markdown guide with exact UTF-8 configuration files."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
from restore_framework import template_records

START = "<!-- ACHE_BUNDLE_START -->\n```json\n"
END = "\n```\n<!-- ACHE_BUNDLE_END -->"


def build(root, destination, mode="snapshot"):
    root, destination = Path(root).resolve(), Path(destination).resolve()
    base = root / "agent-framework"
    registry = json.loads((base / "registry.json").read_text(encoding="utf-8"))
    files = [root / "AGENTS.md"] + sorted(p for p in base.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc")
    records = {str(p.relative_to(root)): p.read_bytes() for p in files}
    if mode == "template":
        records = template_records(records)
    elif mode != "snapshot":
        raise ValueError("Unknown bundle mode")
    payload = {"format": "ache-art-design-project-framework-v3", "version": registry["version"], "mode": mode, "encoding": "per-file", "files": []}
    for name, data in records.items():
        try:
            content, encoding = data.decode("utf-8"), "UTF-8"
        except UnicodeDecodeError:
            content, encoding = base64.b64encode(data).decode("ascii"), "base64"
        payload["files"].append({"path": name, "sha256": hashlib.sha256(data).hexdigest(), "encoding": encoding, "content": content})
    template = (base / "templates/framework-guide.md").read_text(encoding="utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(template.rstrip() + "\n\n" + START + json.dumps(payload, ensure_ascii=False, indent=2) + END + "\n", encoding="utf-8")
    readback = destination.read_text(encoding="utf-8")
    restored = json.loads(readback.split(START, 1)[1].split(END, 1)[0])
    for item in restored["files"]:
        data = base64.b64decode(item["content"], validate=True) if item["encoding"] == "base64" else item["content"].encode("utf-8")
        if hashlib.sha256(data).hexdigest() != item["sha256"] or records[item["path"]] != data:
            raise ValueError("Configuration round-trip mismatch: " + item["path"])
    return {"path": str(destination), "version": registry["version"], "mode": mode, "embedded_files": len(records), "file_size_bytes": destination.stat().st_size, "round_trip": "pass"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--mode", choices=["template", "snapshot"], default="template")
    args = parser.parse_args()
    output = args.output or args.root / "outputs/ACHE_Art_Design_Agent_Framework_v3_20261124.md"
    print(json.dumps(build(args.root, output, args.mode), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
