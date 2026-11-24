"""Regression cases for changed artifacts, local protection and safe portability."""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "agent-framework/scripts"))
from task_integrity import capture_lock, lock_issues, make_receipt, receipt_issues, review_svg_edit, review_text_edit
from restore_framework import restore, unpack
from bundle_framework import build
from task_guard import environment
from framework_validation import check


class BoundChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ache-v3-check-")
        self.root = Path(self.temp.name)
        self.task = {"id": "fixture", "operation": "review", "scope": "fixture"}
        for name, value in [("source.txt", "original input"), ("output.txt", "original output"), ("evidence.txt", "fixture record")]:
            (self.root / name).write_text(value)

    def tearDown(self):
        self.temp.cleanup()

    def receipt(self, inputs=None, outputs=None):
        return make_receipt(self.root, self.task, "R1", "alignment", "evidence.txt", inputs or ["source.txt"], outputs or ["output.txt"], "fixture", "fixture")

    def test_unchanged_check_remains_current(self):
        self.assertEqual(receipt_issues(self.root, self.task, self.receipt(), "alignment"), [])

    def test_changed_output_invalidates_old_check(self):
        receipt = self.receipt()
        (self.root / "output.txt").write_text("changed output")
        self.assertTrue(any("Stale" in x for x in receipt_issues(self.root, self.task, receipt)))

    def test_changed_source_invalidates_old_comparison(self):
        receipt = self.receipt()
        (self.root / "source.txt").write_text("new manuscript")
        self.assertTrue(any("source.txt" in x for x in receipt_issues(self.root, self.task, receipt)))

    def test_unrelated_change_preserves_other_check(self):
        receipt = make_receipt(self.root, self.task, "R2", "another", "evidence.txt", ["source.txt"], [], "fixture", "fixture")
        (self.root / "output.txt").write_text("changed")
        self.assertEqual(receipt_issues(self.root, self.task, receipt), [])

    def test_changed_evidence_invalidates_receipt(self):
        receipt = self.receipt()
        (self.root / "evidence.txt").write_text("rewritten evidence")
        self.assertTrue(receipt_issues(self.root, self.task, receipt))

    def test_changed_task_scope_invalidates_receipt(self):
        receipt = self.receipt()
        self.task["scope"] = "another scope"
        self.assertTrue(receipt_issues(self.root, self.task, receipt))

    def test_changed_check_status_does_not_self_invalidate(self):
        receipt = self.receipt()
        self.task["checks"] = {"alignment": {"status": "pass"}}
        self.assertEqual(receipt_issues(self.root, self.task, receipt), [])

    def test_gate_cannot_reuse_another_gate_receipt(self):
        self.assertTrue(receipt_issues(self.root, self.task, self.receipt(), "visual_inspection"))

    def test_missing_dependency_is_inconclusive(self):
        receipt = self.receipt()
        (self.root / "source.txt").unlink()
        self.assertTrue(any("unavailable" in x for x in receipt_issues(self.root, self.task, receipt)))

    def test_dependency_cannot_escape_project(self):
        receipt = self.receipt()
        receipt["dependencies"][0]["path"] = "../external"
        self.assertTrue(receipt_issues(self.root, self.task, receipt))

    def test_local_edit_can_preserve_locked_title(self):
        p = self.root / "output.txt"
        p.write_text("Title\nold body")
        lock = capture_lock(self.root, "title", "output.txt", "text_fragment", {"text": "Title"})
        p.write_text("Title\nnew body")
        self.assertEqual(lock_issues(self.root, lock), [])

    def test_changed_or_duplicated_locked_title_fails(self):
        p = self.root / "output.txt"
        p.write_text("Title\nbody")
        lock = capture_lock(self.root, "title", "output.txt", "text_fragment", {"text": "Title"})
        p.write_text("Title\nTitle\nbody")
        self.assertTrue(lock_issues(self.root, lock))

    def test_section_lock_preserves_material_condition(self):
        p = self.root / "output.txt"
        p.write_text("A[condition]subject to agreement[end]B")
        lock = capture_lock(self.root, "condition", "output.txt", "text_section", {"start": "[condition]", "end": "[end]"})
        p.write_text("C[condition]subject to agreement[end]D")
        self.assertEqual(lock_issues(self.root, lock), [])
        p.write_text("C[condition]guaranteed[end]D")
        self.assertTrue(lock_issues(self.root, lock))

    def test_allowed_text_diff_rejects_unrelated_edit(self):
        before = "fixed[start]old[end]protected"
        self.assertTrue(review_text_edit(before, "fixed[start]new[end]protected", [{"start": "[start]", "end": "[end]"}])["outside_scope_unchanged"])
        self.assertFalse(review_text_edit(before, "changed[start]new[end]protected", [{"start": "[start]", "end": "[end]"}])["outside_scope_unchanged"])

    def svg(self):
        return b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><g transform="translate(0,0)"><rect id="keep" x="0" width="20"/><text id="edit">Old</text></g><image id="i1" href="a.png"/><image id="i2" href="b.png"/></svg>'

    def test_svg_label_edit_preserves_protected_geometry(self):
        p = self.root / "drawing.svg"
        p.write_bytes(self.svg())
        lock = capture_lock(self.root, "shape", "drawing.svg", "svg_element", {"id": "keep"})
        p.write_bytes(self.svg().replace(b">Old<", b">New<"))
        self.assertEqual(lock_issues(self.root, lock), [])

    def test_svg_ancestor_transform_is_part_of_protection(self):
        p = self.root / "drawing.svg"
        p.write_bytes(self.svg())
        lock = capture_lock(self.root, "shape", "drawing.svg", "svg_element", {"id": "keep"})
        p.write_bytes(self.svg().replace(b"translate(0,0)", b"translate(50,0)"))
        self.assertTrue(lock_issues(self.root, lock))

    def test_svg_reordered_images_are_detected(self):
        p = self.root / "drawing.svg"
        p.write_bytes(self.svg())
        lock = capture_lock(self.root, "order", "drawing.svg", "svg_image_order", {})
        p.write_bytes(self.svg().replace(b'id="i1" href="a.png"', b'id="temp" href="b.png"').replace(b'id="i2" href="b.png"', b'id="i1" href="a.png"').replace(b'id="temp"', b'id="i2"'))
        self.assertTrue(lock_issues(self.root, lock))

    def test_svg_duplicate_id_is_rejected(self):
        p = self.root / "drawing.svg"
        p.write_bytes(self.svg().replace(b'id="edit"', b'id="keep"'))
        with self.assertRaises(ValueError):
            capture_lock(self.root, "shape", "drawing.svg", "svg_element", {"id": "keep"})

    def test_allowed_svg_diff_preserves_other_shapes(self):
        before = self.svg()
        self.assertTrue(review_svg_edit(before, before.replace(b">Old<", b">New<"), ["edit"])["outside_scope_unchanged"])
        self.assertFalse(review_svg_edit(before, before.replace(b'width="20"', b'width="30"'), ["edit"])["outside_scope_unchanged"])


class PortableBundle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="ache-v3-portable-")
        cls.guide = Path(cls.temp.name) / "framework.md"
        build(PROJECT, cls.guide)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_bundle_digests_round_trip(self):
        files = unpack(self.guide)
        self.assertIn("agent-framework/scripts/task_integrity.py", files)

    def test_template_preserves_existing_instructions_and_resets_checks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "AGENTS.md").write_bytes(b"Existing user rules.\n")
            result = restore(self.guide, root)
            self.assertTrue((root / "AGENTS.md").read_bytes().startswith(b"Existing user rules.\n"))
            self.assertFalse(result["inherited_checks_passed"])
            task = json.loads((root / "agent-framework/project/task.json").read_text())
            self.assertEqual(task["checks"], {})
            self.assertFalse((root / "agent-framework/project/evaluation").exists())
            self.assertEqual(check(root)["result"], "pass")
            self.assertEqual(restore(self.guide, root)["written_files"], 0)

    def test_shareable_bundle_excludes_private_records_before_delivery(self):
        guide = Path(self.temp.name) / "shareable.md"
        build(PROJECT, guide, "template")
        files = unpack(guide)
        self.assertFalse(any(x.startswith("agent-framework/project/evaluation/") for x in files))
        self.assertEqual(json.loads(files["agent-framework/project/checks.json"])["receipts"], [])

    def test_collision_does_not_partially_write_project(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "agent-framework").mkdir()
            (root / "agent-framework/registry.json").write_text("existing")
            with self.assertRaises(ValueError):
                restore(self.guide, root)
            self.assertFalse((root / "AGENTS.md").exists())

    def test_host_capabilities_do_not_invent_external_tools_or_costs(self):
        result = environment()
        self.assertEqual(result["image_generation"], "requires_host_tool_discovery")
        self.assertIsNone(result["token_usage"])
        self.assertIsNone(result["monetary_cost"])


if __name__ == "__main__":
    unittest.main()
