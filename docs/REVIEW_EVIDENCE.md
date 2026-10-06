# Review evidence

## Repository verification

- All three Intelligent Contracts pass GenVM lint and validation with GenVM `v0.2.12`.
- Direct Mode regression suite: 52 tests, including baseline compliance, transition consistency, independent judgment, stale callbacks, accounting, recovery actions, and the owner-controlled secondary-wallet case.
- Frontend verification: 19 tests, typecheck, ESLint, and Next.js production build pass.
- The repository-local GenLayer CLI reports `0.39.1`.
- Frontend contract addresses are read from the Studionet deployment manifest; writes enforce chain ID `61999`, wait for `FINALIZED`, and reject unsuccessful contract execution.

## Verified Studionet release

- The three current Studionet deployment transactions and one-time binding transaction finalized with successful leader execution and majority agreement. Current addresses and hashes are in [`deployments/studionet.json`](../deployments/studionet.json) and [`LIVE_VALIDATION.md`](LIVE_VALIDATION.md).
- Live schema read-back confirmed the deployed interfaces, including the baseline packet argument to current inspection.
- Registry read-back confirmed the exact configured component addresses, chain ID `61999`, zero initial covenant/challenge/escrow/credit state, and `accounting_balanced: true`.
- A complete lifecycle transaction set for this fresh deployment has not been recorded.

## Evidence limits

The contracts store only a bounded semantic baseline result and basis. They do not store fetched source text, a source digest, or an exact historical page snapshot. Current validators re-fetch the same frozen canonical URL, and BreachJudge independently re-fetches before settlement.
