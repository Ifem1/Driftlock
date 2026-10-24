# Security notes

> The security analysis on this page documents the pre-V2/V1 hardening and is retained as historical context. Current V2 trust boundaries, appeal settlement and provenance limitations are documented in [`milestone-v2/THREAT_MODEL.md`](milestone-v2/THREAT_MODEL.md), [`milestone-v2/ARCHITECTURE.md`](milestone-v2/ARCHITECTURE.md), and [`milestone-v2/LIVE_VERIFICATION.md`](milestone-v2/LIVE_VERIFICATION.md). V2 publisher identity remains unauthenticated and its full live lifecycle is not yet demonstrated.

## Prompt injection

All user and fetched page text is explicitly treated as untrusted data in semantic prompts. Source text is bounded. Stable decision fields are structurally validated and independently replayed by validators. Free-form `basis` text is not used as an equivalence key.

## Cross-contract authentication

Inspector and Judge are constructed with one Registry address. They verify both the supplied Registry and the actual caller. Registry binds the two semantic components once during bootstrap and clears the bootstrap authority.

## Stale work

Registry only accepts callbacks for the expected challenge stage. Closed/expired covenants cannot be breached by a late callback. Challenge timeouts refund challenger bonds. Covenant expiry refunds any still-pending protocol-blocked challenger before releasing unbreached stake.

## Semantic transition checks

A baseline is verified only when the protected promise is supported, the rule is testable and in scope, the operative source is compliant with the covenant, and no breach condition is present. A source that supports the promise but already contains a breach condition cannot activate. The bounded semantic baseline packet is supplied to the current inspection stage. `NO_RELEVANT_CHANGE` requires an accessible same-subject source that remains compliant; `MATERIAL_CHANGE` requires accessible same-subject evidence of current non-compliance or a supported operative breach condition. `BreachJudge` remains a separate consensus stage and independently re-fetches the canonical URL before settlement.

The Registry validates these response fields and their status combinations at the callback boundary. Unavailable and ambiguous results cannot carry contradictory definitive semantic claims. Stale callbacks cannot bypass these checks or settle a challenge.

## Accounting

Stake and challenge bonds enter explicit escrow totals. Settlement moves values from escrow into claimable credits. `withdraw_credit` moves claimable value into the withdrawn total before emitting the transfer. `get_stats().accounting_balanced` exposes the conservation check.

## October 2026 source audit

The Registry's baseline callback originally identified only a covenant. A finalized callback from attempt 1 could arrive after the owner started attempt 2 and activate the covenant using stale evidence. The Inspector now passes its request ID to the Registry, which checks it against the current attempt and the result packet. A Direct Mode regression test covers this ordering.

The source audit also checked component sender authentication, single binding, stage deadlines, duplicate callbacks, expiry races, cooldown without a lifetime challenge quota, escrow conservation, withdrawal ordering, source text bounds, prompt injection instructions, structured semantic response checks, and validator replay. The app exposes `retry_baseline`, `expire_baseline`, `expire_challenge`, and `expire_covenant` recovery actions. The current hardening regression suite includes the baseline-compliance and current-state transition rules; Direct Mode tests do not prove every production consensus outcome.

The October 2026 dependency refresh preserves the Next.js 15.5.28 application and applies compatible lockfile overrides. Fresh online root and frontend npm audits returned zero vulnerabilities; the release verification record retains the exact gate results.

V1 browser reports elsewhere in this repository are historical. For current V2, the recorded Chrome wallet QA covered account changes, refresh recovery, wrong-network handling and signed lifecycle transactions. Explicit transaction rejection remains untested, and CI does not automate wallet interaction. The current Studionet finalization/RPC limitation and production HTTP checks are documented in `milestone-v2/LIVE_VERIFICATION.md`.

## Source evidence retention

The current contracts store only a bounded semantic baseline result and its basis, not fetched source text or a source digest. They do not archive an exact historical page snapshot or diff. For later checks, GenLayer validators re-fetch and independently re-evaluate the same frozen canonical URL relative to the verified compliant baseline. BreachJudge independently re-fetches that URL before economic settlement.
