import json
import pytest
from tests.direct.conftest import addr, capture, warp


def baseline(status="BASELINE_VERIFIED", **overrides):
    good = status == "BASELINE_VERIFIED"
    value = {
        "status": status, "source_accessible": good, "same_subject": good,
        "protected_promise_supported": good, "rule_testable": good, "time_scope_valid": good,
        "baseline_compliant": good, "breach_condition_present": False,
        "basis": "The current official page supports the protected promise and is compliant." if good else "The baseline could not be certified compliant.",
    }
    value.update(overrides)
    if status == "SOURCE_UNAVAILABLE":
        for field in ("source_accessible", "same_subject", "protected_promise_supported", "rule_testable", "time_scope_valid", "baseline_compliant", "breach_condition_present"):
            value[field] = False
    return value


def current(status="MATERIAL_CHANGE", **overrides):
    unavailable = status == "SOURCE_UNAVAILABLE"
    no_change = status == "NO_RELEVANT_CHANGE"
    value = {
        "status": status, "source_accessible": not unavailable, "same_subject": not unavailable,
        "promise_still_supported": no_change, "current_compliant": no_change,
        "breach_condition_now_supported": status == "MATERIAL_CHANGE", "effective_now": not unavailable and status != "AMBIGUOUS",
        "basis": "Current source is materially non-compliant with an operative breach condition." if status == "MATERIAL_CHANGE" else "The current source remains compliant.",
    }
    if unavailable:
        for field in ("promise_still_supported", "current_compliant", "breach_condition_now_supported", "effective_now"):
            value[field] = False
    value.update(overrides)
    return value


def baseline_packet():
    return json.dumps(baseline())


def test_baseline_replays_stable_fields(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); _, messages = capture(direct_vm)
    contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data is not sold."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V2.*", json.dumps(baseline()))
    contract.inspect_baseline("dl-1:baseline:1", "dl-1", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Sale is breach.", "Formatting is permitted.")
    assert direct_vm.run_validator() is True
    assert contract.get_result("dl-1:baseline:1")["status"] == "BASELINE_VERIFIED"
    assert messages[-1]["on"] == "finalized"


def test_baseline_validator_rejects_semantic_disagreement(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data is not sold."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V2.*", json.dumps(baseline()))
    contract.inspect_baseline("dl-2:baseline:1", "dl-2", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Sale is breach.", "Formatting is permitted.")
    direct_vm.clear_mocks(); direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data may be sold."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V2.*", json.dumps({**baseline(), "status":"PROMISE_NOT_SUPPORTED", "protected_promise_supported":False, "baseline_compliant":False}))
    assert direct_vm.run_validator() is False


def test_current_inspection_detects_material_change(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Customer data may be licensed to partners."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V2.*", json.dumps(current()))
    contract.inspect_current("dc-1", addr(direct_alice), "Customer-data policy", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting is permitted.", baseline_packet())
    assert direct_vm.run_validator() is True
    assert contract.get_result("dc-1")["status"] == "MATERIAL_CHANGE"


def test_inspector_rejects_unconfigured_registry_sender(direct_vm, direct_deploy, direct_alice, direct_bob):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_bob
    with pytest.raises(Exception, match="configured registry"):
        contract.inspect_current("dc-x", addr(direct_bob), "Subject", "https://example.com", "Promise", "Rule", "Allowed", baseline_packet())


def test_clean_compliant_baseline_is_the_only_activating_semantic_outcome(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "We do not sell customer information."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V2.*", json.dumps(baseline()))
    contract.inspect_baseline("dl-clean:baseline:1", "dl-clean", addr(direct_alice), "Data policy", "https://example.com/policy", "Customer information is not sold.", "Selling customer information is breach.", "Formatting permitted.")
    assert direct_vm.run_validator() is True
    assert contract.get_result("dl-clean:baseline:1")["baseline_compliant"] is True


def test_supported_promise_with_existing_breach_is_ambiguous_not_verified(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    result = baseline("AMBIGUOUS", source_accessible=True, same_subject=True,
                      protected_promise_supported=True, rule_testable=True, time_scope_valid=True,
                      baseline_compliant=False, breach_condition_present=True,
                      basis="Page supports no-sale promise but already authorizes commercial licensing.")
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "We do not sell data. We may license it to commercial partners."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V2.*", json.dumps(result))
    contract.inspect_baseline("dl-conflict:baseline:1", "dl-conflict", addr(direct_alice), "Data policy", "https://example.com/policy", "Data is not sold.", "Licensing data is breach.", "Formatting permitted.")
    assert direct_vm.run_validator() is True
    assert contract.get_result("dl-conflict:baseline:1")["status"] == "AMBIGUOUS"
    assert contract.get_result("dl-conflict:baseline:1")["breach_condition_present"] is True


@pytest.mark.parametrize("overrides, message", [
    ({"baseline_compliant": False}, "verified baseline"),
    ({"breach_condition_present": True}, "verified baseline"),
    ({"protected_promise_supported": False}, "verified baseline"),
])
def test_verified_baseline_rejects_contradictory_semantic_fields(direct_vm, direct_deploy, direct_alice, overrides, message):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "Conflicting page."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BASELINE_V2.*", json.dumps(baseline(**overrides)))
    with pytest.raises(Exception, match=message):
        contract.inspect_baseline("dl-invalid:baseline:1", "dl-invalid", addr(direct_alice), "Data policy", "https://example.com/policy", "Data is not sold.", "Sale is breach.", "Formatting permitted.")


@pytest.mark.parametrize("page", [
    "We do not sell customer data.\n\nPrivacy | Contact | Cookies",
    "We do not sell customer data. Our office moved to Lagos and our help center link changed.",
    "We do not sell customer data. We updated headings, typography, and page navigation.",
    "We do not sell customer data. We may publish a new policy date next quarter.",
])
def test_unchanged_formatting_and_unrelated_source_edits_remain_compliant(direct_vm, direct_deploy, direct_alice, page):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": page})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V2.*", json.dumps(current("NO_RELEVANT_CHANGE")))
    contract.inspect_current("dc-clean", addr(direct_alice), "Data policy", "https://example.com/policy", "Customer data is not sold.", "Sale is breach.", "Formatting and navigation changes permitted.", baseline_packet())
    assert direct_vm.run_validator() is True
    result = contract.get_result("dc-clean")
    assert result["status"] == "NO_RELEVANT_CHANGE" and result["current_compliant"] is True
    assert result["baseline_context"]["baseline_compliant"] is True


def test_expressly_permitted_semantic_change_does_not_trigger_inspection(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "We do not sell data. We may share it with a processor to provide the requested service."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V2.*", json.dumps(current("NO_RELEVANT_CHANGE")))
    contract.inspect_current("dc-permitted", addr(direct_alice), "Data policy", "https://example.com/policy", "Customer data is not sold.", "Sale or commercial licensing is breach.", "Service-provider processing is permitted.", baseline_packet())
    assert direct_vm.run_validator() is True


def test_current_supported_breach_condition_is_material_and_contains_baseline_context(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "We now license customer data to commercial partners."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V2.*", json.dumps(current()))
    contract.inspect_current("dc-material", addr(direct_alice), "Data policy", "https://example.com/policy", "Customer data is not sold.", "Commercial licensing is breach.", "Formatting permitted.", baseline_packet())
    assert direct_vm.run_validator() is True
    result = contract.get_result("dc-material")
    assert result["status"] == "MATERIAL_CHANGE"
    assert result["baseline_context"]["status"] == "BASELINE_VERIFIED"
    assert result["baseline_context"]["breach_condition_present"] is False


def test_validator_rejects_material_claim_when_current_page_remains_compliant(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "We do not sell customer data."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V2.*", json.dumps(current()))
    contract.inspect_current("dc-false-material", addr(direct_alice), "Data policy", "https://example.com/policy", "Customer data is not sold.", "Commercial licensing is breach.", "Formatting permitted.", baseline_packet())
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "We do not sell customer data."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V2.*", json.dumps(current("NO_RELEVANT_CHANGE")))
    assert direct_vm.run_validator() is False


def test_validator_rejects_suppressed_current_breach_condition(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "We now license data to commercial partners."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V2.*", json.dumps(current("NO_RELEVANT_CHANGE")))
    contract.inspect_current("dc-suppressed", addr(direct_alice), "Data policy", "https://example.com/policy", "Customer data is not sold.", "Commercial licensing is breach.", "Formatting permitted.", baseline_packet())
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 200, "body": "We now license data to commercial partners."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V2.*", json.dumps(current()))
    assert direct_vm.run_validator() is False


def test_unavailable_current_source_has_no_positive_semantic_fields(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/source_inspector.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status": 503, "body": ""})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_SOURCE_INSPECTION_V2.*", json.dumps(current("SOURCE_UNAVAILABLE")))
    contract.inspect_current("dc-offline", addr(direct_alice), "Data policy", "https://example.com/policy", "Customer data is not sold.", "Sale is breach.", "Formatting permitted.", baseline_packet())
    assert direct_vm.run_validator() is True
    result = contract.get_result("dc-offline")
    assert result["status"] == "SOURCE_UNAVAILABLE"
    assert result["source_accessible"] is False and result["current_compliant"] is False
