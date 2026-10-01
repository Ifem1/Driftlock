# Architecture

## Trust split

`DriftRegistry` is deterministic lifecycle and accounting state. It does not fetch websites and does not author semantic verdicts.

`SourceInspector` stores the exact bounded text from a verified baseline and its SHA-256 digest. Later, it fetches the same canonical URL and compares that evidence with the current bounded text. Identical text returns `NO_RELEVANT_CHANGE` deterministically; semantic evaluation runs only when the text differs. Validators independently refetch the source and compare structured outcomes and evidence identities.

`BreachJudge` runs only after a verified `MATERIAL_CHANGE`. It independently re-fetches the canonical source and asks a different question: whether the current operative wording violates the frozen breach rule after applying explicitly permitted changes.

## Bounded state

Each covenant stores at most 16,000 characters of baseline evidence, a digest and the latest inspection summary. Sources larger than that evidence limit are treated as ambiguous. Challenge history is indexed and paginated. The 24 challenge cap applies to substantive outcomes; refunded uncertainty outcomes do not consume that capacity. A 15-minute cooldown and the 30-day maximum covenant lifetime bound retries. Wallet challenge indexes are direct and paginated rather than implemented as global scans.

## Baseline eligibility

Activation requires that the source supports the protected promise, the rule is testable, the time scope is current, and the source does not already satisfy the breach condition. `BASELINE_ALREADY_BREACHED` is explicit and refunds owner stake through the terminal rejected-baseline path.

## Economic states

- `NO_RELEVANT_CHANGE`: covenant active; challenge bond to owner.
- `PERMITTED_CHANGE`: covenant active; challenge bond to owner.
- `SOURCE_UNAVAILABLE`, `AMBIGUOUS`, `INCONCLUSIVE`, stage timeout: challenger bond refunded.
- `BREACH`: challenger bond returned, finder reward credited to challenger, remaining stake credited to beneficiary.
- `EXPIRED_UNBREACHED`: remaining stake credited back to owner.

Every value movement is first represented as claimable credit. Withdrawal is a separate action.

`withdraw_credit` only permits the credited wallet to withdraw its own amount. The shared frontend write path reads the active account and actual chain immediately before submission, switches to Studionet when needed, then verifies the chain again.
