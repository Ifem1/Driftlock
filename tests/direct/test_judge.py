import json
import pytest
from tests.direct.conftest import addr, capture, warp


def material(request_id="dc-1"):
    return json.dumps({
        "request_id":request_id,"kind":"CURRENT","status":"MATERIAL_CHANGE","source_accessible":True,
        "same_subject":True,"promise_still_supported":False,"current_compliant":False,
        "breach_condition_now_supported":True,"effective_now":True,"basis":"Material relevant change.",
        "baseline_context":{"status":"BASELINE_VERIFIED","source_accessible":True,"same_subject":True,
            "protected_promise_supported":True,"rule_testable":True,"time_scope_valid":True,
            "baseline_compliant":True,"breach_condition_present":False,"basis":"Compliant baseline."},
    })


def verdict(outcome="BREACH"):
    return {
        "outcome": outcome, "breach_supported": outcome == "BREACH", "permitted_by_rule": outcome == "PERMITTED_CHANGE",
        "same_subject": True, "effective_now": True, "basis": "The operative policy now permits commercial licensing contrary to the frozen rule.",
    }


def test_breach_judge_replays_decision_fields(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); _, messages = capture(direct_vm)
    contract = direct_deploy("contracts/breach_judge.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status":200,"body":"Customer data may be licensed to partners."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BREACH_JUDGE_V2.*", json.dumps(verdict()))
    contract.judge_breach("dc-1", addr(direct_alice), "Customer data", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting allowed.", material())
    assert direct_vm.run_validator() is True
    assert contract.get_result("dc-1")["outcome"] == "BREACH"
    assert messages[-1]["on"] == "finalized"


def test_breach_validator_rejects_opposite_outcome(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/breach_judge.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status":200,"body":"Customer data may be licensed to partners."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BREACH_JUDGE_V2.*", json.dumps(verdict()))
    contract.judge_breach("dc-2", addr(direct_alice), "Customer data", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting allowed.", material("dc-2"))
    direct_vm.clear_mocks(); direct_vm.mock_web(r".*example\.com/policy.*", {"status":200,"body":"Customer data may be licensed to partners."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BREACH_JUDGE_V2.*", json.dumps(verdict("PERMITTED_CHANGE")))
    assert direct_vm.run_validator() is False


def test_judge_requires_verified_material_change(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/breach_judge.py", addr(direct_alice)); direct_vm.sender = direct_alice
    with pytest.raises(Exception, match="material-change"):
        contract.judge_breach("dc-x", addr(direct_alice), "Subject", "https://example.com", "Promise", "Rule", "Allowed", '{"status":"NO_RELEVANT_CHANGE"}')


def test_judge_rejects_wrong_registry_sender(direct_vm, direct_deploy, direct_alice, direct_bob):
    warp(direct_vm); contract = direct_deploy("contracts/breach_judge.py", addr(direct_alice)); direct_vm.sender = direct_bob
    with pytest.raises(Exception, match="configured registry"):
        contract.judge_breach("dc-x", addr(direct_bob), "Subject", "https://example.com", "Promise", "Rule", "Allowed", material())


def test_judge_can_finalize_inconclusive_on_uncertain_independent_replay(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/breach_judge.py", addr(direct_alice)); direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*example\.com/policy.*", {"status":200,"body":"The current source is unclear."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BREACH_JUDGE_V2.*", json.dumps(verdict("INCONCLUSIVE")))
    contract.judge_breach("dc-inconclusive", addr(direct_alice), "Customer data", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting allowed.", material("dc-inconclusive"))
    assert direct_vm.run_validator() is True
    assert contract.get_result("dc-inconclusive")["outcome"] == "INCONCLUSIVE"


def test_judge_rejects_material_packet_without_verified_compliant_baseline(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/breach_judge.py", addr(direct_alice)); direct_vm.sender = direct_alice
    invalid = json.loads(material("dc-invalid-baseline"))
    invalid["baseline_context"]["breach_condition_present"] = True
    with pytest.raises(Exception, match="verified compliant semantic baseline"):
        contract.judge_breach("dc-invalid-baseline", addr(direct_alice), "Customer data", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting allowed.", json.dumps(invalid))


def test_judge_rejects_impossible_permitted_verdict(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm); contract = direct_deploy("contracts/breach_judge.py", addr(direct_alice)); direct_vm.sender = direct_alice
    impossible = {**verdict("PERMITTED_CHANGE"), "breach_supported": True}
    direct_vm.mock_web(r".*example\.com/policy.*", {"status":200,"body":"We may license data."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_BREACH_JUDGE_V2.*", json.dumps(impossible))
    with pytest.raises(Exception, match="permitted-change outcome"):
        contract.judge_breach("dc-impossible", addr(direct_alice), "Customer data", "https://example.com/policy", "Data is not sold.", "Licensing is breach.", "Formatting allowed.", material("dc-impossible"))
