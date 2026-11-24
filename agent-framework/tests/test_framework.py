"""Regression checks for ACHE's declared-evidence and completion boundaries."""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT / "agent-framework/scripts"))
from framework_validation import check
from task_integrity import make_receipt


class FrameworkBoundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="ache-v2-case-")
        self.root = Path(self.temp.name)
        shutil.copyfile(str(PROJECT / "AGENTS.md"), str(self.root / "AGENTS.md"))
        shutil.copytree(str(PROJECT / "agent-framework"), str(self.root / "agent-framework"), ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.base = self.root / "agent-framework"
        # Tests exercise declared record behavior, never claim real source verification.
        self.write("project/status.json", {"status": "partial"})
        self.write("project/sources.json", {"sources": []})
        self.write("project/claims.json", {"claims": []})
        self.write("project/assets.json", {"assets": []})
        self.write("project/reviews.json", {"citation_checks": [], "visual_inspections": [], "alignment_checks": []})
        task = self.read("project/task.json")
        task["checks"] = {}
        task["protected_content"] = []
        self.write("project/task.json", task)
        self.write("project/checks.json", {"receipts": []})

    def tearDown(self):
        self.temp.cleanup()

    def read(self, name):
        return json.loads((self.base / name).read_text())

    def write(self, name, value):
        (self.base / name).write_text(json.dumps(value), encoding="utf-8")

    def assertPass(self):
        result = check(self.root)
        self.assertEqual(result["result"], "pass", result["errors"])
        self.assertFalse(result["semantic_validation"])

    def assertError(self, phrase):
        result = check(self.root)
        self.assertEqual(result["result"], "fail")
        self.assertTrue(any(phrase in x for x in result["errors"]), result["errors"])

    def source_claim(self, scope="full_text", authenticity="verified", evidence_type="documented_source", kind="fact", level="detailed"):
        self.write("project/sources.json", {"sources": [{"id": "S1", "kind": "fixture_document", "locator": "fixture-source", "read_scope": scope, "authenticity": authenticity, "evidence_type": evidence_type}]})
        self.write("project/claims.json", {"claims": [{"id": "C1", "text": "Illustrative statement for a record-format test.", "kind": kind, "status": "supported", "assertion_level": level, "source_ids": ["S1"], "evidence_links": [{"source_id": "S1", "location": "fixture paragraph 1", "relation": "supports", "note": "Declared support for the fixture statement."}]}]})

    def test_empty_project_configuration_passes(self):
        self.assertPass()

    def test_located_full_text_support_record_passes(self):
        self.source_claim()
        self.assertPass()

    def test_metadata_can_establish_bibliographic_identity(self):
        self.source_claim(scope="metadata", level="metadata")
        self.assertPass()

    def test_metadata_cannot_establish_detailed_results(self):
        self.source_claim(scope="metadata", level="detailed")
        self.assertError("exceeds reading scope")

    def test_abstract_cannot_establish_empirical_details(self):
        self.source_claim(scope="abstract", level="empirical")
        self.assertError("exceeds reading scope")

    def test_source_ids_alone_do_not_establish_support(self):
        self.source_claim()
        value = self.read("project/claims.json")
        value["claims"][0]["evidence_links"] = []
        self.write("project/claims.json", value)
        self.assertError("no specific supporting evidence link")

    def test_unknown_evidence_id_fails(self):
        self.source_claim()
        value = self.read("project/claims.json")
        value["claims"][0]["source_ids"] = ["MISSING"]
        self.write("project/claims.json", value)
        self.assertError("unknown source_ids")

    def test_unresolved_account_can_remain_attributed(self):
        self.source_claim(authenticity="unresolved", evidence_type="reported_account", kind="reported_account", level="summary")
        self.assertPass()

    def test_unresolved_account_cannot_become_field_observation(self):
        self.source_claim(authenticity="unresolved", evidence_type="reported_account", kind="observation")
        self.assertError("cannot silently become")

    def test_simulation_cannot_establish_empirical_effect(self):
        self.source_claim(evidence_type="simulated_material", level="empirical")
        self.assertError("cannot establish observed effects")

    def test_creative_proposition_does_not_require_empirical_validation(self):
        self.write("project/claims.json", {"claims": [{"id": "P1", "text": "An artistic proposition.", "kind": "proposal", "status": "proposed", "source_ids": []}]})
        self.assertPass()

    def test_generated_image_is_not_a_field_photo(self):
        self.write("project/assets.json", {"assets": [{"id": "A1", "path": "image.png", "kind": "field_photo", "status": "draft", "generated": True, "source_ids": [], "claim_ids": []}]})
        self.assertError("cannot be field photography")

    def test_raster_photo_is_allowed_with_declared_inspection(self):
        (self.root / "photo.jpg").write_bytes(b"test fixture bytes, not a real inspected photo")
        (self.root / "evidence.txt").write_text("Record-format fixture; no actual photography review claimed.")
        receipt = make_receipt(self.root, self.read("project/task.json"), "R1", "visual_inspection", "evidence.txt", [], ["photo.jpg"], "fixture", "fixture")
        self.write("project/checks.json", {"receipts": [receipt]})
        self.write("project/assets.json", {"assets": [{"id": "A1", "path": "photo.jpg", "kind": "field_photo", "status": "final", "generated": False, "source_ids": [], "claim_ids": [], "inspection_id": "V1"}]})
        self.write("project/reviews.json", {"citation_checks": [], "visual_inspections": [{"id": "V1", "status": "pass", "checked_locator": "photo.jpg", "method": "visual_open", "receipt_id": "R1"}], "alignment_checks": []})
        self.assertPass()

    def test_export_success_is_not_visual_inspection(self):
        self.write("project/assets.json", {"assets": [{"id": "A1", "path": "diagram.svg", "kind": "analytical_diagram", "status": "final", "source_ids": [], "claim_ids": []}]})
        self.assertError("lacks a completed inspection record")

    def test_retrieval_error_is_not_a_not_found_verdict(self):
        self.write("project/reviews.json", {"citation_checks": [{"result": "not_found", "method": "same_context_retrieval", "search_status": "timeout", "normal_zero_hits": False, "query_forms": ["title", "author keywords"]}], "visual_inspections": [], "alignment_checks": []})
        self.assertError("not backed by completed varied searches")

    def test_same_context_check_cannot_be_labeled_independent(self):
        task = self.read("project/task.json")
        task["verification_method"] = "same_context_retrieval"
        task["independent_verification"] = True
        self.write("project/task.json", task)
        self.assertError("does not match the declared method")

    def test_required_unperformed_check_blocks_complete_status(self):
        self.write("project/status.json", {"status": "complete"})
        task = self.read("project/task.json")
        task["required_checks"] = ["configuration_integrity"]
        task["checks"] = {}
        self.write("project/task.json", task)
        self.assertError("before required check")

    def test_review_only_does_not_authorize_editing(self):
        task = self.read("project/task.json")
        task.update({"workflow_id": "cross-artifact-review", "required_checks": ["scope_fit", "cross_artifact_alignment"], "checks": {}, "edit_authorized": False, "edits_made": True})
        self.write("project/task.json", task)
        self.assertError("unauthorized edits")

    def test_changed_manual_file_is_detected(self):
        p = self.root / "protected.txt"
        p.write_bytes(b"manual text")
        task = self.read("project/task.json")
        task["protected_paths"] = [{"path": "protected.txt", "sha256": hashlib.sha256(b"original text").hexdigest()}]
        self.write("project/task.json", task)
        self.assertError("Protected file changed")

    def test_original_writing_policy_snapshot_is_preserved(self):
        p = self.base / "policies/anti-defensive-writing.zh.md"
        p.write_bytes(p.read_bytes() + b"\nchanged\n")
        self.assertError("policy snapshot changed")

    def test_missing_workflow_module_is_detected(self):
        value = self.read("workflows.json")
        value["workflows"]["research-quick"]["modules"].append("missing-module")
        self.write("workflows.json", value)
        self.assertError("unknown module")

    def test_configuration_cannot_escape_framework(self):
        value = self.read("registry.json")
        value["references"].append("../AGENTS.md")
        self.write("registry.json", value)
        self.assertError("escapes the framework")

    def test_invalid_ledger_shape_fails_cleanly(self):
        self.write("project/sources.json", [])
        self.assertError("expected a JSON object")

    def test_nonstring_record_values_fail_cleanly(self):
        self.source_claim()
        value = self.read("project/sources.json")
        value["sources"][0]["read_scope"] = []
        self.write("project/sources.json", value)
        self.assertError("invalid reading scope")

    def test_declared_pass_without_version_receipt_fails(self):
        task = self.read("project/task.json")
        task["checks"] = {"scope_fit": {"status": "pass", "evidence": "Unbound fixture statement."}}
        self.write("project/task.json", task)
        self.assertError("Missing version-bound receipt")

    def test_current_receipt_passes_and_changed_dependency_fails(self):
        (self.root / "output.txt").write_text("v1")
        (self.root / "evidence.txt").write_text("Record-shape fixture, not a semantic review.")
        task = self.read("project/task.json")
        receipt = make_receipt(self.root, task, "R", "scope_fit", "evidence.txt", [], ["output.txt"], "fixture", "fixture")
        self.write("project/checks.json", {"receipts": [receipt]})
        task["checks"] = {"scope_fit": {"status": "pass", "evidence": "fixture", "receipt_id": "R"}}
        self.write("project/task.json", task)
        self.assertPass()
        (self.root / "output.txt").write_text("v2")
        self.assertError("Stale receipt dependency")

    def test_old_visual_record_cannot_cover_another_output(self):
        for name in ("old.png", "new.png", "evidence.txt"):
            (self.root / name).write_text("fixture only")
        receipt = make_receipt(self.root, self.read("project/task.json"), "R", "visual_inspection", "evidence.txt", [], ["old.png"], "fixture", "fixture")
        self.write("project/checks.json", {"receipts": [receipt]})
        self.write("project/assets.json", {"assets": [{"id": "A", "path": "new.png", "kind": "generated_image", "status": "final", "source_ids": [], "claim_ids": [], "inspection_id": "V"}]})
        self.write("project/reviews.json", {"visual_inspections": [{"id": "V", "status": "pass", "checked_locator": "old.png", "method": "fixture", "receipt_id": "R"}], "citation_checks": [], "alignment_checks": []})
        self.assertError("checked path is not bound")

    def test_passed_alignment_needs_both_compared_artifacts(self):
        (self.root / "one.txt").write_text("fixture")
        (self.root / "evidence.txt").write_text("fixture")
        receipt = make_receipt(self.root, self.read("project/task.json"), "R", "cross_artifact_alignment", "evidence.txt", ["one.txt"], [], "fixture", "fixture")
        self.write("project/checks.json", {"receipts": [receipt]})
        self.write("project/reviews.json", {"visual_inspections": [], "citation_checks": [], "alignment_checks": [{"status": "pass", "compared_paths": ["one.txt"], "receipt_id": "R"}]})
        self.assertError("needs both compared artifacts")

    def test_nonobject_content_lock_fails_cleanly(self):
        task = self.read("project/task.json")
        task["protected_content"] = ["invalid"]
        self.write("project/task.json", task)
        self.assertError("Invalid content lock record")

    def test_malformed_visual_receipt_dependencies_fail_cleanly(self):
        receipt = {"id": "R", "dependencies": None}
        self.write("project/checks.json", {"receipts": [receipt]})
        self.write("project/reviews.json", {"visual_inspections": [{"id": "V", "status": "pass", "checked_locator": "image.png", "method": "fixture", "receipt_id": "R"}], "citation_checks": [], "alignment_checks": []})
        self.assertError("no checked dependencies")

    def test_final_asset_unknown_source_fails_cleanly(self):
        for name in ("image.png", "evidence.txt"):
            (self.root / name).write_text("fixture only")
        receipt = make_receipt(self.root, self.read("project/task.json"), "R", "visual_inspection", "evidence.txt", [], ["image.png"], "fixture", "fixture")
        self.write("project/checks.json", {"receipts": [receipt]})
        self.write("project/assets.json", {"assets": [{"id": "A", "path": "image.png", "kind": "generated_image", "status": "final", "source_ids": ["missing"], "claim_ids": [], "inspection_id": "V"}]})
        self.write("project/reviews.json", {"visual_inspections": [{"id": "V", "status": "pass", "checked_locator": "image.png", "method": "fixture", "receipt_id": "R"}], "citation_checks": [], "alignment_checks": []})
        self.assertError("unknown source_ids")


if __name__ == "__main__":
    unittest.main()
