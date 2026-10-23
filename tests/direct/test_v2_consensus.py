import hashlib
import json

from tests.direct.conftest import addr, capture, warp
from tests.direct.test_inspector import baseline
from tests.direct.test_judge import verdict
from tests.direct.test_v2_registry import POLICY, artifact, canonical, current_packet, evidence


def normalized_policy():
    return {**POLICY, "sources": [{**source, "publisher": source["publisher"].lower()}
                                  for source in POLICY["sources"]]}


def digest(policy):
    return hashlib.sha256(canonical(policy).encode()).hexdigest()


def test_policy_baseline_replays_complete_artifacts(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm)
    _, messages = capture(direct_vm)
    inspector = direct_deploy("contracts/source_inspector.py", addr(direct_alice))
    direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*primary\.example/privacy.*", {"status": 200, "body": "No sale of data."})
    direct_vm.mock_web(r".*observer\.example/report.*", {"status": 200, "body": "Observer confirms no sale."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_POLICY_EVIDENCE_V1.*", json.dumps({
        "primary": baseline(), "corroboration": ["SUPPORTS"]}))
    policy = normalized_policy()
    inspector.inspect_policy_baseline("dl-1:baseline:1", "dl-1", addr(direct_alice), "Data policy",
                                      "Data is not sold.", "Sale constitutes breach.", "Formatting allowed.",
                                      canonical(policy), digest(policy))
    result = inspector.get_result("dl-1:baseline:1")
    assert result["status"] == "BASELINE_VERIFIED"
    assert result["evidence"][0]["artifact"]["rendered_sha256"]
    assert direct_vm.run_validator() is True
    assert messages[-1]["on"] == "finalized"


def test_single_corroborator_scalar_is_normalized_and_replayed(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm)
    inspector = direct_deploy("contracts/source_inspector.py", addr(direct_alice))
    direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*primary\.example/privacy.*", {"status": 200, "body": "No sale of data."})
    direct_vm.mock_web(r".*observer\.example/report.*", {"status": 200, "body": "Observer confirms no sale."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_POLICY_EVIDENCE_V1.*", json.dumps({
        "primary": baseline(), "corroboration": "SUPPORTS"}))
    policy = normalized_policy()
    inspector.inspect_policy_baseline("dl-scalar:baseline:1", "dl-scalar", addr(direct_alice), "Data policy",
                                      "Data is not sold.", "Sale constitutes breach.", "Formatting allowed.",
                                      canonical(policy), digest(policy))
    result = inspector.get_result("dl-scalar:baseline:1")
    assert result["status"] == "BASELINE_VERIFIED"
    assert result["corroboration"] == ["SUPPORTS"]
    assert direct_vm.run_validator() is True


def test_policy_validator_rejects_changed_evidence(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm)
    inspector = direct_deploy("contracts/source_inspector.py", addr(direct_alice))
    direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*primary\.example/privacy.*", {"status": 200, "body": "No sale of data."})
    direct_vm.mock_web(r".*observer\.example/report.*", {"status": 200, "body": "Observer confirms no sale."})
    response = json.dumps({"primary": baseline(), "corroboration": ["SUPPORTS"]})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_POLICY_EVIDENCE_V1.*", response)
    policy = normalized_policy()
    inspector.inspect_policy_baseline("dl-2:baseline:1", "dl-2", addr(direct_alice), "Data policy",
                                      "Data is not sold.", "Sale constitutes breach.", "Formatting allowed.",
                                      canonical(policy), digest(policy))
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*primary\.example/privacy.*", {"status": 200, "body": "Data may be sold now."})
    direct_vm.mock_web(r".*observer\.example/report.*", {"status": 200, "body": "Observer confirms no sale."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_POLICY_EVIDENCE_V1.*", response)
    assert direct_vm.run_validator() is False


def test_contradiction_blocks_verified_baseline(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm)
    inspector = direct_deploy("contracts/source_inspector.py", addr(direct_alice))
    direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*primary\.example/privacy.*", {"status": 200, "body": "No sale of data."})
    direct_vm.mock_web(r".*observer\.example/report.*", {"status": 200, "body": "Observer contradicts claim."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_POLICY_EVIDENCE_V1.*", json.dumps({
        "primary": baseline(), "corroboration": ["CONTRADICTS"]}))
    policy = normalized_policy()
    inspector.inspect_policy_baseline("dl-3:baseline:1", "dl-3", addr(direct_alice), "Data policy",
                                      "Data is not sold.", "Sale constitutes breach.", "Formatting allowed.",
                                      canonical(policy), digest(policy))
    result = inspector.get_result("dl-3:baseline:1")
    assert result["status"] == "AMBIGUOUS"
    assert result["baseline_compliant"] is False


def test_oversized_corroborator_cannot_count_as_complete(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm)
    inspector = direct_deploy("contracts/source_inspector.py", addr(direct_alice))
    direct_vm.sender = direct_alice
    direct_vm.mock_web(r".*primary\.example/privacy.*", {"status": 200, "body": "No sale of data."})
    direct_vm.mock_web(r".*observer\.example/report.*", {"status": 200, "body": "X" * 6001})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_POLICY_EVIDENCE_V1.*", json.dumps({
        "primary": baseline(), "corroboration": ["INCONCLUSIVE"]}))
    policy = normalized_policy()
    inspector.inspect_policy_baseline("dl-4:baseline:1", "dl-4", addr(direct_alice), "Data policy",
                                      "Data is not sold.", "Sale constitutes breach.", "Formatting allowed.",
                                      canonical(policy), digest(policy))
    result = inspector.get_result("dl-4:baseline:1")
    assert result["status"] == "AMBIGUOUS"
    assert result["evidence"][1]["retrieval_status"] == "OVERSIZED_OR_EMPTY"
    assert result["evidence"][1]["artifact"] is None


def test_context_source_never_counts_as_corroboration(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm)
    inspector = direct_deploy("contracts/source_inspector.py", addr(direct_alice))
    direct_vm.sender = direct_alice
    policy = normalized_policy()
    policy["sources"].append({"url": "https://context.example/context", "role": "CONTEXT",
                              "publisher": "context publisher"})
    direct_vm.mock_web(r".*primary\.example/privacy.*", {"status": 200, "body": "No sale of data."})
    direct_vm.mock_web(r".*observer\.example/report.*", {"status": 200, "body": "Unclear."})
    direct_vm.mock_web(r".*context\.example/context.*", {"status": 200, "body": "Context agrees."})
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_POLICY_EVIDENCE_V1.*", json.dumps({
        "primary": baseline(), "corroboration": ["INCONCLUSIVE", "SUPPORTS"]}))
    inspector.inspect_policy_baseline("dl-5:baseline:1", "dl-5", addr(direct_alice), "Data policy",
                                      "Data is not sold.", "Sale constitutes breach.", "Formatting allowed.",
                                      canonical(policy), digest(policy))
    result = inspector.get_result("dl-5:baseline:1")
    assert result["corroboration_count"] == 0
    assert result["status"] == "AMBIGUOUS"


def test_committed_judge_replays_outcome_and_artifact(direct_vm, direct_deploy, direct_alice):
    warp(direct_vm)
    _, messages = capture(direct_vm)
    judge = direct_deploy("contracts/breach_judge.py", addr(direct_alice))
    direct_vm.sender = direct_alice
    policy = normalized_policy()
    inspection = {"request_id": "dc-1", "kind": "CURRENT", "status": "MATERIAL_CHANGE",
                  "policy_digest": digest(policy), "evidence": evidence("Sale allowed", "Sale confirmed")}
    response = {**verdict(), "corroboration": ["SUPPORTS"]}
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_COMMITTED_JUDGMENT_V1.*", json.dumps(response))
    judge.judge_policy("dc-1", "dc-1", addr(direct_alice), "Data policy", "Data not sold.",
                       "Sale constitutes breach.", "Formatting allowed.", canonical(inspection),
                       canonical(policy), digest(policy), "", False)
    assert judge.get_result("dc-1")["outcome"] == "BREACH"
    assert direct_vm.run_validator() is True
    assert messages[-1]["on"] == "finalized"
    direct_vm.clear_mocks()
    direct_vm.mock_llm(r"(?s).*DRIFTLOCK_COMMITTED_JUDGMENT_V1.*", json.dumps({
        **verdict("PERMITTED_CHANGE"), "corroboration": ["SUPPORTS"]}))
    assert direct_vm.run_validator() is False
