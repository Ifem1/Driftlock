import json
import pytest
from tests.direct.conftest import NOW, STAKE, BOND, addr, capture, warp


def baseline_ok(request_id="dl-1:baseline:1"):
    return json.dumps({
        "request_id": request_id, "kind": "BASELINE",
        "status":"BASELINE_VERIFIED","source_accessible":True,"same_subject":True,
        "protected_promise_supported":True,"rule_testable":True,"time_scope_valid":True,
        "baseline_compliant":True,"breach_condition_present":False,
        "basis":"The canonical page supports the protected promise."
    })


def baseline_reject(request_id="dl-1:baseline:1"):
    return json.dumps({
        "request_id": request_id, "kind": "BASELINE",
        "status":"PROMISE_NOT_SUPPORTED","source_accessible":True,"same_subject":True,
        "protected_promise_supported":False,"rule_testable":True,"time_scope_valid":True,
        "baseline_compliant":False,"breach_condition_present":False,
        "basis":"The canonical page does not support the claimed promise."
    })


def baseline_unavailable(request_id):
    return json.dumps({
        "request_id": request_id, "kind": "BASELINE", "status": "SOURCE_UNAVAILABLE",
        "source_accessible": False, "same_subject": False, "protected_promise_supported": False,
        "rule_testable": False, "time_scope_valid": False, "baseline_compliant": False,
        "breach_condition_present": False, "basis": "Canonical source could not be retrieved.",
    })


def inspection(status="MATERIAL_CHANGE", request_id="dc-test"):
    unavailable = status == "SOURCE_UNAVAILABLE"
    no_change = status == "NO_RELEVANT_CHANGE"
    return json.dumps({
        "request_id":request_id,"kind":"CURRENT","status":status,
        "source_accessible":not unavailable,"same_subject":not unavailable,
        "promise_still_supported":no_change,"current_compliant":no_change,
        "breach_condition_now_supported":status=="MATERIAL_CHANGE","effective_now":not unavailable and status!="AMBIGUOUS",
        "baseline_context": {
            "status":"BASELINE_VERIFIED", "source_accessible":True,"same_subject":True,
            "protected_promise_supported":True,"rule_testable":True,"time_scope_valid":True,
            "baseline_compliant":True,"breach_condition_present":False,
            "basis":"The canonical page supports the protected promise.",
        },
        "basis":"Finalized source inspection result."
    })


def judgment(outcome="BREACH", request_id="dc-test"):
    return json.dumps({
        "request_id":request_id,"kind":"JUDGMENT","outcome":outcome,"breach_supported":outcome=="BREACH","permitted_by_rule":outcome=="PERMITTED_CHANGE",
        "same_subject":True,"effective_now":True,"basis":"Finalized independent breach judgment."
    })


def create_and_activate(vm, deploy, alice, component, beneficiary):
    vm.sender, vm.value = alice, STAKE
    c = deploy("contracts/drift_registry.py", addr(component), addr(component))
    cid = c.create_covenant(
        "Data sale covenant", "The current customer-data policy of Example Company.", "https://example.com/privacy",
        "Customer information is not sold to third parties.",
        "Allowing sale or commercial licensing of customer information constitutes breach.",
        "Formatting and unrelated clarification are permitted.", addr(beneficiary), 1000, NOW + 20000,
    )
    vm.value = 0; vm.sender = component; c.record_baseline(cid, f"{cid}:baseline:1", baseline_ok(f"{cid}:baseline:1"))
    return c, cid


def test_secure_one_time_component_binding(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender = direct_alice
    c = direct_deploy("contracts/drift_registry.py", "", "")
    direct_vm.sender = direct_bob
    with pytest.raises(Exception, match="bootstrapper"):
        c.configure_components(addr(direct_charlie), addr(direct_charlie))
    direct_vm.sender = direct_alice; c.configure_components(addr(direct_charlie), addr(direct_charlie))
    assert c.get_stats()["components_configured"] is True
    with pytest.raises(Exception, match="already configured"):
        c.configure_components(addr(direct_bob), addr(direct_bob))


def test_baseline_activation_freezes_stake_in_active_state(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    state = c.get_covenant(cid)
    assert state["status"] == "ACTIVE"
    assert state["canonical_url"] == "https://example.com/privacy"
    assert c.get_stats()["accounting_balanced"] is True


def test_rejected_baseline_refunds_owner_credit(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant("Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy", "Data is never sold.", "Sale is breach under this covenant.", "Formatting permitted.", addr(direct_bob), 1000, NOW+20000)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_baseline(cid, f"{cid}:baseline:1", baseline_reject(f"{cid}:baseline:1"))
    assert c.get_covenant(cid)["status"] == "BASELINE_REJECTED"
    assert c.get_credit(addr(direct_alice)) == str(STAKE)
    assert c.get_stats()["accounting_balanced"] is True


def test_unavailable_baseline_remains_retryable_and_preserves_escrow(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant("Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy", "Data is never sold.", "Sale is breach under this covenant.", "Formatting permitted.", addr(direct_bob), 1000, NOW+20000)
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    c.record_baseline(cid, f"{cid}:baseline:1", baseline_unavailable(f"{cid}:baseline:1"))
    assert c.get_covenant(cid)["status"] == "BASELINE_RETRYABLE"
    assert c.get_credit(addr(direct_alice)) == "0"
    assert c.get_stats()["accounting_balanced"] is True
    direct_vm.sender = direct_alice
    c.retry_baseline(cid)
    assert c.get_covenant(cid)["status"] == "BASELINE_PENDING"
    assert c.get_stats()["accounting_balanced"] is True


@pytest.mark.parametrize("field, value", [("baseline_compliant", False), ("breach_condition_present", True)])
def test_registry_refuses_unverified_or_prebreached_activation_packet(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie, field, value):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant("Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy", "Data is never sold.", "Sale is breach under this covenant.", "Formatting permitted.", addr(direct_bob), 1000, NOW+20000)
    packet = json.loads(baseline_ok(f"{cid}:baseline:1")); packet[field] = value
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    with pytest.raises(Exception, match="verified baseline"):
        c.record_baseline(cid, f"{cid}:baseline:1", json.dumps(packet))
    assert c.get_covenant(cid)["status"] == "BASELINE_PENDING"
    assert c.get_stats()["accounting_balanced"] is True


def test_late_baseline_from_previous_attempt_cannot_activate_retry(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant("Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy", "Data is never sold.", "Sale of customer data constitutes breach.", "Formatting permitted.", addr(direct_bob), 1000, NOW + 20000)
    direct_vm.value = 0
    warp(direct_vm, NOW + 1800)
    assert c.get_covenant(cid)["can_expire_baseline"] is True
    c.expire_baseline(cid)
    c.retry_baseline(cid)
    assert c.get_covenant(cid)["can_expire_baseline"] is False
    direct_vm.sender = direct_charlie
    c.record_baseline(cid, f"{cid}:baseline:1", baseline_ok(f"{cid}:baseline:1"))
    assert c.get_covenant(cid)["status"] == "BASELINE_PENDING"
    c.record_baseline(cid, f"{cid}:baseline:2", baseline_ok(f"{cid}:baseline:2"))
    assert c.get_covenant(cid)["status"] == "ACTIVE"


def test_baseline_callback_rejects_mismatched_packet(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant("Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy", "Data is never sold.", "Sale of customer data constitutes breach.", "Formatting permitted.", addr(direct_bob), 1000, NOW + 20000)
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    with pytest.raises(Exception, match="request mismatch"):
        c.record_baseline(cid, f"{cid}:baseline:1", baseline_ok("different-request"))
    assert c.get_covenant(cid)["status"] == "BASELINE_PENDING"


def test_baseline_timeout_prevents_late_activation(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant("Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy", "Data is never sold.", "Sale of customer data constitutes breach.", "Formatting permitted.", addr(direct_bob), 1000, NOW + 20000)
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    warp(direct_vm, NOW + 1800)
    c.record_baseline(cid, f"{cid}:baseline:1", baseline_ok(f"{cid}:baseline:1"))
    assert c.get_covenant(cid)["status"] == "BASELINE_RETRYABLE"


def test_wrong_component_cannot_activate_baseline(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant("Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy", "Data is never sold.", "Sale of customer data constitutes breach.", "Formatting permitted.", addr(direct_bob), 1000, NOW + 20000)
    direct_vm.value = 0; direct_vm.sender = direct_bob
    with pytest.raises(Exception, match="configured inspector"):
        c.record_baseline(cid, f"{cid}:baseline:1", baseline_ok(f"{cid}:baseline:1"))
    assert c.get_covenant(cid)["status"] == "BASELINE_PENDING"


def test_owner_cannot_challenge_own_covenant(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_alice, BOND
    with pytest.raises(Exception, match="owner cannot"):
        c.challenge_covenant(cid)


def test_no_change_forfeits_bond_to_owner(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection("NO_RELEVANT_CHANGE", chid))
    assert c.get_challenge(chid)["status"] == "NO_RELEVANT_CHANGE"
    assert c.get_credit(addr(direct_alice)) == str(BOND)
    assert c.get_covenant(cid)["status"] == "ACTIVE"
    assert c.get_stats()["accounting_balanced"] is True


def test_source_unavailable_refunds_challenger(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection("SOURCE_UNAVAILABLE", chid))
    assert c.get_credit(addr(direct_bob)) == str(BOND)
    assert c.get_covenant(cid)["status"] == "ACTIVE"


def test_registry_refuses_material_change_without_semantic_conflict(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; challenge_id = c.challenge_covenant(cid)
    packet = json.loads(inspection("MATERIAL_CHANGE", challenge_id))
    packet["current_compliant"] = True
    packet["breach_condition_now_supported"] = False
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    with pytest.raises(Exception, match="material change requires"):
        c.record_inspection(challenge_id, json.dumps(packet))
    assert c.get_challenge(challenge_id)["status"] == "INSPECTION_PENDING"
    assert c.get_stats()["accounting_balanced"] is True


def test_non_breach_attempts_from_secondary_wallet_do_not_block_later_breach(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant(
        "Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy",
        "Customer information is not sold to third parties.",
        "Sale or commercial licensing of customer information constitutes breach.",
        "Formatting and unrelated clarification are permitted.", addr(direct_charlie), 1000, NOW + 150000,
    )
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    c.record_baseline(cid, f"{cid}:baseline:1", baseline_ok(f"{cid}:baseline:1"))

    # Bob represents an owner-controlled secondary wallet: only the exact owner address is barred.
    outcomes = ["SOURCE_UNAVAILABLE", "AMBIGUOUS", "NO_RELEVANT_CHANGE", "INCONCLUSIVE", "PERMITTED_CHANGE", "STALE", "TIMED_OUT"]
    for attempt in range(25):
        at = NOW + attempt * 4000
        warp(direct_vm, at)
        direct_vm.sender, direct_vm.value = direct_bob, BOND
        challenge_id = c.challenge_covenant(cid)
        direct_vm.sender, direct_vm.value = direct_charlie, 0
        outcome = outcomes[attempt % len(outcomes)]
        if outcome in ("STALE", "TIMED_OUT"):
            warp(direct_vm, at + 1801)
            if outcome == "STALE":
                c.record_inspection(challenge_id, inspection("SOURCE_UNAVAILABLE", challenge_id))
                assert c.get_challenge(challenge_id)["status"] == "STALE"
            else:
                c.expire_challenge(challenge_id)
                assert c.get_challenge(challenge_id)["status"] == "TIMED_OUT"
        elif outcome in ("INCONCLUSIVE", "PERMITTED_CHANGE"):
            c.record_inspection(challenge_id, inspection("MATERIAL_CHANGE", challenge_id))
            c.record_judgment(challenge_id, judgment(outcome, challenge_id))
            assert c.get_challenge(challenge_id)["status"] == outcome
        else:
            c.record_inspection(challenge_id, inspection(outcome, challenge_id))
            assert c.get_challenge(challenge_id)["status"] == outcome

    warp(direct_vm, NOW + 25 * 4000)
    state = c.get_covenant(cid)
    assert state["challenge_count"] == 25
    assert state["can_challenge"] is True
    assert c.get_stats()["accounting_balanced"] is True

    direct_vm.sender, direct_vm.value = direct_bob, BOND
    breach_id = c.challenge_covenant(cid)
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    c.record_inspection(breach_id, inspection("MATERIAL_CHANGE", breach_id))
    c.record_judgment(breach_id, judgment("BREACH", breach_id))
    assert c.get_covenant(cid)["status"] == "BREACHED"
    assert c.get_challenge(breach_id)["status"] == "BREACH"
    assert c.get_stats()["accounting_balanced"] is True


def test_material_change_then_breach_settles_once(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_charlie)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(request_id=chid))
    assert c.get_challenge(chid)["status"] == "JUDGMENT_PENDING"
    c.record_judgment(chid, judgment("BREACH", chid))
    state = c.get_covenant(cid)
    assert state["status"] == "BREACHED" and state["remaining_stake_atto"] == "0"
    reward = STAKE * 1000 // 10000
    assert c.get_credit(addr(direct_bob)) == str(BOND + reward)
    assert c.get_credit(addr(direct_charlie)) == str(STAKE - reward)
    assert c.get_stats()["accounting_balanced"] is True
    c.record_judgment(chid, judgment("BREACH", chid))
    assert c.get_credit(addr(direct_bob)) == str(BOND + reward)


def test_permitted_material_change_keeps_covenant_active(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(request_id=chid)); c.record_judgment(chid, judgment("PERMITTED_CHANGE", chid))
    assert c.get_covenant(cid)["status"] == "ACTIVE"
    assert c.get_credit(addr(direct_alice)) == str(BOND)


def test_inconclusive_judgment_refunds_challenger(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(request_id=chid)); c.record_judgment(chid, judgment("INCONCLUSIVE", chid))
    assert c.get_credit(addr(direct_bob)) == str(BOND)
    assert c.get_covenant(cid)["status"] == "ACTIVE"


def test_challenge_timeout_refunds_bond(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid); direct_vm.value = 0
    warp(direct_vm, NOW + 1900)
    assert c.get_challenge(chid)["can_expire"] is True
    assert c.list_challenges(cid, 0, 24)["items"][0]["can_expire"] is True
    c.expire_challenge(chid)
    assert c.get_challenge(chid)["status"] == "TIMED_OUT"
    assert c.get_credit(addr(direct_bob)) == str(BOND)


def test_inspection_callback_after_timeout_does_not_take_bond(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid); direct_vm.value = 0
    warp(direct_vm, NOW + 1800); direct_vm.sender = direct_charlie
    c.record_inspection(chid, inspection("NO_RELEVANT_CHANGE", chid))
    assert c.get_challenge(chid)["status"] == "STALE"
    assert c.get_credit(addr(direct_bob)) == str(BOND)
    assert c.get_credit(addr(direct_alice)) == "0"
    assert c.get_stats()["accounting_balanced"] is True


def test_duplicate_inspection_cannot_change_settlement(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    c.record_inspection(chid, inspection("NO_RELEVANT_CHANGE", chid))
    c.record_inspection(chid, inspection("MATERIAL_CHANGE", chid))
    assert c.get_challenge(chid)["status"] == "NO_RELEVANT_CHANGE"
    assert c.get_credit(addr(direct_alice)) == str(BOND)
    assert c.get_stats()["accounting_balanced"] is True


def test_judgment_after_expiry_cannot_breach_or_double_release(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(request_id=chid))
    warp(direct_vm, NOW + 21000); assert c.get_covenant(cid)["can_expire"] is True
    direct_vm.sender = direct_alice; c.expire_covenant(cid)
    direct_vm.sender = direct_charlie; c.record_judgment(chid, judgment("BREACH", chid))
    assert c.get_covenant(cid)["status"] == "EXPIRED_UNBREACHED"
    assert c.get_challenge(chid)["status"] == "PROTOCOL_BLOCKED"
    assert c.get_credit(addr(direct_alice)) == str(STAKE)
    assert c.get_credit(addr(direct_bob)) == str(BOND)
    assert c.get_stats()["accounting_balanced"] is True


def test_expiry_refunds_unbreached_stake_and_pending_bond(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid); direct_vm.value = 0
    warp(direct_vm, NOW + 21000); direct_vm.sender = direct_alice; c.expire_covenant(cid)
    assert c.get_covenant(cid)["status"] == "EXPIRED_UNBREACHED"
    assert c.get_challenge(chid)["status"] == "PROTOCOL_BLOCKED"
    assert c.get_credit(addr(direct_alice)) == str(STAKE)
    assert c.get_credit(addr(direct_bob)) == str(BOND)
    assert c.get_stats()["accounting_balanced"] is True


def test_exact_bond_and_cooldown_are_enforced(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND-1
    with pytest.raises(Exception, match="exact challenge bond"): c.challenge_covenant(cid)
    direct_vm.value = BOND; chid = c.challenge_covenant(cid); direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection("NO_RELEVANT_CHANGE", chid))
    direct_vm.sender, direct_vm.value = direct_bob, BOND
    with pytest.raises(Exception, match="cooldown"): c.challenge_covenant(cid)


def test_withdrawal_uses_credit_ledger(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); transfers, _ = capture(direct_vm)
    c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid); direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection("NO_RELEVANT_CHANGE", chid))
    direct_vm.sender = direct_alice; c.withdraw_credit(addr(direct_alice))
    assert int(transfers[-1]["value"]) == BOND
    assert c.get_credit(addr(direct_alice)) == "0"
    assert c.get_stats()["accounting_balanced"] is True


def test_text_and_https_bounds(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    with pytest.raises(Exception, match="https"):
        c.create_covenant("Valid title", "A sufficiently descriptive policy subject.", "http://example.com", "Customer information is never sold.", "Selling customer information constitutes breach.", "Formatting permitted.", addr(direct_bob), 1000, NOW+20000)


def test_latest_owner_and_wallet_indexes_are_bounded_reads(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    assert c.find_latest_covenant_by_owner(addr(direct_alice)) == cid
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid); direct_vm.value = 0
    page = c.list_wallet_challenges(addr(direct_bob), 0, 24)
    assert page["total"] == "1" and page["items"][0]["id"] == chid
