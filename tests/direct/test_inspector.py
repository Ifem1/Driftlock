import json
import pytest
from tests.direct.conftest import addr, capture, warp


def baseline(status="BASELINE_VERIFIED"):
    good = status == "BASELINE_VERIFIED"
    return {
        "status": status, "source_accessible": good, "same_subject": good,
        "protected_promise_supported": good, "rule_testable": good, "time_scope_valid": good,
        "basis": "The current official page supports the protected promise and a testable rule." if good else "The source could not be retrieved.",
    }


def current(status="MATERIAL_CHANGE"):
    return {
        "status": status, "source_accessible": True, "same_subject": True,
        "promise_still_supported": False, "relevant_change_detected": status == "MATERIAL_CHANGE",
        "new_conflicting_term": status == "MATERIAL_CHANGE", "effective_now": True,
        "basis": "The current policy introduces a materially conflicting commercial-transfer term.",
    }


def test_baseline_replays_stable_fields(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); _, messages = capture(direct_vm)
    contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data is not sold."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V1.*", json.dumps(baseline()))
    contract.inspect_baseline("dl-1:baseline:1", "dl-1", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Sale is breach.", "Formatting is permitted.")
    assert direct_vm.run_validator() is True
    assert contract.get_result("dl-1:baseline:1")["status"] == "BASELINE_VERIFIED"
    assert messages[-1]["on"] == "finalized"


def test_baseline_validator_rejects_semantic_disagreement(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data is not sold."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V1.*", json.dumps(baseline()))
    contract.inspect_baseline("dl-2:baseline:1", "dl-2", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Sale is breach.", "Formatting is permitted.")
    direct_vm.clear_mocks(); direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data may be sold."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V1.*", json.dumps({**baseline(), "status":"PROMISE_NOT_SUPPORTED", "protected_promise_supported":False}))
    assert direct_vm.run_validator() is False


def test_current_inspection_detects_material_change(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data may be licensed to partners."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V1.*", json.dumps(current()))
    contract.inspect_current("dc-1", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting is permitted.")
    assert direct_vm.run_validator() is True
    assert contract.get_result("dc-1")["status"] == "MATERIAL_CHANGE"


def test_inspector_rejects_unconfigured_registry_sender(direct_vm, direct_deploy, direct_alice, direct_bob):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_bob
    with pytest.raises(Exception, match="configured registry"):
        contract.inspect_current("dc-x", addr(direct_bob), "Subject", "https://example.com", "Promise", "Rule", "Allowed")
