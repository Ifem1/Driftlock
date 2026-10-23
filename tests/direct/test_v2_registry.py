import hashlib
import json
import pytest

from tests.direct.conftest import NOW, STAKE, BOND, addr, warp


def canonical(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


POLICY = {"version": 1, "min_corroborations": 1, "sources": [
    {"url": "https://primary.example/privacy", "role": "PRIMARY", "publisher": "Primary Inc"},
    {"url": "https://observer.example/report", "role": "CORROBORATING", "publisher": "Observer Org"},
]}


def artifact(text):
    data = text.encode("utf-8")
    return {"manifest_version": 1, "rendered_text": text, "rendered_utf8_bytes": len(data),
            "rendered_sha256": hashlib.sha256(data).hexdigest(),
            "artifact_scope": "GENLAYER_RENDERED_TEXT_NOT_RAW_HTTP_BYTES"}


def evidence(primary="Primary says no sale", corroborator="Observer confirms"):
    return [{**source, "publisher": source["publisher"].lower(),
             "retrieval_status": "AVAILABLE", "artifact": artifact(text)}
            for source, text in zip(POLICY["sources"], (primary, corroborator))]


def setup_v2(vm, deploy, owner, challenger, component):
    warp(vm)
    vm.sender, vm.value = owner, STAKE
    registry = deploy("contracts/drift_registry.py", addr(component), addr(component))
    cid = registry.create_covenant_v2(
        "Data covenant", "Customer-data policy for Example Company.", POLICY["sources"][0]["url"],
        "Customer information is not sold to third parties.",
        "Selling customer information to third parties constitutes breach.",
        "Formatting and unrelated clarifications are permitted.", addr(owner), 1000, NOW + 30000,
        canonical(POLICY))
    vm.sender, vm.value = component, 0
    packet = {"request_id": f"{cid}:baseline:1", "kind": "BASELINE", "status": "BASELINE_VERIFIED",
              "source_accessible": True, "same_subject": True, "protected_promise_supported": True,
              "rule_testable": True, "time_scope_valid": True, "baseline_compliant": True,
              "breach_condition_present": False, "basis": "Primary supports promise.",
              "evidence": evidence(), "corroboration": ["SUPPORTS"], "corroboration_count": 1,
              "contradictory": False,
              "policy_digest": hashlib.sha256(canonical({**POLICY, "sources": [
                  {**source, "publisher": source["publisher"].lower()} for source in POLICY["sources"]
              ]}).encode()).hexdigest()}
    registry.record_baseline(cid, f"{cid}:baseline:1", canonical(packet))
    assert registry.get_covenant(cid)["status"] == "ACTIVE"
    return registry, cid, packet


def current_packet(challenge_id, baseline, status="MATERIAL_CHANGE"):
    context = {key: baseline[key] for key in (
        "status", "source_accessible", "same_subject", "protected_promise_supported", "rule_testable",
        "time_scope_valid", "baseline_compliant", "breach_condition_present", "basis")}
    changed = status == "MATERIAL_CHANGE"
    return {"request_id": challenge_id, "kind": "CURRENT", "status": status,
            "source_accessible": True, "same_subject": True,
            "promise_still_supported": not changed, "current_compliant": not changed,
            "breach_condition_now_supported": changed, "effective_now": changed,
            "baseline_context": context, "basis": "Incident was inspected.",
            "evidence": evidence("Primary permits sale", "Observer confirms sale"),
            "corroboration": ["SUPPORTS"], "corroboration_count": 1,
            "contradictory": False, "policy_digest": baseline["policy_digest"]}


def judgment_packet(challenge_id, current, outcome="BREACH", appeal=False):
    return {"request_id": challenge_id + (":appeal:1" if appeal else ""),
            "kind": "APPEAL" if appeal else "JUDGMENT", "outcome": outcome,
            "breach_supported": outcome == "BREACH", "permitted_by_rule": outcome == "PERMITTED_CHANGE",
            "same_subject": True, "effective_now": True, "basis": "Committed text reviewed.",
            "policy_digest": current["policy_digest"],
            "evidence_digest": hashlib.sha256(canonical(current["evidence"]).encode()).hexdigest()}


def test_v2_breach_is_provisional_and_owner_can_reverse(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    c, cid, baseline = setup_v2(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender, direct_vm.value = direct_bob, BOND
    challenge_id = c.challenge_covenant(cid)
    current = current_packet(challenge_id, baseline)
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    c.record_inspection(challenge_id, canonical(current))
    c.record_judgment(challenge_id, canonical(judgment_packet(challenge_id, current)))
    assert c.get_challenge(challenge_id)["status"] == "PROVISIONAL_BREACH"
    assert c.get_credit(addr(direct_bob)) == "0"
    assert c.get_stats()["accounting_balanced"] is True
    direct_vm.sender, direct_vm.value = direct_alice, BOND
    c.appeal_challenge(challenge_id, "The apparent sale is expressly excluded by the original rule.")
    assert c.get_stats()["appeal_escrow_atto"] == str(BOND)
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    c.record_appeal(challenge_id, challenge_id + ":appeal:1",
                    canonical(judgment_packet(challenge_id, current, "PERMITTED_CHANGE", True)))
    assert c.get_challenge(challenge_id)["status"] == "PERMITTED_CHANGE"
    assert c.get_challenge(challenge_id)["appeal_result"] == "OVERTURNED"
    assert c.get_covenant(cid)["status"] == "ACTIVE"
    assert c.get_stats()["accounting_balanced"] is True
    with pytest.raises(Exception, match="appealable"):
        c.appeal_challenge(challenge_id, "Attempt duplicate appeal after settlement.")


def test_v2_rejects_forged_content_hash(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    c, cid, baseline = setup_v2(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender, direct_vm.value = direct_bob, BOND
    challenge_id = c.challenge_covenant(cid)
    current = current_packet(challenge_id, baseline)
    current["evidence"][0]["artifact"]["rendered_text"] = "Substituted content"
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    with pytest.raises(Exception, match="content commitment"):
        c.record_inspection(challenge_id, canonical(current))
    assert c.get_challenge(challenge_id)["status"] == "INSPECTION_PENDING"


def test_v2_permissionless_finalization_after_window(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    c, cid, baseline = setup_v2(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender, direct_vm.value = direct_bob, BOND
    challenge_id = c.challenge_covenant(cid)
    current = current_packet(challenge_id, baseline)
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    c.record_inspection(challenge_id, canonical(current))
    c.record_judgment(challenge_id, canonical(judgment_packet(challenge_id, current)))
    direct_vm.sender = direct_bob
    with pytest.raises(Exception, match="window"):
        c.finalize_challenge(challenge_id)
    warp(direct_vm, NOW + 3601)
    c.finalize_challenge(challenge_id)
    assert c.get_challenge(challenge_id)["status"] == "BREACH"
    assert c.get_covenant(cid)["status"] == "BREACHED"
    assert c.get_stats()["accounting_balanced"] is True


def test_v2_challenger_can_reverse_no_change(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    c, cid, baseline = setup_v2(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender, direct_vm.value = direct_bob, BOND
    challenge_id = c.challenge_covenant(cid)
    current = current_packet(challenge_id, baseline, "NO_RELEVANT_CHANGE")
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    c.record_inspection(challenge_id, canonical(current))
    assert c.get_challenge(challenge_id)["status"] == "PROVISIONAL_NO_RELEVANT_CHANGE"
    direct_vm.sender, direct_vm.value = direct_bob, 0
    with pytest.raises(Exception, match="exact appeal bond"):
        c.appeal_challenge(challenge_id, "The primary incident text expressly permits data sale now.")
    direct_vm.sender, direct_vm.value = direct_bob, BOND
    c.appeal_challenge(challenge_id, "The primary incident text expressly permits data sale now.")
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    c.record_appeal(challenge_id, challenge_id + ":appeal:1",
                    canonical(judgment_packet(challenge_id, current, "BREACH", True)))
    assert c.get_challenge(challenge_id)["status"] == "BREACH"
    assert c.get_challenge(challenge_id)["appeal_result"] == "OVERTURNED"
    assert c.get_covenant(cid)["status"] == "BREACHED"
    assert c.get_stats()["accounting_balanced"] is True


def test_v2_upheld_owner_appeal_forfeits_appeal_bond(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    c, cid, baseline = setup_v2(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender, direct_vm.value = direct_bob, BOND
    challenge_id = c.challenge_covenant(cid)
    current = current_packet(challenge_id, baseline)
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    c.record_inspection(challenge_id, canonical(current))
    c.record_judgment(challenge_id, canonical(judgment_packet(challenge_id, current)))
    direct_vm.sender, direct_vm.value = direct_alice, BOND
    c.appeal_challenge(challenge_id, "The apparent sale was a hypothetical and should be reconsidered.")
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    c.record_appeal(challenge_id, challenge_id + ":appeal:1",
                    canonical(judgment_packet(challenge_id, current, "BREACH", True)))
    assert c.get_challenge(challenge_id)["appeal_result"] == "UPHELD"
    assert int(c.get_credit(addr(direct_bob))) >= 2 * BOND
    assert c.get_stats()["appeal_escrow_atto"] == "0"
    assert c.get_stats()["accounting_balanced"] is True


def test_v2_appeal_timeout_fails_closed_and_replay_is_inert(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    c, cid, baseline = setup_v2(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie)
    direct_vm.sender, direct_vm.value = direct_bob, BOND
    challenge_id = c.challenge_covenant(cid)
    current = current_packet(challenge_id, baseline)
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    c.record_inspection(challenge_id, canonical(current))
    c.record_judgment(challenge_id, canonical(judgment_packet(challenge_id, current)))
    direct_vm.sender, direct_vm.value = direct_alice, BOND
    c.appeal_challenge(challenge_id, "The original incident should be independently reconsidered.")
    warp(direct_vm, NOW + 1801)
    direct_vm.sender, direct_vm.value = direct_bob, 0
    c.expire_challenge(challenge_id)
    assert c.get_challenge(challenge_id)["status"] == "INCONCLUSIVE"
    assert c.get_covenant(cid)["status"] == "ACTIVE"
    assert c.get_stats()["accounting_balanced"] is True
    direct_vm.sender = direct_charlie
    c.record_appeal(challenge_id, challenge_id + ":appeal:1",
                    canonical(judgment_packet(challenge_id, current, "BREACH", True)))
    assert c.get_challenge(challenge_id)["status"] == "INCONCLUSIVE"


def test_v2_rejects_duplicate_declared_publisher(direct_vm, direct_deploy, direct_alice, direct_charlie):
    warp(direct_vm)
    direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    bad = {**POLICY, "sources": [POLICY["sources"][0],
                                {**POLICY["sources"][1], "publisher": "Primary Inc"}]}
    with pytest.raises(Exception, match="distinct sites and declared publishers"):
        c.create_covenant_v2("Data covenant", "Customer-data policy for Example Company.",
                             POLICY["sources"][0]["url"], "Data is not sold to third parties.",
                             "Sale to third parties is a breach under this rule.", "Formatting allowed.",
                             addr(direct_alice), 1000, NOW + 30000, canonical(bad))


def test_v2_context_cannot_satisfy_threshold(direct_vm, direct_deploy, direct_alice, direct_charlie):
    warp(direct_vm)
    direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    bad = {**POLICY, "sources": [POLICY["sources"][0],
                                {**POLICY["sources"][1], "role": "CONTEXT"}]}
    with pytest.raises(Exception, match="lacks required corroborating"):
        c.create_covenant_v2("Data covenant", "Customer-data policy for Example Company.",
                             POLICY["sources"][0]["url"], "Data is not sold to third parties.",
                             "Sale to third parties is a breach under this rule.", "Formatting allowed.",
                             addr(direct_alice), 1000, NOW + 30000, canonical(bad))


def test_v2_policy_rejects_boolean_threshold(direct_vm, direct_deploy, direct_alice, direct_charlie):
    warp(direct_vm)
    direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    bad = {**POLICY, "min_corroborations": True}
    with pytest.raises(Exception, match="invalid corroboration threshold"):
        c.create_covenant_v2("Data covenant", "Customer-data policy for Example Company.",
                             POLICY["sources"][0]["url"], "Data is not sold to third parties.",
                             "Sale to third parties is a breach under this rule.", "Formatting allowed.",
                             addr(direct_alice), 1000, NOW + 30000, canonical(bad))
