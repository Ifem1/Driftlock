# Architecture

## Trust split

`DriftRegistry` is deterministic lifecycle and accounting state. It does not fetch websites and does not author semantic verdicts.

`SourceInspector` has two source-grounded tasks: establish that the promised statement exists at creation, and later inspect the current contents of that exact URL. It compares stable semantic fields under independent validator replay rather than free-form reasoning prose.

`BreachJudge` runs only after a verified `MATERIAL_CHANGE`. It independently re-fetches the canonical source and asks a different question: whether the current operative wording violates the frozen breach rule after applying explicitly permitted changes.

## Bounded state

Each covenant stores only its latest baseline/inspection summary plus deterministic metadata. Challenge history is indexed and paginated in pages of at most 24 records. Attempts do not consume a lifetime challenge quota; the 15-minute cooldown and 30-day maximum covenant lifetime bound attempts in time. Wallet challenge indexes are direct and paginated rather than implemented as unbounded global scans.

## Economic states

- `NO_RELEVANT_CHANGE`: covenant active; challenge bond to owner.
- `PERMITTED_CHANGE`: covenant active; challenge bond to owner.
- `SOURCE_UNAVAILABLE`, `AMBIGUOUS`, `INCONCLUSIVE`, stage timeout: challenger bond refunded.
- `BREACH`: challenger bond returned, finder reward credited to challenger, remaining stake credited to beneficiary.
- `EXPIRED_UNBREACHED`: remaining stake credited back to owner.

Every value movement is first represented as claimable credit. Withdrawal is a separate action.
