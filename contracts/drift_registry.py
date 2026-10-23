# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json
import re
import hashlib
from urllib.parse import urlparse
from datetime import datetime, timezone

VERSION = "0.2.0-assurance-appeals"
MAX_POLICY_BYTES = 3200
MAX_EVIDENCE_SOURCES = 3
APPEAL_WINDOW = 3600
APPEAL_TIMEOUT = 1800
MAX_REBUTTAL = 1200
NETWORK_ID = "61999"
MIN_STAKE = 10 ** 15
MAX_STAKE = 10 * 10 ** 18
MIN_BOND = 10 ** 14
MIN_REWARD_BPS = 100
MAX_REWARD_BPS = 2500
MAX_COVENANTS_PAGE = 24
MAX_CHALLENGES_PAGE = 24
MAX_TITLE = 100
MAX_SUBJECT = 1200
MAX_URL = 800
MAX_PROMISE = 1800
MAX_RULE = 2400
MAX_PERMITTED = 1600
BASELINE_TIMEOUT = 1800
INSPECTION_TIMEOUT = 1800
JUDGE_TIMEOUT = 1800
CHALLENGE_COOLDOWN = 900
MIN_LIFETIME = 7200
MAX_LIFETIME = 30 * 86400

BASELINE_STATUSES = ("BASELINE_VERIFIED", "PROMISE_NOT_SUPPORTED", "SOURCE_UNAVAILABLE", "AMBIGUOUS")
INSPECTION_STATUSES = ("NO_RELEVANT_CHANGE", "MATERIAL_CHANGE", "SOURCE_UNAVAILABLE", "AMBIGUOUS")
JUDGMENT_OUTCOMES = ("BREACH", "PERMITTED_CHANGE", "INCONCLUSIVE")
TERMINAL_COVENANT = ("BREACHED", "EXPIRED_UNBREACHED", "BASELINE_REJECTED", "EXPIRED_UNVERIFIED")
TERMINAL_CHALLENGE = (
    "NO_RELEVANT_CHANGE", "SOURCE_UNAVAILABLE", "AMBIGUOUS", "PERMITTED_CHANGE",
    "INCONCLUSIVE", "BREACH", "TIMED_OUT", "STALE", "PROTOCOL_BLOCKED",
)


def _now() -> int:
    return int(datetime.fromisoformat(gl.message_raw["datetime"]).timestamp())


def _iso() -> str:
    return datetime.fromtimestamp(_now(), tz=timezone.utc).isoformat()


def _json(value) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _policy(raw: str, canonical_url: str) -> dict:
    if not isinstance(raw, str) or len(raw.encode("utf-8")) > MAX_POLICY_BYTES:
        raise gl.vm.UserError("[EXPECTED] evidence policy exceeds bound")
    try:
        value = json.loads(raw)
    except Exception:
        raise gl.vm.UserError("[EXPECTED] invalid evidence policy JSON") from None
    if not isinstance(value, dict) or type(value.get("version")) is not int or value.get("version") != 1:
        raise gl.vm.UserError("[EXPECTED] unsupported evidence policy version")
    sources = value.get("sources")
    if not isinstance(sources, list) or not 2 <= len(sources) <= MAX_EVIDENCE_SOURCES:
        raise gl.vm.UserError("[EXPECTED] V2 policy requires primary and 1..2 corroborators")
    if type(value.get("min_corroborations")) is not int or value.get("min_corroborations") not in (1, 2):
        raise gl.vm.UserError("[EXPECTED] invalid corroboration threshold")
    hosts = set()
    sites = set()
    publishers = set()
    normalized = []
    for index, source in enumerate(sources):
        if not isinstance(source, dict) or set(source) != {"url", "role", "publisher"}:
            raise gl.vm.UserError("[EXPECTED] invalid evidence source fields")
        url = _text(source["url"], "evidence URL", MAX_URL, 8)
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
            raise gl.vm.UserError("[EXPECTED] evidence URLs require plain HTTPS origins")
        if index == 0 and (source["role"] != "PRIMARY" or url != canonical_url):
            raise gl.vm.UserError("[EXPECTED] first source must match the canonical primary")
        if index > 0 and source["role"] not in ("CORROBORATING", "CONTEXT"):
            raise gl.vm.UserError("[EXPECTED] invalid additional source role")
        publisher = _text(source["publisher"], "publisher", 100, 3).lower()
        host = parsed.hostname.lower()
        labels = host.split(".")
        if (len(labels) < 2 or host == "localhost" or host.endswith(".local")
                or re.fullmatch(r"[0-9.]+", host) is not None):
            raise gl.vm.UserError("[EXPECTED] evidence requires public DNS hostnames")
        site = ".".join(labels[-2:])
        if host in hosts or site in sites or publisher in publishers:
            raise gl.vm.UserError("[EXPECTED] sources must have distinct sites and declared publishers")
        hosts.add(host)
        sites.add(site)
        publishers.add(publisher)
        normalized.append({"url": url, "role": source["role"], "publisher": publisher})
    corroborators = sum(source["role"] == "CORROBORATING" for source in normalized)
    if corroborators < value["min_corroborations"] or corroborators < 1:
        raise gl.vm.UserError("[EXPECTED] policy lacks required corroborating sources")
    return {"version": 1, "sources": normalized, "min_corroborations": value["min_corroborations"]}


def _text(value: str, name: str, limit: int, minimum: int = 1) -> str:
    if not isinstance(value, str) or len(value) < minimum or len(value) > limit or "\x00" in value:
        raise gl.vm.UserError(f"[EXPECTED] {name} must be {minimum}..{limit} characters without NUL")
    if not value.strip():
        raise gl.vm.UserError(f"[EXPECTED] {name} cannot be blank")
    return value.strip()


def _address(value: str, name: str) -> str:
    value = str(value)
    if value.startswith("addr#"):
        value = "0x" + value[5:]
    elif value.startswith("address#"):
        value = "0x" + value[8:]
    if re.fullmatch(r"0x[0-9a-fA-F]{40}", value) is None or int(value[2:], 16) == 0:
        raise gl.vm.UserError(f"[EXPECTED] invalid {name} address")
    return value


@gl.evm.contract_interface
class _Recipient:
    class View:
        pass

    class Write:
        pass


class DriftRegistry(gl.Contract):
    covenants: TreeMap[str, str]
    covenant_ids: DynArray[str]
    challenges: TreeMap[str, str]
    challenge_ids: DynArray[str]
    covenant_challenge_index: TreeMap[str, str]
    wallet_challenge_counts: TreeMap[Address, u256]
    wallet_challenge_index: TreeMap[str, str]
    wallet_appeal_counts: TreeMap[Address, u256]
    wallet_appeal_index: TreeMap[str, str]
    owner_latest: TreeMap[Address, str]
    credits: TreeMap[Address, u256]
    inspector_address: str
    judge_address: str
    bootstrapper: str
    components_configured: bool
    next_covenant: u256
    next_challenge: u256
    total_deposited: u256
    stake_escrow: u256
    bond_escrow: u256
    appeal_escrow: u256
    total_claimable: u256
    total_withdrawn: u256
    covenants_activated: u256
    covenants_breached: u256
    covenants_expired: u256
    total_challenges: u256

    def __init__(self, inspector_address: str, judge_address: str):
        self.bootstrapper = str(gl.message.sender_address)
        if inspector_address and judge_address:
            self.inspector_address = _address(inspector_address, "inspector")
            self.judge_address = _address(judge_address, "judge")
            self.components_configured = True
        else:
            self.inspector_address = ""
            self.judge_address = ""
            self.components_configured = False
        self.next_covenant = u256(1)
        self.next_challenge = u256(1)
        self.total_deposited = u256(0)
        self.stake_escrow = u256(0)
        self.bond_escrow = u256(0)
        self.appeal_escrow = u256(0)
        self.total_claimable = u256(0)
        self.total_withdrawn = u256(0)
        self.covenants_activated = u256(0)
        self.covenants_breached = u256(0)
        self.covenants_expired = u256(0)
        self.total_challenges = u256(0)

    def _covenant(self, covenant_id: str) -> dict:
        if covenant_id not in self.covenants:
            raise gl.vm.UserError("[EXPECTED] covenant not found")
        return json.loads(self.covenants[covenant_id])

    def _challenge(self, challenge_id: str) -> dict:
        if challenge_id not in self.challenges:
            raise gl.vm.UserError("[EXPECTED] challenge not found")
        return json.loads(self.challenges[challenge_id])

    def _save_covenant(self, covenant: dict) -> None:
        self.covenants[covenant["id"]] = _json(covenant)

    def _save_challenge(self, challenge: dict) -> None:
        self.challenges[challenge["id"]] = _json(challenge)

    def _components_only(self) -> None:
        if not self.components_configured:
            raise gl.vm.UserError("[EXPECTED] protocol components are not configured")

    def _inspector_only(self) -> None:
        if str(gl.message.sender_address).lower() != self.inspector_address.lower():
            raise gl.vm.UserError("[EXPECTED] only the configured inspector can callback")

    def _judge_only(self) -> None:
        if str(gl.message.sender_address).lower() != self.judge_address.lower():
            raise gl.vm.UserError("[EXPECTED] only the configured judge can callback")

    @gl.public.write
    def configure_components(self, inspector_address: str, judge_address: str) -> None:
        if self.components_configured:
            raise gl.vm.UserError("[EXPECTED] protocol components are already configured")
        if str(gl.message.sender_address).lower() != self.bootstrapper.lower():
            raise gl.vm.UserError("[EXPECTED] only the deployment bootstrapper can configure components")
        self.inspector_address = _address(inspector_address, "inspector")
        self.judge_address = _address(judge_address, "judge")
        self.components_configured = True
        self.bootstrapper = ""

    def _credit(self, recipient: str, amount: int) -> None:
        if amount <= 0:
            return
        account = Address(recipient)
        current = int(self.credits[account]) if account in self.credits else 0
        self.credits[account] = u256(current + amount)
        self.total_claimable = u256(int(self.total_claimable) + amount)

    def _release_bond(self, challenge: dict, recipient: str) -> None:
        amount = int(challenge["bond_atto"])
        if amount <= 0 or challenge.get("bond_released"):
            return
        self.bond_escrow = u256(int(self.bond_escrow) - amount)
        self._credit(recipient, amount)
        challenge["bond_released"] = True
        challenge["bond_recipient"] = recipient

    def _release_appeal_bond(self, challenge: dict, recipient: str) -> None:
        amount = int(challenge.get("appeal_bond_atto", "0"))
        if amount <= 0 or challenge.get("appeal_bond_released"):
            return
        self.appeal_escrow = u256(int(self.appeal_escrow) - amount)
        self._credit(recipient, amount)
        challenge["appeal_bond_released"] = True
        challenge["appeal_bond_recipient"] = recipient

    def _release_stake(self, covenant: dict, recipient: str, amount: int = -1) -> int:
        stake = int(covenant["remaining_stake_atto"])
        release = stake if amount < 0 else amount
        if release <= 0 or release > stake:
            raise gl.vm.UserError("[EXPECTED] invalid stake release")
        self.stake_escrow = u256(int(self.stake_escrow) - release)
        self._credit(recipient, release)
        covenant["remaining_stake_atto"] = str(stake - release)
        return release

    def _clear_pending(self, covenant: dict, challenge_id: str) -> None:
        if covenant.get("pending_challenge") == challenge_id:
            covenant["pending_challenge"] = ""

    def _accounting_ok(self) -> bool:
        return int(self.total_deposited) == (
            int(self.stake_escrow) + int(self.bond_escrow) + int(self.appeal_escrow)
            + int(self.total_claimable) + int(self.total_withdrawn)
        )

    def _validate_callback_json(self, raw: str) -> dict:
        try:
            value = json.loads(raw)
        except Exception:
            raise gl.vm.UserError("[EXPECTED] malformed semantic callback") from None
        if not isinstance(value, dict):
            raise gl.vm.UserError("[EXPECTED] semantic callback must be an object")
        return value

    def _validate_baseline_packet(self, result: dict) -> None:
        fields = (
            "source_accessible", "same_subject", "protected_promise_supported", "rule_testable",
            "time_scope_valid", "baseline_compliant", "breach_condition_present",
        )
        if any(type(result.get(field)) is not bool for field in fields):
            raise gl.vm.UserError("[EXPECTED] baseline callback fields must be booleans")
        status = result.get("status")
        if status == "BASELINE_VERIFIED":
            if (not all(result[field] for field in fields if field != "breach_condition_present")
                    or result["breach_condition_present"]):
                raise gl.vm.UserError("[EXPECTED] verified baseline must be compliant and breach-free")
        elif status == "SOURCE_UNAVAILABLE":
            if any(result[field] for field in fields):
                raise gl.vm.UserError("[EXPECTED] unavailable baseline cannot carry positive semantic fields")
        elif status == "PROMISE_NOT_SUPPORTED":
            if result["protected_promise_supported"] or result["baseline_compliant"]:
                raise gl.vm.UserError("[EXPECTED] unsupported promise cannot be a compliant baseline")
        elif status == "AMBIGUOUS":
            if result["baseline_compliant"]:
                raise gl.vm.UserError("[EXPECTED] ambiguous baseline cannot be certified compliant")
        else:
            raise gl.vm.UserError("[EXPECTED] unknown baseline status")

    def _validate_inspection_packet(self, result: dict) -> None:
        fields = (
            "source_accessible", "same_subject", "promise_still_supported", "current_compliant",
            "breach_condition_now_supported", "effective_now",
        )
        if any(type(result.get(field)) is not bool for field in fields):
            raise gl.vm.UserError("[EXPECTED] inspection callback fields must be booleans")
        status = result.get("status")
        if status == "NO_RELEVANT_CHANGE":
            if (not result["source_accessible"] or not result["same_subject"]
                    or not result["promise_still_supported"] or not result["current_compliant"]
                    or result["breach_condition_now_supported"]):
                raise gl.vm.UserError("[EXPECTED] no-change result requires current compliant source")
        elif status == "MATERIAL_CHANGE":
            if (not result["source_accessible"] or not result["same_subject"]
                    or (result["current_compliant"] and not result["breach_condition_now_supported"])
                    or not result["effective_now"]):
                raise gl.vm.UserError("[EXPECTED] material change requires current same-subject non-compliance")
        elif status == "SOURCE_UNAVAILABLE":
            if any(result[field] for field in fields):
                raise gl.vm.UserError("[EXPECTED] unavailable inspection cannot carry positive semantic fields")
        elif status == "AMBIGUOUS":
            if any(result[field] for field in (
                "promise_still_supported", "current_compliant", "breach_condition_now_supported", "effective_now"
            )):
                raise gl.vm.UserError("[EXPECTED] ambiguous inspection cannot assert a definitive semantic state")
        else:
            raise gl.vm.UserError("[EXPECTED] unknown inspection status")

    def _validate_v2_evidence(self, covenant: dict, result: dict) -> None:
        policy = covenant["evidence_policy"]
        if result.get("policy_digest") != covenant["evidence_policy_digest"]:
            raise gl.vm.UserError("[EXPECTED] evidence policy commitment mismatch")
        evidence = result.get("evidence")
        classes = result.get("corroboration")
        if (not isinstance(evidence, list) or len(evidence) != len(policy["sources"])
                or not isinstance(classes, list) or len(classes) != len(evidence) - 1):
            raise gl.vm.UserError("[EXPECTED] malformed evidence manifest")
        count = 0
        contradiction = False
        for index, item in enumerate(evidence):
            source = policy["sources"][index]
            if not isinstance(item, dict) or any(item.get(key) != source[key] for key in ("url", "role", "publisher")):
                raise gl.vm.UserError("[EXPECTED] evidence source substitution")
            status = item.get("retrieval_status")
            artifact = item.get("artifact")
            if status == "AVAILABLE":
                if not isinstance(artifact, dict) or artifact.get("manifest_version") != 1:
                    raise gl.vm.UserError("[EXPECTED] invalid evidence artifact")
                rendered = artifact.get("rendered_text")
                if not isinstance(rendered, str) or not rendered or len(rendered.encode("utf-8")) > 6000:
                    raise gl.vm.UserError("[EXPECTED] evidence artifact exceeds bound")
                if (type(artifact.get("rendered_utf8_bytes")) is not int
                        or artifact.get("rendered_utf8_bytes") != len(rendered.encode("utf-8"))
                        or artifact.get("rendered_sha256") != hashlib.sha256(rendered.encode("utf-8")).hexdigest()
                        or artifact.get("artifact_scope") != "GENLAYER_RENDERED_TEXT_NOT_RAW_HTTP_BYTES"):
                    raise gl.vm.UserError("[EXPECTED] evidence content commitment mismatch")
            elif status not in ("UNAVAILABLE", "OVERSIZED_OR_EMPTY") or artifact is not None:
                raise gl.vm.UserError("[EXPECTED] invalid evidence retrieval status")
            if index > 0:
                classification = classes[index - 1]
                if classification not in ("SUPPORTS", "CONTRADICTS", "INCONCLUSIVE"):
                    raise gl.vm.UserError("[EXPECTED] invalid source classification")
                if status != "AVAILABLE" and classification != "INCONCLUSIVE":
                    raise gl.vm.UserError("[EXPECTED] unavailable source cannot corroborate")
                count += classification == "SUPPORTS" and source["role"] == "CORROBORATING"
                contradiction = contradiction or classification == "CONTRADICTS"
        if (type(result.get("corroboration_count")) is not int
                or result.get("corroboration_count") != count or result.get("contradictory") is not contradiction):
            raise gl.vm.UserError("[EXPECTED] inconsistent evidence summary")
        if result.get("status") in ("BASELINE_VERIFIED", "MATERIAL_CHANGE", "NO_RELEVANT_CHANGE"):
            if evidence[0]["retrieval_status"] != "AVAILABLE" or contradiction or count < policy["min_corroborations"]:
                raise gl.vm.UserError("[EXPECTED] definitive assessment lacks required evidence")

    def _settle_v2(self, challenge: dict, covenant: dict, final_outcome: str, appeal_result: str) -> None:
        if challenge.get("settled_at"):
            raise gl.vm.UserError("[EXPECTED] challenge already settled")
        if final_outcome not in ("BREACH", "PERMITTED_CHANGE", "NO_RELEVANT_CHANGE", "INCONCLUSIVE"):
            raise gl.vm.UserError("[EXPECTED] invalid final outcome")
        challenger = challenge["challenger"]
        owner = covenant["owner"]
        if final_outcome == "BREACH":
            stake = int(covenant["remaining_stake_atto"])
            if stake <= 0:
                raise gl.vm.UserError("[EXPECTED] covenant stake already released")
            reward = stake * int(covenant["finder_reward_bps"]) // 10000
            self._release_bond(challenge, challenger)
            self._release_stake(covenant, challenger, reward)
            self._release_stake(covenant, covenant["beneficiary"], stake - reward)
            challenge["finder_reward_atto"] = str(reward)
            covenant.update({"status": "BREACHED", "breach_challenge": challenge["id"],
                             "breached_at": _iso(), "closed_at": _iso(), "pending_challenge": ""})
            self.covenants_breached = u256(int(self.covenants_breached) + 1)
        elif final_outcome in ("PERMITTED_CHANGE", "NO_RELEVANT_CHANGE"):
            self._release_bond(challenge, owner)
            self._clear_pending(covenant, challenge["id"])
            covenant["last_challenge_at"] = str(_now())
        else:
            self._release_bond(challenge, challenger)
            self._clear_pending(covenant, challenge["id"])
            covenant["last_challenge_at"] = str(_now())
        appellant = challenge.get("appellant", "")
        if appellant:
            if appeal_result == "UPHELD":
                recipient = challenger if appellant.lower() == owner.lower() else owner
            else:
                recipient = appellant
            self._release_appeal_bond(challenge, recipient)
        challenge["status"] = final_outcome
        challenge["appeal_result"] = appeal_result
        challenge["settled_at"] = _iso()

    @gl.public.write.payable
    def create_covenant(self, title: str, subject: str, canonical_url: str, protected_promise: str,
                        breach_rule: str, permitted_changes: str, beneficiary: str,
                        finder_reward_bps: u256, expires_at: u256) -> str:
        self._components_only()
        title = _text(title, "title", MAX_TITLE, 4)
        subject = _text(subject, "subject", MAX_SUBJECT, 12)
        canonical_url = _text(canonical_url, "canonical url", MAX_URL, 8)
        protected_promise = _text(protected_promise, "protected promise", MAX_PROMISE, 12)
        breach_rule = _text(breach_rule, "breach rule", MAX_RULE, 20)
        permitted_changes = _text(permitted_changes, "permitted changes", MAX_PERMITTED, 4)
        if not canonical_url.startswith("https://"):
            raise gl.vm.UserError("[EXPECTED] canonical source must use https")
        beneficiary = _address(beneficiary, "beneficiary")
        reward_bps = int(finder_reward_bps)
        if not MIN_REWARD_BPS <= reward_bps <= MAX_REWARD_BPS:
            raise gl.vm.UserError("[EXPECTED] finder reward must be 1%..25%")
        stake = int(gl.message.value)
        if not MIN_STAKE <= stake <= MAX_STAKE:
            raise gl.vm.UserError("[EXPECTED] stake must be 0.001..10 test GEN")
        now = _now()
        expiry = int(expires_at)
        if not now + MIN_LIFETIME <= expiry <= now + MAX_LIFETIME:
            raise gl.vm.UserError("[EXPECTED] expiry must be 2 hours..30 days ahead")

        covenant_id = "dl-" + str(int(self.next_covenant))
        self.next_covenant = u256(int(self.next_covenant) + 1)
        bond = max(MIN_BOND, stake // 100)
        covenant = {
            "id": covenant_id, "title": title, "subject": subject, "canonical_url": canonical_url,
            "protected_promise": protected_promise, "breach_rule": breach_rule,
            "permitted_changes": permitted_changes, "owner": str(gl.message.sender_address),
            "beneficiary": beneficiary, "finder_reward_bps": str(reward_bps),
            "stake_atto": str(stake), "remaining_stake_atto": str(stake), "challenge_bond_atto": str(bond),
            "status": "BASELINE_PENDING", "created_at": _iso(), "activated_at": "", "expires_at": str(expiry),
            "baseline_deadline": str(now + BASELINE_TIMEOUT), "baseline_attempt": 1, "baseline_review": None,
            "pending_challenge": "", "challenge_count": 0, "last_challenge_at": "0",
            "last_inspection": None, "breach_challenge": "", "breached_at": "", "closed_at": "",
        }
        self._save_covenant(covenant)
        self.covenant_ids.append(covenant_id)
        self.owner_latest[Address(str(gl.message.sender_address))] = covenant_id
        self.total_deposited = u256(int(self.total_deposited) + stake)
        self.stake_escrow = u256(int(self.stake_escrow) + stake)
        inspector = gl.get_contract_at(Address(self.inspector_address))
        inspector.emit(on="finalized").inspect_baseline(
            f"{covenant_id}:baseline:1", covenant_id, str(gl.message.contract_address), subject, canonical_url,
            protected_promise, breach_rule, permitted_changes
        )
        return covenant_id

    @gl.public.write.payable
    def create_covenant_v2(self, title: str, subject: str, canonical_url: str, protected_promise: str,
                           breach_rule: str, permitted_changes: str, beneficiary: str,
                           finder_reward_bps: u256, expires_at: u256, policy_json: str) -> str:
        self._components_only()
        title = _text(title, "title", MAX_TITLE, 4)
        subject = _text(subject, "subject", MAX_SUBJECT, 12)
        canonical_url = _text(canonical_url, "canonical url", MAX_URL, 8)
        protected_promise = _text(protected_promise, "protected promise", MAX_PROMISE, 12)
        breach_rule = _text(breach_rule, "breach rule", MAX_RULE, 20)
        permitted_changes = _text(permitted_changes, "permitted changes", MAX_PERMITTED, 4)
        policy = _policy(policy_json, canonical_url)
        beneficiary = _address(beneficiary, "beneficiary")
        reward_bps = int(finder_reward_bps)
        if not MIN_REWARD_BPS <= reward_bps <= MAX_REWARD_BPS:
            raise gl.vm.UserError("[EXPECTED] finder reward must be 1%..25%")
        stake = int(gl.message.value)
        if not MIN_STAKE <= stake <= MAX_STAKE:
            raise gl.vm.UserError("[EXPECTED] stake must be 0.001..10 test GEN")
        now = _now()
        expiry = int(expires_at)
        if not now + MIN_LIFETIME <= expiry <= now + MAX_LIFETIME:
            raise gl.vm.UserError("[EXPECTED] expiry must be 2 hours..30 days ahead")
        covenant_id = "dl-" + str(int(self.next_covenant))
        self.next_covenant = u256(int(self.next_covenant) + 1)
        bond = max(MIN_BOND, stake // 100)
        policy_digest = hashlib.sha256(_json(policy).encode("utf-8")).hexdigest()
        covenant = {
            "id": covenant_id, "protocol_version": 2, "title": title, "subject": subject,
            "canonical_url": canonical_url, "protected_promise": protected_promise, "breach_rule": breach_rule,
            "permitted_changes": permitted_changes, "owner": str(gl.message.sender_address),
            "beneficiary": beneficiary, "finder_reward_bps": str(reward_bps),
            "stake_atto": str(stake), "remaining_stake_atto": str(stake), "challenge_bond_atto": str(bond),
            "evidence_policy": policy, "evidence_policy_digest": policy_digest,
            "status": "BASELINE_PENDING", "created_at": _iso(), "activated_at": "", "expires_at": str(expiry),
            "baseline_deadline": str(now + BASELINE_TIMEOUT), "baseline_attempt": 1, "baseline_review": None,
            "pending_challenge": "", "challenge_count": 0, "last_challenge_at": "0",
            "last_inspection": None, "breach_challenge": "", "breached_at": "", "closed_at": "",
        }
        self._save_covenant(covenant)
        self.covenant_ids.append(covenant_id)
        self.owner_latest[Address(str(gl.message.sender_address))] = covenant_id
        self.total_deposited = u256(int(self.total_deposited) + stake)
        self.stake_escrow = u256(int(self.stake_escrow) + stake)
        gl.get_contract_at(Address(self.inspector_address)).emit(on="finalized").inspect_policy_baseline(
            f"{covenant_id}:baseline:1", covenant_id, str(gl.message.contract_address), subject,
            protected_promise, breach_rule, permitted_changes, _json(policy), policy_digest
        )
        return covenant_id

    @gl.public.write
    def retry_baseline(self, covenant_id: str) -> None:
        covenant = self._covenant(covenant_id)
        if str(gl.message.sender_address).lower() != covenant["owner"].lower():
            raise gl.vm.UserError("[EXPECTED] only covenant owner can retry baseline")
        if covenant["status"] != "BASELINE_RETRYABLE":
            raise gl.vm.UserError("[EXPECTED] baseline is not retryable")
        if _now() >= int(covenant["expires_at"]):
            self._release_stake(covenant, covenant["owner"])
            covenant.update({"status": "EXPIRED_UNVERIFIED", "closed_at": _iso()})
            self._save_covenant(covenant)
            return
        covenant["status"] = "BASELINE_PENDING"
        covenant["baseline_deadline"] = str(_now() + BASELINE_TIMEOUT)
        covenant["baseline_attempt"] = int(covenant.get("baseline_attempt", 1)) + 1
        self._save_covenant(covenant)
        request_id = f"{covenant_id}:baseline:{covenant['baseline_attempt']}"
        inspector = gl.get_contract_at(Address(self.inspector_address)).emit(on="finalized")
        if covenant.get("protocol_version") == 2:
            inspector.inspect_policy_baseline(
                request_id, covenant_id, str(gl.message.contract_address), covenant["subject"],
                covenant["protected_promise"], covenant["breach_rule"], covenant["permitted_changes"],
                _json(covenant["evidence_policy"]), covenant["evidence_policy_digest"])
        else:
            inspector.inspect_baseline(
                request_id, covenant_id, str(gl.message.contract_address), covenant["subject"], covenant["canonical_url"],
                covenant["protected_promise"], covenant["breach_rule"], covenant["permitted_changes"])

    @gl.public.write
    def expire_baseline(self, covenant_id: str) -> None:
        covenant = self._covenant(covenant_id)
        if covenant["status"] != "BASELINE_PENDING":
            raise gl.vm.UserError("[EXPECTED] baseline is not pending")
        if _now() < int(covenant["baseline_deadline"]):
            raise gl.vm.UserError("[EXPECTED] baseline deadline has not passed")
        if _now() >= int(covenant["expires_at"]):
            self._release_stake(covenant, covenant["owner"])
            covenant.update({"status": "EXPIRED_UNVERIFIED", "closed_at": _iso()})
        else:
            covenant["status"] = "BASELINE_RETRYABLE"
        self._save_covenant(covenant)

    @gl.public.write
    def record_baseline(self, covenant_id: str, request_id: str, result_json: str) -> None:
        self._inspector_only()
        covenant = self._covenant(covenant_id)
        if covenant["status"] != "BASELINE_PENDING":
            return
        expected_request = f"{covenant_id}:baseline:{covenant['baseline_attempt']}"
        if request_id != expected_request:
            return
        result = self._validate_callback_json(result_json)
        if result.get("request_id") != expected_request or result.get("kind") != "BASELINE":
            raise gl.vm.UserError("[EXPECTED] baseline callback request mismatch")
        self._validate_baseline_packet(result)
        if covenant.get("protocol_version") == 2:
            self._validate_v2_evidence(covenant, result)
        status = result.get("status")
        covenant["baseline_review"] = result
        if _now() >= int(covenant["expires_at"]):
            self._release_stake(covenant, covenant["owner"])
            covenant.update({"status": "EXPIRED_UNVERIFIED", "closed_at": _iso()})
        elif _now() >= int(covenant["baseline_deadline"]):
            covenant["status"] = "BASELINE_RETRYABLE"
        elif status == "BASELINE_VERIFIED":
            covenant.update({"status": "ACTIVE", "activated_at": _iso()})
            self.covenants_activated = u256(int(self.covenants_activated) + 1)
        elif status == "SOURCE_UNAVAILABLE":
            covenant["status"] = "BASELINE_RETRYABLE"
        else:
            self._release_stake(covenant, covenant["owner"])
            covenant.update({"status": "BASELINE_REJECTED", "closed_at": _iso()})
        self._save_covenant(covenant)

    @gl.public.write.payable
    def challenge_covenant(self, covenant_id: str) -> str:
        covenant = self._covenant(covenant_id)
        now = _now()
        if covenant["status"] != "ACTIVE" or now >= int(covenant["expires_at"]):
            raise gl.vm.UserError("[EXPECTED] covenant is not challengeable")
        if covenant.get("pending_challenge"):
            raise gl.vm.UserError("[EXPECTED] covenant already has a pending challenge")
        challenger = str(gl.message.sender_address)
        if challenger.lower() == covenant["owner"].lower():
            raise gl.vm.UserError("[EXPECTED] covenant owner cannot challenge their own covenant")
        if now < int(covenant.get("last_challenge_at", "0")) + CHALLENGE_COOLDOWN:
            raise gl.vm.UserError("[EXPECTED] covenant challenge cooldown is active")
        required_time = INSPECTION_TIMEOUT + JUDGE_TIMEOUT + 300
        if covenant.get("protocol_version") == 2:
            required_time += APPEAL_WINDOW + APPEAL_TIMEOUT
        if now + required_time >= int(covenant["expires_at"]):
            raise gl.vm.UserError("[EXPECTED] insufficient time remains for challenge adjudication")
        bond = int(gl.message.value)
        if bond != int(covenant["challenge_bond_atto"]):
            raise gl.vm.UserError("[EXPECTED] send the exact challenge bond")

        challenge_id = "dc-" + str(int(self.next_challenge))
        self.next_challenge = u256(int(self.next_challenge) + 1)
        index = int(covenant["challenge_count"])
        challenge = {
            "id": challenge_id, "covenant_id": covenant_id, "challenger": challenger,
            "status": "INSPECTION_PENDING", "bond_atto": str(bond), "bond_released": False,
            "bond_recipient": "", "created_at": _iso(), "stage_deadline": str(now + INSPECTION_TIMEOUT),
            "inspection": None, "judgment": None, "settled_at": "", "finder_reward_atto": "0",
            "appeal_deadline": "0", "appeal_bond_atto": "0", "appellant": "",
            "appeal_bond_released": False, "appeal_result": "", "appeal_judgment": None,
        }
        self._save_challenge(challenge)
        self.challenge_ids.append(challenge_id)
        self.covenant_challenge_index[f"{covenant_id}:{index}"] = challenge_id
        wallet = Address(challenger)
        wallet_count = int(self.wallet_challenge_counts[wallet]) if wallet in self.wallet_challenge_counts else 0
        self.wallet_challenge_index[f"{challenger.lower()}:{wallet_count}"] = challenge_id
        self.wallet_challenge_counts[wallet] = u256(wallet_count + 1)
        covenant["challenge_count"] = index + 1
        covenant["pending_challenge"] = challenge_id
        covenant["last_challenge_at"] = str(now)
        self._save_covenant(covenant)
        self.total_challenges = u256(int(self.total_challenges) + 1)
        self.total_deposited = u256(int(self.total_deposited) + bond)
        self.bond_escrow = u256(int(self.bond_escrow) + bond)
        baseline_packet = _json({"status": covenant["baseline_review"]["status"],
                                 **{key: covenant["baseline_review"][key] for key in (
                                     "source_accessible", "same_subject", "protected_promise_supported", "rule_testable",
                                     "time_scope_valid", "baseline_compliant", "breach_condition_present", "basis",
                                 )}})
        inspector = gl.get_contract_at(Address(self.inspector_address)).emit(on="finalized")
        if covenant.get("protocol_version") == 2:
            inspector.inspect_policy_current(
                challenge_id, str(gl.message.contract_address), covenant["subject"],
                covenant["protected_promise"], covenant["breach_rule"], covenant["permitted_changes"],
                _json(covenant["evidence_policy"]), covenant["evidence_policy_digest"], baseline_packet)
        else:
            inspector.inspect_current(
                challenge_id, str(gl.message.contract_address), covenant["subject"], covenant["canonical_url"],
                covenant["protected_promise"], covenant["breach_rule"], covenant["permitted_changes"], baseline_packet)
        return challenge_id

    @gl.public.write
    def record_inspection(self, challenge_id: str, result_json: str) -> None:
        self._inspector_only()
        challenge = self._challenge(challenge_id)
        if challenge["status"] != "INSPECTION_PENDING":
            return
        covenant = self._covenant(challenge["covenant_id"])
        result = self._validate_callback_json(result_json)
        if result.get("request_id") != challenge_id or result.get("kind") != "CURRENT":
            raise gl.vm.UserError("[EXPECTED] inspection callback request mismatch")
        self._validate_inspection_packet(result)
        if covenant.get("protocol_version") == 2:
            self._validate_v2_evidence(covenant, result)
        status = result.get("status")
        if (not isinstance(result.get("baseline_context"), dict)
                or result["baseline_context"].get("status") != "BASELINE_VERIFIED"
                or any(result["baseline_context"].get(key) != covenant["baseline_review"].get(key) for key in (
                    "source_accessible", "same_subject", "protected_promise_supported", "rule_testable",
                    "time_scope_valid", "baseline_compliant", "breach_condition_present", "basis",
                ))):
            raise gl.vm.UserError("[EXPECTED] inspection does not reference the verified baseline")
        challenge["inspection"] = result
        covenant["last_inspection"] = result

        if covenant["status"] != "ACTIVE" or _now() >= int(covenant["expires_at"]) or _now() >= int(challenge["stage_deadline"]):
            challenge["status"] = "STALE"
            challenge["settled_at"] = _iso()
            self._release_bond(challenge, challenge["challenger"])
            self._clear_pending(covenant, challenge_id)
            covenant["last_challenge_at"] = str(_now())
        elif status == "NO_RELEVANT_CHANGE":
            if covenant.get("protocol_version") == 2:
                challenge["status"] = "PROVISIONAL_NO_RELEVANT_CHANGE"
                challenge["appeal_deadline"] = str(_now() + APPEAL_WINDOW)
            else:
                challenge["status"] = "NO_RELEVANT_CHANGE"
                challenge["settled_at"] = _iso()
                self._release_bond(challenge, covenant["owner"])
                self._clear_pending(covenant, challenge_id)
                covenant["last_challenge_at"] = str(_now())
        elif status in ("SOURCE_UNAVAILABLE", "AMBIGUOUS"):
            challenge["status"] = status
            challenge["settled_at"] = _iso()
            self._release_bond(challenge, challenge["challenger"])
            self._clear_pending(covenant, challenge_id)
            covenant["last_challenge_at"] = str(_now())
        else:
            challenge["status"] = "JUDGMENT_PENDING"
            challenge["stage_deadline"] = str(_now() + JUDGE_TIMEOUT)
            self._save_challenge(challenge)
            self._save_covenant(covenant)
            judge = gl.get_contract_at(Address(self.judge_address)).emit(on="finalized")
            if covenant.get("protocol_version") == 2:
                judge.judge_policy(challenge_id, challenge_id, str(gl.message.contract_address), covenant["subject"],
                                   covenant["protected_promise"], covenant["breach_rule"], covenant["permitted_changes"],
                                   _json(result), _json(covenant["evidence_policy"]),
                                   covenant["evidence_policy_digest"], "", False)
            else:
                judge.judge_breach(
                    challenge_id, str(gl.message.contract_address), covenant["subject"], covenant["canonical_url"],
                    covenant["protected_promise"], covenant["breach_rule"], covenant["permitted_changes"],
                    _json(result))
            return

        self._save_challenge(challenge)
        self._save_covenant(covenant)

    @gl.public.write
    def record_judgment(self, challenge_id: str, result_json: str) -> None:
        self._judge_only()
        challenge = self._challenge(challenge_id)
        if challenge["status"] != "JUDGMENT_PENDING":
            return
        covenant = self._covenant(challenge["covenant_id"])
        result = self._validate_callback_json(result_json)
        outcome = result.get("outcome")
        fields = ("breach_supported", "permitted_by_rule", "same_subject", "effective_now")
        if (result.get("request_id") != challenge_id or result.get("kind") != "JUDGMENT"
                or outcome not in JUDGMENT_OUTCOMES or any(type(result.get(field)) is not bool for field in fields)):
            raise gl.vm.UserError("[EXPECTED] malformed breach judgment")
        inspection = challenge.get("inspection")
        if not isinstance(inspection, dict) or inspection.get("status") != "MATERIAL_CHANGE":
            raise gl.vm.UserError("[EXPECTED] judgment requires a valid material inspection")
        if outcome == "BREACH" and (
            not result["breach_supported"] or result["permitted_by_rule"]
            or not result["same_subject"] or not result["effective_now"]
        ):
            raise gl.vm.UserError("[EXPECTED] inconsistent breach judgment")
        if outcome == "PERMITTED_CHANGE" and (
            not result["permitted_by_rule"] or result["breach_supported"]
            or not result["same_subject"] or not result["effective_now"]
        ):
            raise gl.vm.UserError("[EXPECTED] inconsistent permitted-change judgment")
        if outcome == "INCONCLUSIVE" and result["breach_supported"] and result["permitted_by_rule"]:
            raise gl.vm.UserError("[EXPECTED] inconclusive judgment asserts contradictory findings")
        if covenant.get("protocol_version") == 2:
            expected_digest = hashlib.sha256(_json(inspection["evidence"]).encode("utf-8")).hexdigest()
            if (result.get("policy_digest") != covenant["evidence_policy_digest"]
                    or result.get("evidence_digest") != expected_digest):
                raise gl.vm.UserError("[EXPECTED] judgment evidence reference mismatch")
        challenge["judgment"] = result

        if covenant.get("protocol_version") == 2:
            if (covenant["status"] != "ACTIVE" or _now() >= int(covenant["expires_at"])
                    or _now() >= int(challenge["stage_deadline"])):
                self._settle_v2(challenge, covenant, "INCONCLUSIVE", "NOT_APPEALED")
            elif outcome == "INCONCLUSIVE":
                self._settle_v2(challenge, covenant, "INCONCLUSIVE", "NOT_APPEALED")
            else:
                challenge["status"] = "PROVISIONAL_" + outcome
                challenge["appeal_deadline"] = str(_now() + APPEAL_WINDOW)
            self._save_challenge(challenge)
            self._save_covenant(covenant)
            return

        if covenant["status"] != "ACTIVE" or _now() >= int(covenant["expires_at"]) or _now() >= int(challenge["stage_deadline"]):
            challenge["status"] = "STALE"
            challenge["settled_at"] = _iso()
            self._release_bond(challenge, challenge["challenger"])
            self._clear_pending(covenant, challenge_id)
            covenant["last_challenge_at"] = str(_now())
        elif outcome == "PERMITTED_CHANGE":
            challenge["status"] = "PERMITTED_CHANGE"
            challenge["settled_at"] = _iso()
            self._release_bond(challenge, covenant["owner"])
            self._clear_pending(covenant, challenge_id)
            covenant["last_challenge_at"] = str(_now())
        elif outcome == "INCONCLUSIVE":
            challenge["status"] = "INCONCLUSIVE"
            challenge["settled_at"] = _iso()
            self._release_bond(challenge, challenge["challenger"])
            self._clear_pending(covenant, challenge_id)
            covenant["last_challenge_at"] = str(_now())
        else:
            stake = int(covenant["remaining_stake_atto"])
            if stake <= 0:
                raise gl.vm.UserError("[EXPECTED] covenant stake already released")
            reward = stake * int(covenant["finder_reward_bps"]) // 10000
            beneficiary_amount = stake - reward
            self._release_bond(challenge, challenge["challenger"])
            self._release_stake(covenant, challenge["challenger"], reward)
            self._release_stake(covenant, covenant["beneficiary"], beneficiary_amount)
            challenge["status"] = "BREACH"
            challenge["finder_reward_atto"] = str(reward)
            challenge["settled_at"] = _iso()
            covenant.update({"status": "BREACHED", "breach_challenge": challenge_id,
                             "breached_at": _iso(), "closed_at": _iso(), "pending_challenge": ""})
            self.covenants_breached = u256(int(self.covenants_breached) + 1)

        self._save_challenge(challenge)
        self._save_covenant(covenant)

    @gl.public.write.payable
    def appeal_challenge(self, challenge_id: str, rebuttal: str) -> None:
        challenge = self._challenge(challenge_id)
        covenant = self._covenant(challenge["covenant_id"])
        status = challenge["status"]
        if covenant.get("protocol_version") != 2 or status not in (
            "PROVISIONAL_BREACH", "PROVISIONAL_PERMITTED_CHANGE", "PROVISIONAL_NO_RELEVANT_CHANGE"
        ):
            raise gl.vm.UserError("[EXPECTED] challenge is not appealable")
        if _now() >= int(challenge["appeal_deadline"]):
            raise gl.vm.UserError("[EXPECTED] appeal deadline passed")
        appellant = str(gl.message.sender_address)
        expected = covenant["owner"] if status == "PROVISIONAL_BREACH" else challenge["challenger"]
        if appellant.lower() != expected.lower():
            raise gl.vm.UserError("[EXPECTED] sender cannot appeal this outcome")
        rebuttal = _text(rebuttal, "rebuttal", MAX_REBUTTAL, 12)
        bond = int(gl.message.value)
        if bond != int(covenant["challenge_bond_atto"]):
            raise gl.vm.UserError("[EXPECTED] send the exact appeal bond")
        if not isinstance(challenge.get("inspection"), dict) or not challenge["inspection"].get("evidence"):
            raise gl.vm.UserError("[EXPECTED] committed incident evidence unavailable")
        challenge["status"] = "APPEAL_PENDING"
        challenge["appellant"] = appellant
        challenge["appeal_bond_atto"] = str(bond)
        challenge["rebuttal"] = rebuttal
        challenge["stage_deadline"] = str(_now() + APPEAL_TIMEOUT)
        challenge["appeal_request_id"] = challenge_id + ":appeal:1"
        account = Address(appellant)
        appeal_index = int(self.wallet_appeal_counts[account]) if account in self.wallet_appeal_counts else 0
        self.wallet_appeal_index[f"{appellant.lower()}:{appeal_index}"] = challenge_id
        self.wallet_appeal_counts[account] = u256(appeal_index + 1)
        self._save_challenge(challenge)
        self.total_deposited = u256(int(self.total_deposited) + bond)
        self.appeal_escrow = u256(int(self.appeal_escrow) + bond)
        gl.get_contract_at(Address(self.judge_address)).emit(on="finalized").judge_policy(
            challenge["appeal_request_id"], challenge_id, str(gl.message.contract_address), covenant["subject"],
            covenant["protected_promise"], covenant["breach_rule"], covenant["permitted_changes"],
            _json(challenge["inspection"]), _json(covenant["evidence_policy"]),
            covenant["evidence_policy_digest"], rebuttal, True)

    @gl.public.write
    def record_appeal(self, challenge_id: str, request_id: str, result_json: str) -> None:
        self._judge_only()
        challenge = self._challenge(challenge_id)
        if challenge["status"] != "APPEAL_PENDING" or request_id != challenge.get("appeal_request_id"):
            return
        covenant = self._covenant(challenge["covenant_id"])
        result = self._validate_callback_json(result_json)
        expected_digest = hashlib.sha256(_json(challenge["inspection"]["evidence"]).encode("utf-8")).hexdigest()
        if (result.get("request_id") != request_id or result.get("kind") != "APPEAL"
                or result.get("policy_digest") != covenant["evidence_policy_digest"]
                or result.get("evidence_digest") != expected_digest):
            raise gl.vm.UserError("[EXPECTED] appeal evidence reference mismatch")
        outcome = result.get("outcome")
        fields = ("breach_supported", "permitted_by_rule", "same_subject", "effective_now")
        if outcome not in JUDGMENT_OUTCOMES or any(type(result.get(field)) is not bool for field in fields):
            raise gl.vm.UserError("[EXPECTED] malformed appeal decision")
        if outcome == "BREACH" and (not result["breach_supported"] or result["permitted_by_rule"]
                                     or not result["same_subject"] or not result["effective_now"]):
            raise gl.vm.UserError("[EXPECTED] inconsistent appeal breach")
        if outcome == "PERMITTED_CHANGE" and (not result["permitted_by_rule"] or result["breach_supported"]
                                               or not result["same_subject"] or not result["effective_now"]):
            raise gl.vm.UserError("[EXPECTED] inconsistent appeal permission")
        challenge["appeal_judgment"] = result
        initial = challenge.get("judgment", {}).get("outcome") if challenge.get("judgment") else "NO_RELEVANT_CHANGE"
        if _now() >= int(challenge["stage_deadline"]) or covenant["status"] != "ACTIVE":
            self._settle_v2(challenge, covenant, "INCONCLUSIVE", "TIMED_OUT")
        else:
            final = outcome if outcome != "INCONCLUSIVE" else "INCONCLUSIVE"
            if initial == "NO_RELEVANT_CHANGE" and outcome == "PERMITTED_CHANGE":
                final = "PERMITTED_CHANGE"
            if final == "INCONCLUSIVE":
                appeal_result = "INCONCLUSIVE"
            elif initial == "BREACH":
                appeal_result = "UPHELD" if final == "BREACH" else "OVERTURNED"
            else:
                appeal_result = "OVERTURNED" if final == "BREACH" else "UPHELD"
            self._settle_v2(challenge, covenant, final, appeal_result)
        self._save_challenge(challenge)
        self._save_covenant(covenant)

    @gl.public.write
    def finalize_challenge(self, challenge_id: str) -> None:
        challenge = self._challenge(challenge_id)
        covenant = self._covenant(challenge["covenant_id"])
        status = challenge["status"]
        if covenant.get("protocol_version") != 2 or status not in (
            "PROVISIONAL_BREACH", "PROVISIONAL_PERMITTED_CHANGE", "PROVISIONAL_NO_RELEVANT_CHANGE"
        ):
            raise gl.vm.UserError("[EXPECTED] challenge is not awaiting appeal expiry")
        if _now() < int(challenge["appeal_deadline"]):
            raise gl.vm.UserError("[EXPECTED] appeal window remains open")
        self._settle_v2(challenge, covenant, status[len("PROVISIONAL_"):], "NOT_APPEALED")
        self._save_challenge(challenge)
        self._save_covenant(covenant)

    @gl.public.write
    def expire_challenge(self, challenge_id: str) -> None:
        challenge = self._challenge(challenge_id)
        if challenge["status"] not in ("INSPECTION_PENDING", "JUDGMENT_PENDING", "APPEAL_PENDING"):
            raise gl.vm.UserError("[EXPECTED] challenge is already settled")
        if _now() < int(challenge["stage_deadline"]):
            raise gl.vm.UserError("[EXPECTED] challenge stage deadline has not passed")
        covenant = self._covenant(challenge["covenant_id"])
        if challenge["status"] == "APPEAL_PENDING":
            self._settle_v2(challenge, covenant, "INCONCLUSIVE", "TIMED_OUT")
            self._save_challenge(challenge)
            self._save_covenant(covenant)
            return
        challenge["status"] = "TIMED_OUT"
        challenge["settled_at"] = _iso()
        self._release_bond(challenge, challenge["challenger"])
        self._clear_pending(covenant, challenge_id)
        covenant["last_challenge_at"] = str(_now())
        self._save_challenge(challenge)
        self._save_covenant(covenant)

    @gl.public.write
    def expire_covenant(self, covenant_id: str) -> None:
        covenant = self._covenant(covenant_id)
        if covenant["status"] in TERMINAL_COVENANT:
            raise gl.vm.UserError("[EXPECTED] covenant is already closed")
        if _now() < int(covenant["expires_at"]):
            raise gl.vm.UserError("[EXPECTED] covenant expiry has not passed")
        pending = covenant.get("pending_challenge", "")
        if pending and covenant.get("protocol_version") == 2:
            active = self._challenge(pending)
            if active["status"].startswith("PROVISIONAL_") or active["status"] == "APPEAL_PENDING":
                raise gl.vm.UserError("[EXPECTED] finalize pending appeal before covenant expiry")
        if pending:
            challenge = self._challenge(pending)
            if challenge["status"] in ("INSPECTION_PENDING", "JUDGMENT_PENDING"):
                challenge["status"] = "PROTOCOL_BLOCKED"
                challenge["settled_at"] = _iso()
                self._release_bond(challenge, challenge["challenger"])
                self._save_challenge(challenge)
            covenant["pending_challenge"] = ""
        if int(covenant["remaining_stake_atto"]) > 0:
            self._release_stake(covenant, covenant["owner"])
        if covenant["status"] in ("BASELINE_PENDING", "BASELINE_RETRYABLE"):
            covenant["status"] = "EXPIRED_UNVERIFIED"
        else:
            covenant["status"] = "EXPIRED_UNBREACHED"
        covenant["closed_at"] = _iso()
        self.covenants_expired = u256(int(self.covenants_expired) + 1)
        self._save_covenant(covenant)

    @gl.public.write
    def withdraw_credit(self, recipient: str) -> None:
        recipient = _address(recipient, "credit recipient")
        account = Address(recipient)
        amount = int(self.credits[account]) if account in self.credits else 0
        if amount <= 0:
            raise gl.vm.UserError("[EXPECTED] no credit available")
        self.credits[account] = u256(0)
        self.total_claimable = u256(int(self.total_claimable) - amount)
        self.total_withdrawn = u256(int(self.total_withdrawn) + amount)
        _Recipient(account).emit_transfer(value=amount)

    @gl.public.view
    def get_covenant(self, covenant_id: str) -> dict:
        covenant = self._covenant(covenant_id)
        now = _now()
        required_time = INSPECTION_TIMEOUT + JUDGE_TIMEOUT + 300
        if covenant.get("protocol_version") == 2:
            required_time += APPEAL_WINDOW + APPEAL_TIMEOUT
        covenant["can_challenge"] = (
            covenant["status"] == "ACTIVE" and not covenant.get("pending_challenge")
            and now >= int(covenant.get("last_challenge_at", "0")) + CHALLENGE_COOLDOWN
            and now + required_time < int(covenant["expires_at"])
        )
        pending = covenant.get("pending_challenge", "")
        blocked_by_appeal = bool(pending and covenant.get("protocol_version") == 2 and
                                 (self._challenge(pending)["status"].startswith("PROVISIONAL_")
                                  or self._challenge(pending)["status"] == "APPEAL_PENDING"))
        covenant["can_expire"] = (now >= int(covenant["expires_at"])
                                  and covenant["status"] not in TERMINAL_COVENANT and not blocked_by_appeal)
        covenant["can_expire_baseline"] = (
            covenant["status"] == "BASELINE_PENDING"
            and now >= int(covenant["baseline_deadline"])
            and now < int(covenant["expires_at"])
        )
        return covenant

    @gl.public.view
    def get_challenge(self, challenge_id: str) -> dict:
        challenge = self._challenge(challenge_id)
        challenge["can_expire"] = (
            challenge["status"] in ("INSPECTION_PENDING", "JUDGMENT_PENDING", "APPEAL_PENDING")
            and _now() >= int(challenge["stage_deadline"])
        )
        challenge["can_finalize"] = challenge["status"].startswith("PROVISIONAL_") and _now() >= int(challenge.get("appeal_deadline", "0"))
        return challenge

    @gl.public.view
    def list_covenants(self, offset: u256, count: u256) -> dict:
        if int(count) < 1 or int(count) > MAX_COVENANTS_PAGE:
            raise gl.vm.UserError(f"[EXPECTED] page size must be 1..{MAX_COVENANTS_PAGE}")
        start = int(offset)
        stop = min(len(self.covenant_ids), start + int(count))
        fields = (
            "id", "title", "subject", "canonical_url", "protected_promise", "owner", "beneficiary",
            "stake_atto", "remaining_stake_atto", "challenge_bond_atto", "finder_reward_bps", "status",
            "created_at", "activated_at", "expires_at", "pending_challenge", "challenge_count",
        )
        items = []
        for index in range(start, stop):
            covenant = self._covenant(self.covenant_ids[index])
            items.append({key: covenant[key] for key in fields})
        return {"items": items, "total": str(len(self.covenant_ids))}

    @gl.public.view
    def list_challenges(self, covenant_id: str, offset: u256, count: u256) -> dict:
        covenant = self._covenant(covenant_id)
        if int(count) < 1 or int(count) > MAX_CHALLENGES_PAGE:
            raise gl.vm.UserError(f"[EXPECTED] page size must be 1..{MAX_CHALLENGES_PAGE}")
        total = int(covenant["challenge_count"])
        start = int(offset)
        stop = min(total, start + int(count))
        items = []
        for index in range(start, stop):
            challenge_id = self.covenant_challenge_index[f"{covenant_id}:{index}"]
            challenge = self._challenge(challenge_id)
            challenge["can_expire"] = (
                challenge["status"] in ("INSPECTION_PENDING", "JUDGMENT_PENDING", "APPEAL_PENDING")
                and _now() >= int(challenge["stage_deadline"])
            )
            challenge["can_finalize"] = challenge["status"].startswith("PROVISIONAL_") and _now() >= int(challenge.get("appeal_deadline", "0"))
            items.append(challenge)
        return {"items": items, "total": str(total)}

    @gl.public.view
    def list_wallet_challenges(self, address: str, offset: u256, count: u256) -> dict:
        address = _address(address, "wallet")
        if int(count) < 1 or int(count) > MAX_CHALLENGES_PAGE:
            raise gl.vm.UserError(f"[EXPECTED] page size must be 1..{MAX_CHALLENGES_PAGE}")
        account = Address(address)
        total = int(self.wallet_challenge_counts[account]) if account in self.wallet_challenge_counts else 0
        start = int(offset)
        stop = min(total, start + int(count))
        items = []
        for index in range(start, stop):
            challenge_id = self.wallet_challenge_index[f"{address.lower()}:{index}"]
            items.append(self._challenge(challenge_id))
        return {"items": items, "total": str(total)}

    @gl.public.view
    def list_wallet_appeals(self, address: str, offset: u256, count: u256) -> dict:
        address = _address(address, "wallet")
        if int(count) < 1 or int(count) > MAX_CHALLENGES_PAGE:
            raise gl.vm.UserError(f"[EXPECTED] page size must be 1..{MAX_CHALLENGES_PAGE}")
        account = Address(address)
        total = int(self.wallet_appeal_counts[account]) if account in self.wallet_appeal_counts else 0
        start = int(offset)
        stop = min(total, start + int(count))
        items = []
        for index in range(start, stop):
            challenge_id = self.wallet_appeal_index[f"{address.lower()}:{index}"]
            items.append(self._challenge(challenge_id))
        return {"items": items, "total": str(total)}

    @gl.public.view
    def get_credit(self, recipient: str) -> str:
        account = Address(recipient)
        return str(int(self.credits[account])) if account in self.credits else "0"

    @gl.public.view
    def find_latest_covenant_by_owner(self, owner: str) -> str:
        owner = _address(owner, "owner")
        account = Address(owner)
        return self.owner_latest[account] if account in self.owner_latest else ""

    @gl.public.view
    def get_stats(self) -> dict:
        return {
            "product": "Driftlock", "version": VERSION, "network": "StudioNet", "chain_id": NETWORK_ID,
            "rpc": "https://studio.genlayer.com/api", "inspector": self.inspector_address,
            "judge": self.judge_address, "components_configured": self.components_configured,
            "admin_controls": False, "protocol_fee_bps": "0", "max_challenges_per_covenant": "unlimited",
            "total_covenants": str(len(self.covenant_ids)), "total_challenges": str(int(self.total_challenges)),
            "covenants_activated": str(int(self.covenants_activated)), "covenants_breached": str(int(self.covenants_breached)),
            "covenants_expired": str(int(self.covenants_expired)), "total_deposited_atto": str(int(self.total_deposited)),
            "stake_escrow_atto": str(int(self.stake_escrow)), "bond_escrow_atto": str(int(self.bond_escrow)),
            "appeal_escrow_atto": str(int(self.appeal_escrow)),
            "claimable_atto": str(int(self.total_claimable)), "withdrawn_atto": str(int(self.total_withdrawn)),
            "accounting_balanced": self._accounting_ok(),
        }
