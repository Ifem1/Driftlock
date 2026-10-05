# Review evidence

This file intentionally contains no invented live evidence.

## Repository evidence

- semantic responsibilities are split across three contracts;
- source URLs are HTTPS-only and bounded;
- source render text is bounded;
- component callers are authenticated;
- covenant history is lifetime-bounded and reads are paginated;
- challenge spam is cooldown-gated;
- deterministic accounting exposes a conservation invariant;
- frontend has no application backend and uses injected EIP-1193 only;
- CI checks contracts and frontend.

## Verified release evidence

- Submission-readiness commit `93a4434f52fb62be04c1c4c606cfdd83198d020c` passed [GitHub Actions run `37244901884`](https://github.com/Ifem1/Driftlock/actions/runs/37244901884), including all three GenVM checks, 30 Direct Mode tests, 14 frontend tests, typecheck, lint, build and CLI version check.
- All three Studionet deployment receipts and the one-time binding receipt returned `FINALIZED`; exact hashes and addresses are in `deployments/studionet.json` and `docs/LIVE_VALIDATION.md`.
- On-chain schemas matched the expected Registry, Inspector and Judge methods. Registry stats confirmed binding and balanced zero-state accounting.
- The production frontend is READY at `https://driftlock-nine.vercel.app/`; Vercel reported success for the submission-readiness commit. The project owner reports manually verifying injected-wallet browser interaction and transactions; these checks are separate from CI.

## Evidence limits

This release repository does not include a canonical complete demo-covenant lifecycle transaction set. Deployment and browser verification do not imply such a recorded lifecycle. GenLayer validators independently re-evaluate covenants against the same frozen canonical URL; the contracts do not archive a permanent snapshot or diff of every later fetched page.
