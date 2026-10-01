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

The source audit added immutable bounded baseline text and SHA-256 identity, explicit already-breached baseline rejection, same-source comparison, callback challenge/evidence identity, a substantive challenge cap separate from history, and self-only withdrawals. The suite now has 41 Direct Mode tests, including 25 repeated unavailable attempts followed by a successful breach settlement. These Direct Mode tests do not establish all possible production consensus outcomes.

The frontend dependency audit found a vulnerable Next.js 15.5.7 pin. It was updated to 15.5.27. npm still reports transitive PostCSS and Sharp advisories through Next.js 15.5.27; resolving them may require a framework major upgrade and compatibility review. Do not treat the frontend as free of dependency advisories.

The corrected contracts are deployed on Studionet and the production frontend is deployed. The live baseline, unchanged challenge, changed-source breach, all credit withdrawals, and balanced accounting are verified. Browser transaction paths were not tested because the in-app browser had no injected wallet; see `LIVE_VALIDATION.md` for evidence and limits.
