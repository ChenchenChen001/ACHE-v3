"""Version-bound check receipts and scoped content locks (standard library only).

Receipts record a performed check; hashes detect changed inputs, not truthful review.
All persisted paths are relative to the project. External sources require refreshed,
versioned snapshots before a new check; this module does not poll remote services.
"""
import copy
import hashlib
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def local_path(root, name):
    if not isinstance(name, str) or not name.strip() or Path(name).is_absolute():
        raise ValueError("Expected a relative project path")
    root = Path(root).resolve()
    result = (root / name).resolve()
    try:
        result.relative_to(root)
    except ValueError:
        raise ValueError("Path escapes the project: " + name)
    return result


def fingerprint(root, name, role="input"):
    if role not in {"input", "output", "evidence"}:
        raise ValueError("Unknown dependency role")
    return {"path": name, "sha256": digest(local_path(root, name).read_bytes()), "role": role}


def task_digest(task):
    # These four fields are results/annotations, never the scope of the check.
    context = {k: v for k, v in task.items() if k not in {"checks", "notes", "metrics", "history"}}
    return digest(canonical(context))


def make_receipt(root, task, identifier, gate, evidence_path, inputs, outputs, scope, method):
    if not all(isinstance(x, str) and x.strip() for x in (identifier, gate, scope, method, task.get("id"))):
        raise ValueError("Receipt needs task, gate, scope, method and identity")
    if not inputs and not outputs:
        raise ValueError("Receipt has no checked dependencies")
    dependencies = [fingerprint(root, p, "input") for p in inputs]
    dependencies += [fingerprint(root, p, "output") for p in outputs]
    if len({x["path"] for x in dependencies}) != len(dependencies):
        raise ValueError("Duplicate receipt dependency")
    return {"id": identifier, "task_id": task["id"], "task_context_sha256": task_digest(task),
            "gate": gate, "scope": scope, "method": method,
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "evidence": fingerprint(root, evidence_path, "evidence"), "dependencies": dependencies}


def receipt_issues(root, task, receipt, gate=None):
    issues = []
    if not isinstance(receipt, dict):
        return ["Missing version-bound receipt"]
    if receipt.get("task_id") != task.get("id") or receipt.get("task_context_sha256") != task_digest(task):
        issues.append("Receipt belongs to another task or changed task scope")
    if gate and receipt.get("gate") != gate:
        issues.append("Receipt gate does not match the check")
    for field in ("id", "gate", "scope", "method", "recorded_at"):
        if not isinstance(receipt.get(field), str) or not receipt[field].strip():
            issues.append("Receipt missing " + field)
    dependencies = receipt.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies:
        issues.append("Receipt has no checked dependencies")
        dependencies = []
    seen = set()
    for item in dependencies + [receipt.get("evidence")]:
        if not isinstance(item, dict):
            issues.append("Malformed receipt dependency")
            continue
        name = item.get("path")
        if not isinstance(name, str) or item.get("role") not in {"input", "output", "evidence"}:
            issues.append("Malformed dependency path or role")
            continue
        key = (name, item["role"])
        if key in seen:
            issues.append("Duplicate receipt dependency: " + name)
        seen.add(key)
        try:
            current = digest(local_path(root, name).read_bytes())
            if current != item.get("sha256"):
                issues.append("Stale receipt dependency: " + name)
        except (OSError, ValueError):
            issues.append("Receipt dependency unavailable: " + name)
    return issues


def _section(text, selector):
    start, end = selector.get("start"), selector.get("end")
    if not all(isinstance(x, str) and x for x in (start, end)) or start == end:
        raise ValueError("Section needs distinct start and end markers")
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError("Section markers missing or ambiguous")
    a = text.index(start) + len(start)
    b = text.index(end)
    if b < a:
        raise ValueError("Section markers reversed")
    return a, b


def _svg(data):
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise ValueError("SVG entities are unsupported")
    try:
        tree = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError("Invalid SVG") from exc
    if tree.tag.split("}")[-1] != "svg":
        raise ValueError("Expected SVG root")
    found, parents = {}, {}
    for element in tree.iter():
        if element.get("id"):
            if element.get("id") in found:
                raise ValueError("Duplicate SVG id")
            found[element.get("id")] = element
        for child in element:
            parents[child] = element
    return tree, found, parents


def _node(element):
    return [element.tag, sorted(element.attrib.items()), element.text or "", element.tail or "", [_node(x) for x in element]]


def selection_bytes(data, kind, selector):
    if not isinstance(selector, dict):
        raise ValueError("Protection selector must be an object")
    if kind == "text_fragment":
        text, fragment = data.decode("utf-8"), selector.get("text")
        if not isinstance(fragment, str) or not fragment:
            raise ValueError("Empty protected fragment")
        count = text.count(fragment)
        if count != selector.get("count", 1):
            raise ValueError("Protected fragment changed, missing or duplicated")
        return canonical({"text": fragment, "count": count})
    if kind == "text_section":
        text = data.decode("utf-8")
        a, b = _section(text, selector)
        return text[a:b].encode("utf-8")
    tree, found, parents = _svg(data)
    if kind == "svg_element":
        identifier = selector.get("id")
        if not isinstance(identifier, str) or identifier not in found:
            raise ValueError("Protected SVG element missing")
        element, ancestry = found[identifier], []
        parent = parents.get(element)
        while parent is not None:
            ancestry.append([parent.tag, sorted(parent.attrib.items())])
            parent = parents.get(parent)
        # Ancestor transforms/viewBox and global styles/defs also affect an object.
        context = [_node(x) for x in tree.iter() if x.tag.split("}")[-1] in {"style", "defs"}]
        return canonical({"element": _node(element), "ancestors": ancestry, "context": context})
    if kind == "svg_image_order":
        return canonical([[x.get("id"), x.get("href") or x.get("{http://www.w3.org/1999/xlink}href")]
                          for x in tree.iter() if x.tag.split("}")[-1] == "image"])
    raise ValueError("Unsupported protection kind: " + str(kind))


def capture_lock(root, identifier, path, kind, selector):
    return {"id": identifier, "path": path, "kind": kind, "selector": copy.deepcopy(selector),
            "sha256": digest(selection_bytes(local_path(root, path).read_bytes(), kind, selector))}


def lock_issues(root, lock):
    if not isinstance(lock, dict) or not isinstance(lock.get("id"), str) or not lock["id"]:
        return ["Invalid content lock identity"]
    try:
        actual = digest(selection_bytes(local_path(root, lock.get("path")).read_bytes(), lock.get("kind"), lock.get("selector")))
        if actual != lock.get("sha256"):
            return ["Protected content changed: " + lock["id"]]
    except (OSError, ValueError, UnicodeError, TypeError) as exc:
        return ["Protected content unavailable or changed: " + lock["id"] + " (" + str(exc) + ")"]
    return []


def review_text_edit(before, after, allowed_sections):
    """Compare exact UTF-8 text outside explicitly authorized marker pairs."""
    def mask(text):
        ranges = sorted(_section(text, s) for s in allowed_sections)
        if any(ranges[i][1] > ranges[i + 1][0] for i in range(len(ranges) - 1)):
            raise ValueError("Overlapping authorized text sections")
        for a, b in reversed(ranges):
            text = text[:a] + "[ACHE_AUTHORIZED_SECTION]" + text[b:]
        return text
    return {"outside_scope_unchanged": mask(before) == mask(after), "method": "exact-text-outside-marker-pairs"}


def review_svg_edit(before, after, allowed_ids):
    """Compare SVG structure outside authorized element subtrees, with IDs retained."""
    def mask(data):
        tree, found, _ = _svg(data)
        if len(allowed_ids) != len(set(allowed_ids)) or any(x not in found for x in allowed_ids):
            raise ValueError("Missing or duplicate authorized SVG id")
        for identifier in allowed_ids:
            element = found[identifier]
            tail = element.tail
            element.clear()
            element.set("id", identifier)
            element.tail = tail
        return canonical(_node(tree))
    return {"outside_scope_unchanged": mask(before) == mask(after), "method": "svg-structure-outside-authorized-ids"}
