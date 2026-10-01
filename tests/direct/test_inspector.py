import json
import hashlib
import pytest
from tests.direct.conftest import addr, capture, warp


def baseline(status="BASELINE_VERIFIED"):
    good = status == "BASELINE_VERIFIED"
    return {
        "status": status, "source_accessible": good, "same_subject": good,
        "protected_promise_supported": good, "rule_testable": good, "time_scope_valid": good,
        "breach_condition_absent": good,
        "basis": "The current official page supports the protected promise and a testable rule." if good else "The source could not be retrieved.",
    }


def current(status="MATERIAL_CHANGE"):
    return {
        "status": status, "source_accessible": True, "same_subject": True,
        "promise_still_supported": False, "relevant_change_detected": status == "MATERIAL_CHANGE",
        "new_conflicting_term": status == "MATERIAL_CHANGE", "effective_now": True,
        "basis": "The current policy introduces a materially conflicting commercial-transfer term.",
    }


def verified_evidence(text="Customer data is not sold."):
    return json.dumps({"status": "BASELINE_VERIFIED", "breach_condition_absent": True, "source_url": "https://example.com/policy",
                       "baseline_text": text, "baseline_digest": hashlib.sha256(text.encode()).hexdigest()})


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
    contract.inspect_current("dc-1", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting is permitted.", verified_evidence())
    assert direct_vm.run_validator() is True
    assert contract.get_result("dc-1")["status"] == "MATERIAL_CHANGE"


def test_inspector_rejects_unconfigured_registry_sender(direct_vm, direct_deploy, direct_alice, direct_bob):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_bob
    with pytest.raises(Exception, match="configured registry"):
        contract.inspect_current("dc-x", addr(direct_bob), "Subject", "https://example.com", "Promise", "Rule", "Allowed", verified_evidence())


def test_verified_baseline_commits_bounded_source_evidence(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data is not sold."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V1.*", json.dumps(baseline()))
    contract.inspect_baseline("dl-3:baseline:1", "dl-3", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Sale is breach.", "Formatting is permitted.")
    result = contract.get_result("dl-3:baseline:1")
    assert result["baseline_text"] == "Customer data is not sold."
    assert result["baseline_digest"] == hashlib.sha256(result["baseline_text"].encode()).hexdigest()
    assert direct_vm.run_validator() is True


def test_unchanged_source_cannot_be_material_change(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data may be commercially licensed."})
    contract.inspect_current("dc-unchanged", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting is permitted.", verified_evidence("Customer data may be commercially licensed."))
    result = contract.get_result("dc-unchanged")
    assert result["status"] == "NO_RELEVANT_CHANGE"
    assert result["new_conflicting_term"] is False
    assert direct_vm.run_validator() is True


def test_tampered_baseline_evidence_rejected(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    packet = json.loads(verified_evidence()); packet["baseline_text"] = "Tampered"
    with pytest.raises(Exception, match="invalid verified baseline evidence"):
        contract.inspect_current("dc-tampered", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting is permitted.", json.dumps(packet))


def test_already_breached_baseline_is_explicit(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Data is not sold. Data may be commercially licensed."})
    answer = {**baseline(), "status": "BASELINE_ALREADY_BREACHED", "breach_condition_absent": False}
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V1.*", json.dumps(answer))
    contract.inspect_baseline("dl-breached:baseline:1", "dl-breached", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Commercial licensing is breach.", "Formatting is permitted.")
    assert contract.get_result("dl-breached:baseline:1")["status"] == "BASELINE_ALREADY_BREACHED"
    assert direct_vm.run_validator() is True


def test_current_validator_rejects_different_fetched_evidence(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data may be licensed to partners."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V1.*", json.dumps(current()))
    contract.inspect_current("dc-drift", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting is permitted.", verified_evidence())
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data may be licensed to affiliates."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V1.*", json.dumps(current()))
    assert direct_vm.run_validator() is False


def test_duplicate_inspection_request_is_rejected(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data is not sold."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V1.*", json.dumps(baseline()))
    args = ("dl-duplicate:baseline:1", "dl-duplicate", addr(direct_alice), "Customer-data policy",
            "https://example.com/policy", "Data is not sold.", "Sale is breach.", "Formatting is permitted.")
    contract.inspect_baseline(*args)
    with pytest.raises(Exception, match="already processed"):
        contract.inspect_baseline(*args)
