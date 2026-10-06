# Architecture

## Trust split

`DriftRegistry` is deterministic lifecycle and accounting state. It does not fetch websites and does not author semantic verdicts.

`SourceInspector` has two source-grounded tasks. At creation it verifies that the source supports the protected promise, the breach rule is testable and in scope, and the operative source is compliant with the covenant with no breach condition already present. Later it re-fetches the same canonical URL and evaluates the current semantic state relative to that verified compliant baseline. A `NO_RELEVANT_CHANGE` result requires current compliance; `MATERIAL_CHANGE` requires accessible same-subject evidence of current non-compliance or a supported operative breach condition. Validators replay stable bounded fields, not free-form reasoning prose.

`BreachJudge` runs only after a normalized `MATERIAL_CHANGE` tied to a verified compliant baseline. It independently re-fetches the canonical source and asks a different question: whether the current operative wording violates the frozen breach rule after applying explicitly permitted changes.

The protocol stores a bounded semantic baseline result, not the source document itself. It does not store fetched source text, a source digest, or an exact historical page snapshot. Validators re-fetch the same frozen canonical URL for later decisions.

## Bounded state

Each covenant stores only its latest baseline/inspection summary plus deterministic metadata. Challenge history is indexed and paginated in pages of at most 24 records. Attempts do not consume a lifetime challenge quota; the 15-minute cooldown and 30-day maximum covenant lifetime bound attempts in time. Wallet challenge indexes are direct and paginated rather than implemented as unbounded global scans.

## Economic states

- `NO_RELEVANT_CHANGE`: covenant active; challenge bond to owner.
- `PERMITTED_CHANGE`: covenant active; challenge bond to owner.
- `SOURCE_UNAVAILABLE`, `AMBIGUOUS`, `INCONCLUSIVE`, stage timeout: challenger bond refunded.
- `BREACH`: challenger bond returned, finder reward credited to challenger, remaining stake credited to beneficiary.
- `EXPIRED_UNBREACHED`: remaining stake credited back to owner.

Every value movement is first represented as claimable credit. Withdrawal is a separate action.
