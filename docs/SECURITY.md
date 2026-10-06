# Security notes

## Prompt injection

All user and fetched page text is explicitly treated as untrusted data in semantic prompts. Source text is bounded. Stable decision fields are structurally validated and independently replayed by validators. Free-form `basis` text is not used as an equivalence key.

## Cross-contract authentication

Inspector and Judge are constructed with one Registry address. They verify both the supplied Registry and the actual caller. Registry binds the two semantic components once during bootstrap and clears the bootstrap authority.

## Stale work

Registry only accepts callbacks for the expected challenge stage. Closed/expired covenants cannot be breached by a late callback. Challenge timeouts refund challenger bonds. Covenant expiry refunds any still-pending protocol-blocked challenger before releasing unbreached stake.

## Accounting

Stake and challenge bonds enter explicit escrow totals. Settlement moves values from escrow into claimable credits. `withdraw_credit` moves claimable value into the withdrawn total before emitting the transfer. `get_stats().accounting_balanced` exposes the conservation check.

## October 2026 source audit

The Registry's baseline callback originally identified only a covenant. A finalized callback from attempt 1 could arrive after the owner started attempt 2 and activate the covenant using stale evidence. The Inspector now passes its request ID to the Registry, which checks it against the current attempt and the result packet. A Direct Mode regression test covers this ordering.

The source audit also checked component sender authentication, single binding, stage deadlines, duplicate callbacks, expiry races, cooldown without a lifetime challenge quota, escrow conservation, withdrawal ordering, source text bounds, prompt injection instructions, structured semantic response checks, and validator replay. The app exposes `retry_baseline`, `expire_baseline`, `expire_challenge`, and `expire_covenant` recovery actions. CI passed 31 Direct Mode tests with GenVM v0.2.12; these tests do not prove every production consensus outcome.

The frontend dependency audit found a vulnerable Next.js 15.5.7 pin. It was updated to 15.5.27. npm still reports transitive PostCSS and Sharp advisories through Next.js 15.5.27; resolving them may require a framework major upgrade and compatibility review. Do not treat the frontend as free of dependency advisories.

The updated contracts are deployed on Studionet. The owner reports manually verifying the injected-wallet browser paths. CI does not automate wallet interaction. See `LIVE_VALIDATION.md` for deployment receipts and evidence limits.

## Source evidence retention

The current contracts store only the semantic baseline result and its basis, not fetched source text or a source digest. For later checks, GenLayer validators independently re-evaluate the covenant against the same frozen canonical URL. The contracts do not archive an exact historical page snapshot or diff.
