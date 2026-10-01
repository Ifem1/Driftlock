import json
import hashlib
import pytest
from tests.direct.conftest import NOW, STAKE, BOND, addr, capture, warp


def baseline_ok(request_id="dl-1:baseline:1"):
    evidence = "Customer information is not sold to third parties."
    return json.dumps({
        "request_id": request_id, "kind": "BASELINE",
        "status":"BASELINE_VERIFIED","source_accessible":True,"same_subject":True,
        "protected_promise_supported":True,"rule_testable":True,"time_scope_valid":True,
        "breach_condition_absent":True,"source_url":"https://example.com/privacy",
        "baseline_text":evidence,"baseline_digest":hashlib.sha256(evidence.encode()).hexdigest(),
        "basis":"The canonical page supports the protected promise."
    })


def baseline_reject(request_id="dl-1:baseline:1"):
    return json.dumps({
        "request_id": request_id, "kind": "BASELINE",
        "status":"PROMISE_NOT_SUPPORTED","source_accessible":True,"same_subject":True,
        "protected_promise_supported":False,"rule_testable":True,"time_scope_valid":True,
        "basis":"The canonical page does not support the claimed promise."
    })


def inspection(challenge_id, status="MATERIAL_CHANGE"):
    return json.dumps({
        "request_id":challenge_id,"kind":"CURRENT","source_url":"https://example.com/privacy",
        "baseline_digest":hashlib.sha256(b"Customer information is not sold to third parties.").hexdigest(),
        "status":status,"source_accessible":status!="SOURCE_UNAVAILABLE","same_subject":status!="SOURCE_UNAVAILABLE",
        "promise_still_supported":status=="NO_RELEVANT_CHANGE","relevant_change_detected":status=="MATERIAL_CHANGE",
        "new_conflicting_term":status=="MATERIAL_CHANGE","effective_now":status!="SOURCE_UNAVAILABLE",
        "basis":"Finalized source inspection result."
    })


def judgment(challenge_id, outcome="BREACH"):
    packet = json.dumps(json.loads(inspection(challenge_id)), ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return json.dumps({
        "request_id": challenge_id, "inspection_digest": hashlib.sha256(packet.encode()).hexdigest(),
        "outcome":outcome,"breach_supported":outcome=="BREACH","permitted_by_rule":outcome=="PERMITTED_CHANGE",
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


def test_already_breached_baseline_refunds_without_activation(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant("Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy", "Data is never sold.", "Sale or licensing constitutes breach.", "Formatting permitted.", addr(direct_bob), 1000, NOW+20000)
    packet = json.loads(baseline_reject(f"{cid}:baseline:1"))
    packet.update({"status": "BASELINE_ALREADY_BREACHED", "protected_promise_supported": True,
                   "breach_condition_absent": False})
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    c.record_baseline(cid, f"{cid}:baseline:1", json.dumps(packet))
    assert c.get_covenant(cid)["status"] == "BASELINE_REJECTED"
    assert c.get_credit(addr(direct_alice)) == str(STAKE)
    assert c.get_stats()["accounting_balanced"] is True


def test_replayed_inspection_packet_for_other_challenge_rejected(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    with pytest.raises(Exception, match="identity mismatch"):
        c.record_inspection(chid, inspection("dc-other", "MATERIAL_CHANGE"))
    assert c.get_challenge(chid)["status"] == "INSPECTION_PENDING"


def test_late_baseline_from_previous_attempt_cannot_activate_retry(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant("Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy", "Data is never sold.", "Sale of customer data constitutes breach.", "Formatting permitted.", addr(direct_bob), 1000, NOW + 20000)
    direct_vm.value = 0
    warp(direct_vm, NOW + 1800)
    c.expire_baseline(cid)
    c.retry_baseline(cid)
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
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(chid, "NO_RELEVANT_CHANGE"))
    assert c.get_challenge(chid)["status"] == "NO_RELEVANT_CHANGE"
    assert c.get_credit(addr(direct_alice)) == str(BOND)
    assert c.get_covenant(cid)["status"] == "ACTIVE"
    assert c.get_stats()["accounting_balanced"] is True


def test_source_unavailable_refunds_challenger(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(chid, "SOURCE_UNAVAILABLE"))
    assert c.get_credit(addr(direct_bob)) == str(BOND)
    assert c.get_covenant(cid)["status"] == "ACTIVE"


def test_uncertain_attempts_preserve_future_adjudication(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); direct_vm.sender, direct_vm.value = direct_alice, STAKE
    c = direct_deploy("contracts/drift_registry.py", addr(direct_charlie), addr(direct_charlie))
    cid = c.create_covenant(
        "Data covenant", "Customer-data policy for Example Company.", "https://example.com/privacy",
        "Customer information is not sold to third parties.",
        "Sale or commercial licensing of customer information constitutes breach.",
        "Formatting and unrelated clarification are permitted.", addr(direct_charlie), 1000, NOW + 100000,
    )
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    c.record_baseline(cid, f"{cid}:baseline:1", baseline_ok(f"{cid}:baseline:1"))
    for attempt in range(25):
        warp(direct_vm, NOW + attempt * 901)
        direct_vm.sender, direct_vm.value = direct_bob, BOND
        chid = c.challenge_covenant(cid)
        direct_vm.sender, direct_vm.value = direct_charlie, 0
        c.record_inspection(chid, inspection(chid, "SOURCE_UNAVAILABLE"))
        assert c.get_challenge(chid)["bond_recipient"].lower() == addr(direct_bob).lower()
    state = c.get_covenant(cid)
    assert state["challenge_count"] == 25
    assert state["substantive_challenge_count"] == 0
    warp(direct_vm, NOW + 25 * 901)
    direct_vm.sender, direct_vm.value = direct_bob, BOND
    chid = c.challenge_covenant(cid)
    direct_vm.sender, direct_vm.value = direct_charlie, 0
    c.record_inspection(chid, inspection(chid, "MATERIAL_CHANGE"))
    c.record_judgment(chid, judgment(chid, "BREACH"))
    assert c.get_covenant(cid)["status"] == "BREACHED"
    assert c.get_stats()["accounting_balanced"] is True


def test_credit_withdrawal_requires_credited_wallet(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    c.record_inspection(chid, inspection(chid, "SOURCE_UNAVAILABLE"))
    direct_vm.sender = direct_alice
    with pytest.raises(Exception, match="credited wallet"):
        c.withdraw_credit(addr(direct_bob))
    assert c.get_credit(addr(direct_bob)) == str(BOND)
    assert c.get_stats()["accounting_balanced"] is True


def test_material_change_then_breach_settles_once(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_charlie)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(chid))
    assert c.get_challenge(chid)["status"] == "JUDGMENT_PENDING"
    c.record_judgment(chid, judgment(chid, "BREACH"))
    state = c.get_covenant(cid)
    assert state["status"] == "BREACHED" and state["remaining_stake_atto"] == "0"
    reward = STAKE * 1000 // 10000
    assert c.get_credit(addr(direct_bob)) == str(BOND + reward)
    assert c.get_credit(addr(direct_charlie)) == str(STAKE - reward)
    assert c.get_stats()["accounting_balanced"] is True
    c.record_judgment(chid, judgment(chid, "BREACH"))
    assert c.get_credit(addr(direct_bob)) == str(BOND + reward)


def test_permitted_material_change_keeps_covenant_active(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(chid)); c.record_judgment(chid, judgment(chid, "PERMITTED_CHANGE"))
    assert c.get_covenant(cid)["status"] == "ACTIVE"
    assert c.get_credit(addr(direct_alice)) == str(BOND)


def test_inconclusive_judgment_refunds_challenger(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(chid)); c.record_judgment(chid, judgment(chid, "INCONCLUSIVE"))
    assert c.get_credit(addr(direct_bob)) == str(BOND)
    assert c.get_covenant(cid)["status"] == "ACTIVE"


def test_challenge_timeout_refunds_bond(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid); direct_vm.value = 0
    warp(direct_vm, NOW + 1900); c.expire_challenge(chid)
    assert c.get_challenge(chid)["status"] == "TIMED_OUT"
    assert c.get_credit(addr(direct_bob)) == str(BOND)


def test_inspection_callback_after_timeout_does_not_take_bond(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid); direct_vm.value = 0
    warp(direct_vm, NOW + 1800); direct_vm.sender = direct_charlie
    c.record_inspection(chid, inspection(chid, "NO_RELEVANT_CHANGE"))
    assert c.get_challenge(chid)["status"] == "STALE"
    assert c.get_credit(addr(direct_bob)) == str(BOND)
    assert c.get_credit(addr(direct_alice)) == "0"
    assert c.get_stats()["accounting_balanced"] is True


def test_duplicate_inspection_cannot_change_settlement(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie
    c.record_inspection(chid, inspection(chid, "NO_RELEVANT_CHANGE"))
    c.record_inspection(chid, inspection(chid, "MATERIAL_CHANGE"))
    assert c.get_challenge(chid)["status"] == "NO_RELEVANT_CHANGE"
    assert c.get_credit(addr(direct_alice)) == str(BOND)
    assert c.get_stats()["accounting_balanced"] is True


def test_judgment_after_expiry_cannot_breach_or_double_release(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid)
    direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(chid))
    warp(direct_vm, NOW + 21000); direct_vm.sender = direct_alice; c.expire_covenant(cid)
    direct_vm.sender = direct_charlie; c.record_judgment(chid, judgment(chid, "BREACH"))
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
    direct_vm.value = BOND; chid = c.challenge_covenant(cid); direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(chid, "NO_RELEVANT_CHANGE"))
    direct_vm.sender, direct_vm.value = direct_bob, BOND
    with pytest.raises(Exception, match="cooldown"): c.challenge_covenant(cid)


def test_withdrawal_uses_credit_ledger(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    warp(direct_vm); transfers, _ = capture(direct_vm)
    c, cid = create_and_activate(direct_vm, direct_deploy, direct_alice, direct_charlie, direct_bob)
    direct_vm.sender, direct_vm.value = direct_bob, BOND; chid = c.challenge_covenant(cid); direct_vm.value = 0; direct_vm.sender = direct_charlie; c.record_inspection(chid, inspection(chid, "NO_RELEVANT_CHANGE"))
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
